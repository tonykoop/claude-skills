#!/usr/bin/env python3
"""Apply the #10 release-readiness manifest fixes (idempotent).

Folds in the apply-ready manifest corrections documented in
docs/release-readiness/release-audit-2026-06-16.md:

  * correct 13 stale `repo_path` values left by the marketplace restructure
    (skills/... and claude/skills/... -> plugins/{maker,coding}/skills/...),
  * add the 3 shipped-but-unlisted skills (sheet-music, ci-triage,
    scaffold-hygiene), versions sourced from each SKILL.md frontmatter,
  * bump the idea-incubator entry to 1.5.0 for the image-gen-2 chapter template.

Running twice is a no-op. `manifest.yaml` is LF; this preserves it. The 4 orphan
entries, 8 missing changelogs, and 2 phantom scripts in the audit stay manual
(they need judgment / human-authored history) and are NOT touched here.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAN = ROOT / "manifest.yaml"

REPO_PATH_FIXES = {
    "repo_path: skills/idea-incubator": "repo_path: plugins/maker/skills/idea-incubator",
    "repo_path: skills/instrument-maker": "repo_path: plugins/maker/skills/instrument-maker",
    "repo_path: skills/laser-art": "repo_path: plugins/maker/skills/laser-art",
    "repo_path: skills/maker-engineering": "repo_path: plugins/maker/skills/maker-engineering",
    "repo_path: skills/playlist-builder": "repo_path: plugins/maker/skills/playlist-builder",
    "repo_path: skills/reverse-engineer": "repo_path: plugins/maker/skills/reverse-engineer",
    "repo_path: skills/sheet-metal": "repo_path: plugins/maker/skills/sheet-metal",
    "repo_path: skills/yoga-sequencer": "repo_path: plugins/maker/skills/yoga-sequencer",
    "repo_path: claude/skills/disk-cleanup": "repo_path: plugins/coding/skills/disk-cleanup",
    "repo_path: claude/skills/merge-review": "repo_path: plugins/coding/skills/merge-review",
    "repo_path: skills/run-swarm": "repo_path: plugins/coding/skills/run-swarm",
    "repo_path: skills/skills-meta": "repo_path: plugins/coding/skills/skills-meta",
    "repo_path: claude/skills/sprint-update": "repo_path: plugins/coding/skills/sprint-update",
}

NEW_ENTRIES = '''  sheet-music:
    canonical_version: 0.1.0
    runtime: shared
    repo_path: plugins/maker/skills/sheet-music
    last_updated: 2026-06-16
    status: active
    notes: >-
      Sheet music, fingering charts, MIDI, audio renderings, and printable
      songsheets for instruments built from the instrument-maker repos; ABC ->
      LilyPond/MIDI/SVG/PDF pipeline, deposits learn-to-play/ folders into build repos.
  ci-triage:
    canonical_version: 0.1.0
    runtime: shared
    repo_path: plugins/coding/skills/ci-triage
    last_updated: 2026-06-16
    status: active
    notes: >-
      Read-only CI and Dependabot health check across the WRFCoin repos; writes a
      markdown report under wrfcoin/docs/ci-triage/.
  scaffold-hygiene:
    canonical_version: 0.1.0
    runtime: shared
    repo_path: plugins/coding/skills/scaffold-hygiene
    last_updated: 2026-06-16
    status: active
    notes: >-
      Scaffolding-hygiene sweep across WRFCoin repos: detects drift between
      build/test/deploy scripts, docs, CI workflows, env vars, Docker, and
      cross-repo API contracts; files issues and writes a timestamped report.'''


def main() -> None:
    s = MAN.read_text()
    changed = 0
    for a, b in REPO_PATH_FIXES.items():
        if a in s:
            s = s.replace(a, b, 1)
            changed += 1
    # idea-incubator version + date + notes bump
    s2 = s.replace("""  idea-incubator:
    canonical_version: 1.4.4
    runtime: shared
    repo_path: plugins/maker/skills/idea-incubator
    last_updated: 2026-05-18""", """  idea-incubator:
    canonical_version: 1.5.0
    runtime: shared
    repo_path: plugins/maker/skills/idea-incubator
    last_updated: 2026-06-16""", 1)
    if s2 != s:
        s = s2
        changed += 1
    tail = "and instrument design-book/yearbook/portfolio chapter promotion pattern."
    if tail in s and "image-gen-2 chapter template + asset contract" not in s:
        s = s.replace(tail, tail[:-1] + "; image-gen-2 chapter template + asset "
                      "contract (packet-first gate, authority-vs-concept two-source "
                      "rule, derivative/non-dimensional asset metadata).", 1)
        changed += 1
    # add 3 missing entries after the run-swarm block
    if "\n  sheet-music:\n" not in s:
        lines = s.split("\n")
        start = next(i for i, ln in enumerate(lines) if ln == "  run-swarm:")
        ins = next(j for j in range(start + 1, len(lines))
                   if re.match(r"^  [a-z0-9_-]+:$", lines[j]))
        lines[ins:ins] = NEW_ENTRIES.split("\n")
        s = "\n".join(lines)
        changed += 1
    if changed:
        MAN.write_text(s)
    print(f"manifest.yaml: {changed} edit-groups applied"
          + (" (already current)" if changed == 0 else ""))


if __name__ == "__main__":
    main()
