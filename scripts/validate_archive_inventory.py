#!/usr/bin/env python3
"""Validate the committed archive inventory CSV for issue #53."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


REQUIRED_COLUMNS = ["RelativePath", "Depth", "FileCount", "TotalSizeMB", "LastModified", "Extensions"]


def validate(path: Path, *, min_rows: int = 140) -> list[str]:
    findings: list[str] = []
    if not path.exists():
        return [f"missing inventory: {path}"]

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_COLUMNS:
            findings.append(f"unexpected header: {reader.fieldnames}")
            return findings
        rows = list(reader)

    if len(rows) < min_rows:
        findings.append(f"expected at least {min_rows} rows, got {len(rows)}")

    for index, row in enumerate(rows, start=2):
        if not row["RelativePath"].strip():
            findings.append(f"row {index}: RelativePath is empty")
        try:
            depth = int(row["Depth"])
            file_count = int(row["FileCount"])
            total_size = float(row["TotalSizeMB"])
        except ValueError:
            findings.append(f"row {index}: numeric fields must parse")
            continue
        if depth < 0:
            findings.append(f"row {index}: Depth must be non-negative")
        if file_count < 0:
            findings.append(f"row {index}: FileCount must be non-negative")
        if total_size < 0:
            findings.append(f"row {index}: TotalSizeMB must be non-negative")

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate archive inventory CSV shape.")
    parser.add_argument("csv_path", type=Path, nargs="?", default=Path("data/archive-inventory-2026-05-09.csv"))
    parser.add_argument("--min-rows", type=int, default=140)
    args = parser.parse_args(argv)

    findings = validate(args.csv_path, min_rows=args.min_rows)
    if findings:
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1
    print(f"archive inventory: ok ({args.csv_path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
