"""schema.py — Core data types for manufacturing theory captures.

ManufacturingTheoryCapture is the canonical KB record.  Every field has a
clear purpose so the registry can index, filter, and graph without magic.
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class MaturityLevel(str, Enum):
    """Three-stage lifecycle for a theory capture."""
    SEED       = "seed"        # Raw idea — unstated evidence, internal only
    DEVELOPING = "developing"  # Partial evidence, actively being refined
    VALIDATED  = "validated"   # Multi-source evidence, promotion-ready

    @property
    def rank(self) -> int:
        return {"seed": 0, "developing": 1, "validated": 2}[self.value]

    def can_advance_to(self, target: "MaturityLevel") -> bool:
        return target.rank == self.rank + 1


class ConnectionKind(str, Enum):
    """Semantic type of a directed edge in the knowledge graph."""
    SUPPORTS      = "supports"       # Capture A provides evidence for B
    CONTRADICTS   = "contradicts"    # Capture A challenges claim in B
    EXTENDS       = "extends"        # A builds further on B's thesis
    SHARES_DOMAIN = "shares_domain"  # Co-domain, no directional claim
    CITES         = "cites"          # A explicitly references B's source


class Domain(str, Enum):
    """High-level manufacturing domains to bucket captures for routing."""
    SCALING_LAW      = "scaling_law"
    MATERIALS        = "materials"
    PROCESS          = "process"
    PLM_DFM          = "plm_dfm"
    SUSTAINABILITY   = "sustainability"
    METROLOGY        = "metrology"
    AUTOMATION       = "automation"
    ECONOMICS        = "economics"
    CROSS_DOMAIN     = "cross_domain"


# ---------------------------------------------------------------------------
# CaptureConnection — directed edge in the knowledge graph
# ---------------------------------------------------------------------------

@dataclass
class CaptureConnection:
    """A typed, directed link between two captures."""
    from_id: str
    to_id:   str
    kind:    ConnectionKind
    note:    str = ""

    def __post_init__(self) -> None:
        if not self.from_id or not self.to_id:
            raise ValueError("CaptureConnection requires non-empty from_id and to_id")
        if self.from_id == self.to_id:
            raise ValueError("Self-loops are not allowed in capture connections")
        if not isinstance(self.kind, ConnectionKind):
            self.kind = ConnectionKind(self.kind)

    def reversed(self) -> "CaptureConnection":
        """Return the inverse edge (swapped endpoints, same kind)."""
        return CaptureConnection(from_id=self.to_id, to_id=self.from_id,
                                  kind=self.kind, note=self.note)


# ---------------------------------------------------------------------------
# ManufacturingTheoryCapture — the canonical KB record
# ---------------------------------------------------------------------------

# Valid id pattern: slug of lowercase letters, digits, hyphens
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,63}$")


@dataclass
class ManufacturingTheoryCapture:
    """A single manufacturing-theory capture in the knowledge base.

    Args:
        id:            Unique slug identifier (e.g. ``koops-law-v1``).
        thesis:        One-paragraph statement of the core claim or idea.
        domain:        Primary ``Domain`` this capture belongs to.
        evidence_refs: List of source references (URLs, paper IDs, doc paths).
        maturity:      Lifecycle stage: seed → developing → validated.
        connections:   List of ``CaptureConnection`` to related captures.
        source:        Free-text origin (e.g. "Gemini conversation 2026-06-13").
        tags:          Optional keyword tags for full-text search.
        created_date:  ISO date of first capture; defaults to today.
        promotion_target: Where the validated thesis should be promoted to
                          (e.g. "makerbench-hwe/docs/RFC").
    """
    id:               str
    thesis:           str
    domain:           Domain
    evidence_refs:    list[str]         = field(default_factory=list)
    maturity:         MaturityLevel     = MaturityLevel.SEED
    connections:      list[CaptureConnection] = field(default_factory=list)
    source:           str               = ""
    tags:             list[str]         = field(default_factory=list)
    created_date:     str               = field(default_factory=lambda: date.today().isoformat())
    promotion_target: str               = ""

    def __post_init__(self) -> None:
        # Coerce enum strings
        if not isinstance(self.domain, Domain):
            self.domain = Domain(self.domain)
        if not isinstance(self.maturity, MaturityLevel):
            self.maturity = MaturityLevel(self.maturity)

        # Validate id
        if not _ID_RE.match(self.id):
            raise ValueError(
                f"id {self.id!r} must be a lowercase slug (letters, digits, hyphens, 2-64 chars)"
            )

        # Validate thesis has substance
        if not self.thesis or len(self.thesis.strip()) < 20:
            raise ValueError("thesis must be at least 20 characters")

        # Coerce connection kind strings
        self.connections = [
            c if isinstance(c, CaptureConnection) else CaptureConnection(**c)
            for c in self.connections
        ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def add_connection(self, conn: CaptureConnection) -> None:
        """Append a connection, rejecting self-loops and exact duplicates."""
        if conn.from_id == self.id and conn.to_id == self.id:
            raise ValueError("Self-loop connection not allowed")
        for existing in self.connections:
            if existing.from_id == conn.from_id and existing.to_id == conn.to_id \
                    and existing.kind == conn.kind:
                return  # idempotent
        self.connections.append(conn)

    def keyword_set(self) -> set[str]:
        """Return a normalised set of keywords drawn from thesis + tags."""
        text = self.thesis.lower() + " " + " ".join(self.tags).lower()
        tokens = re.findall(r"[a-z][a-z0-9]{2,}", text)
        return set(tokens)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id":               self.id,
            "thesis":           self.thesis,
            "domain":           self.domain.value,
            "evidence_refs":    self.evidence_refs,
            "maturity":         self.maturity.value,
            "connections":      [
                {"from_id": c.from_id, "to_id": c.to_id,
                 "kind": c.kind.value, "note": c.note}
                for c in self.connections
            ],
            "source":           self.source,
            "tags":             self.tags,
            "created_date":     self.created_date,
            "promotion_target": self.promotion_target,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ManufacturingTheoryCapture":
        conns = [CaptureConnection(**c) for c in data.get("connections", [])]
        return cls(
            id=data["id"],
            thesis=data["thesis"],
            domain=Domain(data["domain"]),
            evidence_refs=data.get("evidence_refs", []),
            maturity=MaturityLevel(data.get("maturity", "seed")),
            connections=conns,
            source=data.get("source", ""),
            tags=data.get("tags", []),
            created_date=data.get("created_date", date.today().isoformat()),
            promotion_target=data.get("promotion_target", ""),
        )

    def __repr__(self) -> str:
        return (f"ManufacturingTheoryCapture(id={self.id!r}, "
                f"domain={self.domain.value!r}, maturity={self.maturity.value!r})")
