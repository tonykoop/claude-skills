#!/usr/bin/env python3
"""Emit starter SolidWorks design table CSVs and equations files for common
sheet metal families. Output is planning material; treat shop tooling, K-factor,
and bend radius as assumptions until measured.
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from dataclasses import dataclass
from typing import Iterable


@dataclass
class BoxConfig:
    name: str
    length: float
    depth: float
    height: float
    material: str
    thickness: float
    inside_radius: float
    k_factor: float
    notes: str = ""


# Material defaults — planning values only.
MATERIAL_DEFAULTS = {
    "mild-steel": {
        "thickness": 0.060,
        "inside_radius": 0.060,
        "k_factor": 0.44,
    },
    "aluminum-5052": {
        "thickness": 0.063,
        "inside_radius": 0.063,
        "k_factor": 0.46,
    },
    "aluminum-6061": {
        "thickness": 0.063,
        "inside_radius": 0.080,
        "k_factor": 0.46,
    },
    "stainless-18ga": {
        "thickness": 0.048,
        "inside_radius": 0.048,
        "k_factor": 0.38,
    },
}


def seed_box_family(seed_l: float, seed_d: float, seed_h: float, material: str) -> list[BoxConfig]:
    """Generate a four-config size family from a seed envelope."""
    mat = MATERIAL_DEFAULTS.get(material, MATERIAL_DEFAULTS["mild-steel"])

    return [
        BoxConfig(
            name=f"BOX-{int(seed_l)}x{int(seed_d)}x{int(seed_h)}-SEED",
            length=seed_l, depth=seed_d, height=seed_h,
            material=material,
            thickness=mat["thickness"],
            inside_radius=mat["inside_radius"],
            k_factor=mat["k_factor"],
            notes="Seed configuration",
        ),
        BoxConfig(
            name=f"BOX-{int(seed_l * 0.8)}x{int(seed_d * 0.8)}x{int(seed_h * 0.75)}-COMPACT",
            length=round(seed_l * 0.8, 3),
            depth=round(seed_d * 0.8, 3),
            height=round(seed_h * 0.75, 3),
            material=material,
            thickness=mat["thickness"],
            inside_radius=mat["inside_radius"],
            k_factor=mat["k_factor"],
            notes="Compact variant; verify hardware pitch still fits",
        ),
        BoxConfig(
            name=f"BOX-{int(seed_l * 1.2)}x{int(seed_d * 1.2)}x{int(seed_h * 1.25)}-LARGE",
            length=round(seed_l * 1.2, 3),
            depth=round(seed_d * 1.2, 3),
            height=round(seed_h * 1.25, 3),
            material=material,
            thickness=mat["thickness"],
            inside_radius=mat["inside_radius"],
            k_factor=mat["k_factor"],
            notes="Large variant; verify stiffness with return flanges or thicker stock",
        ),
        BoxConfig(
            name=f"BOX-{int(seed_l)}x{int(seed_d)}x{int(seed_h)}-{material.upper().replace('-', '_')}-ALT",
            length=seed_l, depth=seed_d, height=seed_h,
            material=material,
            thickness=mat["thickness"],
            inside_radius=mat["inside_radius"],
            k_factor=mat["k_factor"],
            notes="Material alternate; flat pattern will differ — re-export DXF",
        ),
    ]


def write_design_table_csv(configs: Iterable[BoxConfig], stream: io.TextIOBase) -> None:
    writer = csv.writer(stream)
    writer.writerow([
        "Configuration",
        "Box_Length_in",
        "Box_Depth_in",
        "Box_Height_in",
        "Material",
        "Material_Thickness_in",
        "Inside_Bend_Radius_in",
        "K_Factor",
        "Notes",
    ])
    for c in configs:
        writer.writerow([
            c.name,
            c.length,
            c.depth,
            c.height,
            c.material,
            c.thickness,
            c.inside_radius,
            c.k_factor,
            c.notes,
        ])


def write_equations_block(seed: BoxConfig, stream: io.TextIOBase) -> None:
    stream.write(f'"Box_Length"           = {seed.length:.3f}in\n')
    stream.write(f'"Box_Depth"            = {seed.depth:.3f}in\n')
    stream.write(f'"Box_Height"           = {seed.height:.3f}in\n')
    stream.write(f'"Material_Thickness"   = {seed.thickness:.3f}in\n')
    stream.write(f'"Inside_Bend_Radius"   = "Material_Thickness"\n')
    stream.write(f'"K_Factor"             = {seed.k_factor:.3f}\n')
    stream.write(f'"Clearance_Gap"        = 0.030in\n')
    stream.write(f'"Lid_Drop"             = 1.500in\n')
    stream.write(f'"Hardware_Pitch"       = 2.000in\n')
    stream.write(f'"Relief_Size"          = 2 * "Material_Thickness"\n')
    stream.write(f'"Min_Flange"           = 4 * "Material_Thickness"\n')
    stream.write(f'"Min_Hole_To_Bend"     = 3 * "Material_Thickness"\n')


def parse_seed(seed: str) -> tuple[float, float, float]:
    parts = seed.lower().replace(" ", "").split("x")
    if len(parts) != 3:
        raise SystemExit(f"--seed must look like 20x10x8 (LxDxH), got '{seed}'")
    try:
        l, d, h = (float(p) for p in parts)
    except ValueError:
        raise SystemExit(f"--seed values must be numbers, got '{seed}'")
    return l, d, h


def cmd_box_family(args: argparse.Namespace) -> None:
    seed_l, seed_d, seed_h = parse_seed(args.seed)
    if args.material not in MATERIAL_DEFAULTS:
        known = ", ".join(sorted(MATERIAL_DEFAULTS))
        raise SystemExit(f"unknown material '{args.material}'. Known: {known}")

    configs = seed_box_family(seed_l, seed_d, seed_h, args.material)
    out = sys.stdout

    if args.equations:
        write_equations_block(configs[0], out)
        out.write("\n")
    write_design_table_csv(configs, out)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Emit a starter SolidWorks design table CSV (and optional equations block) "
            "for a parametric sheet metal family. Output is planning material."
        )
    )
    sub = parser.add_subparsers(required=True)

    box = sub.add_parser("box-family", help="Generate a 4-config box size family.")
    box.add_argument("--seed", required=True, help="Seed envelope as LxDxH, e.g. 20x10x8.")
    box.add_argument(
        "--material",
        default="mild-steel",
        help="Material key. One of: " + ", ".join(sorted(MATERIAL_DEFAULTS)),
    )
    box.add_argument(
        "--equations",
        action="store_true",
        help="Also emit a SolidWorks Equations block before the CSV.",
    )
    box.set_defaults(func=cmd_box_family)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
