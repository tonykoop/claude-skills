#!/usr/bin/env python3
"""Human-in-the-loop circuit breaker + confidence-score exception routing.

Implements claude-skills#258 (Epic #254 governance layer).

Exception-only review: the cross-model QA auditor (``review_router.py``) attaches
a *confidence score* to its verdict. If the linters pass and confidence clears
the bar, the ticket auto-advances untouched; only the ambiguous ~10% page a
human. The point is to spend scarce human hours on the hard cases — and *never*
let automation cross a deploy boundary unsupervised.

Two enforcement surfaces, both driven by ``agent-roster.yaml``:

1. **Immutable state barriers** — a hardcoded floor of protected actions /
   branches (``IMMUTABLE_PROTECTED_*``). Config may *add* to the protected set
   but can never shrink it below this floor, so an agent that gains write
   access to the roster still cannot edit its way onto ``main`` or past a
   ``publish``/``deploy`` without a human signature. No confidence score, no
   matter how high, crosses these.

2. **Confidence-threshold routing** — for non-protected actions: linters pass
   AND confidence >= ``confidence_auto_advance`` -> ``AUTO_ADVANCE``; otherwise
   the verdict is ``ESCALATE`` and the human is pinged exactly once.

A valid cross-model handoff is a precondition for *any* auto-advance: if the
audit was self/same-family (``review_router.validate_handoff`` fails), the
confidence is untrustworthy and the case escalates regardless of its value.

CLI:
    python circuit_breaker.py decide --verdict verdict.json [--config roster.yaml]
Exit 0 = AUTO_ADVANCE (safe to proceed unattended); exit 1 = a human is needed
(ESCALATE or BLOCK).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Optional

from review_router import validate_handoff
from spend_guard import load_roster  # shared config resolver

# --- verdict states ---------------------------------------------------------
AUTO_ADVANCE = "AUTO_ADVANCE"  # safe to merge/advance with no human in the loop
ESCALATE = "ESCALATE"          # ambiguous ~10%: ping the human, await review
BLOCK = "BLOCK"                # immutable barrier hit: human signature required

# Statuses that require a human before anything proceeds.
NEEDS_HUMAN = frozenset({ESCALATE, BLOCK})

# -----------------------------------------------------------------------------
# Immutable floor. These are hardcoded in the binary, NOT just the YAML, so a
# misconfigured (or maliciously edited) roster cannot remove them. Config can
# only ever ADD to the protected set via circuit_breaker.protected_*.
# -----------------------------------------------------------------------------
IMMUTABLE_PROTECTED_ACTIONS = frozenset({
    "push_main", "merge_to_main", "publish", "deploy", "release", "force_push",
})
IMMUTABLE_PROTECTED_BRANCHES = frozenset({"main", "master"})

DEFAULT_CONFIDENCE_BAR = 0.90
DEFAULT_ESCALATION_HANDLE = "@tonykoop"


def _cb_config(roster: dict) -> dict:
    return roster.get("circuit_breaker", {}) or {}


def protected_actions(roster: dict) -> frozenset:
    """Immutable floor UNION any extra actions the roster opts into."""
    extra = _cb_config(roster).get("protected_actions", []) or []
    return IMMUTABLE_PROTECTED_ACTIONS | {str(a) for a in extra}


def protected_branches(roster: dict) -> frozenset:
    extra = _cb_config(roster).get("protected_branches", []) or []
    return IMMUTABLE_PROTECTED_BRANCHES | {str(b) for b in extra}


def is_protected(roster: dict, action: Optional[str], target_branch: Optional[str]) -> bool:
    """True if this verdict targets a deploy boundary that needs a human."""
    if action and action in protected_actions(roster):
        return True
    if target_branch and target_branch in protected_branches(roster):
        return True
    return False


def _has_human_signature(verdict: dict) -> bool:
    """A signature must name who signed — the orchestrator may only populate
    this from a real human action (out-of-band), never an agent's own output."""
    sig = verdict.get("human_signature")
    if not sig:
        return False
    if isinstance(sig, dict):
        return bool(sig.get("signed_by"))
    return bool(str(sig).strip())


@dataclass
class Decision:
    status: str
    auto_advance: bool
    reasons: list = field(default_factory=list)
    escalation: Optional[dict] = None  # ping payload when a human is needed

    @property
    def needs_human(self) -> bool:
        return self.status in NEEDS_HUMAN


def _escalation(roster: dict, verdict: dict, kind: str, reason: str) -> dict:
    """Build the GitHub @mention / inbox alert for the ambiguous case."""
    handle = _cb_config(roster).get("escalation_handle", DEFAULT_ESCALATION_HANDLE)
    return {
        "ping": handle,
        "kind": kind,                      # "escalate" | "signature_required"
        "asset_id": verdict.get("asset_id"),
        "action": verdict.get("action"),
        "target_branch": verdict.get("target_branch"),
        "creator_agent": verdict.get("creator_agent"),
        "auditor_agent": verdict.get("auditor_agent"),
        "confidence": verdict.get("confidence"),
        "reason": reason,
    }


def decide(roster: dict, verdict: dict) -> Decision:
    """Route an audited verdict to AUTO_ADVANCE, ESCALATE, or BLOCK.

    ``verdict`` fields:
      creator_agent, creator_model, auditor_agent, auditor_model  (handoff)
      confidence       float in [0, 1]   — the auditor's confidence
      linters_passed   bool
      action           str  — the operation being gated (e.g. "merge_pr")
      target_branch    str  — where it lands
      asset_id         str  — traceability (optional)
      human_signature  truthy/{signed_by} — present only after manual signoff
    """
    cfg = _cb_config(roster)
    if not cfg.get("enabled", True):
        # Breaker disabled: still honour the immutable deploy barrier so the
        # kill-switch can never be turned off for protected actions.
        if is_protected(roster, verdict.get("action"), verdict.get("target_branch")) \
                and not _has_human_signature(verdict):
            return Decision(BLOCK, False,
                            ["circuit_breaker disabled, but a human signature is "
                             "still mandatory for a protected action"],
                            _escalation(roster, verdict, "signature_required",
                                        "protected boundary — manual signoff required"))
        return Decision(AUTO_ADVANCE, True, ["circuit_breaker disabled"])

    reasons: list = []

    # 0. The cross-model audit must be trustworthy before its confidence counts.
    handoff_ok = validate_handoff(roster, verdict)
    if not handoff_ok.ok:
        reasons.append("cross-model handoff invalid: " + "; ".join(handoff_ok.violations))
        return Decision(ESCALATE, False, reasons,
                        _escalation(roster, verdict, "escalate",
                                    "untrustworthy audit (handoff failed the QA gate)"))

    protected = is_protected(roster, verdict.get("action"), verdict.get("target_branch"))
    signed = _has_human_signature(verdict)

    # 1. Immutable barrier — checked BEFORE confidence so no score can bypass it.
    if protected and not signed:
        reasons.append(
            f"protected action {verdict.get('action')!r} / branch "
            f"{verdict.get('target_branch')!r} — human signature required "
            f"(confidence {verdict.get('confidence')} cannot override)"
        )
        return Decision(BLOCK, False, reasons,
                        _escalation(roster, verdict, "signature_required",
                                    "deploy boundary — manual signoff required"))
    if protected and signed:
        reasons.append("protected action carries a valid human signature")
        return Decision(AUTO_ADVANCE, True, reasons)

    # 2. Non-protected: confidence + linters route the exception-only review.
    if cfg.get("require_linters_pass", True) and not verdict.get("linters_passed", False):
        reasons.append("linters did not pass")
        return Decision(ESCALATE, False, reasons,
                        _escalation(roster, verdict, "escalate", "linters failed"))

    bar = float(cfg.get("confidence_auto_advance", DEFAULT_CONFIDENCE_BAR))
    conf = verdict.get("confidence")
    try:
        conf = float(conf)
    except (TypeError, ValueError):
        reasons.append(f"confidence {conf!r} is not a number")
        return Decision(ESCALATE, False, reasons,
                        _escalation(roster, verdict, "escalate", "missing/invalid confidence"))
    if not 0.0 <= conf <= 1.0:
        reasons.append(f"confidence {conf} outside [0, 1]")
        return Decision(ESCALATE, False, reasons,
                        _escalation(roster, verdict, "escalate", "confidence out of range"))

    if conf >= bar:
        reasons.append(f"confidence {conf:.2f} >= bar {bar:.2f} and linters passed")
        return Decision(AUTO_ADVANCE, True, reasons)

    reasons.append(f"confidence {conf:.2f} < bar {bar:.2f} — ambiguous, human reviews")
    return Decision(ESCALATE, False, reasons,
                    _escalation(roster, verdict, "escalate",
                                f"low confidence ({conf:.2f} < {bar:.2f})"))


# --- CLI --------------------------------------------------------------------
def _render(decision: Decision) -> str:
    lines = [f"Circuit-breaker verdict: {decision.status}"]
    for r in decision.reasons:
        lines.append(f"  - {r}")
    if decision.escalation:
        e = decision.escalation
        lines.append(f"  >> PING {e['ping']}: {e['reason']} (asset {e['asset_id']})")
    return "\n".join(lines)


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(description="Human-in-the-loop circuit breaker")
    ap.add_argument("mode", choices=["decide"])
    ap.add_argument("--verdict", required=True, help="path to verdict JSON")
    ap.add_argument("--config", help="path to agent-roster.yaml")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args(argv)

    roster = load_roster(args.config)
    with open(args.verdict, "r", encoding="utf-8") as fh:
        verdict = json.load(fh)
    decision = decide(roster, verdict)

    if args.json:
        print(json.dumps({
            "status": decision.status,
            "auto_advance": decision.auto_advance,
            "reasons": decision.reasons,
            "escalation": decision.escalation,
        }, indent=2))
    else:
        print(_render(decision))
    return 0 if decision.auto_advance else 1


if __name__ == "__main__":
    raise SystemExit(main())
