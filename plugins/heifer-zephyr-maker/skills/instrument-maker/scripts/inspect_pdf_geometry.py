#!/usr/bin/env python3
"""Inspect basic PDF geometry and metadata without external dependencies."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def decode_pdf_string(raw: bytes) -> str:
    return raw.decode("latin1", errors="replace").replace("\\\\", "\\")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="PDF file to inspect")
    args = parser.parse_args()

    data = args.pdf.read_bytes()
    print(f"file: {args.pdf}")
    print(f"size_bytes: {len(data)}")
    print(f"header: {data[:8].decode('latin1', errors='replace')}")

    page_count = len(re.findall(rb"/Type\s*/Page\b", data))
    print(f"rough_page_count: {page_count}")

    for match in re.finditer(rb"/MediaBox\s*\[([^\]]+)\]", data):
        values = [float(x) for x in re.findall(rb"-?\d+(?:\.\d+)?", match.group(1))]
        if len(values) == 4:
            width_pt = values[2] - values[0]
            height_pt = values[3] - values[1]
            print(
                "mediabox: "
                f"{values} pt = {width_pt / 72:.3f} x {height_pt / 72:.3f} in"
            )
        else:
            print(f"mediabox_raw: {match.group(0).decode('latin1', errors='replace')}")

    for key in (b"Title", b"Author", b"Creator", b"Producer"):
        pattern = rb"/" + key + rb"\(([^)]*)\)"
        found = False
        for match in re.finditer(pattern, data):
            found = True
            print(f"{key.decode().lower()}: {decode_pdf_string(match.group(1))}")
        if not found:
            continue

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
