"""registry.py — CaptureRegistry: the in-memory knowledge graph store.

Supports:
  - add / get / remove
  - query (full-text substring across thesis + tags)
  - filter (by domain, maturity, tag)
  - connect (create typed edges between captures)
  - neighbors (adjacent node IDs with optional kind filter)
  - subgraph (BFS reachability)
  - load / dump JSON persistence
"""
from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable, Iterator

from bigthink.schema import (
    CaptureConnection,
    ConnectionKind,
    Domain,
    ManufacturingTheoryCapture,
    MaturityLevel,
)


class RegistryError(Exception):
    """Raised for logical errors in registry operations."""


class CaptureRegistry:
    """In-memory store and knowledge graph for ManufacturingTheoryCapture objects.

    The registry maintains:
      - ``_captures``: dict[id → capture]
      - ``_edges``:    dict[id → list[CaptureConnection]]  (outgoing edges)
    Both structures are always consistent with each other.
    """

    def __init__(self) -> None:
        self._captures: dict[str, ManufacturingTheoryCapture] = {}
        # Adjacency list: id → [outgoing connections]
        self._edges: dict[str, list[CaptureConnection]] = defaultdict(list)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def add(self, capture: ManufacturingTheoryCapture) -> None:
        """Register a capture, raising ``RegistryError`` on duplicate id."""
        if capture.id in self._captures:
            raise RegistryError(f"Duplicate capture id: {capture.id!r}")
        self._captures[capture.id] = capture
        # Absorb any connections already embedded on the capture
        for conn in capture.connections:
            self._record_edge(conn)

    def get(self, capture_id: str) -> ManufacturingTheoryCapture:
        """Retrieve by id, raising ``KeyError`` if not found."""
        try:
            return self._captures[capture_id]
        except KeyError:
            raise KeyError(f"No capture with id {capture_id!r}")

    def remove(self, capture_id: str) -> ManufacturingTheoryCapture:
        """Remove a capture and all its edges, returning the removed object."""
        cap = self.get(capture_id)
        del self._captures[capture_id]
        # Drop outgoing edges from this node
        self._edges.pop(capture_id, None)
        # Drop incoming edges to this node from other nodes
        for node_edges in self._edges.values():
            node_edges[:] = [e for e in node_edges if e.to_id != capture_id]
        return cap

    def __len__(self) -> int:
        return len(self._captures)

    def __contains__(self, capture_id: str) -> bool:
        return capture_id in self._captures

    def __iter__(self) -> Iterator[ManufacturingTheoryCapture]:
        return iter(self._captures.values())

    # ------------------------------------------------------------------
    # Query / filter
    # ------------------------------------------------------------------

    def query(self, text: str) -> list[ManufacturingTheoryCapture]:
        """Case-insensitive substring search across thesis, tags, and source."""
        needle = text.lower()
        return [
            c for c in self._captures.values()
            if needle in c.thesis.lower()
            or any(needle in t.lower() for t in c.tags)
            or needle in c.source.lower()
        ]

    def filter(
        self,
        *,
        domain: Domain | str | None = None,
        maturity: MaturityLevel | str | None = None,
        tag: str | None = None,
        promotion_target: str | None = None,
    ) -> list[ManufacturingTheoryCapture]:
        """Return captures matching ALL supplied criteria (None = any)."""
        if isinstance(domain, str):
            domain = Domain(domain)
        if isinstance(maturity, str):
            maturity = MaturityLevel(maturity)

        results = list(self._captures.values())
        if domain is not None:
            results = [c for c in results if c.domain == domain]
        if maturity is not None:
            results = [c for c in results if c.maturity == maturity]
        if tag is not None:
            tag_lower = tag.lower()
            results = [c for c in results if any(tag_lower == t.lower() for t in c.tags)]
        if promotion_target is not None:
            pt_lower = promotion_target.lower()
            results = [c for c in results if pt_lower in c.promotion_target.lower()]
        return results

    def all(self) -> list[ManufacturingTheoryCapture]:
        """Return all captures in insertion order."""
        return list(self._captures.values())

    # ------------------------------------------------------------------
    # Graph — connect / neighbors / subgraph
    # ------------------------------------------------------------------

    def connect(
        self,
        from_id: str,
        to_id: str,
        kind: ConnectionKind | str,
        note: str = "",
        *,
        bidirectional: bool = False,
    ) -> CaptureConnection:
        """Add a typed directed edge from_id → to_id.

        Args:
            bidirectional: If True, also add the reverse edge.

        Returns:
            The created ``CaptureConnection``.
        """
        for cid in (from_id, to_id):
            if cid not in self._captures:
                raise RegistryError(f"Cannot connect: unknown capture id {cid!r}")
        if isinstance(kind, str):
            kind = ConnectionKind(kind)

        conn = CaptureConnection(from_id=from_id, to_id=to_id, kind=kind, note=note)
        self._record_edge(conn)
        self._captures[from_id].add_connection(conn)

        if bidirectional:
            rev = conn.reversed()
            self._record_edge(rev)
            self._captures[to_id].add_connection(rev)

        return conn

    def neighbors(
        self,
        capture_id: str,
        *,
        kind: ConnectionKind | str | None = None,
        direction: str = "outgoing",  # "outgoing" | "incoming" | "both"
    ) -> list[ManufacturingTheoryCapture]:
        """Return captures adjacent to ``capture_id``.

        Args:
            kind:      Restrict to a specific ``ConnectionKind``.
            direction: "outgoing" follows forward edges; "incoming" follows
                       reverse edges; "both" follows all edges.
        """
        if capture_id not in self._captures:
            raise KeyError(f"No capture with id {capture_id!r}")
        if isinstance(kind, str):
            kind = ConnectionKind(kind)

        result_ids: set[str] = set()

        if direction in ("outgoing", "both"):
            for edge in self._edges.get(capture_id, []):
                if kind is None or edge.kind == kind:
                    result_ids.add(edge.to_id)

        if direction in ("incoming", "both"):
            for src_id, edges in self._edges.items():
                for edge in edges:
                    if edge.to_id == capture_id:
                        if kind is None or edge.kind == kind:
                            result_ids.add(src_id)

        return [self._captures[cid] for cid in result_ids if cid in self._captures]

    def subgraph(
        self,
        start_id: str,
        *,
        max_depth: int = 3,
        kind: ConnectionKind | str | None = None,
    ) -> list[ManufacturingTheoryCapture]:
        """BFS from ``start_id`` up to ``max_depth`` hops (both directions)."""
        if start_id not in self._captures:
            raise KeyError(f"No capture with id {start_id!r}")

        visited: set[str] = {start_id}
        queue: deque[tuple[str, int]] = deque([(start_id, 0)])
        result: list[ManufacturingTheoryCapture] = [self._captures[start_id]]

        while queue:
            current_id, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for cap in self.neighbors(current_id, kind=kind, direction="both"):
                if cap.id not in visited:
                    visited.add(cap.id)
                    result.append(cap)
                    queue.append((cap.id, depth + 1))

        return result

    def edges_for(self, capture_id: str) -> list[CaptureConnection]:
        """Return all outgoing edges from ``capture_id``."""
        if capture_id not in self._captures:
            raise KeyError(f"No capture with id {capture_id!r}")
        return list(self._edges.get(capture_id, []))

    def all_edges(self) -> list[CaptureConnection]:
        """Return every edge in the graph."""
        return [e for edges in self._edges.values() for e in edges]

    # ------------------------------------------------------------------
    # Persistence — JSON round-trip
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "captures": [c.to_dict() for c in self._captures.values()],
            # edges are already embedded in captures; stored separately only
            # for captures that received external connect() calls after add()
            "extra_edges": [
                {"from_id": e.from_id, "to_id": e.to_id,
                 "kind": e.kind.value, "note": e.note}
                for edges in self._edges.values()
                for e in edges
                if not any(
                    conn.from_id == e.from_id and conn.to_id == e.to_id
                    and conn.kind == e.kind
                    for conn in self._captures.get(e.from_id, ManufacturingTheoryCapture.__new__(
                        ManufacturingTheoryCapture)).connections
                )
            ],
        }

    def dump(self, path: str | Path) -> None:
        """Serialise registry to a JSON file."""
        payload = {
            "captures": [c.to_dict() for c in self._captures.values()],
        }
        Path(path).write_text(json.dumps(payload, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "CaptureRegistry":
        """Deserialise registry from a JSON file created by ``dump``."""
        data = json.loads(Path(path).read_text())
        reg = cls()
        for cap_data in data.get("captures", []):
            reg.add(ManufacturingTheoryCapture.from_dict(cap_data))
        return reg

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _record_edge(self, conn: CaptureConnection) -> None:
        """Add ``conn`` to the adjacency list if not already present."""
        for existing in self._edges[conn.from_id]:
            if (existing.to_id == conn.to_id and existing.kind == conn.kind):
                return  # idempotent
        self._edges[conn.from_id].append(conn)

    # ------------------------------------------------------------------
    # Pretty summary
    # ------------------------------------------------------------------

    def summary(self) -> str:
        """One-line human-readable summary of registry size."""
        n_edges = sum(len(v) for v in self._edges.values())
        return (
            f"CaptureRegistry: {len(self._captures)} captures, "
            f"{n_edges} edges, "
            f"{len(set(c.domain for c in self._captures.values()))} domains"
        )
