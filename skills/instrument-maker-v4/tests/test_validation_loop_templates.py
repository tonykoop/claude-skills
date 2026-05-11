"""Contract tests for the prototype validation-loop upgrade template."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REFERENCE = SKILL_DIR / "references" / "prototype-validation-loop-upgrade.md"
EXAMPLE = SKILL_DIR / "examples" / "khaen" / "prototype-validation-loop.csv"


class PrototypeValidationLoopTemplate(unittest.TestCase):
    def test_reference_contains_required_upgrade_gates(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        for required in (
            "L0_concept",
            "L1_packet",
            "L2_bench_validated",
            "L3_playable_prototype",
            "L4_repeatable_packet",
            "readiness:bare-bones",
            "validation-loop.csv",
            "CAD, DXF, design tables",
            "concept/story support only",
            "Do not redesign the instrument",
            "supplier_spec_unverified",
        ):
            self.assertIn(required, text)

    def test_example_csv_has_required_columns_and_statuses(self) -> None:
        with EXAMPLE.open(newline="", encoding="utf-8") as f:
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
        statuses = {row["status"] for row in rows}
        self.assertIn("measurement_required", statuses)
        source_statuses = {row["source_status"] for row in rows}
        self.assertIn("supplier_spec_unverified", source_statuses)
        self.assertIn("needs_current_check", source_statuses)
        artifacts = {row["packet_artifact"] for row in rows}
        self.assertIn("family-spec.csv", artifacts)
        self.assertIn("mouth-organ-dxf-checklist.csv", artifacts)

    def test_skill_stub_references_upgrade_template(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("version: 4.4.4", skill)
        self.assertIn("prototype-validation-loop-upgrade.md", skill)
        self.assertIn("prototype-validation-loop.csv", skill)


if __name__ == "__main__":
    unittest.main()
