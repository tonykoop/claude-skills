"""Tests for v4.5 bowed-string packet support assets."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path

import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read_csv_header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return next(csv.reader(handle))


class BowedStringManifest(unittest.TestCase):
    def setUp(self):
        manifest_path = SKILL_ROOT / "manifest.yaml"
        with manifest_path.open(encoding="utf-8") as handle:
            self.manifest = yaml.safe_load(handle)

    def test_manifest_version_matches_bowed_string_release(self):
        self.assertEqual(self.manifest["version"], "4.5.0")

    def test_manifest_exposes_bowed_string_reference(self):
        paths = {entry["path"] for entry in self.manifest["references"]}
        self.assertIn("references/bowed-string-packets.md", paths)
        self.assertIn("references/free-reed-khaen-exploration.md", paths)

    def test_manifest_exposes_templates_and_examples(self):
        template_paths = {entry["path"] for entry in self.manifest["templates"]}
        example_paths = {entry["path"] for entry in self.manifest["examples"]}

        self.assertIn("assets/templates/bowed-string-schedule.csv", template_paths)
        self.assertIn("assets/templates/bowed-source-posture.csv", template_paths)
        self.assertIn("assets/templates/decorative-no-carve-zone.csv", template_paths)
        self.assertIn(
            "examples/bowed-string/tagelharpa-string-schedule.csv",
            example_paths,
        )
        self.assertIn(
            "examples/bowed-string/yayli-source-posture.csv",
            example_paths,
        )
        self.assertIn("examples/khaen/p0-reed-coupon-log.csv", example_paths)
        self.assertIn("examples/khaen/mouth-organ-dxf-checklist.csv", example_paths)
        self.assertIn("examples/khaen/free-reed-sourcing.csv", example_paths)

    def test_manifest_paths_exist_in_partial_skill(self):
        sections = ("references", "templates", "examples", "scripts", "tests")
        for section in sections:
            with self.subTest(section=section):
                for entry in self.manifest[section]:
                    self.assertTrue(
                        (SKILL_ROOT / entry["path"]).exists(),
                        f"missing manifest path: {entry['path']}",
                    )


class BowedStringTemplates(unittest.TestCase):
    def test_string_schedule_template_has_required_fields(self):
        header = read_csv_header(
            SKILL_ROOT / "assets" / "templates" / "bowed-string-schedule.csv"
        )
        for required in (
            "target_pitch",
            "scale_length_mm",
            "material_family",
            "gauge_or_diameter",
            "estimated_tension_lbf",
            "retuning_factor",
            "percent_breaking",
            "risk_flags",
        ):
            self.assertIn(required, header)

    def test_source_posture_template_has_honesty_fields(self):
        header = read_csv_header(
            SKILL_ROOT / "assets" / "templates" / "bowed-source-posture.csv"
        )
        for required in ("claim_text", "posture", "evidence_path_or_url"):
            self.assertIn(required, header)

    def test_no_carve_zone_template_has_validation_fields(self):
        header = read_csv_header(
            SKILL_ROOT / "assets" / "templates" / "decorative-no-carve-zone.csv"
        )
        for required in (
            "geometry_reference",
            "margin_mm",
            "forbidden_operations",
            "validation_coupon_required",
        ):
            self.assertIn(required, header)


class BowedStringReference(unittest.TestCase):
    def test_reference_covers_issue_106_topics(self):
        text = (
            SKILL_ROOT / "references" / "bowed-string-packets.md"
        ).read_text(encoding="utf-8").lower()
        for phrase in (
            "bridge crown",
            "afterlength",
            "tailpiece load path",
            "soundboard patch",
            "bow clearance",
            "top deflection",
            "neck reinforcement",
            "active and sympathetic",
            "solidworks skeleton checklist",
            "decorative no-carve zones",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
