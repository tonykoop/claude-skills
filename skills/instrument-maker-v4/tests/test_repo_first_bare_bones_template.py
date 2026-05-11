"""Contract tests for the repo-first bare-bones packet template."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REFERENCE = SKILL_DIR / "references" / "repo-first-bare-bones-packet.md"
EXAMPLE_DIR = SKILL_DIR / "examples" / "repo-first-bare-bones-packet"
STRING_SPIKE_DIR = EXAMPLE_DIR / "string-spike-fiddle"


class RepoFirstBareBonesTemplate(unittest.TestCase):
    def test_reference_contains_required_readiness_boundaries(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        for required in (
            "readiness:bare-bones",
            "repo-first",
            "not build-ready",
            "future authority unless measured geometry already exists",
            "Do not publish private family, child, location, or media details.",
            "Do not use generated images as dimensional or fabrication authority.",
            "visual-output-register.csv",
            "String and Spike-Fiddle Starters",
            "qianjin-to-bridge span",
            "380-420 mm",
            "membrane/soundboard interface",
            "Do not nest this packet under `build-packets/`",
            "validation-loop upgrade",
        ):
            self.assertIn(required, text)

    def test_example_file_set_is_root_packet_shape(self) -> None:
        expected = {
            "README.md",
            "design.md",
            "bom.csv",
            "sourcing.csv",
            "cut-list.csv",
            "validation.csv",
            "risks.md",
            "drawing-brief.md",
            "photo-shotlist.md",
        }
        actual = {path.name for path in EXAMPLE_DIR.iterdir() if path.is_file()}
        self.assertEqual(expected, actual)

    def test_validation_csv_has_required_columns_and_gates(self) -> None:
        with (EXAMPLE_DIR / "validation.csv").open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        self.assertGreaterEqual(len(rows), 6)
        self.assertEqual(
            set(rows[0].keys()),
            {
                "gate_id",
                "gate",
                "required_before",
                "method",
                "status",
                "next_action",
                "evidence",
                "notes",
            },
        )
        gates = {row["gate"] for row in rows}
        self.assertIn("Acoustic model selected and justified", gates)
        self.assertIn("Public-safe documentation reviewed", gates)
        self.assertTrue(all(row["status"] == "TBD" for row in rows))
        self.assertTrue(all(row["next_action"] for row in rows))
        self.assertTrue(all(row["evidence"] == "TBD" for row in rows))

    def test_bom_and_sourcing_track_source_status(self) -> None:
        for filename in ("bom.csv", "sourcing.csv"):
            with (EXAMPLE_DIR / filename).open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertGreaterEqual(len(rows), 4)
            self.assertIn("source_status", rows[0])

        with (EXAMPLE_DIR / "bom.csv").open(newline="", encoding="utf-8") as f:
            bom_statuses = {row["source_status"] for row in csv.DictReader(f)}
        self.assertIn("supplier_spec_unverified", bom_statuses)
        self.assertIn("substitution_candidate", bom_statuses)

    def test_skill_stub_references_bare_bones_template(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("version: 4.4.7", skill)
        self.assertIn("repo-first-bare-bones-packet.md", skill)
        self.assertIn("repo-first-bare-bones-packet/", skill)
        self.assertIn("string-spike-fiddle", skill)
        self.assertIn("test_repo_first_bare_bones_template.py", skill)

    def test_string_spike_variant_names_guardrails(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        for required in (
            "String / Spike-Fiddle Variant",
            "qianjin-to-bridge speaking span",
            "380-420 mm",
            "measurement-required",
            "membrane/soundboard interface",
            "artifact:dxf",
            "permission to invent cut-ready geometry",
        ):
            self.assertIn(required, text)

    def test_string_spike_example_has_required_gates(self) -> None:
        readme = (STRING_SPIKE_DIR / "README.md").read_text(encoding="utf-8")
        self.assertIn("not build-ready", readme)
        self.assertIn("qianjin-to-bridge", readme)
        self.assertIn("380-420 mm", readme)

        with (STRING_SPIKE_DIR / "readiness-gates.csv").open(
            newline="", encoding="utf-8"
        ) as f:
            rows = list(csv.DictReader(f))

        fields = {row["field"] for row in rows}
        self.assertIn("speaking_length_qianjin_to_bridge_mm", fields)
        self.assertIn("membrane_soundboard_interface", fields)
        self.assertIn("dxf_cad_authority_status", fields)
        self.assertTrue(
            all(
                row["status"] in {"measurement-required", "future-authority"}
                for row in rows
            )
        )


if __name__ == "__main__":
    unittest.main()
