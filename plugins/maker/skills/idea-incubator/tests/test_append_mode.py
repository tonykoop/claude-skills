"""Tests for append_mode.py (Story #410 — CREATE_MODE / APPEND_MODE dedup)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from append_mode import detect_mode, extract_new_content, stamp_processed, clear_stamp


class TestDetectMode(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.d = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _file(self, name: str, content: str) -> Path:
        p = self.d / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_new_file_is_create(self):
        p = self._file("new.md", "# Fresh content\nIncubate this idea")
        mode, pos = detect_mode(p)
        self.assertEqual(mode, "CREATE")
        self.assertEqual(pos, 0)

    def test_missing_file_is_create(self):
        mode, pos = detect_mode(self.d / "nonexistent.md")
        self.assertEqual(mode, "CREATE")
        self.assertEqual(pos, 0)

    def test_stamped_file_is_append(self):
        p = self._file("stamped.md", "# Content\n<!-- incubator-processed-pos: 20 -->\n")
        mode, pos = detect_mode(p)
        self.assertEqual(mode, "APPEND")
        self.assertEqual(pos, 20)

    def test_marker_with_extra_spaces(self):
        p = self._file("spaced.md", "x\n<!--  incubator-processed-pos:  42  -->\n")
        mode, pos = detect_mode(p)
        self.assertEqual(mode, "APPEND")
        self.assertEqual(pos, 42)

    def test_multiple_markers_uses_last(self):
        content = (
            "<!-- incubator-processed-pos: 10 -->\n"
            "more content\n"
            "<!-- incubator-processed-pos: 50 -->\n"
        )
        p = self._file("multi.md", content)
        mode, pos = detect_mode(p)
        self.assertEqual(mode, "APPEND")
        self.assertEqual(pos, 50)

    def test_invalid_pos_falls_back_to_create(self):
        p = self._file("bad.md", "<!-- incubator-processed-pos: 99999999 -->\n")
        # 99999999 > file size → invalid
        mode, pos = detect_mode(p)
        self.assertEqual(mode, "CREATE")

    def test_pos_zero_stamped_is_create(self):
        # pos == 0 after stamp means "whole file processed"; still CREATE-safe
        p = self._file("zero.md", "<!-- incubator-processed-pos: 0 -->\n")
        mode, pos = detect_mode(p)
        # pos == 0: valid stamp but returns CREATE behavior (re-process whole file)
        self.assertEqual(mode, "CREATE")
        self.assertEqual(pos, 0)


class TestExtractNewContent(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.d = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_pos_zero_returns_whole_file(self):
        p = self.d / "whole.md"
        p.write_text("hello world", encoding="utf-8")
        content = extract_new_content(p, 0)
        self.assertEqual(content, "hello world")

    def test_delta_returns_appended_only(self):
        original = "# Original\nFirst idea\n"
        appended = "# New section\nSecond idea\n"
        p = self.d / "delta.md"
        p.write_text(original + appended, encoding="utf-8")
        pos = len(original.encode("utf-8"))
        content = extract_new_content(p, pos)
        self.assertEqual(content, appended)

    def test_no_new_content_returns_empty(self):
        text = "# Content"
        p = self.d / "static.md"
        p.write_text(text, encoding="utf-8")
        pos = len(text.encode("utf-8"))
        content = extract_new_content(p, pos)
        self.assertEqual(content, "")

    def test_pos_beyond_file_returns_empty(self):
        p = self.d / "short.md"
        p.write_text("short", encoding="utf-8")
        content = extract_new_content(p, 10000)
        self.assertEqual(content, "")

    def test_unicode_content_handled(self):
        text = "café ☕\n"
        p = self.d / "unicode.md"
        p.write_text(text, encoding="utf-8")
        raw_len = len(text.encode("utf-8"))
        appended = "après café\n"
        p.write_text(text + appended, encoding="utf-8")
        content = extract_new_content(p, raw_len)
        self.assertEqual(content, appended)


class TestStampProcessed(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.d = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _file(self, name: str, content: str) -> Path:
        p = self.d / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_stamps_at_eof_by_default(self):
        content = "# Content\n"
        p = self._file("s.md", content)
        expected_pos = len(content.encode("utf-8"))
        stamped_pos = stamp_processed(p)
        self.assertEqual(stamped_pos, expected_pos)

    def test_marker_present_in_file_after_stamp(self):
        p = self._file("m.md", "text\n")
        stamp_processed(p)
        body = p.read_text()
        self.assertIn("incubator-processed-pos:", body)

    def test_stamp_at_explicit_pos(self):
        p = self._file("explicit.md", "hello world\n")
        pos = stamp_processed(p, at_pos=5)
        self.assertEqual(pos, 5)
        mode, detected = detect_mode(p)
        self.assertEqual(detected, 5)

    def test_idempotent_same_pos(self):
        p = self._file("idem.md", "same content\n")
        pos1 = stamp_processed(p)
        text_after_first = p.read_text()
        pos2 = stamp_processed(p)
        text_after_second = p.read_text()
        self.assertEqual(pos1, pos2)
        self.assertEqual(text_after_first, text_after_second)

    def test_advances_marker_on_second_stamp(self):
        content = "# Original\n"
        p = self._file("adv.md", content)
        stamp_processed(p)
        # Append more content
        with p.open("a", encoding="utf-8") as f:
            f.write("# Appended\n")
        pos2 = stamp_processed(p)
        # New pos should be larger than original
        self.assertGreater(pos2, len(content.encode("utf-8")))

    def test_stamp_then_detect_returns_append(self):
        p = self._file("cycle.md", "# Brainstorm\nIncubate this\n")
        stamp_processed(p)
        mode, pos = detect_mode(p)
        self.assertEqual(mode, "APPEND")
        self.assertGreater(pos, 0)

    def test_does_not_duplicate_markers(self):
        p = self._file("nodup.md", "content\n")
        stamp_processed(p)
        # Append more text, stamp again
        with p.open("a", encoding="utf-8") as f:
            f.write("more\n")
        stamp_processed(p)
        body = p.read_text()
        count = body.count("incubator-processed-pos:")
        self.assertEqual(count, 1)


class TestClearStamp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.d = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_removes_marker(self):
        p = self.d / "c.md"
        p.write_text("content\n<!-- incubator-processed-pos: 8 -->\n", encoding="utf-8")
        removed = clear_stamp(p)
        self.assertTrue(removed)
        mode, pos = detect_mode(p)
        self.assertEqual(mode, "CREATE")
        self.assertEqual(pos, 0)

    def test_no_marker_returns_false(self):
        p = self.d / "clean.md"
        p.write_text("no markers here\n", encoding="utf-8")
        removed = clear_stamp(p)
        self.assertFalse(removed)

    def test_missing_file_returns_false(self):
        removed = clear_stamp(self.d / "missing.md")
        self.assertFalse(removed)

    def test_content_preserved_after_clear(self):
        original = "# My brainstorm\nSome ideas here\n"
        p = self.d / "preserved.md"
        p.write_text(original, encoding="utf-8")
        stamp_processed(p)
        clear_stamp(p)
        body = p.read_text()
        self.assertIn("My brainstorm", body)
        self.assertIn("Some ideas here", body)
        self.assertNotIn("incubator-processed-pos:", body)


class TestRoundTrip(unittest.TestCase):
    """Integration tests: detect → extract → stamp → detect cycle."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.d = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_full_create_then_append_cycle(self):
        p = self.d / "cycle.md"
        original = "# Session 1\nIncubate this idea\n"
        p.write_text(original, encoding="utf-8")

        # --- First pass: CREATE ---
        mode, pos = detect_mode(p)
        self.assertEqual(mode, "CREATE")
        content = extract_new_content(p, pos)
        self.assertEqual(content, original)
        stamp_processed(p)  # mark at EOF of original

        # --- Simulate user appending to the conversation ---
        appended = "# Session 2\nAnother new idea\n"
        with p.open("a", encoding="utf-8") as f:
            f.write(appended)

        # --- Second pass: APPEND ---
        mode2, pos2 = detect_mode(p)
        self.assertEqual(mode2, "APPEND")
        new_content = extract_new_content(p, pos2)
        self.assertEqual(new_content.strip(), appended.strip())
        stamp_processed(p)

        # --- Third pass: nothing new (idempotent) ---
        mode3, pos3 = detect_mode(p)
        self.assertEqual(mode3, "APPEND")
        no_content = extract_new_content(p, pos3)
        self.assertEqual(no_content, "")

    def test_no_duplicate_issues_on_re_run(self):
        """Re-running the pipeline on an already-stamped file yields no new content."""
        p = self.d / "rerun.md"
        p.write_text("Incubate this", encoding="utf-8")
        stamp_processed(p)

        _, last_pos = detect_mode(p)
        delta = extract_new_content(p, last_pos)
        self.assertEqual(delta, "")


if __name__ == "__main__":
    unittest.main()
