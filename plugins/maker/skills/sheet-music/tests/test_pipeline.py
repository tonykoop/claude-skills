"""Smoke tests for the sheet-music pipeline.

These tests do not require optional dependencies (LilyPond, music21,
fluidsynth). They verify that the parts of the pipeline that work with
just stdlib + reportlab actually produce output.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PYTHON = sys.executable


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, *args], capture_output=True, text=True, cwd=str(REPO)
    )


def test_generate_scales_for_naf(tmp_path):
    out = tmp_path / "scales.abc"
    r = run("scripts/generate_scales.py", "--instrument", "naf-6hole",
            "--out", str(out))
    assert r.returncode == 0, r.stderr
    text = out.read_text()
    assert "T:Range Walk" in text
    assert "K:A" in text
    # NAF range is A4..D6; ABC pitches should include both ends
    assert "A " in text or text.startswith("A ") or "A\n" in text


def test_generate_scales_for_pvc_flute(tmp_path):
    out = tmp_path / "scales.abc"
    r = run("scripts/generate_scales.py", "--instrument", "pvc-flute",
            "--out", str(out))
    assert r.returncode == 0, r.stderr
    text = out.read_text()
    assert "K:C" in text


def test_generate_scales_unknown_instrument(tmp_path):
    out = tmp_path / "scales.abc"
    r = run("scripts/generate_scales.py", "--instrument", "imaginary",
            "--out", str(out))
    assert r.returncode != 0


def test_validate_in_range(tmp_path):
    # PVC flute is C5..C7. Twinkle in C is C5..A5 → in range.
    r = run("scripts/validate_arrangement.py",
            "--tune", "catalog/public-domain/nursery/twinkle-twinkle/tune.abc",
            "--instrument", "pvc-flute")
    assert r.returncode == 0, r.stderr
    assert "no issues" in r.stdout or "warning" not in r.stdout


def test_validate_out_of_range(tmp_path):
    # NAF range starts at A4. Canonical Twinkle starts at C5 (above
    # the registry's range_low=A4 in pitch terms — but the ABC
    # 'C' = C5. So twinkle should actually be in range. Let's use
    # an explicitly-low test tune.
    low_tune = tmp_path / "low.abc"
    low_tune.write_text(
        "X:1\nT:Low test\nM:4/4\nL:1/4\nQ:1/4=90\nK:C\nC, D, E, F, |\n"
    )
    r = run("scripts/validate_arrangement.py",
            "--tune", str(low_tune),
            "--instrument", "naf-6hole",
            "--strict")
    # below range_low=A4 → strict mode returns nonzero
    assert r.returncode != 0
    assert "below" in r.stdout


def test_render_fingering_svg(tmp_path):
    out = tmp_path / "fingering.svg"
    r = run("scripts/render_fingering_svg.py",
            "--tune", "catalog/public-domain/nursery/twinkle-twinkle/tune.abc",
            "--instrument", "naf-6hole",
            "--out", str(out))
    assert r.returncode == 0, r.stderr
    svg = out.read_text()
    assert svg.startswith("<svg")
    assert "scheme: naf-6hole" in svg
    # Twinkle has 6 distinct pitches (C D E F G A); SVG should show ≥ 6 diagrams
    assert svg.count("<rect ") >= 6


def test_abc_to_midi_stdlib_fallback(tmp_path):
    """Even without music21 or abc2midi, the stdlib fallback writes a MIDI."""
    out = tmp_path / "twinkle.mid"
    r = run("scripts/abc_to_midi.py",
            "--tune", "catalog/public-domain/nursery/twinkle-twinkle/tune.abc",
            "--instrument", "naf-6hole",
            "--out", str(out))
    assert r.returncode == 0, r.stderr
    data = out.read_bytes()
    assert data[:4] == b"MThd"
    assert b"MTrk" in data


def test_render_pipeline_end_to_end(tmp_path):
    """Pipeline runs and produces a render-summary.json that lists every stage."""
    r = run("scripts/render_pipeline.py",
            "--tune", "catalog/public-domain/nursery/twinkle-twinkle/tune.abc",
            "--instrument", "naf-6hole",
            "--out", str(tmp_path))
    # Should not crash even if optional stages fail
    assert r.returncode == 0, r.stderr
    summary = json.loads((tmp_path / "render-summary.json").read_text())
    assert "stages" in summary
    # MIDI stage must succeed (stdlib fallback always works)
    assert summary["stages"]["midi"]["ok"] is True
    # Jianpu stage must succeed (pure stdlib, no external deps)
    assert summary["stages"]["jianpu"]["ok"] is True
    # Fingering stage must succeed (no external deps)
    assert summary["stages"]["fingering"]["ok"] is True


def test_abc_to_jianpu_major_key(tmp_path):
    """Twinkle Twinkle in C major: 1=C header, movable-do degrees."""
    out = tmp_path / "twinkle-jianpu.txt"
    r = run("scripts/abc_to_jianpu.py",
            "--tune", "catalog/public-domain/nursery/twinkle-twinkle/tune.abc",
            "--out", str(out))
    assert r.returncode == 0, r.stderr
    text = out.read_text()
    assert "1=C" in text
    assert "4/4" in text
    # C C G G | A A G- | -> scale degrees 1 1 5 5 | 6 6 5-
    assert "1 1 5 5 | 6 6 5- | 4 4 3 3 | 2 2 1- |" in text


def test_abc_to_jianpu_minor_key_shows_relative_major(tmp_path):
    """K:Am renders under the relative major's 1=C header, tonic as scale degree 6."""
    out = tmp_path / "pentatonic-jianpu.txt"
    r = run("scripts/abc_to_jianpu.py",
            "--tune", "tests/sample_inputs/tiny-pentatonic.abc",
            "--out", str(out))
    assert r.returncode == 0, r.stderr
    text = out.read_text()
    assert "1=C" in text
    assert "scale degree 6" in text
    # A B c d e | e d c B A -> 6 7 1 2 3 | 3 2 1 7 6
    assert "6 7 1 2 3 | 3 2 1 7 6" in text
    # lowercase c d e are one octave above the written register -> dot row above
    lines = text.splitlines()
    body_idx = next(i for i, ln in enumerate(lines) if "6 7 1 2 3" in ln)
    assert "." in lines[body_idx - 1]


def test_abc_to_jianpu_rest_and_duration(tmp_path):
    tune = tmp_path / "rest.abc"
    tune.write_text("X:1\nT:Rest Test\nM:4/4\nL:1/4\nQ:1/4=90\nK:C\nC2 z E F |\n")
    out = tmp_path / "rest-jianpu.txt"
    r = run("scripts/abc_to_jianpu.py", "--tune", str(tune), "--out", str(out))
    assert r.returncode == 0, r.stderr
    text = out.read_text()
    # C2 (half note, one extra beat) -> "1-"; z (rest) -> "0"
    assert "1- 0 3 4 |" in text


def test_abc_to_jianpu_missing_tune(tmp_path):
    r = run("scripts/abc_to_jianpu.py",
            "--tune", str(tmp_path / "does-not-exist.abc"),
            "--out", str(tmp_path / "out.txt"))
    assert r.returncode != 0


def test_compose_original_writes_scaffold(tmp_path):
    out = tmp_path / "test-original"
    r = run("scripts/compose_original.py",
            "--instrument", "fujara",
            "--slug", "test-tune",
            "--mood", "slow",
            "--form", "AABA",
            "--out", str(out))
    assert r.returncode == 0, r.stderr
    abc = (out / "tune.abc").read_text()
    notes = (out / "notes.md").read_text()
    assert "T:Test Tune" in abc
    assert "TODO(LLM)" in abc
    assert "AABA" in notes
    assert "fujara" in notes.lower()
