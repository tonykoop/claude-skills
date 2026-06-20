#!/usr/bin/env python3
"""Tests for bigthink.validator — CaptureValidator schema and business rules."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigthink.registry import CaptureRegistry
from bigthink.schema import (
    CaptureConnection,
    ConnectionKind,
    Domain,
    ManufacturingTheoryCapture,
    MaturityLevel,
)
from bigthink.validator import CaptureValidator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_THESIS = (
    "Manufacturing capability scales with evaluated spatial complexity "
    "using power-law dynamics that underpin physical fabrication limits."
)

_SHORT_THESIS = "Too short thesis here."

_LONG_THESIS = (
    "Manufacturing capability scales with a power-law function of evaluated "
    "spatial complexity. Every doubling of programmatically-graded geometric "
    "variations accelerates multi-material manufacturing automation by a fixed "
    "efficiency percentage, empirically measured by the MakerBench fitness "
    "function and mapped onto the Kardashev civilizational framing."
)


def _make(id_: str = "test-cap", thesis: str = _THESIS, **kw) -> ManufacturingTheoryCapture:
    return ManufacturingTheoryCapture(id=id_, thesis=thesis, domain=Domain.SCALING_LAW, **kw)


class TestValidatorIdChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.v = CaptureValidator()

    def test_valid_id_passes(self) -> None:
        cap = _make(id_="my-cap-01")
        result = self.v.validate(cap)
        self.assertNotIn("id", " ".join(result.errors))

    def test_short_id_triggers_error_at_construction(self) -> None:
        # The schema itself rejects it, so we can't even build an invalid one
        with self.assertRaises(ValueError):
            _make(id_="a")  # only 1 char


class TestValidatorThesisChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.v = CaptureValidator()

    def test_long_thesis_passes(self) -> None:
        cap = _make()
        result = self.v.validate(cap)
        thesis_errors = [e for e in result.errors if "thesis" in e.lower()]
        self.assertEqual(thesis_errors, [])

    def test_lowercase_thesis_start_warns(self) -> None:
        cap = ManufacturingTheoryCapture(
            id="lower-start",
            thesis="manufacturing scaling law is a key concept in this domain field.",
            domain=Domain.SCALING_LAW,
        )
        result = self.v.validate(cap)
        warn_text = " ".join(result.warnings)
        self.assertIn("capital", warn_text)


class TestValidatorEvidenceChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.v = CaptureValidator()

    def test_valid_url_ref_passes(self) -> None:
        cap = _make(evidence_refs=["https://example.com/paper1"])
        result = self.v.validate(cap)
        evidence_errors = [e for e in result.errors if "evidence" in e.lower()]
        self.assertEqual(evidence_errors, [])

    def test_empty_ref_triggers_error(self) -> None:
        cap = ManufacturingTheoryCapture(
            id="empty-ref-cap",
            thesis=_THESIS,
            domain=Domain.SCALING_LAW,
            evidence_refs=["", "https://example.com/paper"],
        )
        result = self.v.validate(cap)
        self.assertFalse(result.valid)
        self.assertTrue(any("empty" in e for e in result.errors))

    def test_duplicate_ref_warns(self) -> None:
        cap = ManufacturingTheoryCapture(
            id="dup-ref-cap",
            thesis=_THESIS,
            domain=Domain.SCALING_LAW,
            evidence_refs=["https://example.com/p1", "https://example.com/p1"],
        )
        result = self.v.validate(cap)
        warn_text = " ".join(result.warnings)
        self.assertIn("Duplicate", warn_text)

    def test_odd_ref_string_warns(self) -> None:
        cap = ManufacturingTheoryCapture(
            id="odd-ref-cap",
            thesis=_THESIS,
            domain=Domain.SCALING_LAW,
            evidence_refs=["not a valid path!!!"],
        )
        result = self.v.validate(cap)
        warn_text = " ".join(result.warnings)
        self.assertIn("URL or path", warn_text)


class TestValidatorMaturityConsistency(unittest.TestCase):
    def setUp(self) -> None:
        self.v = CaptureValidator()

    def test_validated_without_evidence_is_invalid(self) -> None:
        cap = ManufacturingTheoryCapture(
            id="val-no-evidence",
            thesis=_LONG_THESIS,
            domain=Domain.SCALING_LAW,
            maturity=MaturityLevel.VALIDATED,
            source="some source",
            promotion_target="some/target",
        )
        # Must also add a connection to pass the gate, but validator checks evidence
        result = self.v.validate(cap)
        errors = " ".join(result.errors)
        self.assertIn("evidence", errors)

    def test_validated_without_source_is_invalid(self) -> None:
        cap = ManufacturingTheoryCapture(
            id="val-no-source",
            thesis=_LONG_THESIS,
            domain=Domain.SCALING_LAW,
            maturity=MaturityLevel.VALIDATED,
            evidence_refs=["https://example.com/p1"],
            promotion_target="some/target",
        )
        result = self.v.validate(cap)
        self.assertFalse(result.valid)
        self.assertTrue(any("source" in e for e in result.errors))

    def test_developing_without_source_warns(self) -> None:
        cap = ManufacturingTheoryCapture(
            id="dev-no-source",
            thesis=_THESIS,
            domain=Domain.SCALING_LAW,
            maturity=MaturityLevel.DEVELOPING,
        )
        result = self.v.validate(cap)
        warn_text = " ".join(result.warnings)
        self.assertIn("source", warn_text)

    def test_validated_without_promotion_target_warns(self) -> None:
        cap = ManufacturingTheoryCapture(
            id="val-no-promo",
            thesis=_LONG_THESIS,
            domain=Domain.SCALING_LAW,
            maturity=MaturityLevel.VALIDATED,
            evidence_refs=["https://example.com/p1"],
            source="some source",
        )
        result = self.v.validate(cap)
        warn_text = " ".join(result.warnings)
        self.assertIn("promotion_target", warn_text)


class TestValidatorAgainstRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.v = CaptureValidator()
        self.reg = CaptureRegistry()
        self.reg.add(_make("existing-cap"))

    def test_duplicate_id_is_error(self) -> None:
        new_cap = _make("existing-cap")
        result = self.v.validate_against(new_cap, self.reg)
        self.assertFalse(result.valid)
        self.assertTrue(any("already exists" in e for e in result.errors))

    def test_dangling_connection_target_is_error(self) -> None:
        cap = ManufacturingTheoryCapture(
            id="dangling-conn",
            thesis=_THESIS,
            domain=Domain.SCALING_LAW,
            connections=[CaptureConnection("dangling-conn", "missing-cap", "supports")],
        )
        result = self.v.validate_against(cap, self.reg)
        self.assertFalse(result.valid)
        self.assertTrue(any("missing-cap" in e for e in result.errors))

    def test_valid_connection_passes(self) -> None:
        cap = ManufacturingTheoryCapture(
            id="new-cap",
            thesis=_THESIS,
            domain=Domain.SCALING_LAW,
            connections=[CaptureConnection("new-cap", "existing-cap", "supports")],
        )
        result = self.v.validate_against(cap, self.reg)
        # No errors about dangling refs
        dangling_errors = [e for e in result.errors if "not in the registry" in e]
        self.assertEqual(dangling_errors, [])


class TestValidateRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.v = CaptureValidator()

    def test_validate_registry_returns_result_per_capture(self) -> None:
        reg = CaptureRegistry()
        reg.add(_make("cap-a"))
        reg.add(_make("cap-b"))
        results = self.v.validate_registry(reg)
        self.assertEqual(len(results), 2)
        ids = {r.capture_id for r in results}
        self.assertEqual(ids, {"cap-a", "cap-b"})

    def test_validate_registry_detects_dangling_edge(self) -> None:
        reg = CaptureRegistry()
        # Manually craft a capture that references a nonexistent peer
        cap = ManufacturingTheoryCapture(
            id="lonely",
            thesis=_THESIS,
            domain=Domain.SCALING_LAW,
            connections=[CaptureConnection("lonely", "ghost", "cites")],
        )
        reg.add(cap)
        results = self.v.validate_registry(reg)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].valid)
        self.assertTrue(any("ghost" in e for e in results[0].errors))


class TestValidationResultHelpers(unittest.TestCase):
    def setUp(self) -> None:
        self.v = CaptureValidator()

    def test_raise_if_invalid_raises_on_error(self) -> None:
        cap = ManufacturingTheoryCapture(
            id="val-no-evidence",
            thesis=_LONG_THESIS,
            domain=Domain.SCALING_LAW,
            maturity=MaturityLevel.VALIDATED,
            source="some source",
        )
        result = self.v.validate(cap)
        with self.assertRaises(ValueError):
            result.raise_if_invalid()

    def test_raise_if_invalid_silent_on_valid(self) -> None:
        cap = _make()
        result = self.v.validate(cap)
        result.raise_if_invalid()  # should not raise

    def test_str_shows_capture_id(self) -> None:
        cap = _make()
        result = self.v.validate(cap)
        self.assertIn("test-cap", str(result))


if __name__ == "__main__":
    unittest.main()
