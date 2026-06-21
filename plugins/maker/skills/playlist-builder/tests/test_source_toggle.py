#!/usr/bin/env python3
"""Tests for source_toggle.py — story #424.

Run from anywhere:
    python3 plugins/maker/skills/playlist-builder/tests/test_source_toggle.py
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "source_toggle.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("source_toggle", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["source_toggle"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestSourceToggle(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    # --- validate_source_mode ---

    def test_library_mode_valid(self):
        result = self.mod.validate_source_mode("library")
        self.assertEqual(result, "library")

    def test_api_mode_valid(self):
        result = self.mod.validate_source_mode("api")
        self.assertEqual(result, "api")

    def test_invalid_mode_raises(self):
        with self.assertRaises(ValueError):
            self.mod.validate_source_mode("streaming")

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            self.mod.validate_source_mode("")

    # --- anchor_search_prompt ---

    def test_prompt_contains_artist(self):
        p = self.mod.anchor_search_prompt("Lane 8", "Sun B (Peak)", 2, "Expanding")
        self.assertIn("Lane 8", p)

    def test_prompt_contains_week(self):
        p = self.mod.anchor_search_prompt("Tinlicker", "Savasana", 4, "Integrating")
        self.assertIn("week:4", p)

    def test_prompt_contains_theme(self):
        p = self.mod.anchor_search_prompt("Lane 8", "Sun A (Rising)", 1, "Rooting")
        self.assertIn("rooting", p)

    def test_prompt_with_bpm_range(self):
        p = self.mod.anchor_search_prompt(
            "Lane 8", "Sun B (Peak)", 3, "Refining",
            bpm_min=121.5, bpm_max=136.0
        )
        self.assertIn("BPM:122-136", p)

    def test_prompt_without_bpm_no_bpm_clause(self):
        p = self.mod.anchor_search_prompt("Lane 8", "Sun B (Peak)", 1, "Rooting")
        self.assertNotIn("BPM:", p)

    # --- emit_api_search_block ---

    def test_emit_returns_string(self):
        episode = {"week": 1, "theme": "Rooting", "anchor_rules": {
            "lane_8": ["Sun A (Rising)"],
            "tinlicker": ["Cool Down (Descent)"],
        }}
        block = self.mod.emit_api_search_block(
            episode, ["Lane 8", "Tinlicker"]
        )
        self.assertIsInstance(block, str)

    def test_emit_contains_both_artists(self):
        episode = {"week": 2, "theme": "Expanding", "anchor_rules": {
            "lane_8": ["Sun B (Peak)"],
            "tinlicker": ["Cool Down (Descent)"],
        }}
        block = self.mod.emit_api_search_block(
            episode, ["Lane 8", "Tinlicker"]
        )
        self.assertIn("Lane 8", block)
        self.assertIn("Tinlicker", block)

    def test_emit_with_bpm_phases(self):
        episode = {"week": 3, "theme": "Refining", "anchor_rules": {
            "lane_8": ["Sun B (Peak)"],
        }}
        bpm_phases = [
            {"name": "Sun B (Peak)", "bpm_min": 121.5, "bpm_max": 136.0}
        ]
        block = self.mod.emit_api_search_block(
            episode, ["Lane 8"], bpm_phases=bpm_phases
        )
        self.assertIn("BPM:", block)

    def test_emit_without_anchor_rules_uses_any(self):
        episode = {"week": 4, "theme": "Integrating"}
        block = self.mod.emit_api_search_block(episode, ["Lane 8"])
        self.assertIn("(any)", block)


if __name__ == "__main__":
    unittest.main()
