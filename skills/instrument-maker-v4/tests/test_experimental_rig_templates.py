"""Smoke tests for the experimental acoustic rig reference/templates."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "references" / "experimental-acoustic-rigs.md"
TEMPLATE_DIR = ROOT / "assets" / "templates" / "experimental-acoustic-rig"


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


if __name__ == "__main__":
    unittest.main()
