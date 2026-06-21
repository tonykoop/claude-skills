#!/usr/bin/env python3
"""Tests for blueprint.py — story #422.

Run from anywhere:
    python3 plugins/maker/skills/playlist-builder/tests/test_sonic_blueprint.py
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "blueprint.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("blueprint", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["blueprint"] = mod
    spec.loader.exec_module(mod)
    return mod


def _sample_phases() -> list[dict]:
    return [
        {"name": "Opening / Centering", "bank": "A", "energy": 1,
         "min_tracks": 1, "max_tracks": 2, "window_min": [0, 5]},
        {"name": "Sun A (Rising)", "bank": "B", "energy": 5,
         "min_tracks": 2, "max_tracks": 3, "window_min": [5, 18]},
        {"name": "Sun B (Peak)", "bank": "D", "energy": 9,
         "min_tracks": 4, "max_tracks": 5, "window_min": [18, 42]},
        {"name": "Cool Down (Descent)", "bank": "E", "energy": 3,
         "min_tracks": 2, "max_tracks": 3, "window_min": [42, 55]},
        {"name": "Savasana", "bank": "A", "energy": 1,
         "min_tracks": 1, "max_tracks": 2, "window_min": [55, 65]},
    ]


class TestBlueprintConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    # --- for_week construction ---

    def test_for_week_valid(self):
        cfg = self.mod.BlueprintConfig.for_week(1)
        self.assertEqual(cfg.week, 1)
        self.assertAlmostEqual(cfg.bpm_scale, 1.00)
        self.assertEqual(cfg.energy_ceiling, 7)
        self.assertEqual(cfg.theme, "Rooting")

    def test_for_week_invalid_raises(self):
        with self.assertRaises(ValueError):
            self.mod.BlueprintConfig.for_week(99)

    def test_all_four_weeks_exist(self):
        for w in (1, 2, 3, 4):
            cfg = self.mod.BlueprintConfig.for_week(w)
            self.assertEqual(cfg.week, w)

    # --- BPM scaling ---

    def test_bpm_scale_week2(self):
        cfg = self.mod.BlueprintConfig.for_week(2)
        scaled = cfg.apply(_sample_phases())
        sun_b = next(p for p in scaled if p["name"] == "Sun B (Peak)")
        # baseline 118–132, × 1.02
        self.assertAlmostEqual(sun_b["bpm_min"], 118.0 * 1.02, places=1)
        self.assertAlmostEqual(sun_b["bpm_max"], 132.0 * 1.02, places=1)

    def test_bpm_scale_week4_lower(self):
        cfg = self.mod.BlueprintConfig.for_week(4)
        scaled = cfg.apply(_sample_phases())
        sun_b = next(p for p in scaled if p["name"] == "Sun B (Peak)")
        # baseline 118–132, × 0.98 < baseline
        self.assertLess(sun_b["bpm_min"], 118.0)

    def test_bpm_fields_present_for_known_phases(self):
        cfg = self.mod.BlueprintConfig.for_week(1)
        scaled = cfg.apply(_sample_phases())
        for phase in scaled:
            if phase["name"] != "Sun B (Peak)":  # spot-check known phases
                self.assertIn("bpm_min", phase)
                self.assertIn("bpm_max", phase)

    def test_unknown_phase_skips_bpm(self):
        cfg = self.mod.BlueprintConfig.for_week(1)
        unknown = [{"name": "XYZ Unknown Phase", "energy": 5}]
        result = cfg.apply(unknown)
        self.assertNotIn("bpm_min", result[0])
        self.assertNotIn("bpm_max", result[0])

    # --- energy ceiling ---

    def test_energy_ceiling_week1(self):
        cfg = self.mod.BlueprintConfig.for_week(1)
        phases = [{"name": "Sun B (Peak)", "energy": 9}]
        result = cfg.apply(phases)
        # Week 1 ceiling = 7; energy 9 should be clamped to 7
        self.assertEqual(result[0]["energy_effective"], 7)

    def test_energy_below_ceiling_unchanged(self):
        cfg = self.mod.BlueprintConfig.for_week(2)
        phases = [{"name": "Opening / Centering", "energy": 1}]
        result = cfg.apply(phases)
        self.assertEqual(result[0]["energy_effective"], 1)

    def test_energy_ceiling_week3_allows_9(self):
        cfg = self.mod.BlueprintConfig.for_week(3)
        phases = [{"name": "Sun B (Peak)", "energy": 9}]
        result = cfg.apply(phases)
        self.assertEqual(result[0]["energy_effective"], 9)

    # --- traceability fields ---

    def test_bpm_scale_field_in_output(self):
        cfg = self.mod.BlueprintConfig.for_week(2)
        result = cfg.apply(_sample_phases())
        for p in result:
            self.assertIn("bpm_scale", p)

    def test_energy_ceiling_field_in_output(self):
        cfg = self.mod.BlueprintConfig.for_week(1)
        result = cfg.apply(_sample_phases())
        for p in result:
            self.assertEqual(p["energy_ceiling"], 7)

    # --- immutability ---

    def test_original_phases_not_mutated(self):
        cfg = self.mod.BlueprintConfig.for_week(1)
        original = _sample_phases()
        cfg.apply(original)
        self.assertNotIn("bpm_min", original[0])


if __name__ == "__main__":
    unittest.main()
