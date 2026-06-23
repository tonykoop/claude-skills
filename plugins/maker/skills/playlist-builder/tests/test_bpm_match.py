#!/usr/bin/env python3
"""Tests for bpm_match.py — story #472.

Run from anywhere:
    python3 plugins/maker/skills/playlist-builder/tests/test_bpm_match.py
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "bpm_match.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("bpm_match", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bpm_match"] = mod
    spec.loader.exec_module(mod)
    return mod


CATALOG = [
    {
        "title": "Exact Hit",
        "bpm": 97,
        "audio_features": {"energy": 0.65},
    },
    {
        "title": "Close Enough",
        "bpm": 99,
        "audio_features": {"energy": 0.70},
    },
    {
        "title": "Just In Range",
        "bpm": 107,
        "audio_features": {"energy": 0.80},
    },
    {
        "title": "Out Of Range",
        "bpm": 120,
        "audio_features": {"energy": 0.90},
    },
    {
        "title": "No BPM",
        "audio_features": {"energy": 0.50},
    },
]


class TestBpmCandidates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_exact_bpm_ranked_first(self):
        results = self.mod.bpm_candidates(
            CATALOG, bpm_target=97, bpm_range=(90, 110)
        )
        self.assertEqual(results[0]["title"], "Exact Hit")

    def test_out_of_range_excluded(self):
        results = self.mod.bpm_candidates(
            CATALOG, bpm_target=97, bpm_range=(90, 110)
        )
        titles = [t["title"] for t in results]
        self.assertNotIn("Out Of Range", titles)

    def test_track_without_bpm_excluded(self):
        results = self.mod.bpm_candidates(
            CATALOG, bpm_target=97, bpm_range=(90, 110)
        )
        titles = [t["title"] for t in results]
        self.assertNotIn("No BPM", titles)

    def test_energy_tie_break(self):
        # With energy_target=0.65, "Exact Hit" (energy 0.65) should beat
        # "Close Enough" (energy 0.70) even though both are close in BPM.
        results = self.mod.bpm_candidates(
            CATALOG,
            bpm_target=97,
            bpm_range=(90, 110),
            energy_target=0.65,
        )
        self.assertEqual(results[0]["title"], "Exact Hit")

    def test_empty_catalog_returns_empty_list(self):
        results = self.mod.bpm_candidates([], bpm_target=97)
        self.assertEqual(results, [])

    def test_top_n_respected(self):
        results = self.mod.bpm_candidates(
            CATALOG, bpm_target=100, bpm_range=(90, 115), top_n=2
        )
        self.assertLessEqual(len(results), 2)

    def test_default_range_is_plus_minus_10(self):
        # bpm_target=100 → default range [90, 110]; "Out Of Range" at 120 excluded
        results = self.mod.bpm_candidates(CATALOG, bpm_target=100)
        titles = [t["title"] for t in results]
        self.assertNotIn("Out Of Range", titles)


class TestMatchBlocks(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_output_parallel_to_input(self):
        blocks = [
            {"name": "Warm-up", "bpm_target": 80, "energy": 0.3},
            {"name": "Peak", "bpm_target": 97, "bpm_range": [90, 105], "energy": 0.65},
        ]
        results = self.mod.match_blocks(blocks, CATALOG)
        self.assertEqual(len(results), len(blocks))

    def test_each_block_has_candidates_key(self):
        blocks = [{"name": "A", "bpm_target": 97}]
        results = self.mod.match_blocks(blocks, CATALOG)
        self.assertIn("candidates", results[0])

    def test_warmup_with_low_bpm_returns_empty_candidates(self):
        # No tracks in CATALOG are near 70 BPM
        blocks = [{"name": "Warm-up", "bpm_target": 70}]
        results = self.mod.match_blocks(blocks, CATALOG)
        self.assertEqual(results[0]["candidates"], [])

    def test_original_block_fields_preserved(self):
        blocks = [{"name": "Peak", "bpm_target": 97, "energy": 0.65, "extra": "x"}]
        results = self.mod.match_blocks(blocks, CATALOG)
        self.assertEqual(results[0]["name"], "Peak")
        self.assertEqual(results[0]["extra"], "x")


if __name__ == "__main__":
    unittest.main()
