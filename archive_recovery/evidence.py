"""
Evidence ledger: separates verifiable archive facts from inferred claims.

Design
------
Tony's provenance discipline requires every claim about a recovered artefact
to be tagged as either a verifiable FACT (derived directly from the archive
byte-stream — path, mtime, hash, extension) or an INFERRED claim (any
heuristic conclusion — project identity, semantic categorisation, date
estimates, authorship).

The EvidenceLedger collects EvidenceEntry objects and provides:
  - audit(): structured summary separated by kind
  - facts() / inferences(): filtered views
  - export_dict(): serialisable representation for embedding in scaffolded repos

Usage
-----
    from archive_recovery.evidence import EvidenceLedger, EvidenceEntry, EvidenceKind

    ledger = EvidenceLedger(project="synth_v2")
    ledger.add(EvidenceEntry(
        kind=EvidenceKind.FACT,
        subject="projects/synth_v2/pcb.kicad_pcb",
        claim="file exists at this path with size 24,576 bytes",
        source="archive byte-stream",
    ))
    ledger.add(EvidenceEntry(
        kind=EvidenceKind.INFERRED,
        subject="projects/synth_v2/pcb.kicad_pcb",
        claim="belongs to project 'synth_v2'",
        source="first directory component heuristic",
        confidence="medium",
    ))
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EvidenceKind(str, Enum):
    """Provenance category for a single claim."""
    FACT     = "fact"      # verifiable from the archive byte-stream
    INFERRED = "inferred"  # derived from heuristics, patterns, or human judgement


class EvidenceEntry(BaseModel):
    """
    A single provenance claim — either a verifiable fact or an inference.

    Fields
    ------
    kind        : FACT or INFERRED.
    subject     : File path, project name, or other entity this claim is about.
    claim       : Human-readable statement of what is asserted.
    source      : Where the claim comes from (e.g. "SHA-256 of file bytes",
                  "extension lookup table", "directory heuristic").
    confidence  : Optional qualitative confidence for INFERRED claims
                  ("high" | "medium" | "low").  Leave empty for FACTs.
    """
    kind:       EvidenceKind
    subject:    str
    claim:      str
    source:     str
    confidence: Optional[str] = None   # only meaningful for INFERRED

    def is_fact(self) -> bool:
        return self.kind == EvidenceKind.FACT

    def is_inferred(self) -> bool:
        return self.kind == EvidenceKind.INFERRED


class EvidenceLedger(BaseModel):
    """
    Ordered collection of EvidenceEntry items for a single recovered project.

    The ledger is append-only during the classification pipeline; once built,
    it is exported alongside the ScaffoldPlan so the scaffolded repo always
    carries a machine-readable provenance record.
    """
    project: str
    entries: list[EvidenceEntry] = Field(default_factory=list)

    def add(self, entry: EvidenceEntry) -> "EvidenceLedger":
        """Append an entry. Returns self for chaining."""
        self.entries.append(entry)
        return self

    # ------------------------------------------------------------------
    # Filtered views
    # ------------------------------------------------------------------

    def facts(self) -> list[EvidenceEntry]:
        """Return only FACT entries."""
        return [e for e in self.entries if e.is_fact()]

    def inferences(self) -> list[EvidenceEntry]:
        """Return only INFERRED entries."""
        return [e for e in self.entries if e.is_inferred()]

    # ------------------------------------------------------------------
    # Audit & export
    # ------------------------------------------------------------------

    def audit(self) -> dict:
        """
        Return a structured summary suitable for logging or human review.

        Shape
        -----
        {
          "project": str,
          "total":   int,
          "facts":   int,
          "inferred": int,
          "entries": [{"kind": ..., "subject": ..., "claim": ..., ...}, ...]
        }
        """
        return {
            "project":  self.project,
            "total":    len(self.entries),
            "facts":    len(self.facts()),
            "inferred": len(self.inferences()),
            "entries":  [e.model_dump() for e in self.entries],
        }

    def export_dict(self) -> dict:
        """Serialisable dict for embedding in the evidence-ledger.json file."""
        return self.audit()

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_archive_items(cls, project: str, items) -> "EvidenceLedger":
        """
        Build a ledger automatically from a list of ArchiveItems.

        Generates:
          - One FACT entry per item covering path, size, and hash.
          - One INFERRED entry per item for kind (when kind_is_inferred=True).
          - One INFERRED entry per item for project grouping.
        """
        ledger = cls(project=project)
        for item in items:
            # Archive facts — derived directly from the file record
            ledger.add(EvidenceEntry(
                kind=EvidenceKind.FACT,
                subject=item.path,
                claim=(
                    f"file exists at path '{item.path}' "
                    f"(size={item.size_bytes} bytes, hash={item.content_hash[:12]}…)"
                ),
                source="archive byte-stream",
            ))
            if not item.kind_is_inferred:
                ledger.add(EvidenceEntry(
                    kind=EvidenceKind.FACT,
                    subject=item.path,
                    claim=f"file kind is '{item.kind.value}' (extension lookup)",
                    source="extension-to-kind lookup table (archive fact)",
                ))
            else:
                ledger.add(EvidenceEntry(
                    kind=EvidenceKind.INFERRED,
                    subject=item.path,
                    claim=f"file kind inferred as '{item.kind.value}'",
                    source="heuristic (no definitive extension match)",
                    confidence="low",
                ))
            # Project grouping is always inferred in this version
            ledger.add(EvidenceEntry(
                kind=EvidenceKind.INFERRED,
                subject=item.path,
                claim=f"belongs to project '{item.inferred_project}'",
                source="path-component heuristic",
                confidence="medium",
            ))
        return ledger
