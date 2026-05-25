#!/usr/bin/env python3
"""
record_measurement.py
=====================

Capture a measurement of a built part and append it to the
empirical-learning loop.

The loop has three storage tiers:
  1. <packet>/measurements.csv     — per-project (mirror of validation.csv)
  2. spaces/<slug>/corrections/raw-measurements.jsonl  — per-shop log
  3. spaces/<slug>/corrections/corrections.sqlite       — rolled-up

This script writes (1) and (2) directly. (3) is recomputed by
build_catalog_db.py from the raw log.

Usage:
    python3 scripts/record_measurement.py \\
        --packet ./projects/cnc-welcome-sign \\
        --space maker-nexus \\
        --check-id v002 \\
        --measured 0.118 \\
        --notes "depth gauge across deepest letter"

    # For a measurement that doesn't have a validation.csv row yet
    python3 scripts/record_measurement.py \\
        --packet ./projects/cnc-welcome-sign \\
        --space maker-nexus \\
        --new-check \\
        --check-name "actual op-3 time" \\
        --target 30 --tolerance 5 --unit minutes \\
        --measured 47 --notes "reset Z twice"
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


VALIDATION_HEADER = [
    "check_id", "check_name", "target", "tolerance", "method",
    "when_to_check", "pass_fail", "notes",
]
MEASUREMENT_HEADER = [
    "check_id", "check_name", "target", "tolerance", "unit",
    "measured", "delta", "in_tolerance",
    "measured_at", "measured_by", "notes",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Record a measurement against a build packet's validation.",
    )
    p.add_argument(
        "--packet",
        type=Path,
        required=True,
        help="Project directory containing validation.csv.",
    )
    p.add_argument(
        "--space",
        default="home-shop-default",
        help="Space slug (default: home-shop-default).",
    )
    p.add_argument(
        "--check-id",
        help="ID of the validation check this measurement is for "
        "(e.g., v002). Required unless --new-check is given.",
    )
    p.add_argument(
        "--measured",
        type=float,
        required=True,
        help="The measured value (numeric).",
    )
    p.add_argument(
        "--measured-by",
        default="",
        help="Optional name of the person who measured.",
    )
    p.add_argument(
        "--notes",
        default="",
        help="Free-form notes about how the measurement was taken.",
    )
    p.add_argument(
        "--unit",
        default="",
        help="Unit of measurement (in, mm, minutes, usd, etc.). If "
        "omitted, the script copies the unit from validation.csv if "
        "present.",
    )

    # New-check mode: record a measurement for something not in
    # validation.csv yet (useful for time/cost actuals).
    p.add_argument("--new-check", action="store_true")
    p.add_argument("--check-name", default="")
    p.add_argument("--target", type=float, default=None)
    p.add_argument("--tolerance", type=float, default=None)

    p.add_argument(
        "--space-root",
        type=Path,
        default=None,
        help="Root containing spaces/<slug>/. Default: searches "
        "./spaces/ then the script's repo.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written; don't write anything.",
    )
    return p.parse_args(argv)


def find_space_dir(slug: str, override: Path | None) -> Path | None:
    candidates = []
    if override is not None:
        candidates.append(override / slug)
    candidates += [
        Path(f"./spaces/{slug}"),
        Path(__file__).parent.parent / "spaces" / slug,
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def read_validation_row(packet: Path, check_id: str) -> dict | None:
    val_path = packet / "validation.csv"
    if not val_path.exists():
        return None
    with val_path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row.get("check_id") == check_id:
                return row
    return None


def upsert_measurement_row(packet: Path, row: dict, *, dry_run: bool) -> None:
    """Append or update measurements.csv for this packet."""
    m_path = packet / "measurements.csv"
    rows: list[dict] = []
    if m_path.exists():
        with m_path.open(newline="") as f:
            for r in csv.DictReader(f):
                rows.append(r)
    # Replace existing row with same check_id, else append
    found = False
    for i, r in enumerate(rows):
        if r.get("check_id") == row["check_id"]:
            rows[i] = row
            found = True
            break
    if not found:
        rows.append(row)
    if dry_run:
        print(f"DRY RUN: would write {len(rows)} rows to {m_path}")
        print(f"  new row: {row}")
        return
    with m_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=MEASUREMENT_HEADER)
        writer.writeheader()
        for r in rows:
            # Normalize: ensure all expected columns exist
            out = {k: r.get(k, "") for k in MEASUREMENT_HEADER}
            writer.writerow(out)


def append_raw_log(space_dir: Path, event: dict, *, dry_run: bool) -> None:
    log_dir = space_dir / "corrections"
    log_path = log_dir / "raw-measurements.jsonl"
    if dry_run:
        print(f"DRY RUN: would append event to {log_path}")
        print(f"  event: {json.dumps(event, sort_keys=True)}")
        return
    log_dir.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")


def compute_delta_and_tolerance(
    measured: float,
    target: float | None,
    tolerance: float | None,
) -> tuple[str, str]:
    if target is None:
        return "", ""
    delta = round(measured - target, 6)
    if tolerance is None:
        return str(delta), ""
    in_tol = "yes" if abs(delta) <= tolerance else "no"
    return str(delta), in_tol


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.packet.exists():
        print(f"Packet directory not found: {args.packet}", file=sys.stderr)
        return 2

    if not args.new_check and not args.check_id:
        print("Either --check-id or --new-check is required.", file=sys.stderr)
        return 2

    # Resolve check info
    check_id = args.check_id
    check_name = args.check_name
    target = args.target
    tolerance = args.tolerance
    unit = args.unit

    if not args.new_check:
        val_row = read_validation_row(args.packet, check_id)
        if val_row is None:
            print(
                f"check_id `{check_id}` not found in "
                f"{args.packet/'validation.csv'}.\n"
                f"Use --new-check to add a new check.",
                file=sys.stderr,
            )
            return 2
        check_name = check_name or val_row.get("check_name", "")
        try:
            target = target if target is not None else float(val_row.get("target", ""))
        except (TypeError, ValueError):
            target = None
        try:
            tolerance = tolerance if tolerance is not None else float(val_row.get("tolerance", "").lstrip("±"))
        except (TypeError, ValueError):
            tolerance = None
    else:
        if not check_name:
            print("--new-check requires --check-name.", file=sys.stderr)
            return 2
        # Generate a check_id if not provided
        if not check_id:
            existing = (args.packet / "measurements.csv")
            existing_count = 0
            if existing.exists():
                with existing.open(newline="") as f:
                    existing_count = sum(1 for _ in csv.DictReader(f))
            check_id = f"v{existing_count + 100:03d}"  # avoid clash with v001-v099

    delta, in_tol = compute_delta_and_tolerance(args.measured, target, tolerance)
    timestamp = datetime.now(timezone.utc).isoformat()

    # Build measurements.csv row
    row = {
        "check_id": check_id,
        "check_name": check_name,
        "target": "" if target is None else str(target),
        "tolerance": "" if tolerance is None else str(tolerance),
        "unit": unit,
        "measured": str(args.measured),
        "delta": delta,
        "in_tolerance": in_tol,
        "measured_at": timestamp,
        "measured_by": args.measured_by,
        "notes": args.notes,
    }
    upsert_measurement_row(args.packet, row, dry_run=args.dry_run)

    # Append to raw log
    space_dir = find_space_dir(args.space, args.space_root)
    if space_dir is None:
        print(
            f"Warning: space `{args.space}` not found; raw measurement "
            f"log not updated. Per-packet measurements.csv was written.",
            file=sys.stderr,
        )
    else:
        event = {
            "timestamp": timestamp,
            "space": args.space,
            "packet": str(args.packet.resolve()),
            "check_id": check_id,
            "check_name": check_name,
            "target": target,
            "tolerance": tolerance,
            "unit": unit,
            "measured": args.measured,
            "delta": float(delta) if delta else None,
            "in_tolerance": in_tol,
            "measured_by": args.measured_by,
            "notes": args.notes,
        }
        append_raw_log(space_dir, event, dry_run=args.dry_run)

    if not args.dry_run:
        print(
            f"Recorded {check_id} = {args.measured} "
            f"(delta {delta or 'n/a'}, in_tolerance: {in_tol or 'n/a'})"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
