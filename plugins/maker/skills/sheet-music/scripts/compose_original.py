#!/usr/bin/env python3
"""Scaffold an original tune for a specific instrument.

This script does NOT compose the tune by itself. It produces a scaffold
ABC file with the right headers, scale, range markers, and structural
template, then prints instructions for Claude (the orchestrator) to
fill in the notes following the family-reference rules.

The compose-then-fill split keeps determinism in the scaffold and
creativity in the LLM step. The scaffold outputs the same headers and
target metadata every time; the LLM fills in the actual melody.

Usage:
    python compose_original.py \\
        --instrument fujara \\
        --slug shepherds-overtone \\
        --mood "slow, contemplative, shepherd-song" \\
        --form AABA \\
        --out catalog/original/shepherds-overtone/

The output folder gets:
  tune.abc        with headers + a TODO marker for the LLM
  notes.md        with composition brief
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_registry_row(instrument_id: str) -> dict | None:
    text = (REPO_ROOT / "instruments" / "registry.yaml").read_text()
    marker = f"id: {instrument_id}"
    if marker not in text:
        return None
    block = text.split(marker, 1)[1].split("- id:", 1)[0]
    row = {"id": instrument_id}
    for line in block.splitlines():
        ln = line.strip()
        if not ln or ln.startswith("#") or ":" not in ln:
            continue
        k, v = ln.split(":", 1)
        v = v.split("#")[0].strip().strip("'\"")
        if v in ("|", ""):
            continue
        row[k.strip()] = v
    return row


def title_from_slug(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.split("-"))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--instrument", required=True)
    p.add_argument("--slug", required=True,
                   help="folder/title slug, e.g. 'river-reed-waltz'")
    p.add_argument("--mood", default="",
                   help="brief mood description for the LLM step")
    p.add_argument("--form", default="AABA",
                   help="structural form: AABA, ABAB, AAB, through-composed")
    p.add_argument("--out", required=True, type=Path,
                   help="output directory")
    p.add_argument("--tempo", type=int, default=90)
    p.add_argument("--meter", default="4/4")
    args = p.parse_args()

    row = load_registry_row(args.instrument)
    if row is None:
        sys.exit(f"unknown instrument: {args.instrument}")

    args.out.mkdir(parents=True, exist_ok=True)
    title = title_from_slug(args.slug)

    abc = f"""X:1
T:{title}
C:Heifer Zephyr / Tony Koop ({date.today().year})
S:Original — MIT-licensed within sheet-music repo
M:{args.meter}
L:1/8
Q:1/4={args.tempo}
K:{row.get("key_default", "C")}
H:Composed for {row.get("display_name", args.instrument)}.
H:Range: {row.get("range_low", "?")} - {row.get("range_high", "?")}.
H:Scale: {row.get("scale", "?")}.
H:Form: {args.form}.
% TODO(LLM): write the melody in {args.form} form using only pitches in
% the {row.get("scale", "?")} scale within the instrument's range.
% Mood: {args.mood or "(unset)"}.
% Each section (A, B, etc.) should be 4 or 8 bars.
% Use ornaments idiomatic to {row.get("family", "?")} family — see
% references/{row.get("family", "?")}-family.md or
% references/{row.get("family", "?")}.md.
"""
    (args.out / "tune.abc").write_text(abc)

    notes = f"""# {title}

Original Heifer Zephyr commission for the
{row.get("display_name", args.instrument)}.

## Brief

- **Instrument:** {row.get("display_name", args.instrument)} ({args.instrument})
- **Range:** {row.get("range_low", "?")} – {row.get("range_high", "?")}
- **Default key:** {row.get("key_default", "?")}
- **Scale:** {row.get("scale", "?")}
- **Mood:** {args.mood or "(unset)"}
- **Form:** {args.form}
- **Tempo:** ♩ = {args.tempo}
- **Meter:** {args.meter}
- **Build repo:** {row.get("build_repo", "tonykoop/" + args.instrument)}

## Composition status

`tune.abc` is a scaffold. The melody itself is `TODO`. To complete:

1. Read `references/{row.get("family", "?")}-family.md` (or the
   percussion / reeds-and-pipes equivalent) for the relevant idiom.
2. Compose the melody section by section. Each section (A, B, etc.)
   should be 4 or 8 bars and use only pitches in the declared scale,
   within the instrument's range.
3. Add idiom-appropriate ornaments — sparingly for beginner songbooks.
4. Run `scripts/validate_arrangement.py --tune tune.abc --instrument
   {args.instrument} --strict` to confirm range and headers are clean.
5. Run `scripts/render_pipeline.py --tune tune.abc --instrument
   {args.instrument} --out .` to generate all derivatives.

## License

MIT — same as the rest of `sheet-music`. The original tune is yours
to perform, record, arrange, and adapt.

## Practice tip

(Add at least one practice tip after the melody is written.)
"""
    (args.out / "notes.md").write_text(notes)

    print(f"  scaffold -> {args.out}/tune.abc (TODO marker for LLM)")
    print(f"  brief    -> {args.out}/notes.md")
    print(f"\nNext: have Claude fill in the melody following the brief above.")


if __name__ == "__main__":
    main()
