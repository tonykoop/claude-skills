#!/usr/bin/env python3
"""Tests for scripts/graft_heal_window.py (#176 heal window + risk verdict)."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "graft_heal_window.py"


def load_module():
    spec = importlib.util.spec_from_file_location("graft_heal_window", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["graft_heal_window"] = module
    spec.loader.exec_module(module)
    return module


ghw = load_module()


class HealWindowTests(unittest.TestCase):
    def test_window_is_a_month_range(self):
        hw = ghw.heal_window("approach", "readily", "warm", "2026-06-18")
        self.assertGreater(hw["high_months"], hw["low_months"])
        self.assertNotEqual(hw["window_start"], hw["window_end"])

    def test_multi_tree_takes_longer_than_approach(self):
        approach = ghw.heal_window("approach", "readily", "neutral", "2026-06-18")
        multi = ghw.heal_window("multi-tree-fusion", "readily", "neutral", "2026-06-18")
        self.assertGreater(multi["high_months"], approach["high_months"])

    def test_poorly_fusing_species_stretches_and_lowers_confidence(self):
        readily = ghw.heal_window("trunk-patch", "readily", "neutral", "2026-06-18")
        poorly = ghw.heal_window("trunk-patch", "poorly", "neutral", "2026-06-18")
        self.assertGreater(poorly["high_months"], readily["high_months"])
        self.assertEqual(poorly["confidence"], "low")

    def test_warm_heals_faster_than_cool(self):
        warm = ghw.heal_window("approach", "readily", "warm", "2026-06-18")
        cool = ghw.heal_window("approach", "readily", "cool", "2026-06-18")
        self.assertLess(warm["high_months"], cool["high_months"])

    def test_unknown_graft_type_is_low_confidence(self):
        self.assertEqual(ghw.heal_window("frankenstein", "readily", "warm", "2026-06-18")["confidence"], "low")

    def test_window_dates_anchor_from_grafted_date(self):
        hw = ghw.heal_window("approach", "readily", "neutral", "2026-01-01")
        # 12-24 months out -> roughly a year-plus later.
        self.assertTrue(hw["window_start"] > "2026-10-01")
        self.assertTrue(hw["window_end"] > hw["window_start"])


class RiskVerdictTests(unittest.TestCase):
    def test_healthy_fusing_is_medium(self):
        self.assertEqual(ghw.risk_verdict("readily", "healthy")["risk"], "Medium")

    def test_weak_plant_is_high_and_defers(self):
        v = ghw.risk_verdict("readily", "weak")
        self.assertEqual(v["risk"], "High")
        self.assertIn("defer", v["reason"])

    def test_pest_flagged_is_high(self):
        self.assertEqual(ghw.risk_verdict("readily", "pest-flagged")["risk"], "High")

    def test_poorly_fusing_species_is_high_even_if_healthy(self):
        v = ghw.risk_verdict("poorly", "healthy")
        self.assertEqual(v["risk"], "High")
        self.assertIn("fuse", v["reason"])


class RenderAndCliTests(unittest.TestCase):
    def test_render_includes_heal_and_risk_and_sim_only(self):
        data = {"plant_id": "ficus-01", "graft_type": "approach", "species_fusion": "readily",
                "condition": "warm", "grafted_date": "2026-06-18"}
        hw = ghw.heal_window("approach", "readily", "warm", "2026-06-18")
        risk = ghw.risk_verdict("readily", "healthy")
        out = ghw.render(data, hw, risk)
        self.assertIn("## Graft Heal Window — ficus-01", out)
        self.assertIn("warm-season growth", out)
        self.assertIn("Risk: Medium", out)
        self.assertIn("simulation-only", out)

    def _run_stdin(self, payload: str) -> int:
        import io
        old = sys.stdin
        sys.stdin = io.StringIO(payload)
        try:
            return ghw.main([])
        finally:
            sys.stdin = old

    def test_main_ok(self):
        self.assertEqual(self._run_stdin(
            '{"plant_id":"x","graft_type":"trunk-patch","species_fusion":"readily",'
            '"condition":"neutral","health":"healthy","grafted_date":"2026-06-18"}'), 0)

    def test_main_rejects_bad_date(self):
        self.assertEqual(self._run_stdin('{"grafted_date":"nope"}'), 2)


if __name__ == "__main__":
    unittest.main()
