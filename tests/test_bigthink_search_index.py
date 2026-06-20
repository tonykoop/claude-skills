#!/usr/bin/env python3
"""Tests for bigthink.search_index — SearchIndex inverted-index engine."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigthink.registry import CaptureRegistry
from bigthink.schema import Domain, ManufacturingTheoryCapture
from bigthink.search_index import SearchIndex
from bigthink.seed_corpus import build_seed_registry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_T_SCALING = (
    "Manufacturing capability scales with evaluated spatial complexity "
    "in a power-law relationship, empirically measured by MakerBench."
)
_T_MATERIALS = (
    "Planetary element inventory tracks crustal abundance and run-rates "
    "for resource-aware scarcity-penalty triage in hardware design."
)
_T_PIPELINE = (
    "Evolution pipeline automates PLM and DFM lifecycle for hardware "
    "prototype development via vendor broker and BOM management."
)


def _build_reg() -> CaptureRegistry:
    reg = CaptureRegistry()
    reg.add(ManufacturingTheoryCapture(
        id="cap-scaling", thesis=_T_SCALING,
        domain=Domain.SCALING_LAW, tags=["koop", "scaling"],
    ))
    reg.add(ManufacturingTheoryCapture(
        id="cap-materials", thesis=_T_MATERIALS,
        domain=Domain.MATERIALS, tags=["elements", "earth"],
    ))
    reg.add(ManufacturingTheoryCapture(
        id="cap-pipeline", thesis=_T_PIPELINE,
        domain=Domain.PLM_DFM, tags=["plm", "bom"],
    ))
    return reg


class TestSearchIndexBuild(unittest.TestCase):
    def test_build_from_registry(self) -> None:
        reg = _build_reg()
        idx = SearchIndex(reg)
        self.assertEqual(idx.capture_count(), 3)

    def test_token_count_positive(self) -> None:
        reg = _build_reg()
        idx = SearchIndex(reg)
        self.assertGreater(idx.token_count(), 0)

    def test_top_tokens_returns_list(self) -> None:
        reg = _build_reg()
        idx = SearchIndex(reg)
        top = idx.top_tokens(5)
        self.assertLessEqual(len(top), 5)
        for tok, freq in top:
            self.assertIsInstance(tok, str)
            self.assertIsInstance(freq, int)

    def test_empty_registry_builds_empty_index(self) -> None:
        idx = SearchIndex(CaptureRegistry())
        self.assertEqual(idx.token_count(), 0)
        self.assertEqual(idx.capture_count(), 0)


class TestSearchIndexSearch(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = _build_reg()
        self.idx = SearchIndex(self.reg)

    def test_search_exact_token(self) -> None:
        ids = self.idx.search_ids("koop")
        self.assertIn("cap-scaling", ids)

    def test_search_multi_token_and_semantics(self) -> None:
        # Both "koop" and "scaling" appear in cap-scaling
        ids = self.idx.search_ids("koop scaling")
        self.assertIn("cap-scaling", ids)
        self.assertNotIn("cap-materials", ids)

    def test_search_returns_nothing_for_unknown_token(self) -> None:
        ids = self.idx.search_ids("zzznomatch")
        self.assertEqual(ids, set())

    def test_search_any_or_semantics(self) -> None:
        # "koop" matches cap-scaling; "elements" matches cap-materials
        ids = self.idx.search_any("koop elements")
        self.assertIn("cap-scaling", ids)
        self.assertIn("cap-materials", ids)

    def test_search_domain_token_indexed(self) -> None:
        ids = self.idx.search_ids("materials")
        self.assertIn("cap-materials", ids)

    def test_search_with_registry_returns_captures(self) -> None:
        results = self.idx.search("koop", self.reg)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "cap-scaling")

    def test_search_with_no_registry_returns_empty(self) -> None:
        results = self.idx.search("koop")  # no registry passed
        self.assertEqual(results, [])

    def test_search_results_sorted_by_id(self) -> None:
        # "power" appears in cap-scaling thesis (power-law)
        # "law" is short (2 chars) so not indexed; use a longer shared token
        results = self.idx.search("the", self.reg)
        ids = [r.id for r in results]
        self.assertEqual(ids, sorted(ids))

    def test_empty_query_returns_nothing(self) -> None:
        ids = self.idx.search_ids("")
        self.assertEqual(ids, set())


class TestSearchIndexIncrementalUpdates(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = _build_reg()
        self.idx = SearchIndex(self.reg)

    def test_add_capture_makes_it_searchable(self) -> None:
        new_cap = ManufacturingTheoryCapture(
            id="cap-new", thesis=(
                "Xometry vendor broker integration provides instant-quote "
                "DFM API for automated trade-off cost analysis."
            ),
            domain=Domain.PLM_DFM, tags=["xometry", "vendor"],
        )
        self.reg.add(new_cap)
        self.idx.add_capture(new_cap)
        ids = self.idx.search_ids("xometry")
        self.assertIn("cap-new", ids)

    def test_remove_capture_removes_from_index(self) -> None:
        self.reg.remove("cap-scaling")
        self.idx.remove_capture("cap-scaling")
        ids = self.idx.search_ids("koop")
        self.assertNotIn("cap-scaling", ids)

    def test_rebuild_syncs_with_registry(self) -> None:
        new_cap = ManufacturingTheoryCapture(
            id="cap-rebuild",
            thesis="Automated spatial complexity measurement drives fabrication benchmark.",
            domain=Domain.SCALING_LAW,
        )
        self.reg.add(new_cap)
        self.idx.build(self.reg)  # full rebuild
        ids = self.idx.search_ids("benchmark")
        self.assertIn("cap-rebuild", ids)

    def test_capture_count_updates_after_add(self) -> None:
        before = self.idx.capture_count()
        new_cap = ManufacturingTheoryCapture(
            id="cap-count",
            thesis="Tolerance floor and kinematic cadence limits per process type.",
            domain=Domain.METROLOGY,
        )
        self.reg.add(new_cap)
        self.idx.add_capture(new_cap)
        self.assertEqual(self.idx.capture_count(), before + 1)

    def test_capture_count_updates_after_remove(self) -> None:
        before = self.idx.capture_count()
        self.reg.remove("cap-scaling")
        self.idx.remove_capture("cap-scaling")
        self.assertEqual(self.idx.capture_count(), before - 1)


class TestSearchIndexWithSeedCorpus(unittest.TestCase):
    def test_seed_corpus_indexed(self) -> None:
        reg = build_seed_registry()
        idx = SearchIndex(reg)
        # "spatial" appears in koops-law thesis
        ids = idx.search_ids("spatial")
        self.assertIn("koops-law-v1", ids)

    def test_planetary_found_by_element(self) -> None:
        reg = build_seed_registry()
        idx = SearchIndex(reg)
        ids = idx.search_ids("element")
        self.assertIn("planetary-index-v1", ids)

    def test_evolution_found_by_plm(self) -> None:
        reg = build_seed_registry()
        idx = SearchIndex(reg)
        ids = idx.search_ids("plm")
        self.assertIn("evolution-pipeline-v1", ids)


if __name__ == "__main__":
    unittest.main()
