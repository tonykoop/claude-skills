#!/usr/bin/env python3
"""Tests for scripts/bloom_forecast.py (#173 bloom-window prediction).

Pure-Python, no Blender. Verifies the order-of-evidence (own log > species
baseline > generic), condition modulation, honest confidence tiers, and the
always-a-range invariant.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "bloom_forecast.py"


def load_module():
    spec = importlib.util.spec_from_file_location("bloom_forecast", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["bloom_forecast"] = module
    spec.loader.exec_module(module)
    return module


bf = load_module()


class ForecastTests(unittest.TestCase):
    def test_own_log_three_plus_is_high_confidence(self):
        fc = bf.forecast([16, 19, 18], "phalaenopsis", "neutral", "2026-06-18")
        self.assertEqual(fc["confidence"], "high")
        self.assertEqual(fc["basis"], "your-own-log")

    def test_own_log_one_or_two_is_medium(self):
        fc = bf.forecast([16, 19], "phalaenopsis", "neutral", "2026-06-18")
        self.assertEqual(fc["confidence"], "medium")
        fc1 = bf.forecast([16], "phalaenopsis", "neutral", "2026-06-18")
        self.assertEqual(fc1["confidence"], "medium")

    def test_no_log_known_species_is_low_baseline(self):
        fc = bf.forecast([], "schlumbergera", "neutral", "2026-06-18")
        self.assertEqual(fc["confidence"], "low")
        self.assertEqual(fc["basis"], "species-baseline-only")
        # Schlumbergera baseline 28-56 days.
        self.assertEqual((fc["low_days"], fc["high_days"]), (28, 56))

    def test_no_log_unknown_species_flags_provisional(self):
        fc = bf.forecast([], "mystery-orchid", "neutral", "2026-06-18")
        self.assertEqual(fc["basis"], "no-log-unknown-species")
        self.assertIn("confirm the species", fc["caveat"])

    def test_warm_shortens_cool_lengthens(self):
        warm = bf.forecast([], "hoya", "warm", "2026-06-18")
        cool = bf.forecast([], "hoya", "cool", "2026-06-18")
        self.assertLess(warm["high_days"], cool["high_days"])

    def test_window_is_always_a_range_never_single_date(self):
        for hist in ([20], [20, 20], [], [20, 20, 20]):
            fc = bf.forecast(hist, "citrus", "neutral", "2026-06-18")
            self.assertGreater(fc["high_days"], fc["low_days"])
            self.assertNotEqual(fc["window_start"], fc["window_end"])

    def test_window_dates_anchor_correctly(self):
        fc = bf.forecast([], "jade", "neutral", "2026-06-01")
        # jade 14-28 days from 2026-06-01.
        self.assertEqual(fc["window_start"], "2026-06-15")
        self.assertEqual(fc["window_end"], "2026-06-29")

    def test_cadence_within_bounds(self):
        for species in ("phalaenopsis", "schlumbergera", "citrus"):
            fc = bf.forecast([], species, "neutral", "2026-06-18")
            self.assertGreaterEqual(fc["cadence_days"], 3)
            self.assertLessEqual(fc["cadence_days"], 14)

    def test_species_baseline_lookup_case_insensitive(self):
        self.assertEqual(bf.species_baseline("Phalaenopsis"), (7, 21))
        self.assertIsNone(bf.species_baseline("unknown"))

    def test_render_includes_range_and_confidence(self):
        data = {"plant_id": "phal-01", "event": "swelling bud", "location": "spike",
                "stage": "swelling", "anchor_date": "2026-06-18"}
        fc = bf.forecast([], "phalaenopsis", "warm", "2026-06-18")
        out = bf.render(data, fc)
        self.assertIn("## Bloom Forecast — phal-01", out)
        self.assertIn("Forecast window:", out)
        self.assertIn("…", out)
        self.assertIn("Confidence:", out)
        self.assertIn("every", out)

    def test_main_with_stdin_like_input(self):
        import io
        payload = '{"plant_id":"x","species":"hoya","condition":"neutral","anchor_date":"2026-06-18"}'
        old = sys.stdin
        sys.stdin = io.StringIO(payload)
        try:
            rc = bf.main([])
        finally:
            sys.stdin = old
        self.assertEqual(rc, 0)

    def test_main_rejects_bad_date(self):
        import io
        old = sys.stdin
        sys.stdin = io.StringIO('{"anchor_date":"not-a-date"}')
        try:
            rc = bf.main([])
        finally:
            sys.stdin = old
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
