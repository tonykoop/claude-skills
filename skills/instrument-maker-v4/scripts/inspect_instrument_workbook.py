#!/usr/bin/env python3
"""Summarize .xlsx workbook structure using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def read_xml(zf: ZipFile, name: str) -> ET.Element:
    return ET.fromstring(zf.read(name))


def rels_for(zf: ZipFile, part: str) -> dict[str, dict[str, str]]:
    rel_name = posixpath.join(
        posixpath.dirname(part), "_rels", posixpath.basename(part) + ".rels"
    )
    rels: dict[str, dict[str, str]] = {}
    if rel_name not in zf.namelist():
        return rels
    root = read_xml(zf, rel_name)
    for rel in root:
        rels[rel.attrib.get("Id", "")] = {
            key.split("}")[-1]: value for key, value in rel.attrib.items()
        }
    return rels


def resolve_part(base_part: str, target: str | None) -> str | None:
    if not target:
        return None
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(base_part), target))


def shared_strings(zf: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = read_xml(zf, "xl/sharedStrings.xml")
    strings: list[str] = []
    for item in root.findall("main:si", NS):
        strings.append("".join(t.text or "" for t in item.findall(".//main:t", NS)))
    return strings


def workbook_sheets(zf: ZipFile) -> dict[str, str]:
    workbook = read_xml(zf, "xl/workbook.xml")
    workbook_rels = rels_for(zf, "xl/workbook.xml")
    sheets: dict[str, str] = {}
    rel_key = f"{{{NS['rel']}}}id"
    for sheet in workbook.findall("main:sheets/main:sheet", NS):
        rid = sheet.attrib.get(rel_key)
        target = workbook_rels.get(rid or "", {}).get("Target")
        part = resolve_part("xl/workbook.xml", target)
        if part:
            sheets[sheet.attrib["name"]] = part
    return sheets


def column_number(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref)
    if not match:
        return 0
    number = 0
    for char in match.group(1):
        number = number * 26 + ord(char) - 64
    return number


def cell_text(cell: ET.Element, strings: list[str]) -> str:
    formula = cell.find("main:f", NS)
    if formula is not None:
        return "=" + (formula.text or "")
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(t.text or "" for t in cell.findall(".//main:t", NS))
    value = cell.find("main:v", NS)
    if value is None:
        return ""
    raw = value.text or ""
    if cell_type == "s":
        try:
            return strings[int(raw)]
        except (ValueError, IndexError):
            return raw
    if cell_type == "b":
        return "TRUE" if raw == "1" else "FALSE"
    return raw


def style_maps(zf: ZipFile) -> tuple[list[ET.Element], list[ET.Element], list[ET.Element]]:
    if "xl/styles.xml" not in zf.namelist():
        return [], [], []
    root = read_xml(zf, "xl/styles.xml")
    fonts_element = root.find("main:fonts", NS)
    fills_element = root.find("main:fills", NS)
    cell_xfs_element = root.find("main:cellXfs", NS)
    fonts = list(fonts_element) if fonts_element is not None else []
    fills = list(fills_element) if fills_element is not None else []
    cell_xfs = list(cell_xfs_element) if cell_xfs_element is not None else []
    return fonts, fills, cell_xfs


def is_blueish_input(
    cell: ET.Element,
    fonts: list[ET.Element],
    fills: list[ET.Element],
    cell_xfs: list[ET.Element],
) -> bool:
    style_id = cell.attrib.get("s")
    if not style_id or not style_id.isdigit():
        return False
    index = int(style_id)
    if index >= len(cell_xfs):
        return False
    xf = cell_xfs[index]
    font_id = int(xf.attrib.get("fontId", "0"))
    fill_id = int(xf.attrib.get("fillId", "0"))

    if font_id < len(fonts):
        color = fonts[font_id].find("main:color", NS)
        rgb = (color.attrib.get("rgb", "") if color is not None else "").upper()
        if rgb.endswith("0000FF") or rgb.endswith("0563C1"):
            return True

    if fill_id < len(fills):
        foreground = fills[fill_id].find(".//main:fgColor", NS)
        rgb = (
            foreground.attrib.get("rgb", "") if foreground is not None else ""
        ).upper()
        if rgb.endswith(("D6E4F0", "D9EAF7", "CFE2F3")):
            return True

    return False


def table_info(zf: ZipFile, sheet_part: str) -> list[dict[str, object]]:
    root = read_xml(zf, sheet_part)
    sheet_rels = rels_for(zf, sheet_part)
    table_parts = root.find("main:tableParts", NS)
    tables: list[dict[str, object]] = []
    if table_parts is None:
        return tables
    rel_key = f"{{{NS['rel']}}}id"
    for table_part in table_parts.findall("main:tablePart", NS):
        rid = table_part.attrib.get(rel_key, "")
        target = sheet_rels.get(rid, {}).get("Target")
        part = resolve_part(sheet_part, target)
        if not part or part not in zf.namelist():
            continue
        table = read_xml(zf, part)
        headers = [
            col.attrib.get("name", "")
            for col in table.findall("main:tableColumns/main:tableColumn", NS)
        ]
        tables.append(
            {
                "name": table.attrib.get("name"),
                "display_name": table.attrib.get("displayName"),
                "ref": table.attrib.get("ref"),
                "headers": headers,
            }
        )
    return tables


def sample_rows(
    root: ET.Element, strings: list[str], row_limit: int, column_limit: int
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in root.findall("main:sheetData/main:row", NS):
        values = [""] * column_limit
        has_value = False
        for cell in row.findall("main:c", NS):
            col_num = column_number(cell.attrib.get("r", ""))
            if 1 <= col_num <= column_limit:
                text = cell_text(cell, strings)
                values[col_num - 1] = text
                has_value = has_value or bool(text)
        if has_value:
            rows.append({"row": row.attrib.get("r"), "values": values})
        if len(rows) >= row_limit:
            break
    return rows


def sheet_summary(
    zf: ZipFile,
    sheet_name: str,
    sheet_part: str,
    strings: list[str],
    fonts: list[ET.Element],
    fills: list[ET.Element],
    cell_xfs: list[ET.Element],
    args: argparse.Namespace,
) -> dict[str, object]:
    root = read_xml(zf, sheet_part)
    dimension = root.find("main:dimension", NS)
    cells = root.findall(".//main:c", NS)
    rows = root.findall("main:sheetData/main:row", NS)
    formulas = root.findall(".//main:f", NS)
    merge_cells = root.find("main:mergeCells", NS)
    pane = root.find("main:sheetViews/main:sheetView/main:pane", NS)

    drawing_count = 0
    image_count = 0
    sheet_rels = rels_for(zf, sheet_part)
    rel_key = f"{{{NS['rel']}}}id"
    for drawing in root.findall("main:drawing", NS):
        drawing_count += 1
        rid = drawing.attrib.get(rel_key, "")
        target = sheet_rels.get(rid, {}).get("Target")
        drawing_part = resolve_part(sheet_part, target)
        if drawing_part and drawing_part in zf.namelist():
            drawing_rels = rels_for(zf, drawing_part)
            image_count += sum(
                1 for rel in drawing_rels.values() if "image" in rel.get("Type", "")
            )

    summary: dict[str, object] = {
        "name": sheet_name,
        "dimension": dimension.attrib.get("ref") if dimension is not None else "",
        "rows": len(rows),
        "cells": len(cells),
        "formulas": len(formulas),
        "blueish_inputs": sum(
            1 for cell in cells if is_blueish_input(cell, fonts, fills, cell_xfs)
        ),
        "merges": int(merge_cells.attrib.get("count", "0")) if merge_cells is not None else 0,
        "drawings": drawing_count,
        "images": image_count,
        "freeze": pane.attrib if pane is not None else {},
    }
    if args.tables:
        summary["tables"] = table_info(zf, sheet_part)
    if args.formulas:
        summary["formula_examples"] = [
            {"cell": cell.attrib.get("r"), "formula": formula.text or ""}
            for cell in root.findall(".//main:c", NS)
            for formula in [cell.find("main:f", NS)]
            if formula is not None
        ][: args.formulas]
    if args.samples:
        summary["sample_rows"] = sample_rows(root, strings, args.samples, args.columns)
    return summary


def truncate(text: object, width: int) -> str:
    value = str(text).replace("\n", " / ")
    if width <= 0 or len(value) <= width:
        return value
    return value[: max(0, width - 3)].rstrip() + "..."


def print_human(summaries: list[dict[str, object]], width: int) -> None:
    for summary in summaries:
        print(
            f"- {summary['name']!r}: {summary['dimension']}, "
            f"rows={summary['rows']}, cells={summary['cells']}, "
            f"formulas={summary['formulas']}, blueish={summary['blueish_inputs']}, "
            f"merges={summary['merges']}, images={summary['images']}"
        )
        if summary.get("tables"):
            for table in summary["tables"]:  # type: ignore[index]
                headers = ", ".join(table["headers"])  # type: ignore[index]
                print(f"  table {table['display_name']} {table['ref']}: {headers}")
        if summary.get("formula_examples"):
            for item in summary["formula_examples"]:  # type: ignore[index]
                print(f"  formula {item['cell']}: {item['formula']}")
        if summary.get("sample_rows"):
            for row in summary["sample_rows"]:  # type: ignore[index]
                values = [truncate(value, width) for value in row["values"]]
                print(f"  row {row['row']}: " + " | ".join(values))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path, help=".xlsx workbook path")
    parser.add_argument("--sheet", action="append", help="Only inspect named sheet")
    parser.add_argument("--tables", action="store_true", help="Include Excel table headers")
    parser.add_argument(
        "--formulas",
        type=int,
        default=0,
        metavar="N",
        help="Include up to N formula examples per sheet",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=0,
        metavar="N",
        help="Include up to N non-empty sample rows per sheet",
    )
    parser.add_argument(
        "--columns",
        type=int,
        default=12,
        help="Maximum sample columns to print",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=120,
        help="Maximum width for each sampled cell in human output",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    with ZipFile(args.workbook) as zf:
        strings = shared_strings(zf)
        fonts, fills, cell_xfs = style_maps(zf)
        sheets = workbook_sheets(zf)
        selected = args.sheet or list(sheets)
        summaries = []
        for sheet_name in selected:
            if sheet_name not in sheets:
                raise SystemExit(f"Sheet not found: {sheet_name}")
            summaries.append(
                sheet_summary(
                    zf,
                    sheet_name,
                    sheets[sheet_name],
                    strings,
                    fonts,
                    fills,
                    cell_xfs,
                    args,
                )
            )

    if args.json:
        print(json.dumps({"workbook": str(args.workbook), "sheets": summaries}, indent=2))
    else:
        print(f"workbook: {args.workbook}")
        print(f"sheet_count: {len(summaries)}")
        print_human(summaries, args.width)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
