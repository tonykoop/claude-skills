"""search_index.py — Pre-computed inverted index for fast keyword search.

The ``SearchIndex`` wraps a ``CaptureRegistry`` and builds a token →
capture-id inverted index at construction time.  Incremental updates
(add/remove) are supported so the index stays in sync after mutations.

This is intentionally lightweight — no external deps, pure Python.
For large registries (thousands of captures), it replaces the O(N) linear
scan in ``CaptureRegistry.query()`` with an O(k) set-intersection lookup.

Usage::

    reg = build_seed_registry()
    idx = SearchIndex(reg)

    hits = idx.search("spatial complexity")
    for cap in hits:
        print(cap.id, cap.thesis[:60])

    # After mutations:
    reg.add(new_cap)
    idx.add_capture(new_cap)
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import TYPE_CHECKING

from bigthink.schema import ManufacturingTheoryCapture

if TYPE_CHECKING:
    from bigthink.registry import CaptureRegistry


# Tokeniser: lowercase alpha-numeric tokens of length ≥ 3
_TOKEN_RE = re.compile(r"[a-z][a-z0-9]{2,}")


def _tokenise(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def _capture_tokens(cap: ManufacturingTheoryCapture) -> set[str]:
    """All indexable tokens for a capture."""
    parts = [
        cap.thesis,
        cap.source,
        " ".join(cap.tags),
        " ".join(cap.evidence_refs),
        cap.domain.value,
        cap.maturity.value,
    ]
    return _tokenise(" ".join(parts))


# ---------------------------------------------------------------------------
# SearchIndex
# ---------------------------------------------------------------------------

class SearchIndex:
    """Inverted token index over a CaptureRegistry.

    Attributes:
        _index:   dict[token → set[capture_id]]
        _tokens:  dict[capture_id → set[token]]  (reverse, for removal)
    """

    def __init__(self, registry: "CaptureRegistry | None" = None) -> None:
        self._index: dict[str, set[str]] = defaultdict(set)
        self._tokens: dict[str, set[str]] = {}
        if registry is not None:
            self.build(registry)

    # ------------------------------------------------------------------
    # Build / rebuild
    # ------------------------------------------------------------------

    def build(self, registry: "CaptureRegistry") -> None:
        """(Re)build the index from all captures in ``registry``."""
        self._index.clear()
        self._tokens.clear()
        for cap in registry:
            self._index_capture(cap)

    def add_capture(self, cap: ManufacturingTheoryCapture) -> None:
        """Index a newly added capture."""
        self._index_capture(cap)

    def remove_capture(self, capture_id: str) -> None:
        """Remove a capture from the index by id."""
        tokens = self._tokens.pop(capture_id, set())
        for tok in tokens:
            self._index[tok].discard(capture_id)
            if not self._index[tok]:
                del self._index[tok]

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        registry: "CaptureRegistry | None" = None,
    ) -> list[ManufacturingTheoryCapture]:
        """Return captures matching ALL tokens in ``query`` (AND semantics).

        Args:
            query:    Space-separated search terms.  Each term must appear
                      as a token in at least one indexed field.
            registry: If supplied, resolve ids to full capture objects.
                      If None, returns an empty list (use search_ids instead).

        Returns:
            List of matching ``ManufacturingTheoryCapture`` objects, sorted
            by id for deterministic ordering.
        """
        ids = self.search_ids(query)
        if registry is None or not ids:
            return []
        results = []
        for cid in sorted(ids):
            try:
                results.append(registry.get(cid))
            except KeyError:
                pass  # capture removed from registry but not yet from index
        return results

    def search_ids(self, query: str) -> set[str]:
        """Return the set of capture ids matching ALL query tokens."""
        tokens = _tokenise(query)
        if not tokens:
            return set()

        # Start with all captures that match the first token
        candidates: set[str] | None = None
        for tok in tokens:
            matching = self._index.get(tok, set())
            if candidates is None:
                candidates = set(matching)
            else:
                candidates &= matching  # AND intersection
            if not candidates:
                break

        return candidates or set()

    def search_any(self, query: str) -> set[str]:
        """Return the set of capture ids matching ANY query token (OR semantics)."""
        tokens = _tokenise(query)
        result: set[str] = set()
        for tok in tokens:
            result |= self._index.get(tok, set())
        return result

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def token_count(self) -> int:
        return len(self._index)

    def capture_count(self) -> int:
        return len(self._tokens)

    def top_tokens(self, n: int = 10) -> list[tuple[str, int]]:
        """Return the n most frequent tokens (token, doc-frequency) pairs."""
        ranked = sorted(
            ((tok, len(ids)) for tok, ids in self._index.items()),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:n]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _index_capture(self, cap: ManufacturingTheoryCapture) -> None:
        tokens = _capture_tokens(cap)
        self._tokens[cap.id] = tokens
        for tok in tokens:
            self._index[tok].add(cap.id)
