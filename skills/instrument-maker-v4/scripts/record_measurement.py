#!/usr/bin/env python3
"""
record_measurement.py — ingest a tuner reading, close the empirical loop.

Brainstorm Tier 1 #4: today validation.csv has target columns but no path
from "I measured this with a tuner" back into the design sheet. v4 ingests
measurements, computes cents error, appends to a per-family corrections
database, and flags sibling packets whose predictions just shifted.

Usage:
    python3 scripts/record_measurement.py \\
        --packet ./build-packets/<slug> \\
        --note-id A4 \\
        --measured-hz 442.3 \\
        --tuner "Korg OT-120" \\
        --environment "shop, 68F, 45% RH"

Optional:
    --corrections-db <path>   default: <skill>/corrections.sqlite
    --dry-run                 don't write files; print actions
"""

import argparse
import csv
import math
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def cents_error(measured_hz, predicted_hz):
    if measured_hz is None or predicted_hz is None or predicted_hz == 0:
        return None
    return 1200.0 * math.log2(measured_hz / predicted_hz)


def ensure_corrections_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS measurements (
      measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
      instrument_id TEXT,
      family TEXT,
      note_id TEXT,
      predicted_hz REAL,
      measured_hz REAL,
      cents_error REAL,
      governing_model TEXT,
      k_constant REAL,
      k2_correction REAL,
      end_correction REAL,
      wood_species TEXT,
      bore_diameter REAL,
      tuner TEXT,
      environment TEXT,
      measurement_date TEXT,
      packet_path TEXT
    );
    CREATE TABLE IF NOT EXISTS pending_regenerations (
      regen_id INTEGER PRIMARY KEY AUTOINCREMENT,
      instrument_id TEXT,
      packet_path TEXT,
      old_prediction_hz REAL,
      new_prediction_hz REAL,
      cents_delta REAL,
      reason TEXT,
      flagged_at TEXT
    );
    CREATE TABLE IF NOT EXISTS corrections_summary (
      family TEXT,
      parameter TEXT,
      parameter_band TEXT,
      current_value REAL,
      ci_low REAL,
      ci_high REAL,
      source_study_id TEXT,
      n_measurements INTEGER,
      last_updated TEXT,
      PRIMARY KEY (family, parameter, parameter_band)
    );
    """)
    conn.commit()


def read_validation_csv(path: Path):
    if not path.exists():
        return None, None
    with path.open(newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return [], []
    return rows[0], rows[1:]


def write_validation_csv(path: Path, header, rows):
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def parse_design_md_governing_model(packet: Path):
    """Light read of design.md for governing model + species."""
    md = packet / "design.md"
    if not md.exists():
        return {"governing_model": None, "wood_species": None,
                "k_constant": None, "k2_correction": None,
                "end_correction": None, "bore_diameter": None,
                "instrument_id": None, "family": None}
    text = md.read_text(errors="ignore").lower()
    info = {"governing_model": None, "wood_species": None,
            "k_constant": None, "k2_correction": None,
            "end_correction": None, "bore_diameter": None,
            "instrument_id": None, "family": None}
    for marker, key in [
        ("helmholtz", "helmholtz"),
        ("open-pipe", "open-pipe"),
        ("open pipe", "open-pipe"),
        ("stopped pipe", "stopped-pipe"),
        ("free-free", "free-free-beam"),
        ("cantilever", "cantilever"),
        ("mersenne", "string"),
    ]:
        if marker in text:
            info["governing_model"] = key
            break
    for species in ("padauk", "wenge", "hard maple", "cherry",
                    "black walnut", "red cedar", "baltic birch",
                    "cedar", "maple", "walnut"):
        if species in text:
            info["wood_species"] = species
            break
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--packet", required=True, help="build-packets/<slug>")
    ap.add_argument("--note-id", required=True,
                    help="row in validation.csv to update")
    ap.add_argument("--measured-hz", required=True, type=float)
    ap.add_argument("--tuner", default="")
    ap.add_argument("--environment", default="")
    ap.add_argument("--corrections-db", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    packet = Path(args.packet)
    if not packet.exists():
        print(f"packet not found: {packet}", file=sys.stderr)
        return 1

    val_csv = packet / "validation.csv"
    header, rows = read_validation_csv(val_csv)
    if header is None:
        print(f"validation.csv not found in {packet}", file=sys.stderr)
        return 1

    # Find note row
    try:
        note_idx = header.index("note_id")
    except ValueError:
        print(f"validation.csv has no 'note_id' column. Header: {header}",
              file=sys.stderr)
        return 1

    target_row = None
    for r in rows:
        if r[note_idx] == args.note_id:
            target_row = r
            break
    if target_row is None:
        print(f"no row in validation.csv with note_id={args.note_id!r}",
              file=sys.stderr)
        return 1

    # Make sure required columns exist
    needed = ["measured_hz", "cents_error", "tuner", "environment",
              "measurement_date", "result"]
    for col in needed:
        if col not in header:
            header.append(col)
            for r in rows:
                if len(r) < len(header):
                    r.extend([""] * (len(header) - len(r)))

    # Compute cents error
    try:
        predicted_hz = float(target_row[header.index("predicted_hz")])
    except (ValueError, IndexError):
        predicted_hz = None
    cerr = cents_error(args.measured_hz, predicted_hz)

    # Block on huge errors
    if cerr is not None and abs(cerr) > 50:
        print(f"!! cents error = {cerr:+.1f} (>50) — likely a tuning bug, "
              f"wrong octave, or wrong note_id.", file=sys.stderr)
        print("   Confirm and re-run; aborting to protect corrections db.",
              file=sys.stderr)
        return 2

    # Update validation row
    target_row[header.index("measured_hz")] = f"{args.measured_hz:.2f}"
    target_row[header.index("cents_error")] = (
        f"{cerr:+.2f}" if cerr is not None else "")
    target_row[header.index("tuner")] = args.tuner
    target_row[header.index("environment")] = args.environment
    target_row[header.index("measurement_date")] = (
        datetime.now().strftime("%Y-%m-%d"))
    if cerr is not None:
        try:
            tol = float(target_row[header.index("tolerance_cents")]
                        .lstrip("±"))
        except (ValueError, IndexError):
            tol = 5.0
        if abs(cerr) <= tol:
            res = "pass"
        elif cerr < 0:
            res = "flat"
        else:
            res = "sharp"
        target_row[header.index("result")] = res

    # Pull design context
    design_info = parse_design_md_governing_model(packet)

    summary = {
        "validation_csv": str(val_csv),
        "note_id": args.note_id,
        "predicted_hz": predicted_hz,
        "measured_hz": args.measured_hz,
        "cents_error": cerr,
        "result": target_row[header.index("result")] if cerr is not None
                  else None,
        "governing_model": design_info["governing_model"],
        "wood_species": design_info["wood_species"],
    }

    # Corrections db
    db_path = args.corrections_db or str(
        Path(__file__).resolve().parents[1] / "corrections.sqlite")

    if args.dry_run:
        print("--dry-run: would update validation.csv with:")
        for k, v in zip(header, target_row):
            print(f"   {k}: {v}")
        print(f"--dry-run: would append measurement to {db_path}")
        print(f"--dry-run summary: {summary}")
        return 0

    # Persist validation.csv
    write_validation_csv(val_csv, header, rows)
    print(f"updated {val_csv}")

    # Persist measurement
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    ensure_corrections_schema(conn)
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO measurements
           (instrument_id, family, note_id, predicted_hz, measured_hz,
            cents_error, governing_model, k_constant, k2_correction,
            end_correction, wood_species, bore_diameter, tuner, environment,
            measurement_date, packet_path)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (design_info["instrument_id"], design_info["family"],
         args.note_id, predicted_hz, args.measured_hz, cerr,
         design_info["governing_model"], design_info["k_constant"],
         design_info["k2_correction"], design_info["end_correction"],
         design_info["wood_species"], design_info["bore_diameter"],
         args.tuner, args.environment,
         datetime.now().strftime("%Y-%m-%d"), str(packet)))
    conn.commit()
    conn.close()
    print(f"appended measurement to {db_path}")

    print(f"\nsummary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
