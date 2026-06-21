"""Tests for url_upsert.py (Story #408 — URL-stable upsert clipping)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from url_upsert import normalize_url, sanitize_chat_url, upsert_clip


class TestNormalizeUrl(unittest.TestCase):
    def test_strips_utm_params(self):
        raw = "https://gemini.google.com/app/abc123?utm_source=share&utm_medium=web"
        norm = normalize_url(raw)
        self.assertNotIn("utm_source", norm)
        self.assertNotIn("utm_medium", norm)

    def test_keeps_stable_params(self):
        raw = "https://gemini.google.com/app/abc?mode=edit"
        norm = normalize_url(raw)
        self.assertIn("mode=edit", norm)

    def test_lowercases_host(self):
        raw = "https://Gemini.Google.Com/app/abc"
        norm = normalize_url(raw)
        self.assertIn("gemini.google.com", norm)

    def test_strips_trailing_slash(self):
        a = normalize_url("https://gemini.google.com/app/abc/")
        b = normalize_url("https://gemini.google.com/app/abc")
        self.assertEqual(a, b)

    def test_same_url_different_utm_same_result(self):
        a = normalize_url("https://gemini.google.com/app/xyz?utm_source=ios")
        b = normalize_url("https://gemini.google.com/app/xyz?utm_source=android")
        self.assertEqual(a, b)

    def test_different_paths_different_result(self):
        a = normalize_url("https://gemini.google.com/app/abc")
        b = normalize_url("https://gemini.google.com/app/def")
        self.assertNotEqual(a, b)

    def test_strips_gl_param(self):
        raw = "https://gemini.google.com/app/abc?_gl=1*abc*def"
        norm = normalize_url(raw)
        self.assertNotIn("_gl", norm)

    def test_deterministic_query_ordering(self):
        a = normalize_url("https://gemini.google.com/app/abc?z=1&a=2")
        b = normalize_url("https://gemini.google.com/app/abc?a=2&z=1")
        self.assertEqual(a, b)


class TestSanitizeChatUrl(unittest.TestCase):
    def test_returns_stable_stem(self):
        url = "https://gemini.google.com/app/abc123"
        stem1 = sanitize_chat_url(url)
        stem2 = sanitize_chat_url(url)
        self.assertEqual(stem1, stem2)

    def test_prefix_gemini(self):
        stem = sanitize_chat_url("https://gemini.google.com/app/abc123")
        self.assertTrue(stem.startswith("gemini-"))

    def test_contains_sha8(self):
        stem = sanitize_chat_url("https://gemini.google.com/app/abc123")
        parts = stem.split("-")
        # format: gemini-<sha8>-<slug>
        self.assertGreaterEqual(len(parts), 3)
        sha8 = parts[1]
        self.assertEqual(len(sha8), 8)
        self.assertTrue(all(c in "0123456789abcdef" for c in sha8))

    def test_utm_ignored_for_stem(self):
        a = sanitize_chat_url("https://gemini.google.com/app/abc?utm_source=ios")
        b = sanitize_chat_url("https://gemini.google.com/app/abc?utm_source=android")
        self.assertEqual(a, b)

    def test_different_paths_different_stems(self):
        a = sanitize_chat_url("https://gemini.google.com/app/abc")
        b = sanitize_chat_url("https://gemini.google.com/app/def")
        self.assertNotEqual(a, b)

    def test_slug_safe_chars_only(self):
        stem = sanitize_chat_url("https://gemini.google.com/app/Some Path/with spaces?q=1")
        # Only alphanumeric and hyphens after "gemini-sha8-"
        slug_part = stem[len("gemini-") + 8 + 1:]
        self.assertRegex(slug_part, r"^[a-z0-9-]+$")

    def test_slug_max_length(self):
        long_url = "https://gemini.google.com/app/" + "a" * 200
        stem = sanitize_chat_url(long_url)
        slug_part = stem[len("gemini-") + 8 + 1:]
        self.assertLessEqual(len(slug_part), 32)

    def test_empty_path_falls_back(self):
        stem = sanitize_chat_url("https://gemini.google.com/")
        self.assertTrue(stem.startswith("gemini-"))
        self.assertNotIn("--", stem)


class TestUpsertClip(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.inbox = Path(self._tmp.name) / "00-inbox"

    def tearDown(self):
        self._tmp.cleanup()

    def test_creates_new_file(self):
        url = "https://gemini.google.com/app/test1"
        path, mode = upsert_clip(self.inbox, url)
        self.assertEqual(mode, "created")
        self.assertTrue(path.exists())

    def test_idempotent_skip(self):
        url = "https://gemini.google.com/app/test2"
        path1, mode1 = upsert_clip(self.inbox, url)
        path2, mode2 = upsert_clip(self.inbox, url)
        self.assertEqual(mode1, "created")
        self.assertEqual(mode2, "existing")
        self.assertEqual(path1, path2)

    def test_same_url_different_utm_same_file(self):
        url_a = "https://gemini.google.com/app/xyz?utm_source=ios"
        url_b = "https://gemini.google.com/app/xyz?utm_source=android"
        path_a, _ = upsert_clip(self.inbox, url_a)
        path_b, mode_b = upsert_clip(self.inbox, url_b)
        self.assertEqual(path_a, path_b)
        self.assertEqual(mode_b, "existing")

    def test_creates_inbox_dir_if_missing(self):
        inbox = Path(self._tmp.name) / "deep" / "inbox"
        url = "https://gemini.google.com/app/newdir"
        path, mode = upsert_clip(inbox, url)
        self.assertTrue(path.exists())
        self.assertEqual(mode, "created")

    def test_stub_content_has_chat_url(self):
        url = "https://gemini.google.com/app/content-test"
        path, _ = upsert_clip(self.inbox, url)
        body = path.read_text()
        self.assertIn("source: gemini", body)
        self.assertIn("chat_url:", body)

    def test_custom_content_written(self):
        url = "https://gemini.google.com/app/custom"
        custom = "# My custom clip\nsome content"
        path, mode = upsert_clip(self.inbox, url, content=custom)
        self.assertEqual(mode, "created")
        self.assertEqual(path.read_text(), custom)

    def test_overwrite_replaces_file(self):
        url = "https://gemini.google.com/app/overwrite-test"
        upsert_clip(self.inbox, url, content="v1")
        path, mode = upsert_clip(self.inbox, url, content="v2", overwrite=True)
        self.assertEqual(mode, "created")
        self.assertEqual(path.read_text(), "v2")

    def test_filename_ends_with_md(self):
        url = "https://gemini.google.com/app/ext-check"
        path, _ = upsert_clip(self.inbox, url)
        self.assertEqual(path.suffix, ".md")

    def test_different_urls_different_files(self):
        url_a = "https://gemini.google.com/app/aaa"
        url_b = "https://gemini.google.com/app/bbb"
        path_a, _ = upsert_clip(self.inbox, url_a)
        path_b, _ = upsert_clip(self.inbox, url_b)
        self.assertNotEqual(path_a, path_b)


if __name__ == "__main__":
    unittest.main()
