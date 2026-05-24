from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import tempfile
import unittest


SCRIPT = (
    pathlib.Path(__file__).resolve().parents[1]
    / "scripts"
    / "provider_failover.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("provider_failover", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ProviderFailoverTests(unittest.TestCase):
    def test_loads_default_and_override_order(self):
        module = load_module()
        self.assertEqual(
            module.load_config(None)["order"],
            ["codex", "claude", "gemini", "manager-absorb"],
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "failover.json"
            path.write_text(
                json.dumps(
                    {
                        "provider_failover": {
                            "order": ["codex", "gemini", "manager-absorb"],
                            "probe_timeout_seconds": 12,
                        }
                    }
                ),
                encoding="utf-8",
            )
            config = module.load_config(path)

        self.assertEqual(config["order"], ["codex", "gemini", "manager-absorb"])
        self.assertEqual(config["probe_timeout_seconds"], 12)
        self.assertEqual(config["probe_prompt"], "Say READY and exit.")

    def test_detects_weekly_budget_rate_limit_and_quota_prompts(self):
        module = load_module()
        cases = [
            (
                "Your weekly budget has been exhausted. Try again later.",
                "weekly_budget_exhausted",
            ),
            (
                "429: retry after 120 seconds because the rate limit was reached.",
                "rate_limit_prompt",
            ),
            (
                "Provider says quota exceeded for this account.",
                "provider_quota_exhausted",
            ),
            (
                "No credits remain for this provider.",
                "provider_quota_exhausted",
            ),
        ]

        for text, reason in cases:
            with self.subTest(reason=reason):
                candidate = module.classify_capture(text)
                self.assertEqual(candidate["action"], "FAILOVER_CANDIDATE")
                self.assertEqual(candidate["failure_reason"], reason)
                self.assertTrue(candidate["matched"])

    def test_ignores_non_provider_blocks(self):
        module = load_module()
        text = """
        Do you want to allow npm test?
        A local unit test failed because expected 1 but got 2.
        To continue this session, run codex resume.
        """

        candidate = module.classify_capture(text)

        self.assertEqual(candidate["action"], "NO_FAILOVER")
        self.assertEqual(candidate["failure_reason"], "")

    def test_updates_round_state_without_migration(self):
        module = load_module()
        state = {"round": 37}
        capture = "line 1\nYour weekly quota has reached the limit for this week.\n"
        candidate = module.classify_capture(capture)

        record = module.update_provider_state(
            state,
            pane="sprint:0.3",
            persona="dan",
            lane="core4-1511",
            worktree="/tmp/core4-dan",
            provider="codex",
            candidate=candidate,
            config=module.DEFAULT_CONFIG,
            capture_text=capture,
            timestamp="2026-05-23T12:34:56+00:00",
        )

        failover = state["provider_failover"]
        self.assertEqual(record["provider_status"], "exhausted")
        self.assertEqual(record["failure_reason"], "weekly_budget_exhausted")
        self.assertEqual(record["recommended_next_provider"], "claude")
        self.assertEqual(record["last_migrated_at"], "")
        self.assertIn("weekly quota", record["capture_excerpt"])
        self.assertEqual(failover["providers"]["sprint:0.3"], record)
        self.assertEqual(failover["events"][0]["action"], "FAILOVER_CANDIDATE")

    def test_cli_scan_capture_updates_state_file(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            capture = root / "pane.txt"
            state = root / "round-state.json"
            capture.write_text(
                "OpenAI Codex\nweekly budget exhausted for this workspace\n",
                encoding="utf-8",
            )

            with contextlib.redirect_stdout(io.StringIO()):
                rc = module.main(
                    [
                        "scan-capture",
                        "--capture",
                        str(capture),
                        "--state",
                        str(state),
                        "--pane",
                        "sprint:0.1",
                        "--persona",
                        "bob",
                        "--lane",
                        "claude-skills-166",
                        "--worktree",
                        "/tmp/claude-skills-bob-r37-gpt55-grid",
                        "--provider",
                        "codex",
                    ]
                )
            data = json.loads(state.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        provider = data["provider_failover"]["providers"]["sprint:0.1"]
        self.assertEqual(provider["persona"], "bob")
        self.assertEqual(provider["recommended_next_provider"], "claude")


if __name__ == "__main__":
    unittest.main()
