#!/usr/bin/env python3
"""CREATE_MODE / APPEND_MODE dedup via chat-ID label for the idea-incubator inbox.

Story #410 (Epic #406). Solves the "only new content" problem when the same
Gemini conversation is clipped multiple times as it grows:

* **CREATE_MODE** — the file is new (or has no processed marker); the entire
  content is fresh input.
* **APPEND_MODE** — the file was already ingested; only the delta after the last
  processed position should be dispatched to avoid re-filing already-known ideas.

The mode is detected from a stamped marker that this script writes into the file
after each successful ingestion pass:

    <!-- incubator-processed-pos: <int> -->

Where ``<int>`` is the byte offset (UTF-8) immediately before this marker was
written on the previous run. On the next clip of the same conversation the
exporter may have appended more text *after the marker*; only those bytes are new.

The chat-ID is the stable anchor: ``url_upsert.py`` maps the conversation URL to
a unique filename, so the same conversation always lands in the same file and the
mode flip (CREATE→APPEND) happens automatically.

Design constraints
------------------
* Stdlib only — no external deps.
* Markers are stripped from extracted content before returning it to callers so
  the pipeline never sees marker text.
* Idempotent stamp: re-calling ``stamp_processed`` when nothing was appended
  since the last stamp is a guaranteed no-op (same position, no file write).
* NEVER truncates original content. Old markers are consolidated (one per file);
  content lines are preserved verbatim.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Literal

# Marker embedded in the processed file so the next pass knows where to start.
_MARKER_PREFIX = "<!-- incubator-processed-pos: "
_MARKER_SUFFIX = " -->"
_MARKER_RE = re.compile(
    r"<!--\s*incubator-processed-pos:\s*(\d+)\s*-->",
    re.IGNORECASE,
)


def detect_mode(path: Path) -> tuple[Literal["CREATE", "APPEND"], int]:
    """Detect whether a file should be processed in CREATE or APPEND mode.

    Returns
    -------
    (mode, last_pos) where:
    - ``('CREATE', 0)``  → whole file is new input (no marker or pos == 0)
    - ``('APPEND', N)``  → only content appended after byte N is new

    ``last_pos`` is a UTF-8 byte offset into the file as written on disk.
    Content before ``last_pos`` was already dispatched; only ``raw[last_pos:]``
    (markers stripped) contains genuinely new ideas.
    """
    if not path.exists():
        return "CREATE", 0

    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")

    matches = list(_MARKER_RE.finditer(text))
    if not matches:
        return "CREATE", 0

    # Use the LAST marker (handles edge case of multiple markers from a crash).
    last_match = matches[-1]
    try:
        last_pos = int(last_match.group(1))
    except ValueError:
        return "CREATE", 0

    # pos 0 means "nothing processed yet" — treat as CREATE.
    # pos > file size means corrupt/stale marker — treat as CREATE.
    if last_pos <= 0 or last_pos > len(raw):
        return "CREATE", 0

    return "APPEND", last_pos


def extract_new_content(path: Path, last_pos: int) -> str:
    """Return only the text appended after *last_pos* bytes, markers stripped.

    Parameters
    ----------
    path:
        The inbox file to read.
    last_pos:
        Byte offset returned by ``detect_mode``. 0 means return the whole file.

    Returns
    -------
    New content as a str with all ``incubator-processed-pos`` marker text
    removed. Returns ``""`` if nothing was appended.
    """
    raw = path.read_bytes()
    if last_pos == 0:
        delta = raw.decode("utf-8", errors="replace")
    elif last_pos >= len(raw):
        return ""
    else:
        delta = raw[last_pos:].decode("utf-8", errors="replace")

    # Strip marker lines so they are never fed to the ingestion pipeline.
    delta = _MARKER_RE.sub("", delta)
    # Remove leading newlines that were adjacent to the stripped marker.
    delta = delta.lstrip("\n")
    return delta


def stamp_processed(path: Path, *, at_pos: int | None = None) -> int:
    """Stamp the file as processed up to *at_pos* bytes (default: current EOF).

    Appends or updates the ``<!-- incubator-processed-pos: N -->`` marker so
    the next pass knows where ingestion left off.  There is always exactly ONE
    marker in the file after this call.

    Idempotency: if there is already a marker and nothing has been appended
    after it (``at_pos`` is ``None``), this is a guaranteed no-op — the file
    is not written and the existing position is returned.

    Parameters
    ----------
    path:
        The inbox file to stamp.
    at_pos:
        Byte offset to record. If ``None``, uses the current raw file length
        (EOF), or returns the existing position when nothing is new.

    Returns
    -------
    The byte offset that was stamped.
    """
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    existing = list(_MARKER_RE.finditer(text))

    if at_pos is not None:
        pos = at_pos
        # Idempotent for explicit at_pos: same position → no-op.
        if existing and int(existing[-1].group(1)) == pos:
            return pos
    elif existing:
        last = existing[-1]
        existing_pos = int(last.group(1))
        # Check for content appended after the last marker.
        after = _MARKER_RE.sub("", text[last.end():]).strip()
        if not after:
            return existing_pos  # Nothing new — idempotent.
        # There is new content: record current EOF as the new processed position.
        pos = len(raw)
    else:
        pos = len(raw)

    marker_str = f"{_MARKER_PREFIX}{pos}{_MARKER_SUFFIX}"

    if existing:
        # Consolidate: remove ALL old markers, preserve content, append new marker.
        clean = _MARKER_RE.sub("", text).rstrip("\n")
        new_text = clean + "\n" + marker_str + "\n"
    else:
        new_text = text.rstrip("\n") + "\n" + marker_str + "\n"

    path.write_bytes(new_text.encode("utf-8"))
    return pos


def clear_stamp(path: Path) -> bool:
    """Remove all processed-pos markers from *path* (resets to CREATE mode).

    Returns True if any markers were removed.
    """
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    new_text, count = _MARKER_RE.subn("", text)
    if count == 0:
        return False
    # Tidy up blank lines left behind.
    new_text = re.sub(r"\n{3,}", "\n\n", new_text).strip() + "\n"
    path.write_text(new_text, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_detect = sub.add_parser("detect", help="Detect CREATE or APPEND mode for a file.")
    p_detect.add_argument("file", type=Path)

    p_extract = sub.add_parser(
        "extract", help="Print only the new content since the last processed position."
    )
    p_extract.add_argument("file", type=Path)

    p_stamp = sub.add_parser("stamp", help="Stamp the file as processed at EOF (or --at).")
    p_stamp.add_argument("file", type=Path)
    p_stamp.add_argument("--at", type=int, default=None, help="Byte offset to stamp (default: EOF).")

    p_clear = sub.add_parser("clear", help="Remove all processed-pos markers (reset to CREATE).")
    p_clear.add_argument("file", type=Path)

    args = parser.parse_args(argv[1:])

    if args.cmd == "detect":
        mode, pos = detect_mode(args.file)
        sys.stdout.write(f"{mode} {pos}\n")

    elif args.cmd == "extract":
        mode, last_pos = detect_mode(args.file)
        content = extract_new_content(args.file, last_pos)
        sys.stdout.write(content)

    elif args.cmd == "stamp":
        pos = stamp_processed(args.file, at_pos=args.at)
        sys.stdout.write(f"stamped at {pos}\n")

    elif args.cmd == "clear":
        removed = clear_stamp(args.file)
        sys.stdout.write(f"{'cleared' if removed else 'no markers found'}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
