"""Tests for the human-in-the-loop circuit breaker (#258)."""
import json
import sys
from pathlib import Path

import pytest

GOV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOV))

import circuit_breaker as cb  # noqa: E402
import spend_guard as sg  # noqa: E402

ROSTER_PATH = GOV / "agent-roster.yaml"


@pytest.fixture(scope="module")
def roster():
    return sg.load_roster(str(ROSTER_PATH))


# A valid cross-model handoff (frank/spark audited by alice/opus) so the
# confidence is trustworthy and only the breaker logic is under test.
def _verdict(**over):
    base = {
        "asset_id": "robotics/urdf-knee-fix-001",
        "creator_agent": "frank", "creator_model": "gpt-5.3-codex-spark",
        "auditor_agent": "alice", "auditor_model": "claude-opus-4-8",
        "linters_passed": True,
        "confidence": 0.96,
        "action": "merge_pr",
        "target_branch": "feature/knee-fix",
        "human_signature": None,
    }
    base.update(over)
    return base


# --- confidence-threshold routing (acceptance #1) ---------------------------
def test_high_confidence_clean_linters_auto_advances(roster):
    d = cb.decide(roster, _verdict(confidence=0.96))
    assert d.status == cb.AUTO_ADVANCE
    assert d.auto_advance
    assert d.escalation is None


def test_low_confidence_escalates(roster):
    d = cb.decide(roster, _verdict(confidence=0.80))
    assert d.status == cb.ESCALATE
    assert not d.auto_advance


def test_confidence_exactly_at_bar_advances(roster):
    d = cb.decide(roster, _verdict(confidence=0.90))
    assert d.status == cb.AUTO_ADVANCE


def test_linter_failure_escalates_regardless_of_confidence(roster):
    d = cb.decide(roster, _verdict(confidence=1.0, linters_passed=False))
    assert d.status == cb.ESCALATE
    assert any("linters" in r for r in d.reasons)


def test_out_of_range_confidence_escalates(roster):
    d = cb.decide(roster, _verdict(confidence=1.5))
    assert d.status == cb.ESCALATE


def test_non_numeric_confidence_escalates(roster):
    d = cb.decide(roster, _verdict(confidence=None))
    assert d.status == cb.ESCALATE


# --- escalation pings the human only for ambiguous cases (acceptance #2) -----
def test_escalation_payload_pings_human(roster):
    d = cb.decide(roster, _verdict(confidence=0.50))
    assert d.escalation is not None
    assert d.escalation["ping"].startswith("@")
    assert d.escalation["asset_id"] == "robotics/urdf-knee-fix-001"


def test_auto_advance_does_not_ping(roster):
    d = cb.decide(roster, _verdict(confidence=0.99))
    assert d.escalation is None  # the easy 90% never pages a human


# --- immutable deploy barriers (acceptance #3) ------------------------------
def test_push_to_main_blocked_even_at_full_confidence(roster):
    # The hardest rule: confidence 1.0 + clean linters still cannot push main.
    d = cb.decide(roster, _verdict(confidence=1.0, action="push_main",
                                   target_branch="main"))
    assert d.status == cb.BLOCK
    assert not d.auto_advance
    assert d.escalation["kind"] == "signature_required"


def test_protected_branch_main_blocks(roster):
    d = cb.decide(roster, _verdict(confidence=1.0, action="merge_pr",
                                   target_branch="main"))
    assert d.status == cb.BLOCK


def test_publish_action_blocks_without_signature(roster):
    d = cb.decide(roster, _verdict(action="publish", target_branch="feature/x"))
    assert d.status == cb.BLOCK


def test_human_signature_releases_the_barrier(roster):
    d = cb.decide(roster, _verdict(
        action="push_main", target_branch="main",
        human_signature={"signed_by": "tony", "at": "2026-06-17T21:00:00Z"},
    ))
    assert d.status == cb.AUTO_ADVANCE
    assert d.auto_advance


def test_empty_signature_does_not_release_barrier(roster):
    d = cb.decide(roster, _verdict(action="publish", human_signature=""))
    assert d.status == cb.BLOCK


# --- the immutable floor cannot be removed via config -----------------------
def test_immutable_floor_holds_when_config_lists_emptied(roster):
    import copy
    r = copy.deepcopy(roster)
    r["circuit_breaker"]["protected_actions"] = []
    r["circuit_breaker"]["protected_branches"] = []
    # main + push_main are in the hardcoded floor, so still protected.
    assert cb.is_protected(r, "push_main", "feature/x")
    assert cb.is_protected(r, "merge_pr", "main")
    d = cb.decide(r, _verdict(confidence=1.0, action="push_main",
                              target_branch="main"))
    assert d.status == cb.BLOCK


def test_disabled_breaker_still_guards_protected_actions(roster):
    import copy
    r = copy.deepcopy(roster)
    r["circuit_breaker"]["enabled"] = False
    # Non-protected work flows through when disabled...
    assert cb.decide(r, _verdict()).status == cb.AUTO_ADVANCE
    # ...but the deploy barrier is never switched off.
    d = cb.decide(r, _verdict(action="deploy", target_branch="main"))
    assert d.status == cb.BLOCK


# --- untrustworthy audit short-circuits regardless of confidence ------------
def test_self_review_handoff_escalates(roster):
    d = cb.decide(roster, _verdict(
        creator_agent="alice", creator_model="claude-opus-4-8",
        auditor_agent="alice", auditor_model="claude-opus-4-8",
        confidence=1.0,
    ))
    assert d.status == cb.ESCALATE
    assert any("handoff" in r for r in d.reasons)


def test_same_family_audit_escalates(roster):
    d = cb.decide(roster, _verdict(
        creator_agent="alice", creator_model="claude-opus-4-8",
        auditor_agent="bob", auditor_model="claude-opus-4-6",
        confidence=0.99,
    ))
    assert d.status == cb.ESCALATE


# --- CLI --------------------------------------------------------------------
def test_cli_auto_advance_exit0(tmp_path):
    v = tmp_path / "verdict.json"
    v.write_text(json.dumps(_verdict(confidence=0.97)))
    rc = cb.main(["decide", "--verdict", str(v), "--config", str(ROSTER_PATH)])
    assert rc == 0


def test_cli_block_main_exit1(tmp_path):
    v = tmp_path / "verdict.json"
    v.write_text(json.dumps(_verdict(confidence=1.0, action="push_main",
                                     target_branch="main")))
    rc = cb.main(["decide", "--verdict", str(v), "--config", str(ROSTER_PATH)])
    assert rc == 1
