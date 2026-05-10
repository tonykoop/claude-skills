#!/usr/bin/env python3
"""Focused tests for instrument-maker-v4 acoustic-law validation."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "instrument-maker-v4"
    / "scripts"
    / "validate_packet.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("instrument_validate_packet", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["instrument_validate_packet"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validator = _load_module()


class AcousticLawValidationTests(unittest.TestCase):
    def _packet_with_family_spec(self, csv_text: str) -> Path:
        tmp = tempfile.TemporaryDirectory(prefix="instrument-v4-law-")
        self.addCleanup(tmp.cleanup)
        packet = Path(tmp.name)
        (packet / "family-spec.csv").write_text(textwrap.dedent(csv_text), encoding="utf-8")
        return packet

    def _findings(self, packet: Path) -> list[str]:
        layout = validator.detect_layout(packet)
        return validator.check_family_spec_acoustic_law(layout)

    def test_missing_acoustic_law_column_is_a_finding(self) -> None:
        packet = self._packet_with_family_spec(
            """\
            member_id,target_hz,target_note,notes
            KHN-HW-G3,196.0,G3,missing acoustic law
            """
        )
        findings = self._findings(packet)
        self.assertTrue(any("missing required acoustic-law column" in f for f in findings), findings)

    def test_invalid_acoustic_law_value_is_a_finding(self) -> None:
        packet = self._packet_with_family_spec(
            """\
            member_id,target_hz,target_note,acoustic_law,end_condition,reed_source_role,cad_dimension_basis,notes
            KHN-HW-G3,196.0,G3,quarter_wave_magic,both_pipe_ends_open,exciter,physics_derived,bad vocab
            """
        )
        findings = self._findings(packet)
        self.assertTrue(any("invalid acoustic_law" in f for f in findings), findings)

    def test_khaen_side_branch_reed_row_passes(self) -> None:
        packet = self._packet_with_family_spec(
            """\
            member_id,target_hz,target_note,acoustic_law,end_condition,reed_source_role,cad_dimension_basis,notes
            KHN-HW-G3,196.0,G3,side_branch_reed,both_pipe_ends_open,exciter,physics_derived,traditional khaen pipe
            """
        )
        self.assertEqual(self._findings(packet), [])

    def test_measurement_required_law_cannot_claim_physics_derived_cad(self) -> None:
        packet = self._packet_with_family_spec(
            """\
            member_id,target_hz,target_note,acoustic_law,end_condition,reed_source_role,cad_dimension_basis,notes
            EXP-1,220.0,A3,unknown_requires_measurement,TBD,unknown_requires_measurement,physics_derived,not measured yet
            """
        )
        findings = self._findings(packet)
        self.assertTrue(any("cad_dimension_basis cannot be physics_derived" in f for f in findings), findings)


if __name__ == "__main__":
    unittest.main()
