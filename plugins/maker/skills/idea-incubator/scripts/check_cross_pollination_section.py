#!/usr/bin/env python3
"""Validate the Cross-Pollination Opportunities report on an epic.

Refs #247 (Epic #236). The Cross-Pollination Librarian rolls its per-pair
matches up into an epic-level `### Cross-Pollination Opportunities Detected`
section that distinguishes three opportunity classes — interface reuse,
interoperability, and silo alert — and cites the source issues/notes behind each
recommendation. This checker makes that contract enforceable: it flags an epic
report that is missing the section, names none of the three opportunity classes,
or carries uncited recommendations.

CLI:
    check_cross_pollination_section.py --body-file epic.md
    check_cross_pollination_section.py --issue 236       # needs gh + repo access
    cat epic.md | check_cross_pollination_section.py --stdin

Exit 0 = conforming, 1 = non-conforming, 2 = usage/runtime error.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

SECTION_HEADER = "### Cross-Pollination Opportunities Detected"
# At least one of the three opportunity classes must be present.
OPPORTUNITY_CLASSES = ["Interface reuse", "Interoperability", "Silo alert"]
# A recommendation cites a source: a `#123` issue ref or a `Source(s):` line.
ISSUE_REF = re.compile(r"#\d+")
SOURCE_LINE = re.compile(r"\bsources?:\s*", re.IGNORECASE)


def _section_body(body: str) -> str | None:
    lines = body.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == SECTION_HEADER:
            collected = []
            for nxt in lines[idx + 1:]:
                # A same-or-higher-level heading (###/##/#) ends the section;
                # the #### opportunity subsections stay inside it.
                if re.match(r"^#{1,3}\s", nxt):
                    break
                collected.append(nxt)
            return "\n".join(collected)
    return None


def find_problems(body: str) -> list[str]:
    section = _section_body(body)
    if section is None:
        return [f"missing `{SECTION_HEADER}` section"]

    problems: list[str] = []
    present_classes = [c for c in OPPORTUNITY_CLASSES if c.lower() in section.lower()]
    if not present_classes:
        problems.append(
            "section names none of the opportunity classes: " + ", ".join(OPPORTUNITY_CLASSES)
        )

    bullets = [ln.strip() for ln in section.splitlines() if ln.strip().startswith(("-", "*"))]
    if not bullets:
        problems.append("section has no opportunity recommendations")
    else:
        uncited = [b for b in bullets if not (ISSUE_REF.search(b) or SOURCE_LINE.search(b))]
        if uncited:
            problems.append(
                f"{len(uncited)} recommendation(s) cite no source issue/note "
                "(need a #N ref or a 'Source:' line)"
            )
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
        description="Validate the epic Cross-Pollination Opportunities section."
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
        print("conforming: epic carries a cited Cross-Pollination Opportunities section")
        return 0
    print("NON-CONFORMING cross-pollination section:")
    for problem in problems:
        print(f"  - {problem}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
