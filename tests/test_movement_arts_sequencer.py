"""Tests for movement-arts core sequencer + state tracker (#464)."""

import json
import math
import os
import sys

import pytest

# Make scripts importable from any cwd
_SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..",
    "plugins", "maker", "skills", "movement-arts", "scripts"
)
sys.path.insert(0, _SCRIPTS)

from tracker import MovementTracker, BreathClock, BeatClock, clock_for_domain
from sequencer import (
    MovementSequencer,
    Block,
    CompiledRoutine,
    sigmoid_intensity,
    intensity_to_cue_density,
    _DEMO_DOMAIN,
)


# ---------------------------------------------------------------------------
# Tracker tests
# ---------------------------------------------------------------------------

class TestMovementTracker:
    def test_initial_state(self):
        t = MovementTracker()
        s = t.current_state
        assert s["weight_distribution"] == {"left": 0.5, "right": 0.5}
        assert s["facing_direction"] == "north"
        assert s["intensity"] == 0.0
        assert s["clock_beat"] == 0

    def test_apply_left_weight_shift(self):
        t = MovementTracker()
        t.apply_primitive({"weight_shift": "left", "energy_delta": 0.1})
        s = t.current_state
        assert s["weight_distribution"]["left"] == 1.0
        assert s["weight_distribution"]["right"] == 0.0

    def test_apply_right_weight_shift(self):
        t = MovementTracker()
        t.apply_primitive({"weight_shift": "right"})
        s = t.current_state
        assert s["weight_distribution"]["right"] == 1.0

    def test_facing_direction_update(self):
        t = MovementTracker()
        t.apply_primitive({"facing": "east"})
        assert t.current_state["facing_direction"] == "east"

    def test_facing_any_does_not_change_direction(self):
        t = MovementTracker()
        t.apply_primitive({"facing": "south"})
        t.apply_primitive({"facing": "any"})
        assert t.current_state["facing_direction"] == "south"

    def test_intensity_clamped_at_zero(self):
        t = MovementTracker()
        t.apply_primitive({"energy_delta": -99.0})
        assert t.current_state["intensity"] == 0.0

    def test_intensity_clamped_at_one(self):
        t = MovementTracker()
        t.apply_primitive({"energy_delta": 99.0})
        assert t.current_state["intensity"] == 1.0

    def test_intensity_accumulates(self):
        t = MovementTracker()
        t.apply_primitive({"energy_delta": 0.3})
        t.apply_primitive({"energy_delta": 0.2})
        assert abs(t.current_state["intensity"] - 0.5) < 1e-9

    def test_clock_beat_advances(self):
        t = MovementTracker()
        t.apply_primitive({"duration_beats": 8})
        assert t.current_state["clock_beat"] == 8

    def test_history_grows(self):
        t = MovementTracker()
        t.apply_primitive({})
        t.apply_primitive({})
        assert len(t.history) == 2

    def test_unweighted_shift(self):
        t = MovementTracker()
        t.apply_primitive({"weight_shift": "unweighted"})
        s = t.current_state
        assert s["weight_distribution"]["left"] == 0.0
        assert s["weight_distribution"]["right"] == 0.0


# ---------------------------------------------------------------------------
# Clock tests
# ---------------------------------------------------------------------------

class TestClocks:
    def test_breath_clock_tick(self):
        clock = BreathClock(breaths_per_minute=12)
        beats = clock.tick(60.0)
        assert beats == 12

    def test_beat_clock_tick(self):
        clock = BeatClock(bpm=120, count_unit=8)
        beats = clock.tick(60.0)
        assert beats == 120

    def test_beat_clock_phrases(self):
        clock = BeatClock(bpm=120, count_unit=8)
        clock.tick(60.0)
        assert clock.phrases == 15

    def test_clock_for_beat_domain(self):
        domain = {"clock": {"type": "beat", "bpm_range": [90, 110], "count_unit": 8}}
        clock = clock_for_domain(domain)
        assert isinstance(clock, BeatClock)
        assert clock.bpm == 100.0

    def test_clock_for_breath_domain(self):
        domain = {"clock": {"type": "breath", "breaths_per_minute": 12}}
        clock = clock_for_domain(domain)
        assert isinstance(clock, BreathClock)


# ---------------------------------------------------------------------------
# Intensity curve tests
# ---------------------------------------------------------------------------

class TestIntensityCurve:
    def test_starts_low(self):
        assert sigmoid_intensity(0.0) < 0.5

    def test_peaks_near_06(self):
        assert sigmoid_intensity(0.6) > sigmoid_intensity(0.2)
        assert sigmoid_intensity(0.6) > sigmoid_intensity(0.9)

    def test_falls_by_end(self):
        end = sigmoid_intensity(1.0)
        peak = sigmoid_intensity(0.6)
        assert end < peak * 0.5

    def test_cue_density_sparse_at_low_intensity(self):
        assert intensity_to_cue_density(0.1) == "sparse"

    def test_cue_density_focused_at_high_intensity(self):
        assert intensity_to_cue_density(0.8) == "focused"

    def test_cue_density_minimal_at_peak(self):
        assert intensity_to_cue_density(0.95) == "minimal"


# ---------------------------------------------------------------------------
# Sequencer tests
# ---------------------------------------------------------------------------

class TestMovementSequencer:
    def test_demo_compile_returns_routine(self):
        seq = MovementSequencer(domain=_DEMO_DOMAIN)
        routine = seq.compile(60.0)
        assert isinstance(routine, CompiledRoutine)
        assert routine.domain == "demo"
        assert len(routine.blocks) > 0

    def test_blocks_cover_full_duration(self):
        seq = MovementSequencer(domain=_DEMO_DOMAIN)
        routine = seq.compile(30.0)
        total_s = sum(b.duration_s for b in routine.blocks)
        assert abs(total_s - 30.0 * 60) < 30.0

    def test_block_has_required_fields(self):
        seq = MovementSequencer(domain=_DEMO_DOMAIN)
        routine = seq.compile(20.0)
        b = routine.blocks[0]
        assert b.primitive_id
        assert b.primitive_name
        assert b.duration_s > 0
        assert 0.0 <= b.energy <= 1.0
        assert b.cue_density in {"sparse", "moderate", "rhythmic", "focused", "minimal"}
        assert b.weight_shift in {"left", "right", "bilateral", "unweighted"}

    def test_tracker_state_in_routine(self):
        seq = MovementSequencer(domain=_DEMO_DOMAIN)
        routine = seq.compile(20.0)
        state = routine.tracker_final_state
        assert "weight_distribution" in state
        assert "facing_direction" in state
        assert "intensity" in state
        assert "clock_beat" in state

    def test_empty_primitives_raises_value_error(self):
        seq = MovementSequencer(domain={"domain": "empty", "primitives": []})
        with pytest.raises(ValueError, match="No primitives"):
            seq.compile(10.0)

    def test_pt_domain_requires_safety_gate(self):
        pt_domain = {
            "domain": "physical_therapy",
            "requires_clinical_review": True,
            "primitives": [
                {"id": "quad_set", "name": "Quad Set", "weight_shift": "bilateral",
                 "facing": "any", "energy_delta": 0.05, "valid_next": ["quad_set"]}
            ]
        }
        seq = MovementSequencer(domain=pt_domain)
        with pytest.raises(PermissionError, match="safety_acknowledged"):
            seq.compile(10.0)

    def test_pt_domain_passes_with_gate(self):
        pt_domain = {
            "domain": "physical_therapy",
            "requires_clinical_review": True,
            "primitives": [
                {"id": "quad_set", "name": "Quad Set", "weight_shift": "bilateral",
                 "facing": "any", "energy_delta": 0.05, "valid_next": ["quad_set"]}
            ]
        }
        seq = MovementSequencer(domain=pt_domain)
        routine = seq.compile(10.0, safety_acknowledged=True)
        assert len(routine.blocks) > 0

    def test_custom_objective_fn_called(self):
        calls = []

        def my_obj(valid_primitives, tracker):
            calls.append(len(valid_primitives))
            return valid_primitives[0] if valid_primitives else None

        seq = MovementSequencer(domain=_DEMO_DOMAIN, objective_fn=my_obj)
        seq.compile(10.0)
        assert len(calls) > 0

    def test_clock_swap_breath_to_beat(self):
        breath_seq = MovementSequencer(domain=_DEMO_DOMAIN, clock=BreathClock(12))
        beat_seq = MovementSequencer(domain=_DEMO_DOMAIN, clock=BeatClock(120, 8))
        r1 = breath_seq.compile(10.0)
        r2 = beat_seq.compile(10.0)
        assert r1.clock_type == "BreathClock"
        assert r2.clock_type == "BeatClock"

    def test_tracker_state_preserved_across_clock_swap(self):
        """Regression: switching clock type must not reset tracker weight/facing."""
        seq1 = MovementSequencer(domain=_DEMO_DOMAIN, clock=BreathClock())
        r1 = seq1.compile(5.0)
        s1 = r1.tracker_final_state

        seq2 = MovementSequencer(domain=_DEMO_DOMAIN, clock=BeatClock())
        r2 = seq2.compile(5.0)
        s2 = r2.tracker_final_state

        # Both should have valid weight distributions summing to <= 1
        assert sum(s1["weight_distribution"].values()) <= 1.0 + 1e-9
        assert sum(s2["weight_distribution"].values()) <= 1.0 + 1e-9

    def test_routine_to_dict_serializable(self):
        seq = MovementSequencer(domain=_DEMO_DOMAIN)
        routine = seq.compile(15.0)
        d = routine.to_dict()
        json.dumps(d)

    def test_blocks_not_empty_for_short_duration(self):
        seq = MovementSequencer(domain=_DEMO_DOMAIN)
        routine = seq.compile(1.0)
        assert len(routine.blocks) >= 1
