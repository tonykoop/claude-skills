"""maturity.py — Maturity progression model for manufacturing theory captures.

Defines the *rules* for advancing a capture through the three stages:
  seed → developing → validated

Each stage has a minimum bar expressed in evidence count and keyword coverage.
The model is deliberately structural (no magic thresholds from thin air) so
it can be unit-tested and adjusted without touching business logic elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from bigthink.schema import MaturityLevel

if TYPE_CHECKING:
    from bigthink.schema import ManufacturingTheoryCapture


# ---------------------------------------------------------------------------
# Stage gate rules
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StageGate:
    """Conditions that must hold for a capture to reach this maturity level."""
    level:              MaturityLevel
    min_evidence_refs:  int     # minimum number of evidence_refs entries
    min_thesis_words:   int     # minimum word-count in thesis
    requires_source:    bool    # source field must be non-empty
    min_connections:    int     # minimum connections to other captures
    requires_promotion_target: bool  # promotion_target must be set


# Canonical gate definitions — adjust here to tune the model
STAGE_GATES: dict[MaturityLevel, StageGate] = {
    MaturityLevel.SEED: StageGate(
        level=MaturityLevel.SEED,
        min_evidence_refs=0,
        min_thesis_words=10,
        requires_source=False,
        min_connections=0,
        requires_promotion_target=False,
    ),
    MaturityLevel.DEVELOPING: StageGate(
        level=MaturityLevel.DEVELOPING,
        min_evidence_refs=1,
        min_thesis_words=30,
        requires_source=True,
        min_connections=0,
        requires_promotion_target=False,
    ),
    MaturityLevel.VALIDATED: StageGate(
        level=MaturityLevel.VALIDATED,
        min_evidence_refs=3,
        min_thesis_words=50,
        requires_source=True,
        min_connections=1,
        requires_promotion_target=True,
    ),
}


# ---------------------------------------------------------------------------
# MaturityScore — a scored assessment of a single capture
# ---------------------------------------------------------------------------

@dataclass
class MaturityScore:
    """Numeric assessment of how far a capture has progressed.

    score (0.0 – 1.0):
      0.0 = bare seed
      1.0 = fully validated, gate-passing
    """
    score:          float
    current_level:  MaturityLevel
    next_level:     MaturityLevel | None
    gap:            list[str]       # human-readable list of what's missing
    evidence_count: int
    word_count:     int
    connection_count: int

    @property
    def is_promotion_ready(self) -> bool:
        """True when the capture meets every gate for the next level."""
        return len(self.gap) == 0 and self.next_level is not None

    def __str__(self) -> str:
        next_str = self.next_level.value if self.next_level else "—"
        gap_str  = "; ".join(self.gap) if self.gap else "none"
        return (
            f"MaturityScore(level={self.current_level.value}, "
            f"next={next_str}, score={self.score:.2f}, gaps=[{gap_str}])"
        )


# ---------------------------------------------------------------------------
# MaturityModel
# ---------------------------------------------------------------------------

class MaturityModel:
    """Stateless engine that scores and advances captures through stage gates.

    Usage::

        model = MaturityModel()
        score = model.score(capture)
        if score.is_promotion_ready:
            new_capture = model.advance(capture)
    """

    def score(self, capture: "ManufacturingTheoryCapture") -> MaturityScore:
        """Evaluate how close ``capture`` is to passing its *next* stage gate.

        Returns a ``MaturityScore`` with a normalised 0-1 float and a gap list
        describing exactly what is missing.
        """
        current = capture.maturity
        next_levels = [l for l in MaturityLevel if l.rank == current.rank + 1]
        next_level  = next_levels[0] if next_levels else None

        evidence_count   = len(capture.evidence_refs)
        word_count       = len(capture.thesis.split())
        connection_count = len(capture.connections)

        gap: list[str] = []

        if next_level is not None:
            gate = STAGE_GATES[next_level]

            if evidence_count < gate.min_evidence_refs:
                missing = gate.min_evidence_refs - evidence_count
                gap.append(f"need {missing} more evidence_ref(s) (have {evidence_count})")

            if word_count < gate.min_thesis_words:
                missing = gate.min_thesis_words - word_count
                gap.append(f"thesis needs {missing} more words (has {word_count})")

            if gate.requires_source and not capture.source.strip():
                gap.append("source field must be non-empty")

            if connection_count < gate.min_connections:
                missing = gate.min_connections - connection_count
                gap.append(f"need {missing} more connection(s) to other captures")

            if gate.requires_promotion_target and not capture.promotion_target.strip():
                gap.append("promotion_target must be set")

        # Compute a score proportional to gate requirements
        score_components = self._score_components(capture, next_level)
        score = min(1.0, sum(score_components) / max(len(score_components), 1))

        return MaturityScore(
            score=score,
            current_level=current,
            next_level=next_level,
            gap=gap,
            evidence_count=evidence_count,
            word_count=word_count,
            connection_count=connection_count,
        )

    def advance(self, capture: "ManufacturingTheoryCapture") -> "ManufacturingTheoryCapture":
        """Return a copy of ``capture`` with maturity advanced one level.

        Raises ``ValueError`` if the capture does not meet the next gate
        or is already at ``validated``.
        """
        ms = self.score(capture)
        if ms.next_level is None:
            raise ValueError(f"Capture {capture.id!r} is already at VALIDATED; cannot advance.")
        if ms.gap:
            raise ValueError(
                f"Capture {capture.id!r} cannot advance to {ms.next_level.value}: "
                + "; ".join(ms.gap)
            )

        # Return a new object with incremented maturity
        import copy
        advanced = copy.deepcopy(capture)
        advanced.maturity = ms.next_level
        return advanced

    def promotion_candidates(
        self,
        captures: "list[ManufacturingTheoryCapture]",
    ) -> "list[ManufacturingTheoryCapture]":
        """Filter to captures that are ready to advance their maturity level."""
        return [c for c in captures if self.score(c).is_promotion_ready]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _score_components(
        self,
        capture: "ManufacturingTheoryCapture",
        next_level: MaturityLevel | None,
    ) -> list[float]:
        """Return a list of 0-1 component scores used to build the aggregate."""
        if next_level is None:
            # Already validated — perfect score
            return [1.0]

        gate = STAGE_GATES[next_level]
        components: list[float] = []

        # Evidence refs
        if gate.min_evidence_refs > 0:
            components.append(
                min(1.0, len(capture.evidence_refs) / gate.min_evidence_refs)
            )
        else:
            components.append(1.0)

        # Thesis word count
        if gate.min_thesis_words > 0:
            components.append(
                min(1.0, len(capture.thesis.split()) / gate.min_thesis_words)
            )
        else:
            components.append(1.0)

        # Source populated
        components.append(1.0 if capture.source.strip() else 0.0)

        # Connections
        if gate.min_connections > 0:
            components.append(
                min(1.0, len(capture.connections) / gate.min_connections)
            )
        else:
            components.append(1.0)

        # Promotion target
        if gate.requires_promotion_target:
            components.append(1.0 if capture.promotion_target.strip() else 0.0)
        else:
            components.append(1.0)

        return components
