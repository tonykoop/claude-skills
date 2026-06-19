#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_hybrid_issue_template.py"
TEMPLATE = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "hybrid-idea.md"


def load_module():
    spec = importlib.util.spec_from_file_location("check_hybrid_issue_template", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_hybrid_issue_template"] = module
    spec.loader.exec_module(module)
    return module


checker = load_module()


class HybridTemplateCheckerTests(unittest.TestCase):
    def test_canonical_template_is_self_conforming(self) -> None:
        # Drift guard: the template must pass its own checker.
        body = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(checker.find_missing(body), [])
        self.assertTrue(checker.is_conforming(body))

    def test_template_names_the_three_required_artifacts(self) -> None:
        body = TEMPLATE.read_text(encoding="utf-8").lower()
        for artifact in checker.REQUIRED_ARTIFACTS:
            self.assertIn(artifact.lower(), body)

    def test_template_distinguishes_hw_sw_hybrid_sections(self) -> None:
        body = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("### Hardware (HW)", body)
        self.assertIn("### Software (SW)", body)
        self.assertIn("### Hybrid (system integration)", body)

    def test_blank_body_is_non_conforming(self) -> None:
        missing = checker.find_missing("just a freeform note, no structure")
        self.assertFalse(checker.is_conforming("freeform"))
        # Every backbone marker is reported missing.
        self.assertEqual(
            len(missing),
            len(checker.REQUIRED_SECTIONS) + len(checker.REQUIRED_ARTIFACTS),
        )

    def test_partial_body_reports_only_what_is_missing(self) -> None:
        body = "## Problem\nx\n## Intent\ny\n### Hybrid (system integration)\nz\n"
        missing = checker.find_missing(body)
        self.assertNotIn("## Problem", missing)
        self.assertNotIn("## Intent", missing)
        self.assertNotIn("### Hybrid (system integration)", missing)
        self.assertIn("ICD", missing)
        self.assertIn("Design Justification README", missing)

    def test_main_exit_codes(self) -> None:
        ok = checker.main(["--body-file", str(TEMPLATE)])
        self.assertEqual(ok, 0)


if __name__ == "__main__":
    unittest.main()
