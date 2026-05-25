#!/usr/bin/env python3
"""Render a fingering chart SVG for the distinct pitches in a tune.

Layout: one fingering diagram per distinct pitch in the tune,
ordered low to high. Each diagram shows the instrument's holes/keys
with filled/open dots indicating which to close/open.

The fingering schemes are looked up by name from the registry, then
mapped to physical hole layouts in `assets/fingering-icons/<scheme>.json`.
If the scheme's JSON file isn't present, a generic 6-hole vertical
layout is used as a placeholder.

Usage:
    python render_fingering_svg.py \\
        --tune tune.abc \\
        --instrument naf-6hole \\
        --out tune-fingering.svg
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Sci-pitch numbers for ABC pitches (rough — accidentals not handled here)
ABC_TO_SCI = {
    "C,": (0, "C3"),  "D,": (2, "D3"),  "E,": (4, "E3"),
    "F,": (5, "F3"),  "G,": (7, "G3"),  "A,": (9, "A3"),  "B,": (11, "B3"),
    "C": (12, "C4"),  "D": (14, "D4"),  "E": (16, "E4"),
    "F": (17, "F4"),  "G": (19, "G4"),  "A": (21, "A4"),  "B": (23, "B4"),
    "c": (24, "C5"),  "d": (26, "D5"),  "e": (28, "E5"),
    "f": (29, "F5"),  "g": (31, "G5"),  "a": (33, "A5"),  "b": (35, "B5"),
    "c'": (36, "C6"), "d'": (38, "D6"), "e'": (40, "E6"),
    "f'": (41, "F6"), "g'": (43, "G6"), "a'": (45, "A6"), "b'": (47, "B6"),
}


def extract_pitches(abc_text: str) -> list[str]:
    """Pull distinct pitch tokens out of an ABC body in pitch order."""
    in_body = False
    body = []
    for line in abc_text.splitlines():
        s = line.strip()
        if not in_body:
            if s.startswith("K:"):
                in_body = True
            continue
        if s.startswith("%") or not s:
            continue
        # Inline ABC headers (H:, W:, N:, etc.) can appear after K: and
        # contain text that looks like pitches. Skip any line whose
        # first two characters are an ABC header code.
        if len(s) >= 2 and s[1] == ":" and s[0].isalpha():
            continue
        body.append(s)

    text = " ".join(body)
    cleaned = re.sub(r"[{}~()|:!]", " ", text)
    cleaned = re.sub(r"\d+", "", cleaned)
    cleaned = re.sub(r"/", "", cleaned)
    cleaned = re.sub(r"-", "", cleaned)

    seen: dict[int, str] = {}
    for m in re.finditer(r"([a-gA-G])([',]*)", cleaned):
        letter = m.group(1)
        oct_marks = m.group(2)
        token = letter + oct_marks if oct_marks else letter
        if token in ABC_TO_SCI:
            num, sci = ABC_TO_SCI[token]
            seen[num] = sci
    return [seen[k] for k in sorted(seen.keys())]


def load_scheme(scheme: str) -> dict:
    """Load a fingering-scheme JSON. Returns a placeholder if missing."""
    path = REPO_ROOT / "assets" / "fingering-icons" / f"{scheme}.json"
    if path.exists():
        return json.loads(path.read_text())
    return {
        "scheme": scheme,
        "holes": [
            {"id": "h1", "y": 0},
            {"id": "h2", "y": 1},
            {"id": "h3", "y": 2},
            {"id": "h4", "y": 3},
            {"id": "h5", "y": 4},
            {"id": "h6", "y": 5},
        ],
        "fingerings": {},
        "placeholder": True,
    }


def render_svg(pitches: list[str], scheme_data: dict, instrument_id: str) -> str:
    diagram_w = 60
    diagram_h = 220
    label_h = 22
    margin = 16
    cols = max(1, len(pitches))
    width = margin * 2 + diagram_w * cols
    height = margin * 2 + label_h + diagram_h

    holes = scheme_data["holes"]
    fingerings = scheme_data.get("fingerings", {})
    placeholder = scheme_data.get("placeholder", False)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="Fingering chart for {instrument_id}">',
        f'<title>Fingering chart -- {instrument_id}</title>',
        '<style>',
        '.label { font: 12px Inter, sans-serif; fill: #2A2A2A; }',
        '.scheme { font: 10px Inter, sans-serif; fill: #888; }',
        '.body  { fill: none; stroke: #2A2A2A; stroke-width: 1.5; }',
        '.closed { fill: #2A2A2A; stroke: #2A2A2A; }',
        '.open   { fill: #FFFFFF; stroke: #2A2A2A; }',
        '.unknown { fill: #FFD8D8; stroke: #C44; stroke-dasharray: 3 2; }',
        '</style>',
    ]

    parts.append(
        f'<text x="{margin}" y="{margin+8}" class="scheme">'
        f'scheme: {scheme_data.get("scheme","?")}'
        + (' (placeholder; add a real fingering JSON for accurate output)' if placeholder else '')
        + '</text>'
    )

    for i, sci in enumerate(pitches):
        x0 = margin + i * diagram_w
        parts.append(
            f'<text x="{x0 + diagram_w/2}" y="{margin + label_h}" '
            f'class="label" text-anchor="middle">{sci}</text>'
        )
        body_x = x0 + 12
        body_y = margin + label_h + 8
        body_w = diagram_w - 24
        body_h = diagram_h - 24
        parts.append(
            f'<rect x="{body_x}" y="{body_y}" width="{body_w}" '
            f'height="{body_h}" rx="8" class="body"/>'
        )
        closed = set(fingerings.get(sci, []))
        unknown = sci not in fingerings
        n_holes = len(holes)
        for h in holes:
            cx = body_x + body_w / 2
            cy = body_y + 18 + (h["y"] / max(1, n_holes - 1)) * (body_h - 36)
            cls = "unknown" if unknown else ("closed" if h["id"] in closed else "open")
            parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="6" class="{cls}"/>'
            )

    parts.append('</svg>')
    return "\n".join(parts)


def fingering_scheme_for(instrument_id: str) -> str:
    """Pull the `fingering` field out of registry.yaml for an instrument."""
    text = (REPO_ROOT / "instruments" / "registry.yaml").read_text()
    marker = f"id: {instrument_id}"
    if marker not in text:
        return "generic-6hole"
    block = text.split(marker, 1)[1].split("- id:", 1)[0]
    for line in block.splitlines():
        if "fingering:" in line:
            return line.split(":", 1)[1].strip().split("#")[0].strip()
    return "generic-6hole"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tune", required=True, type=Path)
    p.add_argument("--instrument", required=True)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()

    if not args.tune.exists():
        sys.exit(f"missing tune: {args.tune}")
    args.out.parent.mkdir(parents=True, exist_ok=True)

    abc = args.tune.read_text()
    pitches = extract_pitches(abc)
    if not pitches:
        pitches = []

    scheme_name = fingering_scheme_for(args.instrument)
    scheme_data = load_scheme(scheme_name)
    svg = render_svg(pitches, scheme_data, args.instrument)
    args.out.write_text(svg)
    print(f"  fingering -> {args.out} ({len(pitches)} distinct pitches; "
          f"scheme={scheme_name}{' [placeholder]' if scheme_data.get('placeholder') else ''})")


if __name__ == "__main__":
    main()
