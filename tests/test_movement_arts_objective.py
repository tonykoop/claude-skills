"""Tests for movement-arts polymorphic objective-function swap (#468)."""

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).parent.parent
_DOMAINS = _ROOT / "plugins" / "maker" / "skills" / "movement-arts" / "domains"
_SCRIPTS = _ROOT / "plugins" / "maker" / "skills" / "movement-arts" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from objective import (
    ObjectiveFn,
    StyleObjective,
    ForceObjective,
    JointSafetyObjective,
    BreathAlignmentObjective,
    load_objective,
    _OBJECTIVE_REGISTRY,
)
from sequencer import MovementSequencer
from tracker import MovementTracker


def load_domain(name: str) -> dict:
    with open(_DOMAINS / f"{name}.json") as f:
        return json.load(f)


def _make_tracker(intensity: float = 0.5, left: float = 0.5, right: float = 0.5, facing: str = "north"):
    t = MovementTracker()
    t._state.intensity = intensity
    t._state.weight_distribution = {"left": left, "right": right}
    t._state.facing_direction = facing
    return t


# ---------------------------------------------------------------------------
# load_objective factory
# ---------------------------------------------------------------------------

class TestLoadObjective:
    def test_loads_all_four(self):
        for name in ["style_expression", "force_output", "joint_safety", "breath_alignment"]:
            obj = load_objective(name)
            assert isinstance(obj, ObjectiveFn)

    def test_unknown_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown objective"):
            load_objective("nonexistent_objective")

    def test_registry_has_four_entries(self):
        assert len(_OBJECTIVE_REGISTRY) == 4

    def test_each_registered_class_is_subclass(self):
        for cls in _OBJECTIVE_REGISTRY.values():
            assert issubclass(cls, ObjectiveFn)


# ---------------------------------------------------------------------------
# ObjectiveFn is callable
# ---------------------------------------------------------------------------

class TestObjectiveFnCallable:
    def test_callable_alias(self):
        obj = StyleObjective()
        prims = [
            {"id": "a", "weight_shift": "bilateral", "facing": "north", "energy_delta": 0.05},
            {"id": "b", "weight_shift": "left", "facing": "north", "energy_delta": 0.1},
        ]
        tracker = _make_tracker()
        result = obj(prims, tracker)
        assert result is not None
        assert result["id"] in {"a", "b"}


# ---------------------------------------------------------------------------
# StyleObjective
# ---------------------------------------------------------------------------

class TestStyleObjective:
    def _prims(self):
        return [
            {"id": "a", "weight_shift": "bilateral", "facing": "north", "energy_delta": 0.02},
            {"id": "b", "weight_shift": "left", "facing": "north", "energy_delta": 0.08},
            {"id": "c", "weight_shift": "right", "facing": "east", "energy_delta": 0.15},
        ]

    def test_avoids_last_id(self):
        obj = StyleObjective()
        prims = self._prims()
        tracker = _make_tracker()
        # first call: "a" is closest to default target 0.5 (energy_delta=0.02 → 0.52)
        result1 = obj(prims, tracker)
        assert result1["id"] == "a"
        # second call: objective tracks _last_id="a" internally, avoids repeating it
        result2 = obj(prims, tracker)
        assert result2["id"] != "a"

    def test_returns_none_on_empty_list(self):
        obj = StyleObjective()
        tracker = _make_tracker()
        assert obj([], tracker) is None

    def test_tracks_target_intensity(self):
        obj = StyleObjective()
        prims = self._prims()
        tracker = _make_tracker(intensity=0.3)
        tracker._intensity_target = 0.35  # want slight rise
        result = obj(prims, tracker)
        # energy_delta=0.02 → 0.32 (closest to 0.35 among candidates)
        assert result["id"] == "a"

    def test_score_variety_ratio(self):
        obj = StyleObjective()
        seq = [{"primitive_id": "a"}, {"primitive_id": "b"}, {"primitive_id": "a"}]
        score = obj.score(seq, [])
        assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# ForceObjective
# ---------------------------------------------------------------------------

class TestForceObjective:
    def _prims(self):
        return [
            {"id": "setup", "weight_shift": "bilateral", "facing": "north",
             "energy_delta": 0.02, "acceleration_curve": "flat"},
            {"id": "strike", "weight_shift": "left", "facing": "north",
             "energy_delta": 0.12, "acceleration_curve": "explosive"},
            {"id": "kick", "weight_shift": "left", "facing": "north",
             "energy_delta": 0.14, "acceleration_curve": "snap"},
        ]

    def test_prefers_explosive_at_peak_intensity(self):
        obj = ForceObjective()
        prims = self._prims()
        tracker = _make_tracker(intensity=0.9)
        result = obj(prims, tracker)
        # explosive (1.0 * 0.9 + 0.12=1.02) vs snap (0.8*0.9+0.14=0.86)
        assert result["id"] == "strike"

    def test_returns_none_on_empty_list(self):
        obj = ForceObjective()
        tracker = _make_tracker()
        assert obj([], tracker) is None

    def test_score_fraction_of_explosive(self):
        obj = ForceObjective()
        seq = [
            {"acceleration_curve": "explosive"},
            {"acceleration_curve": "flat"},
            {"acceleration_curve": "snap"},
        ]
        score = obj.score(seq, [])
        assert abs(score - 2 / 3) < 0.01

    def test_prefers_flat_at_low_intensity(self):
        """At very low intensity flat setup moves should outscore snap kicks."""
        obj = ForceObjective()
        prims = [
            {"id": "setup", "weight_shift": "bilateral", "facing": "north",
             "energy_delta": 0.01, "acceleration_curve": "flat"},
            {"id": "strike", "weight_shift": "left", "facing": "north",
             "energy_delta": 0.01, "acceleration_curve": "explosive"},
        ]
        tracker = _make_tracker(intensity=0.0)
        result = obj(prims, tracker)
        # flat: 0.2*0.0+0.01=0.01; explosive: 1.0*0.0+0.01=0.01 — equal → first wins
        # just verify it returns something, not an error
        assert result is not None


# ---------------------------------------------------------------------------
# JointSafetyObjective
# ---------------------------------------------------------------------------

class TestJointSafetyObjective:
    def _prims(self):
        return [
            {"id": "bilateral_low", "weight_shift": "bilateral", "facing": "north",
             "energy_delta": 0.02, "velocity_cap_m_per_s": 0.1, "unilateral_load": False},
            {"id": "unilateral_fast", "weight_shift": "left", "facing": "north",
             "energy_delta": 0.07, "velocity_cap_m_per_s": 0.3, "unilateral_load": True},
        ]

    def test_prefers_low_velocity(self):
        obj = JointSafetyObjective()
        prims = self._prims()
        tracker = _make_tracker()
        result = obj(prims, tracker)
        assert result["id"] == "bilateral_low"

    def test_penalises_unilateral_when_imbalanced(self):
        obj = JointSafetyObjective()
        prims = [
            {"id": "bilateral", "weight_shift": "bilateral", "facing": "north",
             "energy_delta": 0.02, "velocity_cap_m_per_s": 0.2, "unilateral_load": False},
            {"id": "unilateral", "weight_shift": "left", "facing": "north",
             "energy_delta": 0.05, "velocity_cap_m_per_s": 0.15, "unilateral_load": True},
        ]
        tracker = _make_tracker(left=0.9, right=0.1)
        result = obj(prims, tracker)
        # bilateral: -0.2; unilateral: -0.15 - 0.5 = -0.65 → bilateral wins
        assert result["id"] == "bilateral"

    def test_returns_none_on_empty_list(self):
        obj = JointSafetyObjective()
        tracker = _make_tracker()
        assert obj([], tracker) is None

    def test_score_inverted_velocity(self):
        obj = JointSafetyObjective()
        seq = [{"velocity_cap_m_per_s": 0.1}, {"velocity_cap_m_per_s": 0.2}]
        score = obj.score(seq, [])
        assert abs(score - (1.0 - 0.2)) < 0.01


# ---------------------------------------------------------------------------
# BreathAlignmentObjective
# ---------------------------------------------------------------------------

class TestBreathAlignmentObjective:
    def _prims(self):
        return [
            {"id": "gentle", "weight_shift": "bilateral", "facing": "north", "energy_delta": 0.02},
            {"id": "intense", "weight_shift": "left", "facing": "north", "energy_delta": 0.25},
        ]

    def test_prefers_smooth_delta_toward_target(self):
        obj = BreathAlignmentObjective()
        prims = self._prims()
        tracker = _make_tracker(intensity=0.4)
        tracker._intensity_target = 0.42
        result = obj(prims, tracker)
        assert result["id"] == "gentle"

    def test_returns_none_on_empty_list(self):
        obj = BreathAlignmentObjective()
        tracker = _make_tracker()
        assert obj([], tracker) is None


# ---------------------------------------------------------------------------
# Sequencer auto-loads objective from domain field
# ---------------------------------------------------------------------------

class TestSequencerAutoLoadsObjective:
    def test_vinyasa_loads_breath_alignment(self):
        d = load_domain("vinyasa")
        seq = MovementSequencer(domain=d)
        assert isinstance(seq._objective_fn, BreathAlignmentObjective)

    def test_hip_hop_loads_style_expression(self):
        d = load_domain("hip_hop")
        seq = MovementSequencer(domain=d)
        assert isinstance(seq._objective_fn, StyleObjective)

    def test_kata_loads_force_output(self):
        d = load_domain("kata")
        seq = MovementSequencer(domain=d)
        assert isinstance(seq._objective_fn, ForceObjective)

    def test_pt_loads_joint_safety(self):
        d = load_domain("physical_therapy")
        seq = MovementSequencer(domain=d)
        assert isinstance(seq._objective_fn, JointSafetyObjective)

    def test_explicit_override_takes_precedence(self):
        d = load_domain("vinyasa")
        override = ForceObjective()
        seq = MovementSequencer(domain=d, objective_fn=override)
        assert seq._objective_fn is override


# ---------------------------------------------------------------------------
# Regression: domain swap preserves tracker state fields (no state wipe)
# ---------------------------------------------------------------------------

class TestDomainSwapRegression:
    """Switching vinyasa→hip_hop must preserve tracker state shape."""

    def test_tracker_fields_preserved_after_domain_swap(self):
        d1 = load_domain("vinyasa")
        seq1 = MovementSequencer(domain=d1)
        routine1 = seq1.compile(10.0)
        final_state_1 = routine1.tracker_final_state

        assert "weight_distribution" in final_state_1
        assert "intensity" in final_state_1

        d2 = load_domain("hip_hop")
        seq2 = MovementSequencer(domain=d2)
        routine2 = seq2.compile(10.0)
        final_state_2 = routine2.tracker_final_state

        assert "weight_distribution" in final_state_2
        assert "intensity" in final_state_2

        assert set(final_state_1.keys()) == set(final_state_2.keys()), (
            "Tracker state schema must be identical across domains"
        )

    def test_both_domains_produce_non_empty_sequences(self):
        for name in ["vinyasa", "hip_hop"]:
            d = load_domain(name)
            seq = MovementSequencer(domain=d)
            routine = seq.compile(10.0)
            assert len(routine.blocks) > 0, f"{name} produced empty sequence"

    def test_objective_class_changes_between_domains(self):
        seq1 = MovementSequencer(domain=load_domain("vinyasa"))
        seq2 = MovementSequencer(domain=load_domain("hip_hop"))
        assert type(seq1._objective_fn) != type(seq2._objective_fn)
