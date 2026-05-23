#!/usr/bin/env python3
"""Render a MIDI file to WAV (and optionally MP3) audio.

Pipeline:
  1. fluidsynth + soundfont (.sf2) -> WAV  (preferred)
  2. timidity                       -> WAV  (fallback)
  3. label "skipped" if neither    available

If WAV was produced and ffmpeg is available, also writes MP3.

Usage:
    python render_audio.py --midi tune.mid --instrument naf-6hole --out tune.wav

Soundfont selection:
  - If --soundfont is given, use it.
  - Else look for assets/soundfonts/*.sf2 in this repo.
  - Else look for /usr/share/sounds/sf2/FluidR3_GM.sf2 (Linux default).
  - Else fail with a clear message pointing at references/audio-rendering.md.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SF_PATHS = [
    REPO_ROOT / "assets" / "soundfonts",
    Path("/usr/share/sounds/sf2"),
    Path("/usr/share/soundfonts"),
    Path.home() / "soundfonts",
]


def find_soundfont(explicit: Path | None) -> Path | None:
    if explicit:
        return explicit if explicit.exists() else None
    for d in DEFAULT_SF_PATHS:
        if not d.exists():
            continue
        for sf in d.glob("*.sf2"):
            return sf
        for sf in d.glob("*.sf3"):
            return sf
    return None


def via_fluidsynth(midi: Path, wav: Path, sf: Path) -> bool:
    if shutil.which("fluidsynth") is None:
        return False
    try:
        subprocess.run([
            "fluidsynth", "-ni", "-F", str(wav),
            "-r", "44100", str(sf), str(midi),
        ], check=True, capture_output=True, text=True)
        return wav.exists()
    except subprocess.CalledProcessError as e:
        print(f"fluidsynth failed: {e.stderr}", file=sys.stderr)
        return False


def via_timidity(midi: Path, wav: Path) -> bool:
    if shutil.which("timidity") is None:
        return False
    try:
        subprocess.run([
            "timidity", str(midi), "-Ow", "-o", str(wav),
        ], check=True, capture_output=True, text=True)
        return wav.exists()
    except subprocess.CalledProcessError as e:
        print(f"timidity failed: {e.stderr}", file=sys.stderr)
        return False


def make_mp3(wav: Path) -> Path | None:
    if shutil.which("ffmpeg") is None:
        return None
    mp3 = wav.with_suffix(".mp3")
    try:
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(wav), "-codec:a", "libmp3lame",
            "-qscale:a", "2", str(mp3),
        ], check=True, capture_output=True, text=True)
        return mp3 if mp3.exists() else None
    except subprocess.CalledProcessError:
        return None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--midi", required=True, type=Path)
    p.add_argument("--instrument", required=True,
                   help="instrument id (used for soundfont preset selection)")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--soundfont", type=Path,
                   help="path to a .sf2 soundfont; default searches common dirs")
    p.add_argument("--no-mp3", action="store_true",
                   help="skip MP3 conversion even if ffmpeg is available")
    args = p.parse_args()

    if not args.midi.exists():
        sys.exit(f"missing midi: {args.midi}")
    args.out.parent.mkdir(parents=True, exist_ok=True)

    sf = find_soundfont(args.soundfont)

    if sf and via_fluidsynth(args.midi, args.out, sf):
        print(f"  fluidsynth + {sf.name} -> {args.out}")
    elif via_timidity(args.midi, args.out):
        print(f"  timidity -> {args.out}")
    else:
        sys.exit(
            "audio rendering skipped: no working renderer.\n"
            "Options:\n"
            "  - install fluidsynth and a soundfont "
            "(see references/audio-rendering.md)\n"
            "  - install timidity\n"
            "MIDI is at: " + str(args.midi)
        )

    if not args.no_mp3:
        mp3 = make_mp3(args.out)
        if mp3:
            print(f"  ffmpeg -> {mp3}")
        else:
            print("  mp3: skipped (ffmpeg not available)")


if __name__ == "__main__":
    main()
