#!/usr/bin/env python3
"""Generate a TwinGrid lane matrix from output folders and pane captures."""

from __future__ import annotations

import argparse
import glob
import json
import pathlib
import re
import sys
from typing import Any


BLOCK_PATTERNS = {
    "approval_prompt": [
        r"Do you want to allow",
        r"requires approval",
        r"approve this command",
        r"waiting for approval",
        r"sandbox_permissions",
    ],
    "missing_tool": [
        r"command not found",
        r"No such file or directory",
        r"not installed",
        r"missing tool",
        r"install hint",
    ],
    "network_or_auth": [
        r"Temporary failure resolving",
        r"network is unreachable",
        r"rate limit",
        r"\b401\b",
        r"\b403\b",
    ],
    "waiting_for_input": [
        r"Press Ctrl-C",
        r"watching for changes",
        r"waiting for input",
        r"continue\? \[y/N\]",
    ],
}


def load_json(path: pathlib.Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def first_existing_json(folder: pathlib.Path, names: list[str]) -> dict[str, Any]:
    for name in names:
        data = load_json(folder / name)
        if data is not None:
            return data
    return {}


def infer_from_name(folder: pathlib.Path) -> dict[str, str]:
    parts = folder.name.split("-")
    inferred = {"lane": "", "side": "", "runtime": ""}
    for runtime in ("codex", "claude", "gemini"):
        if runtime in parts:
            inferred["runtime"] = runtime
    for side in ("A", "B", "a", "b"):
        if side in parts:
            inferred["side"] = side.upper()
    known_lanes = {
        "alice",
        "bob",
        "cindy",
        "dan",
        "elsa",
        "frank",
        "gina",
        "henry",
        "irene",
    }
    for part in parts:
        if part.lower() in known_lanes:
            inferred["lane"] = part.lower()
            break
    return inferred


def list_names(folder: pathlib.Path, patterns: list[str]) -> list[str]:
    names: set[str] = set()
    for pattern in patterns:
        for match in folder.glob(pattern):
            if match.is_file():
                names.add(match.name)
    return sorted(names)


def collect_lane(folder: pathlib.Path) -> dict[str, Any]:
    blind = first_existing_json(folder, ["agent_record.json", "twingrid_agent_record.json"])
    peek = first_existing_json(folder, ["partner-peek-record.json", "partner_peek_record.json"])
    inferred = infer_from_name(folder)

    validation: list[str] = []
    for record in (blind, peek):
        values = record.get("validation_run", [])
        if isinstance(values, list):
            validation.extend(str(value) for value in values)
        elif values:
            validation.append(str(values))

    skill_recommendation = (
        peek.get("skill_improvement_recommendation")
        or peek.get("skill_improvement_summary")
        or blind.get("skill_improvement_recommendation")
        or ""
    )

    pr_or_issues = (
        peek.get("pr_or_issues_opened")
        or blind.get("pr_or_issues_opened")
        or ""
    )

    return {
        "lane": blind.get("lane") or peek.get("lane") or inferred["lane"],
        "side": blind.get("side") or peek.get("side") or inferred["side"],
        "runtime": blind.get("runtime") or peek.get("runtime") or inferred["runtime"],
        "output_folder": str(folder),
        "blind_artifacts": blind.get("artifacts_produced") or list_names(
            folder, ["agent_record.*", "*report*.md", "*handoff*.md"]
        ),
        "v2_artifacts": list_names(
            folder, ["partner-peek-improvements.md", "partner-peek-record.*", "v2-*"]
        ),
        "validation_run": validation,
        "skill_recommendation": skill_recommendation,
        "pr_or_issues_opened": pr_or_issues,
    }


def scan_outputs(pattern: str) -> list[dict[str, Any]]:
    folders = [
        pathlib.Path(path)
        for path in glob.glob(pattern)
        if pathlib.Path(path).is_dir()
    ]
    lanes = [collect_lane(folder) for folder in sorted(folders)]
    return [
        lane
        for lane in lanes
        if lane["lane"] or lane["runtime"] or lane["blind_artifacts"] or lane["v2_artifacts"]
    ]


def scan_blocked(capture_dir: str | None) -> list[dict[str, str]]:
    if not capture_dir:
        return []
    root = pathlib.Path(capture_dir)
    if not root.is_dir():
        return []

    findings: list[dict[str, str]] = []
    for path in sorted(root.glob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for block_type, patterns in BLOCK_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    findings.append(
                        {
                            "capture": str(path),
                            "block_type": block_type,
                            "matched": match.group(0),
                        }
                    )
                    break
            else:
                continue
            break
    return findings


def build_lane_pairs(lanes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for lane in lanes:
        lane_name = str(lane.get("lane") or "unknown")
        side = str(lane.get("side") or "?").upper()
        entry = grouped.setdefault(lane_name, {"lane": lane_name, "sides": {}})
        entry["sides"][side] = lane
    return [grouped[name] for name in sorted(grouped)]


def markdown_matrix(data: dict[str, Any]) -> str:
    rows = [
        "| Lane | A output | B output | A v2 | B v2 | Validations | Skill recommendations |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for pair in data["lane_pairs"]:
        side_a = pair["sides"].get("A", {})
        side_b = pair["sides"].get("B", {})
        recommendations = [
            str(item.get("skill_recommendation", ""))
            for item in (side_a, side_b)
            if item.get("skill_recommendation")
        ]
        validation_count = len(side_a.get("validation_run", [])) + len(
            side_b.get("validation_run", [])
        )
        rows.append(
            "| {lane} | {a_out} | {b_out} | {a_v2} | {b_v2} | {validations} | {rec} |".format(
                lane=pair.get("lane", ""),
                a_out=side_a.get("output_folder", ""),
                b_out=side_b.get("output_folder", ""),
                a_v2=", ".join(side_a.get("v2_artifacts", [])),
                b_v2=", ".join(side_b.get("v2_artifacts", [])),
                validations=str(validation_count),
                rec="; ".join(recommendations).replace("|", "/"),
            )
        )

    if data["blocked_panes"]:
        rows.extend(["", "## Blocked Panes", ""])
        rows.extend(["| Capture | Type | Matched |", "| --- | --- | --- |"])
        for finding in data["blocked_panes"]:
            rows.append(
                "| {capture} | {kind} | {matched} |".format(
                    capture=finding["capture"],
                    kind=finding["block_type"],
                    matched=finding["matched"].replace("|", "/"),
                )
            )
    return "\n".join(rows)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--outputs-glob",
        default="/tmp/twingrid-*",
        help="Glob of TwinGrid output folders. Default: /tmp/twingrid-*",
    )
    parser.add_argument(
        "--pane-captures-dir",
        default=None,
        help="Optional directory of tmux pane capture text files to scan.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format. Default: json",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    lanes = scan_outputs(args.outputs_glob)
    data = {
        "lanes": lanes,
        "lane_pairs": build_lane_pairs(lanes),
        "blocked_panes": scan_blocked(args.pane_captures_dir),
    }
    if args.format == "markdown":
        print(markdown_matrix(data))
    else:
        print(json.dumps(data, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
