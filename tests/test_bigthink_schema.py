#!/usr/bin/env python3
"""Tests for bigthink.schema — ManufacturingTheoryCapture, MaturityLevel,
CaptureConnection data types."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Allow running from repo root without installing
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigthink.schema import (
    CaptureConnection,
    ConnectionKind,
    Domain,
    ManufacturingTheoryCapture,
    MaturityLevel,
)


class TestMaturityLevel(unittest.TestCase):
    def test_rank_ordering(self) -> None:
        self.assertLess(MaturityLevel.SEED.rank, MaturityLevel.DEVELOPING.rank)
        self.assertLess(MaturityLevel.DEVELOPING.rank, MaturityLevel.VALIDATED.rank)

    def test_can_advance_to_next(self) -> None:
        self.assertTrue(MaturityLevel.SEED.can_advance_to(MaturityLevel.DEVELOPING))
        self.assertTrue(MaturityLevel.DEVELOPING.can_advance_to(MaturityLevel.VALIDATED))

    def test_cannot_skip_level(self) -> None:
        self.assertFalse(MaturityLevel.SEED.can_advance_to(MaturityLevel.VALIDATED))

    def test_cannot_regress(self) -> None:
        self.assertFalse(MaturityLevel.DEVELOPING.can_advance_to(MaturityLevel.SEED))
        self.assertFalse(MaturityLevel.VALIDATED.can_advance_to(MaturityLevel.DEVELOPING))

    def test_string_values(self) -> None:
        self.assertEqual(MaturityLevel.SEED.value, "seed")
        self.assertEqual(MaturityLevel.DEVELOPING.value, "developing")
        self.assertEqual(MaturityLevel.VALIDATED.value, "validated")


class TestCaptureConnection(unittest.TestCase):
    def test_valid_construction(self) -> None:
        conn = CaptureConnection("a", "b", ConnectionKind.SUPPORTS)
        self.assertEqual(conn.from_id, "a")
        self.assertEqual(conn.to_id, "b")
        self.assertEqual(conn.kind, ConnectionKind.SUPPORTS)

    def test_string_kind_coerced(self) -> None:
        conn = CaptureConnection("a", "b", "extends")
        self.assertIsInstance(conn.kind, ConnectionKind)
        self.assertEqual(conn.kind, ConnectionKind.EXTENDS)

    def test_self_loop_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CaptureConnection("a", "a", ConnectionKind.CITES)

    def test_empty_from_id_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CaptureConnection("", "b", ConnectionKind.SUPPORTS)

    def test_reversed(self) -> None:
        conn = CaptureConnection("x", "y", ConnectionKind.EXTENDS, "note")
        rev = conn.reversed()
        self.assertEqual(rev.from_id, "y")
        self.assertEqual(rev.to_id, "x")
        self.assertEqual(rev.kind, ConnectionKind.EXTENDS)


class TestManufacturingTheorycapture(unittest.TestCase):
    _LONG_THESIS = (
        "This is a detailed thesis about manufacturing scaling laws "
        "that spans enough words to pass the minimum validation gate."
    )

    def _make(self, **overrides) -> ManufacturingTheoryCapture:
        defaults = {
            "id": "test-cap-01",
            "thesis": self._LONG_THESIS,
            "domain": Domain.SCALING_LAW,
        }
        defaults.update(overrides)
        return ManufacturingTheoryCapture(**defaults)

    def test_valid_capture_constructs(self) -> None:
        cap = self._make()
        self.assertEqual(cap.id, "test-cap-01")
        self.assertEqual(cap.domain, Domain.SCALING_LAW)
        self.assertEqual(cap.maturity, MaturityLevel.SEED)

    def test_string_domain_coerced(self) -> None:
        cap = self._make(domain="materials")
        self.assertIsInstance(cap.domain, Domain)
        self.assertEqual(cap.domain, Domain.MATERIALS)

    def test_string_maturity_coerced(self) -> None:
        cap = self._make(maturity="developing")
        self.assertIsInstance(cap.maturity, MaturityLevel)
        self.assertEqual(cap.maturity, MaturityLevel.DEVELOPING)

    def test_invalid_id_slug_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._make(id="Bad ID With Spaces")

    def test_id_must_start_with_alnum(self) -> None:
        with self.assertRaises(ValueError):
            self._make(id="-bad-start")

    def test_thesis_too_short_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._make(thesis="Too short.")

    def test_add_connection_idempotent(self) -> None:
        cap = self._make()
        conn = CaptureConnection("test-cap-01", "other-cap", ConnectionKind.EXTENDS)
        cap.add_connection(conn)
        cap.add_connection(conn)  # second call should not duplicate
        self.assertEqual(len(cap.connections), 1)

    def test_keyword_set_normalised(self) -> None:
        cap = self._make(tags=["scaling", "Automation"])
        kws = cap.keyword_set()
        self.assertIn("scaling", kws)
        self.assertIn("automation", kws)
        # stop-word-length tokens excluded (len ≤ 2)
        for kw in kws:
            self.assertGreater(len(kw), 2)

    def test_to_dict_round_trip(self) -> None:
        cap = self._make(
            evidence_refs=["https://example.com/paper1"],
            tags=["scaling", "law"],
        )
        d = cap.to_dict()
        restored = ManufacturingTheoryCapture.from_dict(d)
        self.assertEqual(restored.id, cap.id)
        self.assertEqual(restored.thesis, cap.thesis)
        self.assertEqual(restored.domain, cap.domain)
        self.assertEqual(restored.evidence_refs, cap.evidence_refs)
        self.assertEqual(restored.maturity, cap.maturity)

    def test_default_created_date_is_set(self) -> None:
        cap = self._make()
        self.assertRegex(cap.created_date, r"^\d{4}-\d{2}-\d{2}$")

    def test_repr_contains_id(self) -> None:
        cap = self._make()
        self.assertIn("test-cap-01", repr(cap))


if __name__ == "__main__":
    unittest.main()
