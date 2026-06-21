#!/usr/bin/env python3
"""Tests for script-doctor scaffold — story #426.

Run from anywhere:
    python3 plugins/maker/skills/script-doctor/tests/test_scaffold.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "run_review.py"
)
SAMPLE = (
    Path(__file__).resolve().parent.parent / "samples" / "sample-script.md"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("run_review", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_review"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestScaffoldReview(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.sample_text = SAMPLE.read_text(encoding="utf-8")

    # --- review() returns correct shape ---

    def test_review_returns_dict(self):
        result = self.mod.review("Hello world.", channel="generic")
        self.assertIsInstance(result, dict)

    def test_review_has_passes_and_greenlight(self):
        result = self.mod.review("Hello world.")
        self.assertIn("passes", result)
        self.assertIn("greenlight", result)

    def test_three_passes_returned(self):
        result = self.mod.review("Hello world.")
        self.assertEqual(len(result["passes"]), 3)

    def test_pass_names(self):
        result = self.mod.review("Hello world.")
        names = {p["pass"] for p in result["passes"]}
        self.assertIn("table_read", names)
        self.assertIn("structural_polish", names)
        self.assertIn("logistical_breakdown", names)

    def test_each_pass_has_score(self):
        result = self.mod.review("Hello world.")
        for p in result["passes"]:
            self.assertIn("score", p)
            self.assertIsInstance(p["score"], float)

    def test_each_pass_has_flags(self):
        result = self.mod.review("Hello world.")
        for p in result["passes"]:
            self.assertIn("flags", p)
            self.assertIsInstance(p["flags"], list)

    # --- greenlight gate ---

    def test_greenlight_has_verdict(self):
        result = self.mod.review("Hello world.")
        gl = result["greenlight"]
        self.assertIn("greenlight", gl)
        self.assertIn(gl["greenlight"], ("PASS", "FAIL"))

    def test_greenlight_has_composite_score(self):
        result = self.mod.review("Hello world.")
        self.assertIn("composite_score", result["greenlight"])

    def test_greenlight_has_ready_line(self):
        result = self.mod.review("Hello world.")
        ready = result["greenlight"]["ready_line"]
        self.assertTrue(ready.startswith("READY:"))

    def test_no_blockers_yields_pass(self):
        result = self.mod.review("Hello world.", channel="generic")
        self.assertEqual(result["greenlight"]["greenlight"], "PASS")

    # --- channel parameter ---

    def test_channel_passed_to_table_read(self):
        result = self.mod.review("Hello world.", channel="yoga")
        tr = next(p for p in result["passes"] if p["pass"] == "table_read")
        self.assertEqual(tr["archetype"], "yoga")

    def test_generic_channel_default(self):
        result = self.mod.review("Hello world.")
        tr = next(p for p in result["passes"] if p["pass"] == "table_read")
        self.assertEqual(tr["archetype"], "generic")

    # --- single pass ---

    def test_single_pass_table_read(self):
        result = self.mod.review("Hello world.", single_pass="table-read")
        self.assertEqual(len(result["passes"]), 1)
        self.assertEqual(result["passes"][0]["pass"], "table_read")

    def test_single_pass_structural_polish(self):
        result = self.mod.review("Hello world.", single_pass="structural-polish")
        self.assertEqual(len(result["passes"]), 1)
        self.assertEqual(result["passes"][0]["pass"], "structural_polish")

    # --- sample script end-to-end ---

    def test_sample_script_runs_end_to_end(self):
        result = self.mod.review(self.sample_text, channel="ai_agentic")
        self.assertIn("greenlight", result)
        self.assertIn("passes", result)
        self.assertEqual(len(result["passes"]), 3)

    def test_sample_script_estimated_runtime(self):
        result = self.mod.review(self.sample_text, channel="ai_agentic")
        tr = next(p for p in result["passes"] if p["pass"] == "table_read")
        # ~250 words → ~60s at 2.5 wps — just verify it's a positive number
        self.assertGreater(tr["estimated_runtime_sec"], 0)

    # --- rendering ---

    def test_render_review_returns_string(self):
        result = self.mod.review("Hello world.")
        rendered = self.mod._render_review(result["passes"], result["greenlight"])
        self.assertIsInstance(rendered, str)
        self.assertIn("GREENLIGHT VERDICT", rendered)
        self.assertIn("READY:", rendered)

    # --- CLI ---

    def test_cli_with_script_file(self):
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = self.mod.main(["--script", str(SAMPLE), "--channel", "ai_agentic"])
        output = buf.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("GREENLIGHT", output)

    def test_cli_json_output(self):
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.mod.main(["--script", str(SAMPLE), "--json"])
        data = json.loads(buf.getvalue())
        self.assertIn("passes", data)
        self.assertIn("greenlight", data)

    def test_cli_missing_script_exits_nonzero(self):
        exit_code = self.mod.main(["--script", "/nonexistent/path.md"])
        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
