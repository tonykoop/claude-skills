#!/usr/bin/env python3
"""Write TwinGrid freeze and Partner Peek helper records."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import sys
from typing import Any


SUMMARY_CANDIDATES = ["artifact_summary.md", "README.md", "summary.md"]
VALIDATION_CANDIDATES = [
    "validation_summary.md",
    "validation-notes.md",
    "validation_notes.md",
]
SKILL_FINDINGS_CANDIDATES = [
    "skill_findings.md",
    "skill-improvement-findings.md",
    "skill-improvement-recommendation.md",
]
AGENT_RECORD_CANDIDATES = [
    "agent_record.json",
    "agent_record.md",
    "twingrid_agent_record.json",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def first_existing(folder: pathlib.Path, names: list[str]) -> pathlib.Path | None:
    for name in names:
        path = folder / name
        if path.is_file():
            return path
    return None


def relpath(path: pathlib.Path, folder: pathlib.Path) -> str:
    try:
        return path.relative_to(folder).as_posix()
    except ValueError:
        return str(path)


def manifest(folder: pathlib.Path, exclude: set[str]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.name in exclude:
            continue
        entries.append(
            {
                "path": str(path.resolve()),
                "name": path.name,
                "sha256": sha256_file(path),
            }
        )
    return entries


def load_record(folder: pathlib.Path, candidates: list[str]) -> dict[str, Any]:
    path = first_existing(folder, candidates)
    if path is None or path.suffix != ".json":
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def parse_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--output-folder",
        required=True,
        help="TwinGrid artifact folder.",
    )
    parser.add_argument("--round", type=int, default=None, help="Round number.")
    parser.add_argument("--lane", default="", help="Lane/persona name.")
    parser.add_argument("--side", default="", help="A/B side.")
    parser.add_argument("--runtime", default="", help="Runtime label.")
    parser.add_argument("--task", default="", help="Task title.")


def freeze_record(args: argparse.Namespace) -> dict[str, Any]:
    folder = pathlib.Path(args.output_folder).resolve()
    if not folder.is_dir():
        raise SystemExit(f"output folder does not exist: {folder}")

    agent = load_record(folder, AGENT_RECORD_CANDIDATES)
    summary = first_existing(folder, SUMMARY_CANDIDATES)
    validation = first_existing(folder, VALIDATION_CANDIDATES)
    skill_findings = first_existing(folder, SKILL_FINDINGS_CANDIDATES)
    agent_record = first_existing(folder, AGENT_RECORD_CANDIDATES)
    entries = manifest(folder, {"ready_for_peek.json"})

    paths = {
        "artifact_summary": str(summary.resolve()) if summary else "",
        "validation": str(validation.resolve()) if validation else "",
        "skill_findings": str(skill_findings.resolve()) if skill_findings else "",
        "agent_record": str(agent_record.resolve()) if agent_record else "",
    }

    return {
        "round": args.round,
        "lane": args.lane or agent.get("lane", ""),
        "side": args.side or agent.get("side", ""),
        "runtime": args.runtime or agent.get("runtime", ""),
        "task": args.task or agent.get("task", ""),
        "state": "BLIND_FROZEN",
        "output_folder": str(folder),
        "paths": paths,
        "blind_artifact_manifest": entries,
        "blind_artifact_sha256": {entry["name"]: entry["sha256"] for entry in entries},
        "canonical_skill_findings": "skill_findings.md",
        "accepted_skill_findings_aliases": [
            "skill-improvement-findings.md",
            "skill-improvement-recommendation.md",
        ],
        "partner_output_read": False,
        "existing_blind_artifacts_modified": False,
        "generated_at_utc": utc_now(),
    }


def write_json(path: pathlib.Path, data: dict[str, Any], force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"{path} exists; pass --force to overwrite")
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def cmd_freeze(args: argparse.Namespace) -> int:
    folder = pathlib.Path(args.output_folder).resolve()
    data = freeze_record(args)
    output = folder / "ready_for_peek.json"
    write_json(output, data, args.force)
    print(output)
    return 0


def cmd_peek_record(args: argparse.Namespace) -> int:
    own = pathlib.Path(args.output_folder).resolve()
    partner = pathlib.Path(args.partner_folder).resolve()
    if not own.is_dir():
        raise SystemExit(f"own output folder does not exist: {own}")
    partner_freeze = load_record(partner, ["ready_for_peek.json"])
    files_added = [
        relpath(path, own)
        for path in sorted(own.glob("v2-*"))
        if path.is_file()
    ]
    files_added.extend(
        name
        for name in [
            "partner-feedback.md",
            "partner-peek-improvements.md",
            "combine_recommendation.md",
        ]
        if (own / name).is_file()
    )
    data = {
        "round": args.round,
        "lane": args.lane,
        "side": args.side,
        "runtime": args.runtime,
        "task": args.task,
        "output_folder": str(own),
        "partner_output_folder": str(partner),
        "partner_freeze_state": partner_freeze.get("state", ""),
        "files_added_or_changed": sorted(set(files_added)),
        "partner_ideas_adopted": [],
        "validation_run": [],
        "pr_or_issues_opened": "",
        "combined_ab_should_feed_skill_improvement": True,
        "skill_improvement_recommendation": "",
        "notes_for_manager": "",
        "generated_at_utc": utc_now(),
    }
    output = own / "partner-peek-record.json"
    write_json(output, data, args.force)
    print(output)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    freeze = subparsers.add_parser("freeze", help="Write ready_for_peek.json.")
    parse_common_args(freeze)
    freeze.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing record.",
    )
    freeze.set_defaults(func=cmd_freeze)

    peek = subparsers.add_parser(
        "peek-record",
        help="Write a Partner Peek record stub.",
    )
    parse_common_args(peek)
    peek.add_argument("--partner-folder", required=True, help="Partner artifact folder.")
    peek.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing record.",
    )
    peek.set_defaults(func=cmd_peek_record)

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
