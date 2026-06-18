"""Tests for the spend dead-man's switch + least-privilege scoping (#259)."""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

GOV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOV))

import spend_guard as sg  # noqa: E402

ROSTER_PATH = GOV / "agent-roster.yaml"


@pytest.fixture(scope="module")
def roster():
    return sg.load_roster(str(ROSTER_PATH))


def _ledger(agents, when=None):
    when = when or datetime.now(timezone.utc)
    return {
        "generated_at": when.isoformat().replace("+00:00", "Z"),
        "agents": {a: {"spent_usd": v} for a, v in agents.items()},
    }


# --- least-privilege scoping (acceptance: per-department scoping enforced) ---
def test_youtube_agent_gets_youtube_api(roster):
    # cindy is studio-video
    assert sg.scope_check(roster, "cindy", tool="youtube_api").allowed


def test_youtube_agent_denied_filesystem_and_repo(roster):
    assert not sg.scope_check(roster, "cindy", tool="local_filesystem").allowed
    assert not sg.scope_check(roster, "cindy", tool="github_push").allowed
    assert not sg.scope_check(roster, "cindy", secret="GITHUB_TOKEN").allowed


def test_default_deny_for_unlisted_tool(roster):
    assert not sg.scope_check(roster, "alice", tool="some_random_tool").allowed


def test_robotics_agent_allowed_repo_denied_youtube(roster):
    assert sg.scope_check(roster, "alice", tool="github_push").allowed
    assert not sg.scope_check(roster, "alice", tool="youtube_api").allowed
    assert not sg.scope_check(roster, "alice", secret="YOUTUBE_API_KEY").allowed


def test_deny_beats_allow_is_impossible_to_bypass(roster):
    d = sg.scope_check(roster, "cindy", tool="github_push")
    assert not d.allowed and "denied" in d.reason


def test_scope_check_requires_exactly_one_target(roster):
    with pytest.raises(ValueError):
        sg.scope_check(roster, "alice")
    with pytest.raises(ValueError):
        sg.scope_check(roster, "alice", tool="x", secret="y")


def test_unknown_agent_raises(roster):
    with pytest.raises(KeyError):
        sg.scope_check(roster, "nobody", tool="github_push")


# --- spend caps (acceptance: hard daily cap + 75% soft-warning) -------------
def test_under_soft_warn_is_ok():
    r = sg.evaluate_agent("alice", spent_usd=10.0, cap_usd=40.0, soft_warn_pct=0.75)
    assert r.status == sg.OK


def test_soft_warning_at_75pct():
    r = sg.evaluate_agent("alice", spent_usd=30.0, cap_usd=40.0, soft_warn_pct=0.75)
    assert r.status == sg.SOFT_WARN
    assert r.blocking


def test_hard_cap_at_100pct():
    r = sg.evaluate_agent("alice", spent_usd=40.0, cap_usd=40.0, soft_warn_pct=0.75)
    assert r.status == sg.HARD_CAP


def test_ledger_soft_warn_pauses_agent(roster):
    # cindy cap is 15.0 -> 75% = 11.25
    report = sg.evaluate_ledger(roster, _ledger({"cindy": 12.0}))
    cindy = next(a for a in report.agents if a.agent == "cindy")
    assert cindy.status == sg.SOFT_WARN
    assert not report.ok
    assert "cindy" in report.blocked_agents


def test_ledger_all_clear_when_low(roster):
    report = sg.evaluate_ledger(roster, _ledger({"alice": 1.0, "bob": 0.5}))
    assert report.ok


# --- dead-man's switch (acceptance: 75% warning pauses; stale fails closed) --
def test_stale_ledger_trips_dead_mans_switch(roster):
    old = datetime.now(timezone.utc) - timedelta(hours=2)
    report = sg.evaluate_ledger(roster, _ledger({"alice": 0.0}, when=old))
    assert report.stale
    assert not report.ok
    assert all(a.status == sg.STALE for a in report.agents)


def test_missing_timestamp_is_stale(roster):
    report = sg.evaluate_ledger(roster, {"agents": {"alice": {"spent_usd": 0.0}}})
    assert report.stale
    assert not report.ok


def test_fresh_ledger_not_stale(roster):
    report = sg.evaluate_ledger(roster, _ledger({"alice": 0.0}))
    assert not report.stale


def test_global_cap_breach_blocks_all(roster):
    # global ceiling is 100.0; pile spend under each cap but over the ceiling
    big = {"alice": 39, "dan": 19, "frank": 19, "cindy": 11, "bob": 7, "elsa": 5}
    report = sg.evaluate_ledger(roster, _ledger(big))
    assert report.global_breach
    assert not report.ok


# --- CLI exit codes ---------------------------------------------------------
def test_cli_exit_nonzero_on_block(tmp_path, roster):
    led = tmp_path / "usage.json"
    led.write_text(json.dumps(_ledger({"cindy": 14.0})))
    rc = sg.main(["--ledger", str(led), "--config", str(ROSTER_PATH)])
    assert rc == 1


def test_cli_exit_zero_when_clear(tmp_path):
    led = tmp_path / "usage.json"
    led.write_text(json.dumps(_ledger({"alice": 1.0})))
    rc = sg.main(["--ledger", str(led), "--config", str(ROSTER_PATH)])
    assert rc == 0
