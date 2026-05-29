#!/usr/bin/env python3
"""Build the ableton-prompt.md handoff file for a tune.

This produces the ready-to-paste prompt the user drops into a
Claude+Ableton connector session. The prompt names the tempo, key,
instrument timbre, and track structure based on the tune's ABC headers
and the registry row for the target instrument.

See references/ableton-handoff.md for the template details.

Usage:
    python build_ableton_handoff.py \\
        --tune-dir learn-to-play/01-easy/twinkle-twinkle/ \\
        --instrument naf-6hole
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DRONE_FAMILIES = {"flute"}  # rough heuristic — drone-flute, NAF, andean often want a drone
DRONE_IDS = {"naf-6hole", "drone-flute", "duduk", "fujara", "moseno", "kena"}


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


def get_abc_headers(abc_path: Path) -> dict:
    headers: dict[str, str] = {}
    if not abc_path.exists():
        return headers
    for line in abc_path.read_text().splitlines():
        if len(line) > 1 and line[1] == ":":
            headers.setdefault(line[0], line[2:].strip())
        else:
            break
    return headers


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tune-dir", required=True, type=Path)
    p.add_argument("--instrument", required=True)
    args = p.parse_args()

    tune_dir = args.tune_dir
    abc = get_abc_headers(tune_dir / "tune.abc")
    row = load_registry_row(args.instrument)
    if row is None:
        sys.exit(f"unknown instrument: {args.instrument}")

    title = abc.get("T", "Untitled")
    tempo = abc.get("Q", "1/4=90")
    tempo_num = re.search(r"=(\d+)", tempo)
    tempo_bpm = tempo_num.group(1) if tempo_num else "90"
    key = abc.get("K", row.get("key_default", "C"))
    meter = abc.get("M", "4/4")

    # Choose timbre description
    timbre_map = {
        76: "warm pan-flute or shakuhachi pad",
        74: "concert flute, slightly breathy",
        75: "wooden recorder, narrow tone",
        41: "solo violin with light vibrato",
        47: "concert harp, intimate (close-miked)",
        25: "fingerpicked steel-string acoustic guitar",
        28: "clean electric guitar, jazz-amp tone",
        72: "warm clarinet, mid-register",
        110: "duduk-style double-reed pad",
        13: "soft mallet marimba",
        116: "mellow steel-pan / handpan",
    }
    preset = int(row.get("soundfont_preset", "74") or "74")
    timbre = timbre_map.get(preset, "instrument-appropriate timbre")

    drone_block = ""
    if args.instrument in DRONE_IDS:
        drone_block = (
            "2. Drone — sustained tonic pad on the home key, low register, "
            "slow attack, very long release. Continuous through the tune.\n"
        )
    metronome_block = (
        "3. Metronome — quiet click on beats 1 and 3 (or whatever fits the meter), "
        "right channel, -12 dB.\n"
    )
    backing_block = (
        "4. Backing pad — root + fifth on each phrase boundary, low register, "
        "slow attack, long release. Use a soft pad sound.\n"
    )

    prompt = f"""# Ableton Live handoff — {title}

Paste the block below into a Claude session that has the Ableton
connector enabled. Attach `tune.mid` and `tune.musicxml` from this
folder.

---

I'd like to build an Ableton Live project for "{title}" — arranged for
the {row.get("display_name", args.instrument)} from Tony Koop's
`{row.get("build_repo", "tonykoop/" + args.instrument)}` build. Use
the attached MIDI and MusicXML as the starting point.

Project requirements:
- Tempo: {tempo_bpm} bpm
- Key: {key}
- Time signature: {meter}

Tracks:
1. Melody — load a software instrument that approximates a {timbre}.
   Set the MIDI clip from tune.mid.
{drone_block}{metronome_block}{backing_block}

Mix:
- Melody centered, +0 dB.
- Drone (if present) centered, -6 dB.
- Metronome panned right, -12 dB.
- Backing pad panned slightly left, -8 dB.

Add a slow plate reverb (1.5 s decay, 20% wet) on the master bus.

Save the project as `{tune_dir.name}.als` in the same folder as this
prompt.
"""

    out = tune_dir / "ableton-prompt.md"
    out.write_text(prompt)
    print(f"  ableton-prompt -> {out}")


if __name__ == "__main__":
    main()
