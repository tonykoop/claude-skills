#!/usr/bin/env python3
"""Wire the image-gen-2 chapter template into the idea-incubator skill (idempotent).

Completes PR #230: the reference file
`plugins/maker/skills/idea-incubator/references/image-gen-2-chapter-template.md`
is already committed; this routes the skill to it and records the version bump:

  * SKILL.md frontmatter version 1.4.4 -> 1.5.0,
  * SKILL.md rollout routing step + Reference list -> point at the new template,
  * CHANGELOG.md: a 1.5.0 entry.

SKILL.md and CHANGELOG.md use CRLF; this preserves their line endings (line-based,
newline='' I/O) so the diff is just the added lines, not a whole-file reflow.
Running twice is a no-op.
"""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugins" / "maker" / "skills" / "idea-incubator" / "SKILL.md"
CHANGELOG = ROOT / "plugins" / "maker" / "skills" / "idea-incubator" / "CHANGELOG.md"

ROUTING_ANCHOR = "before any downstream repo scaffold, imagegen/layout work, or media import."
REFLIST_ANCHOR = "downstream repo scaffolds, imagegen/layout studies, or media imports."


def _eol(line: str) -> str:
    return "\r\n" if line.endswith("\r\n") else "\n"


def wire_skill() -> int:
    with open(SKILL, newline="") as fh:
        lines = fh.readlines()
    if any("image-gen-2-chapter-template.md" in ln for ln in lines):
        return 0
    out, changed = [], 0
    for ln in lines:
        if ln.lstrip().startswith("version: 1.4.4"):
            out.append(ln.replace("1.4.4", "1.5.0"))
            changed += 1
            continue
        out.append(ln)
        e = _eol(ln)
        if ROUTING_ANCHOR in ln:
            for t in (
                "   For an instrument design-book or yearbook chapter, define and apply the",
                "   chapter template and image-gen-2 asset contract in",
                "   [`references/image-gen-2-chapter-template.md`](references/image-gen-2-chapter-template.md)",
                "   before generating any chapter; a chapter may only follow a packet that",
                "   has passed its repo gates.",
            ):
                out.append(t + e)
            changed += 1
        elif REFLIST_ANCHOR in ln:
            for t in (
                "- [`references/image-gen-2-chapter-template.md`](references/image-gen-2-chapter-template.md)",
                "  - Chapter template + image-gen-2 asset contract for instrument design-book /",
                "    yearbook chapters: packet-first gate, authority-vs-concept two-source rule,",
                "    derivative/non-dimensional asset metadata, and the minimum viable chapter.",
            ):
                out.append(t + e)
            changed += 1
    if changed:
        with open(SKILL, "w", newline="") as fh:
            fh.writelines(out)
    return changed


def wire_changelog() -> int:
    with open(CHANGELOG, newline="") as fh:
        text = fh.read()
    if "## 1.5.0 - 2026-06-16" in text:
        return 0
    e = "\r\n" if "\r\n" in text else "\n"
    entry = e.join([
        "## 1.5.0 - 2026-06-16",
        "",
        "- Added `references/image-gen-2-chapter-template.md`, the shared chapter",
        "  template and image-gen-2 asset contract for instrument design-book and",
        "  yearbook chapters (Refs #92, #100). Defines the packet-first gate, the",
        "  authority-vs-concept two-source rule, the per-asset derivative/",
        "  non-dimensional metadata contract, and the minimum viable chapter.",
        "- Routed the rollout step and reference list in `SKILL.md` to the new template.",
        "", "",
    ])
    header = "# Changelog" + e + e
    if text.startswith(header):
        text = header + entry + text[len(header):]
    else:
        text = entry + text
    with open(CHANGELOG, "w", newline="") as fh:
        fh.write(text)
    return 1


def main() -> None:
    s = wire_skill()
    c = wire_changelog()
    print(f"SKILL.md: {s} insertions; CHANGELOG.md: {c} entry added"
          + (" (already wired)" if s == 0 and c == 0 else ""))


if __name__ == "__main__":
    main()
