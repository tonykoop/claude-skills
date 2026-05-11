#!/usr/bin/env python3
"""Validate visual-output authority records for instrument-maker-v4 packets.

This focused validator makes the DXF/CAD authority rule machine-checkable:
image-gen-2 prompts and outputs may support concept/story/visual BOM work,
but they must never be recorded as fabrication authority.

Exit codes:
  0   - all rows pass; warnings are still printed to stdout
  1   - at least one row failed a hard check
  2   - bad invocation (missing file, malformed CSV/JSON)

Usage:
  python3 validate_visual_authority.py path/to/visual-output-register.csv
  python3 validate_visual_authority.py path/to/visual-output-register.json
  python3 validate_visual_authority.py path/to/register.csv --strict
  python3 validate_visual_authority.py path/to/register.csv --json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


REQUIRED_COLUMNS = {
    "artifact_id",
    "path",
    "artifact_kind",
    "role",
    "authority",
    "dimension_claim",
}

ARTIFACT_KIND_VOCAB = {
    "dxf",
    "cad",
    "drawing_pdf",
    "svg_preview",
    "render_preview",
    "design_table",
    "measurement_template",
    "image_gen_2_prompt",
    "image_gen_2_output",
    "photo_reference",
}

FABRICATION_AUTHORITY_KINDS = {
    "dxf",
    "cad",
    "drawing_pdf",
    "design_table",
    "measurement_template",
}

FABRICATION_ROLES = {
    "fabrication_geometry",
    "cut_layout",
    "cnc_reference",
    "laser_reference",
    "dimensioned_drawing",
    "design_table",
    "measurement_template",
}

NON_AUTHORITY_IMAGE_ROLES = {
    "concept",
    "story",
    "visual_bom",
    "ergonomics",
    "finish_study",
    "build_log",
    "photo_reference",
}

ROLE_VOCAB = FABRICATION_ROLES | NON_AUTHORITY_IMAGE_ROLES | {
    "derived_preview",
}

AUTHORITY_VOCAB = {
    "fabrication",
    "derived_preview",
    "concept_only",
    "reference_only",
}

DIMENSION_CLAIM_VOCAB = {
    "none",
    "derived_from_authority",
    "image_inferred",
}

IMAGE_GEN_KINDS = {
    "image_gen_2_prompt",
    "image_gen_2_output",
}


@dataclass
class Finding:
    severity: str
    row_index: int
    artifact_id: str
    code: str
    message: str

    def human(self) -> str:
        loc = f"row {self.row_index}" + (
            f" ({self.artifact_id})" if self.artifact_id else "")
        return f"[{self.severity}] {self.code}  {loc}: {self.message}"


@dataclass
class Report:
    file: str
    rows_total: int = 0
    rows_checked: int = 0
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "ERROR"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "WARN"]


def _norm(value: object) -> str:
    return str(value or "").strip()


def _boolish(value: object) -> bool:
    return _norm(value).lower() in {"1", "true", "yes", "y"}


def validate_rows(rows: list[dict], file_label: str = "") -> Report:
    rep = Report(file=file_label, rows_total=len(rows))

    if not rows:
        rep.findings.append(Finding(
            severity="ERROR",
            row_index=0,
            artifact_id="",
            code="EMPTY_REGISTER",
            message="Visual output register has no rows.",
        ))
        return rep

    present_columns = set().union(*(row.keys() for row in rows))
    missing = sorted(REQUIRED_COLUMNS - present_columns)
    for col in missing:
        rep.findings.append(Finding(
            severity="ERROR",
            row_index=0,
            artifact_id="",
            code=f"MISSING_COLUMN_{col}",
            message=f"visual-output register has no {col!r} column.",
        ))
    if rep.errors:
        return rep

    has_fabrication_authority = False

    for i, row in enumerate(rows, start=1):
        rep.rows_checked += 1
        aid = _norm(row.get("artifact_id"))
        path = _norm(row.get("path"))
        kind = _norm(row.get("artifact_kind"))
        role = _norm(row.get("role"))
        authority = _norm(row.get("authority"))
        derived_from = _norm(row.get("derived_from"))
        dimension_claim = _norm(row.get("dimension_claim"))
        fabrication_required = _boolish(row.get("fabrication_required"))

        if not aid:
            rep.findings.append(Finding(
                severity="ERROR", row_index=i, artifact_id=aid,
                code="EMPTY_artifact_id",
                message="artifact_id is required for every row.",
            ))
        if not path:
            rep.findings.append(Finding(
                severity="ERROR", row_index=i, artifact_id=aid,
                code="EMPTY_path",
                message="path is required for every row.",
            ))

        if kind not in ARTIFACT_KIND_VOCAB:
            rep.findings.append(Finding(
                severity="ERROR", row_index=i, artifact_id=aid,
                code="INVALID_artifact_kind",
                message=(f"artifact_kind={kind!r} is not in the controlled "
                         f"vocabulary: {sorted(ARTIFACT_KIND_VOCAB)}"),
            ))

        if role not in ROLE_VOCAB:
            rep.findings.append(Finding(
                severity="ERROR", row_index=i, artifact_id=aid,
                code="INVALID_role",
                message=(f"role={role!r} is not in the controlled "
                         f"vocabulary: {sorted(ROLE_VOCAB)}"),
            ))

        if authority not in AUTHORITY_VOCAB:
            rep.findings.append(Finding(
                severity="ERROR", row_index=i, artifact_id=aid,
                code="INVALID_authority",
                message=(f"authority={authority!r} is not in the controlled "
                         f"vocabulary: {sorted(AUTHORITY_VOCAB)}"),
            ))

        if dimension_claim not in DIMENSION_CLAIM_VOCAB:
            rep.findings.append(Finding(
                severity="ERROR", row_index=i, artifact_id=aid,
                code="INVALID_dimension_claim",
                message=(f"dimension_claim={dimension_claim!r} is not in "
                         f"{sorted(DIMENSION_CLAIM_VOCAB)}"),
            ))

        if authority == "fabrication":
            if kind in FABRICATION_AUTHORITY_KINDS and role in FABRICATION_ROLES:
                has_fabrication_authority = True
            else:
                rep.findings.append(Finding(
                    severity="ERROR", row_index=i, artifact_id=aid,
                    code="INVALID_FABRICATION_AUTHORITY_KIND",
                    message=("fabrication authority must be a DXF, CAD, "
                             "drawing PDF, design table, or measurement "
                             "template with a fabrication role."),
                ))

        if authority == "derived_preview" and not derived_from:
            rep.findings.append(Finding(
                severity="ERROR", row_index=i, artifact_id=aid,
                code="MISSING_DERIVED_FROM",
                message="derived_preview artifacts must name derived_from.",
            ))

        if kind in IMAGE_GEN_KINDS:
            if authority == "fabrication":
                rep.findings.append(Finding(
                    severity="ERROR", row_index=i, artifact_id=aid,
                    code="IMAGE_GEN_AS_FABRICATION_AUTHORITY",
                    message=("image-gen-2 prompts and outputs are concept or "
                             "story support only; they cannot be fabrication "
                             "authority."),
                ))
            if role in FABRICATION_ROLES:
                rep.findings.append(Finding(
                    severity="ERROR", row_index=i, artifact_id=aid,
                    code="IMAGE_GEN_WITH_FABRICATION_ROLE",
                    message=(f"image-gen-2 artifact uses fabrication role "
                             f"{role!r}; use one of "
                             f"{sorted(NON_AUTHORITY_IMAGE_ROLES)}."),
                ))
            if dimension_claim == "image_inferred":
                rep.findings.append(Finding(
                    severity="ERROR", row_index=i, artifact_id=aid,
                    code="IMAGE_GEN_DIMENSION_INFERRED",
                    message=("image-gen-2 cannot be used to infer dimensions, "
                             "hole locations, sockets, reed windows, or "
                             "toolpaths."),
                ))
            if authority not in {"concept_only", "reference_only"}:
                rep.findings.append(Finding(
                    severity="ERROR", row_index=i, artifact_id=aid,
                    code="IMAGE_GEN_BAD_AUTHORITY",
                    message=("image-gen-2 artifacts must use authority "
                             "concept_only or reference_only."),
                ))
            if role not in NON_AUTHORITY_IMAGE_ROLES:
                rep.findings.append(Finding(
                    severity="ERROR", row_index=i, artifact_id=aid,
                    code="IMAGE_GEN_BAD_ROLE",
                    message=("image-gen-2 artifacts must use a "
                             "non-fabrication visual role."),
                ))

        if fabrication_required and authority != "fabrication":
            rep.findings.append(Finding(
                severity="WARN", row_index=i, artifact_id=aid,
                code="FABRICATION_REQUIRED_NON_AUTHORITY_ROW",
                message=("fabrication_required is true on a non-authority row; "
                         "put the flag on the governing DXF/CAD/design-table "
                         "record or remove it."),
            ))

    any_fabrication_required = any(
        _boolish(row.get("fabrication_required")) for row in rows)
    any_build_visual = any(
        _norm(row.get("role")) in FABRICATION_ROLES
        or _norm(row.get("authority")) in {"fabrication", "derived_preview"}
        for row in rows)

    if (any_fabrication_required or any_build_visual) and not has_fabrication_authority:
        rep.findings.append(Finding(
            severity="ERROR",
            row_index=0,
            artifact_id="",
            code="NO_FABRICATION_AUTHORITY",
            message=("Register includes build/cut/derived visual work but no "
                     "fabrication-authority DXF, CAD, drawing PDF, design "
                     "table, or measurement template."),
        ))

    return rep


def load_register(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("visual_outputs", data.get("outputs"))
        if not isinstance(data, list):
            raise ValueError("JSON register must be a list or contain visual_outputs")
        if not all(isinstance(row, dict) for row in data):
            raise ValueError("JSON register rows must be objects")
        return data

    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=("Validate instrument-maker-v4 visual-output authority "
                     "records for DXF/CAD vs image-gen-2 boundaries."))
    p.add_argument("register", type=Path,
                   help="Path to visual-output-register.csv or .json")
    p.add_argument("--strict", action="store_true",
                   help="Exit 1 on warnings as well as errors.")
    p.add_argument("--json", action="store_true",
                   help="Emit findings as a JSON document on stdout.")
    args = p.parse_args(argv)

    if not args.register.exists():
        print(f"visual-output register not found: {args.register}",
              file=sys.stderr)
        return 2

    try:
        rows = load_register(args.register)
    except (OSError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        print(f"Could not parse {args.register}: {exc}", file=sys.stderr)
        return 2

    rep = validate_rows(rows, file_label=str(args.register))

    if args.json:
        out = {
            "file": rep.file,
            "rows_total": rep.rows_total,
            "rows_checked": rep.rows_checked,
            "errors": [asdict(f) for f in rep.errors],
            "warnings": [asdict(f) for f in rep.warnings],
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"validate_visual_authority: {rep.file}")
        print(f"  rows_total={rep.rows_total} checked={rep.rows_checked}")
        for f in rep.findings:
            print("  " + f.human())
        print(f"  -> {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")

    if rep.errors:
        return 1
    if args.strict and rep.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
