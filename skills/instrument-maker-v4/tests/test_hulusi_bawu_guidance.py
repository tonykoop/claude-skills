"""Contract tests for hulusi/bawu stopped-pipe free-reed guidance."""

from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REFERENCE = SKILL_DIR / "references" / "hulusi-bawu-stopped-pipe-free-reed.md"
EXAMPLE_DIR = SKILL_DIR / "examples" / "hulusi-bawu"
SCRIPTS_DIR = SKILL_DIR / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))

import validate_acoustic_law as acoustic_validator  # noqa: E402
import validate_visual_authority as visual_validator  # noqa: E402


class HulusiBawuGuidance(unittest.TestCase):
    def test_reference_contains_readiness_boundaries(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        for required in (
            "stopped-pipe free-reed",
            "control-build",
            "HUL-P0",
            "HUL-P1",
            "L1_packet -> measurement_required",
            "unknown_requires_measurement",
            "Do not route hulusi/bawu as `side_branch_reed`",
            "rows_checked=0",
            "visual-output-register.csv",
            "Do not redesign the instrument",
            "do not claim build-ready",
        ):
            self.assertIn(required, text)

    def test_example_file_set(self) -> None:
        expected = {
            "README.md",
            "family-spec.csv",
            "validation-loop.csv",
            "visual-output-register.csv",
        }
        actual = {path.name for path in EXAMPLE_DIR.iterdir() if path.is_file()}
        self.assertEqual(expected, actual)

    def test_family_spec_is_measurement_required_and_checked(self) -> None:
        rows = acoustic_validator.load_family_spec(EXAMPLE_DIR / "family-spec.csv")
        rep = acoustic_validator.validate_rows(rows)
        self.assertEqual([f.code for f in rep.errors], [])
        self.assertEqual(rep.rows_checked, 3)
        self.assertTrue(all(
            row["acoustic_law"] == "unknown_requires_measurement"
            for row in rows
        ))
        self.assertTrue(any(
            f.code == "UNKNOWN_LAW_NEEDS_MEASUREMENT"
            for f in rep.warnings
        ))

    def test_validation_loop_preserves_measurement_required_status(self) -> None:
        with (EXAMPLE_DIR / "validation-loop.csv").open(
                newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        self.assertGreaterEqual(len(rows), 4)
        self.assertEqual(
            set(rows[0].keys()),
            {
                "check_id",
                "packet_artifact",
                "readiness_before",
                "prediction_source",
                "target",
                "tolerance",
                "method",
                "measured_result",
                "status",
                "next_action",
                "evidence",
                "source_status",
            },
        )
        self.assertTrue(all(row["readiness_before"] == "L1_packet"
                            for row in rows))
        self.assertTrue(all(row["status"] == "measurement_required"
                            for row in rows))

    def test_visual_register_keeps_concept_images_non_authoritative(self) -> None:
        rows = visual_validator.load_register(EXAMPLE_DIR /
                                              "visual-output-register.csv")
        rep = visual_validator.validate_rows(rows)
        self.assertEqual([f.code for f in rep.errors], [])
        authorities = {row["artifact_id"]: row["authority"] for row in rows}
        self.assertEqual(authorities["DT-001"], "fabrication")
        self.assertEqual(authorities["IMG-001"], "concept_only")
        self.assertEqual(authorities["SVG-001"], "derived_preview")

    def test_skill_stub_references_hulusi_bawu_guidance(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: instrument-maker-v4", skill)
        self.assertIn("partial-skill: true", skill)
        self.assertIn("hulusi-bawu-stopped-pipe-free-reed.md", skill)
        self.assertIn("examples/hulusi-bawu", skill)


if __name__ == "__main__":
    unittest.main()
