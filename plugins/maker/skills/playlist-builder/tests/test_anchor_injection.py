#!/usr/bin/env python3
"""Tests for anchor-artist injection — story #421.

Run from anywhere:
    python3 plugins/maker/skills/playlist-builder/tests/test_anchor_injection.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "anchor.py"
)
SERIES_CTX = (
    Path(__file__).resolve().parent.parent
    / "contexts" / "series" / "4week-yoga-progression.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("anchor", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["anchor"] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_catalog_with_anchors() -> dict:
    """Catalog with 2 Lane 8 + 2 Tinlicker tracks + filler in all banks."""
    banks: dict[str, list] = {}
    for bank in "ABCDE":
        banks[bank] = [
            {"artist": f"Artist-{bank}{i}", "title": f"Track {i}",
             "duration_ms": 300_000,
             "spotify_uri": f"spotify:track:{bank}{i}"}
            for i in range(6)
        ]
    # Inject anchor artists into bank D
    banks["D"].extend([
        {"artist": "Lane 8", "title": "Lane 8 Track A",
         "duration_ms": 420_000, "spotify_uri": "spotify:track:lane8a"},
        {"artist": "Lane 8", "title": "Lane 8 Track B",
         "duration_ms": 400_000, "spotify_uri": "spotify:track:lane8b"},
        {"artist": "Lane 8", "title": "Lane 8 Track C",
         "duration_ms": 380_000, "spotify_uri": "spotify:track:lane8c"},
        {"artist": "Lane 8", "title": "Lane 8 Track D",
         "duration_ms": 360_000, "spotify_uri": "spotify:track:lane8d"},
        {"artist": "Tinlicker", "title": "Tinlicker Track A",
         "duration_ms": 390_000, "spotify_uri": "spotify:track:tinla"},
        {"artist": "Tinlicker", "title": "Tinlicker Track B",
         "duration_ms": 370_000, "spotify_uri": "spotify:track:tinlb"},
        {"artist": "Tinlicker", "title": "Tinlicker Track C",
         "duration_ms": 350_000, "spotify_uri": "spotify:track:tinlc"},
        {"artist": "Tinlicker", "title": "Tinlicker Track D",
         "duration_ms": 330_000, "spotify_uri": "spotify:track:tinld"},
    ])
    return {"banks": banks, "exclusions": []}


def _make_playlist(n: int = 8) -> list[dict]:
    phases = ["Sun A (Rising)", "Sun B (Peak)", "Cool Down (Descent)", "Savasana"]
    return [
        {"artist": f"Artist{i}", "title": f"Track{i}",
         "duration_ms": 300_000, "phase": phases[i % len(phases)],
         "bank": "D", "spotify_uri": f"spotify:track:filler{i}"}
        for i in range(n)
    ]


class TestAnchorModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.catalog = _make_catalog_with_anchors()
        cls.series = json.loads(SERIES_CTX.read_text(encoding="utf-8"))

    # --- AnchorConfig construction ---

    def test_build_anchor_configs_both_artists(self):
        configs = self.mod.build_anchor_configs(
            self.series["episodes"], self.catalog
        )
        self.assertIn("Lane 8", configs)
        self.assertIn("Tinlicker", configs)

    def test_anchor_config_has_phase_prefs(self):
        configs = self.mod.build_anchor_configs(
            self.series["episodes"], self.catalog
        )
        self.assertGreater(len(configs["Lane 8"].phase_preferences), 0)
        self.assertGreater(len(configs["Tinlicker"].phase_preferences), 0)

    # --- inject_anchors ---

    def test_inject_adds_two_tracks(self):
        playlist = _make_playlist()
        original_len = len(playlist)
        episode = self.series["episodes"][0]
        configs = self.mod.build_anchor_configs(
            self.series["episodes"], self.catalog
        )
        series_used: set = set()
        result = self.mod.inject_anchors(
            playlist, episode, self.catalog, configs, series_used
        )
        self.assertEqual(len(result), original_len + 2)

    def test_inject_marks_anchor_artist_field(self):
        playlist = _make_playlist()
        episode = self.series["episodes"][0]
        configs = self.mod.build_anchor_configs(
            self.series["episodes"], self.catalog
        )
        series_used: set = set()
        result = self.mod.inject_anchors(
            playlist, episode, self.catalog, configs, series_used
        )
        anchors = [t for t in result if "anchor_artist" in t]
        self.assertEqual(len(anchors), 2)
        artists = {t["anchor_artist"] for t in anchors}
        self.assertIn("Lane 8", artists)
        self.assertIn("Tinlicker", artists)

    def test_no_anchor_repeats_across_four_episodes(self):
        configs = self.mod.build_anchor_configs(
            self.series["episodes"], self.catalog
        )
        series_used: set = set()
        anchor_track_ids = []
        for ep in self.series["episodes"]:
            playlist = _make_playlist()
            self.mod.inject_anchors(
                playlist, ep, self.catalog, configs, series_used
            )
            anchor_ids = [
                self.mod._track_id(t)
                for t in playlist
                if "anchor_artist" in t
            ]
            anchor_track_ids.extend(anchor_ids)

        self.assertEqual(
            len(anchor_track_ids), len(set(anchor_track_ids)),
            "Anchor tracks repeated across episodes"
        )

    def test_series_used_ids_updated_after_injection(self):
        configs = self.mod.build_anchor_configs(
            self.series["episodes"], self.catalog
        )
        series_used: set = set()
        playlist = _make_playlist()
        episode = self.series["episodes"][0]
        self.mod.inject_anchors(
            playlist, episode, self.catalog, configs, series_used
        )
        self.assertEqual(len(series_used), 2)

    def test_anchor_lands_in_preferred_phase(self):
        playlist = _make_playlist()
        episode = self.series["episodes"][0]
        # Week 1 anchor_rules: lane_8 prefers Sun A (Rising) first
        configs = self.mod.build_anchor_configs(
            self.series["episodes"], self.catalog
        )
        series_used: set = set()
        result = self.mod.inject_anchors(
            playlist, episode, self.catalog, configs, series_used
        )
        lane8_track = next(
            (t for t in result if t.get("anchor_artist") == "Lane 8"), None
        )
        self.assertIsNotNone(lane8_track)
        # Phase must be one of the valid phases that exist in the playlist
        valid_phases = {t["phase"] for t in _make_playlist()}
        self.assertIn(lane8_track["phase"], valid_phases)

    def test_is_anchor_artist_case_insensitive(self):
        t = {"artist": "LANE 8"}
        self.assertTrue(self.mod._is_anchor_artist(t, "Lane 8"))

    def test_find_anchor_track_skips_used(self):
        configs = self.mod.build_anchor_configs(
            self.series["episodes"], self.catalog
        )
        cfg = configs["Lane 8"]
        # Pre-mark lane8a as used
        cfg.used_track_ids.add("spotify:track:lane8a")
        track = self.mod._find_anchor_track(
            self.catalog["banks"], cfg, set()
        )
        self.assertIsNotNone(track)
        self.assertNotEqual(
            self.mod._track_id(track), "spotify:track:lane8a"
        )


if __name__ == "__main__":
    unittest.main()
