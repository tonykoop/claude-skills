#!/usr/bin/env python3
"""
Script Doctor — main entrypoint (story #426 scaffold).

Runs a script through the three-pass review pipeline and emits a greenlight verdict.
Individual pass logic lives in the per-pass scripts (stories #427–#429).
This scaffold contains stub implementations that emit structured output in the
correct schema so downstream tests and the greenlight gate can be wired up.

Usage:
    python run_review.py --script path/to/script.md [--channel yoga] [--all-passes]
    python run_review.py --script path/to/script.md --pass table-read
    python run_review.py --script path/to/script.md --output review.md
    cat script.md | python run_review.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VALID_CHANNELS = ("yoga", "instrument_maker", "ai_agentic", "consciousness", "wrfcoin", "generic")
VALID_PASSES = ("table-read", "structural-polish", "logistical-breakdown", "greenlight")


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

def _flag(line: int | str, severity: str, message: str) -> dict:
    return {"line": line, "severity": severity, "message": message}


def _result(pass_name: str, score: float, flags: list[dict], **extra) -> dict:
    return {"pass": pass_name, "score": score, "flags": flags, **extra}


# ---------------------------------------------------------------------------
# Pass stubs (replaced by full implementations in stories #427–#429)
# ---------------------------------------------------------------------------

def run_table_read(script: str, channel: str) -> dict:
    """Stub: Phase 1 — table-read pass.

    Full implementation: scripts/table_read.py (story #427).
    Returns the canonical pass schema with placeholder scores and no flags,
    so the greenlight gate and downstream tests have a stable contract.
    """
    word_count = len(script.split())
    estimated_runtime_sec = word_count / 2.5  # ~150wpm spoken

    return _result(
        "table_read",
        score=7.0,
        flags=[],
        archetype=channel,
        readability_score=7.0,
        estimated_runtime_sec=round(estimated_runtime_sec),
        breath_breaks=[],
        hard_to_speak=[],
        pacing_by_section=[],
        archetype_alignment="MATCH",
        stub=True,
    )


def run_structural_polish(script: str, channel: str) -> dict:
    """Stub: Phase 2 — structural polish pass.

    Full implementation: scripts/structural_polish.py (story #428).
    """
    return _result(
        "structural_polish",
        score=7.0,
        flags=[],
        hook_score=7.0,
        closing_score=7.0,
        on_the_nose=[],
        retention_dips=[],
        transition_gaps=[],
        overall_summary="(stub — full analysis in story #428)",
        stub=True,
    )


def run_logistical_breakdown(script: str, channel: str) -> dict:
    """Stub: Phase 3 — logistical breakdown pass.

    Full implementation: scripts/logistical_breakdown.py (story #429).
    """
    return _result(
        "logistical_breakdown",
        score=7.0,
        flags=[],
        segments=[],
        missing_assets=[],
        props=[],
        locations=[],
        producibility_score=7.0,
        stub=True,
    )


def run_greenlight(passes: list[dict]) -> dict:
    """Compute greenlight verdict from pass results.

    Collects all BLOCKER-severity flags from the three passes, computes the
    composite score, and returns the verdict dict.
    """
    scores = [p["score"] for p in passes if "score" in p]
    composite = round(sum(scores) / len(scores), 1) if scores else 0.0

    blockers = [
        f for p in passes for f in p.get("flags", []) if f.get("severity") == "blocker"
    ]

    if blockers:
        verdict = "FAIL"
    elif composite >= 8.0:
        verdict = "PASS"
    elif composite >= 6.0:
        verdict = "PASS"  # CONDITIONAL maps to PASS with warnings when no blockers
    else:
        verdict = "FAIL"

    return {
        "pass": "greenlight",
        "composite_score": composite,
        "greenlight": verdict,
        "blockers": blockers,
        "override": False,
        "ready_line": f"READY: {'YES' if verdict == 'PASS' else 'NO'} — composite {composite}/10",
        "flags": blockers,
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

_DIVIDER = "═" * 42
_THIN = "─" * 42


def _render_review(passes: list[dict], greenlight: dict, fmt: str = "md") -> str:
    """Render the full multi-pass review as Markdown."""
    lines: list[str] = []

    lines.append("# Script Doctor Review\n")

    for p in passes:
        pass_name = p.get("pass", "unknown").replace("_", "-").title()
        score = p.get("score", "—")
        stub_note = "  _(stub — full analysis pending)_" if p.get("stub") else ""
        lines.append(f"## {pass_name} Pass — {score}/10{stub_note}\n")
        flags = p.get("flags", [])
        if flags:
            for f in flags:
                tier = f.get("severity", "note").upper()
                msg = f.get("message", "")
                loc = f.get("line", "")
                lines.append(f"- **{tier}** [{loc}]: {msg}")
        else:
            lines.append("_No flags._")
        lines.append("")

    lines.append(f"\n{_DIVIDER}")
    lines.append(f"GREENLIGHT VERDICT: **{greenlight['greenlight']}**")
    lines.append(f"Composite score: {greenlight['composite_score']}/10")
    lines.append(_DIVIDER)
    if greenlight["blockers"]:
        for b in greenlight["blockers"]:
            lines.append(f"BLOCKER  [ ] {b.get('message', '')}")
    lines.append("")
    lines.append(greenlight["ready_line"])
    lines.append("")
    lines.append(
        "_Human-override note: This verdict is advisory. The director may proceed "
        "with a FAIL verdict by noting the override and accepting the flagged risks._"
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Script Doctor — pre-production review")
    p.add_argument("--script", help="Path to the script file (reads stdin if omitted)")
    p.add_argument(
        "--channel",
        default="generic",
        choices=VALID_CHANNELS,
        help="Channel archetype profile to apply",
    )
    p.add_argument(
        "--pass",
        dest="single_pass",
        choices=VALID_PASSES,
        help="Run a single pass only",
    )
    p.add_argument(
        "--all-passes",
        action="store_true",
        default=True,
        help="Run all three passes + greenlight (default)",
    )
    p.add_argument("--output", help="Write review to this file (stdout if omitted)")
    p.add_argument(
        "--json",
        dest="json_out",
        action="store_true",
        help="Emit raw JSON instead of Markdown",
    )
    return p.parse_args(argv)


def review(script: str, channel: str = "generic",
           single_pass: str | None = None) -> dict[str, Any]:
    """Run the review pipeline and return the result dict.

    This is the library interface; the CLI wraps this function.
    """
    passes: list[dict] = []

    run_map = {
        "table-read": lambda: run_table_read(script, channel),
        "structural-polish": lambda: run_structural_polish(script, channel),
        "logistical-breakdown": lambda: run_logistical_breakdown(script, channel),
    }

    if single_pass and single_pass in run_map:
        passes = [run_map[single_pass]()]
    elif single_pass == "greenlight":
        # Greenlight requires all passes — run all first
        passes = [fn() for fn in run_map.values()]
    else:
        passes = [fn() for fn in run_map.values()]

    gl = run_greenlight(passes)
    return {"passes": passes, "greenlight": gl}


def main(argv=None) -> int:
    args = _parse_args(argv)

    if args.script:
        path = Path(args.script)
        if not path.exists():
            print(f"error: script not found: {path}", file=sys.stderr)
            return 1
        script = path.read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        script = sys.stdin.read()
    else:
        print("error: provide --script or pipe script via stdin", file=sys.stderr)
        return 1

    result = review(script, channel=args.channel, single_pass=args.single_pass)

    if args.json_out:
        output = json.dumps(result, indent=2)
    else:
        output = _render_review(result["passes"], result["greenlight"])

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"review written to {args.output}")
    else:
        print(output)

    return 0 if result["greenlight"]["greenlight"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
