#!/usr/bin/env python3
"""Generate a DXF starter layout for a folded stopped-pipe drone.

The input is a centerline-station CSV with at least:

    station_id,x_mm,y_mm,width_mm

Optional columns:

    height_mm,bend_radius_mm,role,note

The output is an AutoCAD R12-style DXF with centerline, duct wall offsets,
bend markers, tuning-tail notes, leak-test notes, breath-contact safety
notes, and a straight reference tube comparison. It is a fabrication starter
for CAD/CAM review, not verified G-code.

Exit codes:
  0   - generated or dry-run cleanly
  2   - bad invocation or malformed CSV
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


DXF_LAYERS = [
    "DUCT_CENTERLINE",
    "DUCT_LEFT_WALL",
    "DUCT_RIGHT_WALL",
    "FOLD_BEND_ZONE",
    "TUNING_TAIL",
    "LEAK_TEST_NOTES",
    "BREATH_SAFETY_NOTES",
    "NOTES_NO_CUT",
]

SPEED_OF_SOUND_BASE_M_S = 331.3


@dataclass
class Station:
    station_id: str
    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float
    bend_radius_mm: float = 0.0
    role: str = ""
    note: str = ""


@dataclass
class DroneSummary:
    station_count: int
    centerline_length_mm: float
    equivalent_diameter_mm: float
    target_hz: float
    playing_temperature_C: float
    room_temperature_C: float
    warm_straight_reference_length_mm: float
    room_straight_reference_length_mm: float
    tuning_tail_mm: float


def parse_float(row: dict, key: str, default: float | None = None) -> float:
    value = (row.get(key) or "").strip()
    if not value:
        if default is None:
            raise ValueError(f"missing required numeric column {key!r}")
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"invalid numeric value for {key!r}: {value!r}") from exc


def load_stations(path: Path, default_height_mm: float) -> list[Station]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise ValueError("station CSV has no rows")
    required = {"station_id", "x_mm", "y_mm", "width_mm"}
    missing = sorted(required - set(reader.fieldnames or []))
    if missing:
        raise ValueError(f"station CSV missing required columns: {', '.join(missing)}")

    stations: list[Station] = []
    for index, row in enumerate(rows, start=1):
        station_id = (row.get("station_id") or "").strip()
        if not station_id:
            raise ValueError(f"row {index}: station_id is required")
        stations.append(Station(
            station_id=station_id,
            x_mm=parse_float(row, "x_mm"),
            y_mm=parse_float(row, "y_mm"),
            width_mm=parse_float(row, "width_mm"),
            height_mm=parse_float(row, "height_mm", default_height_mm),
            bend_radius_mm=parse_float(row, "bend_radius_mm", 0.0),
            role=(row.get("role") or "").strip(),
            note=(row.get("note") or "").strip(),
        ))
    if len(stations) < 2:
        raise ValueError("at least two stations are required")
    return stations


def speed_of_sound_mm_s(temp_c: float) -> float:
    return SPEED_OF_SOUND_BASE_M_S * math.sqrt(1.0 + temp_c / 273.15) * 1000.0


def equivalent_diameter_mm(width_mm: float, height_mm: float) -> float:
    area = width_mm * height_mm
    return 2.0 * math.sqrt(area / math.pi)


def stopped_pipe_geom_length_mm(target_hz: float, temp_c: float,
                                equiv_diameter_mm: float) -> float:
    if target_hz <= 0:
        raise ValueError("target_hz must be positive")
    l_eff = speed_of_sound_mm_s(temp_c) / (4.0 * target_hz)
    return l_eff - 0.82 * equiv_diameter_mm


def centerline_length_mm(stations: list[Station]) -> float:
    total = 0.0
    for a, b in zip(stations, stations[1:]):
        total += math.hypot(b.x_mm - a.x_mm, b.y_mm - a.y_mm)
    return total


def build_summary(stations: list[Station], target_hz: float,
                  playing_temperature_c: float, room_temperature_c: float,
                  tuning_tail_mm: float) -> DroneSummary:
    first = stations[0]
    d_eq = equivalent_diameter_mm(first.width_mm, first.height_mm)
    return DroneSummary(
        station_count=len(stations),
        centerline_length_mm=centerline_length_mm(stations),
        equivalent_diameter_mm=d_eq,
        target_hz=target_hz,
        playing_temperature_C=playing_temperature_c,
        room_temperature_C=room_temperature_c,
        warm_straight_reference_length_mm=stopped_pipe_geom_length_mm(
            target_hz, playing_temperature_c, d_eq),
        room_straight_reference_length_mm=stopped_pipe_geom_length_mm(
            target_hz, room_temperature_c, d_eq),
        tuning_tail_mm=tuning_tail_mm,
    )


def dxf_header() -> str:
    colors = {
        "DUCT_CENTERLINE": 3,
        "DUCT_LEFT_WALL": 7,
        "DUCT_RIGHT_WALL": 7,
        "FOLD_BEND_ZONE": 1,
        "TUNING_TAIL": 5,
        "LEAK_TEST_NOTES": 2,
        "BREATH_SAFETY_NOTES": 4,
        "NOTES_NO_CUT": 8,
    }
    layer_rows = []
    for layer in DXF_LAYERS:
        layer_rows.extend([
            "0", "LAYER", "2", layer, "70", "0",
            "62", str(colors.get(layer, 7)), "6", "CONTINUOUS",
        ])
    return "\n".join([
        "0", "SECTION",
        "2", "HEADER",
        "9", "$ACADVER",
        "1", "AC1009",
        "9", "$INSUNITS",
        "70", "4",
        "0", "ENDSEC",
        "0", "SECTION",
        "2", "TABLES",
        "0", "TABLE",
        "2", "LAYER",
        "70", str(len(DXF_LAYERS)),
        *layer_rows,
        "0", "ENDTAB",
        "0", "ENDSEC",
        "0", "SECTION",
        "2", "ENTITIES",
    ])


def dxf_footer() -> str:
    return "\n".join(["0", "ENDSEC", "0", "EOF", ""])


def dxf_line(layer: str, x1: float, y1: float, x2: float, y2: float) -> str:
    return "\n".join([
        "0", "LINE", "8", layer,
        "10", f"{x1:.3f}", "20", f"{y1:.3f}", "30", "0",
        "11", f"{x2:.3f}", "21", f"{y2:.3f}", "31", "0",
    ])


def dxf_circle(layer: str, x: float, y: float, radius: float) -> str:
    return "\n".join([
        "0", "CIRCLE", "8", layer,
        "10", f"{x:.3f}", "20", f"{y:.3f}", "30", "0",
        "40", f"{radius:.3f}",
    ])


def dxf_text(layer: str, x: float, y: float, text: str,
             height: float = 18.0) -> str:
    safe = str(text).replace("\n", " ")[:240]
    return "\n".join([
        "0", "TEXT", "8", layer,
        "10", f"{x:.3f}", "20", f"{y:.3f}", "30", "0",
        "40", f"{height:.3f}", "1", safe,
    ])


def offset_segment(a: Station, b: Station, side: float) -> tuple[float, float, float, float]:
    dx = b.x_mm - a.x_mm
    dy = b.y_mm - a.y_mm
    length = math.hypot(dx, dy)
    if length == 0:
        raise ValueError(f"zero-length segment at station {a.station_id!r}")
    nx = -dy / length
    ny = dx / length
    return (
        a.x_mm + nx * (a.width_mm / 2.0) * side,
        a.y_mm + ny * (a.width_mm / 2.0) * side,
        b.x_mm + nx * (b.width_mm / 2.0) * side,
        b.y_mm + ny * (b.width_mm / 2.0) * side,
    )


def generate_dxf(stations: list[Station], source_label: str,
                 summary: DroneSummary) -> str:
    entities: list[str] = [dxf_header()]

    for a, b in zip(stations, stations[1:]):
        entities.append(dxf_line("DUCT_CENTERLINE", a.x_mm, a.y_mm, b.x_mm, b.y_mm))
        entities.append(dxf_line("DUCT_LEFT_WALL", *offset_segment(a, b, 1.0)))
        entities.append(dxf_line("DUCT_RIGHT_WALL", *offset_segment(a, b, -1.0)))

    for station in stations[1:-1]:
        if station.bend_radius_mm > 0 or station.role.lower() == "fold":
            radius = station.bend_radius_mm if station.bend_radius_mm > 0 else station.width_mm
            entities.append(dxf_circle("FOLD_BEND_ZONE", station.x_mm, station.y_mm, radius))
            entities.append(dxf_text(
                "FOLD_BEND_ZONE", station.x_mm + 8, station.y_mm + 8,
                f"{station.station_id}: bend radius {radius:.1f} mm"))
        if station.role.lower() == "tuning_tail":
            entities.append(dxf_text(
                "TUNING_TAIL", station.x_mm, station.y_mm + 28,
                f"{station.station_id}: removable tuning tail begins"))

    last = stations[-1]
    entities.append(dxf_text(
        "TUNING_TAIL", last.x_mm, last.y_mm + 28,
        f"Reserve {summary.tuning_tail_mm:.0f} mm removable/trim tail before final pitch."))

    min_x = min(s.x_mm for s in stations)
    max_y = max(s.y_mm for s in stations)
    note_x = min_x
    note_y = max_y + 80
    entities.extend([
        dxf_text("NOTES_NO_CUT", note_x, note_y,
                 "Folded stopped-pipe drone DXF starter; units=mm; not CAM.", 16),
        dxf_text("NOTES_NO_CUT", note_x, note_y + 28,
                 f"Source CSV: {source_label}; centerline={summary.centerline_length_mm:.1f} mm; d_eq={summary.equivalent_diameter_mm:.1f} mm.", 14),
        dxf_text("NOTES_NO_CUT", note_x, note_y + 54,
                 f"Warm straight reference ({summary.playing_temperature_C:.1f} C)={summary.warm_straight_reference_length_mm:.1f} mm for {summary.target_hz:.2f} Hz.", 14),
        dxf_text("NOTES_NO_CUT", note_x, note_y + 80,
                 f"Room straight reference ({summary.room_temperature_C:.1f} C)={summary.room_straight_reference_length_mm:.1f} mm.", 14),
        dxf_text("LEAK_TEST_NOTES", note_x, note_y + 112,
                 "Leak-test before and after finish; check seams, tuning tail, and mouthpiece gasket.", 14),
        dxf_text("BREATH_SAFETY_NOTES", note_x, note_y + 140,
                 "Breath path requires cured non-toxic finish, cleanable/removable mouthpiece, and moisture drainage.", 14),
    ])

    entities.append(dxf_footer())
    return "\n".join(entities)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stations_csv", type=Path,
                        help="CSV with station_id,x_mm,y_mm,width_mm")
    parser.add_argument("--output", type=Path,
                        help="DXF output path. Defaults to <stations_csv>.dxf")
    parser.add_argument("--duct-height-mm", type=float, default=42.0,
                        help="Default duct height when height_mm column is blank.")
    parser.add_argument("--target-hz", type=float, default=82.41,
                        help="Target stopped-pipe fundamental; default E2.")
    parser.add_argument("--playing-temperature-c", type=float, default=33.0,
                        help="Breath-warmed playing temperature for tuning.")
    parser.add_argument("--room-temperature-c", type=float, default=20.0,
                        help="Cool room comparison temperature.")
    parser.add_argument("--tuning-tail-mm", type=float, default=180.0,
                        help="Removable/trim tuning tail allowance.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print summary and do not write the DXF.")
    parser.add_argument("--json", action="store_true",
                        help="Print summary as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.stations_csv.exists():
        print(f"station CSV not found: {args.stations_csv}", file=sys.stderr)
        return 2

    try:
        stations = load_stations(args.stations_csv, args.duct_height_mm)
        summary = build_summary(
            stations,
            target_hz=args.target_hz,
            playing_temperature_c=args.playing_temperature_c,
            room_temperature_c=args.room_temperature_c,
            tuning_tail_mm=args.tuning_tail_mm,
        )
        dxf = generate_dxf(stations, args.stations_csv.name, summary)
    except (OSError, csv.Error, ValueError) as exc:
        print(f"could not generate folded-drone DXF: {exc}", file=sys.stderr)
        return 2

    output = args.output or args.stations_csv.with_suffix(".dxf")

    if args.json:
        print(json.dumps(asdict(summary), indent=2))
    else:
        print("generate_folded_drone_dxf:")
        print(f"  stations={summary.station_count}")
        print(f"  centerline_length_mm={summary.centerline_length_mm:.1f}")
        print(f"  equivalent_diameter_mm={summary.equivalent_diameter_mm:.1f}")
        print(f"  warm_straight_reference_length_mm={summary.warm_straight_reference_length_mm:.1f}")
        print(f"  room_straight_reference_length_mm={summary.room_straight_reference_length_mm:.1f}")

    if args.dry_run:
        print(f"  --dry-run: would write {output} ({len(dxf)} bytes)")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(dxf, encoding="utf-8")
    print(f"  wrote {output} ({len(dxf)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
