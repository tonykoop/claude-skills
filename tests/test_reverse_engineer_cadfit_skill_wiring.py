#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL = REPO_ROOT / "plugins" / "maker" / "skills" / "reverse-engineer" / "SKILL.md"


class CadfitSkillWiringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_mesh_scan_branch_has_narrow_trigger(self) -> None:
        self.assertIn("## CADFit Mesh/Scan Branch", self.text)
        self.assertIn("only when the user supplies a real local mesh", self.text)
        self.assertIn("Do not trigger CADFit for photo-only, sketch-only, named-object, dictated-description, or missing-image intake", self.text)

    def test_branch_names_all_cadfit_tools_in_order(self) -> None:
        for tool in (
            "scripts/cadfit_feature_extractor.py",
            "scripts/cadfit_test_cad_program.py",
            "scripts/cadfit_correction_loop.py",
        ):
            self.assertIn(tool, self.text)

    def test_graceful_fallback_message_is_present(self) -> None:
        self.assertIn("CADFit mesh/scan branch unavailable", self.text)
        self.assertIn("standard reverse-engineering ledger", self.text)

    def test_builder_handoff_alignment_is_preserved(self) -> None:
        self.assertIn("references/builder-handoff-template.md", self.text)
        self.assertIn("Mark the handoff `provisional`", self.text)
        self.assertIn("Never present CADFit IoU as builder readiness by itself", self.text)


if __name__ == "__main__":
    unittest.main()
