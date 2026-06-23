"""Tests for gemini_to_github.py (Story #411 — NotebookLM variant support)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from gemini_to_github import build_payloads, read_export


class TestBuildPayloads(unittest.TestCase):
    def test_notebooklm_variant_adds_needs_clarification(self):
        payloads = build_payloads(
            "conv-001",
            "## New idea\nBuild a mobile capture bridge",
            gemini_variant="notebooklm",
        )
        self.assertTrue(len(payloads) > 0)
        for p in payloads:
            self.assertIn("needs-clarification", p["labels"])
            self.assertEqual(p["gemini_variant"], "notebooklm")

    def test_plain_variant_has_empty_gemini_variant(self):
        payloads = build_payloads(
            "conv-002",
            "## New idea\nBuild a mobile capture bridge",
        )
        for p in payloads:
            # Domain router may independently add needs-clarification; what matters
            # is that the gemini_variant field is empty for a plain clip.
            self.assertEqual(p["gemini_variant"], "")

    def test_needs_clarification_not_duplicated(self):
        payloads = build_payloads(
            "conv-003",
            "## New idea\nSomething needs-clarification level unclear",
            gemini_variant="notebooklm",
        )
        for p in payloads:
            self.assertEqual(p["labels"].count("needs-clarification"), 1)

    def test_gemini_variant_in_payload_dict(self):
        payloads = build_payloads("conv-004", "incubate this idea", gemini_variant="notebooklm")
        self.assertTrue(all("gemini_variant" in p for p in payloads))


class TestCLIGeminiVariant(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_cli_gemini_variant_flag(self):
        import io
        import json
        from gemini_to_github import main

        export = self.tmpdir / "brainstorm.md"
        export.write_text(
            "---\nconversation_id: test-123\n---\n\n## New idea\nIncubate this brainstorm",
            encoding="utf-8",
        )
        buf = io.StringIO()
        orig_stdout = sys.stdout
        sys.stdout = buf
        try:
            rc = main(["prog", str(export), "--gemini-variant", "notebooklm"])
        finally:
            sys.stdout = orig_stdout
        self.assertEqual(rc, 0)
        payloads = json.loads(buf.getvalue())
        for p in payloads:
            self.assertIn("needs-clarification", p["labels"])


if __name__ == "__main__":
    unittest.main()
