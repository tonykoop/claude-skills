#!/usr/bin/env python3
"""Tests for release_hook.py — story #476.

Run from anywhere:
    python3 plugins/maker/skills/playlist-builder/tests/test_release_hook.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "release_hook.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("release_hook", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["release_hook"] = mod
    spec.loader.exec_module(mod)
    return mod


_SAMPLE_MIX_PLAN = {
    "routine_id": "test-routine-001",
    "style": "hip-hop",
    "total_duration_s": 240,
    "blocks": [
        {
            "name": "Peak",
            "bpm_target": 97,
            "duration_s": 120,
            "kinetic_texture": "tutting",
            "peak_count_s": 75.0,
            "candidates": [],
            "anchor_offset_s": 12.5,
            "anchor_fallback": False,
        }
    ],
}


def _write_choreo(tmp: Path, content: str = "# Hip-hop routine\n\nBlock 1: Peak\n") -> Path:
    p = tmp / "choreo.md"
    p.write_text(content, encoding="utf-8")
    return p


class TestCompileRelease(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_writes_three_expected_files(self):
        choreo = _write_choreo(self.tmp)
        out_dir = self.tmp / "bundle"
        self.mod.compile_release(
            _SAMPLE_MIX_PLAN, choreo, out_dir,
            timestamp="2026-06-22T18:30:00Z",
        )
        self.assertTrue((out_dir / "choreo_script.md").exists())
        self.assertTrue((out_dir / "audio_mix_plan.json").exists())
        self.assertTrue((out_dir / "provenance_block.json").exists())

    def test_provenance_has_sha256(self):
        choreo = _write_choreo(self.tmp)
        out_dir = self.tmp / "bundle"
        bundle = self.mod.compile_release(
            _SAMPLE_MIX_PLAN, choreo, out_dir,
            timestamp="2026-06-22T18:30:00Z",
        )
        prov = bundle.provenance
        self.assertIn("choreo_script_sha256", prov)
        self.assertIn("audio_mix_plan_sha256", prov)
        self.assertEqual(len(prov["choreo_script_sha256"]), 64)  # SHA-256 hex
        self.assertEqual(len(prov["audio_mix_plan_sha256"]), 64)

    def test_provenance_has_timestamp(self):
        choreo = _write_choreo(self.tmp)
        out_dir = self.tmp / "bundle"
        bundle = self.mod.compile_release(
            _SAMPLE_MIX_PLAN, choreo, out_dir,
            timestamp="2026-06-22T18:30:00Z",
        )
        self.assertEqual(bundle.provenance["generated_at"], "2026-06-22T18:30:00Z")

    def test_provenance_has_epic_ref(self):
        choreo = _write_choreo(self.tmp)
        out_dir = self.tmp / "bundle"
        bundle = self.mod.compile_release(
            _SAMPLE_MIX_PLAN, choreo, out_dir,
            timestamp="2026-06-22T18:30:00Z",
        )
        self.assertIn("471", bundle.provenance["epic"])

    def test_audio_mix_plan_is_valid_json(self):
        choreo = _write_choreo(self.tmp)
        out_dir = self.tmp / "bundle"
        self.mod.compile_release(
            _SAMPLE_MIX_PLAN, choreo, out_dir,
            timestamp="2026-06-22T18:30:00Z",
        )
        content = (out_dir / "audio_mix_plan.json").read_text(encoding="utf-8")
        parsed = json.loads(content)
        self.assertEqual(parsed["routine_id"], "test-routine-001")

    def test_choreo_script_copied_verbatim(self):
        content = "# Test\n\nSome choreography.\n"
        choreo = _write_choreo(self.tmp, content)
        out_dir = self.tmp / "bundle"
        self.mod.compile_release(
            _SAMPLE_MIX_PLAN, choreo, out_dir,
            timestamp="2026-06-22T18:30:00Z",
        )
        result = (out_dir / "choreo_script.md").read_text(encoding="utf-8")
        self.assertEqual(result, content)

    def test_output_dir_created_if_absent(self):
        choreo = _write_choreo(self.tmp)
        out_dir = self.tmp / "deep" / "nested" / "bundle"
        self.assertFalse(out_dir.exists())
        self.mod.compile_release(
            _SAMPLE_MIX_PLAN, choreo, out_dir,
            timestamp="2026-06-22T18:30:00Z",
        )
        self.assertTrue(out_dir.exists())

    def test_missing_choreo_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.mod.compile_release(
                _SAMPLE_MIX_PLAN,
                self.tmp / "does_not_exist.md",
                self.tmp / "bundle",
            )

    def test_no_studio_hook_url_gives_hook_sent_false(self):
        import os
        os.environ.pop("STUDIOPIPELINE_HOOK_URL", None)
        choreo = _write_choreo(self.tmp)
        out_dir = self.tmp / "bundle"
        bundle = self.mod.compile_release(
            _SAMPLE_MIX_PLAN, choreo, out_dir,
            timestamp="2026-06-22T18:30:00Z",
        )
        self.assertFalse(bundle.hook_sent)
        self.assertIsNone(bundle.hook_warning)

    def test_to_dict_is_serialisable(self):
        choreo = _write_choreo(self.tmp)
        out_dir = self.tmp / "bundle"
        bundle = self.mod.compile_release(
            _SAMPLE_MIX_PLAN, choreo, out_dir,
            timestamp="2026-06-22T18:30:00Z",
        )
        import json as _json
        _json.dumps(bundle.to_dict())  # should not raise

    def test_mix_plan_object_with_to_dict_accepted(self):
        class FakePlan:
            def to_dict(self):
                return {**_SAMPLE_MIX_PLAN}

        choreo = _write_choreo(self.tmp)
        out_dir = self.tmp / "bundle"
        # should not raise
        self.mod.compile_release(
            FakePlan(), choreo, out_dir,
            timestamp="2026-06-22T18:30:00Z",
        )


if __name__ == "__main__":
    unittest.main()
