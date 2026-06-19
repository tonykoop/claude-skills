#!/usr/bin/env python3
"""Pre-read prior lessons before a brainstorm parse.

Refs #241 (Epic #235). Captured lessons are worthless if they aren't read at
the right moment. Before the parser breaks a new brainstorm into epics/stories,
this loader pulls the relevant lessons from the Institutional Knowledge store
(written by the #240 retrospective sweep) and renders a compact "prior lessons
to honor" block to prepend to the parse prompt — so the team never repeats a
mistake it already learned from.

Relevance is scoped, not flooded: lessons are ranked by how many of their
`Applies-to` tags intersect the draft's tags, the top-N are kept, and if nothing
matches it falls back to the small set of cross-cutting `general` lessons. The
loader degrades gracefully when the store file and the per-epic folder are empty
or missing (it emits an explicit "no prior lessons" note instead of failing).

Inputs:
  * the aggregate store `references/institutional-knowledge.md` (curated index);
  * optionally, per-epic notes under `references/institutional-knowledge/`
    (the folder produced by the retrospective sweep), included when present.

CLI:
    prior_lessons_preread.py --tags promote,lfs [--limit 5]
    prior_lessons_preread.py --brainstorm doc.md           # naive tag derivation
    prior_lessons_preread.py --tags maker --store path.md --folder dir/

Exit 0 always (graceful): an empty result is a valid, expected outcome.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STORE = SKILL_ROOT / "references" / "institutional-knowledge.md"
DEFAULT_FOLDER = SKILL_ROOT / "references" / "institutional-knowledge"

# The controlled vocabulary used by Applies-to tags (mirrors the store doc).
KNOWN_TAGS = [
    "instrument", "woodworking", "sheet-metal", "electronics", "firmware",
    "software", "maker", "skills", "yoga",
    "capture", "intake", "promote", "promote-batch", "estimation",
    "dependencies", "lfs", "provenance", "general",
]

ENTRY_HEADER = re.compile(r"^###\s+(.*\S)\s*$")
FIELD = re.compile(r"^\s*[-*]\s*\*\*(Context|Lesson|Applies-to|Source):\*\*\s*(.*)$")


@dataclass
class Lesson:
    title: str
    context: str = ""
    lesson: str = ""
    applies_to: list = field(default_factory=list)
    source: str = ""


def _commit_field(lesson: Lesson, key: str, value: str) -> None:
    value = " ".join(value.split())  # collapse wrapped whitespace
    if key == "Context":
        lesson.context = value
    elif key == "Lesson":
        lesson.lesson = value
    elif key == "Applies-to":
        lesson.applies_to = [t.strip().lower() for t in value.split(",") if t.strip()]
    elif key == "Source":
        lesson.source = value


def parse_store(text: str) -> list[Lesson]:
    """Parse `### title` + bold-field entries into Lesson records.

    Field values may wrap across several physical lines (the store hard-wraps
    prose); continuation lines are folded into the current field until the next
    field bullet or heading.
    """
    lessons: list[Lesson] = []
    current: Lesson | None = None
    field_key: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal field_key, buffer
        if current is not None and field_key is not None:
            _commit_field(current, field_key, " ".join(buffer))
        field_key, buffer = None, []

    for line in text.splitlines():
        header = ENTRY_HEADER.match(line)
        if header:
            flush()
            current = Lesson(title=header.group(1).strip())
            lessons.append(current)
            continue
        if current is None:
            continue
        m = FIELD.match(line)
        if m:
            flush()
            field_key, buffer = m.group(1), [m.group(2).strip()]
            continue
        if field_key is not None and line.strip() and not line.lstrip().startswith(("-", "*", "#")):
            buffer.append(line.strip())  # wrapped continuation of the current field
        else:
            flush()
    flush()
    # Keep only entries that actually carry a lesson (skip stray ### headings).
    return [le for le in lessons if le.lesson]


def normalize_tags(raw: list[str]) -> list[str]:
    return [t.strip().lower() for t in raw if t.strip()]


def derive_tags(brainstorm_text: str, vocab: list[str] = KNOWN_TAGS) -> list[str]:
    """Naive tag derivation: which known vocab tags appear in the text."""
    low = brainstorm_text.lower()
    return [t for t in vocab if t != "general" and t in low]


def select_lessons(lessons: list[Lesson], draft_tags: list[str], limit: int) -> list[Lesson]:
    """Rank lessons by tag overlap with the draft; cap to `limit`.

    Falls back to `general`-tagged lessons when nothing else overlaps, so the
    parse always honors cross-cutting lessons even on an unfamiliar brainstorm.
    """
    draft = set(normalize_tags(draft_tags))
    scored = []
    for idx, le in enumerate(lessons):
        overlap = len(draft.intersection(le.applies_to))
        if overlap > 0:
            scored.append((overlap, -idx, le))
    if scored:
        scored.sort(reverse=True)
        return [le for _, _, le in scored[:limit]]
    # Fallback: cross-cutting general lessons, in store order.
    general = [le for le in lessons if "general" in le.applies_to]
    return general[:limit]


def render_block(selected: list[Lesson], draft_tags: list[str]) -> str:
    tags_str = ", ".join(normalize_tags(draft_tags)) or "(none derived)"
    if not selected:
        return (
            "## Prior lessons to honor\n\n"
            f"_Draft tags: {tags_str}._\n\n"
            "No prior lessons matched — the Institutional Knowledge store is empty, "
            "missing, or has nothing relevant. Proceed without prior-lesson injection.\n"
        )
    lines = [
        "## Prior lessons to honor",
        "",
        f"_Draft tags: {tags_str}. Loaded {len(selected)} lesson(s) by tag overlap._",
        "",
        "Let these shape splitting, labeling, scoping, and which stories to pre-flag "
        "for the Devil's Advocate. When a lesson changes a decision, cite it in the "
        "generated epic (\"applied lesson: <title>\") so the choice is auditable.",
        "",
    ]
    for le in selected:
        tags = ", ".join(le.applies_to)
        lines.append(f"### {le.title}")
        lines.append(f"- **Lesson:** {le.lesson}")
        if le.context:
            lines.append(f"- **Context:** {le.context}")
        lines.append(f"- **Applies-to:** {tags}")
        if le.source:
            lines.append(f"- **Source:** {le.source}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def load_lessons(store: Path, folder: Path | None) -> list[Lesson]:
    """Load lessons from the aggregate store plus any per-epic folder notes."""
    lessons: list[Lesson] = []
    if store.exists():
        lessons.extend(parse_store(store.read_text(encoding="utf-8")))
    if folder is not None and folder.is_dir():
        for note in sorted(folder.glob("epic-*-retro.md")):
            lessons.extend(parse_store(note.read_text(encoding="utf-8")))
    return lessons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pre-read prior lessons for a brainstorm parse.")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--tags", help="Comma-separated draft tags.")
    src.add_argument("--brainstorm", help="Brainstorm file to derive tags from.")
    parser.add_argument("--store", default=str(DEFAULT_STORE), help="Aggregate store path.")
    parser.add_argument("--folder", default=str(DEFAULT_FOLDER), help="Per-epic notes folder.")
    parser.add_argument("--limit", type=int, default=5, help="Max lessons to inject.")
    args = parser.parse_args(argv)

    if args.tags:
        draft_tags = normalize_tags(args.tags.split(","))
    else:
        try:
            text = Path(args.brainstorm).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        draft_tags = derive_tags(text)

    lessons = load_lessons(Path(args.store), Path(args.folder))
    selected = select_lessons(lessons, draft_tags, args.limit)
    sys.stdout.write(render_block(selected, draft_tags))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
