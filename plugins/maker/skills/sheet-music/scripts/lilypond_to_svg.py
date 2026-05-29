#!/usr/bin/env python3
"""Render a LilyPond file to SVG using the lilypond binary.

The SVG is what build_songsheet_pdf.py uses for the engraved-notation
block on the printable songsheet. Without LilyPond on PATH, this step
is skipped and the songsheet shows a placeholder.

Usage:
    python lilypond_to_svg.py --ly tune.ly --out tune.svg
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ly", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()

    if not args.ly.exists():
        sys.exit(f"missing lilypond input: {args.ly}")
    if shutil.which("lilypond") is None:
        sys.exit("lilypond not on PATH. Install LilyPond to render SVG/PDF.")

    args.out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        try:
            subprocess.run([
                "lilypond", "-dbackend=svg", "-o", str(td_path / "out"),
                str(args.ly),
            ], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            sys.exit(f"lilypond failed: {e.stderr}")

        # LilyPond produces out.svg or out-1.svg (and possibly out-2.svg, ...)
        svgs = sorted(td_path.glob("out*.svg"))
        if not svgs:
            sys.exit("lilypond produced no SVG output")
        # Use the first page only for one-page songsheets
        first = svgs[0]
        first.replace(args.out)
    print(f"  lilypond -> {args.out}")


if __name__ == "__main__":
    main()
