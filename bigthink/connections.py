"""connections.py — Cross-pollination and connection-suggestion engine.

Automatically finds related captures using three independent signals:
  1. Keyword overlap (Jaccard similarity on normalised thesis tokens)
  2. Shared domain (same Domain enum value)
  3. Evidence citation overlap (shared URLs / references)

Results are ranked and de-duplicated.  The finder never *writes* to the
registry — it only suggests; the caller decides whether to call
``registry.connect()``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from bigthink.schema import ConnectionKind, ManufacturingTheoryCapture

if TYPE_CHECKING:
    from bigthink.registry import CaptureRegistry


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass(order=True)
class ConnectionSuggestion:
    """A ranked suggestion to connect two captures.

    Attributes:
        score:        Similarity score in [0, 1].  Higher = stronger signal.
        from_id:      The primary capture.
        to_id:        The suggested peer.
        kind:         Recommended ``ConnectionKind``.
        reasons:      Human-readable list of why this pair was flagged.
    """
    score:    float
    from_id:  str
    to_id:    str
    kind:     ConnectionKind
    reasons:  list[str]

    def __repr__(self) -> str:
        return (
            f"ConnectionSuggestion({self.from_id!r} → {self.to_id!r}, "
            f"kind={self.kind.value!r}, score={self.score:.2f}, "
            f"reasons={self.reasons!r})"
        )


# ---------------------------------------------------------------------------
# ConnectionFinder
# ---------------------------------------------------------------------------

# Minimum Jaccard similarity for a keyword-overlap suggestion
_KEYWORD_THRESHOLD = 0.10
# Minimum shared evidence refs for a citation-overlap suggestion
_CITATION_THRESHOLD = 1


class ConnectionFinder:
    """Stateless engine that suggests capture-to-capture connections.

    All methods are pure (read-only) — they return suggestions without
    mutating any registry or capture.

    Usage::

        finder = ConnectionFinder()
        suggestions = finder.suggest_for(capture_id="koops-law-v1",
                                          registry=reg,
                                          top_k=5)
        for s in suggestions:
            print(s)
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def suggest_for(
        self,
        capture_id: str,
        registry: "CaptureRegistry",
        *,
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> list[ConnectionSuggestion]:
        """Return up to ``top_k`` connection suggestions for ``capture_id``.

        Suggestions are ranked by score (descending).  Pairs already connected
        in the registry are excluded.
        """
        source = registry.get(capture_id)
        existing_peer_ids: set[str] = {
            e.to_id for e in registry.edges_for(capture_id)
        } | {
            e.from_id
            for e in registry.all_edges()
            if e.to_id == capture_id
        }

        suggestions: list[ConnectionSuggestion] = []

        for candidate in registry:
            if candidate.id == capture_id or candidate.id in existing_peer_ids:
                continue
            suggestion = self._compare(source, candidate)
            if suggestion is not None and suggestion.score >= min_score:
                suggestions.append(suggestion)

        suggestions.sort(key=lambda s: s.score, reverse=True)
        return suggestions[:top_k]

    def suggest_all_pairs(
        self,
        registry: "CaptureRegistry",
        *,
        top_k: int = 20,
        min_score: float = _KEYWORD_THRESHOLD,
    ) -> list[ConnectionSuggestion]:
        """Return global top-k unconnected pairs across the whole registry.

        Useful for an initial seeding run on a freshly loaded registry.
        """
        all_captures = list(registry)
        existing: set[tuple[str, str]] = {
            (e.from_id, e.to_id) for e in registry.all_edges()
        }

        suggestions: list[ConnectionSuggestion] = []
        for i, a in enumerate(all_captures):
            for b in all_captures[i + 1:]:
                if (a.id, b.id) in existing or (b.id, a.id) in existing:
                    continue
                suggestion = self._compare(a, b)
                if suggestion is not None and suggestion.score >= min_score:
                    suggestions.append(suggestion)

        suggestions.sort(key=lambda s: s.score, reverse=True)
        return suggestions[:top_k]

    def keyword_similarity(
        self,
        a: ManufacturingTheoryCapture,
        b: ManufacturingTheoryCapture,
    ) -> float:
        """Jaccard similarity between keyword sets of two captures."""
        kw_a = a.keyword_set()
        kw_b = b.keyword_set()
        if not kw_a or not kw_b:
            return 0.0
        intersection = len(kw_a & kw_b)
        union        = len(kw_a | kw_b)
        return intersection / union if union else 0.0

    def citation_overlap(
        self,
        a: ManufacturingTheoryCapture,
        b: ManufacturingTheoryCapture,
    ) -> int:
        """Number of shared evidence_refs between two captures."""
        set_a = {ref.strip().lower() for ref in a.evidence_refs}
        set_b = {ref.strip().lower() for ref in b.evidence_refs}
        return len(set_a & set_b)

    def domain_match(
        self,
        a: ManufacturingTheoryCapture,
        b: ManufacturingTheoryCapture,
    ) -> bool:
        """True when both captures share the same domain."""
        return a.domain == b.domain

    # ------------------------------------------------------------------
    # Internal scoring
    # ------------------------------------------------------------------

    def _compare(
        self,
        a: ManufacturingTheoryCapture,
        b: ManufacturingTheoryCapture,
    ) -> ConnectionSuggestion | None:
        """Compute a combined score and pick the best connection kind."""
        reasons: list[str] = []
        score = 0.0

        # Signal 1 — keyword overlap
        kw_sim = self.keyword_similarity(a, b)
        if kw_sim >= _KEYWORD_THRESHOLD:
            reasons.append(f"keyword overlap {kw_sim:.0%}")
            score += kw_sim * 0.5   # weight 0.5

        # Signal 2 — shared domain
        if self.domain_match(a, b):
            reasons.append(f"shared domain '{a.domain.value}'")
            score += 0.25

        # Signal 3 — shared evidence citations
        shared_cites = self.citation_overlap(a, b)
        if shared_cites >= _CITATION_THRESHOLD:
            reasons.append(f"{shared_cites} shared evidence ref(s)")
            score += min(0.25, shared_cites * 0.1)

        if not reasons:
            return None

        # Choose the most appropriate connection kind
        kind = self._infer_kind(a, b, kw_sim, shared_cites)

        # Normalize to [0, 1]
        score = min(1.0, score)

        return ConnectionSuggestion(
            score=score,
            from_id=a.id,
            to_id=b.id,
            kind=kind,
            reasons=reasons,
        )

    @staticmethod
    def _infer_kind(
        a: ManufacturingTheoryCapture,
        b: ManufacturingTheoryCapture,
        kw_sim: float,
        shared_cites: int,
    ) -> ConnectionKind:
        """Heuristic: choose the best edge label from available signals."""
        # Explicit citation signal is the strongest
        if shared_cites >= _CITATION_THRESHOLD:
            return ConnectionKind.CITES
        # Same domain, strong keyword overlap → likely extending each other
        if a.domain == b.domain and kw_sim >= 0.25:
            return ConnectionKind.EXTENDS
        # Same domain, moderate overlap → co-domain
        if a.domain == b.domain:
            return ConnectionKind.SHARES_DOMAIN
        # Cross-domain but strong keyword overlap → one supports the other
        if kw_sim >= 0.20:
            return ConnectionKind.SUPPORTS
        return ConnectionKind.SHARES_DOMAIN
