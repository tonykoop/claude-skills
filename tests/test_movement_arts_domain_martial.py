"""Tests for movement-arts domain registry: tai chi / capoeira / kata / physical therapy (#467)."""

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).parent.parent
_DOMAINS = _ROOT / "plugins" / "maker" / "skills" / "movement-arts" / "domains"
_SCRIPTS = _ROOT / "plugins" / "maker" / "skills" / "movement-arts" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from sequencer import MovementSequencer, BreathClock, BeatClock
from state_machine import ValidTransitionMachine


MARTIAL_DOMAINS = ["tai_chi", "capoeira", "kata"]
ALL_467_DOMAINS = ["tai_chi", "capoeira", "kata", "physical_therapy"]


def load_domain(name: str) -> dict:
    with open(_DOMAINS / f"{name}.json") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Schema compliance — all 4 domains
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("domain_name", ALL_467_DOMAINS)
class TestDomainSchema467:
    def test_loads_without_error(self, domain_name):
        d = load_domain(domain_name)
        assert d["domain"] == domain_name

    def test_has_schema_version_1(self, domain_name):
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

    def test_has_primitives_list(self, domain_name):
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

    def test_valid_next_references_existing_ids(self, domain_name):
        d = load_domain(domain_name)
        ids = {p["id"] for p in d["primitives"]}
        for p in d["primitives"]:
            for nxt in p.get("valid_next", []):
                assert nxt in ids, f"'{nxt}' in valid_next of '{p['id']}' is not a valid id"


# ---------------------------------------------------------------------------
# Domain-specific clock tests
# ---------------------------------------------------------------------------

class TestMartialDomainClocks:
    def test_tai_chi_uses_breath_clock(self):
        d = load_domain("tai_chi")
        assert d["clock"]["type"] == "breath"

    def test_tai_chi_is_slow_bpm(self):
        d = load_domain("tai_chi")
        assert d["clock"]["bpm"] <= 8

    def test_capoeira_uses_beat_clock(self):
        d = load_domain("capoeira")
        assert d["clock"]["type"] == "beat"

    def test_capoeira_3_count(self):
        d = load_domain("capoeira")
        assert d["clock"]["count_unit"] == 3

    def test_kata_uses_breath_clock(self):
        d = load_domain("kata")
        assert d["clock"]["type"] == "breath"

    def test_pt_uses_breath_clock(self):
        d = load_domain("physical_therapy")
        assert d["clock"]["type"] == "breath"

    def test_pt_is_slow_bpm(self):
        d = load_domain("physical_therapy")
        assert d["clock"]["bpm"] <= 8


# ---------------------------------------------------------------------------
# Tai chi content
# ---------------------------------------------------------------------------

class TestTaiChiContent:
    def test_has_grasp_bird_tail(self):
        d = load_domain("tai_chi")
        ids = {p["id"] for p in d["primitives"]}
        assert "grasp_bird_tail_ward_off" in ids

    def test_has_single_whip(self):
        d = load_domain("tai_chi")
        ids = {p["id"] for p in d["primitives"]}
        assert "single_whip" in ids

    def test_has_cloud_hands(self):
        d = load_domain("tai_chi")
        ids = {p["id"] for p in d["primitives"]}
        assert "cloud_hands_left" in ids or "wave_hands_like_clouds" in ids

    def test_has_closing_form(self):
        d = load_domain("tai_chi")
        ids = {p["id"] for p in d["primitives"]}
        assert "closing_form" in ids

    def test_no_clinical_review(self):
        d = load_domain("tai_chi")
        assert d.get("requires_clinical_review", False) is False

    def test_objective_is_breath_alignment(self):
        d = load_domain("tai_chi")
        assert d["objective"] == "breath_alignment"

    def test_grasp_bird_tail_four_phase_chain(self):
        """Ward-off → rollback → press → push must form a chain."""
        d = load_domain("tai_chi")
        by_id = {p["id"]: p for p in d["primitives"]}
        assert "grasp_bird_tail_rollback" in by_id.get("grasp_bird_tail_ward_off", {}).get("valid_next", [])
        assert "grasp_bird_tail_press" in by_id.get("grasp_bird_tail_rollback", {}).get("valid_next", [])
        assert "grasp_bird_tail_push" in by_id.get("grasp_bird_tail_press", {}).get("valid_next", [])


# ---------------------------------------------------------------------------
# Capoeira content
# ---------------------------------------------------------------------------

class TestCapoeiraCaontent:
    def test_has_ginga_loop(self):
        """Ginga left → right → left must be a valid loop."""
        d = load_domain("capoeira")
        by_id = {p["id"]: p for p in d["primitives"]}
        assert "ginga_right" in by_id["ginga_left"]["valid_next"]
        assert "ginga_left" in by_id["ginga_right"]["valid_next"]

    def test_ginga_duration_is_3_beats(self):
        d = load_domain("capoeira")
        gingas = [p for p in d["primitives"] if p["id"].startswith("ginga")]
        for g in gingas:
            assert g["duration_beats"] == 3

    def test_has_meia_lua(self):
        d = load_domain("capoeira")
        ids = {p["id"] for p in d["primitives"]}
        assert "meia_lua_de_frente" in ids
        assert "meia_lua_de_compasso" in ids

    def test_has_au_cartwheel(self):
        d = load_domain("capoeira")
        ids = {p["id"] for p in d["primitives"]}
        assert "au" in ids

    def test_au_is_unweighted(self):
        d = load_domain("capoeira")
        au = next(p for p in d["primitives"] if p["id"] == "au")
        assert au["weight_shift"] == "unweighted"

    def test_has_negativa(self):
        d = load_domain("capoeira")
        ids = {p["id"] for p in d["primitives"]}
        assert "negativa" in ids

    def test_objective_is_style_expression(self):
        d = load_domain("capoeira")
        assert d["objective"] == "style_expression"

    def test_no_clinical_review(self):
        d = load_domain("capoeira")
        assert d.get("requires_clinical_review", False) is False


# ---------------------------------------------------------------------------
# Kata content
# ---------------------------------------------------------------------------

class TestKataContent:
    def test_has_yoi_and_yame(self):
        d = load_domain("kata")
        ids = {p["id"] for p in d["primitives"]}
        assert "yoi" in ids
        assert "yame" in ids

    def test_yame_leads_back_to_yoi(self):
        d = load_domain("kata")
        yame = next(p for p in d["primitives"] if p["id"] == "yame")
        assert "yoi" in yame["valid_next"]

    def test_has_gedan_barai(self):
        d = load_domain("kata")
        ids = {p["id"] for p in d["primitives"]}
        assert "gedan_barai" in ids

    def test_has_mae_geri(self):
        d = load_domain("kata")
        ids = {p["id"] for p in d["primitives"]}
        assert "mae_geri" in ids

    def test_primitives_have_acceleration_curve(self):
        """Kata primitives declare acceleration_curve (force_output domain extra field)."""
        d = load_domain("kata")
        for p in d["primitives"]:
            assert "acceleration_curve" in p, f"'{p['id']}' missing acceleration_curve"
            assert p["acceleration_curve"] in {
                "flat", "fast_finish", "explosive", "snap", "sustained", "impact"
            }

    def test_primitives_have_embusen_direction(self):
        """Kata uses embusen (compass floor-pattern); each primitive declares its direction."""
        d = load_domain("kata")
        for p in d["primitives"]:
            assert "embusen_direction" in p, f"'{p['id']}' missing embusen_direction"
            assert p["embusen_direction"] in {"north", "south", "east", "west"}

    def test_objective_is_force_output(self):
        d = load_domain("kata")
        assert d["objective"] == "force_output"

    def test_no_clinical_review(self):
        d = load_domain("kata")
        assert d.get("requires_clinical_review", False) is False

    def test_explosive_moves_have_short_duration(self):
        """Explosive kata moves should be ≤3 beats (kime is brief)."""
        d = load_domain("kata")
        for p in d["primitives"]:
            if p.get("acceleration_curve") == "explosive":
                assert p["duration_beats"] <= 3, (
                    f"'{p['id']}' is explosive but duration_beats={p['duration_beats']}"
                )


# ---------------------------------------------------------------------------
# Physical therapy content
# ---------------------------------------------------------------------------

class TestPhysicalTherapyContent:
    def test_requires_clinical_review_is_true(self):
        d = load_domain("physical_therapy")
        assert d.get("requires_clinical_review") is True

    def test_objective_is_joint_safety(self):
        d = load_domain("physical_therapy")
        assert d["objective"] == "joint_safety"

    def test_has_bridging(self):
        d = load_domain("physical_therapy")
        ids = {p["id"] for p in d["primitives"]}
        assert "bridging" in ids

    def test_has_single_leg_stance(self):
        d = load_domain("physical_therapy")
        ids = {p["id"] for p in d["primitives"]}
        assert "single_leg_stance_left" in ids
        assert "single_leg_stance_right" in ids

    def test_primitives_have_velocity_cap(self):
        d = load_domain("physical_therapy")
        for p in d["primitives"]:
            assert "velocity_cap_m_per_s" in p, f"'{p['id']}' missing velocity_cap_m_per_s"
            assert isinstance(p["velocity_cap_m_per_s"], (int, float))
            assert p["velocity_cap_m_per_s"] >= 0

    def test_primitives_have_unilateral_load_flag(self):
        d = load_domain("physical_therapy")
        for p in d["primitives"]:
            assert "unilateral_load" in p, f"'{p['id']}' missing unilateral_load"
            assert isinstance(p["unilateral_load"], bool)

    def test_primitives_have_rom_target(self):
        d = load_domain("physical_therapy")
        for p in d["primitives"]:
            assert "ROM_target_deg" in p, f"'{p['id']}' missing ROM_target_deg"
            assert isinstance(p["ROM_target_deg"], (int, float))

    def test_pt_safety_gate_raises_without_acknowledgement(self):
        """Sequencer must refuse to compile PT without safety_acknowledged=True."""
        d = load_domain("physical_therapy")
        seq = MovementSequencer(domain=d)
        with pytest.raises(PermissionError):
            seq.compile(20.0, safety_acknowledged=False)

    def test_pt_compiles_with_acknowledgement(self):
        d = load_domain("physical_therapy")
        seq = MovementSequencer(domain=d)
        routine = seq.compile(20.0, safety_acknowledged=True)
        assert len(routine.blocks) > 0


# ---------------------------------------------------------------------------
# Integration: martial domains compile via sequencer
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("domain_name", MARTIAL_DOMAINS)
def test_martial_domain_compiles_via_sequencer(domain_name):
    d = load_domain(domain_name)
    seq = MovementSequencer(domain=d)
    routine = seq.compile(20.0)
    assert len(routine.blocks) > 0
    assert routine.domain == domain_name


# ---------------------------------------------------------------------------
# Integration: state machine runs on martial domains
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("domain_name", MARTIAL_DOMAINS)
def test_martial_domain_state_machine_valid_next(domain_name):
    d = load_domain(domain_name)
    machine = ValidTransitionMachine(d["primitives"])
    state = {
        "weight_distribution": {"left": 0.5, "right": 0.5},
        "facing_direction": "north",
    }
    first_prim_id = d["primitives"][0]["id"]
    valid = machine.valid_next_maneuvers(state, first_prim_id)
    assert len(valid) >= 1


# ---------------------------------------------------------------------------
# Cross-domain: capoeira ginga 3-count loop locks into state machine
# ---------------------------------------------------------------------------

class TestCapoeiraGingaLoop:
    def test_ginga_left_right_transition_valid(self):
        d = load_domain("capoeira")
        machine = ValidTransitionMachine(d["primitives"])
        state_after_ginga_left = {
            "weight_distribution": {"left": 0.9, "right": 0.1},
            "facing_direction": "west",
        }
        valid_ids = [p["id"] for p in machine.valid_next_maneuvers(state_after_ginga_left, "ginga_left")]
        assert "ginga_right" in valid_ids

    def test_ginga_right_left_transition_valid(self):
        d = load_domain("capoeira")
        machine = ValidTransitionMachine(d["primitives"])
        state_after_ginga_right = {
            "weight_distribution": {"left": 0.1, "right": 0.9},
            "facing_direction": "east",
        }
        valid_ids = [p["id"] for p in machine.valid_next_maneuvers(state_after_ginga_right, "ginga_right")]
        assert "ginga_left" in valid_ids
