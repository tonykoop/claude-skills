#!/usr/bin/env python3
"""Create the idea-incubator label set in a GitHub repo.

Cross-platform companion to bootstrap-labels.sh. Behaves the same way:
shells out to `gh label create --force` once per label. Use this on hosts
where bash is awkward (Claude Desktop on native Windows, sandboxed Codex
Desktop with Python but no shell).

Usage:
    python bootstrap_labels.py owner/repo
    GITHUB_REPOSITORY=owner/repo python bootstrap_labels.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

LABELS: list[tuple[str, str, str]] = [
    ("capture", "Fresh idea captured from Telegram, chat, or a quick note.", "1d76db"),
    ("intake", "A pasted dump that still needs parsing into separate ideas.", "0e8a16"),
    ("connect", "Link this idea to related issues or duplicates.", "5319e7"),
    ("review", "Backlog review or triage pass.", "fbca04"),
    ("promote", "Ready for downstream handoff.", "b60205"),
    ("needs-clarification", "Key detail is missing before the idea can move.", "d93f0b"),
    ("duplicate-candidate", "This idea may overlap with an existing issue.", "e11d21"),
    ("stale", "The idea has sat long enough to deserve a review.", "c2c2c2"),
    ("ready-now", "Low-friction idea that can be executed quickly.", "0052cc"),
    ("maker", "Fabrication, shop, or hardware ideas.", "bfdadc"),
    ("instrument", "Musical instrument ideas and acoustics work.", "c5def5"),
    ("yoga", "Class, sequence, or movement ideas.", "f9d0c4"),
    ("skills", "Skill ecosystem, tooling, or orchestration ideas.", "d4c5f9"),
    ("general", "Idea does not fit a narrower domain.", "ededed"),
]


def main(argv: list[str]) -> int:
    repo = argv[1] if len(argv) > 1 else os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        print("usage: bootstrap_labels.py owner/repo", file=sys.stderr)
        return 1

    if shutil.which("gh") is None:
        print("gh is required for label bootstrap", file=sys.stderr)
        return 1

    for name, description, color in LABELS:
        result = subprocess.run(
            [
                "gh", "label", "create", name,
                "--repo", repo,
                "--description", description,
                "--color", color,
                "--force",
            ],
            stdout=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            print(f"gh label create failed for '{name}' in {repo}", file=sys.stderr)
            return result.returncode

    print(f"Created {len(LABELS)} labels in {repo}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
