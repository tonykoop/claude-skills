"""Tests for validate_visual_authority.py.

Run from the repo root:
    python3 -m unittest discover -s skills/instrument-maker-v4/tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent / "scripts"
FIXTURES_DIR = THIS_DIR / "fixtures" / "visual-authority"
REFERENCE = THIS_DIR.parent / "references" / "drawing-and-visual-authority.md"

sys.path.insert(0, str(SCRIPTS_DIR))

import validate_visual_authority as v  # noqa: E402


def load_pass(name: str):
    return v.load_register(FIXTURES_DIR / "pass" / name)


def load_fail(name: str):
    return v.load_register(FIXTURES_DIR / "fail" / name)


class PassFixtures(unittest.TestCase):
    def test_dxf_authority_with_image_gen_concepts_passes(self):
        rep = v.validate_rows(load_pass("dxf-with-image-gen-concepts.csv"))
        self.assertEqual([f.code for f in rep.errors], [])
        self.assertEqual(rep.rows_checked, 4)

    def test_json_register_passes(self):
        rep = v.validate_rows(load_pass("dxf-with-concept-register.json"))
        self.assertEqual([f.code for f in rep.errors], [])
        self.assertEqual(rep.rows_checked, 3)


class FailFixtures(unittest.TestCase):
    def test_image_gen_fabrication_authority_fails(self):
        rep = v.validate_rows(load_fail("image-gen-as-authority.csv"))
        codes = {f.code for f in rep.errors}
        self.assertIn("IMAGE_GEN_AS_FABRICATION_AUTHORITY", codes)
        self.assertIn("IMAGE_GEN_WITH_FABRICATION_ROLE", codes)
        self.assertIn("IMAGE_GEN_DIMENSION_INFERRED", codes)

    def test_no_fabrication_authority_fails_for_build_visuals(self):
        rep = v.validate_rows(load_fail("no-dxf-authority.csv"))
        self.assertIn("NO_FABRICATION_AUTHORITY",
                      {f.code for f in rep.errors})

    def test_derived_preview_requires_source(self):
        rep = v.validate_rows(load_fail("derived-preview-no-source.csv"))
        self.assertIn("MISSING_DERIVED_FROM",
                      {f.code for f in rep.errors})

    def test_missing_required_columns_fail(self):
        rep = v.validate_rows(load_fail("missing-required-columns.csv"))
        codes = {f.code for f in rep.errors}
        self.assertIn("MISSING_COLUMN_authority", codes)
        self.assertIn("MISSING_COLUMN_dimension_claim", codes)


class Vocabulary(unittest.TestCase):
    def test_image_gen_kinds_are_non_authority(self):
        self.assertEqual(v.IMAGE_GEN_KINDS,
                         {"image_gen_2_prompt", "image_gen_2_output"})
        self.assertNotIn("fabrication", {"concept_only", "reference_only"})

    def test_fabrication_authority_kinds_include_dxf_cad(self):
        self.assertIn("dxf", v.FABRICATION_AUTHORITY_KINDS)
        self.assertIn("cad", v.FABRICATION_AUTHORITY_KINDS)
        self.assertIn("design_table", v.FABRICATION_AUTHORITY_KINDS)


class ReferenceContract(unittest.TestCase):
    def test_reference_requires_early_register_for_concept_visuals(self):
        text = REFERENCE.read_text(encoding="utf-8")
        for required in (
            "before the first",
            "concept image",
            "SVG preview",
            "drawing PDF",
            "Do this even when no fabrication-authority DXF/CAD exists yet.",
            "concept_only",
            "reference_only",
        ):
            self.assertIn(required, text)

    def test_reference_names_spike_fiddle_measurement_gates(self):
        text = REFERENCE.read_text(encoding="utf-8")
        for required in (
            "String and Spike-Fiddle Starters",
            "qianjin-to-bridge speaking length",
            "bridge placement",
            "neck/spike alignment",
            "peg/string path",
            "membrane/soundboard interface",
        ):
            self.assertIn(required, text)


class MainCli(unittest.TestCase):
    def test_main_returns_0_on_pass(self):
        rc = v.main([str(FIXTURES_DIR / "pass" /
                         "dxf-with-image-gen-concepts.csv")])
        self.assertEqual(rc, 0)

    def test_main_returns_1_on_fail(self):
        rc = v.main([str(FIXTURES_DIR / "fail" /
                         "image-gen-as-authority.csv")])
        self.assertEqual(rc, 1)

    def test_main_returns_2_on_missing_file(self):
        rc = v.main([str(FIXTURES_DIR / "does-not-exist.csv")])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
