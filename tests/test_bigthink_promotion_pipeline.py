#!/usr/bin/env python3
"""Tests for bigthink.promotion_pipeline — PromotionAudit and PromotionPipeline."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigthink.promotion_pipeline import (
    BatchPromotionResult,
    PromotionAuditReport,
    PromotionPipeline,
)
from bigthink.registry import CaptureRegistry
from bigthink.schema import Domain, ManufacturingTheoryCapture, MaturityLevel


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_LONG_THESIS = (
    "Manufacturing capability scales with evaluated spatial complexity "
    "in a power-law relationship where each doubling of programmatically "
    "graded geometric variations accelerates multi-material manufacturing "
    "automation by a fixed efficiency percentage, empirically measured "
    "by the MakerBench hardware evaluation benchmark."
)

_SHORT_THESIS = (
    "This is a minimal thesis for a seed-level capture that does not "
    "meet the developing gate requirements yet."
)

_VALIDATED_THESIS = (
    "Manufacturing capability scales with a power-law function of evaluated "
    "spatial complexity that is precisely measurable. Every doubling of "
    "programmatically-graded, physically-verified geometric variations accelerates "
    "multi-material manufacturing automation by a fixed efficiency percentage, "
    "empirically measured by the MakerBench hardware evaluation benchmark "
    "fitness function and mapped onto the Kardashev civilizational scale "
    "from Type 0 toward Type I and beyond as intelligence explodes physically."
)


def _make_promotable_seed(id_: str = "ready-seed") -> ManufacturingTheoryCapture:
    """A seed capture that passes the developing gate."""
    return ManufacturingTheoryCapture(
        id=id_,
        thesis=_LONG_THESIS,
        domain=Domain.SCALING_LAW,
        evidence_refs=["https://example.com/paper1"],
        source="Gemini 2026-06-13",
    )


def _make_blocked_seed(id_: str = "blocked-seed") -> ManufacturingTheoryCapture:
    """A seed capture that does NOT pass the developing gate (missing evidence+source)."""
    return ManufacturingTheoryCapture(
        id=id_,
        thesis=_SHORT_THESIS,
        domain=Domain.SCALING_LAW,
    )


def _make_validated(id_: str = "validated-cap") -> ManufacturingTheoryCapture:
    """A VALIDATED capture (already at top level)."""
    from bigthink.schema import CaptureConnection
    cap = ManufacturingTheoryCapture(
        id=id_,
        thesis=_VALIDATED_THESIS,
        domain=Domain.SCALING_LAW,
        maturity=MaturityLevel.VALIDATED,
        evidence_refs=[
            "https://example.com/p1",
            "https://example.com/p2",
            "https://example.com/p3",
        ],
        source="Gemini 2026-06-13",
        promotion_target="makerbench-hwe/docs/RFC",
    )
    cap.connections.append(CaptureConnection(id_, "other", "supports"))
    return cap


# ---------------------------------------------------------------------------
# Audit tests
# ---------------------------------------------------------------------------

class TestPromotionAudit(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = PromotionPipeline()
        self.reg = CaptureRegistry()

    def test_audit_returns_report(self) -> None:
        self.reg.add(_make_promotable_seed())
        report = self.pipeline.audit(self.reg)
        self.assertIsInstance(report, PromotionAuditReport)

    def test_ready_capture_appears_in_ready(self) -> None:
        self.reg.add(_make_promotable_seed())
        report = self.pipeline.audit(self.reg)
        ready_ids = {e.capture_id for e in report.ready}
        self.assertIn("ready-seed", ready_ids)

    def test_blocked_capture_appears_in_blocked(self) -> None:
        self.reg.add(_make_blocked_seed())
        report = self.pipeline.audit(self.reg)
        blocked_ids = {e.capture_id for e in report.blocked}
        self.assertIn("blocked-seed", blocked_ids)

    def test_validated_capture_appears_in_at_top(self) -> None:
        self.reg.add(_make_validated())
        report = self.pipeline.audit(self.reg)
        top_ids = {e.capture_id for e in report.at_top}
        self.assertIn("validated-cap", top_ids)

    def test_audit_entry_has_score(self) -> None:
        self.reg.add(_make_promotable_seed())
        report = self.pipeline.audit(self.reg)
        for entry in report.entries:
            self.assertGreaterEqual(entry.score, 0.0)
            self.assertLessEqual(entry.score, 1.0)

    def test_blocked_entry_has_gaps(self) -> None:
        self.reg.add(_make_blocked_seed())
        report = self.pipeline.audit(self.reg)
        blocked = report.blocked
        self.assertGreater(len(blocked[0].gaps), 0)

    def test_summary_contains_counts(self) -> None:
        self.reg.add(_make_promotable_seed())
        self.reg.add(_make_blocked_seed())
        report = self.pipeline.audit(self.reg)
        summary = report.summary()
        self.assertIn("1 ready", summary)
        self.assertIn("1 blocked", summary)

    def test_report_text_contains_section_headers(self) -> None:
        self.reg.add(_make_promotable_seed())
        self.reg.add(_make_blocked_seed())
        text = self.pipeline.audit(self.reg).report()
        self.assertIn("READY TO ADVANCE", text)
        self.assertIn("BLOCKED", text)

    def test_empty_registry_audit(self) -> None:
        report = self.pipeline.audit(self.reg)
        self.assertEqual(len(report.entries), 0)
        self.assertEqual(report.ready, [])
        self.assertEqual(report.blocked, [])


# ---------------------------------------------------------------------------
# Pipeline run tests
# ---------------------------------------------------------------------------

class TestPromotionPipelineRun(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = PromotionPipeline()

    def _make_reg(self, *caps: ManufacturingTheoryCapture) -> CaptureRegistry:
        reg = CaptureRegistry()
        for cap in caps:
            reg.add(cap)
        return reg

    def test_run_advances_ready_capture(self) -> None:
        reg = self._make_reg(_make_promotable_seed())
        result = self.pipeline.run(reg)
        self.assertEqual(len(result.promoted), 1)
        cap = reg.get("ready-seed")
        self.assertEqual(cap.maturity, MaturityLevel.DEVELOPING)

    def test_run_skips_blocked_capture(self) -> None:
        reg = self._make_reg(_make_blocked_seed())
        result = self.pipeline.run(reg)
        self.assertEqual(len(result.skipped), 1)
        cap = reg.get("blocked-seed")
        self.assertEqual(cap.maturity, MaturityLevel.SEED)  # unchanged

    def test_run_skips_validated_capture(self) -> None:
        reg = self._make_reg(_make_validated())
        result = self.pipeline.run(reg)
        skipped = {r.capture_id for r in result.skipped}
        self.assertIn("validated-cap", skipped)

    def test_dry_run_does_not_mutate_registry(self) -> None:
        reg = self._make_reg(_make_promotable_seed())
        result = self.pipeline.run(reg, dry_run=True)
        self.assertTrue(result.dry_run)
        cap = reg.get("ready-seed")
        self.assertEqual(cap.maturity, MaturityLevel.SEED)  # unchanged

    def test_dry_run_reports_promoted_count(self) -> None:
        reg = self._make_reg(_make_promotable_seed())
        result = self.pipeline.run(reg, dry_run=True)
        # Even in dry-run, the count is reported (but not committed)
        self.assertEqual(len(result.promoted), 0)  # dry_run → not actually promoted
        # However, the result should not be empty
        self.assertEqual(len(result.results), 1)

    def test_run_with_capture_ids_subset(self) -> None:
        reg = self._make_reg(
            _make_promotable_seed("ready-a"),
            _make_promotable_seed("ready-b"),
        )
        result = self.pipeline.run(reg, capture_ids=["ready-a"])
        promoted_ids = {r.capture_id for r in result.promoted}
        self.assertIn("ready-a", promoted_ids)
        self.assertNotIn("ready-b", promoted_ids)
        # ready-b should remain SEED
        self.assertEqual(reg.get("ready-b").maturity, MaturityLevel.SEED)

    def test_batch_summary_contains_mode(self) -> None:
        reg = self._make_reg(_make_promotable_seed())
        r_live = self.pipeline.run(reg)
        r_dry  = self.pipeline.run(CaptureRegistry(), dry_run=True)
        self.assertIn("RUN", r_live.summary())
        self.assertIn("DRY-RUN", r_dry.summary())

    def test_run_mixed_batch(self) -> None:
        reg = self._make_reg(
            _make_promotable_seed("ready-1"),
            _make_blocked_seed("blocked-1"),
            _make_validated("top-1"),
        )
        result = self.pipeline.run(reg)
        self.assertEqual(len(result.promoted), 1)
        self.assertEqual(len(result.skipped), 2)
        self.assertEqual(len(result.errors), 0)


# ---------------------------------------------------------------------------
# End-to-end full lifecycle test
# ---------------------------------------------------------------------------

class TestFullPromotionLifecycle(unittest.TestCase):
    """Walk a capture from SEED → DEVELOPING → VALIDATED via the pipeline."""

    def test_end_to_end_lifecycle(self) -> None:
        reg = CaptureRegistry()
        pipeline = PromotionPipeline()

        # --- Stage 1: SEED ---
        seed_cap = ManufacturingTheoryCapture(
            id="lifecycle-cap",
            thesis=_LONG_THESIS,
            domain=Domain.SCALING_LAW,
            evidence_refs=["https://example.com/paper1"],
            source="Gemini 2026-06-13",
        )
        reg.add(seed_cap)
        self.assertEqual(reg.get("lifecycle-cap").maturity, MaturityLevel.SEED)

        # Audit: should be ready
        audit1 = pipeline.audit(reg)
        self.assertEqual(len(audit1.ready), 1)

        # Run: advance to DEVELOPING
        result1 = pipeline.run(reg)
        self.assertEqual(len(result1.promoted), 1)
        self.assertEqual(reg.get("lifecycle-cap").maturity, MaturityLevel.DEVELOPING)

        # --- Stage 2: DEVELOPING → VALIDATED ---
        # Enrich the capture to pass the validated gate
        dev_cap = reg.get("lifecycle-cap")
        reg.remove("lifecycle-cap")

        # Add more peers for the connection gate
        peer = ManufacturingTheoryCapture(
            id="peer-cap",
            thesis="Companion theory that relates to lifecycle capture evidence.",
            domain=Domain.SCALING_LAW,
        )
        reg.add(peer)

        import copy
        from bigthink.schema import CaptureConnection
        validated_cap = ManufacturingTheoryCapture(
            id="lifecycle-cap",
            thesis=_VALIDATED_THESIS,
            domain=Domain.SCALING_LAW,
            maturity=MaturityLevel.DEVELOPING,
            evidence_refs=[
                "https://example.com/p1",
                "https://example.com/p2",
                "https://example.com/p3",
            ],
            source="Gemini 2026-06-13",
            promotion_target="makerbench-hwe/docs/RFC",
            connections=[
                CaptureConnection("lifecycle-cap", "peer-cap", "supports")
            ],
        )
        reg.add(validated_cap)

        audit2 = pipeline.audit(reg)
        # lifecycle-cap should now be ready to advance to VALIDATED
        ready_ids = {e.capture_id for e in audit2.ready}
        self.assertIn("lifecycle-cap", ready_ids)

        result2 = pipeline.run(reg, capture_ids=["lifecycle-cap"])
        self.assertEqual(len(result2.promoted), 1)
        self.assertEqual(reg.get("lifecycle-cap").maturity, MaturityLevel.VALIDATED)

        # Audit: lifecycle-cap is now at top
        audit3 = pipeline.audit(reg)
        top_ids = {e.capture_id for e in audit3.at_top}
        self.assertIn("lifecycle-cap", top_ids)


if __name__ == "__main__":
    unittest.main()
