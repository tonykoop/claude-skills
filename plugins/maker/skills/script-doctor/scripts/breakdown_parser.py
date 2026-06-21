"""
breakdown_parser.py — parse a Markdown script with [TC] annotations into a
logistical-breakdown segment table.

Input format expected in the Markdown script:

    [TC:0:00] [A] Presenter on camera: "Welcome to Inner Compass Yoga..."
    [TC:0:08] [GEN] Opening aerial image: yoga studio at dawn
    [TC:0:15] [TEXT] Channel name lower-third
    ...

Each line with a [TC:...] annotation is one segment.

Usage:
    python3 breakdown_parser.py <script.md>
    python3 breakdown_parser.py <script.md> --output breakdown.md
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


SEGMENT_TYPES = {"A", "B", "GEN", "TEXT", "MUSIC", "SFX", "VO"}

TC_RE = re.compile(r"\[TC:(\d+:\d+(?::\d+)?)\]")
TYPE_RE = re.compile(r"\[(" + "|".join(SEGMENT_TYPES) + r")\]", re.IGNORECASE)
ASSET_RE = re.compile(r"\bAssets?:\s*(.+)", re.IGNORECASE)
MISSING_RE = re.compile(r"\b(WARN|BLOCK)\b", re.IGNORECASE)


@dataclass
class Segment:
    index: int
    tc_in: str
    tc_out: str = ""
    seg_type: str = "B"
    description: str = ""
    assets: str = ""
    props: str = ""
    location: str = "POST"
    missing: str = ""


def parse_tc(tc_str: str) -> int:
    """Return total seconds from MM:SS or HH:MM:SS."""
    parts = tc_str.split(":")
    parts = [int(p) for p in parts]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def seconds_to_tc(secs: int) -> str:
    m, s = divmod(secs, 60)
    return f"{m}:{s:02d}"


def parse_script(text: str) -> list[Segment]:
    segments: list[Segment] = []
    lines = text.splitlines()

    for raw_line in lines:
        line = raw_line.strip()
        tc_match = TC_RE.search(line)
        if not tc_match:
            continue

        tc_in = tc_match.group(1)
        type_match = TYPE_RE.search(line)
        seg_type = type_match.group(1).upper() if type_match else "B"

        # Strip annotation markers to get description
        desc = TC_RE.sub("", line)
        desc = TYPE_RE.sub("", desc)
        desc = desc.strip().lstrip("-").strip()

        asset_match = ASSET_RE.search(line)
        assets = asset_match.group(1).strip() if asset_match else ""

        missing_match = MISSING_RE.search(line)
        missing = missing_match.group(1).upper() if missing_match else ""

        seg = Segment(
            index=len(segments) + 1,
            tc_in=tc_in,
            seg_type=seg_type,
            description=desc,
            assets=assets,
            missing=missing,
        )
        segments.append(seg)

    # Fill TC-out from next segment's TC-in
    for i, seg in enumerate(segments[:-1]):
        seg.tc_out = segments[i + 1].tc_in
    if segments:
        # Last segment TC-out: estimate +5s
        last = segments[-1]
        secs = parse_tc(last.tc_in) + 5
        last.tc_out = seconds_to_tc(secs)

    return segments


def render_markdown_table(segments: list[Segment]) -> str:
    header = (
        "| # | TC-in | TC-out | Dur | Type | Description | Assets needed | "
        "Props | Location | Missing |\n"
        "|---|-------|--------|-----|------|-------------|---------------|"
        "-------|----------|---------|\n"
    )
    rows = []
    for seg in segments:
        try:
            dur = parse_tc(seg.tc_out) - parse_tc(seg.tc_in)
        except Exception:
            dur = 0
        rows.append(
            f"| {seg.index} | {seg.tc_in} | {seg.tc_out} | {dur}s | "
            f"{seg.seg_type} | {seg.description} | {seg.assets} | "
            f"{seg.props} | {seg.location} | {seg.missing} |"
        )
    return header + "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Usage: breakdown_parser.py <script.md> [--output <out.md>]")
        return 1

    script_path = Path(args[0])
    if not script_path.exists():
        print(f"File not found: {script_path}")
        return 1

    output_path: Path | None = None
    if "--output" in args:
        idx = args.index("--output")
        if idx + 1 < len(args):
            output_path = Path(args[idx + 1])

    text = script_path.read_text(encoding="utf-8", errors="replace")
    segments = parse_script(text)

    if not segments:
        print("No [TC:...] annotations found in script — nothing to parse.")
        return 0

    table = render_markdown_table(segments)
    result = f"## Logistical Breakdown\n\n{table}\n"

    if output_path:
        output_path.write_text(result, encoding="utf-8")
        print(f"Written to {output_path}")
    else:
        print(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
