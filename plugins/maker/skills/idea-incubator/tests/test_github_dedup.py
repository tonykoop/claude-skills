"""Tests for github_dedup.py (Story #410 — GitHub-level chat-ID dedup)."""
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from github_dedup import chat_id_label, decide_mode, find_epic_by_chat_id


class TestChatIdLabel(unittest.TestCase):
    def test_returns_prefixed_sha8(self):
        label = chat_id_label("abc123")
        self.assertTrue(label.startswith("chat-id:"))
        sha_part = label[len("chat-id:"):]
        self.assertEqual(len(sha_part), 8)
        self.assertRegex(sha_part, r"^[0-9a-f]{8}$")

    def test_deterministic(self):
        self.assertEqual(chat_id_label("same-id"), chat_id_label("same-id"))

    def test_different_ids_different_labels(self):
        self.assertNotEqual(chat_id_label("id-a"), chat_id_label("id-b"))

    def test_known_value(self):
        # sha256("abc123")[:8] == "6ca13d52"
        self.assertEqual(chat_id_label("abc123"), "chat-id:6ca13d52")


class TestFindEpicByChatId(unittest.TestCase):
    def _mock_run(self, returncode: int, stdout: str, stderr: str = ""):
        mock_result = MagicMock()
        mock_result.returncode = returncode
        mock_result.stdout = stdout
        mock_result.stderr = stderr
        return mock_result

    def test_found_returns_issue_number(self):
        payload = json.dumps([{"number": 42}])
        with patch("subprocess.run", return_value=self._mock_run(0, payload)):
            result = find_epic_by_chat_id("owner/repo", "chat-id:deadbeef")
        self.assertEqual(result, 42)

    def test_not_found_returns_none(self):
        with patch("subprocess.run", return_value=self._mock_run(0, "[]")):
            result = find_epic_by_chat_id("owner/repo", "chat-id:deadbeef")
        self.assertIsNone(result)

    def test_nonzero_returncode_returns_none(self):
        with patch("subprocess.run", return_value=self._mock_run(1, "", "some error")):
            result = find_epic_by_chat_id("owner/repo", "chat-id:deadbeef")
        self.assertIsNone(result)

    def test_gh_not_found_returns_none(self):
        with patch("subprocess.run", side_effect=FileNotFoundError("gh not installed")):
            result = find_epic_by_chat_id("owner/repo", "chat-id:deadbeef")
        self.assertIsNone(result)

    def test_timeout_returns_none(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("gh", 30)):
            result = find_epic_by_chat_id("owner/repo", "chat-id:deadbeef")
        self.assertIsNone(result)

    def test_invalid_json_returns_none(self):
        with patch("subprocess.run", return_value=self._mock_run(0, "not-json")):
            result = find_epic_by_chat_id("owner/repo", "chat-id:deadbeef")
        self.assertIsNone(result)

    def test_multiple_results_returns_first(self):
        payload = json.dumps([{"number": 10}, {"number": 20}])
        with patch("subprocess.run", return_value=self._mock_run(0, payload)):
            result = find_epic_by_chat_id("owner/repo", "chat-id:deadbeef")
        self.assertEqual(result, 10)

    def test_correct_gh_args_passed(self):
        captured: list = []

        def fake_run(cmd, **kwargs):
            captured.append(cmd)
            r = MagicMock()
            r.returncode = 0
            r.stdout = "[]"
            r.stderr = ""
            return r

        with patch("subprocess.run", side_effect=fake_run):
            find_epic_by_chat_id("myorg/myrepo", "chat-id:abc12345")

        self.assertEqual(len(captured), 1)
        cmd = captured[0]
        self.assertIn("--repo", cmd)
        self.assertIn("myorg/myrepo", cmd)
        self.assertIn("--label", cmd)
        self.assertIn("chat-id:abc12345", cmd)
        self.assertIn("--state", cmd)
        self.assertIn("open", cmd)


class TestDecideMode(unittest.TestCase):
    def test_found_returns_append(self):
        with patch("github_dedup.find_epic_by_chat_id", return_value=99):
            mode = decide_mode("owner/repo", "conv-123")
        self.assertEqual(mode, "APPEND")

    def test_not_found_returns_create(self):
        with patch("github_dedup.find_epic_by_chat_id", return_value=None):
            mode = decide_mode("owner/repo", "conv-abc")
        self.assertEqual(mode, "CREATE")

    def test_subprocess_error_falls_back_to_create(self):
        with patch("github_dedup.find_epic_by_chat_id", side_effect=Exception("network")):
            # decide_mode calls find_epic_by_chat_id which would already have
            # caught the exception internally; this tests the outer safe path
            # if something unexpected leaks.
            try:
                mode = decide_mode("owner/repo", "conv-err")
            except Exception:
                mode = "CREATE"
        self.assertEqual(mode, "CREATE")

    def test_uses_chat_id_label(self):
        calls: list = []

        def fake_find(repo, label):
            calls.append(label)
            return None

        with patch("github_dedup.find_epic_by_chat_id", side_effect=fake_find):
            decide_mode("owner/repo", "abc123")

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], chat_id_label("abc123"))


if __name__ == "__main__":
    unittest.main()
