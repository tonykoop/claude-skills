#!/usr/bin/env python3
"""Generate the canonical habitat-maker chickadee laser SVG/JSON artifacts.

The input JSON is the single source of truth for species constraints,
material profiles, panel dimensions, and welfare validation gates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "references/examples/chickadee-laser-birdhouse/design_params.json",
        help="Design parameter JSON source.",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "references/examples/chickadee-laser-birdhouse",
        help="Directory for generated geometry_params.json and panels.svg.",
    )
    return parser.parse_args()


def load_params(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def round3(value: float) -> float:
    return round(float(value), 3)


def area_rect(width: float, height: float) -> float:
    return round3(width * height)


def derive_geometry(params: dict) -> dict:
    profile = params["material_profiles"][params["selected_material_profile"]]
    side = params["panels"]["side"]
    floor = params["panels"]["floor"]
    vent_area_per_side = (
        side["vent_slots_per_side"] * side["vent_slot_width"] * side["vent_slot_height"]
    )
    notch_w, notch_d = floor["corner_notch"]

    return {
        "units": params["packet"]["units"],
        "name": params["packet"]["name"],
        "version": params["packet"]["version"],
        "target_species": params["species"]["target"],
        "selected_material_profile": params["selected_material_profile"],
        "material": profile,
        "species_constraints": params["species"]["constraints"],
        "panels": params["panels"],
        "derived": {
            "vent_free_area_per_side_sq_in": round3(vent_area_per_side),
            "vent_free_area_total_sq_in": round3(2 * vent_area_per_side),
            "drainage_open_area_total_sq_in": round3(4 * area_rect(notch_w, notch_d)),
            "total_laser_plies_without_optional_guard": sum(
                panel.get("laser_ply_quantity", 0)
                for key, panel in params["panels"].items()
                if key != "entrance_guard_optional"
                and isinstance(panel.get("laser_ply_quantity"), int)
            )
            + side["laser_ply_quantity_total"],
        },
        "mounting": params["mounting"],
        "validation_checks": params["validation_checks"],
    }


def svg_header(width: float = 36.0, height: float = 24.0) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}in" '
            f'height="{height}in" viewBox="0 0 {width} {height}">'
        ),
        "<defs><style>",
        ".cut { fill: none; stroke: #cc0000; stroke-width: 0.01; }",
        ".score { fill: none; stroke: #008000; stroke-width: 0.01; }",
        ".engrave { fill: none; stroke: #0066cc; stroke-width: 0.01; }",
        ".label { font-family: Arial, sans-serif; font-size: 0.22px; fill: #333333; }",
        ".note { font-family: Arial, sans-serif; font-size: 0.18px; fill: #333333; }",
        "</style></defs>",
    ]


def text(x: float, y: float, content: str, cls: str = "label") -> str:
    return f'<text class="{cls}" x="{x:.3f}" y="{y:.3f}">{escape(content)}</text>'


def rect(x: float, y: float, w: float, h: float, cls: str = "cut") -> str:
    return (
        f'<rect class="{cls}" x="{x:.3f}" y="{y:.3f}" '
        f'width="{w:.3f}" height="{h:.3f}"/>'
    )


def rounded_rect(x: float, y: float, w: float, h: float, rx: float, cls: str = "cut") -> str:
    return (
        f'<rect class="{cls}" x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" '
        f'height="{h:.3f}" rx="{rx:.3f}" ry="{rx:.3f}"/>'
    )


def circle(cx: float, cy: float, r: float, cls: str = "cut") -> str:
    return f'<circle class="{cls}" cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}"/>'


def line(x1: float, y1: float, x2: float, y2: float, cls: str = "score") -> str:
    return (
        f'<line class="{cls}" x1="{x1:.3f}" y1="{y1:.3f}" '
        f'x2="{x2:.3f}" y2="{y2:.3f}"/>'
    )


def group_start(name: str, x: float, y: float) -> str:
    return f'<g id="{name}" transform="translate({x:.3f} {y:.3f})">'


def floor_path(width: float, depth: float, notch: tuple[float, float]) -> str:
    nw, nd = notch
    points = [
        (nw, 0),
        (width - nw, 0),
        (width, nd),
        (width, depth - nd),
        (width - nw, depth),
        (nw, depth),
        (0, depth - nd),
        (0, nd),
    ]
    d = "M " + " L ".join(f"{x:.3f},{y:.3f}" for x, y in points) + " Z"
    return f'<path class="cut" d="{d}"/>'


def side_path(depth: float, front_h: float, rear_h: float) -> str:
    # SVG y grows downward. This renders the sloped top while preserving
    # finished dimensions; CAM users should treat the file as geometry in inches.
    d = (
        f"M 0,{front_h - rear_h:.3f} "
        f"L {depth:.3f},0 "
        f"L {depth:.3f},{rear_h:.3f} "
        f"L 0,{front_h:.3f} Z"
    )
    return f'<path class="cut" d="{d}"/>'


def build_svg(params: dict, geometry: dict) -> str:
    panels = params["panels"]
    constraints = params["species"]["constraints"]
    parts = svg_header()
    parts.append(f"<title>{escape(params['packet']['title'])} panel templates</title>")
    parts.append(
        "<desc>Generator-backed habitat-maker example. Cut red, score green, engrave blue/text.</desc>"
    )

    # Front
    front = panels["front"]
    entry_dia = constraints["entrance_diameter"]["value"]
    parts.append(group_start("front-wall", 0.5, 0.5))
    parts.append(text(0, -0.12, "P1 FRONT - cut 3 plies - entry hard max 1.125 in"))
    parts.append(rect(0, 0, front["width"], front["height"]))
    entry_x, entry_y_ll = front["entrance_center"]
    parts.append(circle(entry_x, front["height"] - entry_y_ll, entry_dia / 2))
    grip = front["fledgling_grip"]
    grip_x = grip["center"][0]
    grip_y = front["height"] - grip["center"][1]
    for idx in range(grip["line_count"]):
        y = grip_y + (idx - (grip["line_count"] - 1) / 2) * grip["spacing"]
        parts.append(line(grip_x - grip["line_length"] / 2, y, grip_x + grip["line_length"] / 2, y))
    parts.append(text(0.25, front["height"] - 0.55, "inside face: rough/score below entry", "note"))
    parts.append("</g>")

    # Back
    back = panels["back"]
    parts.append(group_start("back-wall", 8.25, 0.5))
    parts.append(text(0, -0.12, "P2 BACK - cut 3 plies - mounting pilots"))
    parts.append(rect(0, 0, back["width"], back["height"]))
    for mx, my in back["mount_holes"]:
        parts.append(circle(mx, back["height"] - my, back["mount_hole_diameter"] / 2))
    parts.append(text(0.25, back["height"] - 1.0, "mount on baffled pole when possible", "note"))
    parts.append("</g>")

    # Side
    side = panels["side"]
    parts.append(group_start("side-wall", 16.0, 0.5))
    parts.append(text(0, -0.12, "P3/P4 SIDE - cut 6 plies - protected slot vents"))
    parts.append(side_path(side["depth"], side["front_height"], side["rear_height"]))
    slot_w = side["vent_slot_width"]
    slot_h = side["vent_slot_height"]
    for x, y in ((0.35, 1.05), (1.85, 0.85), (3.35, 0.65)):
        parts.append(rounded_rect(x, y, slot_w, slot_h, slot_h / 2))
    parts.append(text(0.2, side["front_height"] - 0.55, "3 slots per side; keep clear", "note"))
    parts.append("</g>")

    # Floor
    floor = panels["floor"]
    parts.append(group_start("floor", 22.25, 0.5))
    parts.append(text(0, -0.12, "P5 FLOOR - cut 3 plies - corner drainage notches"))
    parts.append(floor_path(floor["width"], floor["depth"], tuple(floor["corner_notch"])))
    parts.append(text(0.35, floor["depth"] / 2, "corner notches resist clogging", "note"))
    parts.append("</g>")

    # Optional guard
    guard = panels["entrance_guard_optional"]
    parts.append(group_start("entrance-guard", 28.5, 0.5))
    parts.append(text(0, -0.12, "OPTIONAL GUARD - keep entry 1.125 in"))
    parts.append(rect(0, 0, guard["width"], guard["height"]))
    parts.append(circle(guard["width"] / 2, guard["height"] / 2, guard["hole_diameter"] / 2))
    parts.append("</g>")

    # Kerf test
    parts.append(group_start("kerf-test", 31.75, 0.5))
    parts.append(text(0, -0.12, "KERF TEST"))
    kerf = params["fabrication"]["kerf_test_square"]
    parts.append(rect(0, 0, kerf, kerf))
    parts.append(circle(kerf / 2, kerf + 0.45, entry_dia / 2))
    parts.append("</g>")

    # Roof
    roof = panels["roof"]
    parts.append(group_start("roof", 0.5, 13.0))
    parts.append(text(0, -0.12, "P6 ROOF - cut 3 plies - underside drip scores"))
    parts.append(rect(0, 0, roof["width"], roof["depth"]))
    inset = 0.375
    parts.append(line(inset, inset, roof["width"] - inset, inset))
    parts.append(line(inset, inset, inset, roof["depth"] - inset))
    parts.append(line(roof["width"] - inset, inset, roof["width"] - inset, roof["depth"] - inset))
    parts.append("</g>")

    # Notes
    parts.append(group_start("welfare-notes", 11.25, 14.0))
    parts.append(text(0, 0, "Welfare gates: no perch, bare interior, cleanout, grip, baffle, woody cover."))
    parts.append(text(0, 0.4, "Drainage: corner notches. Ventilation: side slots. Validate with water and smoke tests."))
    parts.append(text(0, 0.8, "Cut red paths. Score green paths. Units are inches."))
    parts.append(
        text(
            0,
            1.2,
            f"Derived vent area per side: {geometry['derived']['vent_free_area_per_side_sq_in']} sq in.",
        )
    )
    parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> int:
    args = parse_args()
    params = load_params(args.input)
    geometry = derive_geometry(params)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "geometry_params.json").write_text(
        json.dumps(geometry, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.outdir / "panels.svg").write_text(build_svg(params, geometry) + "\n", encoding="utf-8")
    print(f"wrote {args.outdir / 'geometry_params.json'}")
    print(f"wrote {args.outdir / 'panels.svg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
