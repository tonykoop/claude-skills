#!/usr/bin/env python3
"""
Guided design intake for instrument-maker (v4.3 baseline; see CHANGELOG.md for v4.4+).

Turns a fuzzy instrument request into two small machine-readable artifacts:

    design-intake.json
    design-input-row.csv

Use it before generating a packet when the user has not already provided a
Master Catalog row or a fully populated design sheet.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile

from inspect_instrument_workbook import (
    NS,
    cell_text,
    is_blueish_input,
    read_xml,
    shared_strings,
    style_maps,
    workbook_sheets as workbook_sheet_parts,
)


DEFAULT_DESIGN_WORKBOOK = Path(
    "/mnt/c/Users/Tony/Documents/GitHub/Musical Instruments V2.xlsx"
)
DEFAULT_MASTER_WORKBOOK = Path(
    "/mnt/c/Users/Tony/Documents/Claude/Projects/Career/"
    "Instrument Workshop Master v3.xlsx"
)

CANONICAL_FIELDS = [
    "instrument_id",
    "family",
    "instrument_type",
    "variant_size",
    "key_scale",
    "target_fundamental_hz",
    "primary_material",
    "construction_pipeline",
    "design_workbook",
    "design_sheet",
    "master_workbook",
    "done_bar_repo",
    "visual_output_targets",
    "notes",
]


@dataclass
class Intake:
    instrument_id: str = "TBD"
    family: str = "TBD"
    instrument_type: str = "Instrument"
    variant_size: str = "Prototype"
    key_scale: str = "TBD"
    target_fundamental_hz: str = "TBD"
    primary_material: str = "TBD"
    construction_pipeline: str = "TBD"
    design_workbook: str = ""
    design_sheet: str = ""
    master_workbook: str = ""
    done_bar_repo: str = "TBD"
    visual_output_targets: str = "dxf,preview-svg,image-prompts"
    notes: str = ""
    generated_on: str = field(default_factory=lambda: date.today().isoformat())
    workbook_hint: dict[str, object] = field(default_factory=dict)


def workbook_sheets(path: Path) -> list[str]:
    with ZipFile(path) as zf:
        return list(workbook_sheet_parts(zf).keys())


def infer_sheet(path: Path, query: str) -> str:
    sheets = workbook_sheets(path)
    needle = query.lower().replace("-", " ")
    scored: list[tuple[int, str]] = []
    for sheet in sheets:
        hay = sheet.lower().replace("-", " ")
        score = 0
        if hay == needle:
            score += 100
        if needle in hay or hay in needle:
            score += 50
        for token in needle.split():
            if token in hay:
                score += 5
        if score:
            scored.append((score, sheet))
    if not scored:
        return ""
    scored.sort(reverse=True)
    return scored[0][1]


def sheet_hint(path: Path, sheet_name: str) -> dict[str, object]:
    if not path.exists() or not sheet_name:
        return {}
    with ZipFile(path) as zf:
        sheet_parts = workbook_sheet_parts(zf)
        if sheet_name not in sheet_parts:
            return {"sheet": sheet_name, "found": False}
        root = read_xml(zf, sheet_parts[sheet_name])
        strings = shared_strings(zf)
        fonts, fills, cell_xfs = style_maps(zf)
        dimension = root.find("main:dimension", NS)
        dimension_ref = dimension.attrib.get("ref", "") if dimension is not None else ""
        rows = root.findall("main:sheetData/main:row", NS)
    formulas = 0
    blue_cells: list[str] = []
    labels: list[str] = []
    for row in rows[:80]:
        row_values = []
        for cell in list(row)[:12]:
            value = cell_text(cell, strings)
            if value.startswith("="):
                formulas += 1
            if is_blueish_input(cell, fonts, fills, cell_xfs):
                blue_cells.append(cell.attrib.get("r", ""))
            if value not in (None, ""):
                row_values.append(str(value).strip())
        if row_values and len(labels) < 8:
            labels.append(" | ".join(row_values[:4]))
    return {
        "sheet": sheet_name,
        "found": True,
        "dimension": dimension_ref,
        "formula_count_first_80_rows": formulas,
        "blue_input_cells_sample": blue_cells[:20],
        "row_label_sample": labels,
    }


def prompt(default: str, label: str) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def apply_interactive(intake: Intake) -> Intake:
    intake.instrument_id = prompt(intake.instrument_id, "Instrument ID")
    intake.family = prompt(intake.family, "Family")
    intake.instrument_type = prompt(intake.instrument_type, "Instrument type")
    intake.variant_size = prompt(intake.variant_size, "Variant/size")
    intake.key_scale = prompt(intake.key_scale, "Key/scale")
    intake.target_fundamental_hz = prompt(
        intake.target_fundamental_hz, "Target fundamental Hz"
    )
    intake.primary_material = prompt(intake.primary_material, "Primary material")
    intake.construction_pipeline = prompt(
        intake.construction_pipeline, "Construction pipeline"
    )
    intake.design_sheet = prompt(intake.design_sheet, "Design workbook sheet")
    intake.done_bar_repo = prompt(intake.done_bar_repo, "Done-bar reference repo")
    intake.visual_output_targets = prompt(
        intake.visual_output_targets,
        "Visual output targets (comma-separated)",
    )
    intake.notes = prompt(intake.notes, "Notes")
    return intake


def intake_from_args(args: argparse.Namespace) -> Intake:
    design_workbook = args.design_workbook or DEFAULT_DESIGN_WORKBOOK
    master_workbook = args.master_workbook or DEFAULT_MASTER_WORKBOOK
    design_sheet = args.design_sheet or ""
    if args.infer_sheet:
        design_sheet = infer_sheet(design_workbook, args.infer_sheet)
    elif not design_sheet and args.instrument_type and design_workbook.exists():
        design_sheet = infer_sheet(design_workbook, args.instrument_type)
    intake = Intake(
        instrument_id=args.instrument_id or "TBD",
        family=args.family or "TBD",
        instrument_type=args.instrument_type or "Instrument",
        variant_size=args.variant_size or "Prototype",
        key_scale=args.key_scale or "TBD",
        target_fundamental_hz=args.target_fundamental_hz or "TBD",
        primary_material=args.primary_material or "TBD",
        construction_pipeline=args.construction_pipeline or "TBD",
        design_workbook=str(design_workbook),
        design_sheet=design_sheet,
        master_workbook=str(master_workbook),
        done_bar_repo=args.done_bar_repo or "TBD",
        visual_output_targets=args.visual_output_targets
        or "dxf,preview-svg,image-prompts",
        notes=args.notes or "",
    )
    if args.interactive:
        intake = apply_interactive(intake)
    if design_workbook.exists() and intake.design_sheet:
        intake.workbook_hint = sheet_hint(design_workbook, intake.design_sheet)
    return intake


def row_for_csv(intake: Intake) -> dict[str, str]:
    data = asdict(intake)
    return {field_name: str(data.get(field_name, "")) for field_name in CANONICAL_FIELDS}


def write_outputs(intake: Intake, output_dir: Path, dry_run: bool) -> None:
    output_dir = output_dir.expanduser()
    json_path = output_dir / "design-intake.json"
    csv_path = output_dir / "design-input-row.csv"
    if dry_run:
        print(f"--dry-run: would write {json_path}")
        print(f"--dry-run: would write {csv_path}")
        print(json.dumps(asdict(intake), indent=2))
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(asdict(intake), indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANONICAL_FIELDS)
        writer.writeheader()
        writer.writerow(row_for_csv(intake))
    print(json_path)
    print(csv_path)


def print_sheets(path: Path) -> None:
    for sheet in workbook_sheets(path):
        print(sheet)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instrument-id")
    parser.add_argument("--family")
    parser.add_argument("--instrument-type")
    parser.add_argument("--variant-size")
    parser.add_argument("--key-scale")
    parser.add_argument("--target-fundamental-hz")
    parser.add_argument("--primary-material")
    parser.add_argument("--construction-pipeline")
    parser.add_argument("--design-workbook", type=Path, default=DEFAULT_DESIGN_WORKBOOK)
    parser.add_argument("--design-sheet")
    parser.add_argument("--master-workbook", type=Path, default=DEFAULT_MASTER_WORKBOOK)
    parser.add_argument("--done-bar-repo")
    parser.add_argument(
        "--visual-output-targets",
        default="dxf,preview-svg,image-prompts",
        help=(
            "Comma-separated visual artifacts to request. Supported values: "
            "dxf, preview-svg, preview-pdf, image-prompts."
        ),
    )
    parser.add_argument("--notes", default="")
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Ask for missing fields at the terminal.",
    )
    parser.add_argument(
        "--infer-sheet",
        help="Find the closest sheet in the design workbook for this query.",
    )
    parser.add_argument(
        "--list-sheets",
        action="store_true",
        help="Print design workbook sheets and exit.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.list_sheets:
        print_sheets(args.design_workbook)
        return 0
    if args.interactive and not sys.stdin.isatty():
        raise SystemExit("--interactive requires a terminal")
    intake = intake_from_args(args)
    write_outputs(intake, args.output_dir, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
