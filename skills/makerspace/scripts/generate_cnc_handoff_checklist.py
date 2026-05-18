#!/usr/bin/env python3
"""Generate a DXF/CNC fabrication handoff blocker list from one source JSON.

The generated JSON is the machine-readable handoff record. It is a blocker
list, not a pass certificate: it surfaces the gates that must be reviewed by
the fabrication owner before shop work can proceed. The generated validation.csv
mirrors the makerspace structured-artifact schema so the existing packet
validator can check the handoff gates without a second validator.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXAMPLE = (
    ROOT
    / "references"
    / "examples"
    / "cnc-laser-fabrication-handoff"
)
DEFAULT_SOURCE = DEFAULT_EXAMPLE / "design_params.json"

VALIDATION_FIELDS = [
    "check_id",
    "check_name",
    "target",
    "tolerance",
    "method",
    "when_to_check",
    "pass_fail",
    "notes",
]


def load_source(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    required = [
        "handoff_id",
        "project",
        "revision",
        "authority",
        "source_files",
        "machine_routes",
        "readiness_gates",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"{path} missing required keys: {missing}")
    return data


def build_checklist(data: dict[str, Any]) -> dict[str, Any]:
    gates = []
    for gate in data["readiness_gates"]:
        gates.append(
            {
                "check_id": gate["check_id"],
                "check_name": gate["check_name"],
                "status": gate.get("pass_fail", "pending"),
                "target": gate["target"],
                "tolerance": gate.get("tolerance", "TBD"),
                "method": gate["method"],
                "when_to_check": gate["when_to_check"],
                "handoff_owner": gate.get("handoff_owner", "fabrication lead"),
                "stop_work_if_missing": bool(
                    gate.get("stop_work_if_missing", True),
                ),
                "notes": gate.get("notes", ""),
            },
        )

    return {
        "handoff_id": data["handoff_id"],
        "project": data["project"],
        "revision": data["revision"],
        "generated_from": "design_params.json",
        "checklist_role": "blocker_list_not_pass_certificate",
        "generated_checklist_notice": (
            "Generated checklists surface blockers for fabrication-owner "
            "review; they do not certify shop readiness or replace CAD, "
            "drawing, material, CAM, workholding, and safety review."
        ),
        "fabrication_authority": data["authority"],
        "source_files": data["source_files"],
        "machine_routes": data["machine_routes"],
        "readiness_gates": gates,
        "handoff_decision": {
            "ready_when": (
                "all gates are marked pass or explicitly waived by the "
                "fabrication owner after source review"
            ),
            "blocked_when": [
                "CAD/DXF source cannot be tied to the revision",
                "material, machine, or workholding assumptions remain TBD",
                "CAM operator must infer units, origin, scale, kerf, or depth",
                "generated checklist is treated as a pass certificate "
                "without owner review",
            ],
        },
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_validation_csv(path: Path, checklist: dict[str, Any]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=VALIDATION_FIELDS,
            lineterminator="\n",
        )
        writer.writeheader()
        for gate in checklist["readiness_gates"]:
            writer.writerow(
                {
                    "check_id": gate["check_id"],
                    "check_name": gate["check_name"],
                    "target": gate["target"],
                    "tolerance": gate["tolerance"],
                    "method": gate["method"],
                    "when_to_check": gate["when_to_check"],
                    "pass_fail": gate["status"],
                    "notes": gate["notes"],
                },
            )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a CNC/laser fabrication handoff checklist.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Source design_params.json file.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory. Defaults to the source file directory.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = args.source
    out_dir = args.out_dir or source.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    data = load_source(source)
    checklist = build_checklist(data)
    write_json(out_dir / "handoff_checklist.json", checklist)
    write_validation_csv(out_dir / "validation.csv", checklist)

    print(f"wrote {out_dir / 'handoff_checklist.json'}")
    print(f"wrote {out_dir / 'validation.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
