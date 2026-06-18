#!/usr/bin/env python3
"""Adversarial QA routing: never let the model that made an asset audit it.

Implements claude-skills#256 (Epic #254 governance layer).

The org is adversarial, not flat: every completed asset is routed to a QA
Auditor running a DISTINCT model family from the one that produced it. Routing
is enforced from ``agent-roster.yaml`` (``review_policy`` + per-agent
``can_audit`` + ``model_families``), so the rule lives in the orchestration
config rather than in any single agent's prompt.

Two entry points:

* ``assign_auditor(roster, asset)`` — pick a valid auditor for a fresh asset.
* ``validate_handoff(roster, handoff)`` — verify a creator->auditor handoff
  obeys the policy (used as a merge/release gate).

Family comparison, not version comparison: ``claude-opus-4-6`` and
``claude-opus-4-8`` are the same family and may not audit each other.

CLI:
    python review_router.py assign  --asset asset.json [--config roster.yaml]
    python review_router.py validate --handoff handoff.json [--config roster.yaml]
Exit 0 = routable / valid; exit 1 = blocked / violation.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Optional

from spend_guard import load_roster  # reuse the same config resolver

UNKNOWN_FAMILY = "unknown"


def family_of(roster: dict, model: str) -> str:
    return roster.get("model_families", {}).get(model, UNKNOWN_FAMILY)


@dataclass
class RoutingResult:
    ok: bool
    auditor: Optional[str]
    reason: str


def _eligible_auditors(roster: dict) -> list:
    return [name for name, cfg in roster.get("agents", {}).items() if cfg.get("can_audit")]


def assign_auditor(roster: dict, asset: dict) -> RoutingResult:
    """Choose an auditor whose agent AND model family differ from the creator.

    ``asset`` requires ``creator_agent`` and ``creator_model``. Optional
    ``id`` is echoed for traceability. Selection is deterministic (roster
    order) so the same asset always routes the same way.
    """
    policy = roster.get("review_policy", {})
    if not policy.get("enabled", True):
        return RoutingResult(True, None, "review_policy disabled")

    creator_agent = asset.get("creator_agent")
    creator_model = asset.get("creator_model")
    if not creator_agent or not creator_model:
        return RoutingResult(False, None, "asset missing creator_agent/creator_model")

    creator_family = family_of(roster, creator_model)
    require_agent = policy.get("require_distinct_agent", True)
    require_family = policy.get("require_distinct_family", True)
    agents = roster.get("agents", {})

    for cand in _eligible_auditors(roster):
        if require_agent and cand == creator_agent:
            continue
        cand_model = agents[cand]["model"]
        cand_family = family_of(roster, cand_model)
        if cand_family == UNKNOWN_FAMILY:
            continue  # never trust an auditor whose family we can't verify
        if require_family and cand_family == creator_family:
            continue
        return RoutingResult(
            True, cand,
            f"{creator_agent} ({creator_family}) -> {cand} ({cand_family})",
        )

    # Fail closed: no distinct-model auditor available.
    if policy.get("on_no_auditor", "block") == "block":
        return RoutingResult(False, None, f"no distinct-family auditor for {creator_agent} ({creator_family})")
    return RoutingResult(True, None, "no auditor, policy allows pass-through")


@dataclass
class ValidationResult:
    ok: bool
    violations: list


def validate_handoff(roster: dict, handoff: dict) -> ValidationResult:
    """Gate an existing creator->auditor handoff against the policy.

    ``handoff`` requires ``creator_agent``, ``creator_model``,
    ``auditor_agent``, ``auditor_model``.
    """
    policy = roster.get("review_policy", {})
    violations: list = []

    required = ["creator_agent", "creator_model", "auditor_agent", "auditor_model"]
    missing = [k for k in required if not handoff.get(k)]
    if missing:
        return ValidationResult(False, [f"missing field(s): {', '.join(missing)}"])

    ca, cm = handoff["creator_agent"], handoff["creator_model"]
    aa, am = handoff["auditor_agent"], handoff["auditor_model"]
    cf, af = family_of(roster, cm), family_of(roster, am)

    if policy.get("require_distinct_agent", True) and ca == aa:
        violations.append(f"self-review: creator and auditor are both {ca!r}")
    if policy.get("require_distinct_family", True) and cf == af:
        violations.append(
            f"same model family {cf!r}: {cm!r} audited by {am!r} — cross-model bias blindspot"
        )
    if af == UNKNOWN_FAMILY:
        violations.append(f"auditor model {am!r} has unknown family; cannot certify distinctness")

    # Auditor must actually be allowed to audit.
    auditor_cfg = roster.get("agents", {}).get(aa)
    if auditor_cfg is None:
        violations.append(f"auditor {aa!r} is not in the roster")
    elif not auditor_cfg.get("can_audit"):
        violations.append(f"auditor {aa!r} is not flagged can_audit")

    return ValidationResult(not violations, violations)


# --- CLI --------------------------------------------------------------------
def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(description="Adversarial cross-model QA router")
    ap.add_argument("mode", choices=["assign", "validate"])
    ap.add_argument("--asset", help="asset JSON (assign mode)")
    ap.add_argument("--handoff", help="handoff JSON (validate mode)")
    ap.add_argument("--config", help="path to agent-roster.yaml")
    args = ap.parse_args(argv)

    roster = load_roster(args.config)

    if args.mode == "assign":
        if not args.asset:
            ap.error("assign mode requires --asset")
        with open(args.asset, "r", encoding="utf-8") as fh:
            asset = json.load(fh)
        res = assign_auditor(roster, asset)
        print(json.dumps({"ok": res.ok, "auditor": res.auditor, "reason": res.reason}, indent=2))
        return 0 if res.ok else 1

    with open(args.handoff, "r", encoding="utf-8") as fh:
        handoff = json.load(fh)
    res = validate_handoff(roster, handoff)
    if res.ok:
        print("OK: handoff obeys adversarial-QA policy")
    else:
        print("BLOCKED:")
        for v in res.violations:
            print(f"  - {v}")
    return 0 if res.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
