#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "plugins" / "maker" / "skills" / "reverse-engineer"
SCRIPT = SKILL_ROOT / "scripts" / "check_cadfit_license_gate.py"
REFERENCE = SKILL_ROOT / "references" / "cadfit-setup-license.md"


def load_module():
    spec = importlib.util.spec_from_file_location("check_cadfit_license_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_cadfit_license_gate"] = module
    spec.loader.exec_module(module)
    return module


checker = load_module()


class CadfitLicenseGateTests(unittest.TestCase):
    def test_reference_contains_required_license_gate_content(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        self.assertEqual(checker.missing_phrases(text), [])

    def test_reference_flags_redistribution_instead_of_silent_approval(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        self.assertIn("flagged, do not vendor CADFit code", text)
        self.assertIn("Not OK without legal/commercial permission", text)

    def test_runtime_matrix_names_degraded_hosts(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        self.assertIn("Codex CLI sandbox", text)
        self.assertIn("Mobile / zip-uploaded skill host", text)
        self.assertIn("Photo-only intake without watertight mesh", text)

    def test_main_passes_for_packaged_reference(self) -> None:
        self.assertEqual(checker.main([str(REFERENCE)]), 0)


if __name__ == "__main__":
    unittest.main()
