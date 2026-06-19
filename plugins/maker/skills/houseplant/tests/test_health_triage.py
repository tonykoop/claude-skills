#!/usr/bin/env python3
"""Tests for scripts/health_triage.py (#175 plant-health check-engine light).

Pure-Python, no Blender. Verifies symptom->flag mapping, care cross-referencing,
the inspection-first / no-chemicals posture, and the pest/rot risk escalation.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "health_triage.py"


def load_module():
    spec = importlib.util.spec_from_file_location("health_triage", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["health_triage"] = module
    spec.loader.exec_module(module)
    return module


ht = load_module()


class TriageTests(unittest.TestCase):
    def test_known_symptom_maps_to_flag(self):
        flags = ht.triage(
            [{"symptom": "rot-risk", "photo": "p.jpg", "region": "base"}], [], "2026-06-18"
        )
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0].flag, "rot-risk")
        self.assertEqual(flags[0].category, ht.ROT)

    def test_unknown_symptom_is_surfaced_not_dropped(self):
        flags = ht.triage([{"symptom": "mystery-spots"}], [], "2026-06-18")
        self.assertEqual(len(flags), 1)
        self.assertIn("unrecognized", flags[0].cross_ref_note)
        self.assertEqual(flags[0].confidence, "low")

    def test_recent_repot_reinterprets_sudden_drop_as_stress(self):
        flags = ht.triage(
            [{"symptom": "sudden-leaf-drop"}],
            [{"type": "repotted", "date": "2026-06-12"}],
            "2026-06-18",
        )
        self.assertIn("stress", flags[0].cross_ref_note.lower())

    def test_old_care_event_outside_window_does_not_reinterpret(self):
        flags = ht.triage(
            [{"symptom": "sudden-leaf-drop"}],
            [{"type": "repotted", "date": "2026-01-01"}],
            "2026-06-18",
        )
        self.assertNotIn("favor transplant", flags[0].cross_ref_note.lower())

    def test_fertilizer_burn_cross_reference(self):
        flags = ht.triage(
            [{"symptom": "leaf-margin-burn"}],
            [{"type": "fertilized", "date": "2026-06-17"}],
            "2026-06-18",
        )
        self.assertIn("burn", flags[0].cross_ref_note.lower())

    def test_pest_flag_escalates_structural_risk(self):
        flags = ht.triage([{"symptom": "scale-suspected"}], [], "2026-06-18")
        risk = ht.structural_risk(flags)
        self.assertEqual(risk["risk"], "High")
        self.assertIn("scale-suspected", risk["reason"])

    def test_culture_flag_does_not_escalate_risk(self):
        flags = ht.triage([{"symptom": "chlorosis-lower-leaves"}], [], "2026-06-18")
        self.assertEqual(ht.structural_risk(flags)["risk"], "normal")

    def test_no_observations_is_normal_risk_and_no_flags(self):
        flags = ht.triage([], [], "2026-06-18")
        self.assertEqual(flags, [])
        self.assertEqual(ht.structural_risk(flags)["risk"], "normal")

    def test_rendered_event_never_recommends_chemicals(self):
        flags = ht.triage([{"symptom": "thrips-suspected", "photo": "x.jpg"}], [], "2026-06-18")
        out = ht.render_flag_event(flags[0], "2026-06-18")
        self.assertIn("health_flag_added", out)
        self.assertIn("none recommended", out)
        self.assertIn("inspection-first", out)

    def test_report_renders_risk_section(self):
        flags = ht.triage([{"symptom": "rot-risk"}], [], "2026-06-18")
        report = ht.render_report(flags, ht.structural_risk(flags), "2026-06-18")
        self.assertIn("## Structural-work risk", report)
        self.assertIn("High", report)

    def test_empty_report_message(self):
        report = ht.render_report([], ht.structural_risk([]), "2026-06-18")
        self.assertIn("no flags", report.lower())

    def test_all_rule_categories_are_known(self):
        valid = {ht.PEST, ht.ROT, ht.CULTURE, ht.STRESS}
        for rule in ht.SYMPTOM_RULES.values():
            self.assertIn(rule.category, valid)
            self.assertIn(rule.default_confidence, ht.VALID_CONFIDENCE)


if __name__ == "__main__":
    unittest.main()
