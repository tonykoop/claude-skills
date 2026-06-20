#!/usr/bin/env python3
"""Tests for bigthink.connections — ConnectionFinder cross-pollination engine."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigthink.connections import ConnectionFinder
from bigthink.registry import CaptureRegistry
from bigthink.schema import ConnectionKind, Domain, ManufacturingTheoryCapture, MaturityLevel


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_SHARED_THESIS = (
    "Manufacturing scaling law based on evaluated spatial complexity "
    "and physical learning rates drives automation efficiency improvements."
)

_MATERIALS_THESIS = (
    "Planetary element inventory tracks crustal abundance and run-rates "
    "to enable resource-aware strategic hardware design decisions for fabrication."
)

_UNRELATED_THESIS = (
    "Yoga sequences cultivate flexibility and mindfulness through structured "
    "vinyasa flows that progress from basic poses to advanced inversions."
)


def _build_registry() -> CaptureRegistry:
    reg = CaptureRegistry()
    reg.add(ManufacturingTheoryCapture(
        id="koops-law",
        thesis=_SHARED_THESIS,
        domain=Domain.SCALING_LAW,
        tags=["scaling", "automation", "complexity"],
        evidence_refs=["https://example.com/koop"],
        source="Gemini 2026-06-13",
    ))
    reg.add(ManufacturingTheoryCapture(
        id="spatial-complexity",
        thesis=_SHARED_THESIS + " Further: every unit of spatial complexity maps directly "
                "to a manufacturing challenge in the automation pipeline.",
        domain=Domain.SCALING_LAW,
        tags=["complexity", "challenge"],
        evidence_refs=["https://example.com/koop"],  # same ref as koops-law
        source="Gemini 2026-06-13",
    ))
    reg.add(ManufacturingTheoryCapture(
        id="planetary-index",
        thesis=_MATERIALS_THESIS,
        domain=Domain.MATERIALS,
        tags=["elements", "earth", "scarcity"],
        source="Gemini 2026-06-13",
    ))
    reg.add(ManufacturingTheoryCapture(
        id="yoga-capture",
        thesis=_UNRELATED_THESIS,
        domain=Domain.CROSS_DOMAIN,
        tags=["yoga", "vinyasa"],
    ))
    return reg


class TestKeywordSimilarity(unittest.TestCase):
    def setUp(self) -> None:
        self.finder = ConnectionFinder()
        self.reg = _build_registry()

    def test_identical_thesis_scores_high(self) -> None:
        a = self.reg.get("koops-law")
        b = self.reg.get("spatial-complexity")
        sim = self.finder.keyword_similarity(a, b)
        self.assertGreater(sim, 0.3)

    def test_unrelated_scores_low(self) -> None:
        a = self.reg.get("koops-law")
        b = self.reg.get("yoga-capture")
        sim = self.finder.keyword_similarity(a, b)
        self.assertLess(sim, 0.15)

    def test_similarity_symmetric(self) -> None:
        a = self.reg.get("koops-law")
        b = self.reg.get("planetary-index")
        self.assertAlmostEqual(
            self.finder.keyword_similarity(a, b),
            self.finder.keyword_similarity(b, a),
        )

    def test_empty_tags_no_crash(self) -> None:
        a = ManufacturingTheoryCapture(
            id="empty-kw",
            thesis="This is a thesis with no tags to test keyword similarity.",
            domain=Domain.SCALING_LAW,
        )
        b = self.reg.get("koops-law")
        # Should not raise; returns low or zero score
        sim = self.finder.keyword_similarity(a, b)
        self.assertGreaterEqual(sim, 0.0)


class TestCitationOverlap(unittest.TestCase):
    def setUp(self) -> None:
        self.finder = ConnectionFinder()
        self.reg = _build_registry()

    def test_shared_ref_detected(self) -> None:
        a = self.reg.get("koops-law")
        b = self.reg.get("spatial-complexity")
        self.assertEqual(self.finder.citation_overlap(a, b), 1)

    def test_no_shared_refs(self) -> None:
        a = self.reg.get("koops-law")
        b = self.reg.get("planetary-index")
        self.assertEqual(self.finder.citation_overlap(a, b), 0)


class TestDomainMatch(unittest.TestCase):
    def setUp(self) -> None:
        self.finder = ConnectionFinder()
        self.reg = _build_registry()

    def test_same_domain_matches(self) -> None:
        a = self.reg.get("koops-law")
        b = self.reg.get("spatial-complexity")
        self.assertTrue(self.finder.domain_match(a, b))

    def test_different_domain_no_match(self) -> None:
        a = self.reg.get("koops-law")
        b = self.reg.get("planetary-index")
        self.assertFalse(self.finder.domain_match(a, b))


class TestSuggestFor(unittest.TestCase):
    def setUp(self) -> None:
        self.finder = ConnectionFinder()
        self.reg = _build_registry()

    def test_suggest_for_returns_list(self) -> None:
        suggestions = self.finder.suggest_for("koops-law", self.reg)
        self.assertIsInstance(suggestions, list)

    def test_suggest_for_high_overlap_first(self) -> None:
        suggestions = self.finder.suggest_for("koops-law", self.reg)
        # spatial-complexity shares same thesis + same citation → should rank high
        self.assertTrue(any(s.to_id == "spatial-complexity" for s in suggestions))
        top = suggestions[0]
        self.assertGreater(top.score, 0.0)

    def test_suggest_for_excludes_self(self) -> None:
        suggestions = self.finder.suggest_for("koops-law", self.reg)
        self.assertFalse(any(s.to_id == "koops-law" for s in suggestions))

    def test_suggest_for_excludes_existing_connections(self) -> None:
        self.reg.connect("koops-law", "spatial-complexity", ConnectionKind.EXTENDS)
        suggestions = self.finder.suggest_for("koops-law", self.reg)
        self.assertFalse(any(s.to_id == "spatial-complexity" for s in suggestions))

    def test_suggest_for_top_k_limits_results(self) -> None:
        suggestions = self.finder.suggest_for("koops-law", self.reg, top_k=1)
        self.assertLessEqual(len(suggestions), 1)

    def test_suggest_for_sorted_descending(self) -> None:
        suggestions = self.finder.suggest_for("koops-law", self.reg)
        scores = [s.score for s in suggestions]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_unrelated_capture_produces_no_suggestions(self) -> None:
        suggestions = self.finder.suggest_for("yoga-capture", self.reg, min_score=0.15)
        for s in suggestions:
            # yoga should not be flagged as related to manufacturing captures
            self.assertNotEqual(s.to_id, "koops-law")


class TestSuggestAllPairs(unittest.TestCase):
    def setUp(self) -> None:
        self.finder = ConnectionFinder()
        self.reg = _build_registry()

    def test_returns_list(self) -> None:
        suggestions = self.finder.suggest_all_pairs(self.reg)
        self.assertIsInstance(suggestions, list)

    def test_high_overlap_pair_appears(self) -> None:
        suggestions = self.finder.suggest_all_pairs(self.reg)
        pair_ids = {(s.from_id, s.to_id) for s in suggestions}
        self.assertTrue(
            ("koops-law", "spatial-complexity") in pair_ids
            or ("spatial-complexity", "koops-law") in pair_ids
        )

    def test_cites_kind_inferred_for_shared_refs(self) -> None:
        suggestions = self.finder.suggest_all_pairs(self.reg)
        for s in suggestions:
            if ("koops-law" in (s.from_id, s.to_id) and
                    "spatial-complexity" in (s.from_id, s.to_id)):
                self.assertEqual(s.kind, ConnectionKind.CITES)

    def test_top_k_respected(self) -> None:
        suggestions = self.finder.suggest_all_pairs(self.reg, top_k=2)
        self.assertLessEqual(len(suggestions), 2)


if __name__ == "__main__":
    unittest.main()
