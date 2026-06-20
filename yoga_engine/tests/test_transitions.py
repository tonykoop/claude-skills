"""Tests for yoga_engine.transitions — Transition Matrix (#370)."""

import pytest
from yoga_engine.transitions import (
    TransitionVector, Pathway, Pacing,
    TRANSITION_DB,
    get_transitions, get_exits, get_entries,
    suggest_transition, annotate_sequence_transitions,
)
from yoga_engine.schema import BreathOp


# ---------------------------------------------------------------------------
# Pacing
# ---------------------------------------------------------------------------


class TestPacing:
    def test_crossfade_bars_slow(self):
        assert Pacing.SLOW.crossfade_bars == 2.0

    def test_crossfade_bars_medium(self):
        assert Pacing.MEDIUM.crossfade_bars == 1.0

    def test_crossfade_bars_fast(self):
        assert Pacing.FAST.crossfade_bars == 0.5


# ---------------------------------------------------------------------------
# TransitionVector
# ---------------------------------------------------------------------------


class TestTransitionVector:
    def _make(self) -> TransitionVector:
        return TransitionVector(
            origin="DD", pathway=Pathway.STEP_FORWARD, target="CL",
            breath_op=BreathOp.INHALE, pacing=Pacing.MEDIUM,
            cue_template="Step your {side} foot forward, {breath} up — {target}.",
        )

    def test_key(self):
        tv = self._make()
        assert tv.key == ("DD", "CL")

    def test_repr(self):
        tv = self._make()
        assert "DD" in repr(tv)
        assert "CL" in repr(tv)

    def test_render_cue_with_side(self):
        tv = self._make()
        rendered = tv.render_cue(side="right", breath="inhale")
        assert "right" in rendered
        assert "CL" in rendered

    def test_render_cue_defaults_breath_op(self):
        tv = self._make()
        rendered = tv.render_cue(side="left")
        assert "inhale" in rendered

    def test_transcript_cue_defaults_none(self):
        tv = self._make()
        assert tv.transcript_cue is None

    def test_transcript_cue_settable(self):
        tv = self._make()
        tv.transcript_cue = "Step your right foot forward…"
        assert tv.transcript_cue is not None


# ---------------------------------------------------------------------------
# TRANSITION_DB population
# ---------------------------------------------------------------------------


class TestTransitionDB:
    def test_db_non_empty(self):
        assert len(TRANSITION_DB) > 0

    def test_all_transitions_have_valid_breath_op(self):
        for vectors in TRANSITION_DB.values():
            for v in vectors:
                assert isinstance(v.breath_op, BreathOp)

    def test_all_transitions_have_valid_pacing(self):
        for vectors in TRANSITION_DB.values():
            for v in vectors:
                assert isinstance(v.pacing, Pacing)

    def test_all_transitions_have_valid_pathway(self):
        for vectors in TRANSITION_DB.values():
            for v in vectors:
                assert isinstance(v.pathway, Pathway)

    def test_all_cue_templates_are_strings(self):
        for vectors in TRANSITION_DB.values():
            for v in vectors:
                assert isinstance(v.cue_template, str)


# ---------------------------------------------------------------------------
# Crescent Lunge acceptance: multiple entry pathways (#370 requirement)
# ---------------------------------------------------------------------------


class TestCrescentLungeMultiEntry:
    def test_crescent_has_multiple_entries(self):
        entries = get_entries("CL")
        assert len(entries) >= 4, (
            f"Expected ≥ 4 entry pathways into Crescent Lunge (CL), got {len(entries)}"
        )

    def test_crescent_entries_from_dd(self):
        from_dd = [e for e in get_entries("CL") if e.origin == "DD"]
        assert from_dd, "Crescent Lunge should be reachable from Downward Dog"

    def test_crescent_entries_from_ll(self):
        from_ll = [e for e in get_entries("CL") if e.origin == "LL"]
        assert from_ll, "Crescent Lunge should be reachable from Low Lunge"

    def test_crescent_entries_from_wr1(self):
        from_wr1 = [e for e in get_entries("CL") if e.origin == "WR1"]
        assert from_wr1, "Crescent Lunge should be reachable from Warrior I"

    def test_crescent_entries_from_wr3(self):
        from_wr3 = [e for e in get_entries("CL") if e.origin == "WR3"]
        assert from_wr3, "Crescent Lunge should be reachable from Warrior III"

    def test_crescent_entries_have_distinct_origins(self):
        entries = get_entries("CL")
        origins = {e.origin for e in entries}
        # The four required entry origins should all be present
        required = {"DD", "LL", "WR1", "WR3"}
        assert required.issubset(origins), \
            f"Missing CL entry origins: {required - origins}"


# ---------------------------------------------------------------------------
# get_transitions
# ---------------------------------------------------------------------------


class TestGetTransitions:
    def test_known_pair_returns_list(self):
        result = get_transitions("DD", "FF")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_unknown_pair_returns_empty(self):
        result = get_transitions("SV", "CM")
        assert result == []

    def test_all_returned_have_correct_origin_target(self):
        result = get_transitions("PL", "CH")
        for v in result:
            assert v.origin == "PL"
            assert v.target == "CH"


# ---------------------------------------------------------------------------
# get_exits
# ---------------------------------------------------------------------------


class TestGetExits:
    def test_dd_has_exits(self):
        exits = get_exits("DD")
        assert len(exits) > 0

    def test_all_exits_have_correct_origin(self):
        exits = get_exits("DD")
        assert all(v.origin == "DD" for v in exits)

    def test_unknown_pose_returns_empty(self):
        assert get_exits("UNKNOWN_POSE") == []


# ---------------------------------------------------------------------------
# get_entries
# ---------------------------------------------------------------------------


class TestGetEntries:
    def test_ff_has_entries(self):
        entries = get_entries("FF")
        assert len(entries) > 0

    def test_all_entries_have_correct_target(self):
        entries = get_entries("DD")
        assert all(v.target == "DD" for v in entries)


# ---------------------------------------------------------------------------
# suggest_transition
# ---------------------------------------------------------------------------


class TestSuggestTransition:
    def test_returns_transition_for_known_pair(self):
        tv = suggest_transition("DD", "FF")
        assert tv is not None
        assert tv.origin == "DD"
        assert tv.target == "FF"

    def test_returns_none_for_unknown_pair(self):
        tv = suggest_transition("SV", "CM")
        assert tv is None

    def test_preferred_pacing_respected(self):
        # DD -> CL has medium pacing; request medium
        tv = suggest_transition("DD", "CL", preferred_pacing=Pacing.MEDIUM)
        assert tv is not None
        assert tv.pacing == Pacing.MEDIUM

    def test_preferred_pacing_fallback_when_not_available(self):
        # If preferred pacing not in DB, return first entry rather than None
        tv = suggest_transition("DD", "FF", preferred_pacing=Pacing.FAST)
        assert tv is not None  # should not return None


# ---------------------------------------------------------------------------
# annotate_sequence_transitions
# ---------------------------------------------------------------------------


class TestAnnotateSequenceTransitions:
    def test_first_element_has_no_transition(self):
        tokens = [("DD", None), ("FF", None)]
        result = annotate_sequence_transitions(tokens)
        assert result[0][1] is None

    def test_subsequent_elements_have_transition_or_none(self):
        tokens = [("DD", "r"), ("CL", "r"), ("SV", None)]
        result = annotate_sequence_transitions(tokens)
        assert len(result) == 3
        # Second element (CL) should have a transition from DD
        assert result[1][1] is not None
        assert result[1][1].origin == "DD"
        assert result[1][1].target == "CL"

    def test_unknown_transition_returns_none(self):
        tokens = [("SV", None), ("CM", None)]
        result = annotate_sequence_transitions(tokens)
        assert result[1][1] is None

    def test_returns_same_length(self):
        tokens = [("DD", None), ("FF", None), ("PL", None), ("CH", None)]
        result = annotate_sequence_transitions(tokens)
        assert len(result) == len(tokens)

    def test_empty_sequence(self):
        assert annotate_sequence_transitions([]) == []

    def test_single_pose(self):
        result = annotate_sequence_transitions([("DD", None)])
        assert len(result) == 1
        assert result[0][1] is None


# ---------------------------------------------------------------------------
# Pacing ↔ crossfade integration
# ---------------------------------------------------------------------------


class TestCrossfadeHandoff:
    """Verify that pacing maps to crossfade data used by the playlist layer."""

    def test_vinyasa_transitions_are_fast(self):
        # CH → UD is a vinyasa breath (fast)
        tv = suggest_transition("CH", "UD")
        assert tv is not None
        assert tv.pacing == Pacing.FAST
        assert tv.pacing.crossfade_bars == 0.5

    def test_pigeon_entry_is_slow(self):
        # DD → Pigeon is a contemplative, slow transition
        tv = suggest_transition("DD", "PT")
        assert tv is not None
        assert tv.pacing == Pacing.SLOW
        assert tv.pacing.crossfade_bars == 2.0

    def test_camel_exit_is_slow(self):
        tv = suggest_transition("CM", "CB")
        assert tv is not None
        assert tv.pacing == Pacing.SLOW
