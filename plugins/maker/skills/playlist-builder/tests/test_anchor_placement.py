#!/usr/bin/env python3
"""Tests for placement.py — story #423.

Run from anywhere:
    python3 plugins/maker/skills/playlist-builder/tests/test_anchor_placement.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "placement.py"
)
SERIES_CTX = (
    Path(__file__).resolve().parent.parent
    / "contexts" / "series" / "4week-yoga-progression.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("placement", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["placement"] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_playlist_with_phases(phase_names: list[str]) -> list[dict]:
    return [
        {"artist": f"Artist{i}", "title": f"T{i}", "phase": p,
         "duration_ms": 300_000}
        for i, p in enumerate(phase_names)
    ]


class TestPlacementRule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        if SERIES_CTX.exists():
            cls.series = json.loads(SERIES_CTX.read_text(encoding="utf-8"))
        else:
            cls.series = None

    # --- PlacementRule.from_context ---

    def test_from_context_uses_episode_anchor_rules(self):
        episode = {
            "anchor_rules": {
                "lane_8": ["Heart Opener", "Sun B (Peak)"],
            }
        }
        rule = self.mod.PlacementRule.from_context("Lane 8", episode)
        self.assertEqual(rule.preferred_phases[0], "Heart Opener")

    def test_from_context_falls_back_to_defaults(self):
        episode = {}  # no anchor_rules
        rule = self.mod.PlacementRule.from_context("Lane 8", episode)
        self.assertEqual(rule.preferred_phases,
                         self.mod.ANCHOR_DEFAULT_PHASES["Lane 8"])

    def test_tinlicker_defaults_present(self):
        rule = self.mod.PlacementRule.from_context("Tinlicker", {})
        self.assertIn("Cool Down (Descent)", rule.preferred_phases)

    def test_lane8_defaults_present(self):
        rule = self.mod.PlacementRule.from_context("Lane 8", {})
        self.assertIn("Sun A (Rising)", rule.preferred_phases)

    # --- resolve_phase ---

    def test_resolve_prefers_first_available(self):
        # Lane 8 defaults: Sun A > Sun B > Heart Opener ...
        # Playlist has Sun B and Heart Opener but NOT Sun A
        playlist = _make_playlist_with_phases(
            ["Sun B (Peak)", "Heart Opener", "Cool Down (Descent)"]
        )
        rule = self.mod.PlacementRule.from_context("Lane 8", {})
        phase = rule.resolve_phase(playlist)
        self.assertEqual(phase, "Sun B (Peak)")

    def test_resolve_falls_back_to_first_track(self):
        playlist = _make_playlist_with_phases(["Custom Phase A"])
        rule = self.mod.PlacementRule.from_context("Lane 8", {})
        phase = rule.resolve_phase(playlist)
        self.assertEqual(phase, "Custom Phase A")

    def test_resolve_empty_playlist_returns_empty(self):
        rule = self.mod.PlacementRule.from_context("Tinlicker", {})
        phase = rule.resolve_phase([])
        self.assertEqual(phase, "")

    def test_tinlicker_prefers_cool_down(self):
        playlist = _make_playlist_with_phases(
            ["Sun B (Peak)", "Cool Down (Descent)", "Savasana"]
        )
        rule = self.mod.PlacementRule.from_context("Tinlicker", {})
        phase = rule.resolve_phase(playlist)
        self.assertEqual(phase, "Cool Down (Descent)")

    # --- build_placement_rules ---

    def test_build_returns_both_artists(self):
        rules = self.mod.build_placement_rules(
            ["Lane 8", "Tinlicker"], {}
        )
        self.assertIn("Lane 8", rules)
        self.assertIn("Tinlicker", rules)

    def test_build_uses_episode_context(self):
        episode = {"anchor_rules": {"lane_8": ["Savasana"]}}
        rules = self.mod.build_placement_rules(["Lane 8"], episode)
        self.assertEqual(rules["Lane 8"].preferred_phases, ["Savasana"])

    # --- integration with series context (if available) ---

    def test_week1_lane8_phase(self):
        if self.series is None:
            self.skipTest("series context not on this branch")
        ep1 = self.series["episodes"][0]
        rule = self.mod.PlacementRule.from_context("Lane 8", ep1)
        playlist = _make_playlist_with_phases(
            ["Opening / Centering", "Sun A (Rising)", "Sun B (Peak)",
             "Heart Opener", "Cool Down (Descent)", "Savasana"]
        )
        phase = rule.resolve_phase(playlist)
        # week 1 anchor_rules.lane_8 = [Sun A (Rising), Sun B (Peak), Heart Opener]
        self.assertEqual(phase, "Sun A (Rising)")

    def test_week4_tinlicker_phase(self):
        if self.series is None:
            self.skipTest("series context not on this branch")
        ep4 = self.series["episodes"][3]
        rule = self.mod.PlacementRule.from_context("Tinlicker", ep4)
        playlist = _make_playlist_with_phases(
            ["Sun B (Peak)", "Cool Down (Descent)", "Savasana (Extended)"]
        )
        phase = rule.resolve_phase(playlist)
        # week 4 anchor_rules.tinlicker = [Cool Down (Descent), Savasana (Extended)]
        self.assertEqual(phase, "Cool Down (Descent)")


if __name__ == "__main__":
    unittest.main()
