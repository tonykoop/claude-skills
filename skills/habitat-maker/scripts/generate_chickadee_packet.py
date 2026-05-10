#!/usr/bin/env python3
"""
generate_chickadee_packet.py
============================

Read `geometry_params.json` from a chickadee laser packet and emit
`chickadee-panels.svg`. The same JSON is the single source of truth for
the prose dimensions in the surrounding packet (cut-list.md, BOM.md,
validation-checklist.md), so regenerating the SVG never drifts from the
prose.

Usage:
    python3 generate_chickadee_packet.py \\
        --packet path/to/examples/chickadee-laser-baltic-birch
    # or omit --packet to default to the canonical example next to this script
    python3 generate_chickadee_packet.py

Exit codes:
    0 — wrote SVG
    2 — invalid usage / missing input

The output file is `chickadee-panels.svg` inside the packet folder.

This script is part of habitat-maker v0.2. It is intentionally
self-contained (no third-party Python dependencies) so it works on a
fresh Python 3.10+ install without pip.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def load_params(packet_dir: Path) -> dict[str, Any]:
    p = packet_dir / "geometry_params.json"
    if not p.is_file():
        raise SystemExit(f"missing {p} — geometry_params.json is required")
    with p.open() as fh:
        return json.load(fh)


def derive_panel_geometry(params: dict[str, Any]) -> dict[str, float]:
    """Compute derived panel dimensions from the cavity + thickness inputs."""
    g = params["derived_panel_geometry_mm"]
    return {
        "T":               g["panel_thickness"],
        "FLOOR_INT":       g["floor_interior"],
        "BOX_X":           g["box_exterior"],
        "FRONT_H":         g["front_panel_h"],
        "BACK_H":          g["back_panel_box_h"],
        "BACK_TOTAL_H":    g["back_panel_total_h"],
        "SIDE_FRONT_EDGE": g["side_front_edge"],
        "SIDE_BACK_EDGE":  g["side_back_edge"],
        "ROOF_W":          g["roof_w"],
        "ROOF_D":          g["roof_d"],
        "GUARD_W":         g["entrance_guard_w"],
        "ENTRY_DIA":       g["entrance_diameter"],
        "ENTRY_AB_FLOOR":  g["entrance_above_floor"],
        "FLOOR_RECESS":    g["floor_top_above_panel_bottom"],
    }


# ---------------------------------------------------------------- box-joint helpers
def fingers(edge_len: float, n: int = 22) -> tuple[list[float], float]:
    """Return list of transition y-values along a vertical edge of length
    `edge_len`, with `n` fingers + 2 half-fingers at the ends."""
    finger_w = edge_len / (n + 1)
    half_w = finger_w / 2
    ys = [0.0, half_w]
    for _ in range(n):
        ys.append(ys[-1] + finger_w)
    ys.append(edge_len)
    return ys, finger_w


def finger_path_right(base_x: float, base_y: float, edge_len: float, T: float, first: str = "out") -> list[str]:
    """Going UP the right edge of a panel; fingers stick OUT to +T."""
    ys, _ = fingers(edge_len)
    cmds = []
    state_out = (first == "out")
    cur_x = base_x + (T if state_out else 0)
    cmds.append(f"L {cur_x:.3f},{base_y:.3f}")
    for i in range(1, len(ys)):
        cmds.append(f"L {cur_x:.3f},{base_y + ys[i]:.3f}")
        if i < len(ys) - 1:
            state_out = not state_out
            cur_x = base_x + (T if state_out else 0)
            cmds.append(f"L {cur_x:.3f},{base_y + ys[i]:.3f}")
    if cur_x != base_x:
        cmds.append(f"L {base_x:.3f},{base_y + edge_len:.3f}")
    return cmds


def finger_path_left(base_x: float, base_y: float, edge_len: float, T: float, first: str = "out") -> list[str]:
    """Going DOWN the left edge of a panel; fingers stick OUT to -T."""
    ys, _ = fingers(edge_len)
    cmds = []
    state_out = (first == "out")
    cur_x = base_x - (T if state_out else 0)
    cmds.append(f"L {cur_x:.3f},{base_y:.3f}")
    for i in range(1, len(ys)):
        y_step = base_y - ys[i]
        cmds.append(f"L {cur_x:.3f},{y_step:.3f}")
        if i < len(ys) - 1:
            state_out = not state_out
            cur_x = base_x - (T if state_out else 0)
            cmds.append(f"L {cur_x:.3f},{y_step:.3f}")
    if cur_x != base_x:
        cmds.append(f"L {base_x:.3f},{base_y - edge_len:.3f}")
    return cmds


# ---------------------------------------------------------------- svg helpers
def svg_path(d: str, cls: str = "cut") -> str:
    return f'<path d="{d}" class="{cls}" />'


def svg_circle(cx: float, cy: float, r: float, cls: str = "cut") -> str:
    return f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" class="{cls}" />'


def svg_rect(x: float, y: float, w: float, h: float, cls: str = "cut", rx: float = 0) -> str:
    rx_s = f' rx="{rx}"' if rx else ""
    return (f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" '
            f'height="{h:.3f}" class="{cls}"{rx_s} />')


def svg_line(x1: float, y1: float, x2: float, y2: float, cls: str) -> str:
    return (f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
            f'class="{cls}" />')


def svg_label(x: float, y: float, text: str) -> str:
    return f'<text x="{x:.2f}" y="{y:.2f}" class="label">{text}</text>'


# ---------------------------------------------------------------- panel generators
def panel_front(g: dict[str, float]) -> list[str]:
    elems = []
    d = ["M 0,0", f"L {g['BOX_X']:.3f},0"]
    d += finger_path_right(g["BOX_X"], 0, g["SIDE_FRONT_EDGE"], g["T"], first="out")
    d.append(f"L {g['BOX_X']:.3f},{g['FRONT_H']:.3f}")
    d.append(f"L 0,{g['FRONT_H']:.3f}")
    d.append(f"L 0,{g['SIDE_FRONT_EDGE']:.3f}")
    d += finger_path_left(0, g["SIDE_FRONT_EDGE"], g["SIDE_FRONT_EDGE"], g["T"], first="out")
    d.append("L 0,0")
    d.append("Z")
    elems.append(svg_path(" ".join(d), "cut"))

    elems.append(svg_circle(g["BOX_X"] / 2, g["FLOOR_RECESS"] + g["ENTRY_AB_FLOOR"],
                            g["ENTRY_DIA"] / 2, "cut"))
    cy_anchor = g["FLOOR_RECESS"] + g["ENTRY_AB_FLOOR"] - g["ENTRY_DIA"] / 2 - 25
    for k in range(5):
        y = cy_anchor + 2 * (k - 2)
        elems.append(svg_line(g["BOX_X"] / 2 - 40, y, g["BOX_X"] / 2 + 40, y, "score"))
    return elems


def panel_back(g: dict[str, float]) -> list[str]:
    elems = []
    d = ["M 0,0", f"L {g['BOX_X']:.3f},0", f"L {g['BOX_X']:.3f},30"]
    d += finger_path_right(g["BOX_X"], 30, g["SIDE_BACK_EDGE"], g["T"], first="in")
    d.append(f"L {g['BOX_X']:.3f},{30 + g['SIDE_BACK_EDGE']:.3f}")
    d.append(f"L {g['BOX_X']:.3f},{g['BACK_TOTAL_H']:.3f}")
    d.append(f"L 0,{g['BACK_TOTAL_H']:.3f}")
    d.append(f"L 0,{30 + g['SIDE_BACK_EDGE']:.3f}")
    d += finger_path_left(0, 30 + g["SIDE_BACK_EDGE"], g["SIDE_BACK_EDGE"], g["T"], first="in")
    d.append("L 0,30")
    d.append("L 0,0")
    d.append("Z")
    elems.append(svg_path(" ".join(d), "cut"))

    elems.append(svg_circle(g["BOX_X"] / 2, 15, 2.75, "cut"))
    elems.append(svg_circle(g["BOX_X"] / 2, g["BACK_TOTAL_H"] - 15, 2.75, "cut"))
    return elems


def panel_side(g: dict[str, float], handed: str = "L") -> list[str]:
    elems = []
    d = ["M 0,0", f"L {g['FLOOR_INT']:.3f},0"]
    d += finger_path_right(g["FLOOR_INT"], 0, g["SIDE_FRONT_EDGE"], g["T"], first="in")
    d.append(f"L 0,{g['SIDE_BACK_EDGE']:.3f}")
    d += finger_path_left(0, g["SIDE_BACK_EDGE"], g["SIDE_BACK_EDGE"], g["T"], first="in")
    d.append("L 0,0")
    d.append("Z")
    elems.append(svg_path(" ".join(d), "cut"))

    for cx in (27, 55, 83):
        roof_y = g["SIDE_BACK_EDGE"] + (cx / g["FLOOR_INT"]) * (g["SIDE_FRONT_EDGE"] - g["SIDE_BACK_EDGE"])
        cy = roof_y - 14
        x = cx - 25
        y = cy - 2
        elems.append(svg_rect(x, y, 50, 4, "cut", rx=2))

    if handed == "R":
        elems.append(svg_circle(g["FLOOR_INT"] - 6, g["SIDE_FRONT_EDGE"] - 8, 1.5, "cut"))
        elems.append(svg_circle(6, g["SIDE_BACK_EDGE"] - 8, 1.5, "cut"))
        elems.append(svg_circle(g["FLOOR_INT"] - 6, 12, 1.5, "cut"))

    return elems


def panel_floor(g: dict[str, float]) -> list[str]:
    elems = []
    F = g["FLOOR_INT"]
    d = [
        "M 8,0", f"L {F - 8:.3f},0", f"L {F - 8:.3f},8",
        f"L {F:.3f},8", f"L {F:.3f},{F - 8:.3f}",
        f"L {F - 8:.3f},{F - 8:.3f}", f"L {F - 8:.3f},{F:.3f}",
        f"L 8,{F:.3f}", f"L 8,{F - 8:.3f}",
        f"L 0,{F - 8:.3f}", "L 0,8", "L 8,8", "Z",
    ]
    elems.append(svg_path(" ".join(d), "cut"))
    return elems


def panel_roof(g: dict[str, float]) -> list[str]:
    elems = []
    W = g["ROOF_W"]
    D = g["ROOF_D"]
    elems.append(svg_rect(0, 0, W, D, "cut"))
    for cx in (25 + 12, W - 25 - 12):
        for cy in (25 + 12, D - 50 - 12):
            elems.append(svg_circle(cx, cy, 1.5, "cut"))
    elems.append(svg_line(6, 6, W - 6, 6, "score"))
    elems.append(svg_line(6, 6, 6, D - 6, "score"))
    elems.append(svg_line(W - 6, 6, W - 6, D - 6, "score"))
    elems.append(svg_line(6, D - 6, W - 6, D - 6, "score"))
    return elems


def panel_kerf_test() -> list[str]:
    return [svg_rect(0, 0, 50, 50, "cut")]


def panel_entrance_guard(g: dict[str, float]) -> list[str]:
    G = g["GUARD_W"]
    return [
        svg_rect(0, 0, G, G, "cut"),
        svg_circle(G / 2, G / 2, g["ENTRY_DIA"] / 2, "cut"),
    ]


# ---------------------------------------------------------------- assemble
def build_svg(g: dict[str, float]) -> str:
    SHEET_W = 600
    SHEET_H = 760
    layout = [
        ("front",  panel_front(g),               20,  20, g["FRONT_H"],
            "P1 FRONT — entrance + kerf-grip score"),
        ("back",   panel_back(g),               170,  20, g["BACK_TOTAL_H"],
            "P2 BACK — mount tabs + 2× mount holes"),
        ("roof",   panel_roof(g),               320,  20, g["ROOF_D"],
            "P6 ROOF — drip score, 4× pilot"),
        ("kerf",   panel_kerf_test(),           510,  20, 50,
            "P7 KERF TEST 50×50"),
        ("sideL",  panel_side(g, "L"),           20, 410, g["SIDE_FRONT_EDGE"],
            "P3 SIDE-L (fixed) — 3× vent slot"),
        ("sideR",  panel_side(g, "R"),          200, 410, g["SIDE_FRONT_EDGE"],
            "P4 SIDE-R (cleanout door) — 3× pilot"),
        ("floor",  panel_floor(g),              380, 410, g["FLOOR_INT"],
            "P5 FLOOR — 4× corner drains"),
        ("guard",  panel_entrance_guard(g),     510, 410, g["GUARD_W"],
            "P8 GUARD (optional)"),
    ]

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SHEET_W}mm" height="{SHEET_H}mm" '
        f'viewBox="0 0 {SHEET_W} {SHEET_H}">',
        '<defs><style>'
        '.cut { fill: none; stroke: #000000; stroke-width: 0.15; }'
        '.score { fill: none; stroke: #00aa00; stroke-width: 0.15; '
        'stroke-dasharray: 0.6 0.4; }'
        '.label { font-family: monospace; font-size: 3.5px; fill: #444; }'
        '</style></defs>',
        '<title>habitat-maker chickadee laser-cut panels (mm, finished post-kerf)</title>',
    ]

    for name, elems, sx, sy, ph, lbl in layout:
        parts.append(f'<g id="{name}" transform="translate({sx},{sy + ph}) scale(1,-1)">')
        parts.extend(elems)
        parts.append('</g>')
        parts.append(svg_label(sx, sy - 4, lbl))

    parts.append(svg_label(20, SHEET_H - 8,
        "habitat-maker · canonical chickadee · units=mm · cut=black · score=green dashed · "
        f"sheet {SHEET_W}×{SHEET_H} mm"))
    parts.append('</svg>')
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    default_packet = (here.parent / "examples" / "chickadee-laser-baltic-birch").resolve()

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--packet", type=Path, default=default_packet,
                    help="path to the example packet directory containing "
                         "geometry_params.json (default: %(default)s)")
    ap.add_argument("--output-name", default="chickadee-panels.svg",
                    help="output filename inside the packet (default: %(default)s)")
    args = ap.parse_args(argv)

    packet_dir: Path = args.packet
    if not packet_dir.is_dir():
        raise SystemExit(f"--packet path does not exist or is not a directory: {packet_dir}")

    params = load_params(packet_dir)
    g = derive_panel_geometry(params)
    svg = build_svg(g)

    out = packet_dir / args.output_name
    out.write_text(svg)
    print(f"wrote {out} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
