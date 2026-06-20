#!/usr/bin/env python3
"""Tests for the savasana-backward planning engine (Refs #384)."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "plugins" / "maker" / "skills" / "yoga-sequencer"
SCRIPT = SKILL_ROOT / "scripts" / "savasana_backward.py"


def load_module():
    spec = importlib.util.spec_from_file_location("yoga_savasana_backward", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["yoga_savasana_backward"] = module
    spec.loader.exec_module(module)
    return module


sb = load_module()


def _spec(**overrides) -> sb.SavasanaSpec:
    base = dict(
        target_releases=["hip_flexors", "hamstrings", "thoracic_spine"],
        rest_quality=["symmetric_weight", "breath_below_ribs"],
        emotional_landing="earned ease",
        duration_min=4,
        class_length_min=60,
        level="mixed-level",
        reviewer="tk",
    )
    base.update(overrides)
    return sb.SavasanaSpec(**base)


class SavasanaSpecTests(unittest.TestCase):
    def test_from_dict_round_trips(self) -> None:
        data = {
            "target_releases": ["hip_flexors"],
            "rest_quality": ["symmetric_weight"],
            "emotional_landing": "earned ease",
            "reviewer": "tk",
        }
        spec = sb.SavasanaSpec.from_dict(data)
        self.assertEqual(spec.target_releases, ["hip_flexors"])
        self.assertEqual(spec.emotional_landing, "earned ease")
        self.assertEqual(spec.duration_min, 4)  # default

    def test_from_dict_applies_defaults(self) -> None:
        spec = sb.SavasanaSpec.from_dict({"target_releases": ["hamstrings"], "emotional_landing": "rest"})
        self.assertEqual(spec.class_length_min, 60)
        self.assertEqual(spec.level, "mixed-level")
        self.assertEqual(spec.reviewer, "")


class MinimumDisturbanceSetTests(unittest.TestCase):
    def test_generates_minimum_disturbance_set(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec())
        mds = result["minimum_disturbance_set"]
        self.assertGreater(len(mds), 0)
        # Primary movements (non-warm-up) justify with the emotional landing.
        # Warm-up movements carry a different prerequisite justification.
        primary = [m for m in mds if "warm_up" not in m["addresses"]]
        for m in primary:
            self.assertIn("earned ease", m["justification"])
        for m in mds:
            self.assertIsInstance(m["justification"], str)
            self.assertGreater(len(m["justification"]), 10)

    def test_all_requested_releases_are_addressed(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec())
        addressed = {r for m in result["minimum_disturbance_set"] for r in m["addresses"]}
        for release in ["hip_flexors", "hamstrings", "thoracic_spine"]:
            self.assertIn(release, addressed)

    def test_single_release_spec_produces_minimal_set(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec(target_releases=["hip_flexors"]))
        mds = result["minimum_disturbance_set"]
        # Should be lean — no more movements than releases + warm-up.
        self.assertLessEqual(len(mds), 4)

    def test_combinatorial_economy_avoids_redundant_movements(self) -> None:
        # thoracic_spine and shoulder_girdle share Thread the Needle — engine
        # should pick it once to cover both rather than two separate movements.
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec(target_releases=["thoracic_spine", "shoulder_girdle"]))
        tokens = [m["token"] for m in result["minimum_disturbance_set"]]
        self.assertEqual(len(tokens), len(set(tokens)), "Duplicate token in disturbance set")

    def test_bilateral_movements_are_flagged(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec(target_releases=["hip_flexors"]))
        bilateral = [m for m in result["minimum_disturbance_set"] if m["bilateral"]]
        self.assertGreater(len(bilateral), 0)


class PhaseAssignmentTests(unittest.TestCase):
    def test_phase_map_covers_full_class_length(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec())
        phases = result["phases"]
        self.assertEqual(phases[0]["start_min"], 0)
        self.assertEqual(phases[-1]["end_min"], 60)

    def test_savasana_phase_duration_matches_spec(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec(duration_min=5, class_length_min=60))
        savasana = next(p for p in result["phases"] if p["name"] == "savasana")
        self.assertEqual(savasana["end_min"], 60)
        self.assertEqual(savasana["start_min"], 55)

    def test_four_phases_present(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec())
        names = [p["name"] for p in result["phases"]]
        for expected in ("arrival_warm_up", "release_work", "integration_cooldown", "savasana"):
            self.assertIn(expected, names)

    def test_playlist_phase_map_has_energy_and_cue_density(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec())
        for phase in result["playlist_phase_map"]:
            self.assertIn("energy", phase)
            self.assertIn("cue_density", phase)

    def test_savasana_phase_has_minimal_cue_density(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec())
        savasana = next(p for p in result["phases"] if p["name"] == "savasana")
        self.assertEqual(savasana["cue_density"], "minimal")


class QualityGateTests(unittest.TestCase):
    def test_approved_with_full_spec_and_reviewer(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec())
        self.assertTrue(result["quality_gate"]["trusted_for_teaching"])
        self.assertEqual(result["quality_gate"]["status"], "approved")
        self.assertEqual(result["quality_gate"]["findings"], [])

    def test_no_reviewer_fails_gate(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec(reviewer=""))
        self.assertFalse(result["quality_gate"]["trusted_for_teaching"])
        self.assertTrue(
            any("reviewer" in f for f in result["quality_gate"]["findings"])
        )

    def test_empty_rest_quality_flagged(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec(rest_quality=[]))
        self.assertTrue(
            any("rest_quality" in f for f in result["quality_gate"]["findings"])
        )

    def test_empty_target_releases_raises(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        with self.assertRaises(sb.SavasanaBackwardError):
            engine.generate(_spec(target_releases=[]))

    def test_unknown_release_raises(self) -> None:
        engine = sb.SavasanaBackwardError
        with self.assertRaises(sb.SavasanaBackwardError):
            sb.SavasanaBackwardEngine().generate(_spec(target_releases=["not_a_release"]))


class OutputShapeTests(unittest.TestCase):
    def test_mode_field_is_savasana_backward(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec())
        self.assertEqual(result["mode"], "savasana_backward")

    def test_savasana_spec_embedded_in_output(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec())
        embedded = result["savasana_spec"]
        self.assertIn("hip_flexors", embedded["target_releases"])
        self.assertEqual(embedded["emotional_landing"], "earned ease")

    def test_class_summary_references_emotional_landing(self) -> None:
        engine = sb.SavasanaBackwardEngine()
        result = engine.generate(_spec(emotional_landing="quiet awareness"))
        self.assertIn("quiet awareness", result["class_summary"]["design_principle"])

    def test_from_dict_spec_produces_valid_output(self) -> None:
        spec = sb.SavasanaSpec.from_dict({
            "target_releases": ["hip_external_rotation", "low_back_traction"],
            "rest_quality": ["legs_heavy", "no_residual_gripping"],
            "emotional_landing": "complete neutrality",
            "reviewer": "tk",
        })
        result = sb.SavasanaBackwardEngine().generate(spec)
        self.assertTrue(result["quality_gate"]["trusted_for_teaching"])


class ReferenceDocTests(unittest.TestCase):
    def test_savasana_backward_md_exists(self) -> None:
        ref = SKILL_ROOT / "references" / "savasana-backward.md"
        self.assertTrue(ref.exists(), "references/savasana-backward.md not found")

    def test_savasana_backward_md_documents_available_releases(self) -> None:
        ref = SKILL_ROOT / "references" / "savasana-backward.md"
        text = ref.read_text(encoding="utf-8")
        for release in ("hip_flexors", "hamstrings", "thoracic_spine", "shoulder_girdle"):
            self.assertIn(release, text)

    def test_skill_md_documents_savasana_backward_mode(self) -> None:
        skill_md = SKILL_ROOT / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        self.assertIn("savasana-backward", text)
        self.assertIn("savasana_backward.py", text)
        self.assertIn("minimum disturbance", text)


if __name__ == "__main__":
    unittest.main()
