#!/usr/bin/env python3
"""Tests for sonic_anchor.py — story #473.

Run from anywhere:
    python3 plugins/maker/skills/playlist-builder/tests/test_sonic_anchor.py
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "sonic_anchor.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("sonic_anchor", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sonic_anchor"] = mod
    spec.loader.exec_module(mod)
    return mod


_DROP_ANCHOR = {"anchor_ts_s": 62.5, "anchor_type": "drop", "confidence": 0.95, "source": "manual"}
_LOW_CONF_ANCHOR = {"anchor_ts_s": 30.0, "anchor_type": "build", "confidence": 0.3}


class TestAnchorTag(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_from_dict_round_trips(self):
        tag = self.mod.AnchorTag.from_dict(_DROP_ANCHOR)
        d = tag.to_dict()
        self.assertAlmostEqual(d["anchor_ts_s"], 62.5)
        self.assertEqual(d["anchor_type"], "drop")
        self.assertEqual(d["source"], "manual")

    def test_invalid_anchor_type_raises(self):
        with self.assertRaises(ValueError):
            self.mod.AnchorTag(anchor_ts_s=10.0, anchor_type="explode")

    def test_confidence_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            self.mod.AnchorTag(anchor_ts_s=10.0, anchor_type="drop", confidence=1.5)

    def test_defaults(self):
        tag = self.mod.AnchorTag(anchor_ts_s=0.0, anchor_type="pause")
        self.assertEqual(tag.confidence, 1.0)
        self.assertEqual(tag.source, "manual")


class TestTagTrackAnchors(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_anchor_added_to_track(self):
        track = {"title": "T", "bpm": 97}
        result = self.mod.tag_track_anchors(track, [_DROP_ANCHOR])
        self.assertIn("anchors", result)
        self.assertEqual(len(result["anchors"]), 1)

    def test_original_track_unchanged(self):
        track = {"title": "T", "bpm": 97}
        self.mod.tag_track_anchors(track, [_DROP_ANCHOR])
        self.assertNotIn("anchors", track)  # original not mutated

    def test_multiple_anchors_stored(self):
        track = {"title": "T", "bpm": 97}
        anchors = [_DROP_ANCHOR, {"anchor_ts_s": 125.0, "anchor_type": "breakdown"}]
        result = self.mod.tag_track_anchors(track, anchors)
        self.assertEqual(len(result["anchors"]), 2)

    def test_invalid_anchor_raises(self):
        with self.assertRaises(ValueError):
            self.mod.tag_track_anchors({}, [{"anchor_ts_s": 10.0, "anchor_type": "unknown"}])


class TestAlignTimeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def _make_block(self, peak_s: float) -> dict:
        return {"name": "Peak", "bpm_target": 97, "peak_count_s": peak_s}

    def _make_track(self, anchors: list) -> dict:
        return {"title": "T", "bpm": 97, "anchors": anchors}

    def test_peak_count_aligns_to_drop(self):
        # peak_count_s=75, drop at 62.5 → offset = 75 - 62.5 = 12.5
        blocks = [self._make_block(75.0)]
        tracks = [self._make_track([_DROP_ANCHOR])]
        result = self.mod.align_timeline(blocks, tracks)
        self.assertAlmostEqual(result[0]["anchor_offset_s"], 12.5)

    def test_fallback_when_no_anchors(self):
        blocks = [self._make_block(75.0)]
        tracks = [self._make_track([])]
        result = self.mod.align_timeline(blocks, tracks)
        self.assertEqual(result[0]["anchor_offset_s"], 0.0)
        self.assertTrue(result[0]["anchor_fallback"])

    def test_fallback_when_all_low_confidence(self):
        blocks = [self._make_block(75.0)]
        tracks = [self._make_track([_LOW_CONF_ANCHOR])]
        result = self.mod.align_timeline(blocks, tracks)
        self.assertTrue(result[0]["anchor_fallback"])

    def test_offset_clamped_to_max(self):
        # peak at 200s, drop at 100s → raw offset 100s, clamped to 30s
        blocks = [self._make_block(200.0)]
        tracks = [self._make_track([{"anchor_ts_s": 100.0, "anchor_type": "drop", "confidence": 0.9}])]
        result = self.mod.align_timeline(blocks, tracks, max_offset_s=30.0)
        self.assertAlmostEqual(result[0]["anchor_offset_s"], 30.0)
        self.assertIn("anchor_warning", result[0])

    def test_length_mismatch_raises(self):
        with self.assertRaises(ValueError):
            self.mod.align_timeline([self._make_block(0)], [])

    def test_preferred_type_chosen_over_build(self):
        # Track has a "build" anchor at 50s and a "drop" at 65s; peak at 75s
        # Should pick the "drop" (preferred type) even though "build" is closer to 75s
        anchors = [
            {"anchor_ts_s": 50.0, "anchor_type": "build", "confidence": 0.9},
            {"anchor_ts_s": 65.0, "anchor_type": "drop", "confidence": 0.9},
        ]
        blocks = [self._make_block(75.0)]
        tracks = [self._make_track(anchors)]
        result = self.mod.align_timeline(blocks, tracks)
        self.assertEqual(result[0]["anchor_type_used"], "drop")
        self.assertAlmostEqual(result[0]["anchor_offset_s"], 75.0 - 65.0)

    def test_anchor_fallback_false_when_anchor_found(self):
        blocks = [self._make_block(75.0)]
        tracks = [self._make_track([_DROP_ANCHOR])]
        result = self.mod.align_timeline(blocks, tracks)
        self.assertFalse(result[0]["anchor_fallback"])


if __name__ == "__main__":
    unittest.main()
