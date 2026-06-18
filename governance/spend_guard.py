#!/usr/bin/env python3
"""Spend dead-man's switch + least-privilege tool/secret scoping.

Implements claude-skills#259 (Epic #254 governance layer).

Two enforcement surfaces, both driven by ``agent-roster.yaml``:

1. **Least-privilege scoping** — ``scope_check(agent, tool=?, secret=?)``.
   Default-deny: a tool/secret must be in the agent's department ``allow_*``
   list and absent from ``deny_*``. ``deny`` always wins. The YouTube scripting
   agent gets the YouTube API and never the local filesystem or a repo token.

2. **Maximizer-Mode dead-man's switch** — ``evaluate_ledger(ledger)``.
   * hard daily per-agent cap  -> ``HARD_CAP`` (halt the agent for the day)
   * 75% soft-warning          -> ``SOFT_WARN`` (pause heartbeat for audit)
   * stale / missing ledger    -> fail CLOSED: every agent ``STALE`` (paused)
   * optional org-wide ceiling -> ``GLOBAL_CAP`` breach blocks all dispatch

A broken loop that stops reporting usage cannot keep spending: a stale ledger
trips the switch exactly as a real overspend would.

CLI:
    python spend_guard.py --ledger usage.json [--config roster.yaml] [--json]
Exit code 0 = all clear; 1 = at least one agent paused/halted or ledger stale.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:  # pragma: no cover - dependency guard
    sys.stderr.write("spend_guard requires PyYAML (pip install pyyaml)\n")
    raise

# --- status constants -------------------------------------------------------
OK = "OK"
SOFT_WARN = "SOFT_WARN"        # >= soft_warn_pct of cap: pause heartbeat
HARD_CAP = "HARD_CAP"          # >= cap: halt agent for the day
STALE = "STALE"                # ledger too old / missing: fail closed
GLOBAL_CAP = "GLOBAL_CAP"      # org-wide daily ceiling breached

# Statuses that mean "do not keep dispatching to this agent".
BLOCKING = frozenset({SOFT_WARN, HARD_CAP, STALE, GLOBAL_CAP})

DEFAULT_CONFIG_NAME = "agent-roster.yaml"


# --- config loading ---------------------------------------------------------
def find_config(explicit: Optional[str] = None) -> Path:
    """Resolve roster path: explicit > $AGENT_ROSTER_CONFIG > ~/.claude > here."""
    candidates = [
        explicit,
        os.environ.get("AGENT_ROSTER_CONFIG"),
        os.path.expanduser("~/.claude/agent-roster.yaml"),
        str(Path(__file__).resolve().parent / DEFAULT_CONFIG_NAME),
    ]
    for c in candidates:
        if c and Path(c).expanduser().is_file():
            return Path(c).expanduser()
    raise FileNotFoundError("No agent-roster.yaml found in any lookup location")


def load_roster(config: Optional[str] = None) -> dict:
    with open(find_config(config), "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# --- least-privilege scoping ------------------------------------------------
@dataclass
class ScopeDecision:
    allowed: bool
    reason: str


def _department_of(roster: dict, agent: str) -> dict:
    agents = roster.get("agents", {})
    if agent not in agents:
        raise KeyError(f"unknown agent: {agent!r}")
    dept_name = agents[agent]["department"]
    depts = roster.get("departments", {})
    if dept_name not in depts:
        raise KeyError(f"agent {agent!r} references unknown department {dept_name!r}")
    return depts[dept_name]


def scope_check(
    roster: dict,
    agent: str,
    *,
    tool: Optional[str] = None,
    secret: Optional[str] = None,
) -> ScopeDecision:
    """Default-deny check. deny wins over allow; unlisted is denied."""
    if (tool is None) == (secret is None):
        raise ValueError("pass exactly one of tool= or secret=")
    dept = _department_of(roster, agent)
    if tool is not None:
        if tool in dept.get("deny_tools", []):
            return ScopeDecision(False, f"tool {tool!r} explicitly denied for {agent}")
        if tool in dept.get("allow_tools", []):
            return ScopeDecision(True, f"tool {tool!r} allowed for {agent}")
        return ScopeDecision(False, f"tool {tool!r} not in allow-list for {agent} (default-deny)")
    if secret in dept.get("deny_secrets", []):
        return ScopeDecision(False, f"secret {secret!r} explicitly denied for {agent}")
    if secret in dept.get("allow_secrets", []):
        return ScopeDecision(True, f"secret {secret!r} allowed for {agent}")
    return ScopeDecision(False, f"secret {secret!r} not in allow-list for {agent} (default-deny)")


# --- spend evaluation -------------------------------------------------------
@dataclass
class AgentSpend:
    agent: str
    spent_usd: float
    cap_usd: float
    soft_warn_pct: float
    status: str
    utilization: float

    @property
    def blocking(self) -> bool:
        return self.status in BLOCKING


def evaluate_agent(agent: str, spent_usd: float, cap_usd: float, soft_warn_pct: float) -> AgentSpend:
    util = (spent_usd / cap_usd) if cap_usd > 0 else float("inf")
    if spent_usd >= cap_usd:
        status = HARD_CAP
    elif util >= soft_warn_pct:
        status = SOFT_WARN
    else:
        status = OK
    return AgentSpend(agent, spent_usd, cap_usd, soft_warn_pct, status, round(util, 4))


@dataclass
class LedgerReport:
    stale: bool
    age_seconds: Optional[float]
    global_spent_usd: float
    global_cap_usd: Optional[float]
    global_breach: bool
    agents: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        if self.stale or self.global_breach:
            return False
        return not any(a.blocking for a in self.agents)

    @property
    def blocked_agents(self) -> list:
        return [a.agent for a in self.agents if a.blocking]


def _parse_ts(value: str) -> datetime:
    # Accept trailing 'Z' (UTC) which fromisoformat rejects before 3.11.
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def evaluate_ledger(roster: dict, ledger: dict, now: Optional[datetime] = None) -> LedgerReport:
    """Evaluate a usage ledger against the roster. Fails closed when stale."""
    now = now or datetime.now(timezone.utc)
    mm = roster.get("maximizer_mode", {})
    agents_cfg = roster.get("agents", {})

    # Dead-man's switch: how old is this ledger?
    age = None
    stale = False
    gen = ledger.get("generated_at")
    staleness_limit = mm.get("heartbeat_staleness_seconds")
    if gen is None:
        stale = True
    elif staleness_limit is not None:
        age = (now - _parse_ts(gen)).total_seconds()
        stale = age > staleness_limit or age < -60  # future-dated ledgers are also suspect

    reported = ledger.get("agents", {})
    rows: list[AgentSpend] = []
    total = 0.0
    for name, cfg in agents_cfg.items():
        spent = float(reported.get(name, {}).get("spent_usd", 0.0))
        total += spent
        cap = float(cfg["daily_spend_cap_usd"])
        soft = float(cfg.get("soft_warn_pct", mm.get("default_soft_warn_pct", 0.75)))
        row = evaluate_agent(name, spent, cap, soft)
        if stale and mm.get("enabled", True):
            row.status = STALE  # fail closed: pause everyone pending audit
        rows.append(row)

    global_cap = mm.get("global_daily_cap_usd")
    global_breach = global_cap is not None and total >= float(global_cap)
    if global_breach:
        for r in rows:
            if r.status == OK:
                r.status = GLOBAL_CAP

    return LedgerReport(
        stale=stale and mm.get("enabled", True),
        age_seconds=age,
        global_spent_usd=round(total, 4),
        global_cap_usd=global_cap,
        global_breach=global_breach,
        agents=rows,
    )


# --- CLI --------------------------------------------------------------------
def _render(report: LedgerReport) -> str:
    lines = []
    lines.append("Maximizer-Mode spend report")
    lines.append("=" * 40)
    if report.stale:
        lines.append("!! LEDGER STALE — dead-man's switch TRIPPED, all agents paused")
    if report.global_breach:
        lines.append(
            f"!! GLOBAL CAP breached: ${report.global_spent_usd} >= ${report.global_cap_usd}"
        )
    for a in sorted(report.agents, key=lambda r: r.agent):
        flag = "  " if a.status == OK else ">>"
        lines.append(
            f"{flag} {a.agent:<8} {a.status:<10} "
            f"${a.spent_usd:>7.2f} / ${a.cap_usd:>7.2f}  ({a.utilization:>5.0%})"
        )
    lines.append("-" * 40)
    lines.append("ALL CLEAR" if report.ok else f"BLOCKED: {', '.join(report.blocked_agents) or 'global/stale'}")
    return "\n".join(lines)


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(description="Spend dead-man's switch + scope check")
    ap.add_argument("--ledger", required=True, help="path to usage ledger JSON")
    ap.add_argument("--config", help="path to agent-roster.yaml")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args(argv)

    roster = load_roster(args.config)
    with open(args.ledger, "r", encoding="utf-8") as fh:
        ledger = json.load(fh)
    report = evaluate_ledger(roster, ledger)

    if args.json:
        print(json.dumps({
            "ok": report.ok,
            "stale": report.stale,
            "global_breach": report.global_breach,
            "blocked_agents": report.blocked_agents,
            "agents": [vars(a) for a in report.agents],
        }, indent=2))
    else:
        print(_render(report))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
