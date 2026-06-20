#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "plugins" / "maker" / "skills" / "yoga-sequencer"
SCRIPT = SKILL_ROOT / "scripts" / "reverse_sequence_engine.py"


def load_module():
    spec = importlib.util.spec_from_file_location("yoga_reverse_sequence_engine", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["yoga_reverse_sequence_engine"] = module
    spec.loader.exec_module(module)
    return module


reverse = load_module()


PROGRAM = [
    "Viny = PL>CH+UD>DD",
    "DD // 5B",
    "RLH_r > CL_r // 5B > PT_r",
    "RLH_l > CL_l // 5B > PT_l",
    "FF > HL + FF > Viny",
]


class ReverseSequenceEngineTests(unittest.TestCase):
    def test_generates_sixty_minute_scaffold_from_five_line_shorthand(self) -> None:
        engine = reverse.ReverseSequenceEngine.load(SKILL_ROOT)
        result = engine.generate(reverse.ReverseSequenceInput(lines=PROGRAM, reviewer="tk"))
        self.assertEqual(result["class_summary"]["length_min"], 60)
        self.assertEqual(result["phases"][0]["start_min"], 0)
        self.assertEqual(result["phases"][-1]["end_min"], 60)
        self.assertEqual(result["quality_gate"]["status"], "approved")
        self.assertTrue(result["quality_gate"]["trusted_for_teaching"])

    def test_macro_expansion_and_transition_handoffs_are_present(self) -> None:
        engine = reverse.ReverseSequenceEngine.load(SKILL_ROOT)
        result = engine.generate(reverse.ReverseSequenceInput(lines=PROGRAM, reviewer="tk"))
        expanded_raw = [token["raw"] for token in result["expanded_tokens"]]
        self.assertIn("PL", expanded_raw)
        self.assertIn("CH", expanded_raw)
        self.assertTrue(any(handoff["target"] == "CL" for handoff in result["transition_handoffs"]))
        self.assertTrue(any("transcript_cue" in handoff for handoff in result["transition_handoffs"]))

    def test_without_reviewer_generation_is_not_autopilot_trusted(self) -> None:
        engine = reverse.ReverseSequenceEngine.load(SKILL_ROOT)
        result = engine.generate(reverse.ReverseSequenceInput(lines=PROGRAM))
        self.assertFalse(result["quality_gate"]["trusted_for_teaching"])
        self.assertTrue(any("human reviewer" in finding for finding in result["quality_gate"]["findings"]))

    def test_playlist_phase_map_carries_energy_and_cue_density(self) -> None:
        engine = reverse.ReverseSequenceEngine.load(SKILL_ROOT)
        result = engine.generate(reverse.ReverseSequenceInput(lines=PROGRAM, reviewer="tk"))
        self.assertEqual(len(result["playlist_phase_map"]), 6)
        for phase in result["playlist_phase_map"]:
            self.assertIn("energy", phase)
            self.assertIn("cue_density", phase)


if __name__ == "__main__":
    unittest.main()
