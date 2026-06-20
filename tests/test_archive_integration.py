"""
tests/test_archive_integration.py
==================================
Cross-module integration tests for the archive-recovery pipeline.
"""

from __future__ import annotations

import json
import pytest

from archive_recovery.models import FileRecord, ArchiveItem, FileKind
from archive_recovery.classifier import classify_archive
from archive_recovery.dedup import DedupConfig, detect_duplicates
from archive_recovery.scaffold import plan_scaffold
from archive_recovery.evidence import EvidenceLedger, EvidenceEntry, EvidenceKind
from archive_recovery.manifest import build_manifest, RepoManifest
from archive_recovery.migration import plan_migration, MigrationAction
from archive_recovery.workflow import (
    RecoveryWorkflow,
    RecoveryManifest,
    WorkflowStage,
    WorkflowConfig,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_record(path: str, size_bytes: int = 10_000, mtime: float = 1_715_000_000.0,
                 content_hash: str | None = None) -> FileRecord:
    return FileRecord(path=path, size_bytes=size_bytes, mtime=mtime,
                      content_hash=content_hash)


def _basic_records() -> list[FileRecord]:
    """10 FileRecords across two projects covering several kinds."""
    return [
        _make_record("synth_v2/cad/front_panel.step", 80_000),
        _make_record("synth_v2/cad/pcb.dxf", 45_000),
        _make_record("synth_v2/code/firmware.ino", 12_000),
        _make_record("synth_v2/docs/bom.pdf", 30_000),
        _make_record("synth_v2/photos/build01.jpg", 3_000_000),
        _make_record("wood_table/cad/table_top.f3d", 200_000),
        _make_record("wood_table/cad/leg.step", 150_000),
        _make_record("wood_table/photos/final.jpg", 2_500_000),
        _make_record("wood_table/docs/plans.pdf", 95_000),
        _make_record("wood_table/code/cnc_path.py", 8_000),
    ]


def _run_full_workflow(records=None) -> tuple[RecoveryWorkflow, RecoveryManifest]:
    if records is None:
        records = _basic_records()
    wf = RecoveryWorkflow()
    wf.ingest(records)
    wf.run()
    return wf, wf.build_manifest()


# ===========================================================================
# 1. Public API importability
# ===========================================================================

def test_public_api_importable():
    from archive_recovery import classify_archive, plan_scaffold, EvidenceLedger
    assert callable(classify_archive)
    assert callable(plan_scaffold)
    assert EvidenceLedger is not None


# ===========================================================================
# 2–6. cli_demo smoke tests
# ===========================================================================

def test_run_demo_returns_dict():
    from archive_recovery.cli_demo import run_demo
    d = run_demo()
    assert isinstance(d, dict)


def test_run_demo_total_files():
    from archive_recovery.cli_demo import run_demo
    d = run_demo()
    assert d["total_files"] >= 25


def test_run_demo_projects_found():
    from archive_recovery.cli_demo import run_demo
    d = run_demo()
    assert d["project_count"] >= 3


def test_run_demo_duplicates_detected():
    from archive_recovery.cli_demo import run_demo
    d = run_demo()
    assert d["duplicate_count"] >= 1


def test_run_demo_workflow_complete():
    from archive_recovery.cli_demo import run_demo
    d = run_demo()
    assert d["workflow_stage"] == "COMPLETE"


# ===========================================================================
# 7. Full pipeline → manifest has correct total_files
# ===========================================================================

def test_full_pipeline_manifest_total_files():
    records = _basic_records()
    wf, manifest = _run_full_workflow(records)
    assert manifest.total_files == len(records)


# ===========================================================================
# 8. Dedup report accessible via manifest.dedup_report
# ===========================================================================

def test_manifest_dedup_report_accessible():
    _DUP = "deadbeef" * 8
    records = [
        _make_record("proj_a/cad/part.step", content_hash=_DUP),
        _make_record("proj_a/cad/part_copy.step", content_hash=_DUP),
        _make_record("proj_a/code/main.py"),
    ]
    _, manifest = _run_full_workflow(records)
    assert hasattr(manifest, "dedup_report")
    assert len(manifest.dedup_report.exact_groups) >= 1


# ===========================================================================
# 9. ScaffoldPlan for a CAD project has "cad" in its dirs
# ===========================================================================

def test_scaffold_plan_cad_dir_present():
    records = [
        _make_record("guitar_body/cad/body.step", 100_000),
        _make_record("guitar_body/cad/neck_pocket.dxf", 50_000),
    ]
    items = classify_archive(records)
    plan = plan_scaffold("guitar_body", items)
    dir_paths = [d.path for d in plan.dirs]
    assert "cad" in dir_paths


# ===========================================================================
# 10. ScaffoldPlan LFS rule fires for >100 MB item
# ===========================================================================

def test_scaffold_plan_lfs_rule_for_large_binary():
    records = [
        _make_record("big_project/media/timelapse.mp4", size_bytes=150_000_000),
        _make_record("big_project/code/main.py", size_bytes=5_000),
    ]
    items = classify_archive(records)
    plan = plan_scaffold("big_project", items)
    assert len(plan.lfs_rules) >= 1
    assert plan.large_binary_count >= 1


# ===========================================================================
# 11. RepoManifest entries have provenance_confidence set
# ===========================================================================

def test_repo_manifest_entries_have_provenance_confidence():
    records = _basic_records()
    items = classify_archive(records)
    project_items = [i for i in items if i.inferred_project == "synth_v2"]
    plan = plan_scaffold("synth_v2", project_items)
    repo_manifest = build_manifest(plan, project_items)
    for section in repo_manifest.sections:
        for entry in section.entries:
            assert entry.provenance_confidence in ("high", "medium", "low")


# ===========================================================================
# 12. MigrationPlan ADD for new file not in existing_tree
# ===========================================================================

def test_migration_plan_add_for_new_file():
    records = _basic_records()
    items = classify_archive(records)
    project_items = [i for i in items if i.inferred_project == "synth_v2"]
    plan = plan_scaffold("synth_v2", project_items)
    repo_manifest = build_manifest(plan, project_items)
    migration = plan_migration(repo_manifest, existing_tree={})
    assert len(migration.adds) > 0
    assert all(a.action == MigrationAction.ADD for a in migration.adds)


# ===========================================================================
# 13. MigrationPlan SKIP for file already in tree with same hash
# ===========================================================================

def test_migration_plan_skip_for_matching_hash():
    records = [_make_record("lamp/cad/shade.step", 40_000)]
    items = classify_archive(records)
    plan = plan_scaffold("lamp", items)
    repo_manifest = build_manifest(plan, items)
    # Build existing_tree from the manifest so hashes match
    existing_tree = {
        entry.dest_path: entry.content_hash
        for section in repo_manifest.sections
        for entry in section.entries
    }
    migration = plan_migration(repo_manifest, existing_tree)
    assert len(migration.skips) == len(items)
    assert len(migration.adds) == 0


# ===========================================================================
# 14. MigrationPlan REMOVE for orphan in existing_tree
# ===========================================================================

def test_migration_plan_remove_for_orphan():
    records = [_make_record("lamp/cad/shade.step", 40_000)]
    items = classify_archive(records)
    plan = plan_scaffold("lamp", items)
    repo_manifest = build_manifest(plan, items)
    existing_tree = {"misc/stale_old_file.txt": "aabbccdd"}
    migration = plan_migration(repo_manifest, existing_tree)
    assert len(migration.removes) == 1
    assert migration.removes[0].dest_path == "misc/stale_old_file.txt"


# ===========================================================================
# 15. DedupReport from workflow: exact_groups present when duplicates exist
# ===========================================================================

def test_dedup_exact_groups_when_duplicates_present():
    _DUP = "cafe" * 16
    records = [
        _make_record("drone/cad/frame.step", content_hash=_DUP),
        _make_record("drone/cad/frame_copy.step", content_hash=_DUP),
    ]
    _, manifest = _run_full_workflow(records)
    assert len(manifest.dedup_report.exact_groups) >= 1


# ===========================================================================
# 16. RecoveryManifest.export_dict() is JSON-serialisable
# ===========================================================================

def test_recovery_manifest_export_dict_json_serialisable():
    _, manifest = _run_full_workflow()
    d = manifest.export_dict()
    serialised = json.dumps(d)
    assert isinstance(serialised, str)
    assert len(serialised) > 0


# ===========================================================================
# 17. RecoveryWorkflow.summary_lines() returns list of non-empty strings
# ===========================================================================

def test_workflow_summary_lines_non_empty():
    wf, _ = _run_full_workflow()
    lines = wf.summary_lines()
    assert isinstance(lines, list)
    assert len(lines) > 0
    for line in lines:
        assert isinstance(line, str)
        assert len(line.strip()) > 0


# ===========================================================================
# 18. classify_archive produces correct FileKind per item
# ===========================================================================

def test_classify_archive_correct_kinds():
    records = [
        _make_record("proj/cad/body.step"),
        _make_record("proj/photos/shot.jpg"),
        _make_record("proj/docs/readme.pdf"),
        _make_record("proj/code/main.py"),
        _make_record("proj/media/video.mp4"),
    ]
    items = classify_archive(records)
    kinds = [i.kind for i in items]
    assert FileKind.CAD   in kinds
    assert FileKind.PHOTO in kinds
    assert FileKind.DOC   in kinds
    assert FileKind.CODE  in kinds
    assert FileKind.MEDIA in kinds


# ===========================================================================
# 19. EvidenceLedger.audit() returns dict with "facts" and "inferences" keys
# ===========================================================================

def test_evidence_ledger_audit_keys():
    ledger = EvidenceLedger(project="test_proj")
    ledger.add(EvidenceEntry(
        kind=EvidenceKind.FACT,
        subject="test/file.step",
        claim="file exists",
        source="archive byte-stream",
    ))
    ledger.add(EvidenceEntry(
        kind=EvidenceKind.INFERRED,
        subject="test/file.step",
        claim="belongs to project test_proj",
        source="path heuristic",
        confidence="medium",
    ))
    result = ledger.audit()
    assert "facts" in result
    assert "inferences" in result or "inferred" in result


# ===========================================================================
# 20. plan_scaffold with no items returns empty dirs
# ===========================================================================

def test_plan_scaffold_no_items_empty_dirs():
    plan = plan_scaffold("empty_project", [])
    assert plan.dirs == []
    assert plan.item_count == 0


# ===========================================================================
# 21. plan_scaffold with large binary produces LFS rule
# ===========================================================================

def test_plan_scaffold_large_binary_lfs_rule():
    records = [_make_record("vid/media/clip.mp4", size_bytes=200_000_000)]
    items = classify_archive(records)
    plan = plan_scaffold("vid", items)
    assert len(plan.lfs_rules) == 1
    assert plan.lfs_rules[0].source_path == "vid/media/clip.mp4"


# ===========================================================================
# 22. detect_duplicates with no items returns empty DedupReport
# ===========================================================================

def test_detect_duplicates_empty_input():
    report = detect_duplicates([])
    assert report.total_items == 0
    assert report.duplicate_count == 0
    assert report.exact_groups == []
    assert report.near_dup_groups == []
    assert report.stale_pairs == []


# ===========================================================================
# 23. WorkflowConfig min_items_per_project lumps small projects
# ===========================================================================

def test_workflow_config_min_items_lumps_small_projects():
    # Two tiny solo items that should be lumped into "misc"
    records = [
        _make_record("solo_project_a/cad/part.step"),
        _make_record("solo_project_b/docs/note.pdf"),
        # Larger group that should survive
        _make_record("big_project/cad/part1.step"),
        _make_record("big_project/cad/part2.step"),
        _make_record("big_project/code/main.py"),
    ]
    cfg = WorkflowConfig(min_items_per_project=2, unknown_project_label="misc")
    wf = RecoveryWorkflow(config=cfg)
    wf.ingest(records)
    wf.run()
    manifest = wf.build_manifest()
    project_names = {pg.project for pg in manifest.projects}
    # big_project has 3 items → survives; solo projects (1 item each) → lumped
    assert "big_project" in project_names
    assert "misc" in project_names
    assert "solo_project_a" not in project_names
    assert "solo_project_b" not in project_names


# ===========================================================================
# 24. RepoManifest.export_json() produces valid JSON string
# ===========================================================================

def test_repo_manifest_export_json_valid():
    records = [_make_record("proj/cad/part.step", 10_000)]
    items = classify_archive(records)
    plan = plan_scaffold("proj", items)
    repo_manifest = build_manifest(plan, items)
    j = repo_manifest.export_json()
    assert isinstance(j, str)
    parsed = json.loads(j)
    assert parsed["project"] == "proj"


# ===========================================================================
# 25. MigrationPlan.has_conflicts False when no conflicts
# ===========================================================================

def test_migration_plan_no_conflicts_when_hashes_match():
    records = [_make_record("desk/cad/top.step", 50_000)]
    items = classify_archive(records)
    plan = plan_scaffold("desk", items)
    repo_manifest = build_manifest(plan, items)
    existing_tree = {
        entry.dest_path: entry.content_hash
        for section in repo_manifest.sections
        for entry in section.entries
    }
    migration = plan_migration(repo_manifest, existing_tree)
    assert migration.has_conflicts is False


# ===========================================================================
# 26. DedupReport unique_item_count = total - duplicates
# ===========================================================================

def test_dedup_report_unique_item_count():
    _DUP = "abcd" * 16
    records = [
        _make_record("p/a/file.step", content_hash=_DUP),
        _make_record("p/b/file.step", content_hash=_DUP),
        _make_record("p/c/unique.step"),
    ]
    items = classify_archive(records)
    report = detect_duplicates(items)
    assert report.unique_item_count == report.total_items - report.duplicate_count


# ===========================================================================
# 27. ArchiveItem.is_large_binary True for >100 MB
# ===========================================================================

def test_archive_item_is_large_binary():
    big = ArchiveItem(path="proj/media/big.mp4", size_bytes=101 * 1024 * 1024)
    small = ArchiveItem(path="proj/cad/part.step", size_bytes=50_000)
    assert big.is_large_binary is True
    assert small.is_large_binary is False


# ===========================================================================
# 28. FileRecord.compute_hash_stub is deterministic
# ===========================================================================

def test_file_record_compute_hash_stub_deterministic():
    r = _make_record("some/path/file.step")
    h1 = r.compute_hash_stub()
    h2 = r.compute_hash_stub()
    assert h1 == h2
    assert isinstance(h1, str)
    assert len(h1) == 64  # SHA-256 hex


# ===========================================================================
# 29. ScaffoldPlan.export_dict() returns dict with "project" key
# ===========================================================================

def test_scaffold_plan_export_dict_has_project_key():
    records = [_make_record("lamp/cad/shade.dxf")]
    items = classify_archive(records)
    plan = plan_scaffold("lamp", items)
    d = plan.export_dict()
    assert isinstance(d, dict)
    assert "project" in d
    assert d["project"] == "lamp"


# ===========================================================================
# 30. WorkflowStage enum values are strings
# ===========================================================================

def test_workflow_stage_enum_values_are_strings():
    for stage in WorkflowStage:
        assert isinstance(stage.value, str)
        assert len(stage.value) > 0


# ===========================================================================
# Bonus: EvidenceLedger.from_archive_items classmethod works
# ===========================================================================

def test_evidence_ledger_from_archive_items():
    records = [
        _make_record("proj/cad/part.step"),
        _make_record("proj/code/main.py"),
    ]
    items = classify_archive(records)
    ledger = EvidenceLedger.from_archive_items("proj", items)
    assert ledger.project == "proj"
    assert len(ledger.facts()) >= 1
    assert len(ledger.inferences()) >= 1


# ===========================================================================
# Bonus: workflow stage progression is correct
# ===========================================================================

def test_workflow_stage_progression():
    records = _basic_records()
    wf = RecoveryWorkflow()
    assert wf.stage == WorkflowStage.IDLE
    wf.ingest(records)
    assert wf.stage == WorkflowStage.INGESTED
    wf.classify()
    assert wf.stage == WorkflowStage.CLASSIFIED
    wf.dedup()
    assert wf.stage == WorkflowStage.DEDUPED
    wf.group()
    assert wf.stage == WorkflowStage.GROUPED
    wf.plan()
    assert wf.stage == WorkflowStage.PLANNED


# ===========================================================================
# Bonus: build_manifest raises when plan has no items
# ===========================================================================

def test_build_manifest_no_items_returns_empty_sections():
    plan = plan_scaffold("empty", [])
    repo = build_manifest(plan, [])
    assert repo.total_entries == 0
    assert repo.sections == []


# ===========================================================================
# Bonus: near-dup detection fires for same filename with similar sizes
# ===========================================================================

def test_near_dup_detection_same_filename_similar_sizes():
    records = [
        _make_record("proj_a/photos/shot.jpg", size_bytes=3_000_000),
        _make_record("proj_b/photos/shot.jpg", size_bytes=3_050_000),  # ~1.6% larger
    ]
    items = classify_archive(records)
    report = detect_duplicates(items)
    assert len(report.near_dup_groups) >= 1


# ===========================================================================
# Bonus: stale pair detection fires for same stem+ext with different mtimes
# ===========================================================================

def test_stale_pair_detection():
    records = [
        _make_record("proj/v1/template.dxf", mtime=1_714_000_000.0),
        _make_record("proj/v2/template.dxf", mtime=1_715_000_000.0),
    ]
    items = classify_archive(records)
    report = detect_duplicates(items)
    assert len(report.stale_pairs) >= 1
    stale = report.stale_pairs[0]
    assert stale.newer.mtime > stale.older.mtime
