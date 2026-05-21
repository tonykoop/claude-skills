#!/usr/bin/env python3
"""Convert an ABC file to MusicXML via music21.

Usage:
    python abc_to_musicxml.py --tune tune.abc --out tune.musicxml

MusicXML is the format Ableton, Logic, MuseScore, and Sibelius all
import cleanly. The Ableton handoff (`references/ableton-handoff.md`)
expects this file alongside the MIDI.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tune", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()

    if not args.tune.exists():
        sys.exit(f"missing tune: {args.tune}")

    try:
        from music21 import converter
    except ImportError:
        sys.exit("music21 not installed. pip install music21")

    args.out.parent.mkdir(parents=True, exist_ok=True)

    try:
        score = converter.parse(str(args.tune), format="abc")
        score.write("musicxml", fp=str(args.out))
    except Exception as e:
        sys.exit(f"music21 conversion failed: {e}")

    print(f"  music21 -> {args.out}")


if __name__ == "__main__":
    main()
