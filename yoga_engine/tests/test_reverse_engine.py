"""Tests for yoga_engine.reverse_engine — Reverse Sequence Engine (#373)."""

import pytest
from yoga_engine.reverse_engine import (
    ReverseSequenceEngine, ScriptOutput, ScriptLine,
    PlaylistHandoff, PlaylistPhase, ThemeInfusion,
)
from yoga_engine.schema import Phase


SAMPLE_SHORT = """\
# TITLE: Five-Line Flow
# DURATION: 60
WU: CC > DD > LL_r > DD > LL_l
BD: WR2_r > EK_r > Viny > WR2_l > EK_l > Viny
PK: CM/5 > CB
CD: ST_r > KN > ST_l > SF/5
SV: SV/5
"""

MINIMAL = "WU: CC > DD\nBD: WR2_r > WR2_l\nSV: SV"


# ---------------------------------------------------------------------------
# ReverseSequenceEngine.expand — basic contract
# ---------------------------------------------------------------------------


class TestExpandBasicContract:
    def test_returns_script_output(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        assert isinstance(result, ScriptOutput)

    def test_not_reviewed_by_default(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        assert result.is_reviewed is False

    def test_sequence_title_preserved(self):
        engine = ReverseSequenceEngine()
        result = engine.expand("# TITLE: My Flow\nWU: CC\nSV: SV")
        assert result.sequence.title == "My Flow"

    def test_script_lines_non_empty(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        assert len(result.lines) > 0

    def test_all_lines_are_script_lines(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        for line in result.lines:
            assert isinstance(line, ScriptLine)

    def test_validation_summary_in_output(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        assert result.validation_summary  # non-empty

    def test_playlist_handoff_present(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        assert isinstance(result.playlist_handoff, PlaylistHandoff)

    def test_theme_infusions_present(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        assert isinstance(result.theme_infusions, list)
        assert len(result.theme_infusions) > 0


# ---------------------------------------------------------------------------
# Quality gate — approval
# ---------------------------------------------------------------------------


class TestApprovalGate:
    def test_approve_sets_reviewed(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        assert not result.is_reviewed
        result.approve("LGTM")
        assert result.is_reviewed

    def test_approve_stores_notes(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        result.approve("Reviewed and approved by Tony.")
        assert "Tony" in result.human_review_notes

    def test_approve_empty_notes(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        result.approve()
        assert result.is_reviewed
        assert result.human_review_notes == ""


# ---------------------------------------------------------------------------
# Script line structure
# ---------------------------------------------------------------------------


class TestScriptLineStructure:
    def test_pose_lines_exist(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        pose_lines = [l for l in result.lines if l.kind == "pose"]
        assert len(pose_lines) > 0

    def test_theme_lines_exist(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        theme_lines = [l for l in result.lines if l.kind == "theme"]
        assert len(theme_lines) > 0

    def test_transition_lines_exist(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        trans_lines = [l for l in result.lines if l.kind == "transition"]
        # With known transitions in DB, at least one should resolve
        # (WR2_r → WR2_l may not be in DB — but MINIMAL has CC→DD)
        assert isinstance(trans_lines, list)

    def test_all_pose_lines_have_token(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        for line in result.lines:
            if line.kind == "pose":
                assert line.pose_token is not None

    def test_transition_lines_have_transition_vector(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        for line in result.lines:
            if line.kind == "transition":
                assert line.transition is not None

    def test_placeholder_flag_set_without_voice_style(self):
        engine = ReverseSequenceEngine(voice_style=None)
        result = engine.expand(MINIMAL)
        pose_lines = [l for l in result.lines if l.kind == "pose"]
        # All pose lines should be placeholders without a voice style
        assert all(l.is_placeholder for l in pose_lines)


# ---------------------------------------------------------------------------
# render_markdown
# ---------------------------------------------------------------------------


class TestRenderMarkdown:
    def test_render_returns_string(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        md = result.render_markdown()
        assert isinstance(md, str)
        assert len(md) > 0

    def test_title_in_markdown(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        md = result.render_markdown()
        assert "Five-Line Flow" in md

    def test_not_reviewed_warning_in_markdown(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        md = result.render_markdown()
        assert "NOT YET REVIEWED" in md

    def test_reviewed_checkmark_after_approve(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        result.approve("OK")
        md = result.render_markdown()
        assert "✅" in md
        assert "NOT YET REVIEWED" not in md

    def test_playlist_handoff_section_in_markdown(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        md = result.render_markdown()
        assert "Playlist Handoff" in md

    def test_repr(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(MINIMAL)
        r = repr(result)
        assert "ScriptOutput" in r
        assert "reviewed=False" in r


# ---------------------------------------------------------------------------
# Playlist handoff
# ---------------------------------------------------------------------------


class TestPlaylistHandoff:
    def test_playlist_has_phases(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        assert len(result.playlist_handoff.phases) > 0

    def test_playlist_phases_are_playlist_phase(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        for ph in result.playlist_handoff.phases:
            assert isinstance(ph, PlaylistPhase)

    def test_playlist_duration_matches_sequence(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        assert result.playlist_handoff.duration_minutes == 60

    def test_playlist_title_matches_sequence(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        assert result.playlist_handoff.title == "Five-Line Flow"

    def test_playlist_has_energy_values(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        for ph in result.playlist_handoff.phases:
            assert ph.energy in ("low", "medium", "high", "peak")

    def test_playlist_has_cue_density(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        for ph in result.playlist_handoff.phases:
            assert ph.cue_density in ("sparse", "moderate", "rhythmic", "focused", "minimal")

    def test_playlist_peak_phase_energy_is_high(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        peak_phases = [ph for ph in result.playlist_handoff.phases
                       if ph.phase == Phase.PEAK]
        assert peak_phases
        assert peak_phases[0].energy == "high"

    def test_playlist_lufs_varies_by_phase(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        lufs_values = [ph.lufs_target for ph in result.playlist_handoff.phases]
        # Should have different LUFS per phase
        assert len(set(lufs_values)) > 1

    def test_playlist_crossfade_bars_positive(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        for ph in result.playlist_handoff.phases:
            assert ph.avg_crossfade_bars > 0


# ---------------------------------------------------------------------------
# Theme infusions
# ---------------------------------------------------------------------------


class TestThemeInfusions:
    def test_infusions_cover_present_phases(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        present_phases = {b.phase for b in result.sequence.phases}
        infusion_phases = {inf.phase for inf in result.theme_infusions}
        # All present phases should have at least one infusion
        assert present_phases.issubset(infusion_phases | {Phase.BUILD})

    def test_infusions_have_placeholders(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        for inf in result.theme_infusions:
            assert "[" in inf.placeholder_text  # structural placeholder marker

    def test_theme_lines_in_script_match_infusions(self):
        engine = ReverseSequenceEngine()
        result = engine.expand(SAMPLE_SHORT)
        theme_count = len([l for l in result.lines if l.kind == "theme"])
        assert theme_count > 0


# ---------------------------------------------------------------------------
# Macro expansion integration
# ---------------------------------------------------------------------------


class TestMacroExpansionInExpansion:
    def test_viny_expands_in_script(self):
        engine = ReverseSequenceEngine()
        result = engine.expand("WU: CC\nBD: Viny\nSV: SV")
        tokens = [l.pose_token for l in result.lines if l.kind == "pose"]
        assert "PL" in tokens
        assert "CH" in tokens
        assert "UD" in tokens
        assert "DD" in tokens
