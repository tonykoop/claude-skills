"""Tests for the front-end <-> back-end pipeline symmetry wiring (#260).

Verifies the two new departments and their operator agents are wired into the
orchestrator config with the right least-privilege scopes, and that adding them
did not disturb the #256 audit-routing determinism.
"""
import sys
from pathlib import Path

import pytest

GOV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOV))

import review_router as rr  # noqa: E402
import spend_guard as sg  # noqa: E402

ROSTER_PATH = GOV / "agent-roster.yaml"


@pytest.fixture(scope="module")
def roster():
    return sg.load_roster(str(ROSTER_PATH))


# --- departments documented & wired (acceptance: both departments mapped) ---
def test_both_pipeline_departments_exist(roster):
    depts = roster["departments"]
    assert "creative-ingestion" in depts
    assert "release-operations" in depts


def test_front_end_files_issues_but_never_pushes_code(roster):
    # idea-incubator turns text into tickets: issues yes, repo push no.
    assert sg.scope_check(roster, "ingestor", tool="github_issues").allowed
    assert not sg.scope_check(roster, "ingestor", tool="github_push").allowed
    assert not sg.scope_check(roster, "ingestor", tool="shell").allowed


def test_back_end_surfaces_ticket_but_never_deploys(roster):
    # release-operations proposes; it cannot push code or run a shell deploy.
    assert sg.scope_check(roster, "releaser", tool="github_issues").allowed
    assert sg.scope_check(roster, "releaser", tool="asset_storage").allowed
    assert not sg.scope_check(roster, "releaser", tool="github_push").allowed
    assert not sg.scope_check(roster, "releaser", tool="shell").allowed


def test_neither_operator_holds_a_deploy_secret(roster):
    for agent in ("ingestor", "releaser"):
        assert not sg.scope_check(roster, agent, secret="ROBOTICS_DEPLOY_KEY").allowed


# --- heartbeat + label triggers specified (acceptance #3) -------------------
def test_pipeline_heartbeat_and_labels_specified(roster):
    pl = roster["pipeline"]
    assert pl["front_end"]["heartbeat"] == "0 8 * * *"
    assert pl["front_end"]["emits_label"] == "idea:incubated"
    assert "ready-for-release" in pl["back_end"]["triggers_on_labels"]
    assert pl["back_end"]["emits_label"] == "release:proposed"
    # back-end's deploy step defers to the #258 circuit breaker
    assert pl["back_end"]["deploy_gate"] == "circuit_breaker"


def test_handoff_label_chains_front_to_back(roster):
    # the front-end's output label is the seam; back-end fires on the *promoted*
    # labels, so the two halves are decoupled but connected via labels.
    pl = roster["pipeline"]
    assert pl["front_end"]["emits_label"]  # exists
    assert pl["back_end"]["triggers_on_labels"]  # exists


# --- operators are conveyor lanes, not auditors -----------------------------
def test_operators_are_not_auditors(roster):
    assert roster["agents"]["ingestor"]["can_audit"] is False
    assert roster["agents"]["releaser"]["can_audit"] is False


def test_routing_determinism_preserved(roster):
    # Adding the two non-audit operators must not change who audits whom.
    res = rr.assign_auditor(roster, {
        "creator_agent": "alice", "creator_model": "claude-opus-4-8",
    })
    assert res.ok
    assert res.auditor not in ("ingestor", "releaser")  # never picked
    assert rr.family_of(roster, roster["agents"][res.auditor]["model"]) != "opus"


def test_ledger_still_evaluates_with_new_agents(roster):
    # new agents appear in the spend report (caps enforced) without errors.
    report = sg.evaluate_ledger(roster, {
        "generated_at": "2026-06-17T20:00:00Z",
        "agents": {"ingestor": {"spent_usd": 0.0}, "releaser": {"spent_usd": 0.0}},
    }, now=sg.datetime(2026, 6, 17, 20, 5, tzinfo=sg.timezone.utc))
    names = {a.agent for a in report.agents}
    assert {"ingestor", "releaser"} <= names
