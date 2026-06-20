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
    / "yoga-sequencer"
    / "scripts"
    / "dji_mic_ingest.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("yoga_dji_mic_ingest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["yoga_dji_mic_ingest"] = module
    spec.loader.exec_module(module)
    return module


dji = load_module()


def manifest() -> dict:
    return {
        "capture_id": "dji-2026-06-20-test",
        "device": "DJI Mic 2",
        "audio_file": "private://captures/test.wav",
        "duration_sec": 3600,
        "quality": {
            "music_bed_db": -28,
            "movement_noise": "low",
            "breath_noise": "moderate",
            "dropouts": 0,
            "clipping": False,
        },
        "transcript": [
            {
                "start_sec": 0,
                "end_sec": 45,
                "text": "Settle into your breath and notice the space around effort.",
            }
        ],
        "timeline": [
            {
                "start_sec": 0,
                "end_sec": 300,
                "phase": "arrival",
                "energy": "low",
                "cue_density": "sparse",
            }
        ],
    }


class DjiMicIngestTests(unittest.TestCase):
    def test_splits_capture_into_language_and_audio_paths(self) -> None:
        split = dji.DjiMicIngest().split(manifest())
        self.assertTrue(split.quality_gate["capture_quality_ok"])
        self.assertTrue(split.path_a_language["rosetta_ready"])
        self.assertEqual(split.path_a_language["transcript_spans"][0]["end_sec"], 45.0)
        self.assertIn("breath", split.path_a_language["thematic_script"][0]["terms"])
        self.assertTrue(split.path_b_audio["playlist_handoff_ready"])
        self.assertEqual(split.path_b_audio["timeline"][0]["cue_density"], "sparse")

    def test_loud_music_bed_blocks_rosetta_but_preserves_outputs(self) -> None:
        data = manifest()
        data["quality"]["music_bed_db"] = -12
        split = dji.DjiMicIngest().split(data)
        self.assertFalse(split.quality_gate["capture_quality_ok"])
        self.assertFalse(split.path_a_language["rosetta_ready"])
        self.assertTrue(split.path_b_audio["playlist_handoff_ready"])
        self.assertTrue(any("music bed" in finding for finding in split.quality_gate["findings"]))

    def test_high_movement_noise_and_dropouts_are_quality_findings(self) -> None:
        data = manifest()
        data["quality"]["movement_noise"] = "high"
        data["quality"]["dropouts"] = 2
        split = dji.DjiMicIngest().split(data)
        findings = " ".join(split.quality_gate["findings"])
        self.assertIn("movement noise", findings)
        self.assertIn("dropouts", findings)

    def test_empty_transcript_text_is_rejected(self) -> None:
        data = manifest()
        data["transcript"][0]["text"] = ""
        with self.assertRaises(dji.DjiMicIngestError):
            dji.DjiMicIngest().split(data)


if __name__ == "__main__":
    unittest.main()
