#!/usr/bin/env python3
"""
record_doe_results.py
=====================

Initialize and update DoE study data CSVs.

Two modes:
  --init  : write the data CSV header and one blank row per planned run
  (default): append/update a single run's response values

Usage:
    # Initialize from the protocol
    python3 scripts/record_doe_results.py \\
        --packet ./projects/cnc-welcome-sign \\
        --study 1 \\
        --init

    # Update run 1 with measured responses
    python3 scripts/record_doe_results.py \\
        --packet ./projects/cnc-welcome-sign \\
        --study 1 \\
        --run-id 1 \\
        --response measured_depth_delta_in=-0.003,edge_finish_score=4 \\
        --notes "first cell, slight fuzzing on grain"

The script also appends a normalized event to
spaces/<slug>/corrections/raw-measurements.jsonl so DoE response
data feeds the empirical-learning loop.

Protocol parsing assumes the simple YAML shape from
references/doe-integration.md.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_yaml_simple(text: str) -> dict:
    """Reuse the parser from build_catalog_db.py if available."""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from build_catalog_db import parse_yaml_simple as _parser
        return _parser(text)
    except ImportError:
        # Fallback: try real PyYAML
        import yaml
        return yaml.safe_load(text) or {}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Initialize or update a DoE study data CSV.",
    )
    p.add_argument("--packet", type=Path, required=True)
    p.add_argument("--study", type=int, required=True)
    p.add_argument("--init", action="store_true",
                   help="Initialize the data CSV from the protocol.")
    p.add_argument("--run-id", type=int, default=None)
    p.add_argument(
        "--response",
        default="",
        help="comma-separated key=value pairs of response values.",
    )
    p.add_argument(
        "--notes", default="",
        help="Free-form notes for this run.",
    )
    p.add_argument(
        "--space",
        default="home-shop-default",
        help="Space slug for the corrections log.",
    )
    p.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for run-order randomization (init mode).",
    )
    return p.parse_args(argv)


def study_paths(packet: Path, study_id: int) -> tuple[Path, Path]:
    doe_dir = packet / "doe"
    protocol = doe_dir / f"study-{study_id:02d}-protocol.yaml"
    data = doe_dir / f"study-{study_id:02d}-data.csv"
    return protocol, data


def init_data_csv(protocol: dict, data_path: Path, seed: int | None) -> int:
    """Write the data CSV header + planned runs."""
    factors = protocol.get("factors") or []
    if len(factors) < 1:
        print("Protocol has no factors.", file=sys.stderr)
        return 0
    levels_per_factor = [f.get("levels") or [] for f in factors]
    cells = list(itertools.product(*levels_per_factor))
    replicates = int(protocol.get("replicates") or 1)

    response = protocol.get("response_variable") or {}
    primary_response_name = response.get("name", "response")
    primary_response_unit = response.get("unit", "")
    primary_col = f"{primary_response_name}_{primary_response_unit}".rstrip("_")

    secondary = protocol.get("secondary_responses") or []
    secondary_cols = []
    for s in secondary:
        if not isinstance(s, dict):
            continue
        name = s.get("name", "secondary")
        unit = s.get("unit", "")
        col = f"{name}_{unit}".rstrip("_") if unit else name
        secondary_cols.append(col)

    factor_cols = []
    for f in factors:
        name = f.get("name", "factor")
        unit = f.get("unit", "")
        col = f"{name}_{unit}".rstrip("_") if unit else name
        factor_cols.append(col)

    # Build planned runs
    rows = []
    run_id = 0
    for cell in cells:
        for rep in range(1, replicates + 1):
            run_id += 1
            rows.append({
                "run_id": run_id,
                **{factor_cols[i]: cell[i] for i in range(len(factors))},
                "replicate": rep,
                primary_col: "",
                **{c: "" for c in secondary_cols},
                "notes": "",
            })

    # Randomize run_order
    if protocol.get("randomize"):
        if seed is not None:
            random.seed(seed)
        order = list(range(1, len(rows) + 1))
        random.shuffle(order)
        for r, o in zip(rows, order):
            r["run_order"] = o
    else:
        for r in rows:
            r["run_order"] = r["run_id"]

    # Sort columns
    header = ["run_id", "run_order"] + factor_cols + ["replicate", primary_col] + secondary_cols + ["notes"]
    data_path.parent.mkdir(parents=True, exist_ok=True)
    with data_path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=header)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return len(rows)


def update_run(
    data_path: Path,
    run_id: int,
    response_kvs: dict[str, str],
    notes: str,
) -> dict | None:
    if not data_path.exists():
        print(f"Data CSV not found: {data_path}. Run --init first.",
              file=sys.stderr)
        return None
    rows = []
    updated = None
    with data_path.open(newline="") as fp:
        reader = csv.DictReader(fp)
        header = reader.fieldnames or []
        for row in reader:
            if int(row["run_id"]) == run_id:
                for k, v in response_kvs.items():
                    if k in row:
                        row[k] = v
                    else:
                        # Allow loose matching on prefix
                        matches = [c for c in header if c.startswith(k)]
                        if matches:
                            row[matches[0]] = v
                if notes:
                    row["notes"] = notes
                updated = row
            rows.append(row)
    if updated is None:
        print(f"run_id {run_id} not found in {data_path}.", file=sys.stderr)
        return None
    with data_path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    return updated


def append_correction_event(
    space_slug: str,
    space_dir: Path | None,
    project: Path,
    study_id: int,
    run: dict,
    response_kvs: dict[str, str],
) -> None:
    if space_dir is None or not space_dir.exists():
        return
    log_dir = space_dir / "corrections"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "raw-measurements.jsonl"
    timestamp = datetime.now(timezone.utc).isoformat()
    for key, value in response_kvs.items():
        try:
            measured = float(value)
        except (TypeError, ValueError):
            continue
        event = {
            "timestamp": timestamp,
            "space": space_slug,
            "packet": str(project.resolve()),
            "source": f"doe-study-{study_id}-run-{run.get('run_id')}",
            "check_id": f"doe-{study_id}-{run.get('run_id')}-{key}",
            "check_name": key,
            "target": None,
            "tolerance": None,
            "unit": "",
            "measured": measured,
            "delta": None,
            "in_tolerance": None,
            "measured_by": "",
            "notes": run.get("notes", ""),
        }
        with log_path.open("a") as fp:
            fp.write(json.dumps(event, sort_keys=True) + "\n")


def find_space_dir(slug: str) -> Path | None:
    candidates = [
        Path(f"./spaces/{slug}"),
        Path(__file__).parent.parent / "spaces" / slug,
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def parse_response_kvs(s: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for chunk in s.split(","):
        chunk = chunk.strip()
        if not chunk or "=" not in chunk:
            continue
        k, _, v = chunk.partition("=")
        out[k.strip()] = v.strip()
    return out


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    protocol_path, data_path = study_paths(args.packet, args.study)

    if args.init:
        if not protocol_path.exists():
            print(f"Protocol not found: {protocol_path}", file=sys.stderr)
            return 2
        protocol = parse_yaml_simple(protocol_path.read_text())
        n = init_data_csv(protocol, data_path, seed=args.seed)
        print(f"Initialized {data_path} with {n} planned runs.")
        return 0

    if args.run_id is None:
        print("--run-id required (or use --init).", file=sys.stderr)
        return 2

    response_kvs = parse_response_kvs(args.response)
    updated = update_run(data_path, args.run_id, response_kvs, args.notes)
    if updated is None:
        return 2

    # Feed the corrections log
    space_dir = find_space_dir(args.space)
    append_correction_event(
        args.space, space_dir, args.packet, args.study, updated, response_kvs,
    )

    print(f"Updated run {args.run_id} in {data_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
