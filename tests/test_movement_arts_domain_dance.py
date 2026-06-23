"""Tests for movement-arts domain registry: vinyasa / hip-hop / salsa / ballet (#466)."""

import json
import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).parent.parent
_DOMAINS = _ROOT / "plugins" / "maker" / "skills" / "movement-arts" / "domains"
_SCRIPTS = _ROOT / "plugins" / "maker" / "skills" / "movement-arts" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from sequencer import MovementSequencer, BreathClock, BeatClock
from state_machine import ValidTransitionMachine


DANCE_DOMAINS = ["vinyasa", "hip_hop", "salsa", "ballet"]


def load_domain(name: str) -> dict:
    with open(_DOMAINS / f"{name}.json") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Schema compliance for all 4 domains
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("domain_name", DANCE_DOMAINS)
class TestDomainSchema:
    def test_loads_without_error(self, domain_name):
        d = load_domain(domain_name)
        assert d["domain"] == domain_name

    def test_has_schema_version(self, domain_name):
        d = load_domain(domain_name)
        assert d.get("schema_version") == 1

    def test_has_clock(self, domain_name):
        d = load_domain(domain_name)
        assert "clock" in d
        assert d["clock"]["type"] in {"beat", "breath"}

    def test_has_objective(self, domain_name):
        d = load_domain(domain_name)
        valid_objectives = {"style_expression", "breath_alignment", "force_output", "joint_safety"}
        assert d.get("objective") in valid_objectives

    def test_has_primitives(self, domain_name):
        d = load_domain(domain_name)
        assert isinstance(d["primitives"], list)
        assert len(d["primitives"]) >= 8

    def test_primitives_have_required_fields(self, domain_name):
        d = load_domain(domain_name)
        for p in d["primitives"]:
            assert "id" in p, f"missing id in {p}"
            assert "weight_shift" in p
            assert "facing" in p
            assert "energy_delta" in p
            assert p["weight_shift"] in {"left", "right", "bilateral", "unweighted"}
            assert p["facing"] in {"north", "south", "east", "west", "any"}

    def test_valid_next_non_empty_for_most_primitives(self, domain_name):
        """At least 3 primitives should have a non-empty valid_next list."""
        d = load_domain(domain_name)
        with_valid_next = [p for p in d["primitives"] if p.get("valid_next")]
        assert len(with_valid_next) >= 3

    def test_valid_next_references_existing_ids(self, domain_name):
        d = load_domain(domain_name)
        ids = {p["id"] for p in d["primitives"]}
        for p in d["primitives"]:
            for nxt in p.get("valid_next", []):
                assert nxt in ids, f"'{nxt}' in valid_next of '{p['id']}' is not a valid id"

    def test_no_requires_clinical_review(self, domain_name):
        d = load_domain(domain_name)
        assert d.get("requires_clinical_review", False) is False


# ---------------------------------------------------------------------------
# Domain-specific clock tests
# ---------------------------------------------------------------------------

class TestDomainClocks:
    def test_vinyasa_uses_breath_clock(self):
        d = load_domain("vinyasa")
        assert d["clock"]["type"] == "breath"

    def test_hip_hop_uses_beat_clock(self):
        d = load_domain("hip_hop")
        assert d["clock"]["type"] == "beat"
        assert d["clock"]["count_unit"] == 8

    def test_hip_hop_bpm_range(self):
        d = load_domain("hip_hop")
        bpm_range = d["clock"]["bpm_range"]
        assert bpm_range[0] >= 80 and bpm_range[1] <= 130

    def test_salsa_uses_beat_clock(self):
        d = load_domain("salsa")
        assert d["clock"]["type"] == "beat"

    def test_salsa_bpm_range_fast(self):
        d = load_domain("salsa")
        assert d["clock"]["bpm_range"][0] >= 150

    def test_ballet_uses_beat_clock(self):
        d = load_domain("ballet")
        assert d["clock"]["type"] == "beat"

    def test_ballet_phrase_length(self):
        d = load_domain("ballet")
        assert d["clock"].get("phrase_length") == 8


# ---------------------------------------------------------------------------
# Domain-specific content
# ---------------------------------------------------------------------------

class TestVinyasaContent:
    def test_has_savasana(self):
        d = load_domain("vinyasa")
        ids = {p["id"] for p in d["primitives"]}
        assert "savasana" in ids

    def test_has_sun_salutation(self):
        d = load_domain("vinyasa")
        ids = {p["id"] for p in d["primitives"]}
        assert any("sun" in i or "downward_dog" in i or "plank" in i for i in ids)

    def test_has_warrior_poses(self):
        d = load_domain("vinyasa")
        ids = {p["id"] for p in d["primitives"]}
        assert "warrior_i" in ids
        assert "warrior_ii" in ids

    def test_vinyasa_objective_is_breath_alignment(self):
        d = load_domain("vinyasa")
        assert d["objective"] == "breath_alignment"

    def test_at_least_25_primitives(self):
        d = load_domain("vinyasa")
        assert len(d["primitives"]) >= 25


class TestHipHopContent:
    def test_has_isolations(self):
        d = load_domain("hip_hop")
        ids = {p["id"] for p in d["primitives"]}
        assert any("isolation" in i for i in ids)

    def test_has_tutting(self):
        d = load_domain("hip_hop")
        ids = {p["id"] for p in d["primitives"]}
        assert "tutting" in ids

    def test_has_cypher_step(self):
        d = load_domain("hip_hop")
        ids = {p["id"] for p in d["primitives"]}
        assert "cypher_step" in ids

    def test_hip_hop_objective_is_style_expression(self):
        d = load_domain("hip_hop")
        assert d["objective"] == "style_expression"


class TestSalsaContent:
    def test_has_basic_step(self):
        d = load_domain("salsa")
        ids = {p["id"] for p in d["primitives"]}
        assert "basic_step_leader" in ids

    def test_has_cross_body_lead(self):
        d = load_domain("salsa")
        ids = {p["id"] for p in d["primitives"]}
        assert "cross_body_lead" in ids

    def test_has_turns(self):
        d = load_domain("salsa")
        ids = {p["id"] for p in d["primitives"]}
        assert "right_turn_leader" in ids

    def test_salsa_has_slot_geometry(self):
        """Salsa uses linear-slot: side_step primitives must exist."""
        d = load_domain("salsa")
        ids = {p["id"] for p in d["primitives"]}
        assert "side_step" in ids


class TestBalletContent:
    def test_has_plie(self):
        d = load_domain("ballet")
        ids = {p["id"] for p in d["primitives"]}
        assert "plie_demi" in ids or "plie_grand" in ids

    def test_has_tendu(self):
        d = load_domain("ballet")
        ids = {p["id"] for p in d["primitives"]}
        assert "tendu_front" in ids

    def test_has_pirouette(self):
        d = load_domain("ballet")
        ids = {p["id"] for p in d["primitives"]}
        assert "pirouette_en_dehors" in ids

    def test_has_jete(self):
        d = load_domain("ballet")
        ids = {p["id"] for p in d["primitives"]}
        assert "jete_petit" in ids or "jete_petit_left" in ids


# ---------------------------------------------------------------------------
# Integration: each domain compiles via MovementSequencer
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("domain_name", DANCE_DOMAINS)
def test_domain_compiles_via_sequencer(domain_name):
    d = load_domain(domain_name)
    seq = MovementSequencer(domain=d)
    routine = seq.compile(20.0)
    assert len(routine.blocks) > 0
    assert routine.domain == domain_name


# ---------------------------------------------------------------------------
# Integration: state machine runs on each domain
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("domain_name", DANCE_DOMAINS)
def test_domain_state_machine_valid_next(domain_name):
    d = load_domain(domain_name)
    machine = ValidTransitionMachine(d["primitives"])
    state = {
        "weight_distribution": {"left": 0.5, "right": 0.5},
        "facing_direction": "north",
    }
    first_prim_id = d["primitives"][0]["id"]
    valid = machine.valid_next_maneuvers(state, first_prim_id)
    assert len(valid) >= 1
