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
    dispatch_file,
    is_stamped,
    InboxWatcher,
    scan_once,
    stamp_path,
    stamp_processed,
    VERBAL_TRIGGERS,
    WatcherState,
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

    def test_fingerprint_not_a_trigger(self):
        # '<!-- idea-fingerprint:' is the downstream stamp marker.  It must NOT
        # be a trigger — if it were, every already-processed file would re-fire
        # after the pipeline appends it.
        self.assertEqual(detect_triggers("<!-- idea-fingerprint: abc123def -->"), [])

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


class TestDispatchStamp(unittest.TestCase):
    """Persistent .dispatched sidecar guard — survives restart + file modification."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.inbox = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, name: str, content: str) -> Path:
        p = self.inbox / name
        p.write_text(content, encoding="utf-8")
        return p

    # --- stamp helpers ---

    def test_stamp_path_naming(self):
        p = Path("/inbox/foo.md")
        self.assertEqual(stamp_path(p), Path("/inbox/foo.md.dispatched"))

    def test_is_stamped_false_before_stamp(self):
        p = self._write("a.md", "incubate this")
        self.assertFalse(is_stamped(p))

    def test_stamp_processed_creates_sidecar(self):
        p = self._write("a.md", "incubate this")
        stamp_processed(p)
        self.assertTrue(is_stamped(p))
        self.assertTrue(stamp_path(p).exists())

    def test_stamp_processed_idempotent(self):
        p = self._write("a.md", "incubate this")
        stamp_processed(p)
        stamp_processed(p)  # must not raise
        self.assertTrue(is_stamped(p))

    # --- scan_once skips stamped files ---

    def test_scan_skips_stamped_file(self):
        """A file with a .dispatched sidecar must never appear in new_files."""
        p = self._write("stamped.md", "source: gemini")
        stamp_processed(p)
        state = WatcherState()
        result = scan_once(self.inbox, state)
        self.assertNotIn(p, result.new_files)
        self.assertNotIn(p, result.triggered)

    def test_scan_skips_stamped_after_content_change(self):
        """After downstream adds a fingerprint the mtime changes; stamp must block re-fire."""
        p = self._write("fp.md", "source: gemini")
        stamp_processed(p)
        # Simulate downstream appending the fingerprint marker
        time.sleep(0.01)
        p.write_text("source: gemini\n<!-- idea-fingerprint: abc123 -->", encoding="utf-8")
        state = WatcherState()
        result = scan_once(self.inbox, state)
        self.assertNotIn(p, result.triggered)

    # --- restart guard ---

    def test_restart_guard_new_state_still_skips_stamped(self):
        """Watcher restart (fresh WatcherState) must not re-dispatch stamped files."""
        p = self._write("restarted.md", "source: gemini")
        stamp_processed(p)
        # First watcher run — brand new state, as if daemon just restarted
        state = WatcherState()
        result = scan_once(self.inbox, state)
        self.assertNotIn(p, result.triggered)

    def test_unstamped_file_still_triggered_after_restart(self):
        """An unstamped file MUST be picked up on every watcher start."""
        p = self._write("fresh.md", "source: gemini")
        state = WatcherState()  # fresh state simulates restart
        result = scan_once(self.inbox, state)
        self.assertIn(p, result.triggered)

    # --- InboxWatcher integration: stamp written after live dispatch ---

    def test_run_once_stamps_after_live_dispatch(self):
        p = self._write("live.md", "source: gemini")

        def fake_dispatch(cmd, path, **kw):
            return True

        with patch("inbox_watcher.dispatch_file", side_effect=fake_dispatch):
            watcher = InboxWatcher(self.inbox, ["echo"], dry_run=False)
            watcher.run_once()

        self.assertTrue(is_stamped(p))

    def test_run_once_dry_run_does_not_stamp(self):
        """Dry-run dispatches must leave no .dispatched sidecar."""
        p = self._write("dry.md", "source: gemini")
        watcher = InboxWatcher(self.inbox, ["echo"], dry_run=True)
        watcher.run_once()
        self.assertFalse(is_stamped(p))

    def test_run_once_failed_dispatch_does_not_stamp(self):
        """A failed dispatch (non-zero exit) must NOT stamp — file stays retriable."""
        p = self._write("fail.md", "source: gemini")

        def fake_fail(cmd, path, **kw):
            return False

        with patch("inbox_watcher.dispatch_file", side_effect=fake_fail):
            watcher = InboxWatcher(self.inbox, ["false"], dry_run=False)
            watcher.run_once()

        self.assertFalse(is_stamped(p))

    def test_second_run_once_skips_stamped(self):
        """After stamp is written, a second run_once on same watcher skips the file."""
        p = self._write("second.md", "source: gemini")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = type("R", (), {"returncode": 0})()
            watcher = InboxWatcher(self.inbox, ["echo"], dry_run=False)
            r1 = watcher.run_once()
            r2 = watcher.run_once()

        self.assertEqual(len(r1.triggered), 1)
        self.assertEqual(len(r2.triggered), 0)

    def test_restart_after_stamp_no_redispatch(self):
        """New watcher instance (simulates daemon restart) must not re-dispatch stamped file."""
        p = self._write("persisted.md", "source: gemini")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = type("R", (), {"returncode": 0})()
            watcher1 = InboxWatcher(self.inbox, ["echo"], dry_run=False)
            watcher1.run_once()

        self.assertTrue(is_stamped(p))

        # Simulate restart: brand-new InboxWatcher, no shared state
        with patch("subprocess.run") as mock_run2:
            watcher2 = InboxWatcher(self.inbox, ["echo"], dry_run=False)
            r = watcher2.run_once()
            mock_run2.assert_not_called()

        self.assertEqual(len(r.triggered), 0)


if __name__ == "__main__":
    unittest.main()
