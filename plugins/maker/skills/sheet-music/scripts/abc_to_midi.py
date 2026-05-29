#!/usr/bin/env python3
"""Convert an ABC file to MIDI.

Tries, in order:
  1. music21 (preferred, full ABC feature support)
  2. abc2midi (fast command-line tool, part of abcMIDI)
  3. minimal pure-stdlib fallback (single-voice, no ornaments)

Usage:
    python abc_to_midi.py --tune tune.abc --instrument naf-6hole --out tune.mid

The --instrument flag is used to look up the General MIDI program
number from instruments/registry.yaml so the MIDI file uses an
instrument-appropriate timbre when played back.
"""
from __future__ import annotations

import argparse
import shutil
import struct
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_registry():
    """Tiny YAML reader. Avoids requiring PyYAML for this module."""
    try:
        import yaml  # type: ignore
        return yaml.safe_load(
            (REPO_ROOT / "instruments" / "registry.yaml").read_text()
        )
    except ImportError:
        # Very-very-tiny YAML extraction. Just grabs the soundfont_preset
        # for a given id without parsing the whole file.
        return None


def soundfont_preset_for(instrument_id: str, default: int = 74) -> int:
    """Look up the GM preset number for an instrument id."""
    reg = load_registry()
    if reg is None:
        # Fallback: text-search the YAML for the relevant block
        text = (REPO_ROOT / "instruments" / "registry.yaml").read_text()
        marker = f"id: {instrument_id}"
        if marker not in text:
            return default
        block = text.split(marker, 1)[1].split("- id:", 1)[0]
        for line in block.splitlines():
            if "soundfont_preset:" in line:
                val = line.split(":", 1)[1].strip().split("#")[0].strip()
                if val and val != "~":
                    try:
                        return int(val)
                    except ValueError:
                        return default
        return default

    for family, rows in reg.items():
        for row in rows:
            if row.get("id") == instrument_id:
                preset = row.get("soundfont_preset")
                return int(preset) if preset else default
    return default


def via_music21(abc_path: Path, midi_path: Path, preset: int) -> bool:
    try:
        from music21 import converter, instrument as m21_instrument
    except ImportError:
        return False
    try:
        score = converter.parse(str(abc_path), format="abc")
        # Set program for every part
        for part in score.parts if hasattr(score, "parts") else [score]:
            inst = m21_instrument.Instrument()
            inst.midiProgram = max(0, min(127, preset - 1))  # GM is 1-128, MIDI is 0-127
            part.insert(0, inst)
        score.write("midi", fp=str(midi_path))
        return midi_path.exists()
    except Exception as e:
        print(f"music21 path failed: {e}", file=sys.stderr)
        return False


def via_abc2midi(abc_path: Path, midi_path: Path) -> bool:
    if shutil.which("abc2midi") is None:
        return False
    try:
        subprocess.run(
            ["abc2midi", str(abc_path), "-o", str(midi_path)],
            check=True, capture_output=True, text=True,
        )
        return midi_path.exists()
    except subprocess.CalledProcessError as e:
        print(f"abc2midi failed: {e.stderr}", file=sys.stderr)
        return False


# --- Fallback: pure-stdlib minimal ABC -> MIDI -----------------------------

PITCH_TO_MIDI = {
    "C": 60, "D": 62, "E": 64, "F": 65, "G": 67, "A": 69, "B": 71,
}


def _parse_minimal_abc(abc: str) -> tuple[list[tuple[int, float]], int, int]:
    """Yields (midi_pitch_or_-1_for_rest, beats) along with tempo and L."""
    notes = []
    tempo = 90  # quarter note bpm
    default_length = 4  # 1/4
    meter_num, meter_den = 4, 4

    body_lines = []
    in_body = False
    for raw in abc.splitlines():
        line = raw.strip()
        if not line or line.startswith("%"):
            continue
        if not in_body:
            if line.startswith("Q:"):
                # Q:1/4=90 or similar
                try:
                    tempo = int(line.split("=")[-1].strip())
                except Exception:
                    pass
            elif line.startswith("L:"):
                try:
                    num, den = line.split(":", 1)[1].strip().split("/")
                    default_length = int(den)  # the denominator is the L
                except Exception:
                    pass
            elif line.startswith("M:"):
                try:
                    num, den = line.split(":", 1)[1].strip().split("/")
                    meter_num, meter_den = int(num), int(den)
                except Exception:
                    pass
            elif line.startswith("K:"):
                in_body = True
            continue
        body_lines.append(line)

    body = " ".join(body_lines)
    # Strip ornament markers and chord brackets we don't handle
    for ch in "{}~()|:!":
        body = body.replace(ch, " ")

    i = 0
    while i < len(body):
        ch = body[i]
        if ch.isspace():
            i += 1
            continue
        if ch == "z" or ch == "Z":
            length = ""
            i += 1
            while i < len(body) and (body[i].isdigit() or body[i] == "/"):
                length += body[i]
                i += 1
            beats = _length_to_beats(length, default_length)
            notes.append((-1, beats))
            continue
        if ch in "abcdefgABCDEFG":
            pitch = PITCH_TO_MIDI[ch.upper()]
            if ch.islower():
                pitch += 12
            i += 1
            # octave shifts
            while i < len(body) and body[i] in "',":
                if body[i] == "'":
                    pitch += 12
                else:
                    pitch -= 12
                i += 1
            # length
            length = ""
            while i < len(body) and (body[i].isdigit() or body[i] == "/"):
                length += body[i]
                i += 1
            beats = _length_to_beats(length, default_length)
            notes.append((pitch, beats))
            continue
        # accidentals or anything we don't handle
        i += 1

    return notes, tempo, default_length


def _length_to_beats(length: str, default_length_den: int) -> float:
    """ABC length string -> fraction of a quarter note (one MIDI quarter)."""
    base = 4.0 / default_length_den  # if L:1/4, base = 1.0 quarter notes
    if not length:
        return base
    if length == "/":
        return base / 2
    if length.startswith("/"):
        try:
            return base / int(length[1:] or 2)
        except ValueError:
            return base / 2
    if "/" in length:
        n, d = length.split("/", 1)
        n_val = int(n) if n else 1
        d_val = int(d) if d else 2
        return base * n_val / d_val
    try:
        return base * int(length)
    except ValueError:
        return base


def _write_var_len(value: int) -> bytes:
    out = bytearray()
    out.append(value & 0x7F)
    value >>= 7
    while value:
        out.insert(0, (value & 0x7F) | 0x80)
        value >>= 7
    return bytes(out)


def via_stdlib(abc_path: Path, midi_path: Path, preset: int) -> bool:
    abc = abc_path.read_text()
    notes, tempo, default_length = _parse_minimal_abc(abc)
    if not notes:
        print("stdlib fallback: no notes parsed", file=sys.stderr)
        return False

    PPQ = 480  # pulses per quarter
    track_data = bytearray()

    # Tempo meta
    us_per_q = int(60_000_000 / tempo)
    track_data += _write_var_len(0) + bytes([0xFF, 0x51, 0x03])
    track_data += us_per_q.to_bytes(3, "big")

    # Program change to preset (MIDI 0-127, GM is 1-128)
    program = max(0, min(127, preset - 1))
    track_data += _write_var_len(0) + bytes([0xC0, program])

    pending_delta = 0
    for pitch, beats in notes:
        ticks = max(1, int(round(beats * PPQ)))
        if pitch < 0:  # rest
            pending_delta += ticks
            continue
        track_data += _write_var_len(pending_delta) + bytes([0x90, pitch, 0x60])
        track_data += _write_var_len(ticks) + bytes([0x80, pitch, 0x40])
        pending_delta = 0

    # End of track
    track_data += _write_var_len(0) + bytes([0xFF, 0x2F, 0x00])

    # Header chunk (format 0, 1 track, division=PPQ)
    header = b"MThd" + (6).to_bytes(4, "big") + (0).to_bytes(2, "big") \
             + (1).to_bytes(2, "big") + PPQ.to_bytes(2, "big")
    track_chunk = b"MTrk" + len(track_data).to_bytes(4, "big") + bytes(track_data)
    midi_path.write_bytes(header + track_chunk)
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tune", required=True, type=Path)
    p.add_argument("--instrument", required=True)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()

    if not args.tune.exists():
        sys.exit(f"missing tune: {args.tune}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    preset = soundfont_preset_for(args.instrument)

    if via_music21(args.tune, args.out, preset):
        print(f"  music21 -> {args.out}")
        return
    if via_abc2midi(args.tune, args.out):
        print(f"  abc2midi -> {args.out}")
        return
    if via_stdlib(args.tune, args.out, preset):
        print(f"  stdlib  -> {args.out} (limited: single voice, no ornaments)")
        return

    sys.exit("no MIDI converter worked. Install music21 (pip install music21) "
             "or abc2midi (apt install abcmidi).")


if __name__ == "__main__":
    main()
