#!/usr/bin/env python3
"""Generate range-walk warmup scales for an instrument.

Produces an ABC file with the instrument's full playable range,
ascending and descending, as quarter notes at 80 bpm. Useful as a
00-warmup-scales/ deposit and as a sanity check that the instrument's
registry row has correct range.

Usage:
    python generate_scales.py --instrument naf-6hole --out range-walk.abc
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

NOTE_NAMES = ["C","D","E","F","G","A","B"]


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


def sci_to_abc(sci: str) -> str:
    """C4 -> C, c5 -> c, c6 -> c'  (approximate)."""
    m = re.match(r"^([A-G])([#b]?)(\d)$", sci)
    if not m:
        return ""
    letter = m.group(1)
    accidental = m.group(2)
    octave = int(m.group(3))
    # ABC: capital letters = octave 4, lowercase = octave 5,
    # x' = octave 6, X, = octave 3
    prefix = ""
    if accidental == "#":
        prefix = "^"
    elif accidental == "b":
        prefix = "_"
    if octave <= 3:
        return prefix + letter + ("," * (4 - octave))
    if octave == 4:
        return prefix + letter
    return prefix + letter.lower() + ("'" * (octave - 5))


def all_pitches_in_range(low: str, high: str) -> list[str]:
    """Sci pitch list from low to high inclusive (diatonic, no accidentals)."""
    def to_idx(s: str) -> int:
        m = re.match(r"^([A-G])([#b]?)(\d)$", s)
        if not m:
            return -1
        base = "CDEFGAB".index(m.group(1))
        return int(m.group(3)) * 7 + base

    out: list[str] = []
    lo, hi = to_idx(low), to_idx(high)
    if lo < 0 or hi < 0 or hi < lo:
        return out
    for idx in range(lo, hi + 1):
        octave, base = divmod(idx, 7)
        out.append(f"{NOTE_NAMES[base]}{octave}")
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--instrument", required=True)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--tempo", type=int, default=80)
    args = p.parse_args()

    row = load_registry_row(args.instrument)
    if row is None:
        sys.exit(f"unknown instrument: {args.instrument}")

    low = row.get("range_low", "")
    high = row.get("range_high", "")
    if not low or not high or low == "~":
        # unpitched percussion — write a stroke pattern instead
        write_percussion_warmup(args.out, args.instrument, row)
        return

    pitches = all_pitches_in_range(low, high)
    abc_notes = [sci_to_abc(s) for s in pitches]
    asc = " ".join(abc_notes)
    desc = " ".join(reversed(abc_notes))

    abc = f"""X:1
T:Range Walk — {row.get("display_name", args.instrument)}
C:Tony Koop / sheet-music skill (warmup)
M:4/4
L:1/4
Q:1/4={args.tempo}
K:{row.get("key_default", "C")}
% Ascending
{asc} |
% Descending
{desc} |
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(abc)
    print(f"  range-walk -> {args.out} ({len(pitches)} pitches)")


def write_percussion_warmup(out: Path, instrument_id: str, row: dict):
    body = f"""# Warmup pattern — {row.get("display_name", instrument_id)}

Pattern: stroke vocabulary drill, 4/4, ♩=80
Beat:    1 . . . | 2 . . . | 3 . . . | 4 . . . |
Stroke:  B . T . | B . T . | S . T . | S . T O |

Run this for 8 bars at 60 bpm, then 8 bars at 80 bpm. Goal: clean
distinct strokes, even spacing.
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    # write a markdown file with the same stem
    md_path = out.with_suffix(".md")
    md_path.write_text(body)
    print(f"  percussion warmup -> {md_path}")


if __name__ == "__main__":
    main()
