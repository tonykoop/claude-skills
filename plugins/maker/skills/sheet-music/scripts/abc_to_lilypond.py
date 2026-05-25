#!/usr/bin/env python3
"""Convert an ABC file to LilyPond.

Tries music21 first; falls back to abc2ly (part of LilyPond) if
available. If neither, exits with a clear error.

Usage:
    python abc_to_lilypond.py --tune tune.abc --out tune.ly
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def via_music21(abc_path: Path, ly_path: Path) -> bool:
    try:
        from music21 import converter
    except ImportError:
        return False
    try:
        score = converter.parse(str(abc_path), format="abc")
        score.write("lilypond", fp=str(ly_path))
        return ly_path.exists()
    except Exception as e:
        print(f"music21 path failed: {e}", file=sys.stderr)
        return False


def via_abc2ly(abc_path: Path, ly_path: Path) -> bool:
    if shutil.which("abc2ly") is None:
        return False
    try:
        subprocess.run(
            ["abc2ly", "-o", str(ly_path), str(abc_path)],
            check=True, capture_output=True, text=True,
        )
        return ly_path.exists()
    except subprocess.CalledProcessError as e:
        print(f"abc2ly failed: {e.stderr}", file=sys.stderr)
        return False


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tune", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()

    if not args.tune.exists():
        sys.exit(f"missing tune: {args.tune}")
    args.out.parent.mkdir(parents=True, exist_ok=True)

    if via_music21(args.tune, args.out):
        print(f"  music21 -> {args.out}")
        return
    if via_abc2ly(args.tune, args.out):
        print(f"  abc2ly  -> {args.out}")
        return

    sys.exit("no LilyPond converter worked. Install music21 "
             "(pip install music21) or LilyPond (provides abc2ly).")


if __name__ == "__main__":
    main()
