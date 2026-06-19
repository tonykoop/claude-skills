#!/usr/bin/env python3
"""Detect generated epics missing the red-team risks section.

Refs #238 (Epic #235). Every top-level epic produced by the idea-incubator
brainstorm-to-issues pipeline must carry a `### Technical Risks & Assumptions`
section — the filed form of the Devil's Advocate / Red Team pass
(`agents/devils-advocate.md`). The section makes the adversarial pass
attributable as a distinct role and is appended without touching the optimist
`## Vision` / `## Stories` / `**Rollup:**` breakdown.

This checker makes the requirement enforceable: it flags any epic body that is
missing the section, the role-attribution line, or has only boilerplate content.

CLI:
    check_epic_risks_section.py --body-file epic.md
    check_epic_risks_section.py --issue 254          # needs gh + repo access
    cat epic.md | check_epic_risks_section.py --stdin

Exit 0 = conforming, 1 = non-conforming, 2 = usage/runtime error.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

SECTION_HEADER = "### Technical Risks & Assumptions"
# The role must be named in/near the section so the pass is attributable.
ATTRIBUTION_PATTERNS = [
    re.compile(r"red[\s-]?team", re.IGNORECASE),
    re.compile(r"devil'?s advocate", re.IGNORECASE),
]
# Phrases that signal empty boilerplate rather than concrete, epic-specific risk.
BOILERPLATE_MARKERS = [
    "there may be unforeseen risks",
    "various risks may apply",
    "tbd",
    "to be determined",
    "n/a",
]


def _section_body(body: str) -> str | None:
    """Return the text under SECTION_HEADER up to the next heading, or None."""
    lines = body.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == SECTION_HEADER:
            collected = []
            for nxt in lines[idx + 1:]:
                if re.match(r"^#{1,6}\s", nxt):  # next heading of any level ends it
                    break
                collected.append(nxt)
            return "\n".join(collected)
    return None


def find_problems(body: str) -> list[str]:
    """Return the conformance problems with ``body`` (empty == conforming)."""
    problems: list[str] = []
    section = _section_body(body)
    if section is None:
        return [f"missing `{SECTION_HEADER}` section"]

    if not any(p.search(section) for p in ATTRIBUTION_PATTERNS):
        problems.append("section is not attributed to the Red-Team / Devil's Advocate role")

    bullets = [ln for ln in section.splitlines() if ln.strip().startswith(("-", "*"))]
    substantive = [b for b in bullets if len(b.strip().lstrip("-* ").strip()) >= 12]
    if not substantive:
        problems.append("section has no substantive risk bullets")

    lowered = section.lower()
    if any(marker in lowered for marker in BOILERPLATE_MARKERS):
        problems.append("section contains boilerplate placeholder text instead of concrete risks")

    return problems


def is_conforming(body: str) -> bool:
    return not find_problems(body)


def load_issue_body(number: str) -> str:
    result = subprocess.run(
        ["gh", "issue", "view", number, "--json", "body", "--jq", ".body"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or "gh issue view failed").strip())
    return result.stdout


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect epics missing the Technical Risks & Assumptions section."
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--body-file", help="Path to a file holding the epic body.")
    src.add_argument("--issue", help="Epic issue number to fetch via gh.")
    src.add_argument("--stdin", action="store_true", help="Read the epic body from stdin.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.body_file:
            with open(args.body_file, "r", encoding="utf-8") as fh:
                body = fh.read()
        elif args.issue:
            body = load_issue_body(args.issue)
        else:
            body = sys.stdin.read()
    except (OSError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    problems = find_problems(body)
    if not problems:
        print("conforming: epic carries an attributed Technical Risks & Assumptions section")
        return 0
    print("NON-CONFORMING epic risks section:")
    for problem in problems:
        print(f"  - {problem}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
