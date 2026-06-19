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
    / "check_cross_pollination_section.py"
)
AGENT = (
    REPO_ROOT
    / "plugins"
    / "maker"
    / "skills"
    / "idea-incubator"
    / "agents"
    / "cross-pollination-librarian.md"
)


def load_module():
    spec = importlib.util.spec_from_file_location("check_cross_pollination_section", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_cross_pollination_section"] = module
    spec.loader.exec_module(module)
    return module


checker = load_module()


CONFORMING = textwrap.dedent(
    """
    **Tracking epic.** Build it.

    ## Vision
    A vision.

    ### Cross-Pollination Opportunities Detected

    _Posted by cross-pollination-librarian (run 2026-06-18)._

    #### Interface reuse
    - Reuse the index-detent subassembly from #142 for #207. Source: #142.

    #### Interoperability
    - #150 and #168 both expose bus:i2c-3v3. Sources: #150, #168.

    #### Silo alert
    - #211 re-solves spring-return already in #98. Sources: #98, #211.

    ## Links
    - x
    """
).strip()


class CrossPollinationCheckerTests(unittest.TestCase):
    def test_conforming_report_passes(self) -> None:
        self.assertEqual(checker.find_problems(CONFORMING), [])
        self.assertTrue(checker.is_conforming(CONFORMING))

    def test_missing_section_is_flagged(self) -> None:
        body = "## Vision\nx\n## Links\n-\n"
        self.assertTrue(any("missing" in p for p in checker.find_problems(body)))

    def test_no_opportunity_classes_is_flagged(self) -> None:
        body = (
            "### Cross-Pollination Opportunities Detected\n\n"
            "- something vague about #5\n"
        )
        problems = checker.find_problems(body)
        self.assertTrue(any("opportunity classes" in p for p in problems))

    def test_uncited_recommendation_is_flagged(self) -> None:
        body = (
            "### Cross-Pollination Opportunities Detected\n\n"
            "#### Interface reuse\n"
            "- Reuse the detent mechanism somewhere useful.\n"
        )
        problems = checker.find_problems(body)
        self.assertTrue(any("cite no source" in p for p in problems))

    def test_source_line_counts_as_citation(self) -> None:
        body = (
            "### Cross-Pollination Opportunities Detected\n\n"
            "#### Silo alert\n"
            "- A re-solves B. Source: vault/notes/spring.md\n"
        )
        self.assertEqual(checker.find_problems(body), [])

    def test_only_one_class_required(self) -> None:
        body = (
            "### Cross-Pollination Opportunities Detected\n\n"
            "#### Interoperability\n"
            "- #1 and #2 share bus:i2c. Sources: #1, #2.\n"
        )
        self.assertTrue(checker.is_conforming(body))

    def test_agent_doc_stays_in_sync_with_checker(self) -> None:
        # Drift guard: the librarian agent must document the exact section header
        # and all three opportunity classes the checker enforces.
        doc = AGENT.read_text(encoding="utf-8")
        self.assertIn(checker.SECTION_HEADER, doc)
        for cls in checker.OPPORTUNITY_CLASSES:
            self.assertIn(cls, doc)

    def test_main_exit_codes(self) -> None:
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(CONFORMING)
            path = fh.name
        self.assertEqual(checker.main(["--body-file", path]), 0)


if __name__ == "__main__":
    unittest.main()
