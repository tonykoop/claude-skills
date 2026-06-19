#!/usr/bin/env python3
"""Validate Manufacturing Capability Index rows + run the scarcity triage.

First concrete artifact for claude-skills#205 (Planetary Element Inventory +
Manufacturing Capability Index). Two row types, each with a JSON Schema in
``schema/``:

* **process capability row** — a process's spatial / kinematic / energetic /
  tolerance envelope at a point in time.
* **element inventory row** — an element's crustal abundance + run-rate, distilled
  into a scarcity penalty.

The point of the index is that an AI design agent queries it *before* committing
geometry: reject "coat it in gold for EMI" before it reaches the physical grader
and force an abundant-atom substitute. This module is the executable sketch of
that gate, plus a lightweight (stdlib-only) JSON-Schema validator so the rows
stay well-formed without adding a ``jsonschema`` dependency.

CLI::

    python validate.py            # validate the bundled sample rows + demo the gate
    python validate.py --process-data p.json --element-data e.json

Exit 0 = all rows valid; exit 1 = at least one schema violation.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SCHEMA_DIR = HERE / "schema"
DATA_DIR = HERE / "data"

# Abundance reference points (log10 ppm) for the scarcity penalty. ~10^5 ppm is
# "abundant" (Al/Fe class), ~10^-3 ppm is "vanishingly scarce" (precious class).
_LOG_ABUNDANT = 5.0
_LOG_SCARCE = -3.0

# A scarcity penalty at/above this blocks a design and forces a substitute.
DEFAULT_SCARCITY_GATE = 0.7

# The fields a MakerBench seed can enforce against a real grader TODAY (static,
# measurable, vendor-published) versus fields that are aspirational because they
# need live telemetry or under-load measurement we do not have yet.
GATEABLE_TODAY = {
    "process": ["min_feature_mm", "max_envelope_mm", "tolerance_floor_mm", "states_of_matter"],
    "element": ["crustal_abundance_ppm", "scarcity_penalty", "abundant_substitutes"],
}
ASPIRATIONAL = {
    "process": ["kinematic_cadence", "energetic_threshold_j_per_cm3"],
    "element": ["annual_run_rate_tonnes"],
}


# --- minimal JSON-Schema validator (subset) ---------------------------------

def validate_against_schema(instance: Any, schema: dict, path: str = "$") -> list[str]:
    """Validate ``instance`` against the draft-07 subset our schemas use.

    Supports: type, required, properties, additionalProperties:false, items,
    enum, pattern, minLength, minItems, minimum/maximum/exclusiveMinimum.
    Returns a list of human-readable error strings (empty = valid).
    """
    errors: list[str] = []
    t = schema.get("type")
    if t == "object":
        if not isinstance(instance, dict):
            return [f"{path}: expected object, got {type(instance).__name__}"]
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required field '{req}'")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}: unexpected field '{key}'")
        for key, subschema in props.items():
            if key in instance:
                errors.extend(validate_against_schema(instance[key], subschema, f"{path}.{key}"))
    elif t == "array":
        if not isinstance(instance, list):
            return [f"{path}: expected array, got {type(instance).__name__}"]
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: needs >= {schema['minItems']} item(s)")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                errors.extend(validate_against_schema(item, item_schema, f"{path}[{i}]"))
    elif t == "number":
        if isinstance(instance, bool) or not isinstance(instance, (int, float)):
            return [f"{path}: expected number, got {type(instance).__name__}"]
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            errors.append(f"{path}: {instance} <= exclusiveMinimum {schema['exclusiveMinimum']}")
    elif t == "boolean":
        if not isinstance(instance, bool):
            errors.append(f"{path}: expected boolean")
    elif t == "string":
        if not isinstance(instance, str):
            return [f"{path}: expected string, got {type(instance).__name__}"]
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} does not match /{schema['pattern']}/")
        if "enum" in schema and instance not in schema["enum"]:
            errors.append(f"{path}: {instance!r} not in {schema['enum']}")
    # enum on non-string scalars
    if "enum" in schema and t != "string" and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in {schema['enum']}")
    return errors


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


# --- domain logic -----------------------------------------------------------

def derive_scarcity_penalty(crustal_abundance_ppm: float) -> float:
    """Map crustal abundance (ppm) to a 0..1 scarcity penalty on a log scale."""
    if crustal_abundance_ppm <= 0:
        return 1.0
    log_ppm = math.log10(crustal_abundance_ppm)
    raw = (_LOG_ABUNDANT - log_ppm) / (_LOG_ABUNDANT - _LOG_SCARCE)
    return round(max(0.0, min(1.0, raw)), 3)


def scarcity_penalty_of(row: dict) -> float:
    """Stored penalty if present, else derived from crustal abundance."""
    if isinstance(row.get("scarcity_penalty"), (int, float)):
        return float(row["scarcity_penalty"])
    return derive_scarcity_penalty(row["crustal_abundance_ppm"])


def gate_material(row: dict, gate: float = DEFAULT_SCARCITY_GATE) -> dict:
    """Allow/reject a material by scarcity, suggesting abundant substitutes.

    This is the pre-grader triage: a scarce element is rejected before geometry
    reaches the physical grader, with substitutes the agent should try instead.
    """
    penalty = scarcity_penalty_of(row)
    allowed = penalty < gate
    subs = row.get("abundant_substitutes", [])
    if allowed:
        reason = f"{row['symbol']} penalty {penalty} < gate {gate}: allowed"
    elif subs:
        reason = f"{row['symbol']} penalty {penalty} >= gate {gate}: reject, prefer {', '.join(subs)}"
    else:
        reason = f"{row['symbol']} penalty {penalty} >= gate {gate}: reject, no substitute on file"
    return {"symbol": row["symbol"], "penalty": penalty, "allowed": allowed,
            "substitutes": subs, "reason": reason}


def gateable_today(kind: str) -> list[str]:
    """The fields a MakerBench seed can gate on today for a row ``kind``."""
    return GATEABLE_TODAY[kind]


# --- validation entry points ------------------------------------------------

def validate_rows(rows: list, schema: dict, label: str) -> list[str]:
    errors: list[str] = []
    for i, row in enumerate(rows):
        for err in validate_against_schema(row, schema):
            errors.append(f"{label}[{i}] {err}")
    return errors


def _load(path: Path) -> list:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else [data]


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate MCI rows + scarcity triage (#205)")
    ap.add_argument("--process-data", default=str(DATA_DIR / "sample_process_rows.json"))
    ap.add_argument("--element-data", default=str(DATA_DIR / "sample_element_rows.json"))
    ap.add_argument("--gate", type=float, default=DEFAULT_SCARCITY_GATE)
    args = ap.parse_args(argv)

    proc_schema = load_schema("process_capability_row.schema.json")
    elem_schema = load_schema("element_inventory_row.schema.json")
    proc_rows = _load(Path(args.process_data))
    elem_rows = _load(Path(args.element_data))

    errors = validate_rows(proc_rows, proc_schema, "process")
    errors += validate_rows(elem_rows, elem_schema, "element")

    print(f"Process rows: {len(proc_rows)}   Element rows: {len(elem_rows)}")
    print(f"Gateable-today process fields:  {', '.join(gateable_today('process'))}")
    print(f"Gateable-today element fields:   {', '.join(gateable_today('element'))}")
    print("\nScarcity triage (gate = %.2f):" % args.gate)
    for row in elem_rows:
        print("  " + gate_material(row, args.gate)["reason"])

    if errors:
        print("\nSCHEMA ERRORS:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nAll rows valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
