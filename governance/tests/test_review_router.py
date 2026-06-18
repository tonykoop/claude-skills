"""Tests for the adversarial cross-model QA router (#256)."""
import json
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


# --- assignment (acceptance: generation and audit are different agents/models)
def test_opus_creator_routed_to_non_opus_auditor(roster):
    res = rr.assign_auditor(roster, {
        "creator_agent": "alice", "creator_model": "claude-opus-4-8",
    })
    assert res.ok
    assert res.auditor != "alice"
    # auditor family must differ from opus
    auditor_model = roster["agents"][res.auditor]["model"]
    assert rr.family_of(roster, auditor_model) != "opus"


def test_assignment_is_deterministic(roster):
    asset = {"creator_agent": "cindy", "creator_model": "claude-sonnet-4-6"}
    a = rr.assign_auditor(roster, asset)
    b = rr.assign_auditor(roster, asset)
    assert a.auditor == b.auditor


def test_codex_creator_routed_to_non_codex(roster):
    res = rr.assign_auditor(roster, {
        "creator_agent": "dan", "creator_model": "codex-gpt-5.5",
    })
    assert res.ok
    auditor_model = roster["agents"][res.auditor]["model"]
    assert rr.family_of(roster, auditor_model) != "gpt-5.5"


def test_assign_missing_fields_blocks(roster):
    res = rr.assign_auditor(roster, {"creator_agent": "alice"})
    assert not res.ok


# --- validation gate (acceptance: routing rule enforced) --------------------
def test_valid_cross_model_handoff_passes(roster):
    res = rr.validate_handoff(roster, {
        "creator_agent": "alice", "creator_model": "claude-opus-4-8",
        "auditor_agent": "dan", "auditor_model": "codex-gpt-5.5",
    })
    assert res.ok, res.violations


def test_self_review_same_agent_blocked(roster):
    res = rr.validate_handoff(roster, {
        "creator_agent": "alice", "creator_model": "claude-opus-4-8",
        "auditor_agent": "alice", "auditor_model": "claude-opus-4-8",
    })
    assert not res.ok
    assert any("self-review" in v for v in res.violations)


def test_same_family_different_version_blocked(roster):
    # opus-4-6 auditing opus-4-8: different version, SAME family -> blocked
    res = rr.validate_handoff(roster, {
        "creator_agent": "alice", "creator_model": "claude-opus-4-8",
        "auditor_agent": "bob", "auditor_model": "claude-opus-4-6",
    })
    assert not res.ok
    assert any("model family" in v for v in res.violations)


def test_unknown_auditor_family_blocked(roster):
    res = rr.validate_handoff(roster, {
        "creator_agent": "alice", "creator_model": "claude-opus-4-8",
        "auditor_agent": "dan", "auditor_model": "some-future-model",
    })
    assert not res.ok
    assert any("unknown family" in v for v in res.violations)


def test_missing_handoff_fields_blocked(roster):
    res = rr.validate_handoff(roster, {
        "creator_agent": "alice", "creator_model": "claude-opus-4-8",
    })
    assert not res.ok
    assert any("missing field" in v for v in res.violations)


# --- fail-closed on UNKNOWN CREATOR family (claude-skills#265 review) --------
def test_unknown_creator_family_blocked(roster):
    # Symmetric to the unknown-auditor rule: an unknown creator family must
    # also fail closed, since distinctness can't be certified.
    res = rr.validate_handoff(roster, {
        "creator_agent": "dan", "creator_model": "some-vendor-x-model",
        "auditor_agent": "alice", "auditor_model": "claude-opus-4-8",
    })
    assert not res.ok
    assert any("creator model" in v and "unknown family" in v for v in res.violations)


def test_version_bump_unknown_creator_is_not_a_self_review_loophole(roster):
    # THE bug dan caught: a creator on an unmapped NEW version of opus
    # (claude-opus-4-9 -> unknown) "audited" by alice/opus-4-8 must NOT pass.
    # Before the fix this slipped through as distinct (unknown != opus) — i.e.
    # opus auditing opus, the exact self-review family comparison exists to stop.
    res = rr.validate_handoff(roster, {
        "creator_agent": "dan", "creator_model": "claude-opus-4-9",
        "auditor_agent": "alice", "auditor_model": "claude-opus-4-8",
    })
    assert not res.ok
    assert any("unknown family" in v for v in res.violations)


def test_assign_unknown_creator_family_fails_closed(roster):
    res = rr.assign_auditor(roster, {
        "creator_agent": "dan", "creator_model": "some-vendor-x-model",
    })
    assert not res.ok
    assert "unknown family" in res.reason


def test_spark_creator_now_known_and_routes(roster):
    # The fleet's spark personas (frank/elsa/ivan) must resolve to a KNOWN
    # family so the new fail-closed rule doesn't block legitimate reviews.
    assert rr.family_of(roster, "gpt-5.3-codex-spark") == "spark"
    res = rr.validate_handoff(roster, {
        "creator_agent": "frank", "creator_model": "gpt-5.3-codex-spark",
        "auditor_agent": "alice", "auditor_model": "claude-opus-4-8",
    })
    assert res.ok, res.violations


# --- CLI --------------------------------------------------------------------
def test_cli_validate_blocks_self_review(tmp_path):
    h = tmp_path / "handoff.json"
    h.write_text(json.dumps({
        "creator_agent": "alice", "creator_model": "claude-opus-4-8",
        "auditor_agent": "alice", "auditor_model": "claude-opus-4-8",
    }))
    rc = rr.main(["validate", "--handoff", str(h), "--config", str(ROSTER_PATH)])
    assert rc == 1


def test_cli_assign_succeeds(tmp_path):
    a = tmp_path / "asset.json"
    a.write_text(json.dumps({
        "creator_agent": "alice", "creator_model": "claude-opus-4-8",
    }))
    rc = rr.main(["assign", "--asset", str(a), "--config", str(ROSTER_PATH)])
    assert rc == 0
