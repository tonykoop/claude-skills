"""validator.py — Schema and business-rule validation for captures.

Validates a ManufacturingTheoryCapture in isolation, and can also
cross-validate a capture against a CaptureRegistry (e.g. dangling connection
targets, duplicate ids).

Validation results are accumulated into a ``ValidationResult`` so callers can
choose to raise, log, or display all errors at once.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from bigthink.schema import ManufacturingTheoryCapture, MaturityLevel

if TYPE_CHECKING:
    from bigthink.registry import CaptureRegistry


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """Accumulates errors and warnings from validation checks."""
    capture_id: str
    errors:   list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def raise_if_invalid(self) -> None:
        if not self.valid:
            formatted = "\n".join(f"  - {e}" for e in self.errors)
            raise ValueError(
                f"Capture {self.capture_id!r} is invalid:\n{formatted}"
            )

    def __str__(self) -> str:
        lines = [f"ValidationResult for {self.capture_id!r}:"]
        lines += [f"  ERROR:   {e}" for e in self.errors]
        lines += [f"  WARNING: {w}" for w in self.warnings]
        if self.valid and not self.warnings:
            lines.append("  OK — no issues found")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# CaptureValidator
# ---------------------------------------------------------------------------

# URL-like pattern for evidence refs (http/https or a repo path)
_URL_RE  = re.compile(r"^https?://\S+$")
_PATH_RE = re.compile(r"^[a-zA-Z0-9_./-]{3,}$")


class CaptureValidator:
    """Validates ManufacturingTheoryCapture objects against schema and rules.

    Two entry points:
      validate(capture)                   — standalone field checks
      validate_against(capture, registry) — cross-checks vs registry state
    """

    # ------------------------------------------------------------------
    # Primary API
    # ------------------------------------------------------------------

    def validate(self, capture: ManufacturingTheoryCapture) -> ValidationResult:
        """Run all standalone validation rules and return a ``ValidationResult``."""
        result = ValidationResult(capture_id=capture.id)
        self._check_id(capture, result)
        self._check_thesis(capture, result)
        self._check_evidence_refs(capture, result)
        self._check_connections_internal(capture, result)
        self._check_maturity_consistency(capture, result)
        self._check_dates(capture, result)
        return result

    def validate_against(
        self,
        capture: ManufacturingTheoryCapture,
        registry: "CaptureRegistry",
    ) -> ValidationResult:
        """Run standalone checks plus registry cross-validation."""
        result = self.validate(capture)
        self._check_registry_refs(capture, registry, result)
        self._check_duplicate_id(capture, registry, result)
        return result

    def validate_registry(
        self, registry: "CaptureRegistry"
    ) -> list[ValidationResult]:
        """Validate every capture in the registry, returning all results."""
        results = []
        all_ids = {c.id for c in registry}
        for capture in registry:
            result = ValidationResult(capture_id=capture.id)
            self._check_id(capture, result)
            self._check_thesis(capture, result)
            self._check_evidence_refs(capture, result)
            self._check_connections_internal(capture, result)
            self._check_maturity_consistency(capture, result)
            self._check_dates(capture, result)
            # Cross-check connection targets against the registry
            for conn in capture.connections:
                if conn.to_id not in all_ids:
                    result.error(
                        f"Connection target {conn.to_id!r} not found in registry"
                    )
            results.append(result)
        return results

    # ------------------------------------------------------------------
    # Individual rule checks
    # ------------------------------------------------------------------

    @staticmethod
    def _check_id(cap: ManufacturingTheoryCapture, r: ValidationResult) -> None:
        if not cap.id:
            r.error("id must not be empty")
        elif not re.match(r"^[a-z0-9][a-z0-9\-]{1,63}$", cap.id):
            r.error(
                f"id {cap.id!r} must be a lowercase slug "
                "(letters, digits, hyphens, length 2–64)"
            )

    @staticmethod
    def _check_thesis(cap: ManufacturingTheoryCapture, r: ValidationResult) -> None:
        text = cap.thesis.strip()
        word_count = len(text.split())
        if word_count < 10:
            r.error(f"thesis too short: {word_count} words (minimum 10)")
        if not text[0].isupper():
            r.warn("thesis should begin with a capital letter")
        if len(text) > 4000:
            r.warn("thesis is very long (>4000 chars); consider breaking into sub-captures")

    @staticmethod
    def _check_evidence_refs(cap: ManufacturingTheoryCapture, r: ValidationResult) -> None:
        seen: set[str] = set()
        for i, ref in enumerate(cap.evidence_refs):
            stripped = ref.strip()
            if not stripped:
                r.error(f"evidence_refs[{i}] is empty or whitespace-only")
                continue
            if stripped in seen:
                r.warn(f"Duplicate evidence ref at index {i}: {stripped!r}")
            seen.add(stripped)
            if not (_URL_RE.match(stripped) or _PATH_RE.match(stripped)):
                r.warn(
                    f"evidence_refs[{i}] does not look like a URL or path: {stripped!r}"
                )

    @staticmethod
    def _check_connections_internal(
        cap: ManufacturingTheoryCapture, r: ValidationResult
    ) -> None:
        seen: set[tuple[str, str, str]] = set()
        for i, conn in enumerate(cap.connections):
            key = (conn.from_id, conn.to_id, conn.kind.value)
            if key in seen:
                r.warn(f"Duplicate connection at index {i}: {conn}")
            seen.add(key)
            if conn.from_id == conn.to_id:
                r.error(f"Self-loop connection at index {i}")

    @staticmethod
    def _check_maturity_consistency(
        cap: ManufacturingTheoryCapture, r: ValidationResult
    ) -> None:
        m = cap.maturity
        if m == MaturityLevel.VALIDATED:
            if not cap.evidence_refs:
                r.error("validated captures must have at least one evidence_ref")
            if not cap.source.strip():
                r.error("validated captures must have a non-empty source field")
            if not cap.promotion_target.strip():
                r.warn("validated captures should have a promotion_target")
        elif m == MaturityLevel.DEVELOPING:
            if not cap.source.strip():
                r.warn("developing captures should have a source field")

    @staticmethod
    def _check_dates(cap: ManufacturingTheoryCapture, r: ValidationResult) -> None:
        date_str = cap.created_date
        if date_str:
            try:
                import datetime
                datetime.date.fromisoformat(date_str)
            except ValueError:
                r.error(f"created_date {date_str!r} is not a valid ISO date (YYYY-MM-DD)")

    @staticmethod
    def _check_registry_refs(
        cap: ManufacturingTheoryCapture,
        registry: "CaptureRegistry",
        r: ValidationResult,
    ) -> None:
        for conn in cap.connections:
            if conn.to_id not in registry:
                r.error(
                    f"Connection target {conn.to_id!r} is not in the registry"
                )

    @staticmethod
    def _check_duplicate_id(
        cap: ManufacturingTheoryCapture,
        registry: "CaptureRegistry",
        r: ValidationResult,
    ) -> None:
        if cap.id in registry:
            r.error(f"id {cap.id!r} already exists in registry")
