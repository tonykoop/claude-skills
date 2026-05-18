#!/usr/bin/env python3
"""Build a promote-batch readiness matrix from saved issue evidence.

The helper is intentionally offline-first: pass JSON captured from `gh` when
GitHub works, then rerun the matrix later with local anchor roots and inventory
CSVs even if the network is unavailable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STOPWORDS = {
    "add",
    "archive",
    "cad",
    "capture",
    "check",
    "content",
    "from",
    "idea",
    "into",
    "keep",
    "project",
    "pull",
    "recover",
    "recovery",
    "repo",
    "scaffold",
    "search",
    "the",
    "this",
    "verify",
}


@dataclass(frozen=True)
class Anchor:
    path: Path
    slug: str


@dataclass(frozen=True)
class InventoryHit:
    path: Path
    line_number: int
    text: str


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\[[^\]]+\]", " ", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def title_terms(title: str) -> list[str]:
    terms = re.findall(r"[a-z0-9]+", title.lower())
    return [term for term in terms if len(term) > 2 and term not in STOPWORDS]


def label_names(issue: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for label in issue.get("labels", []) or []:
        if isinstance(label, str):
            names.add(label)
        elif isinstance(label, dict) and label.get("name"):
            names.add(str(label["name"]))
    return names


def issue_number(issue: dict[str, Any]) -> str:
    number = issue.get("number")
    return f"#{number}" if number is not None else "(no number)"


def load_issues(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "items" in data:
        data = data["items"]
    if not isinstance(data, list):
        raise ValueError("issues JSON must be a list or an object with an items list")
    return [item for item in data if isinstance(item, dict)]


def load_anchors(roots: list[Path]) -> list[Anchor]:
    anchors: list[Anchor] = []
    for root in roots:
        if not root.exists():
            continue
        root_depth = len(root.resolve().parts)
        for dirpath, dirnames, _filenames in os.walk(root):
            path = Path(dirpath)
            depth = len(path.resolve().parts) - root_depth
            dirnames[:] = [
                name for name in dirnames
                if name not in {".git", "node_modules", "target", ".venv", "__pycache__"}
            ]
            if depth > 2:
                dirnames[:] = []
                continue
            if depth > 0:
                anchors.append(Anchor(path=path, slug=slugify(path.name)))
    return anchors


def matching_anchors(issue: dict[str, Any], anchors: list[Anchor]) -> list[Path]:
    title_slug = slugify(str(issue.get("title", "")))
    title_words = set(title_terms(str(issue.get("title", ""))))
    matches: list[Path] = []
    for anchor in anchors:
        anchor_words = set(anchor.slug.split("-"))
        if anchor.slug and (anchor.slug in title_slug or title_slug in anchor.slug):
            matches.append(anchor.path)
        elif len(anchor_words & title_words) >= 2:
            matches.append(anchor.path)
    return matches[:4]


def load_inventory_hits(paths: list[Path], issue: dict[str, Any]) -> list[InventoryHit]:
    title = str(issue.get("title", ""))
    if "inventory" in title.lower():
        return [
            InventoryHit(path=path, line_number=1, text="inventory file provided")
            for path in paths
            if path.exists()
        ][:3]
    terms = title_terms(title)
    if not terms:
        return []
    hits: list[InventoryHit] = []
    for path in paths:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line_number, line in enumerate(handle, start=1):
                haystack = line.lower()
                score = sum(1 for term in terms if term in haystack)
                if score >= min(3, len(terms)):
                    hits.append(InventoryHit(path=path, line_number=line_number, text=line.strip()))
                    if len(hits) >= 3:
                        return hits
    return hits


def state_from_labels(labels: set[str]) -> str:
    ordered = ["needs-clarification", "ready-now", "promote", "capture"]
    found = [label for label in ordered if label in labels]
    return ", ".join(found) if found else "unlabeled"


def route_from_labels(labels: set[str]) -> str:
    if "instrument" in labels:
        return "instrument-maker-v4"
    if "maker" in labels:
        return "maker-engineering / makerspace"
    if "skills" in labels:
        return "skills-meta or target skill"
    if "yoga" in labels:
        return "yoga-sequencer"
    return "idea-incubator review"


def decision_for(issue: dict[str, Any], anchors: list[Path], inventory_hits: list[InventoryHit]) -> str:
    labels = label_names(issue)
    title = str(issue.get("title", "")).lower()
    if "needs-clarification" in labels:
        return "comment / defer"
    if ("inventory" in title or "full inventory" in title) and inventory_hits:
        return "close / comment"
    if anchors and "promote" not in labels:
        return "comment / existing anchor"
    if "promote" in labels:
        return "promote"
    if "ready-now" in labels:
        return "promote or close"
    return "defer"


def evidence_for(issue: dict[str, Any], anchors: list[Path], inventory_hits: list[InventoryHit]) -> str:
    parts: list[str] = []
    if anchors:
        parts.append("anchors: " + ", ".join(str(path) for path in anchors))
    if inventory_hits:
        parts.append(
            "inventory: "
            + ", ".join(f"{hit.path.name}:{hit.line_number}" for hit in inventory_hits)
        )
    url = issue.get("url")
    if url:
        parts.append(str(url))
    return "; ".join(parts) if parts else "issue metadata only"


def blocker_for(issue: dict[str, Any], anchors: list[Path], inventory_hits: list[InventoryHit]) -> str:
    labels = label_names(issue)
    if "needs-clarification" in labels:
        return "missing key detail"
    if "promote" in labels and not anchors and not inventory_hits:
        return "target/provenance evidence not found locally"
    if "promote" in labels and (anchors or inventory_hits):
        return "confirm route, provenance, and close vs refs"
    return "none identified"


def render_matrix(issues: list[dict[str, Any]], anchor_roots: list[Path], inventory_csvs: list[Path]) -> str:
    anchors = load_anchors(anchor_roots)
    lines = [
        "| Issue | State | Evidence | Blockers | Best next route | Decision |",
        "|---|---|---|---|---|---|",
    ]
    for issue in issues:
        matched_anchors = matching_anchors(issue, anchors)
        inventory_hits = load_inventory_hits(inventory_csvs, issue)
        title = str(issue.get("title", "")).replace("|", "\\|")
        label_state = state_from_labels(label_names(issue))
        lines.append(
            "| {issue} {title} | {state} | {evidence} | {blockers} | {route} | {decision} |".format(
                issue=issue_number(issue),
                title=title,
                state=label_state,
                evidence=evidence_for(issue, matched_anchors, inventory_hits).replace("|", "\\|"),
                blockers=blocker_for(issue, matched_anchors, inventory_hits).replace("|", "\\|"),
                route=route_from_labels(label_names(issue)),
                decision=decision_for(issue, matched_anchors, inventory_hits),
            )
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issues-json", required=True, type=Path, help="Saved gh issue JSON.")
    parser.add_argument(
        "--anchor-root",
        action="append",
        default=[],
        type=Path,
        help="Directory tree to scan for existing anchors (up to two levels deep).",
    )
    parser.add_argument(
        "--inventory-csv",
        action="append",
        default=[],
        type=Path,
        help="Archive inventory CSV to scan for title terms.",
    )
    args = parser.parse_args(argv[1:])

    issues = load_issues(args.issues_json)
    sys.stdout.write(render_matrix(issues, args.anchor_root, args.inventory_csv))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
