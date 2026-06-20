"""
archive_recovery.workflow
=========================
Recovery workflow orchestrator: drives the full pipeline from raw FileRecords
to a structured RecoveryManifest.

Pipeline stages
---------------
1. INGEST    — accept raw FileRecord list
2. CLASSIFY  — run classifier to produce ArchiveItem list
3. DEDUP     — detect duplicates/near-dups across all items
4. GROUP     — group ArchiveItems by inferred_project
5. PLAN      — run plan_scaffold() for each project group
6. MANIFEST  — assemble into RecoveryManifest

The workflow is stateful (each stage updates internal state) but pure
in-memory — no I/O, no randomness.

Usage
-----
    wf = RecoveryWorkflow()
    wf.ingest(file_records)
    wf.run()   # or step-by-step: wf.classify(); wf.dedup(); wf.group(); wf.plan()
    manifest = wf.build_manifest()
"""

from __future__ import annotations

from enum import Enum
from typing import Sequence

from pydantic import BaseModel, Field

from .classifier import classify_archive
from .dedup import DedupConfig, DedupReport, detect_duplicates
from .models import ArchiveItem, FileRecord
from .scaffold import ScaffoldPlan, plan_scaffold


class WorkflowStage(str, Enum):
    """Ordered pipeline stage identifiers."""

    IDLE = "IDLE"
    INGESTED = "INGESTED"
    CLASSIFIED = "CLASSIFIED"
    DEDUPED = "DEDUPED"
    GROUPED = "GROUPED"
    PLANNED = "PLANNED"
    COMPLETE = "COMPLETE"


# Ordered list used for >= comparisons
_STAGE_ORDER = [
    WorkflowStage.IDLE,
    WorkflowStage.INGESTED,
    WorkflowStage.CLASSIFIED,
    WorkflowStage.DEDUPED,
    WorkflowStage.GROUPED,
    WorkflowStage.PLANNED,
    WorkflowStage.COMPLETE,
]


def _stage_index(stage: WorkflowStage) -> int:
    return _STAGE_ORDER.index(stage)


class WorkflowConfig(BaseModel):
    """Tuning knobs for the recovery workflow."""

    dedup_config: DedupConfig = Field(default_factory=DedupConfig)

    min_items_per_project: int = 1
    """Projects with fewer items are lumped into unknown_project_label."""

    unknown_project_label: str = "misc"
    """Label for items with inferred_project == 'unknown_project' or tiny projects."""

    max_projects: int = 500
    """Safety cap on the number of distinct projects."""


class ProjectGroup(BaseModel):
    """A named project and its ArchiveItems plus optional ScaffoldPlan."""

    project: str
    items: list[ArchiveItem]
    scaffold_plan: ScaffoldPlan | None = None


class RecoveryManifest(BaseModel):
    """Assembled result of a completed (or partially completed) workflow run."""

    total_files: int
    total_size_bytes: int
    project_count: int
    projects: list[ProjectGroup]
    dedup_report: DedupReport
    duplicate_count: int
    potential_savings_bytes: int
    stage: WorkflowStage
    warnings: list[str] = []

    def export_dict(self) -> dict:
        """Serialisable summary — no nested Pydantic objects."""
        return {
            "total_files": self.total_files,
            "total_size_bytes": self.total_size_bytes,
            "project_count": self.project_count,
            "duplicate_count": self.duplicate_count,
            "potential_savings_bytes": self.potential_savings_bytes,
            "stage": self.stage.value,
            "warnings": self.warnings,
            "dedup_report": self.dedup_report.model_dump(),
            "projects": [
                {
                    "project": pg.project,
                    "item_count": len(pg.items),
                    "scaffold_plan": pg.scaffold_plan.export_dict()
                    if pg.scaffold_plan is not None
                    else None,
                }
                for pg in self.projects
            ],
        }


class RecoveryWorkflow:
    """
    Stateful (but pure in-memory) recovery pipeline driver.

    Stages must be executed in order:
        ingest → classify → dedup → group → plan → build_manifest

    ``run()`` executes all stages from classify through plan in a single call.
    """

    def __init__(self, config: WorkflowConfig | None = None) -> None:
        self.config = config or WorkflowConfig()
        self.stage = WorkflowStage.IDLE
        self._raw_records: list[FileRecord] = []
        self._items: list[ArchiveItem] = []
        self._dedup_report: DedupReport | None = None
        self._groups: dict[str, list[ArchiveItem]] = {}   # project → items
        self._scaffold_plans: dict[str, ScaffoldPlan] = {}
        self._warnings: list[str] = []

    # ------------------------------------------------------------------
    # Stage methods
    # ------------------------------------------------------------------

    def ingest(self, records: Sequence[FileRecord]) -> None:
        """Accept raw FileRecords.  Stage → INGESTED."""
        if _stage_index(self.stage) not in (
            _stage_index(WorkflowStage.IDLE),
            _stage_index(WorkflowStage.INGESTED),
        ):
            raise RuntimeError(
                f"ingest() requires stage IDLE or INGESTED; current stage is {self.stage.value}"
            )
        self._raw_records = list(records)
        self.stage = WorkflowStage.INGESTED

    def classify(self) -> list[ArchiveItem]:
        """Run classifier.  Stage → CLASSIFIED."""
        if _stage_index(self.stage) < _stage_index(WorkflowStage.INGESTED):
            raise RuntimeError(
                f"classify() requires stage >= INGESTED; current stage is {self.stage.value}"
            )
        self._items = classify_archive(self._raw_records)
        self.stage = WorkflowStage.CLASSIFIED
        return self._items

    def dedup(self) -> DedupReport:
        """Detect duplicates.  Stage → DEDUPED."""
        if _stage_index(self.stage) < _stage_index(WorkflowStage.CLASSIFIED):
            raise RuntimeError(
                f"dedup() requires stage >= CLASSIFIED; current stage is {self.stage.value}"
            )
        self._dedup_report = detect_duplicates(self._items, self.config.dedup_config)
        self.stage = WorkflowStage.DEDUPED
        return self._dedup_report

    def group(self) -> dict[str, list[ArchiveItem]]:
        """
        Group items by inferred_project.  Stage → GROUPED.

        Remaps 'unknown_project' to config.unknown_project_label and lumps
        projects smaller than config.min_items_per_project into the same label.
        Caps total project count at config.max_projects (emits a warning).
        """
        if _stage_index(self.stage) < _stage_index(WorkflowStage.DEDUPED):
            raise RuntimeError(
                f"group() requires stage >= DEDUPED; current stage is {self.stage.value}"
            )

        misc_label = self.config.unknown_project_label

        # First pass: bucket by project
        raw: dict[str, list[ArchiveItem]] = {}
        for item in self._items:
            proj = item.inferred_project
            if proj == "unknown_project":
                proj = misc_label
            raw.setdefault(proj, []).append(item)

        # Second pass: lump tiny projects into misc
        if self.config.min_items_per_project > 1:
            final: dict[str, list[ArchiveItem]] = {}
            for proj, proj_items in raw.items():
                if proj == misc_label or len(proj_items) >= self.config.min_items_per_project:
                    final.setdefault(proj, []).extend(proj_items)
                else:
                    final.setdefault(misc_label, []).extend(proj_items)
            raw = final

        # Third pass: apply max_projects cap
        if len(raw) > self.config.max_projects:
            # Sort projects deterministically; excess projects are lumped into misc
            sorted_projects = sorted(raw.keys())
            kept = sorted_projects[: self.config.max_projects]
            overflow = sorted_projects[self.config.max_projects :]
            self._warnings.append(
                f"max_projects cap ({self.config.max_projects}) reached; "
                f"{len(overflow)} project(s) lumped into '{misc_label}'"
            )
            capped: dict[str, list[ArchiveItem]] = {}
            for proj in kept:
                capped[proj] = raw[proj]
            for proj in overflow:
                capped.setdefault(misc_label, []).extend(raw[proj])
            raw = capped

        self._groups = raw
        self.stage = WorkflowStage.GROUPED
        return self._groups

    def plan(self) -> dict[str, ScaffoldPlan]:
        """
        Run plan_scaffold() for each project group.  Stage → PLANNED.
        """
        if _stage_index(self.stage) < _stage_index(WorkflowStage.GROUPED):
            raise RuntimeError(
                f"plan() requires stage >= GROUPED; current stage is {self.stage.value}"
            )
        self._scaffold_plans = {
            project: plan_scaffold(project, proj_items)
            for project, proj_items in self._groups.items()
        }
        self.stage = WorkflowStage.PLANNED
        return self._scaffold_plans

    def run(self) -> None:
        """Execute classify → dedup → group → plan in sequence.  Stage → COMPLETE."""
        self.classify()
        self.dedup()
        self.group()
        self.plan()
        self.stage = WorkflowStage.COMPLETE

    # ------------------------------------------------------------------
    # Manifest assembly
    # ------------------------------------------------------------------

    def build_manifest(self) -> RecoveryManifest:
        """
        Assemble a RecoveryManifest.  Requires stage >= GROUPED.

        Plans are included when available (stage >= PLANNED).
        """
        if _stage_index(self.stage) < _stage_index(WorkflowStage.GROUPED):
            raise RuntimeError(
                f"build_manifest() requires stage >= GROUPED; current stage is {self.stage.value}"
            )

        dedup_report = self._dedup_report or DedupReport(total_items=len(self._items))

        project_groups: list[ProjectGroup] = []
        for project, proj_items in self._groups.items():
            scaffold = self._scaffold_plans.get(project)
            project_groups.append(ProjectGroup(
                project=project,
                items=proj_items,
                scaffold_plan=scaffold,
            ))

        return RecoveryManifest(
            total_files=len(self._items),
            total_size_bytes=sum(it.size_bytes for it in self._items),
            project_count=len(self._groups),
            projects=project_groups,
            dedup_report=dedup_report,
            duplicate_count=dedup_report.duplicate_count,
            potential_savings_bytes=dedup_report.potential_savings_bytes,
            stage=self.stage,
            warnings=list(self._warnings),
        )

    # ------------------------------------------------------------------
    # Human-readable summary
    # ------------------------------------------------------------------

    def summary_lines(self) -> list[str]:
        """Return human-readable strings describing the current state."""
        lines: list[str] = [f"Stage: {self.stage.value}"]
        lines.append(f"Records ingested: {len(self._raw_records)}")
        lines.append(f"Items classified: {len(self._items)}")
        if self._dedup_report is not None:
            dr = self._dedup_report
            pct = (
                f"{dr.duplicate_count / dr.total_items * 100:.1f}%"
                if dr.total_items > 0
                else "0.0%"
            )
            lines.append(f"Duplicates: {dr.duplicate_count} ({pct})")
            lines.append(
                f"Potential savings: {dr.potential_savings_bytes:,} bytes"
            )
        if self._groups:
            lines.append(f"Projects: {len(self._groups)}")
        if self._scaffold_plans:
            lines.append(f"Scaffold plans: {len(self._scaffold_plans)}")
        if self._warnings:
            for w in self._warnings:
                lines.append(f"Warning: {w}")
        return lines
