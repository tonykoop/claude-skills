#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "plugins" / "maker" / "skills" / "yoga-sequencer"
SCRIPT = SKILL_ROOT / "scripts" / "phase_gate_ingest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("yoga_phase_gate_ingest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["yoga_phase_gate_ingest"] = module
    spec.loader.exec_module(module)
    return module


ingest_mod = load_module()


def sample_class(index: int = 1) -> dict:
    return {
        "class_id": f"class-{index:03d}",
        "teacher": "Tony",
        "duration_min": 60,
        "source": "synthetic test fixture",
        "segments": [
            {"start_sec": 0, "end_sec": 60, "kind": "audio", "text": "Opening bed", "pacing": "slow"},
            {"start_sec": 60, "end_sec": 120, "kind": "choreography", "shorthand": "DD // 5B", "text": "Hold down dog"},
            {"start_sec": 120, "end_sec": 150, "kind": "theme", "text": "Notice the space between effort and ease."},
        ],
    }


class PhaseGateIngestTests(unittest.TestCase):
    def test_anchor_class_produces_four_arrays(self) -> None:
        ingest = ingest_mod.PhaseGateIngest.load(SKILL_ROOT)
        parsed = ingest.parse_class(sample_class())
        self.assertEqual(set(parsed), {"metadata", "audio_timeline", "choreography_raw", "thematic_drops"})
        self.assertEqual(parsed["metadata"]["class_id"], "class-001")
        self.assertEqual(parsed["choreography_raw"][0]["pose_tokens"], ["DD"])
        self.assertIn("space", parsed["thematic_drops"][0]["terms"])

    def test_phase_gate_enforces_anchor_and_micro_batch_counts(self) -> None:
        ingest = ingest_mod.PhaseGateIngest.load(SKILL_ROOT)
        self.assertTrue(ingest.run_phase("anchor", [sample_class()]).go)
        too_many_anchor = ingest.run_phase("anchor", [sample_class(1), sample_class(2)])
        self.assertFalse(too_many_anchor.go)
        self.assertTrue(any("at most 1" in finding for finding in too_many_anchor.findings))

        micro = ingest.run_phase("micro_batch", [sample_class(i) for i in range(1, 6)])
        self.assertTrue(micro.go)
        too_few_micro = ingest.run_phase("micro_batch", [sample_class(1), sample_class(2)])
        self.assertFalse(too_few_micro.go)

    def test_bulk_phase_accepts_thirty_five_classes(self) -> None:
        ingest = ingest_mod.PhaseGateIngest.load(SKILL_ROOT)
        result = ingest.run_phase("bulk", [sample_class(i) for i in range(1, 36)])
        self.assertTrue(result.go)
        self.assertEqual(result.class_count, 35)
        self.assertEqual(len(result.parsed_classes), 35)

    def test_malformed_timing_fails_closed(self) -> None:
        ingest = ingest_mod.PhaseGateIngest.load(SKILL_ROOT)
        bad = sample_class()
        bad["segments"][0]["end_sec"] = 0
        result = ingest.run_phase("anchor", [bad])
        self.assertFalse(result.go)
        self.assertTrue(any("positive duration" in finding for finding in result.findings))


if __name__ == "__main__":
    unittest.main()
