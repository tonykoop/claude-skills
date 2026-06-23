#!/usr/bin/env python3
"""Tests for movement_bridge.py — story #475.

Run from anywhere:
    python3 plugins/maker/skills/playlist-builder/tests/test_movement_bridge.py
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "movement_bridge.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("movement_bridge", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["movement_bridge"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Sample data — interpretive hip-hop routine, 4 blocks
# ---------------------------------------------------------------------------

SAMPLE_PAYLOAD = {
    "routine_id": "hip-hop-demo-001",
    "style": "hip-hop",
    "total_duration_s": 480,
    "source_engine": "movement_arts@1.0.0",
    "blocks": [
        {
            "name": "Warm-up",
            "bpm_target": 80,
            "duration_s": 120,
            "energy": 0.3,
        },
        {
            "name": "Groove Build",
            "bpm_target": 92,
            "bpm_range": [88, 98],
            "duration_s": 120,
            "energy": 0.5,
            "kinetic_texture": "fluid",
        },
        {
            "name": "Tutting Peak",
            "bpm_target": 97,
            "bpm_range": [90, 105],
            "duration_s": 120,
            "energy": 0.65,
            "kinetic_texture": "tutting",
            "peak_count_s": 75.0,
        },
        {
            "name": "Cool-down",
            "bpm_target": 78,
            "duration_s": 120,
            "energy": 0.2,
            "kinetic_texture": "fluid",
        },
    ],
}

CATALOG = [
    {
        "title": "Poly Rhythm X",
        "bpm": 97,
        "genre": "hip-hop",
        "tags": ["polyrhythmic", "hi-hats", "sub-bass"],
        "audio_features": {"energy": 0.65},
        "anchors": [
            {"anchor_ts_s": 62.5, "anchor_type": "drop", "confidence": 0.9, "source": "manual"}
        ],
    },
    {
        "title": "Pad Wave",
        "bpm": 92,
        "genre": "ambient",
        "tags": ["pads", "legato", "warm"],
        "audio_features": {"energy": 0.3},
    },
    {
        "title": "Clock Lock",
        "bpm": 80,
        "genre": "minimal techno",
        "tags": ["ticking", "mechanical"],
        "audio_features": {"energy": 0.3},
    },
    {
        "title": "Chill Drift",
        "bpm": 78,
        "genre": "lo-fi",
        "tags": ["pads", "ambient"],
        "audio_features": {"energy": 0.2},
    },
]


class TestValidatePayload(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_valid_payload_passes(self):
        self.mod.validate_payload(SAMPLE_PAYLOAD)  # should not raise

    def test_missing_routine_id_raises(self):
        bad = {**SAMPLE_PAYLOAD}
        del bad["routine_id"]
        with self.assertRaises(ValueError):
            self.mod.validate_payload(bad)

    def test_missing_bpm_target_in_block_raises(self):
        bad = {
            **SAMPLE_PAYLOAD,
            "blocks": [{"name": "A", "duration_s": 60}],
        }
        with self.assertRaises(ValueError):
            self.mod.validate_payload(bad)

    def test_negative_bpm_raises(self):
        bad = {
            **SAMPLE_PAYLOAD,
            "blocks": [{"name": "A", "bpm_target": -10, "duration_s": 60}],
        }
        with self.assertRaises(ValueError):
            self.mod.validate_payload(bad)

    def test_empty_blocks_raises(self):
        bad = {**SAMPLE_PAYLOAD, "blocks": []}
        with self.assertRaises(ValueError):
            self.mod.validate_payload(bad)


class TestBuildMixPlan(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.plan = cls.mod.build_mix_plan(SAMPLE_PAYLOAD, CATALOG)

    def test_one_mix_block_per_input_block(self):
        self.assertEqual(len(self.plan.blocks), len(SAMPLE_PAYLOAD["blocks"]))

    def test_routine_id_echoed(self):
        self.assertEqual(self.plan.routine_id, "hip-hop-demo-001")

    def test_style_echoed(self):
        self.assertEqual(self.plan.style, "hip-hop")

    def test_total_duration_echoed(self):
        self.assertAlmostEqual(self.plan.total_duration_s, 480.0)

    def test_each_block_has_candidates_key(self):
        for block in self.plan.blocks:
            self.assertIsInstance(block.candidates, list)

    def test_tutting_block_gets_polyrhythmic_candidate(self):
        # Block index 2 is "Tutting Peak" with kinetic_texture=tutting
        tutting_block = self.plan.blocks[2]
        titles = [c["title"] for c in tutting_block.candidates]
        self.assertIn("Poly Rhythm X", titles)

    def test_anchor_offset_applied_to_peak_block(self):
        # "Tutting Peak": peak_count_s=75, track drop at 62.5 → offset=12.5
        peak_block = self.plan.blocks[2]
        self.assertAlmostEqual(peak_block.anchor_offset_s, 12.5, places=1)
        self.assertFalse(peak_block.anchor_fallback)

    def test_block_without_peak_count_uses_fallback(self):
        # "Warm-up" has no peak_count_s
        warmup = self.plan.blocks[0]
        self.assertTrue(warmup.anchor_fallback)
        self.assertAlmostEqual(warmup.anchor_offset_s, 0.0)

    def test_to_dict_is_serialisable(self):
        import json
        d = self.plan.to_dict()
        # Should not raise
        json.dumps(d)

    def test_from_dict_shortcut(self):
        payload_obj = self.mod.MovementRoutinePayload.from_dict(SAMPLE_PAYLOAD)
        plan2 = self.mod.build_mix_plan(payload_obj, CATALOG)
        self.assertEqual(len(plan2.blocks), 4)

    def test_empty_catalog_yields_empty_candidates(self):
        plan = self.mod.build_mix_plan(SAMPLE_PAYLOAD, [])
        for block in plan.blocks:
            self.assertEqual(block.candidates, [])


if __name__ == "__main__":
    unittest.main()
