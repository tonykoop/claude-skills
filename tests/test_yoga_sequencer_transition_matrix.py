#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "plugins" / "maker" / "skills" / "yoga-sequencer"
SCRIPT = SKILL_ROOT / "scripts" / "transition_matrix.py"


def load_module():
    spec = importlib.util.spec_from_file_location("yoga_transition_matrix", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["yoga_transition_matrix"] = module
    spec.loader.exec_module(module)
    return module


transition_matrix = load_module()


class TransitionMatrixTests(unittest.TestCase):
    def test_crescent_lunge_has_multiple_entry_pathways(self) -> None:
        matrix = transition_matrix.TransitionMatrix.load(SKILL_ROOT)
        crescent = matrix.for_target("CL")
        pathways = {transition.pathway for transition in crescent}
        self.assertGreaterEqual(len(crescent), 4)
        self.assertIn("step_through_r", pathways)
        self.assertIn("rise_from_runner_lunge_r", pathways)
        self.assertIn("step_back_to_lunge_r", pathways)
        self.assertIn("unwind_to_crescent_r", pathways)

    def test_transitions_carry_transcript_cues_and_handoff_crossfades(self) -> None:
        matrix = transition_matrix.TransitionMatrix.load(SKILL_ROOT)
        transition = matrix.between("PT", "CL")[0]
        handoff = matrix.as_handoff(transition)
        self.assertIn("Unwind from the prayer twist", handoff["transcript_cue"])
        self.assertEqual(handoff["crossfade_seconds"], matrix.crossfade_seconds("slow"))
        self.assertEqual(handoff["shorthand"], "PT_r > CL_r")

    def test_pacing_to_crossfade_orders_fast_before_slow(self) -> None:
        matrix = transition_matrix.TransitionMatrix.load(SKILL_ROOT)
        self.assertLess(matrix.crossfade_seconds("fast"), matrix.crossfade_seconds("medium"))
        self.assertLess(matrix.crossfade_seconds("medium"), matrix.crossfade_seconds("slow"))

    def test_unknown_pacing_is_rejected(self) -> None:
        matrix = transition_matrix.TransitionMatrix.load(SKILL_ROOT)
        with self.assertRaises(transition_matrix.TransitionMatrixError):
            matrix.crossfade_seconds("glacial")


if __name__ == "__main__":
    unittest.main()
