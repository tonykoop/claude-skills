#!/usr/bin/env python3
"""Render a tune through every available format.

Pipeline stages, in order:

  1. abc_to_lilypond.py    -> tune.ly
  2. abc_to_musicxml.py    -> tune.musicxml
  3. abc_to_midi.py        -> tune.mid
  4. render_fingering_svg  -> tune-fingering.svg
  5. render_audio.py       -> tune.wav (and optionally tune.mp3)
  6. build_songsheet_pdf   -> tune.pdf

Each stage checks for its dependencies and degrades gracefully. Stages
that can't run print "skipped: <reason>" and the pipeline continues.

Usage
-----
    python render_pipeline.py \\
        --tune catalog/public-domain/nursery/twinkle-twinkle/tune.abc \\
        --instrument naf-6hole \\
        --out /tmp/twinkle/

Required:
    --tune          path to a canonical .abc file
    --instrument    instrument id (matches instruments/registry.yaml)

Optional:
    --out           output directory (default: alongside the tune)
    --skip          comma-separated list of stages to skip
    --strict        fail on any stage error (default: continue)
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"


def stage(name: str):
    def decorator(fn):
        fn._stage_name = name
        return fn
    return decorator


def run_subscript(script: str, *args: str, capture: bool = False) -> tuple[bool, str]:
    """Run another script in this repo. Returns (success, stdout-or-error)."""
    cmd = [sys.executable, str(SCRIPTS / script), *args]
    try:
        proc = subprocess.run(
            cmd, capture_output=capture, text=True, check=False
        )
        ok = proc.returncode == 0
        out = (proc.stdout or "") + (proc.stderr or "") if capture else ""
        return ok, out
    except FileNotFoundError as e:
        return False, f"script not found: {e}"


def have(binary: str) -> bool:
    return shutil.which(binary) is not None


def have_python_module(name: str) -> bool:
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def render(tune: Path, instrument: str, out_dir: Path,
           skip: set[str], strict: bool) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Always copy the canonical ABC into the output dir
    canonical = out_dir / "tune.abc"
    if canonical.resolve() != tune.resolve():
        shutil.copy2(tune, canonical)

    results = {"tune": str(tune), "instrument": instrument, "stages": {}}

    stages = [
        ("lilypond",    "abc_to_lilypond.py", ["--tune", str(canonical),
                                                "--out", str(out_dir / "tune.ly")]),
        ("musicxml",    "abc_to_musicxml.py", ["--tune", str(canonical),
                                                "--out", str(out_dir / "tune.musicxml")]),
        ("midi",        "abc_to_midi.py",     ["--tune", str(canonical),
                                                "--instrument", instrument,
                                                "--out", str(out_dir / "tune.mid")]),
        ("fingering",   "render_fingering_svg.py", ["--tune", str(canonical),
                                                    "--instrument", instrument,
                                                    "--out", str(out_dir / "tune-fingering.svg")]),
        ("audio",       "render_audio.py",    ["--midi", str(out_dir / "tune.mid"),
                                                "--instrument", instrument,
                                                "--out", str(out_dir / "tune.wav")]),
        ("svg-staff",   "lilypond_to_svg.py", ["--ly", str(out_dir / "tune.ly"),
                                                "--out", str(out_dir / "tune.svg")]),
        ("songsheet",   "build_songsheet_pdf.py", ["--tune-dir", str(out_dir),
                                                    "--instrument", instrument,
                                                    "--out", str(out_dir / "tune.pdf")]),
    ]

    for name, script, args in stages:
        if name in skip:
            results["stages"][name] = {"status": "skipped (--skip)", "ok": None}
            continue
        ok, out = run_subscript(script, *args, capture=True)
        results["stages"][name] = {
            "status": "ok" if ok else "error",
            "ok": ok,
            "log": out.strip()[-400:] if not ok else "",
        }
        marker = "✓" if ok else "✗"
        print(f"  [{marker}] {name:10s}  {results['stages'][name]['log'][:120]}")
        if not ok and strict:
            print(f"\nstrict mode: stopping at {name}")
            break

    summary_path = out_dir / "render-summary.json"
    summary_path.write_text(json.dumps(results, indent=2))
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tune", required=True, type=Path,
                   help="path to canonical .abc")
    p.add_argument("--instrument", required=True,
                   help="instrument id from registry.yaml")
    p.add_argument("--out", type=Path,
                   help="output directory (default: alongside the tune)")
    p.add_argument("--skip", default="",
                   help="comma-separated stages to skip")
    p.add_argument("--strict", action="store_true",
                   help="fail on any stage error")
    args = p.parse_args()

    tune = args.tune
    if not tune.exists():
        sys.exit(f"tune file not found: {tune}")

    out_dir = args.out or tune.parent
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}

    print(f"sheet-music render pipeline")
    print(f"  tune:       {tune}")
    print(f"  instrument: {args.instrument}")
    print(f"  out:        {out_dir}")
    print()

    results = render(tune, args.instrument, out_dir, skip, args.strict)

    print()
    ok_count = sum(1 for s in results["stages"].values() if s["ok"])
    total = len(results["stages"])
    print(f"done: {ok_count}/{total} stages succeeded")
    print(f"summary: {out_dir / 'render-summary.json'}")


if __name__ == "__main__":
    main()
