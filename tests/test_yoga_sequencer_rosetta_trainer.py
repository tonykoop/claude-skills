#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "plugins" / "maker" / "skills" / "yoga-sequencer"
SCRIPT = SKILL_ROOT / "scripts" / "rosetta_trainer.py"


def load_module():
    spec = importlib.util.spec_from_file_location("yoga_rosetta_trainer", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["yoga_rosetta_trainer"] = module
    spec.loader.exec_module(module)
    return module


rosetta = load_module()


def sample_class(review_status: str = "approved") -> dict:
    return {
        "class_id": "class-2026-06-20-test",
        "source": "test fixture",
        "pairs": [
            {
                "id": "pair-001",
                "shorthand": "DD // 5B",
                "transcript": {
                    "start_sec": 0,
                    "end_sec": 45,
                    "text": "Settle into your breath and notice the space between effort and ease.",
                },
                "human_review": {"status": review_status, "reviewer": "tk"},
            },
            {
                "id": "pair-002",
                "shorthand": "DD > RLH_r > CL_r",
                "transcript": {
                    "start_sec": 45,
                    "end_sec": 75,
                    "text": "Step forward and rise into crescent with grounded attention.",
                },
                "human_review": {"status": review_status, "reviewer": "tk"},
            },
        ],
    }


class RosettaTrainerTests(unittest.TestCase):
    def test_aligns_shorthand_to_transcript_with_spacing_and_labels(self) -> None:
        trainer = rosetta.RosettaTrainer.load(SKILL_ROOT)
        result = trainer.train(sample_class())
        first = result["alignments"][0]
        second = result["alignments"][1]

        self.assertTrue(result["quality_gate"]["trusted_for_training"])
        self.assertEqual(first["somatic_spacing"]["duration_sec"], 45.0)
        self.assertEqual(first["somatic_spacing"]["explicit_breath_count"], 5.0)
        self.assertIn("breath", first["thematic_terms"])
        self.assertEqual(
            second["structural_transitions"],
            [{"origin": "DD", "target": "RLH"}, {"origin": "RLH", "target": "CL"}],
        )

    def test_human_review_gate_blocks_unapproved_pairs(self) -> None:
        trainer = rosetta.RosettaTrainer.load(SKILL_ROOT)
        result = trainer.train(sample_class(review_status="pending"))
        self.assertFalse(result["quality_gate"]["trusted_for_training"])
        self.assertEqual(result["quality_gate"]["status"], "needs_human_review")
        self.assertTrue(any("human review" in finding for finding in result["quality_gate"]["findings"]))

    def test_rejects_empty_transcript_span(self) -> None:
        trainer = rosetta.RosettaTrainer.load(SKILL_ROOT)
        data = sample_class()
        data["pairs"][0]["transcript"]["text"] = ""
        with self.assertRaises(rosetta.RosettaError):
            trainer.train(data)


if __name__ == "__main__":
    unittest.main()
