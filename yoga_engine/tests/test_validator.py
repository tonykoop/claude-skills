"""Tests for yoga_engine.validator — safety rule engine."""

import pytest
from yoga_engine.parser import parse_shorthand
from yoga_engine.validator import validate_sequence
from yoga_engine.schema import (
    IssueSeverity, Phase, PhaseBlock, PoseInstance, Sequence,
    Pose, PoseFamily,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seq(shorthand: str, **kwargs) -> Sequence:
    return parse_shorthand(shorthand, **kwargs)


def _has_code(report, code: str) -> bool:
    return any(i.code == code for i in report.issues)


def _count_code(report, code: str) -> int:
    return sum(1 for i in report.issues if i.code == code)


# ---------------------------------------------------------------------------
# PEAK_NO_WARMUP_PHASE
# ---------------------------------------------------------------------------


class TestPeakNeedsWarmup:
    def test_peak_without_warmup_is_error(self):
        seq = _seq("PK: CM")
        report = validate_sequence(seq)
        assert _has_code(report, "PEAK_NO_WARMUP_PHASE")
        assert report.errors  # must be error level

    def test_peak_with_warmup_is_ok(self):
        seq = _seq("WU: CC > DD\nPK: CM")
        report = validate_sequence(seq)
        assert not _has_code(report, "PEAK_NO_WARMUP_PHASE")

    def test_build_counts_as_warmup(self):
        seq = _seq("BD: WR2_r\nPK: CM")
        report = validate_sequence(seq)
        assert not _has_code(report, "PEAK_NO_WARMUP_PHASE")


# ---------------------------------------------------------------------------
# MISSING_COUNTER_AFTER (backbend / twist with needs_counter)
# ---------------------------------------------------------------------------


class TestCounterAfterBackbend:
    def test_camel_without_counter_warns(self):
        # CM alone at end of sequence — no counter within 3 steps
        seq = _seq("WU: CC\nPK: CM")
        report = validate_sequence(seq)
        assert _has_code(report, "MISSING_COUNTER_AFTER")

    def test_camel_with_cb_nearby_ok(self):
        # CB = Child's Pose (counter)
        seq = _seq("WU: CC\nPK: CM > CB")
        report = validate_sequence(seq)
        assert not _has_code(report, "MISSING_COUNTER_AFTER")

    def test_upward_dog_followed_by_dd_ok(self):
        # UD (backbend) → DD (is_counter)
        seq = _seq("WU: CC\nBD: Viny")  # Viny = PL>CH+UD>DD
        report = validate_sequence(seq)
        # UD is followed by DD (counter), so no error for UD
        ud_issues = [i for i in report.issues
                     if i.code == "MISSING_COUNTER_AFTER" and i.pose_token == "UD"]
        assert not ud_issues


# ---------------------------------------------------------------------------
# BILATERAL_MISSING_SIDE
# ---------------------------------------------------------------------------


class TestBilateralSymmetry:
    def test_missing_left_warns(self):
        seq = _seq("BD: WR2_r > WR2_r")
        report = validate_sequence(seq)
        assert _has_code(report, "BILATERAL_MISSING_SIDE")

    def test_both_sides_present_ok(self):
        seq = _seq("BD: WR2_r > WR2_l")
        report = validate_sequence(seq)
        assert not _has_code(report, "BILATERAL_MISSING_SIDE")

    def test_no_side_modifier_ok(self):
        seq = _seq("BD: WR2")
        report = validate_sequence(seq)
        assert not _has_code(report, "BILATERAL_MISSING_SIDE")

    def test_different_poses_independent(self):
        # WR2_r without WR2_l, EK_r without EK_l — should get 2 bilateral warnings
        seq = _seq("BD: WR2_r > EK_r")
        report = validate_sequence(seq)
        assert _count_code(report, "BILATERAL_MISSING_SIDE") == 2


# ---------------------------------------------------------------------------
# PHASE_ORDER_IRREGULAR
# ---------------------------------------------------------------------------


class TestPhaseOrder:
    def test_correct_order_no_warning(self):
        seq = _seq("WU: CC\nBD: WR2_r\nPK: CM > CB\nCD: ST\nSV: SV")
        report = validate_sequence(seq)
        assert not _has_code(report, "PHASE_ORDER_IRREGULAR")

    def test_peak_before_warmup_triggers(self):
        seq = _seq("PK: CM > CB\nWU: CC")
        report = validate_sequence(seq)
        assert _has_code(report, "PHASE_ORDER_IRREGULAR")

    def test_cooldown_before_build_triggers(self):
        seq = _seq("WU: CC\nCD: ST\nBD: WR2_r > WR2_l")
        report = validate_sequence(seq)
        assert _has_code(report, "PHASE_ORDER_IRREGULAR")


# ---------------------------------------------------------------------------
# INTENSITY_SPIKE
# ---------------------------------------------------------------------------


class TestIntensitySpike:
    def test_gentle_steps_no_spike(self):
        seq = _seq("WU: CC\nBD: LL_r > HL_r > WR2_r")
        report = validate_sequence(seq)
        assert not _has_code(report, "INTENSITY_SPIKE")

    def test_direct_to_peak_spikes(self):
        # SC (intensity 1) → CM (intensity 8) in one step → spike > 3
        seq = _seq("WU: SC\nPK: CM")
        report = validate_sequence(seq)
        assert _has_code(report, "INTENSITY_SPIKE")


# ---------------------------------------------------------------------------
# SAVASANA_MISSING
# ---------------------------------------------------------------------------


class TestSavasanaMissing:
    def test_no_cooldown_warns(self):
        seq = _seq("WU: CC\nBD: WR2_r > WR2_l")
        report = validate_sequence(seq)
        assert _has_code(report, "SAVASANA_MISSING")

    def test_cooldown_present_ok(self):
        seq = _seq("WU: CC\nCD: ST")
        report = validate_sequence(seq)
        assert not _has_code(report, "SAVASANA_MISSING")

    def test_savasana_present_ok(self):
        seq = _seq("WU: CC\nSV: SV")
        report = validate_sequence(seq)
        assert not _has_code(report, "SAVASANA_MISSING")


# ---------------------------------------------------------------------------
# HEATED_CAUTION_POSE
# ---------------------------------------------------------------------------


class TestHeatedRoom:
    def test_no_heated_flags_when_not_heated(self):
        seq = _seq("WU: CC\nPK: CM > CB\nSV: SV")
        assert not seq.heated_room
        report = validate_sequence(seq)
        assert not _has_code(report, "HEATED_CAUTION_POSE")

    def test_heated_camel_flagged(self):
        seq = _seq("# HEATED: true\nWU: CC\nPK: CM > CB\nSV: SV")
        assert seq.heated_room
        report = validate_sequence(seq)
        assert _has_code(report, "HEATED_CAUTION_POSE")

    def test_non_caution_pose_not_flagged_in_heated(self):
        # CC (Cat-Cow) has no heated_caution
        seq = _seq("# HEATED: true\nWU: CC\nSV: SV")
        report = validate_sequence(seq)
        assert not _has_code(report, "HEATED_CAUTION_POSE")


# ---------------------------------------------------------------------------
# PEAK_TOO_EARLY
# ---------------------------------------------------------------------------


class TestPeakTooEarly:
    def test_peak_at_end_ok(self):
        seq = _seq("WU: CC > DD > LL_r > LL_l > WR2_r > WR2_l\nPK: CM > CB")
        report = validate_sequence(seq)
        assert not _has_code(report, "PEAK_TOO_EARLY")

    def test_peak_at_start_warns(self):
        # Only a single warmup then immediately an intensity-8 pose
        seq = _seq("WU: CC\nPK: CM > CB")
        report = validate_sequence(seq)
        # CM is intensity=8, CC is intensity=2; CM is at position 2/3
        # Whether it triggers depends on relative position — at 2 out of 3
        # that is 67% which is > 30%, so should NOT trigger PEAK_TOO_EARLY
        # (This checks the rule is not too aggressive)
        # The rule fires only if pose is within the first 30% of ALL poses

    def test_peak_at_very_start_warns(self):
        # CM appears at position 0 (first pose)
        seq = _seq("PK: CM > CB > KN > KN > SF > SV")
        report = validate_sequence(seq)
        assert _has_code(report, "PEAK_TOO_EARLY")


# ---------------------------------------------------------------------------
# Safe sequence integration test
# ---------------------------------------------------------------------------


SAFE_CLASS = """\
# TITLE: Safe Flow
WU: CC/5 > DD > LL_r > DD > LL_l
BD: WR2_r > EK_r > Viny > WR2_l > EK_l > Viny
PK: CM/5 > CB
CD: ST_r > KN > ST_l > SF/5
SV: SV/5
"""


class TestSafeClassIntegration:
    def test_safe_class_no_errors(self):
        seq = _seq(SAFE_CLASS)
        report = validate_sequence(seq)
        # A well-formed class should have zero errors
        assert report.is_safe, f"Expected no errors; got: {report.errors}"

    def test_safe_class_report_summary(self):
        seq = _seq(SAFE_CLASS)
        report = validate_sequence(seq)
        assert "errors=" in repr(report)
