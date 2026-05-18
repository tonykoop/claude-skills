#!/usr/bin/env python3
"""Patch the canonical instrument-maker-v4 SKILL.md with v4.5 rig routing.

The claude-skills repo currently carries a partial instrument-maker-v4
entry. References and templates can be copied into the canonical install,
but issue #107 also needs runtime-facing routing behavior in the invoked
SKILL.md. This helper inserts or refreshes that block idempotently.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


START = "<!-- instrument-maker-v4:v4.5-experimental-rig-routing:start -->"
END = "<!-- instrument-maker-v4:v4.5-experimental-rig-routing:end -->"

BLOCK = f"""{START}
## v4.5 Experimental Acoustic Rig Routing

When a prompt asks for a yaybahar-style instrument, coupled
string-spring-membrane system, resonance test bed, experimental acoustic
apparatus, or unknown hybrid resonator, produce a **bench-rig packet
before a performance-instrument packet**.

Read `references/experimental-acoustic-rigs.md` before designing the
performance form. Seed the bench-rig packet with:

- `README.md`
- `variable-matrix.csv`
- `measurement-log-template.csv`
- `sensor-capture-checklist.md`
- `stored-energy-safety-checklist.md`
- `validation-plan.md`
- `risks.md`

Treat isolated string, spring, membrane, bridge, frame, or cavity
formulas as local estimates only. The coupled behavior must be measured
before locking scale length, spring count, membrane diameter, bridge
material, pickup placement, or performance ergonomics.
{END}
"""


def patch_text(text: str) -> tuple[str, bool]:
    block = BLOCK.rstrip()
    if START in text and END in text:
        start_index = text.index(START)
        end_index = text.index(END) + len(END)
        before = text[:start_index].rstrip()
        after = text[end_index:].lstrip()
        updated = f"{before}\n\n{block}\n\n{after}".rstrip() + "\n"
        return updated, updated != text

    anchor = "## Core Workflow"
    if anchor in text:
        before, after = text.split(anchor, 1)
        updated = f"{before.rstrip()}\n\n{block}\n\n{anchor}{after}".rstrip() + "\n"
        return updated, True

    updated = f"{text.rstrip()}\n\n{block}\n"
    return updated, True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Insert v4.5 experimental rig routing into canonical SKILL.md."
    )
    parser.add_argument("skill_md", type=Path, help="Path to canonical SKILL.md")
    parser.add_argument("--check", action="store_true",
                        help="Report whether the file is already patched without writing.")
    args = parser.parse_args(argv)

    if not args.skill_md.is_file():
        print(f"SKILL.md not found: {args.skill_md}", file=sys.stderr)
        return 2

    text = args.skill_md.read_text(encoding="utf-8")
    updated, changed = patch_text(text)

    if args.check:
        print("patched" if not changed else "needs patch")
        return 1 if changed else 0

    if changed:
        args.skill_md.write_text(updated, encoding="utf-8")
        print(f"patched {args.skill_md}")
    else:
        print(f"already patched {args.skill_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
