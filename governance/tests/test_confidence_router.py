"""Tests for the confidence-score circuit breaker (#258)."""
import sys
from pathlib import Path

import pytest

GOV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOV))

import confidence_router as cr  # noqa: E402
import spend_guard as sg  # noqa: E402

ROSTER_PATH = GOV / "agent-roster.yaml"


@pytest.fixture(scope="module")
def roster():
    return sg.load_roster(str(ROSTER_PATH))


# --- route_by_confidence -----------------------------------------------------

def test_high_confidence_all_gates_passed_auto_advances(roster):
    audit = {"id": "a1", "confidence_score": 95, "gates_passed": True}
    res = cr.route_by_confidence(audit, roster)
    assert res.status == cr.AUTO_ADVANCE
    assert res.score == 95.0


def test_exactly_at_threshold_auto_advances(roster):
    audit = {"confidence_score": 90, "gates_passed": True}
    res = cr.route_by_confidence(audit, roster)
    assert res.status == cr.AUTO_ADVANCE


def test_below_threshold_escalates(roster):
    audit = {"id": "a2", "confidence_score": 89.9, "gates_passed": True}
    res = cr.route_by_confidence(audit, roster)
    assert res.status == cr.ESCALATE_HUMAN
    assert "89.9" in res.reason


def test_gate_failure_escalates_regardless_of_score(roster):
    audit = {
        "confidence_score": 99,
        "gates_passed": False,
        "failed_gates": ["sandbox", "markdown"],
    }
    res = cr.route_by_confidence(audit, roster)
    assert res.status == cr.ESCALATE_HUMAN
    assert "sandbox" in res.reason


def test_failed_gates_list_escalates_even_if_gates_passed_true(roster):
    # failed_gates present overrides gates_passed: True
    audit = {"confidence_score": 95, "gates_passed": True, "failed_gates": ["urdf"]}
    res = cr.route_by_confidence(audit, roster)
    assert res.status == cr.ESCALATE_HUMAN


def test_missing_confidence_score_escalates(roster):
    audit = {"id": "a3", "gates_passed": True}
    res = cr.route_by_confidence(audit, roster)
    assert res.status == cr.ESCALATE_HUMAN
    assert "missing" in res.reason


def test_no_gates_key_defaults_to_passed(roster):
    # When gates_passed absent and no failed_gates, score decides routing.
    audit = {"confidence_score": 95}
    res = cr.route_by_confidence(audit, roster)
    assert res.status == cr.AUTO_ADVANCE


def test_asset_id_echoed(roster):
    audit = {"id": "MY-ASSET-42", "confidence_score": 91, "gates_passed": True}
    res = cr.route_by_confidence(audit, roster)
    assert res.asset_id == "MY-ASSET-42"


def test_custom_threshold_respected(roster):
    # Patch threshold by passing a modified roster copy.
    import copy
    low_roster = copy.deepcopy(roster)
    low_roster["confidence_routing"] = {"auto_advance_threshold_pct": 50}
    audit = {"confidence_score": 55, "gates_passed": True}
    res = cr.route_by_confidence(audit, low_roster)
    assert res.status == cr.AUTO_ADVANCE


# --- check_deploy_clearance --------------------------------------------------

def test_human_signed_off_true_clears_deploy():
    audit = {"id": "a4", "confidence_score": 95, "human_signed_off": True}
    res = cr.check_deploy_clearance(audit)
    assert res.status == cr.DEPLOY_CLEAR


def test_human_signed_off_false_blocks_deploy():
    audit = {"human_signed_off": False}
    res = cr.check_deploy_clearance(audit)
    assert res.status == cr.DEPLOY_BLOCKED


def test_human_signed_off_absent_blocks_deploy():
    # Missing field MUST block — fail closed.
    audit = {"confidence_score": 99, "gates_passed": True}
    res = cr.check_deploy_clearance(audit)
    assert res.status == cr.DEPLOY_BLOCKED


def test_deploy_blocked_even_with_high_confidence():
    # Immutable barrier: confidence does not override the signoff requirement.
    audit = {"confidence_score": 100, "gates_passed": True, "human_signed_off": False}
    res = cr.check_deploy_clearance(audit)
    assert res.status == cr.DEPLOY_BLOCKED


def test_deploy_asset_id_echoed():
    audit = {"id": "REL-7", "human_signed_off": True}
    res = cr.check_deploy_clearance(audit)
    assert res.asset_id == "REL-7"
