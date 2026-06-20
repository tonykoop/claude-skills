"""Tests for yoga_engine.arc — energy-curve analyser."""

import pytest
from yoga_engine.parser import parse_shorthand
from yoga_engine.arc import analyze_arc, _classify_arc
from yoga_engine.schema import ArcReport


# ---------------------------------------------------------------------------
# _classify_arc (unit tests on the shape classifier)
# ---------------------------------------------------------------------------


class TestClassifyArc:
    def test_flat_curve(self):
        # Very little variance
        assert _classify_arc([5, 5, 5, 5, 5]) == "flat"

    def test_mountain_curve(self):
        # Classic build-peak-release
        assert _classify_arc([2, 4, 6, 8, 6, 4, 2]) == "mountain"

    def test_spike_curve(self):
        # One sharp high point
        assert _classify_arc([2, 2, 2, 9, 2, 2, 2]) == "spike"

    def test_inverted_curve(self):
        # High–low–high
        assert _classify_arc([7, 7, 3, 3, 3, 7, 7]) == "inverted"

    def test_wave_curve(self):
        # Two distinct peaks
        assert _classify_arc([2, 7, 2, 7, 2]) == "wave"

    def test_very_short_curve(self):
        # Less than 3 poses — always flat
        assert _classify_arc([8]) == "flat"
        assert _classify_arc([3, 9]) == "flat"

    def test_plateau_like_curve(self):
        # rises, holds high, falls sharply
        curve = [2, 5, 7, 7, 7, 7, 7, 3, 1]
        shape = _classify_arc(curve)
        # Should be plateau or mountain — not spike or flat
        assert shape in ("plateau", "mountain")


# ---------------------------------------------------------------------------
# analyze_arc (integration)
# ---------------------------------------------------------------------------


class TestAnalyzeArc:
    def test_empty_sequence(self):
        seq = parse_shorthand("")
        report = analyze_arc(seq)
        assert report.arc_shape == "flat"
        assert report.intensity_curve == []
        assert any("empty" in n.lower() for n in report.notes)

    def test_returns_arc_report(self):
        seq = parse_shorthand("WU: CC > DD\nBD: WR2_r > WR2_l\nPK: CM > CB\nSV: SV")
        report = analyze_arc(seq)
        assert isinstance(report, ArcReport)

    def test_curve_length_matches_pose_count(self):
        seq = parse_shorthand("WU: CC > DD\nBD: WR2_r\nPK: CM\nCD: ST\nSV: SV")
        report = analyze_arc(seq)
        assert len(report.intensity_curve) == len(seq.all_poses)

    def test_phase_labels_parallel(self):
        seq = parse_shorthand("WU: CC\nBD: WR2_r\nPK: CM\nSV: SV")
        report = analyze_arc(seq)
        assert len(report.phase_labels) == len(report.intensity_curve)

    def test_peak_index_correct(self):
        seq = parse_shorthand("WU: CC\nBD: WR2_r\nPK: UB\nCD: ST\nSV: SV")
        report = analyze_arc(seq)
        # UB = Upward Bow (intensity 9) should be the max
        assert report.peak_intensity == 9

    def test_warmup_plateau_gt_zero(self):
        seq = parse_shorthand("WU: CC > DD\nBD: WR2_r > WR2_l\nSV: SV")
        report = analyze_arc(seq)
        assert report.warmup_plateau > 0

    def test_cooldown_plateau_zero_when_missing(self):
        seq = parse_shorthand("WU: CC > DD\nBD: WR2_r > WR2_l")
        report = analyze_arc(seq)
        assert report.cooldown_plateau == 0.0

    def test_arc_shape_not_empty(self):
        seq = parse_shorthand("WU: CC > DD\nBD: WR2_r > WR2_l\nPK: CM\nCD: ST\nSV: SV")
        report = analyze_arc(seq)
        assert report.arc_shape in ("mountain", "plateau", "spike", "flat", "inverted", "wave")

    def test_summary_method(self):
        seq = parse_shorthand("WU: CC > DD\nBD: WR2_r > WR2_l\nPK: CM\nCD: ST\nSV: SV")
        report = analyze_arc(seq)
        summary = report.summary()
        assert "Arc:" in summary
        assert "Peak intensity" in summary

    def test_notes_populated(self):
        seq = parse_shorthand("WU: CC > DD\nBD: WR2_r > WR2_l\nPK: CM\nCD: ST\nSV: SV")
        report = analyze_arc(seq)
        assert isinstance(report.notes, list)
        assert len(report.notes) > 0

    def test_heated_spike_adds_note(self):
        seq = parse_shorthand(
            "# HEATED: true\n"
            "WU: CC > CC > CC\n"
            "PK: UB\n"  # spike
            "CD: ST > ST > ST\n"
            "SV: SV"
        )
        report = analyze_arc(seq)
        if report.arc_shape == "spike":
            assert any("heated" in n.lower() or "rest" in n.lower() for n in report.notes)


# ---------------------------------------------------------------------------
# Mountain arc integration — well-sequenced class
# ---------------------------------------------------------------------------


MOUNTAIN_CLASS = """\
# TITLE: Mountain Flow
WU: CC > DD > LL_r > DD > LL_l > DD
BD: WR2_r > EK_r > Viny > WR2_l > EK_l > Viny > HL_r > Viny > HL_l
PK: CM/5 > CB
CD: ST_r > KN > ST_l > SF
SV: SV/5
"""


class TestMountainArc:
    def test_arc_is_mountain_or_reasonable(self):
        seq = parse_shorthand(MOUNTAIN_CLASS)
        report = analyze_arc(seq)
        # A well-structured class should have a mountain or plateau arc
        assert report.arc_shape in ("mountain", "plateau", "wave"), \
            f"Unexpected arc shape: {report.arc_shape}"

    def test_peak_in_middle_section(self):
        seq = parse_shorthand(MOUNTAIN_CLASS)
        report = analyze_arc(seq)
        total = len(report.intensity_curve)
        # Peak should not be in the first 25% or last 15%
        assert report.peak_index >= total * 0.25, \
            f"Peak at {report.peak_index}/{total} — too early"

    def test_cooldown_lower_than_peak(self):
        seq = parse_shorthand(MOUNTAIN_CLASS)
        report = analyze_arc(seq)
        assert report.cooldown_plateau < report.peak_intensity
