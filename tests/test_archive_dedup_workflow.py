"""
Tests for archive_recovery.dedup and archive_recovery.workflow.

All tests are deterministic — no I/O, no randomness, no mocking.
"""

from __future__ import annotations

import pytest

from archive_recovery.dedup import (
    DedupConfig,
    DedupReport,
    ExactDupGroup,
    NearDupGroup,
    StalePair,
    detect_duplicates,
)
from archive_recovery.models import ArchiveItem, FileKind, FileRecord
from archive_recovery.workflow import (
    ProjectGroup,
    RecoveryManifest,
    RecoveryWorkflow,
    WorkflowConfig,
    WorkflowStage,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _item(
    path: str,
    size: int = 2048,
    mtime: float = 1_000_000.0,
    content_hash: str = "",
    kind: FileKind = FileKind.UNKNOWN,
    project: str = "proj_a",
) -> ArchiveItem:
    """Build a minimal ArchiveItem without going through classify_archive."""
    return ArchiveItem(
        path=path,
        size_bytes=size,
        mtime=mtime,
        content_hash=content_hash,
        kind=kind,
        inferred_project=project,
    )


def _record(path: str, size: int = 2048, mtime: float = 1_000_000.0) -> FileRecord:
    return FileRecord(path=path, size_bytes=size, mtime=mtime)


# ===========================================================================
# ExactDupGroup unit tests
# ===========================================================================

class TestExactDupGroupSavings:
    def test_savings_bytes_two_items(self):
        items = [
            _item("a/file.txt", size=1024, content_hash="abc"),
            _item("b/file.txt", size=1024, content_hash="abc"),
        ]
        grp = ExactDupGroup(
            content_hash="abc",
            items=items,
            keep_path="a/file.txt",
            drop_paths=["b/file.txt"],
        )
        assert grp.savings_bytes == 1024

    def test_savings_bytes_three_items(self):
        items = [
            _item("a/file.txt", size=500, content_hash="xyz"),
            _item("b/file.txt", size=500, content_hash="xyz"),
            _item("c/file.txt", size=500, content_hash="xyz"),
        ]
        grp = ExactDupGroup(
            content_hash="xyz",
            items=items,
            keep_path="a/file.txt",
            drop_paths=["b/file.txt", "c/file.txt"],
        )
        assert grp.savings_bytes == 1000

    def test_savings_bytes_empty_items(self):
        grp = ExactDupGroup(
            content_hash="nohash",
            items=[],
            keep_path="",
            drop_paths=[],
        )
        assert grp.savings_bytes == 0


# ===========================================================================
# detect_duplicates — empty / all-unique
# ===========================================================================

class TestDetectDuplicatesEdgeCases:
    def test_empty_list_returns_empty_report(self):
        report = detect_duplicates([])
        assert report.exact_groups == []
        assert report.near_dup_groups == []
        assert report.stale_pairs == []
        assert report.total_items == 0
        assert report.duplicate_count == 0
        assert report.potential_savings_bytes == 0

    def test_all_unique_items_no_groups(self):
        items = [
            _item("a/foo.step", content_hash="h1"),
            _item("b/bar.py", content_hash="h2"),
            _item("c/baz.mp4", content_hash="h3"),
        ]
        report = detect_duplicates(items)
        assert report.exact_groups == []
        assert not report.has_duplicates

    def test_total_items_counted_correctly(self):
        items = [_item(f"p{i}/f.txt", content_hash=f"h{i}") for i in range(7)]
        report = detect_duplicates(items)
        assert report.total_items == 7


# ===========================================================================
# Exact duplicate detection
# ===========================================================================

class TestExactDuplicates:
    def test_three_items_same_hash_one_group(self):
        h = "deadbeef" * 8
        items = [
            _item("a/file.step", content_hash=h, size=4096),
            _item("b/file.step", content_hash=h, size=4096),
            _item("c/file.step", content_hash=h, size=4096),
        ]
        report = detect_duplicates(items)
        assert len(report.exact_groups) == 1
        grp = report.exact_groups[0]
        assert grp.content_hash == h
        assert len(grp.items) == 3
        assert len(grp.drop_paths) == 2

    def test_keep_path_is_deepest(self):
        h = "cafe" * 16
        items = [
            _item("a/file.step", content_hash=h),
            _item("a/b/c/file.step", content_hash=h),   # deepest (3 slashes)
            _item("a/b/file.step", content_hash=h),
        ]
        report = detect_duplicates(items)
        grp = report.exact_groups[0]
        assert grp.keep_path == "a/b/c/file.step"
        assert "a/file.step" in grp.drop_paths
        assert "a/b/file.step" in grp.drop_paths

    def test_keep_path_tiebreak_alphabetical(self):
        h = "babe" * 16
        # Both at same depth (same number of slashes)
        items = [
            _item("z/omega/file.step", content_hash=h),
            _item("a/alpha/file.step", content_hash=h),
        ]
        report = detect_duplicates(items)
        grp = report.exact_groups[0]
        # Alphabetically smaller path should be kept
        assert grp.keep_path == "a/alpha/file.step"
        assert grp.drop_paths == ["z/omega/file.step"]

    def test_multiple_hash_groups(self):
        items = [
            _item("a/x.txt", content_hash="hash1"),
            _item("b/x.txt", content_hash="hash1"),
            _item("c/y.txt", content_hash="hash2"),
            _item("d/y.txt", content_hash="hash2"),
        ]
        report = detect_duplicates(items)
        assert len(report.exact_groups) == 2

    def test_duplicate_count_sums_drop_paths(self):
        h1 = "h1" + "0" * 62
        h2 = "h2" + "0" * 62
        items = [
            _item("a/f.txt", content_hash=h1),
            _item("b/f.txt", content_hash=h1),
            _item("c/g.txt", content_hash=h2),
            _item("d/g.txt", content_hash=h2),
            _item("e/g.txt", content_hash=h2),
        ]
        report = detect_duplicates(items)
        # group h1: 1 drop; group h2: 2 drops => total 3
        assert report.duplicate_count == 3

    def test_potential_savings_bytes(self):
        h = "ff" * 32
        items = [
            _item("x/a.step", content_hash=h, size=1000),
            _item("y/a.step", content_hash=h, size=1000),
            _item("z/a.step", content_hash=h, size=1000),
        ]
        report = detect_duplicates(items)
        # 2 drops × 1000 bytes each
        assert report.potential_savings_bytes == 2000

    def test_run_exact_false_skips_exact_detection(self):
        h = "aa" * 32
        items = [
            _item("a/file.step", content_hash=h),
            _item("b/file.step", content_hash=h),
        ]
        cfg = DedupConfig(run_exact=False)
        report = detect_duplicates(items, cfg)
        assert report.exact_groups == []
        assert report.duplicate_count == 0


# ===========================================================================
# Near-duplicate detection
# ===========================================================================

class TestNearDuplicates:
    def test_same_filename_within_tolerance(self):
        items = [
            _item("a/photo.jpg", size=10_000),
            _item("b/photo.jpg", size=10_200),   # ~2% difference
        ]
        report = detect_duplicates(items, DedupConfig(run_exact=False, run_stale_versions=False))
        assert len(report.near_dup_groups) == 1
        grp = report.near_dup_groups[0]
        assert grp.filename == "photo.jpg"
        assert len(grp.items) == 2

    def test_same_filename_sizes_differ_too_much(self):
        items = [
            _item("a/photo.jpg", size=10_000),
            _item("b/photo.jpg", size=15_000),   # 33% difference
        ]
        cfg = DedupConfig(run_exact=False, run_stale_versions=False, size_tolerance_pct=5.0)
        report = detect_duplicates(items, cfg)
        assert report.near_dup_groups == []

    def test_tiny_files_excluded(self):
        # Both below 1024 bytes threshold
        items = [
            _item("a/config.txt", size=100),
            _item("b/config.txt", size=102),
        ]
        cfg = DedupConfig(run_exact=False, run_stale_versions=False)
        report = detect_duplicates(items, cfg)
        assert report.near_dup_groups == []

    def test_mixed_large_and_tiny_files_excluded(self):
        # Only one file is large enough — should not form a near-dup group
        items = [
            _item("a/config.txt", size=500),
            _item("b/config.txt", size=5000),
        ]
        cfg = DedupConfig(run_exact=False, run_stale_versions=False, min_size_bytes_for_near_dup=1024)
        report = detect_duplicates(items, cfg)
        # Only one item passes the size filter; not a group
        assert report.near_dup_groups == []

    def test_filename_comparison_case_insensitive(self):
        items = [
            _item("a/Photo.JPG", size=10_000),
            _item("b/photo.jpg", size=10_100),
        ]
        cfg = DedupConfig(run_exact=False, run_stale_versions=False)
        report = detect_duplicates(items, cfg)
        assert len(report.near_dup_groups) == 1

    def test_run_near_dup_false_skips(self):
        items = [
            _item("a/photo.jpg", size=10_000),
            _item("b/photo.jpg", size=10_000),
        ]
        cfg = DedupConfig(run_near_dup=False)
        report = detect_duplicates(items, cfg)
        assert report.near_dup_groups == []

    def test_near_dup_note_contains_directory_count(self):
        items = [
            _item("x/logo.png", size=5_000),
            _item("y/logo.png", size=5_100),
            _item("z/logo.png", size=4_900),
        ]
        cfg = DedupConfig(run_exact=False, run_stale_versions=False)
        report = detect_duplicates(items, cfg)
        assert len(report.near_dup_groups) == 1
        assert "3" in report.near_dup_groups[0].note


# ===========================================================================
# Stale version detection
# ===========================================================================

class TestStaleVersions:
    def test_two_items_same_stem_ext_different_mtime(self):
        items = [
            _item("a/design.step", mtime=1_000.0, content_hash="h1"),
            _item("b/design.step", mtime=2_000.0, content_hash="h2"),
        ]
        report = detect_duplicates(items, DedupConfig(run_exact=False, run_near_dup=False))
        assert len(report.stale_pairs) == 1
        pair = report.stale_pairs[0]
        assert pair.stem == "design"
        assert pair.extension == "step"
        assert pair.newer.mtime == 2_000.0
        assert pair.older.mtime == 1_000.0
        assert pair.mtime_diff_seconds == pytest.approx(1_000.0)

    def test_three_items_same_stem_emits_min_max_pair(self):
        items = [
            _item("a/rev.py", mtime=100.0, content_hash="h1"),
            _item("b/rev.py", mtime=500.0, content_hash="h2"),
            _item("c/rev.py", mtime=300.0, content_hash="h3"),
        ]
        report = detect_duplicates(items, DedupConfig(run_exact=False, run_near_dup=False))
        assert len(report.stale_pairs) == 1
        pair = report.stale_pairs[0]
        assert pair.newer.mtime == 500.0
        assert pair.older.mtime == 100.0

    def test_same_mtime_no_stale_pair(self):
        items = [
            _item("a/doc.pdf", mtime=999.0, content_hash="h1"),
            _item("b/doc.pdf", mtime=999.0, content_hash="h2"),
        ]
        cfg = DedupConfig(run_exact=False, run_near_dup=False)
        report = detect_duplicates(items, cfg)
        # newer == older → no meaningful stale pair
        assert report.stale_pairs == []

    def test_run_stale_versions_false_skips(self):
        items = [
            _item("a/model.stl", mtime=1.0, content_hash="h1"),
            _item("b/model.stl", mtime=9.0, content_hash="h2"),
        ]
        cfg = DedupConfig(run_stale_versions=False)
        report = detect_duplicates(items, cfg)
        assert report.stale_pairs == []


# ===========================================================================
# DedupReport properties
# ===========================================================================

class TestDedupReportProperties:
    def test_has_duplicates_true(self):
        h = "ff" * 32
        items = [
            _item("a/x.txt", content_hash=h),
            _item("b/x.txt", content_hash=h),
        ]
        report = detect_duplicates(items)
        assert report.has_duplicates is True

    def test_has_duplicates_false(self):
        items = [
            _item("a/x.txt", content_hash="h1"),
            _item("b/y.txt", content_hash="h2"),
        ]
        report = detect_duplicates(items)
        assert report.has_duplicates is False

    def test_unique_item_count(self):
        h = "ee" * 32
        items = [
            _item("a/x.txt", content_hash=h, size=100),
            _item("b/x.txt", content_hash=h, size=100),
            _item("c/z.txt", content_hash="other" + "0" * 59),
        ]
        report = detect_duplicates(items)
        # 1 drop_path → duplicate_count == 1; unique == 2
        assert report.unique_item_count == 2

    def test_potential_savings_sums_across_groups(self):
        h1 = "a1" * 32
        h2 = "b2" * 32
        items = [
            _item("p/a.txt", content_hash=h1, size=1000),
            _item("q/a.txt", content_hash=h1, size=1000),
            _item("p/b.txt", content_hash=h2, size=500),
            _item("q/b.txt", content_hash=h2, size=500),
        ]
        report = detect_duplicates(items)
        # h1 saves 1000, h2 saves 500
        assert report.potential_savings_bytes == 1500


# ===========================================================================
# Workflow tests
# ===========================================================================

class TestWorkflowInitialState:
    def test_starts_at_idle(self):
        wf = RecoveryWorkflow()
        assert wf.stage == WorkflowStage.IDLE

    def test_default_config(self):
        wf = RecoveryWorkflow()
        assert isinstance(wf.config, WorkflowConfig)


class TestWorkflowIngest:
    def test_ingest_transitions_to_ingested(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("a/b.py")])
        assert wf.stage == WorkflowStage.INGESTED

    def test_ingest_stores_records(self):
        recs = [_record("x/y.py"), _record("z/w.stl")]
        wf = RecoveryWorkflow()
        wf.ingest(recs)
        assert len(wf._raw_records) == 2

    def test_ingest_twice_replaces_records(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("a/b.py")])
        wf.ingest([_record("c/d.py"), _record("e/f.py")])
        assert len(wf._raw_records) == 2


class TestWorkflowClassify:
    def test_classify_transitions_to_classified(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("proj/foo.py")])
        wf.classify()
        assert wf.stage == WorkflowStage.CLASSIFIED

    def test_classify_produces_archive_items(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("proj/foo.py"), _record("proj/bar.step")])
        items = wf.classify()
        assert len(items) == 2
        assert all(isinstance(it, ArchiveItem) for it in items)

    def test_classify_before_ingest_raises(self):
        wf = RecoveryWorkflow()
        with pytest.raises(RuntimeError):
            wf.classify()


class TestWorkflowDedup:
    def test_dedup_transitions_to_deduped(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("p/a.py"), _record("p/b.py")])
        wf.classify()
        wf.dedup()
        assert wf.stage == WorkflowStage.DEDUPED

    def test_dedup_stores_report(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("p/a.py")])
        wf.classify()
        report = wf.dedup()
        assert isinstance(report, DedupReport)
        assert wf._dedup_report is report

    def test_dedup_before_classify_raises(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("p/a.py")])
        with pytest.raises(RuntimeError):
            wf.dedup()


class TestWorkflowGroup:
    def test_group_transitions_to_grouped(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("alpha/a.py"), _record("beta/b.step")])
        wf.classify()
        wf.dedup()
        wf.group()
        assert wf.stage == WorkflowStage.GROUPED

    def test_group_by_project(self):
        wf = RecoveryWorkflow()
        # Two different first-level dirs → two projects
        wf.ingest([_record("alpha/a.py"), _record("beta/b.step")])
        wf.classify()
        wf.dedup()
        groups = wf.group()
        assert "alpha" in groups
        assert "beta" in groups

    def test_unknown_project_remapped_to_misc(self):
        # A file with no directory ends up as unknown_project
        wf = RecoveryWorkflow()
        wf.ingest([_record("bare_file.step")])
        wf.classify()
        wf.dedup()
        groups = wf.group()
        # The classifier maps no-directory files to a stem-based project;
        # but if inferred_project == "unknown_project" it should remap.
        # We inject an item manually to test the remap logic:
        wf._items = [_item("bare.step", project="unknown_project")]
        wf._dedup_report = detect_duplicates(wf._items)
        wf.stage = WorkflowStage.DEDUPED
        groups = wf.group()
        assert "misc" in groups
        assert "unknown_project" not in groups

    def test_min_items_per_project_lump_to_misc(self):
        cfg = WorkflowConfig(min_items_per_project=2)
        wf = RecoveryWorkflow(config=cfg)
        # Project "solo" has only 1 item → should be lumped into misc
        wf._items = [
            _item("solo/a.py", project="solo"),
            _item("team/b.py", project="team"),
            _item("team/c.py", project="team"),
        ]
        wf._raw_records = []
        wf.stage = WorkflowStage.CLASSIFIED
        wf._dedup_report = detect_duplicates(wf._items)
        wf.stage = WorkflowStage.DEDUPED
        groups = wf.group()
        assert "solo" not in groups
        assert "misc" in groups
        assert len(groups["misc"]) == 1

    def test_group_before_dedup_raises(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("a/b.py")])
        wf.classify()
        with pytest.raises(RuntimeError):
            wf.group()


class TestWorkflowPlan:
    def test_plan_transitions_to_planned(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("proj/a.step")])
        wf.classify()
        wf.dedup()
        wf.group()
        wf.plan()
        assert wf.stage == WorkflowStage.PLANNED

    def test_plan_produces_one_scaffold_per_project(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("alpha/a.step"), _record("beta/b.py")])
        wf.classify()
        wf.dedup()
        wf.group()
        plans = wf.plan()
        assert "alpha" in plans
        assert "beta" in plans

    def test_plan_before_classify_raises(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("a/b.py")])
        with pytest.raises(RuntimeError):
            wf.plan()


class TestWorkflowRun:
    def test_run_transitions_to_complete(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("proj/a.py"), _record("proj/b.step")])
        wf.run()
        assert wf.stage == WorkflowStage.COMPLETE

    def test_run_full_pipeline_executes_all_stages(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("alpha/a.py"), _record("beta/b.step")])
        wf.run()
        assert len(wf._items) == 2
        assert wf._dedup_report is not None
        assert len(wf._groups) >= 1
        assert len(wf._scaffold_plans) >= 1


class TestBuildManifest:
    def test_manifest_correct_total_files(self):
        wf = RecoveryWorkflow()
        records = [_record(f"proj/f{i}.py") for i in range(5)]
        wf.ingest(records)
        wf.run()
        manifest = wf.build_manifest()
        assert manifest.total_files == 5

    def test_manifest_project_count(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("alpha/a.py"), _record("beta/b.step")])
        wf.run()
        manifest = wf.build_manifest()
        assert manifest.project_count == 2

    def test_manifest_dedup_info(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("p/a.py")])
        wf.run()
        manifest = wf.build_manifest()
        assert isinstance(manifest.dedup_report, DedupReport)
        assert manifest.duplicate_count == manifest.dedup_report.duplicate_count

    def test_manifest_stage_recorded(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("p/a.py")])
        wf.run()
        manifest = wf.build_manifest()
        assert manifest.stage == WorkflowStage.COMPLETE

    def test_manifest_before_group_raises(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("p/a.py")])
        wf.classify()
        wf.dedup()
        with pytest.raises(RuntimeError):
            wf.build_manifest()

    def test_export_dict_returns_plain_dict(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("proj/a.step")])
        wf.run()
        manifest = wf.build_manifest()
        d = manifest.export_dict()
        assert isinstance(d, dict)
        assert "total_files" in d
        assert "projects" in d
        assert "dedup_report" in d
        assert "stage" in d
        # Ensure no nested Pydantic objects
        import json
        json.dumps(d)  # should not raise

    def test_export_dict_stage_is_string(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("p/a.py")])
        wf.run()
        d = wf.build_manifest().export_dict()
        assert isinstance(d["stage"], str)


class TestSummaryLines:
    def test_summary_lines_returns_nonempty_list(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("proj/a.py")])
        lines = wf.summary_lines()
        assert isinstance(lines, list)
        assert len(lines) > 0
        assert all(isinstance(ln, str) for ln in lines)

    def test_summary_lines_contains_stage(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("proj/a.py")])
        wf.run()
        lines = wf.summary_lines()
        joined = "\n".join(lines)
        assert "COMPLETE" in joined

    def test_summary_lines_after_run_contains_projects(self):
        wf = RecoveryWorkflow()
        wf.ingest([_record("alpha/a.py"), _record("beta/b.step")])
        wf.run()
        lines = wf.summary_lines()
        joined = "\n".join(lines)
        assert "Projects" in joined


class TestMaxProjectsCap:
    def test_max_projects_cap_warning(self):
        cfg = WorkflowConfig(max_projects=2)
        wf = RecoveryWorkflow(config=cfg)
        # 5 distinct projects
        wf._items = [_item(f"proj{i}/a.py", project=f"proj{i}") for i in range(5)]
        wf._raw_records = []
        wf.stage = WorkflowStage.CLASSIFIED
        wf._dedup_report = detect_duplicates(wf._items)
        wf.stage = WorkflowStage.DEDUPED
        groups = wf.group()
        # The cap keeps max_projects entries alphabetically; the rest overflow
        # into misc, so the final group count is at most max_projects + 1 (misc).
        assert len(groups) <= cfg.max_projects + 1
        # A warning must be emitted
        assert any("max_projects" in w or "cap" in w for w in wf._warnings)
        # The misc bucket must contain the overflow items
        assert "misc" in groups


class TestLargeArchive:
    def test_large_archive_runs_without_error(self):
        records = [
            _record(f"project_{i % 10}/file_{i}.py", size=2000 + i * 10)
            for i in range(50)
        ]
        wf = RecoveryWorkflow()
        wf.ingest(records)
        wf.run()
        manifest = wf.build_manifest()
        assert manifest.total_files == 50
        assert manifest.project_count >= 1
