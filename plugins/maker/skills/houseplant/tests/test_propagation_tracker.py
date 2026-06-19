#!/usr/bin/env python3
"""Tests for scripts/propagation_tracker.py (#177).

Pure-Python, no Blender. Covers the lifecycle state machine, lineage queries
(ancestors/descendants/forest/tree, incl. external-parent + cycle safety), child
id derivation, and the rooting-window forecast (always a range).
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "propagation_tracker.py"


def load_module():
    spec = importlib.util.spec_from_file_location("propagation_tracker", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["propagation_tracker"] = module
    spec.loader.exec_module(module)
    return module


pt = load_module()

RECORDS = [
    {"plant_id": "ficus-01", "state": "independent"},
    {"plant_id": "ficus-01-c01", "parent_plant_id": "ficus-01", "state": "rooted"},
    {"plant_id": "ficus-01-c02", "parent_plant_id": "ficus-01", "state": "failed"},
    {"plant_id": "ficus-01-c01-c01", "parent_plant_id": "ficus-01-c01", "state": "started"},
]


class LifecycleTests(unittest.TestCase):
    def test_next_state_progression(self):
        self.assertEqual(pt.next_state("started"), "rooted")
        self.assertEqual(pt.next_state("rooted"), "potted_up")
        self.assertEqual(pt.next_state("potted_up"), "independent")

    def test_final_and_terminal_have_no_next(self):
        with self.assertRaises(ValueError):
            pt.next_state("independent")
        with self.assertRaises(ValueError):
            pt.next_state("failed")

    def test_valid_transition(self):
        self.assertTrue(pt.valid_transition("started", "rooted"))
        self.assertTrue(pt.valid_transition("rooted", "failed"))
        self.assertFalse(pt.valid_transition("started", "independent"))
        self.assertFalse(pt.valid_transition("independent", "failed"))

    def test_is_terminal(self):
        self.assertTrue(pt.is_terminal("failed"))
        self.assertTrue(pt.is_terminal("independent"))
        self.assertFalse(pt.is_terminal("rooted"))


class LineageTests(unittest.TestCase):
    def test_ancestors_chain(self):
        self.assertEqual(pt.ancestors(RECORDS, "ficus-01-c01-c01"), ["ficus-01-c01", "ficus-01"])
        self.assertEqual(pt.ancestors(RECORDS, "ficus-01"), [])

    def test_descendants_transitive(self):
        desc = pt.descendants(RECORDS, "ficus-01")
        self.assertIn("ficus-01-c01", desc)
        self.assertIn("ficus-01-c02", desc)
        self.assertIn("ficus-01-c01-c01", desc)

    def test_forest_roots_at_top(self):
        forest = pt.build_forest(RECORDS)
        self.assertEqual(list(forest.keys()), ["ficus-01"])
        self.assertIn("ficus-01-c01", forest["ficus-01"])

    def test_external_parent_becomes_root(self):
        recs = [{"plant_id": "child", "parent_plant_id": "external-not-in-set"}]
        forest = pt.build_forest(recs)
        self.assertIn("child", forest)  # not dropped

    def test_cycle_does_not_infinite_loop(self):
        recs = [
            {"plant_id": "a", "parent_plant_id": "b"},
            {"plant_id": "b", "parent_plant_id": "a"},
        ]
        # ancestors must terminate
        self.assertLessEqual(len(pt.ancestors(recs, "a")), 2)
        # render must terminate
        self.assertIn("##", pt.render_tree(recs))

    def test_render_tree_indents_children(self):
        out = pt.render_tree(RECORDS)
        self.assertIn("- ficus-01 [independent]", out)
        self.assertIn("  - ficus-01-c01 [rooted]", out)
        self.assertIn("    - ficus-01-c01-c01 [started]", out)

    def test_derive_child_id(self):
        self.assertEqual(pt.derive_child_id("ficus-01", 1), "ficus-01-c01")
        self.assertEqual(pt.derive_child_id("ficus-01", 12), "ficus-01-c12")


class RootingForecastTests(unittest.TestCase):
    def test_window_is_a_range(self):
        fc = pt.rooting_forecast("tip-cutting", "ficus", "warm", "2026-06-18")
        self.assertGreater(fc["high_days"], fc["low_days"])
        self.assertNotEqual(fc["window_start"], fc["window_end"])

    def test_air_layering_takes_longer_than_tip_cutting(self):
        tip = pt.rooting_forecast("tip-cutting", "ficus", "neutral", "2026-06-18")
        air = pt.rooting_forecast("air-layering", "ficus", "neutral", "2026-06-18")
        self.assertGreater(air["high_days"], tip["high_days"])

    def test_unknown_method_is_low_confidence(self):
        fc = pt.rooting_forecast("teleportation", "ficus", "warm", "2026-06-18")
        self.assertEqual(fc["confidence"], "low")

    def test_warm_roots_faster_than_cool(self):
        warm = pt.rooting_forecast("tip-cutting", "ficus", "warm", "2026-06-18")
        cool = pt.rooting_forecast("tip-cutting", "ficus", "cool", "2026-06-18")
        self.assertLess(warm["high_days"], cool["high_days"])

    def test_cadence_within_bounds(self):
        fc = pt.rooting_forecast("air-layering", "ficus", "neutral", "2026-06-18")
        self.assertGreaterEqual(fc["check_cadence_days"], 5)
        self.assertLessEqual(fc["check_cadence_days"], 14)


class CliTests(unittest.TestCase):
    def _run_stdin(self, payload: str) -> int:
        import io
        old = sys.stdin
        sys.stdin = io.StringIO(payload)
        try:
            return pt.main([])
        finally:
            sys.stdin = old

    def test_main_renders_lineage_and_forecast(self):
        payload = (
            '{"records":[{"plant_id":"a"},{"plant_id":"a-c01","parent_plant_id":"a"}],'
            '"propagation":{"method":"tip-cutting","species":"ficus","condition":"warm",'
            '"started_date":"2026-06-18"}}'
        )
        self.assertEqual(self._run_stdin(payload), 0)

    def test_main_rejects_empty_input(self):
        self.assertEqual(self._run_stdin('{}'), 2)


if __name__ == "__main__":
    unittest.main()
