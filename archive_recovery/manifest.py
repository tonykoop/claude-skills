"""
archive_recovery.manifest
=========================
Manifest emitter: converts a ScaffoldPlan (or batch of plans) into a
structured, serialisable repo-creation manifest.

The manifest is the hand-off document between the planning phase (pure data)
and any downstream repo-creation tooling.  It fully describes what files go
where, what LFS rules to install, what the README looks like, and what the
evidence ledger says about provenance confidence.

A manifest can be:
  * Serialised to JSON (for CI artefacts)
  * Displayed as human-readable text (for review)
  * Checked for completeness before any downstream write

Nothing in this module writes to disk.  It is purely a data-transformation layer.
"""

from __future__ import annotations

import json
from typing import Sequence

from pydantic import BaseModel, Field

from .models import ArchiveItem, FileKind
from .scaffold import ScaffoldPlan, LFSRule, ScaffoldedDir
from .evidence import EvidenceLedger


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class ManifestEntry(BaseModel):
    """One file placement decision."""
    source_path: str
    dest_path: str
    kind: FileKind
    size_bytes: int
    is_lfs_tracked: bool = False
    content_hash: str = ""
    provenance_confidence: str = "high"


class ManifestSection(BaseModel):
    """All entries for one destination directory."""
    dest_dir: str
    kind: FileKind
    entries: list[ManifestEntry] = Field(default_factory=list)

    @property
    def total_size_bytes(self) -> int:
        return sum(e.size_bytes for e in self.entries)

    @property
    def lfs_entry_count(self) -> int:
        return sum(1 for e in self.entries if e.is_lfs_tracked)


class RepoManifest(BaseModel):
    """Complete manifest for one project repo."""
    project: str
    sections: list[ManifestSection] = Field(default_factory=list)
    lfs_rules: list[str] = Field(default_factory=list)
    gitignore_lines: list[str] = Field(default_factory=list)
    readme_content: str = ""
    evidence_summary: dict = Field(default_factory=dict)
    total_entries: int = 0
    total_size_bytes: int = 0
    low_confidence_count: int = 0
    warnings: list[str] = Field(default_factory=list)

    def export_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)

    def to_text_summary(self) -> str:
        lines = [
            f"=== Repo Manifest: {self.project} ===",
            (
                f"Sections: {len(self.sections)}"
                f"   Entries: {self.total_entries}"
                f"   Size: {self.total_size_bytes / 1024:.1f} KB"
            ),
            f"Low-confidence: {self.low_confidence_count}",
            f"LFS rules: {len(self.lfs_rules)}",
            f"Warnings: {len(self.warnings)}",
            "---",
        ]
        for section in self.sections:
            lines.append(
                f"{section.dest_dir}/"
                f"  ({len(section.entries)} files,"
                f" {section.total_size_bytes / 1024:.1f} KB)"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def _provenance_confidence(item: ArchiveItem) -> str:
    both_inferred = item.kind_is_inferred and item.project_is_inferred
    neither_inferred = (not item.kind_is_inferred) and (not item.project_is_inferred)
    if neither_inferred:
        return "high"
    if both_inferred:
        return "low"
    return "medium"


def build_manifest(
    plan: ScaffoldPlan,
    items: Sequence[ArchiveItem],
) -> RepoManifest:
    """
    Build a RepoManifest from a ScaffoldPlan and the matching ArchiveItems.

    Parameters
    ----------
    plan
        The ScaffoldPlan produced by plan_scaffold().
    items
        All ArchiveItems that belong to this plan's project.

    Returns
    -------
    RepoManifest
        Fully populated manifest.
    """
    items_list = list(items)

    # Build a set of source paths that are LFS-tracked (from LFSRule.source_path)
    lfs_source_paths: set[str] = {rule.source_path for rule in plan.lfs_rules}

    # Index items by kind for fast lookup
    kind_to_items: dict[FileKind, list[ArchiveItem]] = {}
    for item in items_list:
        kind_to_items.setdefault(item.kind, []).append(item)

    warnings: list[str] = []
    sections: list[ManifestSection] = []
    all_dest_paths: list[str] = []  # for collision detection (ordered)

    for scaffolded_dir in plan.dirs:
        dir_items = kind_to_items.get(scaffolded_dir.kind, [])
        entries: list[ManifestEntry] = []

        # Track filenames used within this section to detect collisions
        filename_counts: dict[str, int] = {}

        for item in dir_items:
            filename = item.filename
            count = filename_counts.get(filename, 0)
            filename_counts[filename] = count + 1

            if count == 0:
                dest_path = f"{scaffolded_dir.path}/{filename}"
            else:
                # Disambiguate: append _{n+1} before the extension
                base, _, ext = filename.rpartition(".")
                if base:
                    new_filename = f"{base}_{count + 1}.{ext}"
                else:
                    new_filename = f"{filename}_{count + 1}"
                dest_path = f"{scaffolded_dir.path}/{new_filename}"
                warnings.append(
                    f"Collision: '{filename}' in '{scaffolded_dir.path}/' "
                    f"— renamed to '{new_filename}'"
                )

            # Check for collisions across ALL sections (different dirs, same dest)
            if dest_path in all_dest_paths:
                warnings.append(
                    f"Cross-section collision: dest_path '{dest_path}' is already used"
                )
            all_dest_paths.append(dest_path)

            is_lfs = item.path in lfs_source_paths
            confidence = _provenance_confidence(item)

            entries.append(ManifestEntry(
                source_path=item.path,
                dest_path=dest_path,
                kind=item.kind,
                size_bytes=item.size_bytes,
                is_lfs_tracked=is_lfs,
                content_hash=item.content_hash,
                provenance_confidence=confidence,
            ))

        sections.append(ManifestSection(
            dest_dir=scaffolded_dir.path,
            kind=scaffolded_dir.kind,
            entries=entries,
        ))

    # Collect warnings for UNKNOWN kind items
    for item in items_list:
        if item.kind == FileKind.UNKNOWN:
            warnings.append(
                f"Unknown kind: '{item.path}' could not be classified"
            )

    # Collect warnings for low-confidence entries
    low_confidence_count = 0
    for section in sections:
        for entry in section.entries:
            if entry.provenance_confidence == "low":
                low_confidence_count += 1
                warnings.append(
                    f"Low confidence: '{entry.source_path}' — "
                    "both kind and project are inferred"
                )

    total_entries = sum(len(s.entries) for s in sections)
    total_size = sum(s.total_size_bytes for s in sections)

    return RepoManifest(
        project=plan.project,
        sections=sections,
        lfs_rules=[rule.pattern for rule in plan.lfs_rules],
        gitignore_lines=plan.gitignore_lines,
        readme_content=plan.readme_skeleton,
        evidence_summary=plan.evidence_ledger.export_dict(),
        total_entries=total_entries,
        total_size_bytes=total_size,
        low_confidence_count=low_confidence_count,
        warnings=warnings,
    )


def build_batch_manifests(
    plans: Sequence[ScaffoldPlan],
    all_items: Sequence[ArchiveItem],
) -> list[RepoManifest]:
    """
    Build one RepoManifest per plan, grouping items by inferred_project.

    Parameters
    ----------
    plans
        One ScaffoldPlan per project.
    all_items
        All ArchiveItems across all projects.

    Returns
    -------
    list[RepoManifest]
        One manifest per plan, in the same order as *plans*.
    """
    # Group items by inferred_project
    project_to_items: dict[str, list[ArchiveItem]] = {}
    for item in all_items:
        project_to_items.setdefault(item.inferred_project, []).append(item)

    manifests: list[RepoManifest] = []
    for plan in plans:
        project_items = project_to_items.get(plan.project, [])
        manifests.append(build_manifest(plan, project_items))
    return manifests
