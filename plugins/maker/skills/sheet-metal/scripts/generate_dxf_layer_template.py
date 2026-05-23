#!/usr/bin/env python3
"""Emit a standard DXF layer-naming template for plasma/laser handoff. The
template covers cut, mark, etch, bend-centerline, construction, registration,
and drill-later layers, with planning conventions for each.

This script does not produce a DXF file. It produces a small CSV or JSON
manifest describing the layer scheme; humans paste this into the actual DXF
creation tool (SolidWorks, Illustrator, LightBurn, Inkscape, etc.).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, asdict
from typing import Iterable


@dataclass
class LayerSpec:
    name: str
    purpose: str
    cam_action: str
    color_hint: str
    line_weight: str
    notes: str


def standard_layers() -> list[LayerSpec]:
    return [
        LayerSpec(
            name="cut",
            purpose="The actual cut profile — what the plasma/laser will cut through.",
            cam_action="through-cut",
            color_hint="red",
            line_weight="0.001 in (hairline)",
            notes="All loops must be closed. Splines converted to arcs/lines if CAM requires.",
        ),
        LayerSpec(
            name="mark",
            purpose="Low-power surface mark for layout, station lines, alignment witness.",
            cam_action="low-power scribe",
            color_hint="orange",
            line_weight="0.001 in",
            notes="Cuts shallow; for sheet metal: helps align before forming, no through-cut.",
        ),
        LayerSpec(
            name="etch",
            purpose="Surface text, logos, decorative marks.",
            cam_action="raster or vector etch",
            color_hint="blue",
            line_weight="0.001 in",
            notes="For laser; plasma typically can't etch precisely. Keep text >= 1/4 in tall.",
        ),
        LayerSpec(
            name="bend-centerline",
            purpose="Bend line locations from the SolidWorks flat pattern.",
            cam_action="ignore (for human reference only)",
            color_hint="green",
            line_weight="0.002 in",
            notes="Some users hand-scribe bend lines; in CAM this layer must be excluded.",
        ),
        LayerSpec(
            name="construction",
            purpose="Datums, centerlines, dimension chains, anything not cut.",
            cam_action="ignore",
            color_hint="gray",
            line_weight="0.0005 in",
            notes="CAM must exclude this layer entirely.",
        ),
        LayerSpec(
            name="registration",
            purpose="Holes used to align stacked layers, locate parts, or fixture dowels.",
            cam_action="through-cut (precise diameter)",
            color_hint="purple",
            line_weight="0.001 in",
            notes="Typical 1/8 in (3.175 mm) holes for brass dowel pins. Three holes minimum, non-collinear.",
        ),
        LayerSpec(
            name="drill-later",
            purpose="Hole locations too small to plasma cleanly — pierce-only, drill or ream later.",
            cam_action="pierce/center-mark",
            color_hint="yellow",
            line_weight="0.001 in",
            notes="Use for holes smaller than ~2*T on plasma. Laser can typically cut smaller.",
        ),
    ]


def write_csv(layers: Iterable[LayerSpec], stream) -> None:
    writer = csv.writer(stream)
    writer.writerow([
        "layer_name",
        "purpose",
        "cam_action",
        "color_hint",
        "line_weight",
        "notes",
    ])
    for L in layers:
        writer.writerow([L.name, L.purpose, L.cam_action, L.color_hint, L.line_weight, L.notes])


def write_json(layers: Iterable[LayerSpec], stream) -> None:
    payload = {
        "layer_scheme": "sheet-metal default",
        "units": "inch",
        "layers": [asdict(L) for L in layers],
        "notes": [
            "Replace `inch` with `mm` if exporting in SI units; also update line weights.",
            "Every loop in the `cut` layer must be closed.",
            "Every layer color must be distinct in the source file so CAM can isolate it.",
            "Verify your CAM software respects layer-based action assignment before relying on this scheme.",
        ],
    }
    json.dump(payload, stream, indent=2)
    stream.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Emit a standard DXF layer-naming template (CSV or JSON) for sheet metal "
            "handoff to plasma, laser, or waterjet CAM workflows."
        )
    )
    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        help="Output format (default: csv).",
    )
    parser.add_argument(
        "--units",
        choices=["inch", "mm"],
        default="inch",
        help="Units the template references in notes (default: inch).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    layers = standard_layers()
    if args.format == "csv":
        write_csv(layers, sys.stdout)
    else:
        write_json(layers, sys.stdout)


if __name__ == "__main__":
    main()
