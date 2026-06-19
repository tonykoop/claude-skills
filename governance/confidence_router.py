#!/usr/bin/env python3
"""Human-in-the-loop circuit breaker: confidence-score exception routing.

Implements claude-skills#258 (Epic #254 governance layer).

The QA Auditor assigns a 0–100 confidence score to every reviewed asset.
Routing is exception-only:

* confidence >= threshold AND all gates passed  -> AUTO_ADVANCE
* otherwise (low confidence OR any gate failed)  -> ESCALATE_HUMAN

A **second, immutable barrier** governs publish/deploy actions:
no asset may be pushed to main or published without an explicit
``human_signed_off: true`` in the audit record — regardless of confidence
score or gate status. That barrier is enforced by ``check_deploy_clearance``
and intentionally has no bypass path.

Threshold is read from ``agent-roster.yaml`` under
``confidence_routing.auto_advance_threshold_pct`` (default 90).

CLI:
    python confidence_router.py route   --audit audit.json [--config roster.yaml]
    python confidence_router.py deploy  --audit audit.json [--config roster.yaml]
Exit 0 = proceed; exit 1 = escalate / blocked.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass

from spend_guard import load_roster

# --- status constants --------------------------------------------------------
AUTO_ADVANCE = "AUTO_ADVANCE"    # confidence high + gates green: advance ticket
ESCALATE_HUMAN = "ESCALATE_HUMAN"  # ambiguous or gates failed: ping human
DEPLOY_CLEAR = "DEPLOY_CLEAR"    # human signed off: publish/push allowed
DEPLOY_BLOCKED = "DEPLOY_BLOCKED"  # no human signoff: immutable barrier

DEFAULT_THRESHOLD_PCT = 90


# --- data types --------------------------------------------------------------
@dataclass
class ConfidenceDecision:
    status: str    # AUTO_ADVANCE | ESCALATE_HUMAN
    score: float   # 0–100
    reason: str
    asset_id: str = ""


@dataclass
class DeployDecision:
    status: str    # DEPLOY_CLEAR | DEPLOY_BLOCKED
    reason: str
    asset_id: str = ""


# --- helpers -----------------------------------------------------------------
def _threshold(roster: dict) -> float:
    return float(
        roster.get("confidence_routing", {}).get(
            "auto_advance_threshold_pct", DEFAULT_THRESHOLD_PCT
        )
    )


def _gates_ok(audit: dict) -> bool:
    """True iff all recorded verification gates passed (or none were run)."""
    return audit.get("gates_passed", True) and not audit.get("failed_gates")


# --- public API --------------------------------------------------------------
def route_by_confidence(audit: dict, roster: dict) -> ConfidenceDecision:
    """Route an audited asset to AUTO_ADVANCE or ESCALATE_HUMAN.

    ``audit`` must contain ``confidence_score`` (0–100). Optional fields:
    ``id`` (echo), ``gates_passed`` (bool), ``failed_gates`` (list).

    Selection is deterministic so the same record always routes the same way.
    """
    asset_id = audit.get("id", "")
    raw = audit.get("confidence_score")
    if raw is None:
        return ConfidenceDecision(
            ESCALATE_HUMAN, 0.0, "missing confidence_score field", asset_id
        )

    score = float(raw)
    threshold = _threshold(roster)
    gates_ok = _gates_ok(audit)

    if not gates_ok:
        failed = audit.get("failed_gates", [])
        return ConfidenceDecision(
            ESCALATE_HUMAN,
            score,
            f"gate(s) failed: {', '.join(failed) if failed else 'unspecified'}",
            asset_id,
        )

    if score >= threshold:
        return ConfidenceDecision(
            AUTO_ADVANCE,
            score,
            f"confidence {score:.1f} >= threshold {threshold:.1f} and all gates passed",
            asset_id,
        )

    return ConfidenceDecision(
        ESCALATE_HUMAN,
        score,
        f"confidence {score:.1f} < threshold {threshold:.1f}; human review required",
        asset_id,
    )


def check_deploy_clearance(audit: dict) -> DeployDecision:
    """Immutable deploy barrier: asset may not be published without human signoff.

    This check is intentionally separate from ``route_by_confidence`` and has
    no bypass path. Even an AUTO_ADVANCE asset must pass this gate before any
    push-to-main or publish action occurs.

    ``audit`` must contain ``human_signed_off: true`` to clear the barrier.
    """
    asset_id = audit.get("id", "")
    if audit.get("human_signed_off") is True:
        return DeployDecision(DEPLOY_CLEAR, "human_signed_off confirmed", asset_id)

    return DeployDecision(
        DEPLOY_BLOCKED,
        "no human_signed_off: true in audit record — direct main push / publish is blocked",
        asset_id,
    )


# --- CLI ---------------------------------------------------------------------
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Confidence-score exception routing + deploy barrier (claude-skills#258)"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    for name, help_text in (
        ("route", "Route asset to AUTO_ADVANCE or ESCALATE_HUMAN"),
        ("deploy", "Check immutable deploy/publish clearance"),
    ):
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument("--audit", required=True, help="Path to audit JSON")
        sp.add_argument(
            "--config",
            default=None,
            help="Path to agent-roster.yaml (default: auto-resolve)",
        )
        sp.add_argument("--json", dest="as_json", action="store_true", help="JSON output")

    return p


def _load_audit(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"confidence_router: cannot read audit file: {exc}")


def main(argv: list | None = None) -> int:
    args = _build_parser().parse_args(argv)
    audit = _load_audit(args.audit)

    if args.cmd == "route":
        roster = load_roster(args.config)
        result = route_by_confidence(audit, roster)
        if args.as_json:
            print(json.dumps({"status": result.status, "score": result.score, "reason": result.reason, "asset_id": result.asset_id}))
        else:
            print(f"status:   {result.status}")
            print(f"score:    {result.score:.1f}")
            print(f"reason:   {result.reason}")
            if result.asset_id:
                print(f"asset_id: {result.asset_id}")
        return 0 if result.status == AUTO_ADVANCE else 1

    else:  # deploy
        result = check_deploy_clearance(audit)
        if args.as_json:
            print(json.dumps({"status": result.status, "reason": result.reason, "asset_id": result.asset_id}))
        else:
            print(f"status:   {result.status}")
            print(f"reason:   {result.reason}")
            if result.asset_id:
                print(f"asset_id: {result.asset_id}")
        return 0 if result.status == DEPLOY_CLEAR else 1


if __name__ == "__main__":
    sys.exit(main())
