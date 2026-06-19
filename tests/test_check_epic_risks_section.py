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
    / "check_epic_risks_section.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("check_epic_risks_section", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_epic_risks_section"] = module
    spec.loader.exec_module(module)
    return module


checker = load_module()


CONFORMING_EPIC = textwrap.dedent(
    """
    **Tracking epic.** Build the thing. Source: doc.md (2026-06-18).

    ## Vision
    A clean vision.

    ## Stories
    - [ ] #2 - first story (sp 3)

    **Rollup:** ~3 points.

    ### Technical Risks & Assumptions

    _Red-Team pass (Devil's Advocate role - agents/devils-advocate.md). Optimist
    breakdown above is unchanged._

    - **Assumption:** the URDF importer keeps joint order -> kinematic check breaks if not.
    - **Weakest story:** #2 first story - depends on an unbuilt parser.

    ## Links
    - Source: doc.md
    """
).strip()


class EpicRisksCheckerTests(unittest.TestCase):
    def test_conforming_epic_passes(self) -> None:
        self.assertEqual(checker.find_problems(CONFORMING_EPIC), [])
        self.assertTrue(checker.is_conforming(CONFORMING_EPIC))

    def test_missing_section_is_flagged(self) -> None:
        body = "## Vision\nx\n## Stories\n- [ ] #2 - s (sp 3)\n**Rollup:** ~3 points.\n## Links\n-\n"
        problems = checker.find_problems(body)
        self.assertTrue(any("missing" in p for p in problems))
        self.assertFalse(checker.is_conforming(body))

    def test_unattributed_section_is_flagged(self) -> None:
        body = (
            "### Technical Risks & Assumptions\n\n"
            "- **Assumption:** the importer keeps joint order -> check breaks otherwise.\n"
        )
        problems = checker.find_problems(body)
        self.assertTrue(any("attributed" in p for p in problems))

    def test_boilerplate_section_is_flagged(self) -> None:
        body = (
            "### Technical Risks & Assumptions\n\n"
            "_Red-Team pass (Devil's Advocate role)._\n\n"
            "- There may be unforeseen risks.\n"
        )
        problems = checker.find_problems(body)
        self.assertTrue(any("boilerplate" in p for p in problems))

    def test_empty_section_is_flagged(self) -> None:
        body = "### Technical Risks & Assumptions\n\n_Red-Team pass._\n\n## Links\n-\n"
        problems = checker.find_problems(body)
        self.assertTrue(any("substantive" in p for p in problems))

    def test_main_exit_codes(self, tmp=None) -> None:
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(CONFORMING_EPIC)
            path = fh.name
        self.assertEqual(checker.main(["--body-file", path]), 0)


if __name__ == "__main__":
    unittest.main()
