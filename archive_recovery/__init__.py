"""
Maker Archive Recovery & Repo Scaffolding Toolkit.

Recover scattered maker archives (CAD, code, photos, docs, media) and scaffold
them into well-structured repositories with full provenance tracking.

Public surface:
    ArchiveItem        — data model for a recovered file
    FileRecord         — raw input record (path + mtime + size)
    classify_archive   — infer kind + project grouping from a list of FileRecords
    ScaffoldPlan       — proposed repo layout for a recovered project
    plan_scaffold      — produce a ScaffoldPlan from a project name + its ArchiveItems
    EvidenceLedger     — separates verifiable archive facts from inferred claims
    EvidenceEntry      — a single ledger entry (fact or inferred)
"""

from .models import ArchiveItem, FileRecord, FileKind
from .classifier import classify_archive
from .scaffold import ScaffoldPlan, plan_scaffold
from .evidence import EvidenceLedger, EvidenceEntry, EvidenceKind

__all__ = [
    "ArchiveItem",
    "FileRecord",
    "FileKind",
    "classify_archive",
    "ScaffoldPlan",
    "plan_scaffold",
    "EvidenceLedger",
    "EvidenceEntry",
    "EvidenceKind",
]
