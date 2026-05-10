"""Tests for validate_acoustic_law.py.

Run from the skill folder:
    python3 -m unittest skills/instrument-maker-v4/tests/test_validate_acoustic_law.py

Or from anywhere:
    python3 -m unittest discover -s skills/instrument-maker-v4/tests
"""

from __future__ import annotations

import csv
import io
import sys
import unittest
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent / "scripts"
FIXTURES_DIR = THIS_DIR / "fixtures" / "family-spec"

sys.path.insert(0, str(SCRIPTS_DIR))

import validate_acoustic_law as v  # noqa: E402


def load_pass(name: str):
    return v.load_family_spec(FIXTURES_DIR / "pass" / name)


def load_fail(name: str):
    return v.load_family_spec(FIXTURES_DIR / "fail" / name)


class PassFixtures(unittest.TestCase):
    def test_traditional_khaen_passes(self):
        rep = v.validate_rows(load_pass("khaen-traditional.csv"))
        self.assertEqual([f.code for f in rep.errors], [])
        self.assertGreater(rep.rows_checked, 0)

    def test_quarter_wave_sister_passes(self):
        rep = v.validate_rows(load_pass("khaen-quarter-wave-sister.csv"))
        self.assertEqual([f.code for f in rep.errors], [])

    def test_unknown_requires_measurement_warns_not_fails(self):
        rep = v.validate_rows(load_pass("khaen-needs-measurement.csv"))
        self.assertEqual([f.code for f in rep.errors], [])
        self.assertTrue(any(
            f.code == "UNKNOWN_LAW_NEEDS_MEASUREMENT"
            for f in rep.warnings))

    def test_idiophone_skipped(self):
        rep = v.validate_rows(load_pass("tongue-drum-idiophone.csv"))
        self.assertEqual([f.code for f in rep.errors], [])
        self.assertEqual(rep.rows_checked, 0)
        self.assertEqual(rep.rows_skipped_non_wind, 3)
        self.assertTrue(any(
            f.code == "NON_WIND_FAMILY_SKIPPED" for f in rep.findings))


class FailFixtures(unittest.TestCase):
    def test_missing_acoustic_law_column_fails(self):
        rep = v.validate_rows(load_fail("khaen-missing-acoustic-law.csv"))
        codes = {f.code for f in rep.errors}
        self.assertIn("MISSING_COLUMN_acoustic_law", codes)
        self.assertIn("MISSING_COLUMN_end_condition", codes)
        self.assertIn("MISSING_COLUMN_dimension_provenance", codes)

    def test_bad_vocabulary_fails(self):
        rep = v.validate_rows(load_fail("khaen-bad-vocabulary.csv"))
        bad = [f for f in rep.errors if f.code == "INVALID_acoustic_law"]
        self.assertEqual(len(bad), 2)
        self.assertIn("half_wave", bad[0].message)
        self.assertIn("quarter_wave_closed_open", bad[1].message)

    def test_incompatible_end_condition_fails(self):
        rep = v.validate_rows(load_fail("khaen-incompatible-end-condition.csv"))
        bad = [f for f in rep.errors
               if f.code == "INCOMPATIBLE_law_end_condition"]
        self.assertEqual(len(bad), 2)

    def test_physics_dimension_mismatch_fails(self):
        rep = v.validate_rows(load_fail("khaen-physics-mismatch.csv"))
        bad = [f for f in rep.errors if f.code == "PHYSICS_DIMENSION_MISMATCH"]
        self.assertGreaterEqual(len(bad), 1,
            "The Round 7 'half-the-correct-length' bug should be caught")
        # G3 half-wave correct ≈ 867 mm; failing fixture says 427 mm
        self.assertIn("disagrees", bad[0].message)


class FormulaCorrectness(unittest.TestCase):
    """Sanity-check the embedded formula against the v2 partner-peek
    Octave numerical cross-check from /tmp/twingrid-r7-claude-irene-khaen-family.
    """

    def test_g3_side_branch_reed_matches_octave_value(self):
        # From v2-octave-output.txt:  G3 → L_geom = 866.89 mm
        # Our formula uses 8.13 mm total end correction (12x12 channel)
        L = v.predicted_length_from_formula("side_branch_reed", 196.0)
        self.assertAlmostEqual(L, 866.87, delta=0.5)

    def test_a4_side_branch_reed_matches_octave_value(self):
        # From v2-octave-output.txt:  A4 → L_geom = 381.65 mm
        L = v.predicted_length_from_formula("side_branch_reed", 440.0)
        self.assertAlmostEqual(L, 381.65, delta=0.5)

    def test_a4_closed_open_is_half_of_open_open(self):
        L_oo = v.predicted_length_from_formula("open_open", 440.0)
        L_co = v.predicted_length_from_formula("closed_open", 440.0)
        # The closed_open form sounds an octave below open_open of same
        # length, so for the same target Hz it's half the length.
        # Allowing for end-correction (which we halve too in the
        # implementation), the ratio should be near 0.5.
        self.assertLess(abs((L_co / L_oo) - 0.5), 0.05)


class ControlledVocabulary(unittest.TestCase):
    """The vocabulary shipped in the validator must match the docs."""

    def test_vocabulary_is_exactly_seven(self):
        # If you add or remove a value, update references/acoustic-models.md
        # and references/family-aware-design.md to match.
        self.assertEqual(len(v.CONTROLLED_VOCABULARY), 7)

    def test_required_values_present(self):
        for required in ("open_open", "closed_open", "stopped_pipe",
                         "side_branch_reed", "free_reed_coupled_pipe",
                         "empirical_only", "unknown_requires_measurement"):
            self.assertIn(required, v.CONTROLLED_VOCABULARY)


class MainCli(unittest.TestCase):
    def test_main_returns_0_on_pass(self):
        rc = v.main([str(FIXTURES_DIR / "pass" / "khaen-traditional.csv")])
        self.assertEqual(rc, 0)

    def test_main_returns_1_on_fail(self):
        rc = v.main([str(FIXTURES_DIR / "fail" / "khaen-missing-acoustic-law.csv")])
        self.assertEqual(rc, 1)

    def test_main_returns_2_on_missing_file(self):
        rc = v.main([str(FIXTURES_DIR / "does-not-exist.csv")])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
