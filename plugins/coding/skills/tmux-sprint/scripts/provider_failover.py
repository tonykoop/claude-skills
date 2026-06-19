#!/usr/bin/env python3
"""Provider-failover detection + state for budget-exhausted sprinter panes.

Implements the low-risk first slice of claude-skills#166 (see
``references/provider-failover.md``): the manager can recognise when a pane has
exhausted its provider, record a structured failover candidate, and roll those
records into the morning summary — WITHOUT sending any pane keystrokes. The
actual same-pane CLI swap (C-c / exit / relaunch / probe) lands in a later PR on
top of this validated detection/state layer.

Three pure pieces, all stdlib (matching ``twingrid_matrix.py``):

* ``detect_exhaustion(text)`` — classify a pane capture into a ``failure_reason``
  from the contract's vocabulary, or ``None`` when the pane shows only transient
  noise (approval prompts, local test failures, compaction) that must NOT
  trigger a provider migration.
* ``failover_candidate(...)`` — given the detection plus the lane's identity and
  the configured fallback order, build the round-state provider record and pick
  the next provider to try (or ``manager-absorb`` when the order is exhausted).
* ``render_summary(records)`` — the ``## Provider Failover`` morning-summary
  table.

CLI::

    # classify one pane capture and emit a candidate record
    provider_failover.py detect --capture pane.txt \
        --pane sprint:0.3 --persona dan --lane core4-1511 --provider codex

    # render the morning-summary table from a JSON list of records
    provider_failover.py summary --records records.json

``detect`` exits 0 when the pane is healthy and 1 when a failover candidate is
found — so a manager loop can branch on the exit code without parsing stdout.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Any, Optional

# --- config -----------------------------------------------------------------

# Defaults mirror references/provider-failover.md so the script and the contract
# never drift. A round may override `order` (e.g. a user-requested runtime mix).
DEFAULT_CONFIG: dict[str, Any] = {
    "order": ["codex", "claude", "gemini", "manager-absorb"],
    "probe_prompt": "Say READY and exit.",
    "probe_success_pattern": r"\bREADY\b",
    "launch_timeout_seconds": 20,
    "probe_timeout_seconds": 30,
}

# The terminal step in any fallback order: stop swapping, hand the lane to the
# manager's own context.
MANAGER_ABSORB = "manager-absorb"


def resolve_config(overrides: Optional[dict] = None) -> dict[str, Any]:
    """Merge user overrides onto the contract defaults (shallow)."""
    cfg = dict(DEFAULT_CONFIG)
    if overrides:
        # Accept either a bare mapping or one nested under `provider_failover`.
        if "provider_failover" in overrides and isinstance(overrides["provider_failover"], dict):
            overrides = overrides["provider_failover"]
        for key, value in overrides.items():
            if value is not None:
                cfg[key] = value
    if not cfg.get("order"):
        cfg["order"] = list(DEFAULT_CONFIG["order"])
    return cfg


def load_config_file(path: pathlib.Path) -> dict[str, Any]:
    """Load a config file (YAML if PyYAML is present, else JSON). Empty on miss."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    try:
        import yaml  # optional; tmux hosts usually have it
        data = yaml.safe_load(raw)
    except Exception:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {}
    return data if isinstance(data, dict) else {}


# --- exhaustion detection ---------------------------------------------------

# Ordered most-specific -> least-specific. Weekly-budget exhaustion is checked
# before a generic rate-limit so "weekly limit reached" is not mislabelled as a
# transient rate-limit prompt. Each value is a list of case-insensitive regexes.
EXHAUSTION_PATTERNS: list[tuple[str, list[str]]] = [
    ("weekly_budget_exhausted", [
        r"weekly\s+(limit|quota|budget)",
        r"weekly\s+limit\s+reached",
        r"out of (your )?weekly",
        r"resets?\s+(next week|on \w+day|in \d+ days)",
        r"weekly usage",
    ]),
    ("provider_auth_blocked", [
        r"not\s+authenticated",
        r"please (log ?in|sign ?in|authenticate)",
        r"login required",
        r"unauthorized",
        r"\b401\b",
        r"\b403\b",
    ]),
    ("provider_cli_missing", [
        r"command not found",
        r"No such file or directory",
        r"not installed",
    ]),
    ("rate_limit_prompt", [
        r"rate[\s-]?limit",
        r"too many requests",
        r"\b429\b",
        r"slow down",
    ]),
    # Generic provider-credit/quota exhaustion, lowest priority.
    ("weekly_budget_exhausted", [
        r"no credits",
        r"out of credits",
        r"quota exceeded",
        r"usage limit",
        r"insufficient_quota",
    ]),
]

# Lines that look alarming but are NOT provider exhaustion. If a capture matches
# only these and no exhaustion family, the pane is healthy-for-failover-purposes
# and the manager should keep using its normal supervise/restart/dispatch flow.
TRANSIENT_PATTERNS: list[str] = [
    r"Do you want to allow",
    r"requires approval",
    r"approve this command",
    r"waiting for approval",
    r"continue\? \[y/N\]",
    r"\bFAILED\b.*test",
    r"compaction",
    r"watching for changes",
]


def _matches_any(text: str, patterns: list[str]) -> Optional[str]:
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return pat
    return None


def detect_exhaustion(text: str) -> Optional[str]:
    """Return the ``failure_reason`` for a pane capture, or ``None`` if healthy.

    Exhaustion families always win over transient noise: a pane can show an
    approval prompt *and* a weekly-budget message; the budget message is the one
    that demands a provider migration.
    """
    if not text:
        return None
    for reason, patterns in EXHAUSTION_PATTERNS:
        if _matches_any(text, patterns):
            return reason
    return None


def is_transient_only(text: str) -> bool:
    """True when the capture shows transient noise and no exhaustion family."""
    if detect_exhaustion(text) is not None:
        return False
    return _matches_any(text, TRANSIENT_PATTERNS) is not None


# --- next-provider selection ------------------------------------------------

def next_provider(order: list[str], current: Optional[str]) -> str:
    """Pick the next provider after ``current`` in the fallback order.

    Falls through to ``manager-absorb`` when ``current`` is the last real
    provider, is unknown, or the order is empty. Never returns ``current``.
    """
    reals = [p for p in order if p != MANAGER_ABSORB]
    if not reals:
        return MANAGER_ABSORB
    if current in reals:
        idx = reals.index(current)
        if idx + 1 < len(reals):
            return reals[idx + 1]
        return MANAGER_ABSORB
    # Unknown current provider: start at the top of the order.
    return reals[0]


# --- candidate record -------------------------------------------------------

def failover_candidate(
    *,
    capture_text: str,
    pane: str,
    persona: str = "",
    lane: str = "",
    worktree: str = "",
    provider: Optional[str] = None,
    config: Optional[dict] = None,
    capture_tail_lines: int = 80,
) -> Optional[dict[str, Any]]:
    """Build a round-state failover record, or ``None`` if no failover is needed.

    Detection + state only — no keystrokes are sent. The record mirrors the
    contract's provider-state shape, with ``recommended_action`` telling the
    manager what the next step would be once the swap layer lands.
    """
    reason = detect_exhaustion(capture_text)
    if reason is None:
        return None

    cfg = resolve_config(config)
    order = cfg["order"]
    target = next_provider(order, provider)

    tail = "\n".join(capture_text.splitlines()[-capture_tail_lines:])

    return {
        "pane": pane,
        "persona": persona,
        "lane": lane,
        "worktree": worktree,
        "provider": provider,
        "provider_status": "exhausted",
        "failure_reason": reason,
        "next_provider": target,
        "recommended_action": (
            "manager_absorb" if target == MANAGER_ABSORB else "FAILOVER_CANDIDATE"
        ),
        "fallback_order": list(order),
        "probe": {
            "prompt": cfg["probe_prompt"],
            "success": None,          # not run in the detection-only slice
            "output_excerpt": "",
        },
        "capture_excerpt": tail,
    }


# --- morning-summary table --------------------------------------------------

def render_summary(records: list[dict[str, Any]]) -> str:
    """Render the ``## Provider Failover`` morning-summary section."""
    header = (
        "## Provider Failover\n\n"
        "| Pane | Persona | From | To | Reason | Probe | Result |\n"
        "|---|---|---|---|---|---|---|"
    )
    if not records:
        return header + "\n| _none_ | | | | | | no panes migrated |"

    rows = []
    for r in records:
        probe = r.get("probe", {}) or {}
        success = probe.get("success")
        probe_cell = "(pending)" if success is None else ("READY" if success else "probe_failed")
        action = r.get("recommended_action", "")
        if action == "manager_absorb":
            result = "manager-absorbed"
        elif success is True:
            result = "resumed"
        elif success is False:
            result = "probe_failed"
        else:
            result = "candidate"
        rows.append(
            f"| {r.get('pane','')} | {r.get('persona','')} | {r.get('provider','') or ''} "
            f"| {r.get('next_provider','')} | {r.get('failure_reason','')} | {probe_cell} | {result} |"
        )
    return header + "\n" + "\n".join(rows)


# --- CLI --------------------------------------------------------------------

def _cmd_detect(args: argparse.Namespace) -> int:
    capture_text = pathlib.Path(args.capture).read_text(encoding="utf-8")
    cfg = load_config_file(pathlib.Path(args.config)) if args.config else None
    record = failover_candidate(
        capture_text=capture_text,
        pane=args.pane,
        persona=args.persona,
        lane=args.lane,
        worktree=args.worktree,
        provider=args.provider,
        config=cfg,
    )
    if record is None:
        if args.json:
            print(json.dumps({"failover": False, "transient_only": is_transient_only(capture_text)}, indent=2))
        else:
            print(f"OK: pane {args.pane} healthy (no provider exhaustion detected)")
        return 0

    if args.json:
        print(json.dumps({"failover": True, "record": record}, indent=2))
    else:
        print(f"FAILOVER_CANDIDATE: pane {args.pane} ({record['provider']}) "
              f"-> {record['next_provider']}  reason={record['failure_reason']}")
        print(f"  action: {record['recommended_action']}")
    return 1


def _cmd_summary(args: argparse.Namespace) -> int:
    data = json.loads(pathlib.Path(args.records).read_text(encoding="utf-8"))
    records = data.get("records", data) if isinstance(data, dict) else data
    if not isinstance(records, list):
        records = []
    print(render_summary(records))
    return 0


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(description="Provider-failover detection + state (#166)")
    sub = ap.add_subparsers(dest="mode", required=True)

    p_det = sub.add_parser("detect", help="classify a pane capture; emit a candidate record")
    p_det.add_argument("--capture", required=True, help="path to a pane-capture text file")
    p_det.add_argument("--pane", required=True)
    p_det.add_argument("--persona", default="")
    p_det.add_argument("--lane", default="")
    p_det.add_argument("--worktree", default="")
    p_det.add_argument("--provider", default=None, help="the pane's current provider")
    p_det.add_argument("--config", default=None, help="provider_failover config (yaml/json)")
    p_det.add_argument("--json", action="store_true")
    p_det.set_defaults(func=_cmd_detect)

    p_sum = sub.add_parser("summary", help="render the morning-summary failover table")
    p_sum.add_argument("--records", required=True, help="JSON list (or {records:[...]}) of candidate records")
    p_sum.set_defaults(func=_cmd_summary)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
