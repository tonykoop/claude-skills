"""Tests for yoga_engine.parser — shorthand parsing."""

import pytest
from yoga_engine.parser import parse_shorthand, expand_macros, ParseError
from yoga_engine.schema import Phase, BreathOp


# ---------------------------------------------------------------------------
# expand_macros
# ---------------------------------------------------------------------------


class TestExpandMacros:
    def test_no_macros(self):
        text = "DD > FF"
        assert expand_macros(text, {}) == text

    def test_single_macro(self):
        result = expand_macros("WU: Viny", {"Viny": "PL>CH+UD>DD"})
        assert "PL>CH+UD>DD" in result
        assert "Viny" not in result

    def test_macro_at_start_of_chain(self):
        result = expand_macros("BD: Viny > WR2_r", {"Viny": "PL>CH+UD>DD"})
        assert result.startswith("BD: PL>CH+UD>DD")

    def test_macro_not_partial_match(self):
        # "VinyK" should not be expanded by "Viny" macro
        result = expand_macros("BD: VinyK > DD", {"Viny": "PL>CH+UD>DD",
                                                   "VinyK": "PL>CB2+DD"})
        assert "PL>CB2+DD" in result
        # Original Viny expansion should NOT replace the K variant
        assert "PL>CH+UD>DD" not in result

    def test_multiple_macro_expansions(self):
        result = expand_macros("BD: Viny > WR2 > Viny", {"Viny": "PL>CH+UD>DD"})
        assert result.count("PL>CH+UD>DD") == 2

    def test_default_macros_expand_viny(self):
        result = expand_macros("BD: Viny")
        assert "PL" in result
        assert "CH" in result
        assert "DD" in result


# ---------------------------------------------------------------------------
# parse_shorthand — meta directives
# ---------------------------------------------------------------------------


class TestParseShorthandMeta:
    def test_default_title(self):
        seq = parse_shorthand("WU: CC > DD")
        assert seq.title == "Untitled Class"

    def test_custom_title(self):
        seq = parse_shorthand("# TITLE: Sunday Flow\nWU: CC > DD")
        assert seq.title == "Sunday Flow"

    def test_duration(self):
        seq = parse_shorthand("# DURATION: 75\nWU: CC > DD")
        assert seq.duration_minutes == 75

    def test_heated_true(self):
        seq = parse_shorthand("# HEATED: true\nWU: DD")
        assert seq.heated_room is True

    def test_heated_false(self):
        seq = parse_shorthand("# HEATED: false\nWU: DD")
        assert seq.heated_room is False

    def test_heated_yes(self):
        seq = parse_shorthand("# HEATED: yes\nWU: DD")
        assert seq.heated_room is True

    def test_level(self):
        seq = parse_shorthand("# LEVEL: intermediate\nWU: DD")
        assert seq.level == "intermediate"

    def test_theme(self):
        seq = parse_shorthand("# THEME: hip openers\nWU: DD")
        assert seq.theme == "hip openers"

    def test_duration_invalid(self):
        with pytest.raises(ParseError, match="DURATION"):
            parse_shorthand("# DURATION: sixty\nWU: DD")

    def test_unknown_meta_ignored(self):
        # Should not raise
        seq = parse_shorthand("# FUTURE_KEY: something\nWU: DD")
        assert seq.title == "Untitled Class"


# ---------------------------------------------------------------------------
# parse_shorthand — phase parsing
# ---------------------------------------------------------------------------


class TestParseShorthandPhases:
    def test_single_phase_single_pose(self):
        seq = parse_shorthand("WU: DD")
        assert len(seq.phases) == 1
        assert seq.phases[0].phase == Phase.WARMUP
        assert seq.phases[0].poses[0].pose.token == "DD"

    def test_phase_label_mapping_ar(self):
        seq = parse_shorthand("AR: SC")
        assert seq.phases[0].phase == Phase.ARRIVAL

    def test_phase_label_mapping_pk(self):
        seq = parse_shorthand("WU: CC\nPK: CM")
        pk = next(b for b in seq.phases if b.phase == Phase.PEAK)
        assert pk is not None

    def test_phase_label_mapping_sv(self):
        seq = parse_shorthand("SV: SV")
        assert seq.phases[0].phase == Phase.SAVASANA

    def test_multiple_phases(self):
        text = "WU: CC\nBD: WR2_r\nPK: CM\nCD: PT_r\nSV: SV"
        seq = parse_shorthand(text)
        assert len(seq.phases) == 5

    def test_pose_chain_exhale_op(self):
        seq = parse_shorthand("WU: DD > FF")
        poses = seq.phases[0].poses
        assert poses[0].entry_op is None
        assert poses[1].entry_op == BreathOp.EXHALE

    def test_pose_chain_inhale_op(self):
        seq = parse_shorthand("WU: DD + FF")
        poses = seq.phases[0].poses
        assert poses[1].entry_op == BreathOp.INHALE

    def test_pose_chain_hold_op(self):
        seq = parse_shorthand("WU: DD // FF")
        poses = seq.phases[0].poses
        assert poses[1].entry_op == BreathOp.HOLD

    def test_side_modifier_right(self):
        seq = parse_shorthand("BD: WR2_r")
        assert seq.phases[0].poses[0].side == "r"

    def test_side_modifier_left(self):
        seq = parse_shorthand("BD: WR2_l")
        assert seq.phases[0].poses[0].side == "l"

    def test_side_modifier_open(self):
        seq = parse_shorthand("BD: WR2_open")
        assert seq.phases[0].poses[0].side == "open"

    def test_breath_count(self):
        seq = parse_shorthand("CD: PT_r/10")
        inst = seq.phases[0].poses[0]
        assert inst.breath_count == 10
        assert inst.side == "r"

    def test_breath_count_no_side(self):
        seq = parse_shorthand("CD: SV/5")
        assert seq.phases[0].poses[0].breath_count == 5

    def test_empty_phase_is_valid(self):
        seq = parse_shorthand("WU:")
        assert seq.phases[0].phase == Phase.WARMUP
        assert seq.phases[0].poses == []

    def test_blank_lines_skipped(self):
        text = "\nWU: DD\n\nBD: WR2_r\n"
        seq = parse_shorthand(text)
        assert len(seq.phases) == 2

    def test_comment_lines_skipped(self):
        text = "# a comment\nWU: DD"
        seq = parse_shorthand(text)
        assert len(seq.phases) == 1

    def test_unknown_token_raises(self):
        # Token too long for the grammar regex → "Cannot parse token spec"
        with pytest.raises(ParseError, match="Cannot parse token spec|Unknown pose token"):
            parse_shorthand("WU: ZZZUNKNOWN")

    def test_malformed_line_raises(self):
        with pytest.raises(ParseError, match="expected"):
            parse_shorthand("this is not a valid line")


# ---------------------------------------------------------------------------
# parse_shorthand — macro expansion integration
# ---------------------------------------------------------------------------


class TestParseShorthandMacros:
    def test_viny_macro_expands(self):
        seq = parse_shorthand("BD: Viny")
        # Viny = PL>CH+UD>DD  → 4 poses
        poses = seq.phases[0].poses
        tokens = [p.pose.token for p in poses]
        assert tokens == ["PL", "CH", "UD", "DD"]

    def test_viny_macro_operators(self):
        seq = parse_shorthand("BD: Viny")
        ops = [p.entry_op for p in seq.phases[0].poses]
        # PL (None), CH (exhale '>'), UD (inhale '+'), DD (exhale '>')
        assert ops[0] is None
        assert ops[1] == BreathOp.EXHALE
        assert ops[2] == BreathOp.INHALE
        assert ops[3] == BreathOp.EXHALE

    def test_macro_with_surrounding_poses(self):
        seq = parse_shorthand("BD: HL_r > Viny > HL_l")
        tokens = [p.pose.token for p in seq.phases[0].poses]
        # HL, PL, CH, UD, DD, HL
        assert tokens[0] == "HL"
        assert tokens[-1] == "HL"
        assert "DD" in tokens

    def test_custom_macros_override(self):
        custom = {"XX": "DD > FF"}
        seq = parse_shorthand("WU: XX", macros=custom)
        tokens = [p.pose.token for p in seq.phases[0].poses]
        assert tokens == ["DD", "FF"]

    def test_disable_macros(self):
        # If Viny were a pose token it would work; since it's not, should raise
        with pytest.raises(ParseError):
            parse_shorthand("BD: Viny", macros={})


# ---------------------------------------------------------------------------
# parse_shorthand — full class example
# ---------------------------------------------------------------------------


SAMPLE_CLASS = """\
# TITLE: Hip-Opening Flow
# DURATION: 60
# LEVEL: mixed
AR: SC/3 > BW/3
WU: CC/5 > TB > DD > LL_r > DD > LL_l
BD: WR2_r > EK_r > Viny > WR2_l > EK_l > Viny > HL_r/3 > Viny > HL_l/3
PK: PT_r/10 > PT_l/10 > CM/5 > CB
CD: ST_r > KN > ST_l > SF/5
SV: SV/5
"""


class TestFullSampleClass:
    def test_parses_without_error(self):
        seq = parse_shorthand(SAMPLE_CLASS)
        assert seq.title == "Hip-Opening Flow"

    def test_phase_count(self):
        seq = parse_shorthand(SAMPLE_CLASS)
        assert len(seq.phases) == 6

    def test_all_poses_non_empty(self):
        seq = parse_shorthand(SAMPLE_CLASS)
        assert len(seq.all_poses) > 0

    def test_heated_defaults_false(self):
        seq = parse_shorthand(SAMPLE_CLASS)
        assert seq.heated_room is False

    def test_raw_shorthand_stored(self):
        seq = parse_shorthand(SAMPLE_CLASS)
        assert "Hip-Opening Flow" in seq.raw_shorthand
