#!/usr/bin/env python3
"""
migrate_packet.py — upgrade a v3 packet to v4 format.

Brainstorm Tier 4 #14: every breaking change orphans previous work without a
migration script.

What it adds (idempotent — safe to re-run):
  - risks.md skeleton (5 categories, placeholder entries)
  - drawings/*.svg by invoking generate_drawings.py if family-spec.csv exists
  - site/ folder by invoking generate_site.py
  - extends validation.csv schema with v4 columns
    (cents_error, tuner, environment, measurement_date, result, action)

Usage:
    python3 scripts/migrate_packet.py ./build-packets/<slug>
    python3 scripts/migrate_packet.py ./build-packets/<slug> --dry-run
"""

import argparse
import csv
import subprocess
import sys
from pathlib import Path


RISKS_TEMPLATE = """# Risks

This file was scaffolded by `migrate_packet.py` during the v3 → v4 upgrade.
Run `red-team` specialist or fill in by hand.

## Acoustic

(none identified — replace with real risks before shipping)

## Structural

(none identified — replace with real risks before shipping)

## Ergonomic

(none identified — replace with real risks before shipping)

## Supply

(none identified — replace with real risks before shipping)

## Fit/Finish

(none identified — replace with real risks before shipping)
"""


V4_VALIDATION_COLS = ["measured_hz", "cents_error", "tuner", "environment",
                       "measurement_date", "result", "action"]


def upgrade_validation_csv(packet: Path, dry_run: bool) -> bool:
    val = packet / "validation.csv"
    if not val.exists():
        print(f"  - no validation.csv to upgrade")
        return False
    with val.open(newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return False
    header = rows[0]
    new_cols = [c for c in V4_VALIDATION_COLS if c not in header]
    if not new_cols:
        print(f"  - validation.csv already v4-compatible")
        return False
    if dry_run:
        print(f"  --dry-run: would extend validation.csv with: {new_cols}")
        return True
    new_header = header + new_cols
    new_rows = [new_header]
    for r in rows[1:]:
        new_rows.append(r + [""] * len(new_cols))
    with val.open("w", newline="") as f:
        csv.writer(f).writerows(new_rows)
    print(f"  - extended validation.csv with: {new_cols}")
    return True


def add_risks_skeleton(packet: Path, dry_run: bool) -> bool:
    risks = packet / "risks.md"
    if risks.exists():
        print(f"  - risks.md already exists")
        return False
    if dry_run:
        print(f"  --dry-run: would write {risks.name} ({len(RISKS_TEMPLATE)} bytes)")
        return True
    risks.write_text(RISKS_TEMPLATE, encoding="utf-8")
    print(f"  - wrote {risks.name} skeleton")
    return True


def maybe_run(cmd, dry_run, label):
    if dry_run:
        print(f"  --dry-run: would run: {' '.join(cmd)}")
        return False
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  - ran {label} (OK)")
            return True
        else:
            print(f"  ! {label} failed (rc={result.returncode}):")
            print(f"    stderr: {result.stderr[:300]}")
            return False
    except Exception as e:
        print(f"  ! {label} raised: {e}")
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("packet")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    packet = Path(args.packet)
    if not packet.exists():
        print(f"packet not found: {packet}", file=sys.stderr)
        return 1

    print(f"migrating {packet} v3 → v4")

    skill_root = Path(__file__).resolve().parents[1]
    py = sys.executable

    add_risks_skeleton(packet, args.dry_run)
    upgrade_validation_csv(packet, args.dry_run)

    drawings_dir = packet / "drawings"
    has_svg = (drawings_dir.exists()
               and any(p.suffix == ".svg" for p in drawings_dir.iterdir()))
    if not has_svg:
        cmd = [py, str(skill_root / "scripts" / "generate_drawings.py"),
               str(packet)]
        maybe_run(cmd, args.dry_run, "generate_drawings.py")
    else:
        print(f"  - drawings/ already populated")

    site_dir = packet / "site"
    if not (site_dir / "index.html").exists():
        cmd = [py, str(skill_root / "scripts" / "generate_site.py"),
               str(packet)]
        maybe_run(cmd, args.dry_run, "generate_site.py")
    else:
        print(f"  - site/ already exists")

    print(f"\nmigration complete (dry-run={args.dry_run})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
