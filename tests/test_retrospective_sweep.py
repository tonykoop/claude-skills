#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "maker"
    / "skills"
    / "idea-incubator"
    / "scripts"
    / "retrospective_sweep.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("retrospective_sweep", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["retrospective_sweep"] = module
    spec.loader.exec_module(module)
    return module


sweep = load_module()


EPIC_BODY = textwrap.dedent(
    """
    **Tracking epic.** Build it. Source: doc.md (2026-06-18).

    ## Vision
    Vision text mentioning #999 inline (should be ignored when checklist present).

    ## Stories
    - [x] #255 - studio release (sp 5)
    - [ ] #256 - adversarial qa (sp 5)
    - [x] #255 - duplicate row (dedup) (sp 5)

    **Rollup:** ~10 points.
    """
).strip()


class ParseStoryNumbersTests(unittest.TestCase):
    def test_parses_checklist_in_order_deduped(self) -> None:
        self.assertEqual(sweep.parse_story_numbers(EPIC_BODY), [255, 256])

    def test_ignores_inline_refs_when_checklist_present(self) -> None:
        self.assertNotIn(999, sweep.parse_story_numbers(EPIC_BODY))

    def test_falls_back_to_bare_refs_without_checklist(self) -> None:
        body = "## Vision\nDepends on #12 and #34, also #12 again.\n"
        self.assertEqual(sweep.parse_story_numbers(body), [12, 34])


class BuildRetroNoteTests(unittest.TestCase):
    def _sample_sweep(self) -> dict:
        return {
            "epic": 254,
            "title": "Studio Release Epic",
            "stories": [
                {"number": 255, "title": "release", "state": "CLOSED", "labels": ["story", "sp:5"]},
                {"number": 256, "title": "qa", "state": "OPEN", "labels": ["story"]},
            ],
            "commits": ["abc123 feat: do thing (#254)"],
            "pr_comments": ["PR #288: release gate"],
        }

    def test_note_has_backlink_and_source(self) -> None:
        note = sweep.build_retro_note(254, "Studio Release Epic", self._sample_sweep())
        self.assertIn("# Retrospective: Studio Release Epic (#254)", note)
        self.assertIn("Source: epic #254 retro", note)
        self.assertIn("## Backlink", note)
        self.assertIn("Source epic: #254", note)

    def test_note_reports_evidence_counts(self) -> None:
        note = sweep.build_retro_note(254, "Studio Release Epic", self._sample_sweep())
        self.assertIn("Child stories: 2 (1 closed).", note)
        self.assertIn("Commits referencing the epic: 1.", note)
        self.assertIn("#255 [CLOSED] release", note)

    def test_note_handles_empty_sweep(self) -> None:
        empty = {"epic": 1, "title": "x", "stories": [], "commits": [], "pr_comments": []}
        note = sweep.build_retro_note(1, "x", empty)
        self.assertIn("(none parsed from the epic body)", note)
        self.assertIn("(none found)", note)


class PathTests(unittest.TestCase):
    def test_paths(self) -> None:
        out = Path("/tmp/ik")
        self.assertEqual(sweep.note_path(out, 254).name, "epic-254-retro.md")
        self.assertEqual(sweep.sweep_path(out, 254).name, "epic-254-sweep.json")


class RunSweepTests(unittest.TestCase):
    def test_run_sweep_composes_wrappers(self) -> None:
        # Stub the network/VCS wrappers; verify orchestration + parsing.
        sweep.fetch_epic = lambda n, repo: {"title": "T", "body": EPIC_BODY}
        sweep.fetch_story = lambda n, repo: {"number": n, "title": "s", "state": "CLOSED", "labels": []}
        sweep.fetch_commits = lambda n: ["c1 (#254)"]
        sweep.fetch_pr_comments = lambda n, repo: ["PR #288: x"]
        title, data = sweep.run_sweep(254, None)
        self.assertEqual(title, "T")
        self.assertEqual([s["number"] for s in data["stories"]], [255, 256])
        self.assertEqual(data["commits"], ["c1 (#254)"])


if __name__ == "__main__":
    unittest.main()
