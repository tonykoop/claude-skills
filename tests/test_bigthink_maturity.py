#!/usr/bin/env python3
"""Tests for bigthink.maturity — MaturityModel stage gates and scoring."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigthink.maturity import MaturityModel, STAGE_GATES
from bigthink.schema import Domain, ManufacturingTheoryCapture, MaturityLevel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SEED_THESIS = (
    "This is a minimal seed-level thesis describing a raw manufacturing idea "
    "that has not yet been refined or supported by evidence."
)

_LONG_THESIS = (
    "Manufacturing capability scales with a power-law function of evaluated "
    "spatial complexity. Every doubling of programmatically-graded geometric "
    "variations accelerates multi-material manufacturing automation by a fixed "
    "efficiency percentage, empirically measured by the MakerBench fitness "
    "function and mapped onto the Kardashev civilizational framing."
)


def make_seed(id_: str = "test-seed") -> ManufacturingTheoryCapture:
    return ManufacturingTheoryCapture(id=id_, thesis=_SEED_THESIS, domain=Domain.SCALING_LAW)


def make_developing(id_: str = "test-dev") -> ManufacturingTheoryCapture:
    return ManufacturingTheoryCapture(
        id=id_,
        thesis=_LONG_THESIS,
        domain=Domain.SCALING_LAW,
        maturity=MaturityLevel.DEVELOPING,
        evidence_refs=["https://example.com/paper1"],
        source="Gemini conversation 2026-06-13",
    )


def make_validated(id_: str = "test-val") -> ManufacturingTheoryCapture:
    from bigthink.schema import CaptureConnection, ConnectionKind
    cap = ManufacturingTheoryCapture(
        id=id_,
        thesis=_LONG_THESIS,
        domain=Domain.SCALING_LAW,
        maturity=MaturityLevel.VALIDATED,
        evidence_refs=[
            "https://example.com/paper1",
            "https://example.com/paper2",
            "https://example.com/paper3",
        ],
        source="Gemini conversation 2026-06-13",
        promotion_target="makerbench-hwe/docs/RFC",
    )
    conn = CaptureConnection(id_, "other-cap", "supports")
    cap.connections.append(conn)
    return cap


class TestStageGates(unittest.TestCase):
    def test_seed_gate_zero_evidence(self) -> None:
        gate = STAGE_GATES[MaturityLevel.SEED]
        self.assertEqual(gate.min_evidence_refs, 0)

    def test_developing_gate_one_evidence(self) -> None:
        gate = STAGE_GATES[MaturityLevel.DEVELOPING]
        self.assertEqual(gate.min_evidence_refs, 1)
        self.assertTrue(gate.requires_source)

    def test_validated_gate_three_evidence_and_connection(self) -> None:
        gate = STAGE_GATES[MaturityLevel.VALIDATED]
        self.assertEqual(gate.min_evidence_refs, 3)
        self.assertEqual(gate.min_connections, 1)
        self.assertTrue(gate.requires_promotion_target)


class TestMaturityModelScore(unittest.TestCase):
    def setUp(self) -> None:
        self.model = MaturityModel()

    def test_seed_scores_below_one(self) -> None:
        cap = make_seed()
        ms = self.model.score(cap)
        self.assertLess(ms.score, 1.0)
        self.assertEqual(ms.current_level, MaturityLevel.SEED)
        self.assertEqual(ms.next_level, MaturityLevel.DEVELOPING)

    def test_seed_without_evidence_has_gap(self) -> None:
        cap = make_seed()
        ms = self.model.score(cap)
        gap_text = " ".join(ms.gap)
        self.assertIn("evidence_ref", gap_text)

    def test_developing_has_developing_gaps(self) -> None:
        # A developing-maturity capture that lacks some validated requirements
        cap = make_developing()
        ms = self.model.score(cap)
        self.assertEqual(ms.current_level, MaturityLevel.DEVELOPING)
        self.assertEqual(ms.next_level, MaturityLevel.VALIDATED)
        # Should flag missing evidence refs (need 3, have 1)
        gap_text = " ".join(ms.gap)
        self.assertIn("evidence_ref", gap_text)

    def test_validated_scores_one(self) -> None:
        cap = make_validated()
        ms = self.model.score(cap)
        self.assertAlmostEqual(ms.score, 1.0)
        self.assertIsNone(ms.next_level)
        self.assertEqual(ms.gap, [])
        self.assertTrue(ms.is_promotion_ready is False)  # already at top

    def test_score_str_contains_level(self) -> None:
        cap = make_seed()
        ms = self.model.score(cap)
        self.assertIn("seed", str(ms))


class TestMaturityModelAdvance(unittest.TestCase):
    def setUp(self) -> None:
        self.model = MaturityModel()

    def test_advance_seed_to_developing(self) -> None:
        # Build a capture that meets developing gate
        cap = ManufacturingTheoryCapture(
            id="ready-seed",
            thesis=_LONG_THESIS,
            domain=Domain.SCALING_LAW,
            evidence_refs=["https://example.com/paper"],
            source="some source",
        )
        advanced = self.model.advance(cap)
        self.assertEqual(advanced.maturity, MaturityLevel.DEVELOPING)

    def test_advance_fails_when_gaps_exist(self) -> None:
        cap = make_seed()  # no evidence, no source
        with self.assertRaises(ValueError):
            self.model.advance(cap)

    def test_advance_validated_raises(self) -> None:
        cap = make_validated()
        with self.assertRaises(ValueError):
            self.model.advance(cap)

    def test_advance_is_non_destructive(self) -> None:
        """Original capture should not be mutated."""
        cap = ManufacturingTheoryCapture(
            id="immutable-cap",
            thesis=_LONG_THESIS,
            domain=Domain.SCALING_LAW,
            evidence_refs=["https://example.com/paper"],
            source="some source",
        )
        advanced = self.model.advance(cap)
        self.assertEqual(cap.maturity, MaturityLevel.SEED)  # unchanged
        self.assertEqual(advanced.maturity, MaturityLevel.DEVELOPING)


class TestMaturityModelCandidates(unittest.TestCase):
    def setUp(self) -> None:
        self.model = MaturityModel()

    def test_promotion_candidates_excludes_seed_without_evidence(self) -> None:
        seed = make_seed()
        candidates = self.model.promotion_candidates([seed])
        self.assertNotIn(seed, candidates)

    def test_promotion_candidates_includes_gate_passing_seed(self) -> None:
        cap = ManufacturingTheoryCapture(
            id="pass-seed",
            thesis=_LONG_THESIS,
            domain=Domain.SCALING_LAW,
            evidence_refs=["https://example.com/paper"],
            source="some source",
        )
        candidates = self.model.promotion_candidates([cap])
        self.assertIn(cap, candidates)

    def test_promotion_candidates_empty_on_all_validated(self) -> None:
        cap = make_validated()
        candidates = self.model.promotion_candidates([cap])
        self.assertEqual(candidates, [])


if __name__ == "__main__":
    unittest.main()
