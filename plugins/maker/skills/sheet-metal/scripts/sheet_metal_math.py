#!/usr/bin/env python3
"""Small deterministic helpers for sheet-metal planning estimates."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass


DENSITY_LB_PER_IN3 = {
    "mild-steel": 0.284,
    "steel": 0.284,
    "stainless": 0.289,
    "aluminum": 0.098,
    "brass": 0.307,
    "copper": 0.323,
    "titanium": 0.163,
}

COMBAT_CLASSES = {
    "antweight": {
        "limit_lb": 1.0,
        "limit_g": 454,
        "target_chassis_g_min": 100,
        "target_chassis_g_max": 130,
        "starting_material": "0.031 in 6061-T6 aluminum or 0.020 in Grade 2 titanium",
    },
    "beetleweight": {
        "limit_lb": 3.0,
        "limit_g": 1360,
        "target_chassis_g_min": 300,
        "target_chassis_g_max": 400,
        "starting_material": "0.062 in 6061-T6 aluminum or 0.040 in Grade 2 titanium",
    },
}


@dataclass
class BendAllowance:
    angle_deg: float
    inside_radius: float
    thickness: float
    k_factor: float
    bend_allowance: float
    min_flange_length: float
    min_hole_distance_from_bend: float


@dataclass
class CylinderBlank:
    diameter: float
    height: float
    seam_allowance: float
    trim_margin_each_end: float
    developed_width: float
    developed_height: float
    note: str


@dataclass
class WeightEstimate:
    material: str
    area_in2: float
    thickness_in: float
    density_lb_per_in3: float
    volume_in3: float
    weight_lb: float
    weight_g: float


def rounded(value: float) -> float:
    return round(value, 6)


def emit(data, as_json: bool) -> None:
    payload = asdict(data) if hasattr(data, "__dataclass_fields__") else data
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    for key, value in payload.items():
        print(f"{key}: {value}")


def bend_allowance(args: argparse.Namespace) -> None:
    ba = math.pi * args.angle_deg / 180.0 * (
        args.radius + args.k_factor * args.thickness
    )
    result = BendAllowance(
        angle_deg=args.angle_deg,
        inside_radius=args.radius,
        thickness=args.thickness,
        k_factor=args.k_factor,
        bend_allowance=rounded(ba),
        min_flange_length=rounded(4.0 * args.thickness),
        min_hole_distance_from_bend=rounded(3.0 * args.thickness),
    )
    emit(result, args.json)


def cylinder_blank(args: argparse.Namespace) -> None:
    developed_width = (
        math.pi * args.diameter + args.seam_allowance + 2.0 * args.trim_margin
    )
    result = CylinderBlank(
        diameter=args.diameter,
        height=args.height,
        seam_allowance=args.seam_allowance,
        trim_margin_each_end=args.trim_margin,
        developed_width=rounded(developed_width),
        developed_height=args.height,
        note="Slip rollers leave flatter lead/trail regions; trim margin is sacrificial unless pre-bent.",
    )
    emit(result, args.json)


def weight(args: argparse.Namespace) -> None:
    material = args.material.lower()
    if material not in DENSITY_LB_PER_IN3:
        known = ", ".join(sorted(DENSITY_LB_PER_IN3))
        raise SystemExit(f"unknown material '{args.material}'. Known: {known}")
    density = DENSITY_LB_PER_IN3[material]
    volume = args.area * args.thickness
    weight_lb = volume * density
    result = WeightEstimate(
        material=material,
        area_in2=args.area,
        thickness_in=args.thickness,
        density_lb_per_in3=density,
        volume_in3=rounded(volume),
        weight_lb=rounded(weight_lb),
        weight_g=rounded(weight_lb * 453.59237),
    )
    emit(result, args.json)


def combat_budget(args: argparse.Namespace) -> None:
    key = args.class_name.lower()
    if key not in COMBAT_CLASSES:
        known = ", ".join(sorted(COMBAT_CLASSES))
        raise SystemExit(f"unknown combat class '{args.class_name}'. Known: {known}")
    result = dict(COMBAT_CLASSES[key])
    result["class"] = key
    result["notes"] = [
        "Estimate full robot weight before committing chassis material.",
        "Default to R >= T for bends unless a test coupon proves tighter.",
        "Prefer mechanical interlocks for very thin micro-bot sheet metal.",
    ]
    emit(result, args.json)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sheet metal planning estimates. Outputs are not a substitute for measured tooling or shop approval."
    )
    subparsers = parser.add_subparsers(required=True)

    bend = subparsers.add_parser("bend-allowance", help="Calculate bend allowance.")
    bend.add_argument("--angle-deg", type=float, required=True)
    bend.add_argument("--radius", type=float, required=True, help="Inside bend radius.")
    bend.add_argument("--thickness", type=float, required=True)
    bend.add_argument("--k-factor", type=float, required=True)
    bend.add_argument("--json", action="store_true")
    bend.set_defaults(func=bend_allowance)

    cyl = subparsers.add_parser(
        "cylinder-blank", help="Estimate a rectangular blank for a rolled cylinder."
    )
    cyl.add_argument("--diameter", type=float, required=True)
    cyl.add_argument("--height", type=float, required=True)
    cyl.add_argument("--seam-allowance", type=float, default=0.0)
    cyl.add_argument("--trim-margin", type=float, default=0.0)
    cyl.add_argument("--json", action="store_true")
    cyl.set_defaults(func=cylinder_blank)

    wt = subparsers.add_parser("weight", help="Estimate sheet weight from area.")
    wt.add_argument("--material", required=True)
    wt.add_argument("--area", type=float, required=True, help="Area in square inches.")
    wt.add_argument("--thickness", type=float, required=True, help="Thickness in inches.")
    wt.add_argument("--json", action="store_true")
    wt.set_defaults(func=weight)

    bot = subparsers.add_parser(
        "combat-budget", help="Print planning weight budget for micro combat robots."
    )
    bot.add_argument("--class", dest="class_name", required=True)
    bot.add_argument("--json", action="store_true")
    bot.set_defaults(func=combat_budget)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
