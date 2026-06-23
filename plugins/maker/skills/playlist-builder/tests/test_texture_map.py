#!/usr/bin/env python3
"""Tests for texture_map.py — story #474.

Run from anywhere:
    python3 plugins/maker/skills/playlist-builder/tests/test_texture_map.py
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "texture_map.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("texture_map", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["texture_map"] = mod
    spec.loader.exec_module(mod)
    return mod


# Minimal stub catalog
CATALOG = [
    {
        "title": "ClockWork",
        "artist": "Glitch Co",
        "bpm": 98,
        "genre": "minimal techno",
        "tags": ["ticking", "mechanical"],
        "audio_features": {"energy": 0.7},
    },
    {
        "title": "Ocean Drift",
        "artist": "Pad World",
        "bpm": 75,
        "genre": "ambient",
        "tags": ["pads", "legato", "warm"],
        "audio_features": {"energy": 0.25},
    },
    {
        "title": "Box Theory",
        "artist": "Geometry",
        "bpm": 95,
        "genre": "hip-hop",
        "tags": ["polyrhythmic", "hi-hats", "sub-bass"],
        "audio_features": {"energy": 0.65},
    },
    {
        "title": "Generic Track",
        "artist": "Nobody",
        "bpm": 120,
        "genre": "pop",
        "tags": [],
        "audio_features": {"energy": 0.5},
    },
]


class TestSonicCriteriaForTexture(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_staccato_returns_ticking_tags(self):
        c = self.mod.sonic_criteria_for_texture("staccato")
        self.assertIn("ticking", c["tags"])
        self.assertIn("mechanical", c["tags"])

    def test_fluid_returns_pads_tags(self):
        c = self.mod.sonic_criteria_for_texture("fluid")
        self.assertIn("pads", c["tags"])
        self.assertIn("legato", c["tags"])

    def test_tutting_returns_polyrhythm_tags(self):
        c = self.mod.sonic_criteria_for_texture("tutting")
        self.assertIn("polyrhythmic", c["tags"])
        self.assertIn("hi-hats", c["tags"])

    def test_unknown_texture_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.mod.sonic_criteria_for_texture("boneless")

    def test_composite_texture_unions_tags(self):
        c = self.mod.sonic_criteria_for_texture("fluid+grounded")
        self.assertIn("pads", c["tags"])       # from fluid
        self.assertIn("bass-heavy", c["tags"]) # from grounded

    def test_composite_texture_intersects_avoid(self):
        # staccato avoids "pads"; tutting avoids "ambient"
        # intersection should be empty (or only shared avoid terms)
        c = self.mod.sonic_criteria_for_texture("staccato+tutting")
        # both avoid "ambient" — it must survive intersection
        self.assertIn("ambient", c["avoid"])

    def test_unknown_in_composite_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.mod.sonic_criteria_for_texture("fluid+boneless")


class TestFilterTracksByTexture(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_staccato_selects_ticking_track(self):
        result = self.mod.filter_tracks_by_texture(CATALOG, "staccato")
        titles = [t["title"] for t in result]
        self.assertIn("ClockWork", titles)

    def test_fluid_selects_pad_track(self):
        result = self.mod.filter_tracks_by_texture(CATALOG, "fluid")
        titles = [t["title"] for t in result]
        self.assertIn("Ocean Drift", titles)

    def test_tutting_selects_polyrhythmic_track(self):
        result = self.mod.filter_tracks_by_texture(CATALOG, "tutting")
        titles = [t["title"] for t in result]
        self.assertIn("Box Theory", titles)

    def test_staccato_excludes_pad_track(self):
        # staccato avoids "pads" — Ocean Drift should be excluded
        result = self.mod.filter_tracks_by_texture(CATALOG, "staccato")
        titles = [t["title"] for t in result]
        self.assertNotIn("Ocean Drift", titles)

    def test_empty_catalog_returns_empty_list(self):
        result = self.mod.filter_tracks_by_texture([], "fluid")
        self.assertEqual(result, [])

    def test_best_match_ranked_first(self):
        # ClockWork has 2 staccato tags; Generic Track has 0
        result = self.mod.filter_tracks_by_texture(CATALOG, "staccato")
        self.assertEqual(result[0]["title"], "ClockWork")

    def test_unknown_texture_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.mod.filter_tracks_by_texture(CATALOG, "floaty")


if __name__ == "__main__":
    unittest.main()
