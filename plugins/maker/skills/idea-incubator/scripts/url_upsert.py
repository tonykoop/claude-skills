#!/usr/bin/env python3
"""URL-stable upsert clipping for the idea-incubator inbox.

Story #408 (Epic #406). Converts a Gemini chat URL to a stable, reproducible
filename and writes a stub .md file into the Obsidian vault inbox — creating it
on first clip, skipping silently on repeat (idempotent).

Design goals
------------
* **Same URL → same filename** across sessions: strip ephemeral query params
  (utm_*, session IDs) that change each share while preserving the stable chat
  path component.
* **Offline-first / stdlib-only**: no network calls, no external deps.
* **Dry-run by default**: CLI prints the would-be path without writing; pass
  ``--write`` to actually create the file.

Filename convention
-------------------
  gemini-<sha8>-<slug>.md

where:
  sha8  = first 8 hex chars of sha256(normalized_url)
  slug  = first 32 chars of the URL path component, lowercased, non-alphanum→"-"

This is short enough to fit on mobile displays and unique enough to avoid
collisions across a realistic conversation history.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs

# Query-string keys that vary per share session and must be stripped.
_EPHEMERAL_PARAMS: frozenset[str] = frozenset(
    {"utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "usp", "_gl"}
)

# Gemini/AI chat hostnames we recognize.
_KNOWN_HOSTS: frozenset[str] = frozenset(
    {"gemini.google.com", "aistudio.google.com", "chat.openai.com", "claude.ai"}
)


def normalize_url(url: str) -> str:
    """Strip ephemeral query params and trailing slashes; lowercase the host.

    Returns a canonical URL string used as the dedup key. The normalized form
    is NOT necessarily a valid request URL (params are dropped intentionally).
    """
    url = url.strip()
    parsed = urlparse(url)
    # Lowercase the netloc so http://Gemini.Google.Com and gemini.google.com match.
    netloc = parsed.netloc.lower()

    qs = parse_qs(parsed.query, keep_blank_values=True)
    stable_qs = {k: v for k, v in sorted(qs.items()) if k not in _EPHEMERAL_PARAMS}
    # Re-encode deterministically: sorted keys, first value only (no lists).
    clean_query = urlencode({k: v[0] for k, v in stable_qs.items()})

    normalized = urlunparse(
        (parsed.scheme.lower(), netloc, parsed.path.rstrip("/"), parsed.params, clean_query, "")
    )
    return normalized


def sanitize_chat_url(url: str) -> str:
    """Return a stable filesystem-safe filename stem for a chat URL.

    >>> sanitize_chat_url("https://gemini.google.com/app/abc123?utm_source=share")
    'gemini-xxxxxxxx-app-abc123'  # sha8 varies; slug is deterministic
    """
    norm = normalize_url(url)
    sha8 = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:8]

    parsed = urlparse(norm)
    path_part = parsed.path.strip("/") or parsed.netloc
    slug = re.sub(r"[^a-z0-9]+", "-", path_part.lower()).strip("-")[:32].rstrip("-")
    if not slug:
        slug = "clip"
    return f"gemini-{sha8}-{slug}"


def upsert_clip(
    inbox_dir: Path,
    url: str,
    content: str = "",
    *,
    overwrite: bool = False,
) -> tuple[Path, Literal["created", "existing"]]:
    """Write a stub .md file into *inbox_dir* keyed by the stable URL hash.

    Parameters
    ----------
    inbox_dir:
        Obsidian vault inbox folder (created if absent).
    url:
        The Gemini chat URL being clipped.
    content:
        Optional body text (front-matter + clip body). When empty a minimal
        stub is generated so the watcher can pick it up.
    overwrite:
        If True, overwrite an existing file. Default is False (idempotent).

    Returns
    -------
    (path, mode) where mode is 'created' or 'existing'.
    """
    stem = sanitize_chat_url(url)
    path = inbox_dir / f"{stem}.md"

    if path.exists() and not overwrite:
        return path, "existing"

    inbox_dir.mkdir(parents=True, exist_ok=True)

    if not content:
        norm = normalize_url(url)
        content = (
            "---\n"
            "source: gemini\n"
            f"chat_url: {norm}\n"
            "exported_at: \n"
            f"title: Gemini clip — {stem}\n"
            "---\n\n"
            f"> Clipped from: {url}\n\n"
            "**Next step:** run the idea-incubator ingestion pipeline.\n"
        )

    path.write_text(content, encoding="utf-8")
    return path, "created"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Clip a Gemini chat URL into the Obsidian vault inbox (idempotent)."
    )
    parser.add_argument("url", help="Gemini chat URL to clip.")
    parser.add_argument(
        "--inbox",
        type=Path,
        default=Path("Inbound_Brainstorms"),
        help="Obsidian vault inbox folder (default: Inbound_Brainstorms).",
    )
    parser.add_argument(
        "--content-file",
        type=Path,
        help="Read clip body from this file instead of generating a stub.",
    )
    parser.add_argument(
        "--content",
        help="Clip body as a string (overrides --content-file).",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Actually write the clip file to disk (default: dry-run).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing clip file (default: skip). Implies --write.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the would-be path without writing (the default; kept for explicitness).",
    )
    parser.add_argument(
        "--show-stem",
        action="store_true",
        help="Print the stable filename stem and exit.",
    )
    args = parser.parse_args(argv[1:])

    if args.show_stem:
        print(sanitize_chat_url(args.url))
        return 0

    # Dry-run is the default. --write (or --overwrite) opts in to disk writes.
    # Explicit --dry-run always wins even if --write is also passed.
    do_write = (args.write or args.overwrite) and not args.dry_run
    if not do_write:
        stem = sanitize_chat_url(args.url)
        path = args.inbox / f"{stem}.md"
        sys.stdout.write(f"[dry-run] would write: {path}\n")
        return 0

    body = ""
    if args.content:
        body = args.content
    elif args.content_file:
        body = args.content_file.read_text(encoding="utf-8")

    path, mode = upsert_clip(args.inbox, args.url, body, overwrite=args.overwrite)
    verb = "created" if mode == "created" else "skipped (existing)"
    sys.stdout.write(f"[{verb}] {path}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
