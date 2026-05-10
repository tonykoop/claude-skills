#!/usr/bin/env python3
"""
validate_packet.py
==================

Verifier-as-script. Walk a build packet, check it against the tier
contract, and emit a findings report.

Also validates the structured shop CSV schemas documented in
references/structured-shop-artifacts.md when those files are present.

Usage:
    # Check only (default) — emits findings, doesn't change files
    python3 scripts/validate_packet.py \\
        --packet ./projects/cnc-welcome-sign \\
        --tier 2 \\
        --space maker-nexus

    # Auto-fix what's deterministically fixable
    python3 scripts/validate_packet.py \\
        --packet ./projects/cnc-welcome-sign \\
        --tier 2 \\
        --space maker-nexus \\
        --fix

    # Validate just the space profile (lighter check)
    python3 scripts/validate_packet.py \\
        --check-profile maker-nexus

Exit codes:
    0 = green (or yellow with --fix)
    1 = yellow (only with --check-only)
    2 = red (escalations exist regardless of mode)
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


# ─────────────────── Tier contracts ───────────────────────────

TIER_REQUIRED_FILES: dict[int, list[str]] = {
    1: [
        "design.md",
        "bom.csv",
        "cut-list.csv",
        "op-sequence.md",
        "safety-notes.md",
    ],
    2: [
        "design.md",
        "bom.csv",
        "cut-list.csv",
        "op-sequence.md",
        "safety-notes.md",
        "assembly-manual.md",
        "sourcing.csv",
        "validation.csv",
        "risks.md",
        "README.md",
    ],
    3: [
        "design.md",
        "bom.csv",
        "cut-list.csv",
        "op-sequence.md",
        "safety-notes.md",
        "assembly-manual.md",
        "sourcing.csv",
        "validation.csv",
        "risks.md",
        "README.md",
        "photo-shotlist.md",
        "site/index.html",
    ],
}

# Tier 2/3 also need at least one of these (drawing brief OR drawings):
DRAWING_OPTIONS = ["drawing-brief.md", "drawings"]

# Tier 3 placeholder files — accept either the .placeholder or the
# real artifact. The verifier flags if both are missing.
TIER_3_OPTIONAL_PAIRS = [
    ("deck.pptx", "deck.pptx.placeholder"),
    ("print-packet.pdf", "print-packet.pdf.placeholder"),
]

# Structured artifact schemas documented in
# references/structured-shop-artifacts.md. These are minimum required
# columns; packets may add project-specific columns.
CSV_SCHEMAS: dict[str, list[str]] = {
    "cut-list.csv": [
        "part_id",
        "part_name",
        "qty",
        "material",
        "stock_id",
        "length_in",
        "width_in",
        "thickness_in",
        "grain_dir",
        "kerf_in",
        "notes",
    ],
    "validation.csv": [
        "check_id",
        "check_name",
        "target",
        "tolerance",
        "method",
        "when_to_check",
        "pass_fail",
        "notes",
    ],
    "process-schedule.csv": [
        "step_id",
        "part",
        "process",
        "stock",
        "prep",
        "process_time",
        "working_window",
        "fixture",
        "release_time",
        "go_no_go",
    ],
    "bending-schedule.csv": [
        "step_id",
        "part",
        "option",
        "stock",
        "prep",
        "heat_or_glue_time",
        "bend_or_clamp_window",
        "fixture",
        "release_time",
        "go_no_go",
    ],
}

STEAM_BENDING_TERMS = [
    "steam bend",
    "steam-bend",
    "steam bending",
    "steam-bending",
    "bending-schedule.csv",
]


# ─────────────────── Findings ─────────────────────────────────

@dataclass
class Finding:
    severity: str       # "red" | "yellow" | "green"
    description: str
    location: str = ""
    auto_fix: str | None = None


@dataclass
class Report:
    tier: int
    packet: Path
    space: str
    findings: list[Finding] = field(default_factory=list)
    auto_fixed: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        if any(f.severity == "red" for f in self.findings):
            return "red"
        if any(f.severity == "yellow" for f in self.findings):
            return "yellow"
        return "green"

    def add(self, severity: str, description: str, **kwargs) -> None:
        self.findings.append(
            Finding(severity=severity, description=description, **kwargs),
        )


# ─────────────────── Checks ───────────────────────────────────

def check_tier_completeness(report: Report) -> None:
    """Check that every required file exists."""
    required = TIER_REQUIRED_FILES[report.tier]
    for rel in required:
        path = report.packet / rel
        if not path.exists():
            report.add(
                "red",
                f"Tier {report.tier} requires `{rel}` and it's missing.",
                location=str(path),
                auto_fix="Generate placeholder via "
                "scripts/generate_build_packet.py",
            )

    if report.tier >= 2:
        if not any((report.packet / opt).exists() for opt in DRAWING_OPTIONS):
            report.add(
                "red",
                "Tier 2+ requires either `drawing-brief.md` or a "
                "non-empty `drawings/` directory.",
                location=str(report.packet),
            )


def check_unmarked_unknowns(report: Report) -> None:
    """Scan files for unmarked guesses.

    The expected flag phrases are TBD, assumption, derived estimate.
    A file with zero TBDs *and* obviously-guessed prices/feeds is
    suspicious. v0.1 implements a light scan.
    """
    md_files = list(report.packet.rglob("*.md"))
    for path in md_files:
        if "site/" in str(path):
            continue  # site is auto-generated; skip
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        # Look for common "guessed price" patterns: $NN.NN with no
        # nearby vendor citation. Light heuristic; skips obvious totals.
        # This is intentionally simple in v0.1.
        if "$TBD" in text or "TBD" in text:
            continue  # acceptable
        # No actionable check yet — leave the framework in place.


def check_bom_internal_consistency(report: Report) -> None:
    """bom.csv: line_cost = qty × unit_cost when both are numeric."""
    path = report.packet / "bom.csv"
    if not path.exists():
        return
    try:
        with path.open(newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):
                qty_s = row.get("qty", "").strip()
                unit_s = row.get("unit_cost_usd", "").strip()
                line_s = row.get("line_cost_usd", "").strip()
                if any(s.upper() == "TBD" for s in (qty_s, unit_s, line_s)):
                    continue
                try:
                    qty = float(qty_s)
                    unit = float(unit_s)
                    line = float(line_s)
                except ValueError:
                    continue
                expected = round(qty * unit, 2)
                if abs(expected - line) > 0.01:
                    report.add(
                        "yellow",
                        f"BOM line {i}: line_cost {line} ≠ qty × unit "
                        f"= {expected}",
                        location=f"{path}:row {i}",
                        auto_fix=f"Set line_cost_usd = {expected}",
                    )
    except OSError:
        pass


def _read_packet_text(report: Report) -> str:
    """Return lowercased packet text for lightweight gate checks."""
    chunks: list[str] = []
    for path in report.packet.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".csv", ".txt"}:
            continue
        try:
            chunks.append(path.read_text().lower())
        except (UnicodeDecodeError, OSError):
            continue
    return "\n".join(chunks)


def check_structured_csv_schemas(report: Report) -> None:
    """Check known structured CSV artifacts for parseability and headers."""
    for filename, required in CSV_SCHEMAS.items():
        path = report.packet / filename
        if not path.exists():
            continue
        try:
            with path.open(newline="") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                rows = list(reader)
        except csv.Error as exc:
            report.add(
                "red",
                f"`{filename}` is not parseable CSV: {exc}",
                location=str(path),
            )
            continue
        except OSError:
            continue

        if not header:
            report.add(
                "red",
                f"`{filename}` is empty; expected structured CSV headers.",
                location=str(path),
            )
            continue

        missing = [col for col in required if col not in header]
        if missing:
            report.add(
                "yellow",
                f"`{filename}` missing required column(s): "
                + ", ".join(f"`{col}`" for col in missing),
                location=str(path),
            )

        expected_len = len(header)
        for row_num, row in enumerate(rows, start=2):
            if not row or all(not cell.strip() for cell in row):
                continue
            if len(row) != expected_len:
                report.add(
                    "yellow",
                    f"`{filename}` row {row_num} has {len(row)} fields; "
                    f"header has {expected_len}.",
                    location=f"{path}:row {row_num}",
                )


def check_steam_bending_gates(report: Report) -> None:
    """Steam-bending packets need explicit material/process/safety gates."""
    text = _read_packet_text(report)
    if not any(term in text for term in STEAM_BENDING_TERMS):
        return

    gates = [
        (
            "moisture content gate for bending stock",
            ["moisture", "% mc", " mc "],
        ),
        (
            "compression strap or equivalent anti-fracture strategy",
            ["compression strap"],
        ),
        (
            "working window / transfer-time gate",
            ["working window", "transfer", "60 sec", "60 second"],
        ),
        (
            "breakage threshold for failed bends",
            ["crack", "split", "fracture", "breakage", "tear-out"],
        ),
        (
            "oil-rag or finish fire check",
            ["oil rag", "oil-rag", "spontaneous combustion", "fire"],
        ),
    ]
    for description, terms in gates:
        if not any(term in text for term in terms):
            report.add(
                "yellow",
                f"Steam-bending packet missing {description}.",
                location=str(report.packet),
            )


def check_op_seq_uses_known_tools(report: Report) -> None:
    """op-sequence.md should cite tools that exist in the space profile.

    v0.1: light check — extracts `[tool: <name>]` patterns and warns
    if a name isn't found in the profile's tools.md (we don't load
    YAML in v0.1 to avoid PyYAML dependency).
    """
    op_path = report.packet / "op-sequence.md"
    if not op_path.exists():
        return
    try:
        text = op_path.read_text()
    except OSError:
        return

    # Find space profile dir if it exists
    candidates = [
        Path(f"./spaces/{report.space}"),
        Path(__file__).parent.parent / "spaces" / report.space,
    ]
    profile_dir = next((c for c in candidates if c.exists()), None)
    if profile_dir is None:
        report.add(
            "yellow",
            f"Could not find space profile dir for `{report.space}` "
            f"to verify cited tools.",
            location=str(op_path),
        )
        return

    tools_md = profile_dir / "tools.md"
    if not tools_md.exists():
        return
    try:
        tools_text = tools_md.read_text().lower()
    except OSError:
        return

    cited_tools = re.findall(r"\[tool:\s*([^\],]+)\]", text, re.IGNORECASE)
    for tool in cited_tools:
        tool = tool.strip().lower()
        if tool == "tbd":
            continue
        # crude substring check
        if tool not in tools_text:
            report.add(
                "yellow",
                f"op-sequence cites tool `{tool}` not found in "
                f"`{tools_md}`.",
                location=str(op_path),
            )


def check_risks_have_tests(report: Report) -> None:
    """Tier 2+: every risk in risks.md should have a 'Test:' line."""
    if report.tier < 2:
        return
    risks_path = report.packet / "risks.md"
    if not risks_path.exists():
        return
    try:
        text = risks_path.read_text()
    except OSError:
        return

    # crude: split into per-risk blocks at H3 headers, count blocks
    # without a "Test:" line.
    blocks = re.split(r"^###\s+", text, flags=re.MULTILINE)[1:]
    for i, block in enumerate(blocks, start=1):
        if "**Test:**" not in block and "Test:" not in block:
            title = block.splitlines()[0].strip() if block else f"#{i}"
            if title.lower() in {"considered and dismissed",
                                 "(none yet)"}:
                continue
            report.add(
                "yellow",
                f"Risk `{title}` missing a *Test* line.",
                location=str(risks_path),
            )


# ─────────────────── Auto-fix ─────────────────────────────────

def attempt_fixes(report: Report) -> None:
    """Apply straightforward fixes; mark each as auto_fixed."""
    for finding in list(report.findings):
        if finding.severity != "yellow":
            continue
        if finding.auto_fix and "Set line_cost_usd" in finding.auto_fix:
            # Re-compute line costs in bom.csv
            path = report.packet / "bom.csv"
            try:
                lines = path.read_text().splitlines()
                if len(lines) < 2:
                    continue
                header = lines[0].split(",")
                qty_idx = header.index("qty")
                unit_idx = header.index("unit_cost_usd")
                line_idx = header.index("line_cost_usd")
                rewritten = [lines[0]]
                for raw in lines[1:]:
                    cols = raw.split(",")
                    if len(cols) <= max(qty_idx, unit_idx, line_idx):
                        rewritten.append(raw)
                        continue
                    try:
                        q = float(cols[qty_idx])
                        u = float(cols[unit_idx])
                        cols[line_idx] = f"{round(q * u, 2)}"
                        rewritten.append(",".join(cols))
                    except ValueError:
                        rewritten.append(raw)
                path.write_text("\n".join(rewritten) + "\n")
                report.auto_fixed.append(
                    f"Recomputed line costs in {path.name}"
                )
                report.findings.remove(finding)
            except (OSError, ValueError, IndexError):
                pass


# ─────────────────── Output ───────────────────────────────────

def print_report(report: Report) -> None:
    print(f"# Verifier report — {report.packet} @ Tier {report.tier}")
    print(f"**Space:** {report.space}")
    print(f"**Status:** {report.status}")
    print()

    counts = {"red": 0, "yellow": 0, "green": 0}
    for f in report.findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    print(
        f"Findings: red={counts['red']} yellow={counts['yellow']}"
    )
    print()

    if report.findings:
        print("## Findings")
        for f in sorted(
            report.findings,
            key=lambda x: {"red": 0, "yellow": 1, "green": 2}[x.severity],
        ):
            print(f"- [{f.severity}] {f.description}")
            if f.location:
                print(f"  → {f.location}")
            if f.auto_fix:
                print(f"  → fix: {f.auto_fix}")
        print()

    if report.auto_fixed:
        print("## Auto-fixed")
        for line in report.auto_fixed:
            print(f"- {line}")
        print()


# ─────────────────── Main ─────────────────────────────────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validate a build packet against its tier contract.",
    )
    p.add_argument(
        "--packet",
        type=Path,
        help="Project directory containing the packet.",
    )
    p.add_argument(
        "--tier",
        type=int,
        choices=[1, 2, 3],
        default=1,
    )
    p.add_argument(
        "--space",
        default="home-shop-default",
    )
    p.add_argument(
        "--check-profile",
        help="Validate only the named space profile (skip packet check).",
    )
    p.add_argument(
        "--fix",
        action="store_true",
        help="Apply deterministic auto-fixes.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.check_profile:
        # Lightweight profile check
        candidates = [
            Path(f"./spaces/{args.check_profile}"),
            Path(__file__).parent.parent / "spaces" / args.check_profile,
        ]
        profile_dir = next((c for c in candidates if c.exists()), None)
        if profile_dir is None:
            print(f"Profile not found: {args.check_profile}")
            return 2
        required = ["profile.yaml"]
        missing = [
            f for f in required if not (profile_dir / f).exists()
        ]
        if missing:
            print(f"Missing in {profile_dir}: {missing}")
            return 1
        print(f"Profile {args.check_profile} OK (basic check).")
        return 0

    if args.packet is None:
        print("Either --packet or --check-profile required.", file=sys.stderr)
        return 2

    report = Report(tier=args.tier, packet=args.packet, space=args.space)
    check_tier_completeness(report)
    check_unmarked_unknowns(report)
    check_structured_csv_schemas(report)
    check_bom_internal_consistency(report)
    check_op_seq_uses_known_tools(report)
    check_risks_have_tests(report)
    check_steam_bending_gates(report)

    if args.fix:
        attempt_fixes(report)

    print_report(report)

    if report.status == "red":
        return 2
    if report.status == "yellow":
        return 0 if args.fix else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
