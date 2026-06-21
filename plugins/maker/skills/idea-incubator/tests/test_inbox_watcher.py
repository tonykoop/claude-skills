"""Tests for inbox_watcher.py (Story #409 — file-watcher daemon + verbal-trigger regex)."""
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from inbox_watcher import (
    detect_triggers,
    scan_once,
    dispatch_file,
    InboxWatcher,
    WatcherState,
    VERBAL_TRIGGERS,
)


class TestDetectTriggers(unittest.TestCase):
    def test_incubate_this(self):
        self.assertTrue(detect_triggers("Please incubate this idea for later"))

    def test_new_idea(self):
        self.assertTrue(detect_triggers("New idea: build a mobile clip bridge"))

    def test_add_to_inbox(self):
        self.assertTrue(detect_triggers("Add this to my inbox please"))

    def test_file_gh_issues(self):
        self.assertTrue(detect_triggers("file gh issues from this brainstorm"))

    def test_ingest_brainstorm(self):
        self.assertTrue(detect_triggers("Ingest this brainstorm doc"))

    def test_here_is_brainstorm(self):
        self.assertTrue(detect_triggers("here's my next brainstorming doc"))

    def test_source_gemini_front_matter(self):
        self.assertTrue(detect_triggers("---\nsource: gemini\nchat_url: ...\n---"))

    def test_fingerprint_comment(self):
        self.assertTrue(detect_triggers("<!-- idea-fingerprint: abc123def -->"))

    def test_capture_from_mobile(self):
        self.assertTrue(detect_triggers("capture from mobile shortcut"))

    def test_obsidian_clip(self):
        self.assertTrue(detect_triggers("obsidian clip setup"))

    def test_red_team(self):
        self.assertTrue(detect_triggers("red-team this epic before filing"))

    def test_no_trigger_plain_text(self):
        self.assertEqual(detect_triggers("Just a random note without any trigger"), [])

    def test_case_insensitive(self):
        self.assertTrue(detect_triggers("INCUBATE THIS now"))

    def test_returns_list_of_pattern_strings(self):
        matches = detect_triggers("new idea here")
        self.assertIsInstance(matches, list)
        self.assertTrue(len(matches) > 0)

    def test_multiple_triggers_returns_all(self):
        matches = detect_triggers("new idea — incubate this and file gh issues")
        self.assertGreater(len(matches), 1)


class TestScanOnce(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.inbox = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, name: str, content: str) -> Path:
        p = self.inbox / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_empty_inbox_no_results(self):
        state = WatcherState()
        result = scan_once(self.inbox, state)
        self.assertEqual(result.new_files, [])
        self.assertEqual(result.triggered, [])

    def test_new_triggered_file(self):
        self._write("brainstorm.md", "source: gemini\nsome content")
        state = WatcherState()
        result = scan_once(self.inbox, state)
        self.assertEqual(len(result.triggered), 1)
        self.assertEqual(len(result.skipped_no_trigger), 0)

    def test_new_untriggered_file(self):
        self._write("notes.md", "Just random notes with no trigger phrase")
        state = WatcherState()
        result = scan_once(self.inbox, state)
        self.assertEqual(len(result.triggered), 0)
        self.assertEqual(len(result.skipped_no_trigger), 1)

    def test_no_trigger_check_fires_all(self):
        self._write("any.md", "plain content no trigger")
        state = WatcherState()
        result = scan_once(self.inbox, state, no_trigger_check=True)
        self.assertEqual(len(result.triggered), 1)

    def test_seen_file_not_re_triggered(self):
        p = self._write("seen.md", "source: gemini")
        state = WatcherState()
        scan_once(self.inbox, state)  # first scan — marks mtime
        result = scan_once(self.inbox, state)  # second scan — unchanged
        self.assertEqual(result.new_files, [])

    def test_modified_file_re_triggered(self):
        p = self._write("mod.md", "source: gemini")
        state = WatcherState()
        scan_once(self.inbox, state)
        # Touch the file to update mtime
        time.sleep(0.01)
        p.write_text("source: gemini\n<!-- modified -->", encoding="utf-8")
        result = scan_once(self.inbox, state)
        self.assertEqual(len(result.new_files), 1)

    def test_non_md_file_ignored(self):
        (self.inbox / "image.png").write_bytes(b"\x89PNG")
        (self.inbox / "notes.txt").write_text("incubate this", encoding="utf-8")
        state = WatcherState()
        result = scan_once(self.inbox, state)
        self.assertEqual(result.new_files, [])

    def test_missing_inbox_dir_returns_empty(self):
        state = WatcherState()
        result = scan_once(Path("/nonexistent/inbox"), state)
        self.assertEqual(result.new_files, [])

    def test_multiple_triggered_files(self):
        for i in range(3):
            self._write(f"b{i}.md", f"incubate this idea {i}")
        state = WatcherState()
        result = scan_once(self.inbox, state)
        self.assertEqual(len(result.triggered), 3)


class TestDispatchFile(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.inbox = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_dry_run_does_not_execute(self):
        p = self.inbox / "test.md"
        p.write_text("content", encoding="utf-8")
        with patch("subprocess.run") as mock_run:
            result = dispatch_file(["echo", "test"], p, dry_run=True)
            mock_run.assert_not_called()
        self.assertTrue(result)

    def test_file_placeholder_replaced(self):
        p = self.inbox / "test.md"
        p.write_text("content", encoding="utf-8")
        captured: list[list[str]] = []

        def fake_run(cmd, **kwargs):
            captured.append(cmd)
            class R:
                returncode = 0
            return R()

        with patch("subprocess.run", side_effect=fake_run):
            dispatch_file(["python", "script.py", "{file}"], p, dry_run=False)

        self.assertEqual(len(captured), 1)
        self.assertIn(str(p.resolve()), captured[0])
        self.assertNotIn("{file}", captured[0])

    def test_no_placeholder_appends_path(self):
        p = self.inbox / "test.md"
        p.write_text("content", encoding="utf-8")
        captured: list[list[str]] = []

        def fake_run(cmd, **kwargs):
            captured.append(cmd)
            class R:
                returncode = 0
            return R()

        with patch("subprocess.run", side_effect=fake_run):
            dispatch_file(["echo"], p, dry_run=False)

        self.assertTrue(captured[0][-1].endswith("test.md"))

    def test_nonzero_returncode_returns_false(self):
        p = self.inbox / "fail.md"
        p.write_text("x", encoding="utf-8")

        def fake_run(cmd, **kwargs):
            class R:
                returncode = 1
            return R()

        with patch("subprocess.run", side_effect=fake_run):
            result = dispatch_file(["false"], p, dry_run=False)
        self.assertFalse(result)


class TestInboxWatcher(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.inbox = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_run_once_triggers_file(self):
        (self.inbox / "clip.md").write_text("source: gemini\ncontent", encoding="utf-8")
        dispatched: list[Path] = []

        with patch("inbox_watcher.dispatch_file", side_effect=lambda cmd, p, **kw: dispatched.append(p) or True):
            watcher = InboxWatcher(self.inbox, ["echo"], dry_run=False)
            result = watcher.run_once()

        self.assertEqual(len(result.triggered), 1)
        self.assertEqual(len(dispatched), 1)

    def test_run_once_dry_run_no_dispatch(self):
        (self.inbox / "clip.md").write_text("source: gemini\ncontent", encoding="utf-8")

        with patch("subprocess.run") as mock_run:
            watcher = InboxWatcher(self.inbox, ["echo"], dry_run=True)
            watcher.run_once()
            mock_run.assert_not_called()

    def test_second_scan_no_re_trigger(self):
        (self.inbox / "clip.md").write_text("source: gemini\ncontent", encoding="utf-8")
        watcher = InboxWatcher(self.inbox, ["echo"], dry_run=True)
        r1 = watcher.run_once()
        r2 = watcher.run_once()
        self.assertEqual(len(r1.triggered), 1)
        self.assertEqual(len(r2.triggered), 0)


if __name__ == "__main__":
    unittest.main()
