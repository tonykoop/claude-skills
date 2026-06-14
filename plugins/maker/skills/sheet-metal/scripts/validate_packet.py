#!/usr/bin/env python3
"""Lint a sheet-metal deliverable folder. Checks for the expected default
artifacts listed in SKILL.md, validates basic CSV column shapes, and flags
missing safety/authority statements.

Exit code:
    0 = all required checks passed (warnings may still print)
    1 = at least one required check failed
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_FILES = [
    "design-brief.md",
    "parameters.csv",
]

RECOMMENDED_FILES = [
    "solidworks-plan.md",
    "flat-pattern-checklist.md",
    "fabrication-plan.md",
    "validation-checklist.md",
    "agent-record.md",
]

CONDITIONAL_FILES = [
    # filename, when it's expected
    ("bom.csv", "more than 5 parts"),
    ("hardware.csv", "more than 5 hardware items"),
    ("bend-table.csv", "any bent parts"),
    ("cut-list.csv", "any cut blanks"),
    ("load-cases.csv", "any load-bearing or safety-sensitive use"),
]

PARAMETERS_REQUIRED_COLUMNS = ["name", "value"]
PARAMETERS_RECOMMENDED_COLUMNS = ["units", "source", "confidence", "notes"]

AUTHORITY_PHRASES = [
    "fabrication-ready",
    "fabrication ready",
    "fabrication authority",
    "design and CAD planning",
    "design planning",
    "planning authority",
    "not road-ready",
    "not road ready",
]


@dataclass
class CheckResult:
    passed: bool
    message: str
    severity: str = "error"  # error | warning | info


@dataclass
class Report:
    packet_path: Path
    results: list[CheckResult] = field(default_factory=list)

    def add(self, passed: bool, msg: str, severity: str = "error") -> None:
        self.results.append(CheckResult(passed=passed, message=msg, severity=severity))

    def summarize(self) -> tuple[int, int, int]:
        errors = sum(1 for r in self.results if not r.passed and r.severity == "error")
        warnings = sum(1 for r in self.results if not r.passed and r.severity == "warning")
        passed = sum(1 for r in self.results if r.passed)
        return passed, warnings, errors


def check_required_files(report: Report) -> None:
    for fname in REQUIRED_FILES:
        p = report.packet_path / fname
        if p.exists():
            report.add(True, f"required file present: {fname}", "info")
        else:
            report.add(False, f"required file missing: {fname}", "error")


def check_recommended_files(report: Report) -> None:
    for fname in RECOMMENDED_FILES:
        p = report.packet_path / fname
        if p.exists():
            report.add(True, f"recommended file present: {fname}", "info")
        else:
            report.add(False, f"recommended file missing: {fname}", "warning")


def check_parameters_csv(report: Report) -> None:
    p = report.packet_path / "parameters.csv"
    if not p.exists():
        return
    try:
        with p.open("r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                report.add(False, "parameters.csv: empty file", "error")
                return
            header_lc = [h.strip().lower() for h in header]
            for col in PARAMETERS_REQUIRED_COLUMNS:
                if col not in header_lc:
                    report.add(False, f"parameters.csv: missing required column '{col}'", "error")
                else:
                    report.add(True, f"parameters.csv: has required column '{col}'", "info")
            for col in PARAMETERS_RECOMMENDED_COLUMNS:
                if col not in header_lc:
                    report.add(False, f"parameters.csv: missing recommended column '{col}'", "warning")
                else:
                    report.add(True, f"parameters.csv: has recommended column '{col}'", "info")

            row_count = sum(1 for _ in reader)
            if row_count == 0:
                report.add(False, "parameters.csv: zero data rows", "error")
            else:
                report.add(True, f"parameters.csv: {row_count} data rows", "info")
    except Exception as e:
        report.add(False, f"parameters.csv: failed to parse ({e})", "error")


def check_authority_statement(report: Report) -> None:
    """Look for an explicit authority phrase in design-brief.md, README.md, or
    agent-record.md. Catches packets that forgot to state their authority level."""
    candidates = ["design-brief.md", "README.md", "agent-record.md"]
    found = False
    for fname in candidates:
        p = report.packet_path / fname
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8").lower()
        except Exception:
            continue
        if any(phrase in text for phrase in AUTHORITY_PHRASES):
            found = True
            report.add(True, f"authority statement found in {fname}", "info")
            break
    if not found:
        report.add(
            False,
            f"no explicit authority statement found in any of {candidates}. "
            "Packets should state whether they are concept, design/planning, or "
            "fabrication-ready (with appropriate stop-work conditions).",
            "warning",
        )


def check_csv_files_well_formed(report: Report) -> None:
    """For any CSV file in the packet, check it has a header and at least one
    data row, and that all rows have the same column count as the header."""
    for entry in sorted(report.packet_path.iterdir()):
        if not entry.is_file() or entry.suffix.lower() != ".csv":
            continue
        try:
            with entry.open("r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header is None:
                    report.add(False, f"{entry.name}: empty file", "error")
                    continue
                ncols = len(header)
                ragged_rows = []
                row_count = 0
                for i, row in enumerate(reader, start=2):
                    # Skip blank lines (e.g., trailing newline at EOF).
                    if not row or all(cell == "" for cell in row):
                        continue
                    row_count += 1
                    if len(row) != ncols:
                        ragged_rows.append(i)
                if ragged_rows:
                    report.add(
                        False,
                        f"{entry.name}: rows with wrong column count (header={ncols}): lines {ragged_rows[:5]}{'...' if len(ragged_rows) > 5 else ''}",
                        "error",
                    )
                else:
                    report.add(True, f"{entry.name}: {row_count} rows, all columns aligned", "info")
        except Exception as e:
            report.add(False, f"{entry.name}: failed to parse ({e})", "error")


def print_report(report: Report, verbose: bool) -> int:
    passed, warnings, errors = report.summarize()
    for r in report.results:
        if r.severity == "info" and not verbose:
            continue
        prefix = {"error": "ERROR", "warning": "WARN", "info": "OK"}[r.severity]
        status = "PASS" if r.passed else prefix
        print(f"  [{status}] {r.message}")
    print()
    print(f"Summary for {report.packet_path}:")
    print(f"  Passed checks:   {passed}")
    print(f"  Warnings:        {warnings}")
    print(f"  Errors:          {errors}")
    return 0 if errors == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lint a sheet-metal deliverable folder for the expected default artifacts and CSV shapes."
    )
    parser.add_argument("path", help="Path to the packet directory.")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show passing checks in addition to warnings and errors.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    packet_path = Path(args.path).resolve()
    if not packet_path.exists() or not packet_path.is_dir():
        print(f"ERROR: {packet_path} is not a directory", file=sys.stderr)
        sys.exit(2)

    report = Report(packet_path=packet_path)
    check_required_files(report)
    check_recommended_files(report)
    check_parameters_csv(report)
    check_authority_statement(report)
    check_csv_files_well_formed(report)

    exit_code = print_report(report, args.verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
