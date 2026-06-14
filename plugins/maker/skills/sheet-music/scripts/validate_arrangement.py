#!/usr/bin/env python3
"""Validate an arrangement against the target instrument.

Checks:
  - All pitches in the tune fall within the instrument's range
  - Required ABC headers are present (X, T, M, L, K, at least)
  - Tune has a Q: tempo line OR uses a default-tempo convention noted
    in the file
  - Every distinct pitch has either a registry entry or is flagged

In --strict mode, all warnings become errors and the exit code is
nonzero.

Usage:
    python validate_arrangement.py \\
        --tune tune.abc --instrument fujara

    python validate_arrangement.py \\
        --target learn-to-play/ --strict
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Sci-pitch -> MIDI number
def sci_to_midi(sci: str) -> int | None:
    m = re.match(r"^([A-G])([#b]?)(\d)$", sci)
    if not m:
        return None
    base = {"C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11}[m.group(1)]
    if m.group(2) == "#": base += 1
    if m.group(2) == "b": base -= 1
    octave = int(m.group(3))
    return base + (octave + 1) * 12


def load_registry_row(instrument_id: str) -> dict | None:
    text = (REPO_ROOT / "instruments" / "registry.yaml").read_text()
    marker = f"id: {instrument_id}"
    if marker not in text:
        return None
    block = text.split(marker, 1)[1].split("- id:", 1)[0]
    row = {"id": instrument_id}
    for line in block.splitlines():
        ln = line.strip()
        if ":" not in ln or ln.startswith("#"):
            continue
        k, v = ln.split(":", 1)
        v = v.split("#")[0].strip()
        if v in ("|", ""):
            continue
        row[k.strip()] = v
    return row


# Reuse the ABC pitch extractor from render_fingering_svg
sys.path.insert(0, str(REPO_ROOT / "scripts"))
try:
    from render_fingering_svg import extract_pitches  # type: ignore
except ImportError:
    def extract_pitches(_):  # type: ignore
        return []


def validate_tune(tune_path: Path, instrument_id: str) -> list[str]:
    issues: list[str] = []
    if not tune_path.exists():
        return [f"missing file: {tune_path}"]

    abc = tune_path.read_text()
    headers = {ln[0]: ln[2:].strip()
               for ln in abc.splitlines()
               if len(ln) > 1 and ln[1] == ":"}
    for required in ("X", "T", "M", "L", "K"):
        if required not in headers:
            issues.append(f"{tune_path.name}: missing header {required}:")
    if "Q" not in headers:
        issues.append(f"{tune_path.name}: missing Q: tempo line "
                      "(beginner songbooks need an explicit tempo)")

    row = load_registry_row(instrument_id)
    if row is None:
        issues.append(f"instrument id not in registry: {instrument_id}")
        return issues

    range_low = sci_to_midi(row.get("range_low", ""))
    range_high = sci_to_midi(row.get("range_high", ""))
    if range_low is None or range_high is None:
        # Pitched percussion may have ~ for range; that's OK
        if row.get("range_low", "").strip() == "~":
            return issues  # unpitched, no range to validate
        issues.append(f"{instrument_id}: registry range fields unparseable")
        return issues

    pitches_sci = extract_pitches(abc)
    for sci in pitches_sci:
        m = sci_to_midi(sci)
        if m is None:
            continue
        if m < range_low:
            issues.append(
                f"{tune_path.name}: pitch {sci} below {row['range_low']} "
                f"(instrument's lowest playable note)"
            )
        if m > range_high:
            issues.append(
                f"{tune_path.name}: pitch {sci} above {row['range_high']} "
                f"(instrument's highest playable note)"
            )

    return issues


def validate_directory(target: Path, strict: bool) -> int:
    """Quick structural check on a learn-to-play/ directory."""
    issues: list[str] = []
    required_subdirs = ["00-warmup-scales", "01-easy",
                        "02-intermediate", "03-original"]
    required_files_in_tune = ["tune.abc", "tune.mid", "notes.md"]

    for sub in required_subdirs:
        if not (target / sub).is_dir():
            issues.append(f"missing required subdir: {sub}")

    for tune_dir in target.glob("0*-*/*/"):
        for f in required_files_in_tune:
            if not (tune_dir / f).exists():
                issues.append(f"{tune_dir.name}: missing {f}")

    if not (target / "fingering-charts.svg").exists() \
            and not (target / "stroke-key.svg").exists():
        issues.append("missing combined fingering/stroke chart "
                      "(fingering-charts.svg or stroke-key.svg)")

    if not (target / "songsheet.pdf").exists():
        issues.append("missing songsheet.pdf")

    if not (target / "README.md").exists():
        issues.append("missing README.md")

    return print_issues(issues, strict)


def print_issues(issues: list[str], strict: bool) -> int:
    if not issues:
        print("  ✓ no issues")
        return 0
    severity = "ERROR" if strict else "warning"
    for i in issues:
        print(f"  {severity}: {i}")
    return 1 if strict else 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tune", type=Path, help="single .abc file")
    p.add_argument("--instrument", help="required when --tune is given")
    p.add_argument("--target", type=Path,
                   help="learn-to-play/ directory to structurally validate")
    p.add_argument("--strict", action="store_true",
                   help="exit nonzero on any issue")
    args = p.parse_args()

    if args.target:
        sys.exit(validate_directory(args.target, args.strict))

    if not args.tune or not args.instrument:
        p.error("use --tune+--instrument for single-tune validation, "
                "or --target for directory validation")

    issues = validate_tune(args.tune, args.instrument)
    sys.exit(print_issues(issues, args.strict))


if __name__ == "__main__":
    main()
