#!/usr/bin/env python3
"""Generate an instrument build packet from a Master Catalog row and design sheet."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
from pathlib import Path
from zipfile import ZipFile

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from inspect_instrument_workbook import (  # noqa: E402
    NS,
    cell_text,
    column_number,
    read_xml,
    shared_strings,
    style_maps,
    table_info,
    workbook_sheets,
    is_blueish_input,
)


DEFAULT_MASTER = Path(
    "/mnt/c/Users/Tony/Documents/Claude/Projects/Career/Instrument Workshop Master v3.xlsx"
)
DEFAULT_DESIGN = Path(
    "/mnt/c/Users/Tony/Documents/Claude/Projects/Career/flutes-staging/Flutes-AI.xlsx"
)


def split_cell(ref: str) -> tuple[int, int]:
    match = re.fullmatch(r"([A-Z]+)(\d+)", ref)
    if not match:
        raise ValueError(f"Invalid cell reference: {ref}")
    return column_number(match.group(1)), int(match.group(2))


def parse_range(ref: str) -> tuple[int, int, int, int]:
    start, end = ref.split(":", 1)
    start_col, start_row = split_cell(start)
    end_col, end_row = split_cell(end)
    return start_col, start_row, end_col, end_row


def worksheet_cells(zf: ZipFile, sheet_part: str) -> tuple[dict[int, dict[int, str]], object]:
    strings = shared_strings(zf)
    root = read_xml(zf, sheet_part)
    rows: dict[int, dict[int, str]] = {}
    for cell in root.findall(".//main:c", NS):
        ref = cell.attrib.get("r", "")
        match = re.fullmatch(r"([A-Z]+)(\d+)", ref)
        if not match:
            continue
        col = column_number(match.group(1))
        row = int(match.group(2))
        rows.setdefault(row, {})[col] = cell_text(cell, strings)
    return rows, root


def load_table_rows(
    workbook: Path,
    sheet_name: str,
    preferred_table: str | None = None,
) -> list[dict[str, str]]:
    with ZipFile(workbook) as zf:
        sheets = workbook_sheets(zf)
        if sheet_name not in sheets:
            raise SystemExit(f"Sheet not found in {workbook}: {sheet_name}")
        sheet_part = sheets[sheet_name]
        tables = table_info(zf, sheet_part)
        if not tables:
            raise SystemExit(f"No Excel table found on sheet: {sheet_name}")
        table = tables[0]
        if preferred_table:
            for candidate in tables:
                names = {candidate.get("name"), candidate.get("display_name")}
                if preferred_table in names:
                    table = candidate
                    break
        ref = str(table["ref"])
        start_col, start_row, end_col, end_row = parse_range(ref)
        rows, _root = worksheet_cells(zf, sheet_part)
        headers = [
            rows.get(start_row, {}).get(col, "").strip()
            for col in range(start_col, end_col + 1)
        ]
        records: list[dict[str, str]] = []
        for row_num in range(start_row + 1, end_row + 1):
            values = [rows.get(row_num, {}).get(col, "") for col in range(start_col, end_col + 1)]
            if not any(str(value).strip() for value in values):
                continue
            record = {header: value for header, value in zip(headers, values) if header}
            record["_excel_row"] = str(row_num)
            records.append(record)
        return records


def find_catalog_row(
    master_workbook: Path,
    instrument_id: str | None,
    master_row: int | None,
) -> dict[str, str]:
    records = load_table_rows(master_workbook, "Master Catalog", "tblCatalog")
    if instrument_id:
        wanted = instrument_id.strip().lower()
        for record in records:
            if record.get("Instrument ID", "").strip().lower() == wanted:
                return record
        raise SystemExit(f"Instrument ID not found in Master Catalog: {instrument_id}")
    if master_row is not None:
        for record in records:
            if record.get("_excel_row") == str(master_row):
                return record
        raise SystemExit(f"Master Catalog Excel row not found: {master_row}")
    raise SystemExit("Provide --instrument-id or --master-row.")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "instrument-build"


def truncate(text: object, width: int = 120) -> str:
    value = str(text).replace("\n", " / ").strip()
    if len(value) <= width:
        return value
    return value[: max(0, width - 3)].rstrip() + "..."


def resolve_design_workbook(explicit: Path | None) -> Path | None:
    if explicit:
        return explicit
    if DEFAULT_DESIGN.exists():
        return DEFAULT_DESIGN
    return None


def summarize_design_sheet(workbook: Path | None, sheet_name: str | None) -> dict[str, object]:
    if not workbook or not sheet_name:
        return {"available": False, "reason": "No design workbook/sheet provided or resolved."}
    if not workbook.exists():
        return {"available": False, "reason": f"Design workbook not found: {workbook}"}

    with ZipFile(workbook) as zf:
        sheets = workbook_sheets(zf)
        if sheet_name not in sheets:
            return {
                "available": False,
                "reason": f"Design sheet not found: {sheet_name}",
                "workbook": str(workbook),
            }
        sheet_part = sheets[sheet_name]
        strings = shared_strings(zf)
        fonts, fills, cell_xfs = style_maps(zf)
        root = read_xml(zf, sheet_part)
        dimension = root.find("main:dimension", NS)
        cells = root.findall(".//main:c", NS)
        formulas = [
            {"cell": cell.attrib.get("r", ""), "formula": formula.text or ""}
            for cell in cells
            for formula in [cell.find("main:f", NS)]
            if formula is not None and formula.text
        ][:12]
        rows: list[dict[str, object]] = []
        for row in root.findall("main:sheetData/main:row", NS):
            values = [""] * 10
            has_value = False
            for cell in row.findall("main:c", NS):
                col = column_number(cell.attrib.get("r", ""))
                if 1 <= col <= len(values):
                    value = cell_text(cell, strings)
                    values[col - 1] = truncate(value, 80)
                    has_value = has_value or bool(str(value).strip())
            if has_value:
                rows.append({"row": row.attrib.get("r", ""), "values": values})
            if len(rows) >= 14:
                break
        return {
            "available": True,
            "workbook": str(workbook),
            "sheet": sheet_name,
            "dimension": dimension.attrib.get("ref") if dimension is not None else "",
            "cells": len(cells),
            "formulas": len(root.findall(".//main:f", NS)),
            "blueish_inputs": sum(
                1 for cell in cells if is_blueish_input(cell, fonts, fills, cell_xfs)
            ),
            "tables": table_info(zf, sheet_part),
            "formula_examples": formulas,
            "sample_rows": rows,
        }


def markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header = rows[0]
    sep = ["---"] * len(header)
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in rows[1:]:
        clean = [str(cell).replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(clean) + " |")
    return "\n".join(lines)


def catalog_markdown(record: dict[str, str]) -> str:
    rows = [["Field", "Value"]]
    for key, value in record.items():
        if key.startswith("_") or not str(value).strip():
            continue
        rows.append([key, truncate(value, 160)])
    return markdown_table(rows)


def design_summary_markdown(summary: dict[str, object]) -> str:
    if not summary.get("available"):
        return f"Design sheet summary unavailable: {summary.get('reason')}\n"
    lines = [
        f"- Workbook: `{summary['workbook']}`",
        f"- Sheet: `{summary['sheet']}`",
        f"- Used range: `{summary['dimension']}`",
        f"- Cells/formulas/blue inputs: `{summary['cells']}` / `{summary['formulas']}` / `{summary['blueish_inputs']}`",
    ]
    tables = summary.get("tables") or []
    if tables:
        lines.append("- Tables:")
        for table in tables:  # type: ignore[assignment]
            headers = ", ".join(table.get("headers", []))
            lines.append(f"  - `{table.get('display_name')}` `{table.get('ref')}`: {headers}")
    formulas = summary.get("formula_examples") or []
    if formulas:
        lines.append("- Formula examples:")
        for item in formulas:  # type: ignore[assignment]
            lines.append(f"  - `{item['cell']}`: `={truncate(item['formula'], 100)}`")
    samples = summary.get("sample_rows") or []
    if samples:
        lines.append("- First non-empty rows:")
        for row in samples:  # type: ignore[assignment]
            values = " | ".join(value for value in row["values"] if value)
            lines.append(f"  - Row {row['row']}: {truncate(values, 180)}")
    return "\n".join(lines) + "\n"


def infer_subsystem_rows(record: dict[str, str]) -> list[list[str]]:
    family = record.get("Family", "")
    instrument_type = record.get("Instrument Type", "Instrument")
    instrument_lower = instrument_type.lower()
    material = record.get("Primary Material", "") or "TBD"
    estimated_cost = record.get("Estimated Cost", "")
    rows = [
        [
            "1",
            "Primary structure",
            f"{instrument_type} body/shell/blank",
            "1",
            record.get("Variant/Size", "") or "TBD",
            material,
            "Make",
            "TBD",
            "",
            estimated_cost,
            "drawings/primary-structure.pdf",
            "Populate from design sheet and CAD model.",
        ],
        [
            "2",
            "Sound system",
            "Sound-producing element set",
            "1 set",
            record.get("Key/Scale", "") or "TBD tuning/range",
            "TBD",
            "Make/Buy",
            "TBD",
            "",
            "",
            "drawings/sound-system.pdf",
            "Strings, reeds, tongues, tone fields, head, bore, or resonator as applicable.",
        ],
        [
            "3",
            "Hardware",
            "Hardware and fasteners",
            "1 set",
            "TBD",
            "TBD",
            "Buy",
            "TBD",
            "",
            "",
            "drawings/hardware-layout.pdf",
            "Bridge, tuning hardware, straps, pins, screws, jacks, or lacing as applicable.",
        ],
        [
            "4",
            "Fixtures",
            "Jigs, templates, and workholding",
            "1 set",
            "TBD",
            "MDF/acrylic/plywood or shop stock",
            "Make",
            "Shop",
            "",
            "",
            "drawings/fixtures.pdf",
            "Registration pins, laser templates, CNC spoilboard, bending forms, or lathe supports.",
        ],
        [
            "5",
            "Finish",
            "Finish and consumables",
            "1 set",
            "TBD",
            "Oil/wax/lacquer/adhesive/abrasives",
            "Buy",
            "TBD",
            "",
            "",
            "drawings/finish-notes.md",
            "Confirm finish is compatible with skin contact, food safety, reeds, strings, or glue.",
        ],
        [
            "6",
            "Validation",
            "Measurement and tuning supplies",
            "1 set",
            "Tuner, mic, calipers, hygrometer, test fixture",
            "TBD",
            "Buy/Use",
            "Shop/lab",
            "",
            "",
            "data/measurements.csv",
            "Record target frequency, measured frequency, cents error, humidity, and notes.",
        ],
    ]
    family_lower = family.lower()
    if "tongue" in instrument_lower:
        rows[1][10] = "drawings/tongue-layout.pdf"
        rows[1][11] = "Tongue/slot layout, kerf, bridge geometry, resonator, tuning trim, and strike zones."
    elif "handpan" in instrument_lower or "pan" == instrument_lower.strip():
        rows[1][10] = "drawings/tone-field-layout.pdf"
        rows[1][11] = "Tone fields, ding/gu, shell profile, material thickness, forming, and tuning process."
    elif any(name in instrument_lower for name in ("marimba", "xylophone", "glockenspiel")):
        rows[1][10] = "drawings/bar-schedule.pdf"
        rows[1][11] = "Bar lengths, widths, thickness/undercut, node positions, frame, and resonators."
    elif "woodwind" in family_lower:
        rows[1][10] = "drawings/bore-and-hole-layout.pdf"
        rows[1][11] = "Bore, tone holes, reed/edge/blowhole, tuning trim, and end corrections."
    elif "string" in family_lower:
        rows[1][10] = "drawings/string-schedule.pdf"
        rows[1][11] = "Scale length, string schedule, bridge/nut, tension, and percent breaking."
    elif "drum" in family_lower:
        rows[1][10] = "drawings/head-and-shell.pdf"
        rows[1][11] = "Head/skin, bearing edge, shell/stave/ring geometry, lacing or hardware."
    return rows


def write_bom(path: Path, record: dict[str, str]) -> None:
    headers = [
        "Item #",
        "Subsystem",
        "Part / Material",
        "Qty",
        "Dimensions / Spec",
        "Material",
        "Make / Buy",
        "Source / Supplier",
        "Estimated Unit Cost",
        "Extended Cost",
        "Drawing Ref",
        "Notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(infer_subsystem_rows(record))


def sourcing_rows(record: dict[str, str]) -> list[list[str]]:
    family = record.get("Family", "").lower()
    instrument = record.get("Instrument Type", "").lower()
    primary_material = record.get("Primary Material", "") or "TBD"
    rows = [
        [
            "1",
            "Primary material",
            "Main body/shell/blank stock",
            record.get("Variant/Size", "") or "TBD dimensions and oversize allowance",
            "TBD",
            "ea/bd ft/sheet",
            f"{record.get('Instrument Type', 'instrument')} {primary_material} stock lumber blank shell",
            "TBD",
            "",
            "",
            "",
            "Equivalent material with matching acoustic, structural, and machining requirements.",
            "Confirm dimensions, grade, moisture, defects, and shipping size.",
            "Needs sourcing",
        ],
        [
            "2",
            "Hardware",
            "Instrument-specific hardware set",
            "TBD from drawing and assembly method",
            "1",
            "set",
            f"{record.get('Instrument Type', 'instrument')} hardware parts kit",
            "TBD",
            "",
            "",
            "",
            "Compatible hardware with same critical dimensions.",
            "Do not buy until drawings identify hole spacing, thread, and clearances.",
            "Needs sourcing",
        ],
        [
            "3",
            "Consumables",
            "Adhesives, abrasives, finish, and shop supplies",
            "Skin/contact-safe finish where applicable",
            "1",
            "set",
            "instrument finish adhesive sandpaper wax oil lacquer",
            "TBD",
            "",
            "",
            "",
            "Equivalent finish compatible with material and player contact.",
            "Confirm finish does not inhibit tuning, glue, reeds, or skin contact.",
            "Needs sourcing",
        ],
        [
            "4",
            "Validation",
            "Measurement and tuning tools",
            "Tuner, microphone, calipers, hygrometer, scale",
            "1",
            "set",
            "instrument tuner measurement microphone calipers hygrometer",
            "Shop/lab",
            "",
            "",
            "",
            "Existing shop tools acceptable if calibrated enough for the task.",
            "Record tool/model in validation notes.",
            "Check inventory",
        ],
    ]

    def add(category: str, component: str, spec: str, search: str, notes: str) -> None:
        rows.append(
            [
                str(len(rows) + 1),
                category,
                component,
                spec,
                "TBD",
                "TBD",
                search,
                "TBD",
                "",
                "",
                "",
                "TBD after spec review",
                notes,
                "Needs sourcing",
            ]
        )

    if "tongue" in instrument:
        add("Sound plate", "Tongue plate or soundboard", "Material, thickness, kerf, tuning allowance", "steel tongue drum blank hardwood tongue drum soundboard", "Frequency depends strongly on thickness, slot geometry, and material batch.")
        add("Resonator", "Box, shell, or resonant body stock", "Envelope, wall thickness, port/cavity requirements", "tongue drum resonator box hardwood shell steel shell", "Confirm coupling and access before final glue/weld.")
        add("Shop service", "Laser/CNC cutting or routing", "Kerf, minimum slot width, tab/fixture method", "laser cut steel tongue drum CNC route tongue slots", "Cut quality affects tuning and crack initiation.")
        add("Accessories", "Feet, mallets, pads, or dampers", "Hardness, contact-safe material, size", "rubber feet mallets tongue drum pads dampers", "Small accessories affect sustain, rattle, and player experience.")
    elif any(word in instrument for word in ("handpan", "steel pan")):
        add("Metal", "Steel shell or sheet blank", "Alloy, thickness, diameter, forming condition", "handpan steel shell DC04 nitrided stainless blank", "Verify forming/tuning process before ordering volume.")
        add("Metal service", "Nitriding, heat treatment, or cutting service", "Service spec, part size, finish", "handpan nitriding service laser cut steel tongue drum blank", "Service capability and minimums change often.")
        add("Accessories", "Edge trim, feet, stand, or case", "Diameter, contact material, transport needs", "handpan edge trim stand case rubber feet", "Protect finish and tuning during handling.")
    elif any(name in instrument for name in ("marimba", "xylophone", "glockenspiel", "tubular bell")):
        add("Bars/tubes", "Tone bars or tubes", "Material, thickness/wall, length range, tuning allowance", "marimba bar stock xylophone bar aluminum brass tube", "Buy extra length for tuning and mounting holes.")
        add("Frame", "Frame rails and suspension hardware", "Rail size, cord, posts, isolation material", "marimba frame cord posts rubber tubing", "Suspension position controls sustain.")
        add("Resonators", "Resonator tubes or chamber stock", "Diameter, length, cap/plug method", "marimba resonator tubes aluminum PVC", "Length must include tuning and mounting allowance.")
    elif any(word in family for word in ("drum", "percussion")) or any(
        word in instrument for word in ("drum", "ashiko", "conga", "bongo", "djembe", "dunun", "dundun")
    ):
        add("Drum head", "Goatskin or drum head", "Diameter, thickness, hair on/off, flesh hoop method", "goatskin drum head rawhide hand drum skin", "Check diameter margin and ethical/import constraints.")
        add("Rope/lacing", "Drum rope or cord", "Diameter, stretch, color, tensile strength", "polyester drum rope djembe rope 3/16 1/4", "Low-stretch cord matters for tuning stability.")
        add("Rings/hoops", "Metal rings or hoops", "Diameter, rod size, weld quality, finish", "steel drum rings flesh hoop tension hoop", "Confirm ring diameter against head and shell geometry.")
        add("Hardware", "Lugs, tension rods, side plates, rim hardware", "Thread, spacing, finish, shell radius", "conga drum hardware lugs tension rods rim hoop", "Hardware hole pattern must match drawings.")
        add("Lumber", "Stave or segmented-shell lumber", "Species, board feet, thickness, grain, moisture", "hardwood lumber staves drum shell maple cherry walnut", "Buy extra for grain matching, defects, and setup cuts.")

    if any(word in family for word in ("string",)) or any(
        word in instrument for word in ("harp", "kora", "ngoni", "guitar", "violin", "ukulele", "lute", "oud", "bass")
    ):
        add("Strings", "Strings or monofilament", "Gauge/material/tension schedule", "harp strings nylon monofilament wound bass strings fluorocarbon", "Match scale length, target tension, and percent breaking.")
        add("Tuning hardware", "Tuning pins or machines", "Torque, shaft size, layout, finish", "zither pins harp tuning pins guitar tuning machines", "Pilot holes and access must match drawing.")
        add("Bridge/nut", "Bridge, nut, saddle, or notched bridge material", "Hardness, dimensions, string spacing", "instrument bridge saddle nut bone hardwood delrin", "Contact geometry affects tone and tuning.")

    if "woodwind" in family or any(word in instrument for word in ("flute", "duduk", "bagpipe", "fujara", "xiao", "didgeridoo", "ocarina")):
        add("Woodwind stock", "Bore blank or tube stock", "Bore/OD/length, grain, moisture", "flute blank cedar hardwood bore stock bamboo cane", "Oversize for tuning and workholding.")
        add("Seals/cork", "Cork, thread, wax, leather, or gasket material", "Thickness, density, contact-safe finish", "instrument cork waxed thread leather gasket flute", "Small seal materials often decide playability.")
        add("Reeds", "Reed cane or reed assemblies", "Instrument family, pitch, strength", "duduk reed bagpipe reed cane drone reed", "Reed sourcing is player- and climate-sensitive.")

    return rows


def write_sourcing(path: Path, record: dict[str, str]) -> None:
    headers = [
        "Item #",
        "Category",
        "Component",
        "Required Spec",
        "Qty Estimate",
        "Unit",
        "Search Terms",
        "Supplier Candidate",
        "Current Unit Price",
        "Date Checked",
        "Lead Time",
        "Acceptable Substitutes",
        "Risk / Notes",
        "Status",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(sourcing_rows(record))


def write_cut_list(path: Path, record: dict[str, str]) -> None:
    headers = [
        "Part #",
        "Part Name",
        "Qty",
        "Finished Dimensions",
        "Rough Stock Dimensions",
        "Material",
        "Grain / Orientation",
        "Source Formula / Drawing",
        "Operation",
        "Yield / Board Ft / Sheet Use",
        "Offcut Notes",
        "Status",
    ]
    rows = [
        [
            "1",
            "Primary blank or shell stock",
            "1",
            record.get("Variant/Size", "") or "TBD",
            "TBD plus workholding/tuning allowance",
            record.get("Primary Material", "") or "TBD",
            "TBD",
            "Design sheet and drawing-brief.md",
            "Cut to rough size, flatten/square, mark datum",
            "TBD",
            "Reserve offcuts for test cuts and tuning coupons.",
            "Needs dimensions",
        ],
        [
            "2",
            "Fixture or template stock",
            "1 set",
            "TBD",
            "TBD",
            "MDF, acrylic, plywood, or shop stock",
            "N/A",
            "drawing-brief.md and CAD/CNC setup",
            "Laser/CNC/drill fixture components",
            "TBD",
            "Use offcuts when registration accuracy is not compromised.",
            "Needs fixture design",
        ],
        [
            "3",
            "Test coupons",
            "TBD",
            "Representative tuning/material samples",
            "TBD",
            record.get("Primary Material", "") or "Same as primary material",
            "Match production orientation",
            "validation.csv",
            "Cut before final part when tuning or finish risk exists",
            "TBD",
            "Keep labeled with material batch and orientation.",
            "Recommended",
        ],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def write_validation(path: Path, record: dict[str, str]) -> None:
    headers = [
        "Check #",
        "Feature / Test",
        "Target",
        "Unit",
        "Tolerance",
        "Source",
        "Measured 1",
        "Measured 2",
        "Measured 3",
        "Environment",
        "Result",
        "Action / Notes",
    ]
    instrument = record.get("Instrument Type", "instrument")
    rows = [
        ["1", "A4 frequency reference", "440", "Hz", "Exact formula sanity check", "acoustic-models.md", "", "", "", "TBD", "", ""],
        ["2", "Overall envelope", record.get("Variant/Size", "") or "TBD", "in", "TBD", "drawing-brief.md", "", "", "", "TBD", "", ""],
        ["3", f"{instrument} tuning targets", record.get("Key/Scale", "") or "TBD", "Hz/cents", "TBD", "design sheet", "", "", "", "Temp/humidity TBD", "", ""],
        ["4", "Critical fit hardware", "All purchased/made parts fit", "pass/fail", "No forced fit", "bom.csv and drawings", "", "", "", "Shop", "", ""],
        ["5", "Finish and contact safety", "Compatible with use", "pass/fail", "No tack/odor/skin issue", "sourcing.csv", "", "", "", "Shop", "", ""],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def write_assembly_manual(path: Path, record: dict[str, str], date: str) -> None:
    content = f"""# Assembly Manual

Instrument ID: {record.get("Instrument ID", "UNKNOWN")}
Instrument: {record.get("Instrument Type", "Instrument")}
Revision/date: REV-A / {date}

## Before You Start

- Confirm `design.md`, `bom.csv`, `sourcing.csv`, `cut-list.csv`, `drawing-brief.md`, and `validation.csv` agree.
- Confirm all purchased hardware dimensions against drawings before cutting irreversible features.
- Photograph each major setup and save images in `images/`.

## Tools And Fixtures

- CNC / laser / lathe / hand tools:
- Measuring tools:
- Workholding and fixtures:
- Safety equipment:

## Build Phases

1. Source and inspect materials.
2. Prepare rough stock and test coupons.
3. Build fixtures/templates and verify datums.
4. Machine or form primary parts.
5. Dry fit hardware and sound-producing elements.
6. Assemble with reversible checks where possible.
7. Tune, trim, tension, or adjust.
8. Finish, cure, and re-check tuning/fit.
9. Document final measurements and build notes.

## Photo / Diagram Placeholders

- `images/01-materials.jpg`
- `images/02-fixture-setup.jpg`
- `images/03-machining.jpg`
- `images/04-dry-fit.jpg`
- `images/05-assembly.jpg`
- `images/06-validation.jpg`

## Maintenance / Setup Notes

- Tuning/setup:
- Seasonal humidity/temperature notes:
- Replaceable wear parts:
- Storage and transport:
"""
    path.write_text(content, encoding="utf-8")


def write_supplier_rfq(path: Path, record: dict[str, str]) -> None:
    content = f"""# Supplier RFQ Draft

Subject: RFQ for {record.get("Instrument Type", "instrument")} prototype components - {record.get("Instrument ID", "UNKNOWN")}

Hello,

I am sourcing components for a musical-instrument prototype:

- Instrument: {record.get("Instrument Type", "Instrument")}
- Variant/size: {record.get("Variant/Size", "TBD") or "TBD"}
- Key/scale: {record.get("Key/Scale", "TBD") or "TBD"}
- Primary material: {record.get("Primary Material", "TBD") or "TBD"}

Could you quote the items listed in `sourcing.csv` or recommend compatible alternatives?

Please include:

- Unit price and any volume breaks
- Minimum order quantity
- Current stock status
- Lead time
- Shipping estimate to my location
- Material/spec sheet or drawing if available
- Notes on acceptable substitutions or constraints

Thank you,

Tony
"""
    path.write_text(content, encoding="utf-8")


def write_visual_bom_brief(path: Path, record: dict[str, str], date: str) -> None:
    content = f"""# Visual BOM Brief

Instrument ID: {record.get("Instrument ID", "UNKNOWN")}
Instrument: {record.get("Instrument Type", "Instrument")}
Revision/date: REV-A / {date}

## Reference Style

Use Tony's Ashiko visual BOM as the preferred pattern:

```text
C:/Users/Tony/Documents/GitHub/ashiko-drum-workshop/images/figure-bom-v2.png
/mnt/c/Users/Tony/Documents/GitHub/ashiko-drum-workshop/images/figure-bom-v2.png
```

## Layout

- Header: assembly name, quote date, estimated cost, revision.
- Hero image: finished assembly or best current render/photo.
- Main table columns: Part #, Part Name, Description, Qty, Units, Picture, Cost Each, Total.
- Alternating row fills for readability.
- Bottom notes: supplier assumptions, material species, discounts, substitutions, and TBDs.

## Image Rules

- Prefer real part photos, supplier images, CAD renders, or shop photos.
- Generated part images are allowed as placeholders, but label them as concept/placeholder.
- Keep image thumbnails consistent in crop and scale where possible.
- Do not infer dimensions from generated images.

## Needed Images

- Finished assembly / hero:
- Primary material:
- Sound-producing elements:
- Hardware:
- Rope/lacing/strings/reeds/skin/head:
- Finish/consumables:
- Fixtures/templates:

## Output Targets

- `images/visual-bom.png`
- `images/visual-bom.pdf`
- Source workbook/sheet or editable design file:
"""
    path.write_text(content, encoding="utf-8")


def write_design_md(
    path: Path,
    record: dict[str, str],
    design_summary: dict[str, object],
    date: str,
    packet_dir: Path,
) -> None:
    instrument_id = record.get("Instrument ID", "UNKNOWN")
    instrument_type = record.get("Instrument Type", "Instrument")
    title = f"{instrument_id} - {instrument_type}"
    content = f"""# {title}

Generated: {date}

## Intent

Create a traceable build packet for `{instrument_id}` that connects the master catalog row, design sheet, BOM, sourcing, stock prep, validation, assembly, drawing brief, visual BOM brief, Wolfram starter, and CAD/CNC placeholder paths.

## Master Catalog Row

{catalog_markdown(record)}

## Design Sheet Summary

{design_summary_markdown(design_summary)}
## Engineering Assumptions To Resolve

- Confirm which dimensions come from formulas, measured builds, supplier drawings, or concept estimates.
- Confirm units, tuning standard, material batch, workholding strategy, and machine envelope.
- Add empirical correction factors or validation measurements before final machining.
- Mark any generated product sketches as communication artifacts unless dimensions are also backed by this packet.

## Build Package Inventory

- `design.md`: design intent, catalog metadata, assumptions, and validation plan.
- `bom.csv`: starter bill of materials with drawing references.
- `sourcing.csv`: supplier/search-term tracker with price/date/lead-time fields.
- `cut-list.csv`: stock, rough/final dimensions, yield, and offcut planning.
- `validation.csv`: target/measured values, environment, result, and action log.
- `assembly-manual.md`: phased build manual with photo placeholders.
- `supplier-rfq.md`: supplier request-for-quote draft.
- `visual-bom-brief.md`: image-forward BOM brief based on Tony's Ashiko BOM style.
- `drawing-brief.md`: manufacturing drawing and technical product sketch brief.
- `wolfram-starter.wl`: Wolfram Language starter for physics, optimization, and visualization.
- `cad/`: placeholder for CAD models and design tables.
- `cnc/`: placeholder for operation plans, setup sheets, CAM, and toolpaths.
- `drawings/`: placeholder for PDFs, SVGs, DXFs, and drawing exports.
- `images/`: placeholder for product sketches, BOM plates, ergonomic views, and renderings.
- `data/`: placeholder for measurements, tuning validation, and DoE logs.
- `wolfram/`: placeholder for generated Wolfram model packages.

## Placeholder Paths

```text
{packet_dir}/cad/
{packet_dir}/cnc/
{packet_dir}/drawings/
{packet_dir}/images/
{packet_dir}/data/
{packet_dir}/wolfram/
```

## Validation Plan

- Physics sanity check:
- Critical dimensions checked against design sheet:
- CNC/laser/lathe work envelope check:
- Material and structural check:
- Ergonomic/player check:
- Tuning measurement plan:
- Build photos and revision notes:
"""
    path.write_text(content, encoding="utf-8")


def write_drawing_brief(path: Path, record: dict[str, str], design_summary: dict[str, object], date: str) -> None:
    instrument_id = record.get("Instrument ID", "UNKNOWN")
    instrument_type = record.get("Instrument Type", "Instrument")
    content = f"""# Instrument Drawing Brief

Instrument: {instrument_type}
Instrument ID: {instrument_id}
Variant/size: {record.get("Variant/Size", "TBD") or "TBD"}
Key/scale: {record.get("Key/Scale", "TBD") or "TBD"}
Revision/date: REV-A / {date}
Units: inches unless noted
Scale: TBD
Source workbook/CAD/catalog ID: {record.get("Source Workbook", "TBD") or "TBD"} / {record.get("CAD Design ID", "TBD") or "TBD"}

## Required Views

- Plan:
- Side/front:
- Section:
- Detail:
- Exploded/BOM:
- Ergonomic/player:

## Technical Product Sketch

Use a technical-leaning concept sketch when the design needs a fast shared picture of scale, resources, size, character, material choices, and interaction. It may combine a hero 3D view, small orthographic insets, material swatches, callout labels, a simple scale figure/hand reference, and resource/BOM badges.

Rules:

- Use only known dimensions from the design sheet or mark values as `TBD`.
- Include scale cues, but do not infer final geometry from the sketch.
- Show material intent clearly: wood species, metal, skin/head, strings, ceramic, finish, or hardware.
- Prefer clean information-board layouts for communication: engineering poster, magazine-style explainer, reference sheet, or storyboard/process board.
- Keep build-critical geometry in vector/CAD drawings.

## Critical Dimensions

| Feature | Dimension | Tolerance | Source | Notes |
| --- | ---: | --- | --- | --- |
| Overall envelope | TBD | TBD | Design sheet/CAD |  |
| Primary datum/centerline | TBD | TBD | CAD |  |
| Tuning-critical geometry | TBD | TBD | Formula/measurement |  |
| Workholding datum | TBD | TBD | CNC setup |  |

## Materials And Finish

| Part | Material/spec | Grain/orientation | Finish | Notes |
| --- | --- | --- | --- | --- |
| Primary structure | {record.get("Primary Material", "TBD") or "TBD"} | TBD | TBD |  |
| Sound-producing element | TBD | TBD | TBD |  |
| Hardware/fixtures | TBD | N/A | TBD |  |

## Manufacturing Notes

- Stock:
- Workholding:
- Tooling:
- Operation sequence:
- Kerf/bit-radius compensation:
- Trim/tuning allowance:

## Design Sheet Context

{design_summary_markdown(design_summary)}
## Assumptions / TBDs

-
"""
    path.write_text(content, encoding="utf-8")


def wl_string(value: str) -> str:
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def write_wolfram(path: Path, record: dict[str, str], design_summary: dict[str, object]) -> None:
    pairs = {
        "InstrumentID": record.get("Instrument ID", "UNKNOWN"),
        "Family": record.get("Family", ""),
        "InstrumentType": record.get("Instrument Type", ""),
        "VariantSize": record.get("Variant/Size", ""),
        "KeyScale": record.get("Key/Scale", ""),
        "PrimaryMaterial": record.get("Primary Material", ""),
        "DesignSheet": str(design_summary.get("sheet", "")),
        "DesignWorkbook": str(design_summary.get("workbook", "")),
    }
    association = ",\n  ".join(f"{wl_string(key)} -> {wl_string(value)}" for key, value in pairs.items())
    content = f"""(* Instrument-maker build-packet Wolfram starter. *)

ClearAll["Global`*"];

design = <|
  {association},
  "Units" -> "Imperial",
  "A4" -> 440,
  "SpeedOfSoundInPerSec" -> 13552
|>;

frequencyFromMidi[midi_, a4_: 440] := a4*2^((midi - 69)/12);
centsError[measured_, target_] := 1200*Log2[measured/target];
openPipeLengthIn[freq_, c_: 13552, radius_: 0] := c/(2*freq) - 2*0.6*radius;
stoppedPipeLengthIn[freq_, c_: 13552, radius_: 0] := c/(4*freq) - 0.6*radius;
cantileverLengthIn[freq_, thickness_, k_] := Sqrt[k*thickness/freq];

CreateDocument[
  {{
    TextCell[design["InstrumentID"] <> " - " <> design["InstrumentType"], "Title"],
    TextCell["Build-packet computational design notebook", "Subtitle"],
    ExpressionCell[design, "Input"],
    TextCell["Add imported design rows, Manipulate controls, plots, audio, 3D geometry, and validation cells below.", "Text"]
  }},
  WindowTitle -> design["InstrumentID"]
]
"""
    path.write_text(content, encoding="utf-8")


def create_packet(args: argparse.Namespace) -> Path:
    master_workbook = args.master_workbook
    record = find_catalog_row(master_workbook, args.instrument_id, args.master_row)
    instrument_id = record.get("Instrument ID", "UNKNOWN")
    instrument_type = record.get("Instrument Type", "Instrument")
    design_sheet = args.design_sheet or record.get("Source Sheet") or record.get("Legacy Link/Design Sheet")
    design_workbook = resolve_design_workbook(args.design_workbook)
    design_summary = summarize_design_sheet(design_workbook, design_sheet)

    date = args.date or dt.date.today().isoformat()
    default_slug = slugify(f"{date}-{instrument_id}-{instrument_type}")
    packet_dir = args.output_root / (args.slug or default_slug)
    if packet_dir.exists() and not args.force:
        raise SystemExit(f"Output folder already exists. Use --force to overwrite files: {packet_dir}")
    packet_dir.mkdir(parents=True, exist_ok=True)
    for dirname in ("cad", "cnc", "drawings", "images", "data", "wolfram"):
        directory = packet_dir / dirname
        directory.mkdir(exist_ok=True)
        (directory / ".gitkeep").write_text("", encoding="utf-8")

    write_design_md(packet_dir / "design.md", record, design_summary, date, packet_dir)
    write_bom(packet_dir / "bom.csv", record)
    write_sourcing(packet_dir / "sourcing.csv", record)
    write_cut_list(packet_dir / "cut-list.csv", record)
    write_validation(packet_dir / "validation.csv", record)
    write_assembly_manual(packet_dir / "assembly-manual.md", record, date)
    write_supplier_rfq(packet_dir / "supplier-rfq.md", record)
    write_visual_bom_brief(packet_dir / "visual-bom-brief.md", record, date)
    write_drawing_brief(packet_dir / "drawing-brief.md", record, design_summary, date)
    write_wolfram(packet_dir / "wolfram-starter.wl", record, design_summary)
    # v4 additions
    write_risks_skeleton(packet_dir / "risks.md", record)
    write_photo_shotlist(packet_dir / "photo-shotlist.md", record)
    write_readme_stub(packet_dir / "README.md", record, date)
    return packet_dir


# --- v4 additions ---------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--master-workbook",
        type=Path,
        default=DEFAULT_MASTER,
        help="Instrument Workshop Master workbook path",
    )
    parser.add_argument("--instrument-id", help="Master Catalog Instrument ID to package")
    parser.add_argument("--master-row", type=int, help="Excel row number in Master Catalog")
    parser.add_argument("--design-workbook", type=Path, help="Workbook containing the design sheet")
    parser.add_argument("--design-sheet", help="Design sheet name to summarize")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("build-packets"),
        help="Folder where build packet folders are created",
    )
    parser.add_argument("--slug", help="Override generated output folder name")
    parser.add_argument("--date", help="Override generated date, YYYY-MM-DD")
    parser.add_argument("--force", action="store_true", help="Allow overwriting generated files")
    parser.add_argument("--dry-run", action="store_true",
                        help="v4 Tier 4 #11: print the file list without writing anything")
    args = parser.parse_args()

    if not args.master_workbook.exists():
        raise SystemExit(f"Master workbook not found: {args.master_workbook}")
    if args.dry_run:
        # Resolve as much as we can without writing
        record = find_catalog_row(args.master_workbook, args.instrument_id, args.master_row)
        date = args.date or dt.date.today().isoformat()
        slug = args.slug or slugify(record.get("Instrument Type", "instrument"))
        packet_dir = args.output_root / f"{date}-{(args.instrument_id or 'M').lower()}-{slug}"
        print(f"--dry-run: would create packet at {packet_dir}")
        for f in ["design.md", "bom.csv", "sourcing.csv", "cut-list.csv",
                  "validation.csv", "assembly-manual.md", "supplier-rfq.md",
                  "visual-bom-brief.md", "drawing-brief.md",
                  "wolfram-starter.wl", "risks.md", "photo-shotlist.md",
                  "README.md"]:
            print(f"  -> {packet_dir / f}")
        return 0
    packet_dir = create_packet(args)
    print(packet_dir)
    return 0


def write_risks_skeleton(path, record):
    """v4 red-team scaffold."""
    instrument = record.get("Instrument Type", "Instrument")
    iid = record.get("Instrument ID", "TBD")
    body = (
        "# Risks - " + instrument + " (" + iid + ")\n\n"
        "Scaffolded by `generate_build_packet.py`. Replace each "
        "`(none identified)` line with real risks before shipping. "
        "Each risk follows the v4 red-team format: Symptom -> Mechanism "
        "-> Test -> Mitigation -> Severity (Low/Medium/High).\n\n"
        "## Acoustic\n\n(none identified - replace before shipping)\n\n"
        "## Structural\n\n(none identified - replace before shipping)\n\n"
        "## Ergonomic\n\n(none identified - replace before shipping)\n\n"
        "## Supply\n\n(none identified - replace before shipping)\n\n"
        "## Fit/Finish\n\n(none identified - replace before shipping)\n"
    )
    path.write_text(body, encoding="utf-8")


def write_photo_shotlist(path, record):
    """v4 Tier 4 #13: photo-shotlist.md scaffold. The build-log site
    picks up matching files in `images/` automatically."""
    instrument = record.get("Instrument Type", "Instrument")
    body = (
        "# Photo Shotlist - " + instrument + "\n\n"
        "Reference shotlist for capturing this build. Drop final images "
        "into `images/` with the suggested filenames; the build-log site "
        "generator picks them up automatically.\n\n"
        "Lighting: neutral background, diffused daylight or single softbox "
        "45 deg from camera. Include a ruler in BOM and process shots.\n\n"
        "## Required\n\n"
        "| Filename | Subject | Notes |\n"
        "|---|---|---|\n"
        "| `images/hero.jpg` | Finished " + instrument + ", 3/4 view | Single-instrument shot, neutral background, primary asset for the build-log site and capstone deck |\n"
        "| `images/exploded.jpg` | All parts laid out flat | One photo per family member if family-aware |\n"
        "| `images/bom-plate.jpg` | Parts arranged with labels and ruler | Reference for visual BOM |\n"
        "| `images/finished-detail.jpg` | Close-up of a feature unique to this instrument | Inlay, joinery, signature detail |\n\n"
        "## Process (one per major operation)\n\n"
        "| Filename | Subject | When to shoot |\n"
        "|---|---|---|\n"
        "| `images/process-1-stock-prep.jpg` | Blanks before machining | Stock prep |\n"
        "| `images/process-2-cnc-bore.jpg` | CNC machine cutting bore | CNC machining |\n"
        "| `images/process-3-glue-up.jpg` | Body in clamps | Glue-up |\n"
        "| `images/process-4-shaping.jpg` | Major shaping operation | Shaping |\n"
        "| `images/process-5-tone-holes.jpg` | Drilling or cutting tone features | Tone-hole/feature work |\n"
        "| `images/process-6-inlay.jpg` | Inlay or detail work | Inlay phase |\n"
        "| `images/process-7-finish.jpg` | First finish coat | Finish phase |\n"
        "| `images/process-8-tuning.jpg` | Chromatic tuner against the instrument | Tuning |\n\n"
        "## Optional\n\n"
        "| Filename | Subject | Use |\n"
        "|---|---|---|\n"
        "| `images/in-shop.jpg` | Workspace context | Capstone deck cover |\n"
        "| `images/maker-portrait.jpg` | Tony with the finished instrument | Recruiter-facing site |\n"
        "| `images/family-group.jpg` | All family members together | Family-overview page |\n\n"
        "## Camera notes\n\n"
        "- Wood instruments: warm color temperature (3500-4500 K)\n"
        "- Metal/ceramic: cooler temperature (5500-6500 K)\n"
        "- For inlay close-ups, use raking side-light\n"
        "- For multi-bore work, include at least one shot with the bore visible\n"
    )
    path.write_text(body, encoding="utf-8")


def write_readme_stub(path, record, date):
    """v4 documentarian scaffold."""
    instrument = record.get("Instrument Type", "Instrument")
    iid = record.get("Instrument ID", "TBD")
    family = record.get("Family", "TBD")
    body = (
        "# " + instrument + " (" + iid + ")\n\n"
        "> *Hero image placeholder - replace `images/hero.jpg`.*\n\n"
        "Build packet for " + instrument + " (" + iid + ", family: " + family + "). "
        "Generated " + date + " by `generate_build_packet.py` (instrument-maker-v4).\n\n"
        "## What's in this folder\n\n"
        "| File | Purpose |\n"
        "|---|---|\n"
        "| [`design.md`](design.md) | Project intent, governing acoustic model, hardware alignment |\n"
        "| [`bom.csv`](bom.csv) | Bill of materials |\n"
        "| [`sourcing.csv`](sourcing.csv) | Suppliers, search terms, lead times |\n"
        "| [`cut-list.csv`](cut-list.csv) | Stock cuts |\n"
        "| [`validation.csv`](validation.csv) | Predicted vs measured tuning |\n"
        "| [`assembly-manual.md`](assembly-manual.md) | Step-by-step build |\n"
        "| [`risks.md`](risks.md) | Failure-mode walk-through |\n"
        "| [`photo-shotlist.md`](photo-shotlist.md) | What to photograph |\n"
        "| `drawings/` | SVG drawings - run `generate_drawings.py` |\n"
        "| `cad/` | OpenSCAD master and SolidWorks files |\n"
        "| `cnc/` | CNC operation plan, setup sheets, CAM/toolpath handoffs |\n"
        "| `images/` | Finished and process photos |\n"
        "| `wolfram/` | Wolfram model package generated by `generate_wolfram_packet.py` |\n"
        "| `site/` | Build-log static site - run `generate_site.py` |\n\n"
        "## Next steps\n\n"
        "This README is a scaffold. The v4 documentarian specialist replaces "
        "it with a tongue-drum-style narrative once the build is underway. "
        "To regenerate, ask the skill: \"Rewrite the README for " + iid + " "
        "in tongue-drum style.\"\n"
    )
    path.write_text(body, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
