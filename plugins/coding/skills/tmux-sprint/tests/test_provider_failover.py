from __future__ import annotations

import importlib.util
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


pf = load_module()


class TestDetectExhaustion(unittest.TestCase):
    def test_weekly_budget(self):
        self.assertEqual(
            pf.detect_exhaustion("You've reached your weekly limit. Resets next week."),
            "weekly_budget_exhausted",
        )

    def test_generic_quota_maps_to_budget(self):
        self.assertEqual(pf.detect_exhaustion("Error: quota exceeded"), "weekly_budget_exhausted")

    def test_rate_limit(self):
        self.assertEqual(pf.detect_exhaustion("HTTP 429: rate limit, slow down"), "rate_limit_prompt")

    def test_auth_blocked(self):
        self.assertEqual(pf.detect_exhaustion("Error 401 Unauthorized — please log in"), "provider_auth_blocked")

    def test_cli_missing(self):
        self.assertEqual(pf.detect_exhaustion("bash: gemini: command not found"), "provider_cli_missing")

    def test_weekly_wins_over_rate_limit(self):
        # Both phrases present; the weekly-budget family is higher priority.
        text = "rate limit hit; also you are out of your weekly quota"
        self.assertEqual(pf.detect_exhaustion(text), "weekly_budget_exhausted")

    def test_healthy_pane_returns_none(self):
        self.assertIsNone(pf.detect_exhaustion("running tests... all green"))

    def test_transient_prompt_is_not_exhaustion(self):
        text = "Do you want to allow this command? continue? [y/N]"
        self.assertIsNone(pf.detect_exhaustion(text))
        self.assertTrue(pf.is_transient_only(text))

    def test_exhaustion_overrides_transient(self):
        text = "Do you want to allow this command?\nweekly limit reached"
        self.assertEqual(pf.detect_exhaustion(text), "weekly_budget_exhausted")
        self.assertFalse(pf.is_transient_only(text))

    def test_empty_text(self):
        self.assertIsNone(pf.detect_exhaustion(""))


class TestNextProvider(unittest.TestCase):
    def setUp(self):
        self.order = ["codex", "claude", "gemini", "manager-absorb"]

    def test_codex_to_claude(self):
        self.assertEqual(pf.next_provider(self.order, "codex"), "claude")

    def test_claude_to_gemini(self):
        self.assertEqual(pf.next_provider(self.order, "claude"), "gemini")

    def test_last_real_provider_falls_to_manager_absorb(self):
        self.assertEqual(pf.next_provider(self.order, "gemini"), "manager-absorb")

    def test_unknown_current_starts_at_top(self):
        self.assertEqual(pf.next_provider(self.order, "mystery"), "codex")

    def test_none_current_starts_at_top(self):
        self.assertEqual(pf.next_provider(self.order, None), "codex")

    def test_custom_order_respected(self):
        self.assertEqual(pf.next_provider(["claude", "codex"], "claude"), "codex")

    def test_empty_order_absorbs(self):
        self.assertEqual(pf.next_provider([], "codex"), "manager-absorb")


class TestResolveConfig(unittest.TestCase):
    def test_defaults(self):
        cfg = pf.resolve_config()
        self.assertEqual(cfg["order"][0], "codex")
        self.assertIn("manager-absorb", cfg["order"])

    def test_override_order(self):
        cfg = pf.resolve_config({"order": ["claude", "gemini"]})
        self.assertEqual(cfg["order"], ["claude", "gemini"])

    def test_nested_override(self):
        cfg = pf.resolve_config({"provider_failover": {"order": ["gemini"]}})
        self.assertEqual(cfg["order"], ["gemini"])

    def test_empty_order_falls_back_to_default(self):
        cfg = pf.resolve_config({"order": []})
        self.assertEqual(cfg["order"], pf.DEFAULT_CONFIG["order"])


class TestFailoverCandidate(unittest.TestCase):
    def test_healthy_returns_none(self):
        self.assertIsNone(pf.failover_candidate(
            capture_text="all good", pane="s:0.1", provider="codex"))

    def test_candidate_record_shape(self):
        rec = pf.failover_candidate(
            capture_text="weekly limit reached",
            pane="sprint:0.3", persona="dan", lane="core4-1511",
            worktree="/wt/dan", provider="codex",
        )
        self.assertIsNotNone(rec)
        self.assertEqual(rec["provider"], "codex")
        self.assertEqual(rec["next_provider"], "claude")
        self.assertEqual(rec["provider_status"], "exhausted")
        self.assertEqual(rec["failure_reason"], "weekly_budget_exhausted")
        self.assertEqual(rec["recommended_action"], "FAILOVER_CANDIDATE")
        self.assertIsNone(rec["probe"]["success"])  # no keystrokes/probe yet

    def test_last_provider_recommends_manager_absorb(self):
        rec = pf.failover_candidate(
            capture_text="quota exceeded", pane="s:0.1", provider="gemini")
        self.assertEqual(rec["next_provider"], "manager-absorb")
        self.assertEqual(rec["recommended_action"], "manager_absorb")

    def test_capture_excerpt_is_tailed(self):
        text = "\n".join(f"line{i}" for i in range(200)) + "\nweekly limit reached"
        rec = pf.failover_candidate(
            capture_text=text, pane="s:0.1", provider="codex", capture_tail_lines=10)
        self.assertLessEqual(len(rec["capture_excerpt"].splitlines()), 10)
        self.assertIn("weekly limit reached", rec["capture_excerpt"])


class TestRenderSummary(unittest.TestCase):
    def test_empty(self):
        out = pf.render_summary([])
        self.assertIn("## Provider Failover", out)
        self.assertIn("no panes migrated", out)

    def test_candidate_row(self):
        rec = pf.failover_candidate(
            capture_text="weekly limit reached",
            pane="sprint:0.3", persona="dan", provider="codex")
        out = pf.render_summary([rec])
        self.assertIn("sprint:0.3", out)
        self.assertIn("codex", out)
        self.assertIn("claude", out)
        self.assertIn("(pending)", out)
        self.assertIn("candidate", out)

    def test_resumed_row_when_probe_succeeded(self):
        rec = pf.failover_candidate(
            capture_text="weekly limit reached", pane="s:0.1", provider="codex")
        rec["probe"]["success"] = True
        out = pf.render_summary([rec])
        self.assertIn("READY", out)
        self.assertIn("resumed", out)


class TestCLI(unittest.TestCase):
    def _write(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
        f.write(text)
        f.close()
        return f.name

    def test_detect_healthy_exit_zero(self):
        cap = self._write("tests passed")
        rc = pf.main(["detect", "--capture", cap, "--pane", "s:0.1", "--provider", "codex"])
        self.assertEqual(rc, 0)

    def test_detect_candidate_exit_one(self):
        cap = self._write("weekly limit reached, resets next week")
        rc = pf.main(["detect", "--capture", cap, "--pane", "s:0.1", "--provider", "codex"])
        self.assertEqual(rc, 1)

    def test_summary_cli(self):
        rec = pf.failover_candidate(
            capture_text="quota exceeded", pane="s:0.2", persona="elsa", provider="claude")
        recs = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump({"records": [rec]}, recs)
        recs.close()
        rc = pf.main(["summary", "--records", recs.name])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
