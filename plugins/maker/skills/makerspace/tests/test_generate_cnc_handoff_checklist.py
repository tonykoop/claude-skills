"""Tests for generate_cnc_handoff_checklist.py.

Run from the repo root:
    python3 -m unittest discover -s skills/makerspace/tests -v
"""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
EXAMPLE_DIR = (
    SKILL_DIR
    / "references"
    / "examples"
    / "cnc-laser-fabrication-handoff"
)

sys.path.insert(0, str(SCRIPTS_DIR))

import generate_cnc_handoff_checklist as g  # noqa: E402


class ChecklistRole(unittest.TestCase):
    def test_generated_checklist_declares_blocker_role(self):
        data = g.load_source(EXAMPLE_DIR / "design_params.json")
        checklist = g.build_checklist(data)

        self.assertEqual(
            checklist["checklist_role"],
            "blocker_list_not_pass_certificate",
        )
        self.assertIn("do not certify shop readiness",
                      checklist["generated_checklist_notice"])
        self.assertIn("fabrication owner after source review",
                      checklist["handoff_decision"]["ready_when"])
        self.assertIn(
            "generated checklist is treated as a pass certificate "
            "without owner review",
            checklist["handoff_decision"]["blocked_when"],
        )

    def test_cli_outputs_blocker_role_and_schema_valid_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            rc = g.main([
                "--source",
                str(EXAMPLE_DIR / "design_params.json"),
                "--out-dir",
                str(out_dir),
            ])
            self.assertEqual(rc, 0)

            checklist = json.loads(
                (out_dir / "handoff_checklist.json").read_text(),
            )
            self.assertEqual(
                checklist["checklist_role"],
                "blocker_list_not_pass_certificate",
            )

            with (out_dir / "validation.csv").open(newline="") as f:
                rows = list(csv.reader(f))
            self.assertEqual(rows[0], g.VALIDATION_FIELDS)
            self.assertGreater(len(rows), 1)


if __name__ == "__main__":
    unittest.main()
