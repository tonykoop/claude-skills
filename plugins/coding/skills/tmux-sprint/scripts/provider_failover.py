#!/usr/bin/env python3
"""Detect provider-exhausted panes and update failover round state.

This helper is intentionally non-invasive: it reads saved pane captures and
round-state JSON, then reports ``FAILOVER_CANDIDATE`` records. It does not send
tmux keys, launch CLIs, or migrate live panes.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from typing import Any


DEFAULT_CONFIG = {
    "order": ["codex", "claude", "gemini", "manager-absorb"],
    "probe_prompt": "Say READY and exit.",
    "probe_success_pattern": r"\bREADY\b",
    "launch_timeout_seconds": 20,
    "probe_timeout_seconds": 30,
}

EXHAUSTION_PATTERNS: list[tuple[str, list[str]]] = [
    (
        "weekly_budget_exhausted",
        [
            r"\bweekly\b.{0,80}\b(?:budget|quota|usage|limit)\b.{0,80}\b(?:exhausted|reached|used up|spent|depleted)\b",
            r"\b(?:budget|quota|usage|limit)\b.{0,80}\b(?:exhausted|reached|used up|spent|depleted)\b.{0,80}\bweekly\b",
        ],
    ),
    (
        "rate_limit_prompt",
        [
            r"\brate[- ]?limit(?:ed| prompt)?\b",
            r"\btoo many requests\b",
            r"\b429\b.{0,80}\b(?:retry|rate|limit)\b",
        ],
    ),
    (
        "provider_quota_exhausted",
        [
            r"\bno credits?\b",
            r"\bquota exceeded\b",
            r"\busage limit\b.{0,80}\b(?:reached|exceeded|hit)\b",
            r"\binsufficient credits?\b",
        ],
    ),
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        raise SystemExit(f"cannot parse JSON {path}: {exc}") from exc
    return data if isinstance(data, dict) else {}


def load_config(path: pathlib.Path | None) -> dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    if path is None:
        return config

    if not path.is_file():
        raise SystemExit(f"config file does not exist: {path}")

    if path.suffix.lower() == ".json":
        raw = load_json(path)
    else:
        try:
            import yaml
        except ImportError as exc:
            raise SystemExit("pyyaml is required for YAML config files") from exc
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise SystemExit(f"cannot parse YAML {path}: {exc}") from exc
        raw = loaded if isinstance(loaded, dict) else {}

    provider_failover = raw.get("provider_failover", raw)
    if not isinstance(provider_failover, dict):
        return config

    for key in DEFAULT_CONFIG:
        if key not in provider_failover:
            continue
        value = provider_failover[key]
        if key == "order":
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise SystemExit("provider_failover.order must be a list of provider names")
            config[key] = value
        else:
            config[key] = value
    return config


def excerpt(text: str, max_lines: int = 80) -> str:
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


def classify_capture(text: str) -> dict[str, str]:
    for reason, patterns in EXHAUSTION_PATTERNS:
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
            if match:
                return {
                    "action": "FAILOVER_CANDIDATE",
                    "failure_reason": reason,
                    "matched": " ".join(match.group(0).split()),
                }
    return {
        "action": "NO_FAILOVER",
        "failure_reason": "",
        "matched": "",
    }


def next_provider(order: list[str], current_provider: str) -> str:
    if current_provider in order:
        index = order.index(current_provider) + 1
        if index < len(order):
            return order[index]
    for provider in order:
        if provider != current_provider:
            return provider
    return "manager-absorb"


def update_provider_state(
    state: dict[str, Any],
    *,
    pane: str,
    persona: str,
    lane: str,
    worktree: str,
    provider: str,
    candidate: dict[str, str],
    config: dict[str, Any],
    capture_text: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    when = timestamp or utc_now()
    failover = state.setdefault("provider_failover", {})
    failover["config"] = config
    providers = failover.setdefault("providers", {})
    previous = providers.get(pane, {}) if isinstance(providers.get(pane), dict) else {}
    recommended = next_provider(list(config["order"]), provider)
    record = {
        "pane": pane,
        "persona": persona,
        "lane": lane,
        "worktree": worktree,
        "provider": provider,
        "provider_status": "exhausted",
        "previous_provider": previous.get("provider", ""),
        "failure_reason": candidate["failure_reason"],
        "matched": candidate["matched"],
        "recommended_next_provider": recommended,
        "last_migrated_at": "",
        "last_exhausted_at": when,
        "capture_excerpt": excerpt(capture_text),
        "probe": {},
    }
    providers[pane] = record
    events = failover.setdefault("events", [])
    if isinstance(events, list):
        events.append(
            {
                "at": when,
                "pane": pane,
                "persona": persona,
                "from_provider": provider,
                "recommended_next_provider": recommended,
                "failure_reason": candidate["failure_reason"],
                "action": "FAILOVER_CANDIDATE",
            }
        )
    return record


def write_json(path: pathlib.Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cmd_scan(args: argparse.Namespace) -> int:
    capture = pathlib.Path(args.capture)
    text = capture.read_text(encoding="utf-8", errors="replace")
    config = load_config(pathlib.Path(args.config) if args.config else None)
    candidate = classify_capture(text)
    result: dict[str, Any] = {
        "capture": str(capture),
        "action": candidate["action"],
        "failure_reason": candidate["failure_reason"],
        "matched": candidate["matched"],
    }

    if args.state and candidate["action"] == "FAILOVER_CANDIDATE":
        state_path = pathlib.Path(args.state)
        state = load_json(state_path)
        record = update_provider_state(
            state,
            pane=args.pane,
            persona=args.persona,
            lane=args.lane,
            worktree=args.worktree,
            provider=args.provider,
            candidate=candidate,
            config=config,
            capture_text=text,
        )
        write_json(state_path, state)
        result["provider_state"] = record

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def cmd_config(args: argparse.Namespace) -> int:
    config = load_config(pathlib.Path(args.config) if args.config else None)
    print(json.dumps({"provider_failover": config}, indent=2, sort_keys=True))
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan-capture", help="Scan a saved pane capture.")
    scan.add_argument("--capture", required=True, help="Pane capture text file.")
    scan.add_argument("--config", default="", help="Optional JSON/YAML failover config.")
    scan.add_argument("--state", default="", help="Optional round-state JSON to update.")
    scan.add_argument("--pane", required=True, help="tmux pane target, e.g. sprint:0.3.")
    scan.add_argument("--persona", default="", help="Persona/lane owner.")
    scan.add_argument("--lane", default="", help="Issue or lane identifier.")
    scan.add_argument("--worktree", default="", help="Lane worktree.")
    scan.add_argument("--provider", required=True, help="Current provider/runtime.")
    scan.set_defaults(func=cmd_scan)

    config = subparsers.add_parser("show-config", help="Print merged failover config.")
    config.add_argument("--config", default="", help="Optional JSON/YAML failover config.")
    config.set_defaults(func=cmd_config)

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
