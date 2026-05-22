"""Smoke tests for the experimental acoustic rig reference/templates."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "references" / "experimental-acoustic-rigs.md"
TEMPLATE_DIR = ROOT / "assets" / "templates" / "experimental-acoustic-rig"
SCRIPTS_DIR = ROOT / "scripts"

import sys

sys.path.insert(0, str(SCRIPTS_DIR))

import apply_experimental_rig_runtime_patch as patcher  # noqa: E402


class ExperimentalRigTemplates(unittest.TestCase):
    def test_reference_contains_routing_and_maturity_labels(self):
        text = REFERENCE.read_text(encoding="utf-8")
        self.assertIn("bench-rig packet before a performance-instrument packet", text)
        for label in (
            "concept",
            "bench_rig",
            "alpha_instrument",
            "performance_prototype",
            "production_packet",
        ):
            self.assertIn(label, text)
        self.assertIn("Coupled-System Modeling Caution", text)
        for required in (
            "README.md",
            "validation-plan.md",
            "risks.md",
            "variable-matrix.csv",
            "measurement-log-template.csv",
            "sensor-capture-checklist.md",
            "stored-energy-safety-checklist.md",
        ):
            self.assertIn(required, text)

    def test_stub_seed_list_matches_reference_minimum_outputs(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for required in (
            "README.md",
            "validation-plan.md",
            "risks.md",
            "variable-matrix.csv",
            "measurement-log-template.csv",
            "sensor-capture-checklist.md",
            "stored-energy-safety-checklist.md",
        ):
            self.assertIn(required, skill_text)

    def test_minimum_output_templates_exist(self):
        for filename in (
            "README.md",
            "validation-plan.md",
            "risks.md",
            "variable-matrix.csv",
            "measurement-log-template.csv",
            "sensor-capture-checklist.md",
            "stored-energy-safety-checklist.md",
        ):
            self.assertTrue((TEMPLATE_DIR / filename).is_file(), filename)

    def test_variable_matrix_columns(self):
        path = TEMPLATE_DIR / "variable-matrix.csv"
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            self.assertEqual(reader.fieldnames, [
                "variable_id",
                "subsystem",
                "variable",
                "baseline",
                "levels",
                "unit",
                "control_or_independent",
                "response_metrics",
                "safety_bound",
                "measurement_method",
                "notes",
            ])
            rows = list(reader)
        self.assertGreaterEqual(len(rows), 5)
        self.assertTrue(any(row["subsystem"] == "spring" for row in rows))
        self.assertTrue(any(row["subsystem"] == "membrane" for row in rows))

    def test_measurement_log_columns_cover_capture_fields(self):
        path = TEMPLATE_DIR / "measurement-log-template.csv"
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            fields = set(reader.fieldnames or [])
        for field in (
            "mic_distance_cm",
            "input_gain_db",
            "contact_mic_mounting",
            "environment",
            "excitation_method",
            "subjective_descriptors",
        ):
            self.assertIn(field, fields)

    def test_checklists_cover_sensor_and_stored_energy_terms(self):
        sensor = (TEMPLATE_DIR / "sensor-capture-checklist.md").read_text(encoding="utf-8")
        safety = (TEMPLATE_DIR / "stored-energy-safety-checklist.md").read_text(encoding="utf-8")
        for term in ("Mic distance", "Input gain", "Contact mic", "Environment", "Excitation"):
            self.assertIn(term, sensor)
        for term in ("string tension", "spring extension", "secondary restraint", "Stop Rules"):
            self.assertIn(term, safety)

    def test_runtime_patch_is_idempotent_and_contains_seed_list(self):
        original = "# Instrument Maker\n\n## Core Workflow\n\n1. Define the deliverable.\n"
        patched, changed = patcher.patch_text(original)
        self.assertTrue(changed)
        self.assertIn(patcher.START, patched)
        self.assertIn("bench-rig packet", patched)
        self.assertIn("performance-instrument packet", patched)
        for required in ("README.md", "validation-plan.md", "risks.md"):
            self.assertIn(required, patched)

        patched_again, changed_again = patcher.patch_text(patched)
        self.assertFalse(changed_again)
        self.assertEqual(patched, patched_again)

    def test_runtime_patch_cli_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text("# Instrument Maker\n", encoding="utf-8")
            self.assertEqual(patcher.main([str(path), "--check"]), 1)
            self.assertEqual(patcher.main([str(path)]), 0)
            self.assertEqual(patcher.main([str(path), "--check"]), 0)


if __name__ == "__main__":
    unittest.main()
