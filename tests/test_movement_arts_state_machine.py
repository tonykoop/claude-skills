"""Tests for movement-arts valid-transition state machine (#465)."""

import os
import sys

import pytest

_SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..",
    "plugins", "maker", "skills", "movement-arts", "scripts"
)
sys.path.insert(0, _SCRIPTS)

from state_machine import ValidTransitionMachine, ImpossibleTransitionError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

PRIMITIVES = [
    {
        "id": "neutral_stand",
        "name": "Neutral Stand",
        "weight_shift": "bilateral",
        "facing": "north",
        "energy_delta": 0.0,
        "valid_next": ["step_left", "step_right", "pivot_right"],
    },
    {
        "id": "step_left",
        "name": "Step Left",
        "weight_shift": "left",
        "facing": "north",
        "energy_delta": 0.05,
        "valid_next": ["step_right", "pivot_right", "neutral_stand"],
    },
    {
        "id": "step_right",
        "name": "Step Right",
        "weight_shift": "right",
        "facing": "north",
        "energy_delta": 0.05,
        "valid_next": ["step_left", "neutral_stand"],
    },
    {
        "id": "pivot_right",
        "name": "Pivot Right",
        "weight_shift": "right",
        "facing": "east",
        "energy_delta": 0.08,
        "valid_next": ["step_right", "neutral_stand"],
    },
    {
        "id": "jump_land",
        "name": "Jump and Land",
        "weight_shift": "unweighted",
        "facing": "any",
        "energy_delta": 0.15,
        "valid_next": ["neutral_stand"],
    },
    {
        "id": "reverse_face",
        "name": "About Face",
        "weight_shift": "bilateral",
        "facing": "south",
        "energy_delta": 0.03,
        "valid_next": ["neutral_stand", "step_left"],
    },
]


@pytest.fixture
def machine():
    return ValidTransitionMachine(PRIMITIVES)


def _state(weight_left, weight_right, facing="north"):
    return {
        "weight_distribution": {"left": weight_left, "right": weight_right},
        "facing_direction": facing,
    }


# ---------------------------------------------------------------------------
# Basic valid_next filtering
# ---------------------------------------------------------------------------

class TestValidNextManeuvers:
    def test_bilateral_base_allows_left_and_right(self, machine):
        state = _state(0.5, 0.5)
        valid = machine.valid_next_maneuvers(state, "neutral_stand")
        ids = {p["id"] for p in valid}
        assert "step_left" in ids
        assert "step_right" in ids

    def test_pivot_right_appears_from_neutral(self, machine):
        state = _state(0.5, 0.5)
        valid = machine.valid_next_maneuvers(state, "neutral_stand")
        ids = {p["id"] for p in valid}
        assert "pivot_right" in ids

    def test_valid_next_constrained_by_current_prim(self, machine):
        state = _state(1.0, 0.0)
        valid = machine.valid_next_maneuvers(state, "step_left")
        ids = {p["id"] for p in valid}
        assert "step_right" in ids or "neutral_stand" in ids

    def test_no_current_primitive_returns_all_feasible(self, machine):
        state = _state(0.5, 0.5)
        valid = machine.valid_next_maneuvers(state)
        assert len(valid) >= 3

    def test_returns_list(self, machine):
        state = _state(0.5, 0.5)
        result = machine.valid_next_maneuvers(state)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Weight-shift rules
# ---------------------------------------------------------------------------

class TestWeightShiftRules:
    def test_cannot_shift_to_left_when_fully_left(self, machine):
        """Fully left-weighted: shifting to left again is blocked."""
        state = _state(1.0, 0.0)
        valid = machine.valid_next_maneuvers(state)
        ids = {p["id"] for p in valid}
        # step_left requires full left shift, which is already the case — blocked
        assert "step_left" not in ids

    def test_cannot_shift_to_right_when_fully_right(self, machine):
        state = _state(0.0, 1.0)
        valid = machine.valid_next_maneuvers(state)
        ids = {p["id"] for p in valid}
        assert "step_right" not in ids

    def test_can_shift_right_from_left_base(self, machine):
        state = _state(1.0, 0.0)
        valid = machine.valid_next_maneuvers(state)
        ids = {p["id"] for p in valid}
        assert "step_right" in ids

    def test_can_shift_left_from_right_base(self, machine):
        state = _state(0.0, 1.0)
        valid = machine.valid_next_maneuvers(state)
        ids = {p["id"] for p in valid}
        assert "step_left" in ids

    def test_jump_requires_bilateral_base(self, machine):
        state = _state(0.5, 0.5)
        valid = machine.valid_next_maneuvers(state)
        ids = {p["id"] for p in valid}
        assert "jump_land" in ids

    def test_jump_blocked_from_single_foot(self, machine):
        state = _state(1.0, 0.0)
        valid = machine.valid_next_maneuvers(state)
        ids = {p["id"] for p in valid}
        assert "jump_land" not in ids

    def test_bilateral_always_reachable(self, machine):
        """Neutral stand (bilateral) can be reached from any base."""
        for left, right in [(1.0, 0.0), (0.0, 1.0), (0.5, 0.5)]:
            state = _state(left, right)
            valid = machine.valid_next_maneuvers(state)
            ids = {p["id"] for p in valid}
            assert "neutral_stand" in ids or "reverse_face" in ids


# ---------------------------------------------------------------------------
# Facing rules
# ---------------------------------------------------------------------------

class TestFacingRules:
    def test_adjacent_facing_allowed(self, machine):
        state = _state(0.5, 0.5, facing="north")
        valid = machine.valid_next_maneuvers(state)
        ids = {p["id"] for p in valid}
        # pivot_right → facing=east is adjacent to north
        assert "pivot_right" in ids

    def test_180_flip_allowed_from_bilateral(self, machine):
        """north → south (180°) is allowed when weight is bilateral."""
        state = _state(0.5, 0.5, facing="north")
        valid = machine.valid_next_maneuvers(state)
        ids = {p["id"] for p in valid}
        assert "reverse_face" in ids  # reverse_face: facing=south

    def test_180_flip_blocked_from_single_foot(self, machine):
        """north → south (180°) is blocked when fully on one foot."""
        state = _state(1.0, 0.0, facing="north")
        valid = machine.valid_next_maneuvers(state)
        ids = {p["id"] for p in valid}
        assert "reverse_face" not in ids

    def test_any_facing_always_valid(self, machine):
        """Primitives with facing='any' pass the facing gate regardless of current facing."""
        state = _state(0.5, 0.5, facing="south")
        valid = machine.valid_next_maneuvers(state)
        ids = {p["id"] for p in valid}
        assert "jump_land" in ids  # jump_land has facing=any


# ---------------------------------------------------------------------------
# assert_transition_valid
# ---------------------------------------------------------------------------

class TestAssertTransitionValid:
    def test_valid_transition_does_not_raise(self, machine):
        state = _state(0.5, 0.5)
        step_right = next(p for p in PRIMITIVES if p["id"] == "step_right")
        machine.assert_transition_valid(state, step_right, "neutral_stand")

    def test_impossible_transition_raises(self, machine):
        state = _state(1.0, 0.0)
        step_left = next(p for p in PRIMITIVES if p["id"] == "step_left")
        with pytest.raises(ImpossibleTransitionError):
            machine.assert_transition_valid(state, step_left, "neutral_stand")

    def test_error_message_contains_primitive_id(self, machine):
        state = _state(0.0, 1.0)
        step_right = next(p for p in PRIMITIVES if p["id"] == "step_right")
        with pytest.raises(ImpossibleTransitionError, match="step_right"):
            machine.assert_transition_valid(state, step_right, "step_right")

    def test_error_message_contains_weight_info(self, machine):
        state = _state(1.0, 0.0)
        step_left = next(p for p in PRIMITIVES if p["id"] == "step_left")
        with pytest.raises(ImpossibleTransitionError, match="weight"):
            machine.assert_transition_valid(state, step_left)


# ---------------------------------------------------------------------------
# Domain-agnostic / rule-based checks
# ---------------------------------------------------------------------------

class TestRuleBasedNotEnumerated:
    def test_machine_works_with_any_primitive_set(self):
        """State machine is parameterized by primitives, not hardcoded."""
        custom_prims = [
            {"id": "a", "weight_shift": "bilateral", "facing": "north", "valid_next": ["b"]},
            {"id": "b", "weight_shift": "left", "facing": "east", "valid_next": ["a"]},
        ]
        m = ValidTransitionMachine(custom_prims)
        state = _state(0.5, 0.5)
        valid = m.valid_next_maneuvers(state, "a")
        assert any(p["id"] == "b" for p in valid)

    def test_empty_primitives_returns_empty(self):
        m = ValidTransitionMachine([])
        state = _state(0.5, 0.5)
        assert m.valid_next_maneuvers(state) == []

    def test_at_least_five_valid_from_bilateral_neutral(self, machine):
        """Bilateral neutral base should yield >= 5 valid candidates from full set."""
        state = _state(0.5, 0.5)
        valid = machine.valid_next_maneuvers(state)
        assert len(valid) >= 5
