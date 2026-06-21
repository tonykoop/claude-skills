"""Tests for breakdown_parser.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from breakdown_parser import parse_script, render_markdown_table, parse_tc, seconds_to_tc, Segment


SAMPLE_SCRIPT = """\
# Channel Trailer

[TC:0:00] [A] Presenter to camera: "Welcome to Inner Compass Yoga..."
[TC:0:08] [GEN] Opening aerial image of yoga studio at dawn
[TC:0:15] [TEXT] Channel name lower-third
[TC:0:20] [B] B-roll of students in warrior pose — Assets: studio footage
[TC:0:28] [MUSIC] Background score begins — WARN
"""


def test_parse_tc_mmss():
    assert parse_tc("0:08") == 8
    assert parse_tc("1:30") == 90
    assert parse_tc("0:00") == 0


def test_parse_tc_hhmmss():
    assert parse_tc("0:01:30") == 90
    assert parse_tc("1:00:00") == 3600


def test_parse_script_segment_count():
    segments = parse_script(SAMPLE_SCRIPT)
    assert len(segments) == 5


def test_parse_script_types():
    segments = parse_script(SAMPLE_SCRIPT)
    types = [s.seg_type for s in segments]
    assert types == ["A", "GEN", "TEXT", "B", "MUSIC"]


def test_parse_script_tc_out_chain():
    segments = parse_script(SAMPLE_SCRIPT)
    # TC-out of segment 0 should equal TC-in of segment 1
    assert segments[0].tc_out == segments[1].tc_in
    assert segments[1].tc_out == segments[2].tc_in
    assert segments[2].tc_out == segments[3].tc_in


def test_parse_script_missing_flag():
    segments = parse_script(SAMPLE_SCRIPT)
    music_seg = segments[4]
    assert music_seg.missing == "WARN"


def test_render_markdown_table_headers():
    segments = parse_script(SAMPLE_SCRIPT)
    table = render_markdown_table(segments)
    assert "TC-in" in table
    assert "TC-out" in table
    assert "Type" in table
    assert "Missing" in table


def test_render_markdown_table_row_count():
    segments = parse_script(SAMPLE_SCRIPT)
    table = render_markdown_table(segments)
    # Header row + separator + 5 data rows
    lines = [l for l in table.strip().splitlines() if l.startswith("|")]
    assert len(lines) == 7  # header + separator + 5 rows


def test_empty_script_returns_no_segments():
    segments = parse_script("# Just a heading\n\nNo TC annotations here.\n")
    assert segments == []


def test_seconds_to_tc_roundtrip():
    assert seconds_to_tc(90) == "1:30"
    assert seconds_to_tc(0) == "0:00"
    assert seconds_to_tc(65) == "1:05"
