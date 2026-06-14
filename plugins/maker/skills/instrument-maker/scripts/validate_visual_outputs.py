#!/usr/bin/env python3
"""Validate the v4 DXF-first visual-output contract.

Checks:
  - visual-output-contract.json exists and declares supported targets
  - DXF authority files exist, declare millimeter units, and contain layers
  - SVG/PDF previews are declared as derived artifacts, not geometry authority
  - image-gen-2 prompt scaffolds are labeled non-dimensional

Usage:
  python3 scripts/validate_visual_outputs.py <packet_dir> [--strict]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_TARGETS = {"dxf", "preview-svg", "preview-pdf", "image-prompts"}
REQUIRED_LAYERS = {
    "OUTLINE",
    "CENTERLINE_REF",
    "SCALE_REF",
    "BRIDGE",
    "STRING_PATH",
    "NOTES_NO_CUT",
}


@dataclass
class Finding:
    severity: str
    code: str
    message: str

    def human(self) -> str:
        return f"[{self.severity}] {self.code}: {self.message}"


def load_contract(packet: Path) -> tuple[dict, list[Finding]]:
    path = packet / "visual-output-contract.json"
    if not path.exists():
        return {}, [Finding(
            "ERROR",
            "MISSING_VISUAL_CONTRACT",
            "visual-output-contract.json is required for DXF-first packets.",
        )]
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return {}, [Finding("ERROR", "BAD_VISUAL_CONTRACT_JSON", str(exc))]


def dxf_layers(text: str) -> set[str]:
    return set(re.findall(r"\n2\n([A-Z0-9_]+)\n70\n0\n62\n", text))


def dxf_units_mm(text: str) -> bool:
    return "$INSUNITS" in text and re.search(r"\$INSUNITS\s*\n70\s*\n4\b", text) is not None


def validate_dxf(packet: Path, rel_path: str) -> list[Finding]:
    findings: list[Finding] = []
    path = packet / rel_path
    if not path.exists():
        return [Finding("ERROR", "MISSING_DXF", f"{rel_path} does not exist")]
    text = path.read_text(encoding="utf-8", errors="replace")
    if "$ACADVER" not in text:
        findings.append(Finding("ERROR", "DXF_MISSING_HEADER", f"{rel_path} has no DXF header"))
    if not dxf_units_mm(text):
        findings.append(Finding("ERROR", "DXF_UNITS_NOT_MM", f"{rel_path} must declare $INSUNITS=4 (millimeters)"))
    missing = sorted(REQUIRED_LAYERS - dxf_layers(text))
    if missing:
        findings.append(Finding("ERROR", "DXF_MISSING_LAYERS", f"{rel_path} missing layers: {', '.join(missing)}"))
    if "ENDSEC" not in text or not text.rstrip().endswith("EOF"):
        findings.append(Finding("ERROR", "DXF_BAD_TERMINATOR", f"{rel_path} is missing ENDSEC/EOF terminator"))
    return findings


def validate_prompt(packet: Path, rel_path: str) -> list[Finding]:
    path = packet / rel_path
    if not path.exists():
        return [Finding("ERROR", "MISSING_IMAGE_PROMPTS", f"{rel_path} does not exist")]
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    if "non-dimensional" not in text:
        return [Finding(
            "ERROR",
            "IMAGE_PROMPTS_NOT_LABELED",
            f"{rel_path} must label image-gen-2 prompts as non-dimensional.",
        )]
    return []


def validate_preview(packet: Path, rel_path: str) -> list[Finding]:
    path = packet / rel_path
    if not path.exists():
        return [Finding("ERROR", "MISSING_PREVIEW", f"{rel_path} does not exist")]
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            header = path.read_bytes()[:5]
        except OSError as exc:
            return [Finding("ERROR", "PREVIEW_UNREADABLE", f"{rel_path} could not be read: {exc}")]
        if header != b"%PDF-":
            return [Finding("ERROR", "BAD_PDF_PREVIEW", f"{rel_path} does not look like a PDF file")]
    elif suffix == ".svg":
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        if "<svg" not in text:
            return [Finding("ERROR", "BAD_SVG_PREVIEW", f"{rel_path} does not look like an SVG file")]
    else:
        return [Finding("WARN", "UNKNOWN_PREVIEW_TYPE", f"{rel_path} is not SVG or PDF")]
    return []


def validate(packet: Path) -> list[Finding]:
    contract, findings = load_contract(packet)
    if findings:
        return findings

    targets = set(contract.get("visual_output_targets") or [])
    unknown = sorted(targets - SUPPORTED_TARGETS)
    if unknown:
        findings.append(Finding("ERROR", "UNKNOWN_VISUAL_TARGET", f"Unsupported visual targets: {', '.join(unknown)}"))

    if "dxf" in targets:
        dxf_paths = contract.get("geometry_authority") or []
        if not dxf_paths:
            findings.append(Finding("ERROR", "NO_DXF_AUTHORITY", "target dxf requires geometry_authority entries"))
        for rel in dxf_paths:
            if not str(rel).lower().endswith(".dxf"):
                findings.append(Finding("ERROR", "AUTHORITY_NOT_DXF", f"{rel} is not a DXF authority file"))
            findings.extend(validate_dxf(packet, str(rel)))

    preview_paths = [str(rel) for rel in (contract.get("derived_previews") or [])]
    if "preview-svg" in targets and not any(path.lower().endswith(".svg") for path in preview_paths):
        findings.append(Finding("ERROR", "NO_SVG_PREVIEW", "target preview-svg requires a derived .svg preview"))
    if "preview-pdf" in targets and not any(path.lower().endswith(".pdf") for path in preview_paths):
        findings.append(Finding("ERROR", "NO_PDF_PREVIEW", "target preview-pdf requires a derived .pdf preview"))

    for rel in preview_paths:
        if str(rel).lower().endswith(".dxf"):
            findings.append(Finding("ERROR", "DXF_LISTED_AS_PREVIEW", f"{rel} cannot be a derived preview"))
            continue
        findings.extend(validate_preview(packet, str(rel)))

    for rel in contract.get("image_gen_2_prompt_scaffolds") or []:
        findings.extend(validate_prompt(packet, str(rel)))

    rules = " ".join(contract.get("rules") or []).lower()
    if "svg" not in rules or "derived" not in rules:
        findings.append(Finding("WARN", "PREVIEW_DERIVATION_NOT_EXPLICIT", "contract rules should state SVG/PDF are derived previews"))
    if "non-dimensional" not in rules:
        findings.append(Finding("WARN", "IMAGE_RULE_NOT_EXPLICIT", "contract rules should state AI images are non-dimensional"))

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    findings = validate(args.packet)
    print(f"validate_visual_outputs: {args.packet}")
    for finding in findings:
        print("  " + finding.human())
    errors = [f for f in findings if f.severity == "ERROR"]
    warnings = [f for f in findings if f.severity == "WARN"]
    print(f"  -> {len(errors)} error(s), {len(warnings)} warning(s)")
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
