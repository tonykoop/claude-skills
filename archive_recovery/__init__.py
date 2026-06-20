"""
Maker Archive Recovery & Repo Scaffolding Toolkit.

Recover scattered maker archives (CAD, code, photos, docs, media) and scaffold
them into well-structured repositories with full provenance tracking.

Public surface
--------------
Core models & classification
    FileRecord, ArchiveItem, FileKind, classify_archive

Scaffold planning
    ScaffoldPlan, plan_scaffold, LFSRule, ScaffoldedDir

Provenance / evidence
    EvidenceLedger, EvidenceEntry, EvidenceKind

Duplicate detection
    DedupConfig, DedupReport, ExactDupGroup, NearDupGroup, StalePair, detect_duplicates

Recovery workflow orchestrator
    RecoveryWorkflow, RecoveryManifest, WorkflowStage, WorkflowConfig, ProjectGroup

Manifest emitter
    ManifestEntry, ManifestSection, RepoManifest, build_manifest, build_batch_manifests

Migration planner
    MigrationAction, MigrationItem, MigrationPlan, plan_migration

CSV inventory ingestion
    InventoryRow, FileInventoryRow, InventoryParseResult, ArchiveSummary
    parse_directory_csv, rows_to_file_records, summarise_inventory

Project router
    KeywordRule, KindRule, RouterConfig, RoutingDecision, ProjectRouter
"""

from .models import ArchiveItem, FileRecord, FileKind
from .classifier import classify_archive
from .scaffold import ScaffoldPlan, LFSRule, ScaffoldedDir, plan_scaffold
from .evidence import EvidenceLedger, EvidenceEntry, EvidenceKind
from .dedup import (
    DedupConfig, DedupReport, ExactDupGroup, NearDupGroup, StalePair,
    detect_duplicates,
)
from .workflow import (
    RecoveryWorkflow, RecoveryManifest, WorkflowStage, WorkflowConfig, ProjectGroup,
)
from .manifest import (
    ManifestEntry, ManifestSection, RepoManifest, build_manifest, build_batch_manifests,
)
from .migration import MigrationAction, MigrationItem, MigrationPlan, plan_migration
from .inventory_csv import (
    InventoryRow, FileInventoryRow, InventoryParseResult, ArchiveSummary,
    parse_directory_csv, rows_to_file_records, summarise_inventory,
)
from .project_router import (
    KeywordRule, KindRule, RouterConfig, RoutingDecision, ProjectRouter,
)

__all__ = [
    # core
    "FileRecord", "ArchiveItem", "FileKind", "classify_archive",
    # scaffold
    "ScaffoldPlan", "LFSRule", "ScaffoldedDir", "plan_scaffold",
    # evidence
    "EvidenceLedger", "EvidenceEntry", "EvidenceKind",
    # dedup
    "DedupConfig", "DedupReport", "ExactDupGroup", "NearDupGroup", "StalePair",
    "detect_duplicates",
    # workflow
    "RecoveryWorkflow", "RecoveryManifest", "WorkflowStage", "WorkflowConfig", "ProjectGroup",
    # manifest
    "ManifestEntry", "ManifestSection", "RepoManifest", "build_manifest", "build_batch_manifests",
    # migration
    "MigrationAction", "MigrationItem", "MigrationPlan", "plan_migration",
    # inventory CSV
    "InventoryRow", "FileInventoryRow", "InventoryParseResult", "ArchiveSummary",
    "parse_directory_csv", "rows_to_file_records", "summarise_inventory",
    # project router
    "KeywordRule", "KindRule", "RouterConfig", "RoutingDecision", "ProjectRouter",
]
