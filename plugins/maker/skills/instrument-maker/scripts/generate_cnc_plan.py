#!/usr/bin/env python3
"""
Generate a v4.2 CNC/manufacturing operation plan for a build packet.

This is intentionally not CAM. It emits the structured setup information a
human can carry into Vectric, Fusion, SolidWorks CAM, laser software, or the
lathe: operation order, tools, workholding, datum strategy, checks, and files.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


@dataclass
class Operation:
    op_id: str
    name: str
    machine: str
    tool: str
    workholding: str
    datum: str
    inputs: list[str]
    outputs: list[str]
    checks: list[str]
    notes: str = ""


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def extract_field(text: str, names: Iterable[str]) -> str:
    for name in names:
        pattern = re.compile(rf"^\s*(?:[-*]\s*)?\**{re.escape(name)}\**\s*[:|]\s*(.+)$", re.I | re.M)
        match = pattern.search(text)
        if match:
            return match.group(1).strip().strip("|").strip()
    return ""


def detect_family(packet: Path, override: str = "") -> str:
    if override:
        return override.lower()
    text = "\n".join(
        read_text(packet / name)
        for name in ("design.md", "README.md", "drawing-brief.md", "assembly-manual.md")
    )
    explicit = extract_field(text, ["Family", "Instrument family"])
    hay = f"{explicit}\n{text}".lower()
    checks = [
        ("segmented-drum", ["ashiko", "conga", "djembe", "dundun", "segmented drum"]),
        ("vessel-ceramic", ["slip cast", "slip-cast", "ocarina", "udu", "gemshorn", "ceramic"]),
        ("woodwind", ["flute", "shakuhachi", "quena", "kena", "duduk", "fujara", "didgeridoo", "bore"]),
        ("beam-idiophone", ["tongue drum", "marimba", "xylophone", "glockenspiel", "tubular bells", "beam"]),
        ("string-body", ["guitar", "violin", "harp", "kora", "ngoni", "oud", "lute", "ukulele", "string"]),
        ("box-drum", ["cajon", "cajón", "resonant box"]),
    ]
    for family, needles in checks:
        if any(needle in hay for needle in needles):
            return family
    return "generic"


def packet_files(packet: Path) -> dict[str, bool]:
    names = [
        "design.md",
        "family-spec.csv",
        "bom.csv",
        "cut-list.csv",
        "sourcing.csv",
        "drawing-brief.md",
        "assembly-manual.md",
        "validation.csv",
    ]
    return {name: (packet / name).exists() for name in names}


def op(
    op_id: str,
    name: str,
    machine: str,
    tool: str,
    workholding: str,
    datum: str,
    inputs: list[str],
    outputs: list[str],
    checks: list[str],
    notes: str = "",
) -> Operation:
    return Operation(op_id, name, machine, tool, workholding, datum, inputs, outputs, checks, notes)


def template_operations(family: str) -> list[Operation]:
    common_first = op(
        "OP-010",
        "Review design package and mark datums",
        "Bench",
        "Calipers, square, marking knife, center punch",
        "Flat bench, drawing packet",
        "Primary centerline / face A",
        ["design.md", "drawing-brief.md", "cut-list.csv"],
        ["shop-marked blank", "datum checklist"],
        ["All stock dimensions exceed finished dimensions plus allowance", "Units match drawings"],
    )
    common_last = op(
        "OP-900",
        "Validation and tuning pass",
        "Bench",
        "Chromatic tuner, calipers, scale, recording device",
        "Padded bench",
        "Same acoustic datum used in design.md",
        ["validation.csv", "finished part"],
        ["updated validation.csv", "process photo"],
        ["Measured frequency recorded", "Cents error computed", "Tuning trim notes written"],
    )
    templates: dict[str, list[Operation]] = {
        "woodwind": [
            common_first,
            op(
                "OP-110",
                "Prepare bore blank",
                "Table saw / jointer / planer",
                "Rip blade, jointer knives, planer",
                "Push blocks, featherboard",
                "Face A and centerline",
                ["cut-list.csv"],
                ["square bore blank"],
                ["Blank straightness checked", "Grain direction marked"],
            ),
            op(
                "OP-210",
                "Create bore",
                "Lathe or CNC router",
                "Long brad-point bit, reamer, or ball/end mill for split blank",
                "Tailstock vise/carrier or flip jig with datum pins",
                "Centerline A-B",
                ["drawing-brief.md", "family-spec.csv"],
                ["bored or routed body half"],
                ["Bore wander checked on scrap", "Bore diameter measured at both ends"],
                "Use the deep-bore technique reference when the bore is long and straight.",
            ),
            op(
                "OP-310",
                "Cut tone features",
                "CNC router / drill press / laser template",
                "1/8 in upcut spiral, brad-point bits, or printed drill guide",
                "V-block, centerline fence, registration pins",
                "Embouchure end datum",
                ["scale table", "drawing-brief.md"],
                ["tone holes / windows"],
                ["Hole spacing matches scale table", "Undercut/tuning allowance left"],
            ),
            common_last,
        ],
        "beam-idiophone": [
            common_first,
            op(
                "OP-120",
                "Surface and thickness blanks",
                "Planer / drum sander",
                "Planer knives, sanding conveyor",
                "Flat carrier board",
                "Top face A",
                ["cut-list.csv", "bom.csv"],
                ["thicknessed blanks"],
                ["Thickness within tolerance", "Grain direction logged"],
            ),
            op(
                "OP-220",
                "CNC cut tongues/bars/slots",
                "CNC router or laser",
                "1/8 in upcut spiral for slits; 3/4 in ball-end for arches",
                "Spoilboard tape/clamps; tabs where needed",
                "Top face A, left edge B",
                ["drawing-brief.md", "family-spec.csv"],
                ["rough-tuned tongues or bars"],
                ["No inside radius blocks motion", "Tabs avoid vibrating areas"],
            ),
            op(
                "OP-320",
                "Tune by controlled material removal",
                "Bench / sander / rotary tool",
                "Sanding block, small round file, tuner",
                "Soft support at nodes",
                "Node marks / tongue root",
                ["validation.csv"],
                ["final tuning log"],
                ["Remove mass from correct region", "Record before/after Hz"],
            ),
            common_last,
        ],
        "segmented-drum": [
            common_first,
            op(
                "OP-130",
                "Cut segmented ring stock",
                "Table saw with miter sled",
                "Sharp crosscut blade, stop block",
                "Miter sled, length stop, labeled bins",
                "Segment long edge",
                ["cut-list.csv", "family-spec.csv"],
                ["labeled segments"],
                ["Miter angle verified", "Segment count plus spares cut"],
            ),
            op(
                "OP-230",
                "Glue and flatten rings",
                "Bench / drum sander",
                "Band clamps, cauls, sanding jig",
                "Ring clamp, flat reference board",
                "Ring center",
                ["assembly-manual.md"],
                ["flat rings"],
                ["Gaps inspected", "Ring thickness logged"],
            ),
            op(
                "OP-330",
                "Stack glue-up and turn shell",
                "Lathe",
                "Bowl gouge, scraper, calipers",
                "Faceplate or chuck with tailstock support",
                "Shell axis",
                ["drawing-brief.md"],
                ["turned shell"],
                ["Wall thickness above minimum", "Rim diameter checked"],
            ),
            common_last,
        ],
        "vessel-ceramic": [
            common_first,
            op(
                "OP-140",
                "Prepare master and mold plan",
                "3D printer / CNC / bench",
                "Printer, sanding blocks, mold boards",
                "Parting-board registration keys",
                "Mold parting plane",
                ["drawing-brief.md", "family-spec.csv"],
                ["master pattern", "mold plan"],
                ["Shrinkage allowance applied", "Undercuts resolved"],
            ),
            op(
                "OP-240",
                "Cast and trim greenware",
                "Ceramic bench",
                "Slip, plaster mold, trimming tools",
                "Mold straps and keyed halves",
                "Mold registration keys",
                ["assembly-manual.md"],
                ["trimmed greenware"],
                ["Wall thickness checked", "Tone holes undersized for post-fire tuning"],
            ),
            op(
                "OP-340",
                "Fire, measure shrinkage, post-fire tune",
                "Kiln / bench",
                "Kiln furniture, diamond files, tuner",
                "Padded bench",
                "Mouth/window datum",
                ["validation.csv", "data/shrinkage-fit.csv"],
                ["fired body", "updated validation.csv"],
                ["Shrinkage recorded", "Tuning corrections written back"],
            ),
            common_last,
        ],
        "string-body": [
            common_first,
            op(
                "OP-150",
                "Create body/neck datum geometry",
                "CNC router / bandsaw / hand tools",
                "1/4 in upcut, 1/2 in downcut, template bit",
                "Spoilboard, centerline pins, perimeter tabs",
                "Centerline and scale-length datum",
                ["drawing-brief.md", "bom.csv"],
                ["routed body/neck blanks"],
                ["Bridge line and neck pocket agree", "Hardware templates match BOM"],
            ),
            op(
                "OP-250",
                "Route cavities and hardware features",
                "CNC router / drill press",
                "1/4 in upcut, Forstner bits, brad-point bits",
                "Flip jig if back-side operations exist",
                "Centerline and bridge datum",
                ["sourcing.csv", "drawing-brief.md"],
                ["cavities, holes, slots"],
                ["Pickup/control depth checked", "Inside radii dogboned if needed"],
            ),
            common_last,
        ],
        "box-drum": [
            common_first,
            op(
                "OP-160",
                "Cut panel set and joinery",
                "Table saw / CNC router / laser",
                "Panel saw blade, 1/4 in downcut, V-bit for labels",
                "Panel sled, spoilboard clamps",
                "Front face and bottom edge",
                ["cut-list.csv"],
                ["panel set"],
                ["Panel squareness checked", "Joinery test-fit on scrap"],
            ),
            op(
                "OP-260",
                "Cut soundhole/snare/port features",
                "CNC router / drill press",
                "Hole saw, 1/4 in spiral, small drill bits",
                "Panel clamp fixture",
                "Back panel centerline",
                ["drawing-brief.md"],
                ["ported and snare-ready panels"],
                ["Port area matches Helmholtz target", "Snare access serviceable"],
            ),
            common_last,
        ],
    }
    return templates.get(
        family,
        [
            common_first,
            op(
                "OP-200",
                "Plan primary shaping operation",
                "CNC router / lathe / laser / bench",
                "TBD after reviewing drawing",
                "TBD fixture",
                "Primary datum from drawing",
                ["drawing-brief.md", "cut-list.csv"],
                ["setup-specific artifact"],
                ["Machine envelope checked", "Tool access checked", "Workholding checked"],
                "Generic fallback: refine this plan before cutting material.",
            ),
            common_last,
        ],
    )


def build_plan(packet: Path, family: str, machine_note: str) -> dict[str, object]:
    files = packet_files(packet)
    operations = template_operations(family)
    return {
        "schema": "instrument-maker-v4.2-cnc-plan",
        "generated_on": date.today().isoformat(),
        "packet": str(packet),
        "family": family,
        "machine_note": machine_note,
        "available_inputs": files,
        "assumptions": [
            "This is a pre-CAM operation graph, not verified G-code.",
            "Verify feeds, speeds, work envelope, hold-down, and tool clearance at the machine.",
            "Run air-cut or simulation before cutting instrument material.",
        ],
        "operations": [asdict(operation) for operation in operations],
        "release_checks": [
            "Every operation has a datum and workholding method.",
            "Every tool has a real machine available or an escalation note.",
            "All tuning-critical features include trim allowance.",
            "Validation.csv receives measured data after the first prototype.",
        ],
    }


def write_plan(packet: Path, plan: dict[str, object], dry_run: bool) -> None:
    cnc_dir = packet / "cnc"
    json_path = cnc_dir / "cnc-plan.json"
    csv_path = cnc_dir / "operations.csv"
    md_path = cnc_dir / "setup-sheet.md"
    if dry_run:
        print(f"--dry-run: would write {json_path}")
        print(f"--dry-run: would write {csv_path}")
        print(f"--dry-run: would write {md_path}")
        print(json.dumps(plan, indent=2))
        return
    cnc_dir.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    operations = plan["operations"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "op_id",
            "name",
            "machine",
            "tool",
            "workholding",
            "datum",
            "inputs",
            "outputs",
            "checks",
            "notes",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for operation in operations:
            row = dict(operation)
            for key in ("inputs", "outputs", "checks"):
                row[key] = "; ".join(row[key])
            writer.writerow(row)
    md_path.write_text(markdown_setup_sheet(plan), encoding="utf-8")
    print(json_path)
    print(csv_path)
    print(md_path)


def markdown_setup_sheet(plan: dict[str, object]) -> str:
    lines = [
        "# CNC / Manufacturing Setup Sheet",
        "",
        f"- Packet: `{plan['packet']}`",
        f"- Family: `{plan['family']}`",
        f"- Generated: {plan['generated_on']}",
        f"- Machine note: {plan['machine_note']}",
        "",
        "## Assumptions",
        "",
    ]
    for assumption in plan["assumptions"]:
        lines.append(f"- {assumption}")
    lines.extend(["", "## Operation Graph", ""])
    for operation in plan["operations"]:
        lines.extend(
            [
                f"### {operation['op_id']} - {operation['name']}",
                "",
                f"- Machine: {operation['machine']}",
                f"- Tool: {operation['tool']}",
                f"- Workholding: {operation['workholding']}",
                f"- Datum: {operation['datum']}",
                f"- Inputs: {', '.join(operation['inputs'])}",
                f"- Outputs: {', '.join(operation['outputs'])}",
                "- Checks:",
            ]
        )
        lines.extend(f"  - {check}" for check in operation["checks"])
        if operation.get("notes"):
            lines.append(f"- Notes: {operation['notes']}")
        lines.append("")
    lines.extend(["## Release Checks", ""])
    lines.extend(f"- [ ] {check}" for check in plan["release_checks"])
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet_dir", type=Path)
    parser.add_argument("--family", help="Override detected family/pipeline")
    parser.add_argument(
        "--machine-note",
        default="Maker Nexus/home shop; verify exact machine before CAM.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    packet = args.packet_dir
    if not packet.exists():
        raise SystemExit(f"Packet folder not found: {packet}")
    family = detect_family(packet, args.family or "")
    plan = build_plan(packet, family, args.machine_note)
    write_plan(packet, plan, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
