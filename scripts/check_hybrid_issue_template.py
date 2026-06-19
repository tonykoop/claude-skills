#!/usr/bin/env python3
"""Detect hybrid issues that skipped the skeletal template backbone.

Refs #239 (Epic #235). The hybrid hardware/software/firmware issue template
(`.github/ISSUE_TEMPLATE/hybrid-idea.md`) guarantees every hybrid issue carries
the same backbone: distinct HW / SW / FW / Hybrid discipline sections and an
Expected PDM Artifacts checklist whose required core is the ICD, the Design
Justification README, and a pinned CAD/source version.

This checker makes "missing template usage" *detectable* so non-conforming
issues can be caught in CI, a sprint sweep, or a pre-merge gate. It reads an
issue body from a file, stdin, or a live issue via ``gh`` and reports every
backbone marker that is absent.

The canonical template must itself pass this checker (a drift guard): if the
template changes, update REQUIRED_SECTIONS / REQUIRED_ARTIFACTS to match.

CLI:
    check_hybrid_issue_template.py --body-file issue.md
    check_hybrid_issue_template.py --issue 239        # needs gh + repo access
    cat issue.md | check_hybrid_issue_template.py --stdin

Exit 0 = conforming, 1 = non-conforming, 2 = usage/runtime error.
"""
from __future__ import annotations

import argparse
import subprocess
import sys

# Backbone the template enforces. Matching is case-insensitive substring over
# the issue body, so reworded prose around a marker still counts as present.
REQUIRED_SECTIONS = [
    "## Problem",
    "## Intent",
    "## Constraints",
    "### Hardware (HW)",
    "### Software (SW)",
    "### Firmware (FW)",
    "### Hybrid (system integration)",
    "## Expected PDM Artifacts",
]

# The three required-backbone PDM artifacts named in #239's acceptance criteria.
REQUIRED_ARTIFACTS = [
    "ICD",
    "Design Justification README",
    "CAD / source version",
]


def find_missing(body: str) -> list[str]:
    """Return the backbone markers absent from ``body`` (empty == conforming)."""
    haystack = body.lower()
    missing: list[str] = []
    for marker in REQUIRED_SECTIONS + REQUIRED_ARTIFACTS:
        if marker.lower() not in haystack:
            missing.append(marker)
    return missing


def is_conforming(body: str) -> bool:
    return not find_missing(body)


def load_issue_body(number: str) -> str:
    result = subprocess.run(
        ["gh", "issue", "view", number, "--json", "body", "--jq", ".body"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or "gh issue view failed").strip())
    return result.stdout


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect hybrid issues missing the skeletal template backbone."
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--body-file", help="Path to a file holding the issue body.")
    src.add_argument("--issue", help="Issue number to fetch via gh.")
    src.add_argument("--stdin", action="store_true", help="Read the issue body from stdin.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.body_file:
            with open(args.body_file, "r", encoding="utf-8") as fh:
                body = fh.read()
        elif args.issue:
            body = load_issue_body(args.issue)
        else:
            body = sys.stdin.read()
    except (OSError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    missing = find_missing(body)
    if not missing:
        print("conforming: all hybrid-template backbone markers present")
        return 0
    print("NON-CONFORMING: missing backbone markers:")
    for marker in missing:
        print(f"  - {marker}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
