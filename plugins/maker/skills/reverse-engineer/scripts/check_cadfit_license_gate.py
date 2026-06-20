#!/usr/bin/env python3
"""Validate the CADFit setup/license gate reference."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_PHRASES = [
    "CC BY-NC 4.0",
    "do not vendor CADFit code",
    "patent and trademark rights are not licensed",
    "provisional patent application",
    "Ghadi Nehme, Eamon Whalen, and Faez Ahmed",
    "arXiv:2605.01171",
    "Runtime Availability Matrix",
    "Codex CLI sandbox",
    "Mobile / zip-uploaded skill host",
    "real scan/mesh already exists",
]


def missing_phrases(text: str) -> list[str]:
    return [phrase for phrase in REQUIRED_PHRASES if phrase not in text]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check CADFit license gate reference completeness.")
    parser.add_argument(
        "reference",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "references" / "cadfit-setup-license.md",
    )
    args = parser.parse_args(argv)

    text = args.reference.read_text(encoding="utf-8")
    missing = missing_phrases(text)
    if missing:
        for phrase in missing:
            print(f"missing: {phrase}", file=sys.stderr)
        return 1
    print("cadfit license gate: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
