#!/usr/bin/env python3
"""
Generate the four-chamber bat-house helper artifacts.

Reads geometry_params.json from the packet folder and writes:
  - four-chamber-bat-house-layout.svg
  - generated-cut-list.csv

The SVG is a shop-layout sanity check, not CAM-ready joinery. The JSON remains
the source of truth for dimensions, welfare gates, climate presets, and mounting
constraints.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PACKET = SCRIPT_DIR.parent / "examples" / "temperate-na-four-chamber-bat-house"


def load_params(packet_dir: Path) -> dict[str, Any]:
    params_path = packet_dir / "geometry_params.json"
    if not params_path.is_file():
        raise SystemExit(f"missing {params_path}")
    with params_path.open() as fh:
        return json.load(fh)


def panel_size(panel: dict[str, Any]) -> tuple[float, float]:
    if panel["shape"] == "trapezoid":
        return float(panel["depth_mm"]), float(panel["rear_height_mm"])
    return float(panel["width_mm"]), float(panel["height_mm"])


def write_cut_list(packet_dir: Path, params: dict[str, Any]) -> Path:
    out = packet_dir / "generated-cut-list.csv"
    fields = [
        "part",
        "qty",
        "material",
        "shape",
        "width_mm",
        "height_mm",
        "depth_mm",
        "rear_height_mm",
        "front_height_mm",
        "thickness_mm",
    ]
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for panel in params["panel_schedule"]:
            writer.writerow({field: panel.get(field, "") for field in fields})
    return out


def rect(x: float, y: float, w: float, h: float, klass: str = "cut") -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'class="{klass}" />'
    )


def polygon(points: list[tuple[float, float]], klass: str = "cut") -> str:
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" class="{klass}" />'


def line(x1: float, y1: float, x2: float, y2: float, klass: str = "score") -> str:
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'class="{klass}" />'
    )


def circle(cx: float, cy: float, r: float, klass: str = "cut") -> str:
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" class="{klass}" />'


def label(x: float, y: float, text: str) -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" class="label">{html.escape(text)}</text>'


def groove_lines(x: float, y: float, w: float, h: float, spacing: float = 13.0) -> list[str]:
    elems = []
    cur = y + spacing
    while cur < y + h - spacing:
        elems.append(line(x + 8, cur, x + w - 8, cur, "score"))
        cur += spacing
    return elems


def draw_panel(panel: dict[str, Any], x: float, y: float, params: dict[str, Any]) -> tuple[str, float]:
    part = panel["part"]
    shape = panel["shape"]
    elems = [f'<g id="{html.escape(part)}">']
    if shape == "trapezoid":
        depth = float(panel["depth_mm"])
        rear = float(panel["rear_height_mm"])
        front = float(panel["front_height_mm"])
        elems.append(polygon([(x, y), (x + depth, y + rear - front), (x + depth, y + rear), (x, y + rear)]))
        if part == "side_wall":
            vent = params["venting_mm"]
            slot_h = float(vent["side_vent_slot_height"])
            slot_w = min(float(vent["side_vent_slot_length"]), max(20.0, depth - 20.0))
            slot_x = x + (depth - slot_w) / 2
            slot_y = y + rear - float(vent["side_vent_slot_bottom_above_back_bottom"]) - slot_h
            elems.append(rect(slot_x, slot_y, slot_w, slot_h, "vent side-vent-slot"))
        h = rear
    else:
        w = float(panel["width_mm"])
        h = float(panel["height_mm"])
        elems.append(rect(x, y, w, h))

        if part in {"back_panel", "partition", "lower_front_panel"}:
            elems.extend(groove_lines(x, y, w, h))
        if part == "partition":
            dia = params["chamber_geometry_mm"]["partition_passage_hole_diameter"]
            elems.append(circle(x + w * 0.35, y + 70, dia / 2))
            elems.append(circle(x + w * 0.65, y + 70, dia / 2))
        if part == "lower_front_panel":
            vent = params["venting_mm"]
            elems.append(rect(x + 19, y - vent["split_front_vent_gap"], vent["front_vent_slot_clear_width"], vent["split_front_vent_gap"], "vent"))
    elems.append(label(x, y - 6, f'{part} x{panel["qty"]}'))
    elems.append("</g>")
    return "\n".join(elems), h


def write_svg(packet_dir: Path, params: dict[str, Any]) -> Path:
    scale = 0.38
    margin = 20
    col_gap = 36
    row_gap = 34
    max_col_height = 0.0
    x = margin
    y = 48
    col_width = 0.0
    body: list[str] = []

    for panel in params["panel_schedule"]:
        w, h = panel_size(panel)
        if y + h * scale > 760 and y > 48:
            x += col_width * scale + col_gap
            y = 48
            col_width = 0.0
        group, drawn_h = draw_panel(panel, x, y, params)
        body.append(f'<g transform="scale({scale})">{group}</g>')
        y += drawn_h * scale + row_gap
        col_width = max(col_width, w)
        max_col_height = max(max_col_height, y)

    svg_w = max(900, int(x + col_width * scale + margin))
    svg_h = max(760, int(max_col_height + margin))
    title = params["packet"]
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
  <style>
    .cut {{ fill: none; stroke: #111; stroke-width: 1.5; }}
    .score {{ stroke: #2c7a7b; stroke-width: 0.7; }}
    .vent {{ fill: none; stroke: #b45309; stroke-width: 1.2; stroke-dasharray: 4 3; }}
    .label {{ font: 13px sans-serif; fill: #111; }}
    .note {{ font: 12px sans-serif; fill: #444; }}
  </style>
  <text x="20" y="26" class="label">{html.escape(title)} generated layout sanity check</text>
  <text x="20" y="44" class="note">Not CAM-ready joinery. Cut list and welfare gates come from geometry_params.json.</text>
  {''.join(body)}
</svg>
'''
    out = packet_dir / "four-chamber-bat-house-layout.svg"
    out.write_text(svg)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    args = parser.parse_args()
    packet_dir = args.packet.resolve()
    params = load_params(packet_dir)
    csv_out = write_cut_list(packet_dir, params)
    svg_out = write_svg(packet_dir, params)
    print(f"wrote {csv_out}")
    print(f"wrote {svg_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
