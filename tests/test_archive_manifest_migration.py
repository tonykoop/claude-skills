"""
Tests for archive_recovery.manifest and archive_recovery.migration.

35+ deterministic tests; no I/O, no randomness.
"""

from __future__ import annotations

import json

import pytest

from archive_recovery.models import ArchiveItem, FileKind
from archive_recovery.scaffold import plan_scaffold, ScaffoldPlan, LFSRule, ScaffoldedDir
from archive_recovery.evidence import EvidenceLedger
from archive_recovery.manifest import (
    ManifestEntry,
    ManifestSection,
    RepoManifest,
    build_manifest,
    build_batch_manifests,
)
from archive_recovery.migration import (
    MigrationAction,
    MigrationItem,
    MigrationPlan,
    plan_migration,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _item(
    path: str,
    kind: FileKind = FileKind.CAD,
    size_bytes: int = 100,
    kind_is_inferred: bool = False,
    project_is_inferred: bool = False,
    project: str = "test_project",
    content_hash: str = "",
) -> ArchiveItem:
    return ArchiveItem(
        path=path,
        kind=kind,
        size_bytes=size_bytes,
        kind_is_inferred=kind_is_inferred,
        project_is_inferred=project_is_inferred,
        inferred_project=project,
        content_hash=content_hash,
    )


def _make_plan_and_items(
    project: str = "test_project",
    items: list[ArchiveItem] | None = None,
) -> tuple[ScaffoldPlan, list[ArchiveItem]]:
    if items is None:
        items = [_item("cad/part.step", project=project)]
    plan = plan_scaffold(project, items)
    return plan, items


def _make_manifest(
    project: str = "test_project",
    items: list[ArchiveItem] | None = None,
) -> RepoManifest:
    plan, actual_items = _make_plan_and_items(project, items)
    return build_manifest(plan, actual_items)


# ---------------------------------------------------------------------------
# ManifestSection properties
# ---------------------------------------------------------------------------

class TestManifestSection:
    def test_total_size_bytes_empty(self):
        section = ManifestSection(dest_dir="cad", kind=FileKind.CAD)
        assert section.total_size_bytes == 0

    def test_total_size_bytes_sums_entries(self):
        entries = [
            ManifestEntry(
                source_path="a.step", dest_path="cad/a.step",
                kind=FileKind.CAD, size_bytes=1000,
            ),
            ManifestEntry(
                source_path="b.step", dest_path="cad/b.step",
                kind=FileKind.CAD, size_bytes=2500,
            ),
        ]
        section = ManifestSection(dest_dir="cad", kind=FileKind.CAD, entries=entries)
        assert section.total_size_bytes == 3500

    def test_lfs_entry_count_none(self):
        entries = [
            ManifestEntry(
                source_path="a.step", dest_path="cad/a.step",
                kind=FileKind.CAD, size_bytes=100, is_lfs_tracked=False,
            ),
        ]
        section = ManifestSection(dest_dir="cad", kind=FileKind.CAD, entries=entries)
        assert section.lfs_entry_count == 0

    def test_lfs_entry_count_some(self):
        entries = [
            ManifestEntry(
                source_path="a.step", dest_path="cad/a.step",
                kind=FileKind.CAD, size_bytes=100, is_lfs_tracked=True,
            ),
            ManifestEntry(
                source_path="b.step", dest_path="cad/b.step",
                kind=FileKind.CAD, size_bytes=200, is_lfs_tracked=False,
            ),
            ManifestEntry(
                source_path="c.step", dest_path="cad/c.step",
                kind=FileKind.CAD, size_bytes=300, is_lfs_tracked=True,
            ),
        ]
        section = ManifestSection(dest_dir="cad", kind=FileKind.CAD, entries=entries)
        assert section.lfs_entry_count == 2


# ---------------------------------------------------------------------------
# build_manifest — dest_path construction
# ---------------------------------------------------------------------------

class TestBuildManifestDestPath:
    def test_dest_path_is_dir_slash_filename(self):
        items = [_item("archive/foo/part.step")]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        # CAD files go into "cad/" dir
        all_entries = [e for s in manifest.sections for e in s.entries]
        assert any(e.dest_path == "cad/part.step" for e in all_entries)

    def test_photo_dest_path(self):
        items = [_item("raw/IMG_001.jpg", kind=FileKind.PHOTO)]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        all_entries = [e for s in manifest.sections for e in s.entries]
        assert any(e.dest_path == "photos/IMG_001.jpg" for e in all_entries)

    def test_doc_dest_path(self):
        items = [_item("docs/spec.pdf", kind=FileKind.DOC)]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        all_entries = [e for s in manifest.sections for e in s.entries]
        assert any(e.dest_path == "docs/spec.pdf" for e in all_entries)


# ---------------------------------------------------------------------------
# build_manifest — LFS tracking
# ---------------------------------------------------------------------------

class TestBuildManifestLFS:
    def test_large_item_is_lfs_tracked(self):
        big_size = 200 * 1024 * 1024  # 200 MB
        items = [_item("cad/big.step", size_bytes=big_size)]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        all_entries = [e for s in manifest.sections for e in s.entries]
        lfs_entries = [e for e in all_entries if e.is_lfs_tracked]
        assert len(lfs_entries) == 1
        assert lfs_entries[0].dest_path == "cad/big.step"

    def test_small_item_is_not_lfs_tracked(self):
        items = [_item("cad/small.step", size_bytes=1024)]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        all_entries = [e for s in manifest.sections for e in s.entries]
        assert all(not e.is_lfs_tracked for e in all_entries)


# ---------------------------------------------------------------------------
# build_manifest — provenance_confidence
# ---------------------------------------------------------------------------

class TestBuildManifestConfidence:
    def test_high_confidence_when_neither_inferred(self):
        items = [_item("cad/part.step", kind_is_inferred=False, project_is_inferred=False)]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        all_entries = [e for s in manifest.sections for e in s.entries]
        assert all(e.provenance_confidence == "high" for e in all_entries)

    def test_medium_confidence_when_only_kind_inferred(self):
        items = [_item("cad/part.step", kind_is_inferred=True, project_is_inferred=False)]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        all_entries = [e for s in manifest.sections for e in s.entries]
        assert any(e.provenance_confidence == "medium" for e in all_entries)

    def test_medium_confidence_when_only_project_inferred(self):
        items = [_item("cad/part.step", kind_is_inferred=False, project_is_inferred=True)]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        all_entries = [e for s in manifest.sections for e in s.entries]
        assert any(e.provenance_confidence == "medium" for e in all_entries)

    def test_low_confidence_when_both_inferred(self):
        items = [_item("misc/unknown.dat", kind_is_inferred=True, project_is_inferred=True,
                       kind=FileKind.CAD)]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        all_entries = [e for s in manifest.sections for e in s.entries]
        assert any(e.provenance_confidence == "low" for e in all_entries)


# ---------------------------------------------------------------------------
# build_manifest — warnings
# ---------------------------------------------------------------------------

class TestBuildManifestWarnings:
    def test_warns_about_unknown_kind(self):
        items = [_item("misc/weird.xyz", kind=FileKind.UNKNOWN)]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        assert any("Unknown kind" in w or "unknown" in w.lower() for w in manifest.warnings)

    def test_warns_about_low_confidence(self):
        items = [_item("cad/part.step", kind_is_inferred=True, project_is_inferred=True)]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        assert any("Low confidence" in w or "low" in w.lower() for w in manifest.warnings)

    def test_collision_detection_same_filename(self):
        items = [
            _item("folder_a/part.step", kind=FileKind.CAD),
            _item("folder_b/part.step", kind=FileKind.CAD),
        ]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        collision_warnings = [w for w in manifest.warnings if "ollision" in w or "rename" in w.lower()]
        assert len(collision_warnings) >= 1

    def test_collision_dest_path_disambiguated(self):
        items = [
            _item("a/part.step", kind=FileKind.CAD),
            _item("b/part.step", kind=FileKind.CAD),
        ]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        all_entries = [e for s in manifest.sections for e in s.entries]
        dest_paths = [e.dest_path for e in all_entries]
        # All dest_paths must be unique
        assert len(dest_paths) == len(set(dest_paths))

    def test_no_warnings_for_clean_manifest(self):
        items = [
            _item("cad/part.step", kind=FileKind.CAD,
                  kind_is_inferred=False, project_is_inferred=False),
        ]
        plan, _ = _make_plan_and_items(items=items)
        manifest = build_manifest(plan, items)
        # No low-confidence, no UNKNOWN, no collision
        assert manifest.low_confidence_count == 0


# ---------------------------------------------------------------------------
# RepoManifest methods
# ---------------------------------------------------------------------------

class TestRepoManifest:
    def test_export_json_is_valid_json(self):
        manifest = _make_manifest()
        raw = manifest.export_json()
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)

    def test_export_json_contains_all_top_level_keys(self):
        manifest = _make_manifest()
        parsed = json.loads(manifest.export_json())
        for key in ("project", "sections", "lfs_rules", "gitignore_lines",
                    "readme_content", "evidence_summary", "total_entries",
                    "total_size_bytes", "low_confidence_count", "warnings"):
            assert key in parsed, f"Missing key: {key}"

    def test_to_text_summary_contains_project_name(self):
        manifest = _make_manifest(project="my_synth")
        summary = manifest.to_text_summary()
        assert "my_synth" in summary

    def test_to_text_summary_contains_entry_count(self):
        items = [
            _item("cad/a.step"), _item("cad/b.step"),
        ]
        manifest = _make_manifest(items=items)
        summary = manifest.to_text_summary()
        assert str(manifest.total_entries) in summary

    def test_to_text_summary_header_line(self):
        manifest = _make_manifest(project="robot_arm")
        summary = manifest.to_text_summary()
        assert "=== Repo Manifest: robot_arm ===" in summary

    def test_total_entries_correct(self):
        items = [
            _item("cad/a.step", kind=FileKind.CAD),
            _item("photos/img.jpg", kind=FileKind.PHOTO),
            _item("docs/spec.pdf", kind=FileKind.DOC),
        ]
        manifest = _make_manifest(items=items)
        assert manifest.total_entries == 3

    def test_total_size_bytes_sums_across_sections(self):
        items = [
            _item("cad/a.step", kind=FileKind.CAD, size_bytes=1000),
            _item("photos/img.jpg", kind=FileKind.PHOTO, size_bytes=2000),
        ]
        manifest = _make_manifest(items=items)
        assert manifest.total_size_bytes == 3000

    def test_low_confidence_count(self):
        items = [
            _item("cad/a.step", kind_is_inferred=True, project_is_inferred=True),
            _item("cad/b.step", kind_is_inferred=False, project_is_inferred=False),
        ]
        manifest = _make_manifest(items=items)
        assert manifest.low_confidence_count == 1


# ---------------------------------------------------------------------------
# build_batch_manifests
# ---------------------------------------------------------------------------

class TestBuildBatchManifests:
    def test_returns_one_manifest_per_plan(self):
        items_a = [_item("a/part.step", project="proj_a")]
        items_b = [_item("b/img.jpg", kind=FileKind.PHOTO, project="proj_b")]
        plan_a = plan_scaffold("proj_a", items_a)
        plan_b = plan_scaffold("proj_b", items_b)
        manifests = build_batch_manifests([plan_a, plan_b], items_a + items_b)
        assert len(manifests) == 2

    def test_batch_manifests_correct_projects(self):
        items_a = [_item("a/part.step", project="alpha")]
        items_b = [_item("b/img.jpg", kind=FileKind.PHOTO, project="beta")]
        plan_a = plan_scaffold("alpha", items_a)
        plan_b = plan_scaffold("beta", items_b)
        manifests = build_batch_manifests([plan_a, plan_b], items_a + items_b)
        projects = {m.project for m in manifests}
        assert projects == {"alpha", "beta"}

    def test_batch_manifests_items_split_by_project(self):
        items_a = [_item("a/part.step", project="proj_a", kind=FileKind.CAD)]
        items_b = [_item("b/img.jpg", kind=FileKind.PHOTO, project="proj_b")]
        plan_a = plan_scaffold("proj_a", items_a)
        plan_b = plan_scaffold("proj_b", items_b)
        manifests = build_batch_manifests([plan_a, plan_b], items_a + items_b)
        m_a = next(m for m in manifests if m.project == "proj_a")
        assert m_a.total_entries == 1

    def test_empty_plans_list(self):
        manifests = build_batch_manifests([], [])
        assert manifests == []


# ---------------------------------------------------------------------------
# Migration — MigrationPlan properties
# ---------------------------------------------------------------------------

class TestMigrationPlan:
    def _make_item(self, action: MigrationAction, size: int = 0) -> MigrationItem:
        return MigrationItem(
            action=action, dest_path=f"dir/{action.value.lower()}.txt",
            size_bytes=size,
        )

    def test_adds_filter(self):
        plan = MigrationPlan(project="x", items=[
            self._make_item(MigrationAction.ADD),
            self._make_item(MigrationAction.SKIP),
        ])
        assert len(plan.adds) == 1

    def test_updates_filter(self):
        plan = MigrationPlan(project="x", items=[
            self._make_item(MigrationAction.UPDATE),
            self._make_item(MigrationAction.SKIP),
        ])
        assert len(plan.updates) == 1

    def test_skips_filter(self):
        plan = MigrationPlan(project="x", items=[
            self._make_item(MigrationAction.SKIP),
            self._make_item(MigrationAction.ADD),
        ])
        assert len(plan.skips) == 1

    def test_conflicts_filter(self):
        plan = MigrationPlan(project="x", items=[
            self._make_item(MigrationAction.CONFLICT),
        ])
        assert len(plan.conflicts) == 1

    def test_removes_filter(self):
        plan = MigrationPlan(project="x", items=[
            self._make_item(MigrationAction.REMOVE),
        ])
        assert len(plan.removes) == 1

    def test_total_bytes_to_add_sums_add_and_update(self):
        plan = MigrationPlan(project="x", items=[
            self._make_item(MigrationAction.ADD, size=500),
            self._make_item(MigrationAction.UPDATE, size=300),
            self._make_item(MigrationAction.SKIP, size=9999),
            self._make_item(MigrationAction.REMOVE, size=1000),
        ])
        assert plan.total_bytes_to_add == 800

    def test_has_conflicts_true(self):
        plan = MigrationPlan(project="x", items=[
            self._make_item(MigrationAction.CONFLICT),
        ])
        assert plan.has_conflicts is True

    def test_has_conflicts_false(self):
        plan = MigrationPlan(project="x", items=[
            self._make_item(MigrationAction.ADD),
            self._make_item(MigrationAction.SKIP),
        ])
        assert plan.has_conflicts is False

    def test_summary_lines_non_empty(self):
        plan = MigrationPlan(project="x", items=[
            self._make_item(MigrationAction.ADD),
        ])
        lines = plan.summary_lines()
        assert len(lines) > 0
        assert any("ADD" in line for line in lines)


# ---------------------------------------------------------------------------
# plan_migration — core logic
# ---------------------------------------------------------------------------

class TestPlanMigration:
    def _manifest_with_entry(
        self,
        dest_path: str = "cad/part.step",
        content_hash: str = "abc123",
        size_bytes: int = 100,
        confidence: str = "high",
        project: str = "proj",
    ) -> RepoManifest:
        entry = ManifestEntry(
            source_path="archive/part.step",
            dest_path=dest_path,
            kind=FileKind.CAD,
            size_bytes=size_bytes,
            content_hash=content_hash,
            provenance_confidence=confidence,
        )
        section = ManifestSection(dest_dir="cad", kind=FileKind.CAD, entries=[entry])
        return RepoManifest(
            project=project,
            sections=[section],
            total_entries=1,
            total_size_bytes=size_bytes,
        )

    def test_empty_manifest_empty_tree_empty_plan(self):
        manifest = RepoManifest(project="x")
        plan = plan_migration(manifest, {})
        assert plan.items == []

    def test_new_file_is_add(self):
        manifest = self._manifest_with_entry(dest_path="cad/part.step", content_hash="abc")
        plan = plan_migration(manifest, {})
        assert len(plan.adds) == 1
        assert plan.adds[0].dest_path == "cad/part.step"

    def test_matching_hash_is_skip(self):
        manifest = self._manifest_with_entry(dest_path="cad/part.step", content_hash="abc123")
        plan = plan_migration(manifest, {"cad/part.step": "abc123"})
        assert len(plan.skips) == 1
        assert plan.adds == []

    def test_different_hash_high_confidence_is_update(self):
        manifest = self._manifest_with_entry(
            dest_path="cad/part.step", content_hash="newHash", confidence="high"
        )
        plan = plan_migration(manifest, {"cad/part.step": "oldHash"})
        assert len(plan.updates) == 1
        assert plan.conflicts == []

    def test_different_hash_low_confidence_flag_conflicts_true_is_conflict(self):
        manifest = self._manifest_with_entry(
            dest_path="cad/part.step", content_hash="newHash", confidence="low"
        )
        plan = plan_migration(manifest, {"cad/part.step": "oldHash"}, flag_conflicts=True)
        assert len(plan.conflicts) == 1
        assert plan.updates == []

    def test_different_hash_low_confidence_flag_conflicts_false_is_update(self):
        manifest = self._manifest_with_entry(
            dest_path="cad/part.step", content_hash="newHash", confidence="low"
        )
        plan = plan_migration(manifest, {"cad/part.step": "oldHash"}, flag_conflicts=False)
        assert len(plan.updates) == 1
        assert plan.conflicts == []

    def test_orphan_in_tree_is_remove(self):
        manifest = RepoManifest(project="x")
        plan = plan_migration(manifest, {"old/file.txt": "hash1"})
        assert len(plan.removes) == 1
        assert plan.removes[0].dest_path == "old/file.txt"

    def test_file_in_both_tree_and_manifest_not_removed(self):
        manifest = self._manifest_with_entry(dest_path="cad/part.step", content_hash="abc")
        plan = plan_migration(manifest, {"cad/part.step": "abc"})
        assert plan.removes == []

    def test_medium_confidence_different_hash_is_update(self):
        manifest = self._manifest_with_entry(
            dest_path="cad/part.step", content_hash="new", confidence="medium"
        )
        plan = plan_migration(manifest, {"cad/part.step": "old"})
        assert len(plan.updates) == 1

    def test_mixed_scenario(self):
        """Some ADD, SKIP, UPDATE, CONFLICT, REMOVE."""
        entries = [
            ManifestEntry(
                source_path="a/new.step", dest_path="cad/new.step",
                kind=FileKind.CAD, size_bytes=100,
                content_hash="hash_new", provenance_confidence="high",
            ),
            ManifestEntry(
                source_path="a/same.step", dest_path="cad/same.step",
                kind=FileKind.CAD, size_bytes=200,
                content_hash="hash_same", provenance_confidence="high",
            ),
            ManifestEntry(
                source_path="a/conflict.step", dest_path="cad/conflict.step",
                kind=FileKind.CAD, size_bytes=300,
                content_hash="hash_conflict_new", provenance_confidence="low",
            ),
        ]
        section = ManifestSection(dest_dir="cad", kind=FileKind.CAD, entries=entries)
        manifest = RepoManifest(
            project="mixed",
            sections=[section],
            total_entries=3,
            total_size_bytes=600,
        )
        existing_tree = {
            "cad/same.step": "hash_same",       # SKIP
            "cad/conflict.step": "hash_old",    # CONFLICT (low confidence)
            "cad/orphan.step": "hash_orphan",   # REMOVE
        }
        plan = plan_migration(manifest, existing_tree)
        assert len(plan.adds) == 1      # new.step
        assert len(plan.skips) == 1     # same.step
        assert len(plan.conflicts) == 1 # conflict.step (low confidence)
        assert len(plan.removes) == 1   # orphan.step
        assert plan.updates == []
        assert plan.has_conflicts is True

    def test_total_bytes_to_add_add_plus_update(self):
        entries = [
            ManifestEntry(
                source_path="a/new.step", dest_path="cad/new.step",
                kind=FileKind.CAD, size_bytes=500,
                content_hash="hash_a", provenance_confidence="high",
            ),
            ManifestEntry(
                source_path="a/changed.step", dest_path="cad/changed.step",
                kind=FileKind.CAD, size_bytes=250,
                content_hash="hash_b_new", provenance_confidence="high",
            ),
        ]
        section = ManifestSection(dest_dir="cad", kind=FileKind.CAD, entries=entries)
        manifest = RepoManifest(
            project="p", sections=[section], total_entries=2, total_size_bytes=750
        )
        existing_tree = {"cad/changed.step": "hash_b_old"}
        plan = plan_migration(manifest, existing_tree)
        assert plan.total_bytes_to_add == 750  # 500 (ADD) + 250 (UPDATE)

    def test_plan_project_matches_manifest(self):
        manifest = self._manifest_with_entry(project="synth_v3")
        plan = plan_migration(manifest, {})
        assert plan.project == "synth_v3"
