#!/usr/bin/env python3
"""Validate the v4.4 acoustic_law / end_condition / dimension_provenance
columns in a family-spec.csv.

Closes issue #73: catches the "silent wrong physics" class of error that
Round 7 TwinGrid lane Irene exposed in two khaen packets.

This is a focused validator. It does NOT replace `validate_packet.py` —
it is intended to be called from there (or directly by a maker) on the
single concern of acoustic-law correctness.

Exit codes:
  0   — all rows pass; warnings are still printed to stdout
  1   — at least one row failed a hard check
  2   — bad invocation (missing file, malformed CSV)

Usage:
  python3 validate_acoustic_law.py path/to/family-spec.csv
  python3 validate_acoustic_law.py path/to/family-spec.csv --strict
  python3 validate_acoustic_law.py path/to/family-spec.csv --json

The --json flag emits structured findings to stdout; otherwise the
findings are printed in a human-readable form.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


CONTROLLED_VOCABULARY = {
    "open_open",
    "closed_open",
    "stopped_pipe",
    "side_branch_reed",
    "free_reed_coupled_pipe",
    "empirical_only",
    "unknown_requires_measurement",
}

# acoustic_law ↔ end_condition compatibility map
COMPATIBLE_END_CONDITIONS = {
    "open_open":                       {"both_ends_open"},
    "closed_open":                     {"one_end_closed_reed",
                                        "one_end_closed_stopped",
                                        "vented_chamber"},
    "stopped_pipe":                    {"one_end_closed_stopped",
                                        "one_end_closed_reed"},
    "side_branch_reed":                {"both_ends_open"},
    "free_reed_coupled_pipe":          {"both_ends_open"},
    "empirical_only":                  {"n_a_empirical"},
    "unknown_requires_measurement":    {"n_a_empirical",
                                        "both_ends_open",
                                        "one_end_closed_reed",
                                        "one_end_closed_stopped"},
}

DIMENSION_PROVENANCE_VOCAB = {
    "physics_derived",
    "empirically_seeded",
    "measurement_required",
}

# Heuristic: which families need acoustic_law enforcement.
# We treat any family with at least one row whose member_id matches a
# wind/free-reed pattern as a wind/free-reed family. Idiophones (TNG, MAR,
# GLK, KAL, RNS) and string/membrane families are skipped.
WIND_OR_REED_PREFIX_RE = re.compile(
    r"^(KHN|SNG|SHO|HAR|MEL|ACC|BAW|HUL|HRM|CHL|FLU|NAF|TRF|GMS|OCA|UDU|FUJ|DID|PNF|QNA|XIO|TIN|SHK)\b",
    re.IGNORECASE,
)

# Audio constant
SPEED_OF_SOUND_MM_S_AT_20C = 343000.0


@dataclass
class Finding:
    severity: str    # "ERROR" | "WARN" | "INFO"
    row_index: int   # 1-based row number including header? we use 1-based row content
    member_id: str
    code: str
    message: str

    def human(self) -> str:
        loc = f"row {self.row_index}" + (f" ({self.member_id})" if self.member_id else "")
        return f"[{self.severity}] {self.code}  {loc}: {self.message}"


@dataclass
class Report:
    file: str
    rows_total: int = 0
    rows_skipped_non_wind: int = 0
    rows_checked: int = 0
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "ERROR"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "WARN"]


def is_wind_or_reed_family(rows: list[dict]) -> bool:
    for r in rows:
        mid = (r.get("member_id") or "").strip()
        if WIND_OR_REED_PREFIX_RE.match(mid):
            return True
        # Also catch explicit acoustic_law present
        if (r.get("acoustic_law") or "").strip():
            return True
    return False


def predicted_length_from_formula(acoustic_law: str, target_hz: float,
                                  end_correction_mm: float = 8.13) -> float | None:
    """Compute predicted L_geom in mm from the declared acoustic_law.

    end_correction_mm defaults to 8.13 mm (≈ 2 × 0.6 × √(12·12/π) for a
    12 mm × 12 mm channel) which matches the khaen-family reference. This
    is the same default used in the v4 family-aware-design tutorial. The
    1 mm / 0.5 % tolerance is generous enough that other channel sizes do
    not produce false positives.
    """
    if target_hz <= 0:
        return None
    c = SPEED_OF_SOUND_MM_S_AT_20C
    if acoustic_law in ("open_open", "side_branch_reed", "free_reed_coupled_pipe"):
        return c / (2.0 * target_hz) - end_correction_mm
    if acoustic_law in ("closed_open", "stopped_pipe"):
        return c / (4.0 * target_hz) - end_correction_mm / 2.0
    return None


def validate_rows(rows: list[dict], file_label: str = "") -> Report:
    rep = Report(file=file_label, rows_total=len(rows))

    is_wind = is_wind_or_reed_family(rows)

    if not is_wind:
        rep.rows_skipped_non_wind = len(rows)
        rep.findings.append(Finding(
            severity="INFO",
            row_index=0,
            member_id="",
            code="NON_WIND_FAMILY_SKIPPED",
            message=("No wind/free-reed member_id prefix detected and no "
                     "acoustic_law column present; skipping acoustic-law "
                     "enforcement (idiophones, strings, membranes are exempt)."),
        ))
        return rep

    # Check that the column even exists somewhere
    has_acoustic_law_col = any("acoustic_law" in r for r in rows)
    has_end_cond_col = any("end_condition" in r for r in rows)
    has_provenance_col = any("dimension_provenance" in r for r in rows)

    if not has_acoustic_law_col:
        rep.findings.append(Finding(
            severity="ERROR", row_index=0, member_id="",
            code="MISSING_COLUMN_acoustic_law",
            message=("family-spec.csv has no 'acoustic_law' column. "
                     "v4.4 requires it for wind/free-reed families. "
                     "See references/family-aware-design.md."),
        ))
    if not has_end_cond_col:
        rep.findings.append(Finding(
            severity="ERROR", row_index=0, member_id="",
            code="MISSING_COLUMN_end_condition",
            message=("family-spec.csv has no 'end_condition' column. "
                     "v4.4 requires it for wind/free-reed families."),
        ))
    if not has_provenance_col:
        rep.findings.append(Finding(
            severity="ERROR", row_index=0, member_id="",
            code="MISSING_COLUMN_dimension_provenance",
            message=("family-spec.csv has no 'dimension_provenance' column. "
                     "v4.4 requires it for wind/free-reed families."),
        ))
    if rep.errors:
        # No point checking individual rows when the schema is wrong.
        return rep

    for i, row in enumerate(rows, start=1):
        rep.rows_checked += 1
        mid = (row.get("member_id") or "").strip()
        law = (row.get("acoustic_law") or "").strip()
        end_cond = (row.get("end_condition") or "").strip()
        prov = (row.get("dimension_provenance") or "").strip()

        # 1. acoustic_law presence + vocab
        if not law:
            rep.findings.append(Finding(
                severity="ERROR", row_index=i, member_id=mid,
                code="EMPTY_acoustic_law",
                message="acoustic_law is required for every row.",
            ))
            continue
        if law not in CONTROLLED_VOCABULARY:
            rep.findings.append(Finding(
                severity="ERROR", row_index=i, member_id=mid,
                code="INVALID_acoustic_law",
                message=(f"acoustic_law={law!r} is not in the controlled "
                         f"vocabulary: {sorted(CONTROLLED_VOCABULARY)}"),
            ))
            continue

        # 2. end_condition + compatibility
        if not end_cond:
            rep.findings.append(Finding(
                severity="ERROR", row_index=i, member_id=mid,
                code="EMPTY_end_condition",
                message="end_condition is required for every row.",
            ))
        else:
            allowed = COMPATIBLE_END_CONDITIONS.get(law, set())
            if end_cond not in allowed:
                rep.findings.append(Finding(
                    severity="ERROR", row_index=i, member_id=mid,
                    code="INCOMPATIBLE_law_end_condition",
                    message=(f"acoustic_law={law!r} requires "
                             f"end_condition in {sorted(allowed)}, "
                             f"got {end_cond!r}."),
                ))

        # 3. dimension_provenance vocab
        if not prov:
            rep.findings.append(Finding(
                severity="ERROR", row_index=i, member_id=mid,
                code="EMPTY_dimension_provenance",
                message="dimension_provenance is required for every row.",
            ))
        elif prov not in DIMENSION_PROVENANCE_VOCAB:
            rep.findings.append(Finding(
                severity="ERROR", row_index=i, member_id=mid,
                code="INVALID_dimension_provenance",
                message=(f"dimension_provenance={prov!r} not in "
                         f"{sorted(DIMENSION_PROVENANCE_VOCAB)}"),
            ))

        # 4. unknown_requires_measurement → WARN, not fail
        if law == "unknown_requires_measurement":
            rep.findings.append(Finding(
                severity="WARN", row_index=i, member_id=mid,
                code="UNKNOWN_LAW_NEEDS_MEASUREMENT",
                message=("acoustic_law=unknown_requires_measurement; "
                         "packet may ship as a planning packet. Re-run "
                         "after measuring the donor reed and updating "
                         "the row."),
            ))

        # 5. physics_derived → cross-check pipe length vs formula
        if (prov == "physics_derived" and
                law in ("open_open", "side_branch_reed",
                        "free_reed_coupled_pipe", "closed_open",
                        "stopped_pipe")):
            pred_str = (row.get("predicted_L_geom_mm")
                        or row.get("predicted_L_total_mm")
                        or "").strip()
            hz_str = (row.get("target_hz") or "").strip()
            if pred_str and hz_str:
                try:
                    pred = float(pred_str)
                    hz = float(hz_str)
                except ValueError:
                    rep.findings.append(Finding(
                        severity="ERROR", row_index=i, member_id=mid,
                        code="UNPARSEABLE_NUMERIC",
                        message=(f"Could not parse target_hz={hz_str!r} or "
                                 f"predicted_L_geom_mm={pred_str!r}"),
                    ))
                else:
                    expected = predicted_length_from_formula(law, hz)
                    if expected is not None:
                        delta = abs(pred - expected)
                        pct = (delta / expected * 100.0) if expected else 0.0
                        if delta > 1.0 and pct > 0.5:
                            rep.findings.append(Finding(
                                severity="ERROR", row_index=i, member_id=mid,
                                code="PHYSICS_DIMENSION_MISMATCH",
                                message=(
                                    f"acoustic_law={law!r} declares "
                                    f"physics_derived but predicted_L_geom_mm="
                                    f"{pred:.2f} disagrees with formula prediction "
                                    f"{expected:.2f} mm by {delta:.2f} mm "
                                    f"({pct:.2f}%). Tolerance is 1 mm or 0.5%."
                                ),
                            ))

    return rep


def load_family_spec(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=("Validate v4.4 acoustic_law / end_condition / "
                     "dimension_provenance fields in family-spec.csv"))
    p.add_argument("family_spec", type=Path,
                   help="Path to family-spec.csv")
    p.add_argument("--strict", action="store_true",
                   help="Exit 1 on warnings as well as errors.")
    p.add_argument("--json", action="store_true",
                   help="Emit findings as a JSON document on stdout.")
    args = p.parse_args(argv)

    if not args.family_spec.exists():
        print(f"family-spec.csv not found: {args.family_spec}",
              file=sys.stderr)
        return 2

    try:
        rows = load_family_spec(args.family_spec)
    except (OSError, csv.Error) as exc:
        print(f"Could not parse {args.family_spec}: {exc}",
              file=sys.stderr)
        return 2

    rep = validate_rows(rows, file_label=str(args.family_spec))

    if args.json:
        out = {
            "file": rep.file,
            "rows_total": rep.rows_total,
            "rows_skipped_non_wind": rep.rows_skipped_non_wind,
            "rows_checked": rep.rows_checked,
            "errors": [asdict(f) for f in rep.errors],
            "warnings": [asdict(f) for f in rep.warnings],
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"validate_acoustic_law: {rep.file}")
        print(f"  rows_total={rep.rows_total} "
              f"checked={rep.rows_checked} "
              f"skipped_non_wind={rep.rows_skipped_non_wind}")
        for f in rep.findings:
            print("  " + f.human())
        print(f"  → {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")

    if rep.errors:
        return 1
    if args.strict and rep.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
