"""promotion_pipeline.py — End-to-end promotion audit and runner.

Provides two public entry points:

``PromotionAudit``
    Generates a read-only report on all captures in a registry:
    which are ready to advance, which are blocked and why, and
    a full breakdown by maturity level.

``PromotionPipeline``
    Executes a batch promotion run: advances every gate-passing capture
    one level and writes the results back into a registry.  Supports
    dry_run mode for preview.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from bigthink.maturity import MaturityModel
from bigthink.schema import ManufacturingTheoryCapture, MaturityLevel
from bigthink.validator import CaptureValidator

if TYPE_CHECKING:
    from bigthink.registry import CaptureRegistry


# ---------------------------------------------------------------------------
# PromotionAudit
# ---------------------------------------------------------------------------

@dataclass
class CaptureAuditEntry:
    """Audit result for a single capture."""
    capture_id:     str
    current_level:  MaturityLevel
    next_level:     MaturityLevel | None
    score:          float
    ready:          bool
    gaps:           list[str]
    warnings:       list[str]


@dataclass
class PromotionAuditReport:
    """Aggregate audit report for an entire registry.

    Attributes:
        entries:  One entry per capture.
        ready:    Captures ready to advance (no gaps).
        blocked:  Captures with at least one gap.
        at_top:   Captures already at VALIDATED (nothing to advance).
    """
    entries:  list[CaptureAuditEntry]

    @property
    def ready(self) -> list[CaptureAuditEntry]:
        return [e for e in self.entries if e.ready]

    @property
    def blocked(self) -> list[CaptureAuditEntry]:
        return [e for e in self.entries if not e.ready and e.next_level is not None]

    @property
    def at_top(self) -> list[CaptureAuditEntry]:
        return [e for e in self.entries if e.next_level is None]

    def summary(self) -> str:
        return (
            f"PromotionAudit: {len(self.entries)} captures — "
            f"{len(self.ready)} ready, "
            f"{len(self.blocked)} blocked, "
            f"{len(self.at_top)} at VALIDATED"
        )

    def report(self) -> str:
        """Human-readable multi-line report."""
        lines: list[str] = [self.summary(), ""]

        if self.ready:
            lines.append("=== READY TO ADVANCE ===")
            for e in self.ready:
                next_str = e.next_level.value if e.next_level else "—"
                lines.append(
                    f"  {e.capture_id:40s}  {e.current_level.value} → {next_str}"
                    f"  score={e.score:.0%}"
                )

        if self.blocked:
            lines.append("\n=== BLOCKED ===")
            for e in sorted(self.blocked, key=lambda x: x.score, reverse=True):
                next_str = e.next_level.value if e.next_level else "—"
                lines.append(
                    f"  {e.capture_id:40s}  → {next_str}  score={e.score:.0%}"
                )
                for gap in e.gaps:
                    lines.append(f"      GAP: {gap}")

        if self.at_top:
            lines.append("\n=== VALIDATED (top level) ===")
            for e in self.at_top:
                lines.append(f"  {e.capture_id}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# PromotionPipeline
# ---------------------------------------------------------------------------

@dataclass
class PromotionResult:
    """Result of a single promotion attempt."""
    capture_id:    str
    from_level:    MaturityLevel
    to_level:      MaturityLevel | None
    promoted:      bool
    skipped:       bool          # not ready — gaps exist
    error:         str           = ""

    @property
    def success(self) -> bool:
        return self.promoted


@dataclass
class BatchPromotionResult:
    """Aggregate result of a PromotionPipeline run."""
    results:  list[PromotionResult]
    dry_run:  bool

    @property
    def promoted(self) -> list[PromotionResult]:
        return [r for r in self.results if r.promoted]

    @property
    def skipped(self) -> list[PromotionResult]:
        return [r for r in self.results if r.skipped]

    @property
    def errors(self) -> list[PromotionResult]:
        return [r for r in self.results if r.error]

    def summary(self) -> str:
        mode = "DRY-RUN" if self.dry_run else "RUN"
        return (
            f"[{mode}] Promotion: "
            f"{len(self.promoted)} promoted, "
            f"{len(self.skipped)} skipped, "
            f"{len(self.errors)} errors"
        )


class PromotionPipeline:
    """Batch promotion runner.

    Usage::

        pipeline = PromotionPipeline()
        audit = pipeline.audit(registry)
        print(audit.report())

        result = pipeline.run(registry)          # advance all ready captures
        result = pipeline.run(registry, dry_run=True)  # preview only
    """

    def __init__(self) -> None:
        self._model    = MaturityModel()
        self._validator = CaptureValidator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def audit(self, registry: "CaptureRegistry") -> PromotionAuditReport:
        """Generate a read-only audit report for all captures in ``registry``."""
        entries: list[CaptureAuditEntry] = []
        for cap in registry:
            ms = self._model.score(cap)
            # Collect warnings from the validator too
            vr = self._validator.validate(cap)
            entries.append(CaptureAuditEntry(
                capture_id=cap.id,
                current_level=cap.maturity,
                next_level=ms.next_level,
                score=ms.score,
                ready=ms.is_promotion_ready,
                gaps=ms.gap,
                warnings=vr.warnings,
            ))
        return PromotionAuditReport(entries=entries)

    def run(
        self,
        registry: "CaptureRegistry",
        *,
        dry_run: bool = False,
        capture_ids: list[str] | None = None,
    ) -> BatchPromotionResult:
        """Advance all gate-passing captures one maturity level.

        Args:
            dry_run:     If True, compute promotions but do not mutate registry.
            capture_ids: If supplied, restrict to this subset of ids.
                         Defaults to all captures in the registry.

        Returns:
            ``BatchPromotionResult`` with per-capture outcomes.
        """
        target_ids: set[str] = (
            set(capture_ids) if capture_ids is not None
            else {cap.id for cap in registry}
        )

        results: list[PromotionResult] = []
        to_replace: list[tuple[str, ManufacturingTheoryCapture]] = []

        for cap in list(registry):
            if cap.id not in target_ids:
                continue

            ms = self._model.score(cap)
            if ms.next_level is None:
                # Already validated — intentional skip, not an error
                results.append(PromotionResult(
                    capture_id=cap.id,
                    from_level=cap.maturity,
                    to_level=None,
                    promoted=False,
                    skipped=True,
                    error="",  # empty: this is expected, not a failure
                ))
                continue

            if not ms.is_promotion_ready:
                results.append(PromotionResult(
                    capture_id=cap.id,
                    from_level=cap.maturity,
                    to_level=ms.next_level,
                    promoted=False,
                    skipped=True,
                ))
                continue

            try:
                advanced = self._model.advance(cap)
                to_replace.append((cap.id, advanced))
                results.append(PromotionResult(
                    capture_id=cap.id,
                    from_level=cap.maturity,
                    to_level=advanced.maturity,
                    promoted=not dry_run,
                    skipped=False,
                ))
            except ValueError as exc:
                results.append(PromotionResult(
                    capture_id=cap.id,
                    from_level=cap.maturity,
                    to_level=ms.next_level,
                    promoted=False,
                    skipped=False,
                    error=str(exc),
                ))

        # Commit changes outside the loop
        if not dry_run:
            for old_id, advanced in to_replace:
                registry.remove(old_id)
                registry.add(advanced)

        return BatchPromotionResult(results=results, dry_run=dry_run)
