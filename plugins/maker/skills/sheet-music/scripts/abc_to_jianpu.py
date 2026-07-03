#!/usr/bin/env python3
"""Convert an ABC file to Jianpu (numbered notation, 简谱) text output.

Pure stdlib -- no music21, LilyPond, or jianpu-ly required. This is a
render target derived from the same ABC source of truth the rest of the
pipeline uses (see references/notation-formats.md), not a separate
authoring path.

Movable-do convention: the stated ABC key's tonic maps to scale degree 1
for a major key. For a minor key (K:Xm), the tonic is shown under its
*relative major*'s "1=" header with the tonic itself as degree 6 -- the
standard Jianpu convention (e.g. K:Am renders as header "1=C" with the A
written as "6"). Any other mode suffix (Amix, Ddor, ...) falls back to
being treated as major-scale-relative; modal Jianpu is out of scope.

Text-mode layout (plain text can't stack a real dot or line on a single
row, so this uses a small multi-row block per ABC line):

    above row      -- "." per octave above the written register
    digit row      -- degree number (1-7, 0 = rest), "#"/"b" prefix for
                       chromatic passing tones, "-" suffix per extra
                       beat held (augmentation)
    underline row(s) -- one row of "_" per halving of the beat
                       (subdivision): 1 row = eighth note, 2 rows =
                       sixteenth note
    below row      -- "." per octave below the written register

Usage:
    python abc_to_jianpu.py --tune tune.abc --out tune-jianpu.txt
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

NATURAL_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
PC_NAMES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJOR_OFFSETS = [0, 2, 4, 5, 7, 9, 11]  # do re mi fa sol la ti, as semitone offsets


def build_chromatic_map() -> dict[int, tuple[str, str]]:
    """semitone-offset-from-do -> (accidental_prefix, degree_char).

    Non-scale semitones are notated as a sharp of the scale degree one
    semitone below them -- the common simplified-Jianpu convention for
    chromatic passing tones.
    """
    m: dict[int, tuple[str, str]] = {}
    for degree, off in enumerate(MAJOR_OFFSETS, start=1):
        m[off] = ("", str(degree))
    for off in range(12):
        if off not in m:
            prefix, deg = m[(off - 1) % 12]
            m[off] = ("#", deg)
    return m


CHROMATIC_MAP = build_chromatic_map()


def parse_key(key_str: str) -> tuple[int, str, bool]:
    """Return (display_root_pc, display_root_name, is_minor)."""
    key_str = key_str.strip()
    if not key_str:
        return 0, "C", False
    letter = key_str[0].upper()
    rest = key_str[1:]
    acc = 0
    if rest[:1] in ("#", "b"):
        acc = 1 if rest[0] == "#" else -1
        rest = rest[1:]
    tonic_pc = (NATURAL_PC.get(letter, 0) + acc) % 12
    is_minor = rest.strip().lower().startswith("m") and not rest.strip().lower().startswith("maj")
    if is_minor:
        display_root_pc = (tonic_pc + 3) % 12  # relative major is a minor 3rd up
    else:
        display_root_pc = tonic_pc
    return display_root_pc, PC_NAMES_SHARP[display_root_pc], is_minor


def _length_to_beats(length: str, default_length_den: int) -> float:
    """ABC length string -> fraction of a quarter note (one Jianpu beat)."""
    base = 4.0 / default_length_den
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


def duration_marks(beats: float) -> tuple[int, int]:
    """beats -> (dash_count, underline_count)."""
    if beats >= 1:
        n = max(1, round(beats))
        return n - 1, 0
    halvings = 0
    b = beats
    while b < 1 and halvings < 4:
        b *= 2
        halvings += 1
    return 0, halvings


def parse_header(abc: str) -> tuple[dict, list[str]]:
    header = {"title": "Untitled", "key": "C", "tempo": 90, "default_length_den": 4,
              "meter_num": 4, "meter_den": 4}
    body_lines: list[str] = []
    in_body = False
    for raw in abc.splitlines():
        line = raw.strip()
        if not line or line.startswith("%"):
            continue
        if not in_body:
            if line.startswith("T:"):
                header["title"] = line.split(":", 1)[1].strip()
            elif line.startswith("Q:"):
                try:
                    header["tempo"] = int(line.split("=")[-1].strip())
                except ValueError:
                    pass
            elif line.startswith("L:"):
                try:
                    _, den = line.split(":", 1)[1].strip().split("/")
                    header["default_length_den"] = int(den)
                except Exception:
                    pass
            elif line.startswith("M:"):
                try:
                    num, den = line.split(":", 1)[1].strip().split("/")
                    header["meter_num"], header["meter_den"] = int(num), int(den)
                except Exception:
                    pass
            elif line.startswith("K:"):
                header["key"] = line.split(":", 1)[1].strip()
                in_body = True
            continue
        # Info fields (H:, N:, w:, ...) can legally follow K: before the
        # note body actually starts; a bare "<letter>:" is never valid
        # note-body syntax, so treat it as another field line, not notes.
        if len(line) > 1 and line[0].isalpha() and line[1] == ":":
            continue
        body_lines.append(line)
    return header, body_lines


def tokenize_line(line: str) -> list[tuple]:
    """Split one ABC body line into ('note'|'rest'|'bar', ...) tokens."""
    # Strip ornaments/ties/slurs/dotted-note shorthand we don't model.
    for ch in "{}~()!><":
        line = line.replace(ch, " ")
    tokens: list[tuple] = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "|:[]":
            j = i
            while j < n and line[j] in "|:[]":
                j += 1
            tokens.append(("bar", line[i:j]))
            i = j
            continue
        if ch in "zZ":
            i += 1
            length = ""
            while i < n and (line[i].isdigit() or line[i] == "/"):
                length += line[i]
                i += 1
            tokens.append(("rest", length))
            continue
        acc = 0
        if ch in "^_=":
            j = i
            sign = 1 if ch == "^" else (-1 if ch == "_" else 0)
            count = 0
            while j < n and line[j] == ch:
                count += 1
                j += 1
            acc = sign * count
            i = j
            if i >= n or line[i] not in "abcdefgABCDEFG":
                continue  # stray accidental with no note; drop it
            ch = line[i]
        if ch in "abcdefgABCDEFG":
            letter = ch.upper()
            octave = 0 if ch.isupper() else 1
            i += 1
            while i < n and line[i] in "',":
                octave += 1 if line[i] == "'" else -1
                i += 1
            length = ""
            while i < n and (line[i].isdigit() or line[i] == "/"):
                length += line[i]
                i += 1
            tokens.append(("note", letter, acc, octave, length))
            continue
        i += 1
    return tokens


def render_line(tokens: list[tuple], header: dict, display_root_pc: int) -> str:
    main_parts: list[str] = []
    above_parts: list[str] = []
    below_parts: list[str] = []
    underline_parts: list[list[str]] = []  # per-token list of underline rows
    max_underline = 0

    for tok in tokens:
        if tok[0] == "bar":
            width = len(tok[1])
            main_parts.append(tok[1])
            above_parts.append(" " * width)
            below_parts.append(" " * width)
            underline_parts.append([])
            continue

        if tok[0] == "rest":
            _, length = tok
            beats = _length_to_beats(length, header["default_length_den"])
            dash, underline = duration_marks(beats)
            digit = "0" + ("-" * dash)
            octave = 0
        else:
            _, letter, acc, octave, length = tok
            beats = _length_to_beats(length, header["default_length_den"])
            dash, underline = duration_marks(beats)
            pc = (NATURAL_PC[letter] + acc) % 12
            offset = (pc - display_root_pc) % 12
            prefix, deg = CHROMATIC_MAP[offset]
            digit = prefix + deg + ("-" * dash)

        width = len(digit)
        main_parts.append(digit)
        above_parts.append(("." * octave).ljust(width) if octave > 0 else " " * width)
        below_parts.append(("." * (-octave)).ljust(width) if octave < 0 else " " * width)
        rows = [("_" * width) for _ in range(underline)]
        underline_parts.append(rows)
        max_underline = max(max_underline, underline)

    # Underline rows, aligned to each token's main-row width.
    underline_lines = []
    for level in range(max_underline):
        cells = []
        for idx, rows in enumerate(underline_parts):
            width = len(main_parts[idx])
            cells.append(rows[level] if level < len(rows) else " " * width)
        underline_lines.append(" ".join(cells))

    out_lines = []
    above_line = " ".join(above_parts)
    if above_line.strip():
        out_lines.append(above_line)
    out_lines.append(" ".join(main_parts))
    out_lines.extend(underline_lines)
    below_line = " ".join(below_parts)
    if below_line.strip():
        out_lines.append(below_line)
    return "\n".join(out_lines)


def render_jianpu(abc_text: str) -> str:
    header, body_lines = parse_header(abc_text)
    display_root_pc, display_root_name, is_minor = parse_key(header["key"])

    heading = (
        f"{header['title']}  (Jianpu: 1={display_root_name}, "
        f"{header['meter_num']}/{header['meter_den']}, q={header['tempo']})"
    )
    if is_minor:
        heading += f"  [K:{header['key']} -> tonic shown as scale degree 6]"

    blocks = [heading, ""]
    note_count = 0
    for line in body_lines:
        tokens = tokenize_line(line)
        if not tokens:
            continue
        note_count += sum(1 for t in tokens if t[0] in ("note", "rest"))
        blocks.append(render_line(tokens, header, display_root_pc))
        blocks.append("")

    if note_count == 0:
        raise ValueError("no notes parsed from ABC body")

    return "\n".join(blocks).rstrip() + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tune", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()

    if not args.tune.exists():
        sys.exit(f"missing tune: {args.tune}")

    try:
        jianpu = render_jianpu(args.tune.read_text())
    except ValueError as e:
        sys.exit(str(e))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(jianpu)
    print(f"  jianpu  -> {args.out}")


if __name__ == "__main__":
    main()
