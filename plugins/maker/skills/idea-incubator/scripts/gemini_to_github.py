#!/usr/bin/env python3
"""Convert an exported Gemini brainstorm into draft GitHub issue payloads.

This is the Story #237 helper: it reads a Markdown or JSON brainstorm exported
from a Gemini conversation (the Gemini -> Obsidian half of the pipeline),
splits it into idea blocks, and emits one draft issue payload per block.

The helper is intentionally offline-first and **dry-run by default**: it prints
payloads to stdout and never calls the GitHub API unless `--create` is passed
AND credentials are configured. Mirrors the offline-first posture of
`promote_batch_readiness.py`.

Dedup is fingerprint-based: each payload carries a sha256 of the conversation
id plus the normalized idea-block text, embedded in the issue body as
`<!-- idea-fingerprint: ... -->` so downstream tools (and StudioPipeline #57)
can dedup against it. See references/gemini-export-pipeline.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# --- Domain routing -------------------------------------------------------
# Routing is delegated to the tuned, confidence-weighted router in
# domain_router.py (the data-driven implementation of
# references/domain-label-routing.md). It replaces the old any-keyword inline
# fallback, which confidently mislabeled captures on a single incidental
# substring hit. The router stays self-contained (stdlib only), so importing it
# does not add a dependency.
try:  # absolute import when run as a loose script
    from domain_router import NEEDS_TRIAGE_LABEL  # noqa: F401 (re-exported for callers)
    from domain_router import route_labels as _route_labels
    from github_dedup import decide_mode as _decide_mode
    from github_dedup import chat_id_label as _chat_id_label
except ImportError:  # package-relative import when imported as a module
    from .domain_router import NEEDS_TRIAGE_LABEL  # noqa: F401 (re-exported for callers)
    from .domain_router import route_labels as _route_labels
    from .github_dedup import decide_mode as _decide_mode
    from .github_dedup import chat_id_label as _chat_id_label


@dataclass
class IdeaBlock:
    text: str
    index: int
    title: str = ""
    labels: list[str] = field(default_factory=list)
    fingerprint: str = ""


def normalize(text: str) -> str:
    """Lowercase, collapse whitespace, strip trailing punctuation (dedup key)."""
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text.rstrip(".!?,; ")


def fingerprint(conversation_id: str, block_text: str) -> str:
    digest = hashlib.sha256()
    digest.update(conversation_id.encode("utf-8"))
    digest.update(b"\n")
    digest.update(normalize(block_text).encode("utf-8"))
    return digest.hexdigest()


def read_export(path: Path) -> tuple[str, str]:
    """Return (conversation_id, raw_text) from a Markdown or JSON export.

    JSON form is expected to look like {"conversation_id": ..., "text": ...}
    or {"messages": [{"content": ...}, ...]}. Markdown form may carry YAML
    front-matter with a conversation_id; if absent we synthesize one from a
    hash of the transcript (see references/gemini-export-pipeline.md).
    """
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data: Any = json.loads(raw)
        conv_id = str(data.get("conversation_id") or "")
        if "text" in data:
            text = str(data["text"])
        elif "messages" in data:
            text = "\n\n".join(str(m.get("content", "")) for m in data["messages"])
        else:
            text = json.dumps(data)
    else:
        conv_id, text = _strip_front_matter(raw)
    if not conv_id:
        conv_id = "sha256:" + hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()[:16]
    return conv_id, text


def _strip_front_matter(raw: str) -> tuple[str, str]:
    """Pull conversation_id out of YAML front-matter; return (id, body)."""
    conv_id = ""
    body = raw
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            front = raw[3:end]
            body = raw[end + 4 :]
            match = re.search(r"^conversation_id:\s*(.+)$", front, re.MULTILINE)
            if match:
                conv_id = match.group(1).strip()
    return conv_id, body


def split_blocks(text: str) -> list[str]:
    """Split a transcript into candidate idea blocks.

    Strategy: prefer Markdown headings as block boundaries; fall back to
    blank-line-separated paragraphs. Ambiguous splits are NOT forced here -
    the caller marks short/uncertain blocks as needs-clarification.
    """
    heading_split = re.split(r"\n(?=#{1,6}\s)", text)
    if len(heading_split) > 1:
        blocks = heading_split
    else:
        blocks = re.split(r"\n\s*\n", text)
    return [b.strip() for b in blocks if b.strip()]


def derive_title(block: str) -> str:
    first = block.lstrip("#").strip().splitlines()[0] if block.strip() else "Untitled idea"
    first = first.strip("#-* ").strip()
    return (first[:72] + "...") if len(first) > 75 else first or "Untitled idea"


def route_labels(block: str) -> list[str]:
    """Assign domain labels via the tuned confidence-weighted router.

    Always includes 'capture'; unroutable captures fall back to
    'needs-clarification'. See domain_router.py / domain-label-routing.md.
    """
    return _route_labels(block)


def build_body(block: IdeaBlock, conversation_id: str) -> str:
    """Render the issue body using the house issue-template skeleton."""
    return (
        f"## Capture\n"
        f"- Source: gemini\n"
        f"- conversation_id: {conversation_id}\n"
        f"- Original text:\n"
        f"  > {block.text.replace(chr(10), chr(10) + '  > ')}\n\n"
        f"## What this is\n<1-3 sentences paraphrase - TODO: fill during review>\n\n"
        f"## Why it matters\n- <why this is worth keeping>\n\n"
        f"## Next step\n- <one concrete action>\n\n"
        f"## Suggested labels\n"
        + "".join(f"- {label}\n" for label in block.labels)
        + f"\n<!-- idea-fingerprint: {block.fingerprint} -->\n"
    )


def build_payloads(
    conversation_id: str,
    text: str,
    *,
    gemini_variant: str = "",
) -> list[dict[str, Any]]:
    """Build issue payloads from a parsed brainstorm export.

    Parameters
    ----------
    gemini_variant:
        When ``"notebooklm"``, appends ``needs-clarification`` to every
        block's label list so reviewers know the content came from a
        NotebookLM grounded session (Story #411).
    """
    payloads: list[dict[str, Any]] = []
    for index, raw_block in enumerate(split_blocks(text)):
        block = IdeaBlock(text=raw_block, index=index)
        block.title = derive_title(raw_block)
        block.labels = route_labels(raw_block)
        if gemini_variant == "notebooklm" and "needs-clarification" not in block.labels:
            block.labels = block.labels + ["needs-clarification"]
        block.fingerprint = fingerprint(conversation_id, raw_block)
        payloads.append(
            {
                "fingerprint": block.fingerprint,
                "conversation_id": conversation_id,
                "source": "gemini",
                "gemini_variant": gemini_variant,
                "title": block.title,
                "body": build_body(block, conversation_id),
                "labels": block.labels,
                "block_index": index,
            }
        )
    return payloads


def create_issue(repo: str, payload: dict[str, Any]) -> None:
    """Placeholder for real issue creation.

    Intentionally NOT implemented against a live API. Wire this to either the
    `gh` CLI (subprocess) or the GitHub MCP/REST API once credentials and the
    target repo are confirmed. Must first dedup on the fingerprint marker.
    """
    # TODO: pre-flight search repo for `<!-- idea-fingerprint: {fingerprint} -->`
    #       and skip if found (idempotency contract, see design doc).
    # TODO: authenticate via GH_TOKEN / gh auth and POST /repos/{repo}/issues.
    raise NotImplementedError(
        "Live issue creation is not wired up. Configure credentials and target "
        f"repo, then implement create_issue(). Would have created in {repo!r}: "
        f"{payload['title']!r}"
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="Exported Gemini brainstorm (.md or .json).")
    parser.add_argument(
        "--create",
        action="store_true",
        help="Actually create issues (requires --repo and credentials). Default is dry-run.",
    )
    parser.add_argument("--repo", help="Target inbox repo OWNER/REPO (required with --create).")
    parser.add_argument(
        "--failed-out",
        type=Path,
        help="Write payloads that failed to create here for later replay.",
    )
    parser.add_argument(
        "--dedup-repo",
        metavar="OWNER/REPO",
        help=(
            "Check this repo for an existing open issue labelled chat-id:<sha8> "
            "before filing. Prints CREATE or APPEND to stderr. No-op in dry-run mode."
        ),
    )
    parser.add_argument(
        "--gemini-variant",
        default="",
        metavar="VARIANT",
        help=(
            "Gemini source variant for this export. Pass 'notebooklm' when the clip "
            "originated from a NotebookLM session; adds 'needs-clarification' label to "
            "all issues so reviewers know the content came from a grounded session."
        ),
    )
    args = parser.parse_args(argv[1:])

    conversation_id, text = read_export(args.export)
    payloads = build_payloads(conversation_id, text, gemini_variant=args.gemini_variant)

    if args.dedup_repo and args.create:
        mode = _decide_mode(args.dedup_repo, conversation_id)
        sys.stderr.write(
            f"[dedup] conversation {conversation_id[:16]}… → {mode} "
            f"(label: {_chat_id_label(conversation_id)}, repo: {args.dedup_repo})\n"
        )
        for p in payloads:
            p["dedup_mode"] = mode

    if not args.create:
        # Dry-run: emit a JSON array of draft payloads to stdout.
        json.dump(payloads, sys.stdout, indent=2)
        sys.stdout.write("\n")
        sys.stderr.write(
            f"[dry-run] {len(payloads)} idea block(s) from conversation "
            f"{conversation_id}. Re-run with --create --repo OWNER/REPO to file.\n"
        )
        return 0

    if not args.repo:
        parser.error("--create requires --repo OWNER/REPO")

    failed: list[dict[str, Any]] = []
    for payload in payloads:
        try:
            create_issue(args.repo, payload)
        except NotImplementedError as exc:
            sys.stderr.write(f"[skip] {exc}\n")
            failed.append(payload)
    if failed and args.failed_out:
        args.failed_out.write_text(json.dumps(failed, indent=2), encoding="utf-8")
        sys.stderr.write(f"[failed] wrote {len(failed)} payload(s) to {args.failed_out}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
