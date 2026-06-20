#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "maker"
    / "skills"
    / "reverse-engineer"
    / "scripts"
    / "cadfit_correction_loop.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("cadfit_correction_loop", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["cadfit_correction_loop"] = module
    spec.loader.exec_module(module)
    return module


loop = load_module()


class CadfitCorrectionLoopTests(unittest.TestCase):
    def test_over_and_under_reconstruction_map_to_cut_and_union(self) -> None:
        score = {
            "status": "ok",
            "volumetric_iou": 0.7,
            "residuals": [
                {"kind": "over_reconstruction", "region": "boss_outer_wall"},
                {"kind": "under_reconstruction", "region": "missing_lug"},
            ],
        }
        actions = loop.correction_actions(score)
        self.assertEqual(actions[0]["action"], "cut")
        self.assertEqual(actions[0]["target"], "boss_outer_wall")
        self.assertEqual(actions[1]["action"], "union")
        self.assertEqual(actions[1]["target"], "missing_lug")

    def test_kernel_failure_simplifies_instead_of_throwing(self) -> None:
        actions = loop.correction_actions({"status": "kernel_failure", "volumetric_iou": 0.0})
        self.assertEqual(actions, [{"action": "simplify", "reason": "kernel/program failure", "target": "last risky operation"}])

    def test_backward_pruning_drops_only_noncritical_low_delta_ops(self) -> None:
        result = loop.backward_prune(
            [
                {"id": "base_extrude", "iou_delta_without": 0.5, "manufacturing_critical": True},
                {"id": "tiny_fillet", "iou_delta_without": 0.002},
                {"id": "mounting_boss", "iou_delta_without": 0.003, "manufacturing_critical": True},
            ],
            prune_tolerance=0.01,
        )
        self.assertEqual([op["id"] for op in result["dropped_operations"]], ["tiny_fillet"])
        self.assertEqual([op["id"] for op in result["kept_operations"]], ["base_extrude", "mounting_boss"])

    def test_termination_includes_manufacturing_review_guardrail(self) -> None:
        terminate, reasons = loop.should_terminate(
            {"status": "ok", "volumetric_iou": 0.95, "manufacturing_review": "unresolved"},
            iteration=2,
        )
        self.assertTrue(terminate)
        self.assertIn("target IoU reached", reasons)
        self.assertIn("manufacturing review unresolved", reasons)


if __name__ == "__main__":
    unittest.main()
