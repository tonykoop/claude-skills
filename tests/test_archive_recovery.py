"""
Tests for archive_recovery — fully offline, no filesystem mutation.

Coverage targets
----------------
* Extension classification (known kinds → fact; unknown → inferred)
* project grouping (path heuristics, archive-prefix stripping)
* ScaffoldPlan: dirs-by-kind, LFS rules for large binaries
* Evidence ledger: fact/inferred split, counts, export
* Determinism: identical input → identical output on repeated calls
"""

from __future__ import annotations

import pytest
from archive_recovery import (
    ArchiveItem,
    FileRecord,
    FileKind,
    classify_archive,
    ScaffoldPlan,
    plan_scaffold,
    EvidenceLedger,
    EvidenceEntry,
    EvidenceKind,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_record(path: str, size_bytes: int = 0, mtime: float = 0.0) -> FileRecord:
    return FileRecord(path=path, size_bytes=size_bytes, mtime=mtime)


LARGE = 101 * 1024 * 1024  # just over 100 MB


# ===========================================================================
# 1. Classification by extension
# ===========================================================================

class TestClassifyByExtension:
    """Known extensions → archive-fact (kind_is_inferred=False)."""

    @pytest.mark.parametrize("path,expected_kind", [
        # CAD
        ("proj/model.step",       FileKind.CAD),
        ("proj/board.stl",        FileKind.CAD),
        ("proj/part.f3d",         FileKind.CAD),
        ("proj/pcb.kicad_pcb",    FileKind.CAD),
        ("proj/drawing.dxf",      FileKind.CAD),
        # PHOTO
        ("proj/img.jpg",          FileKind.PHOTO),
        ("proj/img.JPEG",         FileKind.PHOTO),   # uppercase ext
        ("proj/raw.CR2",          FileKind.PHOTO),
        ("proj/snap.png",         FileKind.PHOTO),
        ("proj/snap.webp",        FileKind.PHOTO),
        # DOC
        ("proj/spec.pdf",         FileKind.DOC),
        ("proj/notes.md",         FileKind.DOC),
        ("proj/bom.csv",          FileKind.DOC),
        ("proj/config.yaml",      FileKind.DOC),
        # CODE
        ("proj/main.py",          FileKind.CODE),
        ("proj/firmware.ino",     FileKind.CODE),
        ("proj/build.sh",         FileKind.CODE),
        ("proj/driver.cpp",       FileKind.CODE),
        ("proj/util.rs",          FileKind.CODE),
        # MEDIA
        ("proj/demo.mp4",         FileKind.MEDIA),
        ("proj/timelapse.mov",    FileKind.MEDIA),
        ("proj/audio.wav",        FileKind.MEDIA),
    ])
    def test_known_extension_classifies_correctly(self, path, expected_kind):
        records = [make_record(path)]
        items = classify_archive(records)
        assert items[0].kind == expected_kind

    @pytest.mark.parametrize("path,expected_kind", [
        ("proj/model.step",    FileKind.CAD),
        ("proj/notes.md",      FileKind.DOC),
        ("proj/main.py",       FileKind.CODE),
        ("proj/demo.mp4",      FileKind.MEDIA),
        ("proj/img.jpg",       FileKind.PHOTO),
    ])
    def test_known_extension_is_not_inferred(self, path, expected_kind):
        """Extension in the lookup table → kind_is_inferred must be False."""
        items = classify_archive([make_record(path)])
        assert items[0].kind_is_inferred is False

    def test_unknown_extension_yields_unknown_kind(self):
        items = classify_archive([make_record("proj/file.xyzzy")])
        assert items[0].kind == FileKind.UNKNOWN
        assert items[0].kind_is_inferred is True

    def test_no_extension_inferred_as_code(self):
        items = classify_archive([make_record("proj/Makefile")])
        assert items[0].kind == FileKind.CODE
        assert items[0].kind_is_inferred is True

    def test_dotfile_inferred_as_code(self):
        items = classify_archive([make_record("proj/.gitignore")])
        assert items[0].kind == FileKind.CODE
        assert items[0].kind_is_inferred is True

    def test_extension_case_insensitive(self):
        upper = classify_archive([make_record("proj/render.JPG")])[0]
        lower = classify_archive([make_record("proj/render.jpg")])[0]
        assert upper.kind == lower.kind == FileKind.PHOTO

    def test_provenance_note_is_non_empty(self):
        items = classify_archive([make_record("proj/model.step")])
        assert len(items[0].provenance_note) > 10

    def test_content_hash_auto_filled(self):
        """When FileRecord has no hash, ArchiveItem derives a deterministic stub."""
        record = FileRecord(path="proj/test.py")
        items = classify_archive([record])
        assert len(items[0].content_hash) == 64  # SHA-256 hex


# ===========================================================================
# 2. Project grouping
# ===========================================================================

class TestProjectGrouping:

    def test_first_directory_component_is_project(self):
        items = classify_archive([make_record("synth_v2/pcb.kicad_pcb")])
        assert items[0].inferred_project == "synth_v2"

    def test_archive_prefix_stripped(self):
        """Common archive-prefix dirs (archive/, backup/, etc.) should be removed."""
        for prefix in ("archive", "backup", "exports", "old", "misc", "projects"):
            items = classify_archive([make_record(f"{prefix}/laser_cutter/design.dxf")])
            assert items[0].inferred_project == "laser_cutter", (
                f"Expected 'laser_cutter' but got '{items[0].inferred_project}' "
                f"for prefix '{prefix}'"
            )

    def test_nested_archive_prefixes_stripped(self):
        """Multiple consecutive archive prefixes should all be stripped."""
        items = classify_archive([make_record("archive/old/drum_machine/main.py")])
        assert items[0].inferred_project == "drum_machine"

    def test_flat_file_uses_stem_as_project(self):
        """No parent directories → filename stem becomes project name."""
        items = classify_archive([make_record("pedalboard_v3.stl")])
        assert items[0].inferred_project == "pedalboard_v3"

    def test_project_slug_normalised(self):
        """Spaces / dashes / special chars should be collapsed to underscores."""
        items = classify_archive([make_record("My Guitar Build 2024/frets.dxf")])
        assert items[0].inferred_project == "my_guitar_build_2024"

    def test_project_is_always_flagged_inferred(self):
        """In this classifier version, project identity is always heuristic."""
        items = classify_archive([make_record("synth_v2/pcb.kicad_pcb")])
        assert items[0].project_is_inferred is True

    def test_multiple_files_same_project_grouped(self):
        records = [
            make_record("synth_v2/pcb.kicad_pcb"),
            make_record("synth_v2/firmware.ino"),
            make_record("synth_v2/photo.jpg"),
        ]
        items = classify_archive(records)
        projects = {i.inferred_project for i in items}
        assert projects == {"synth_v2"}

    def test_different_dirs_different_projects(self):
        records = [
            make_record("project_a/design.step"),
            make_record("project_b/code.py"),
        ]
        items = classify_archive(records)
        assert items[0].inferred_project == "project_a"
        assert items[1].inferred_project == "project_b"

    def test_empty_input_returns_empty_list(self):
        assert classify_archive([]) == []


# ===========================================================================
# 3. ScaffoldPlan: dirs by kind, LFS rules
# ===========================================================================

class TestScaffoldPlan:

    def _items(self, *paths_sizes) -> list[ArchiveItem]:
        """Build ArchiveItems from (path, size_bytes) tuples."""
        records = [make_record(p, s) for p, s in paths_sizes]
        return classify_archive(records)

    def test_dirs_cover_each_kind_present(self):
        items = self._items(
            ("proj/model.step", 0),
            ("proj/main.py",    0),
            ("proj/notes.md",   0),
            ("proj/snap.jpg",   0),
        )
        plan = plan_scaffold("proj", items)
        dir_paths = {d.path for d in plan.dirs}
        assert "cad"    in dir_paths
        assert "src"    in dir_paths
        assert "docs"   in dir_paths
        assert "photos" in dir_paths

    def test_no_extra_dirs_for_absent_kinds(self):
        items = self._items(("proj/model.step", 0))
        plan = plan_scaffold("proj", items)
        dir_paths = {d.path for d in plan.dirs}
        # Only CAD files → should not have src/photos/docs/media
        assert dir_paths == {"cad"}

    def test_large_binary_triggers_lfs_rule(self):
        items = self._items(("proj/assembly.step", LARGE))
        plan = plan_scaffold("proj", items)
        assert len(plan.lfs_rules) == 1
        rule = plan.lfs_rules[0]
        assert "assembly.step" in rule.pattern
        assert plan.large_binary_count == 1

    def test_small_binary_no_lfs_rule(self):
        items = self._items(("proj/tiny.stl", 1024))
        plan = plan_scaffold("proj", items)
        assert plan.lfs_rules == []
        assert plan.large_binary_count == 0

    def test_multiple_large_files_each_get_lfs_rule(self):
        items = self._items(
            ("proj/big_a.stl", LARGE),
            ("proj/big_b.stl", LARGE),
            ("proj/small.stl", 500),
        )
        plan = plan_scaffold("proj", items)
        assert len(plan.lfs_rules) == 2
        assert plan.large_binary_count == 2

    def test_lfs_rule_pattern_is_path_specific(self):
        """LFS pattern must be file-specific, not a glob like '*.stl'."""
        items = self._items(("proj/giant.stl", LARGE))
        plan = plan_scaffold("proj", items)
        pattern = plan.lfs_rules[0].pattern
        # Should contain the filename, not just an extension wildcard
        assert "giant.stl" in pattern
        assert pattern != "*.stl"

    def test_readme_skeleton_contains_project_name(self):
        items = self._items(("proj/model.step", 0))
        plan = plan_scaffold("my_synthesiser", items)
        assert "my_synthesiser" in plan.readme_skeleton

    def test_readme_skeleton_mentions_lfs_when_applicable(self):
        items = self._items(("proj/heavy.step", LARGE))
        plan = plan_scaffold("proj", items)
        assert "LFS" in plan.readme_skeleton

    def test_readme_no_lfs_section_when_no_large_files(self):
        """The dedicated '## Git LFS' section must not appear when no files are large."""
        items = self._items(("proj/small.step", 100))
        plan = plan_scaffold("proj", items)
        # The ## Git LFS heading is only injected when lfs_note is non-empty
        assert "## Git LFS" not in plan.readme_skeleton

    def test_gitignore_lines_non_empty(self):
        items = self._items(("proj/model.step", 0))
        plan = plan_scaffold("proj", items)
        assert len(plan.gitignore_lines) > 0
        # Should always mention .DS_Store
        assert ".DS_Store" in plan.gitignore_lines

    def test_item_count_correct(self):
        items = self._items(
            ("proj/a.step", 0),
            ("proj/b.py",   0),
            ("proj/c.jpg",  0),
        )
        plan = plan_scaffold("proj", items)
        assert plan.item_count == 3

    def test_plan_project_matches_input(self):
        items = self._items(("proj/model.step", 0))
        plan = plan_scaffold("custom_project_name", items)
        assert plan.project == "custom_project_name"

    def test_empty_items_produces_valid_plan(self):
        plan = plan_scaffold("empty_proj", [])
        assert plan.item_count == 0
        assert plan.dirs == []
        assert plan.lfs_rules == []

    def test_export_dict_is_serialisable(self):
        """export_dict() must return JSON-friendly types only."""
        import json
        items = self._items(("proj/model.step", LARGE))
        plan = plan_scaffold("proj", items)
        d = plan.export_dict()
        # Should not raise
        serialised = json.dumps(d)
        assert len(serialised) > 100

    def test_media_files_in_media_dir(self):
        items = self._items(("proj/timelapse.mp4", 0))
        plan = plan_scaffold("proj", items)
        assert any(d.path == "media" for d in plan.dirs)

    def test_unknown_kind_in_misc_dir(self):
        items = self._items(("proj/mystery.xyzzy", 0))
        plan = plan_scaffold("proj", items)
        assert any(d.path == "misc" for d in plan.dirs)


# ===========================================================================
# 4. Evidence ledger — fact / inferred split
# ===========================================================================

class TestEvidenceLedger:

    def test_manual_fact_entry(self):
        ledger = EvidenceLedger(project="test_proj")
        entry = EvidenceEntry(
            kind=EvidenceKind.FACT,
            subject="proj/model.step",
            claim="file exists at path",
            source="archive byte-stream",
        )
        ledger.add(entry)
        assert len(ledger.facts()) == 1
        assert len(ledger.inferences()) == 0

    def test_manual_inferred_entry(self):
        ledger = EvidenceLedger(project="test_proj")
        ledger.add(EvidenceEntry(
            kind=EvidenceKind.INFERRED,
            subject="proj/model.step",
            claim="belongs to project 'test_proj'",
            source="path heuristic",
            confidence="medium",
        ))
        assert len(ledger.facts()) == 0
        assert len(ledger.inferences()) == 1

    def test_from_archive_items_builds_ledger(self):
        records = [make_record("project_x/pcb.kicad_pcb")]
        items = classify_archive(records)
        ledger = EvidenceLedger.from_archive_items("project_x", items)
        assert ledger.project == "project_x"
        assert len(ledger.entries) > 0

    def test_known_extension_generates_fact_kind_entry(self):
        """When kind_is_inferred=False, the kind entry should be a FACT."""
        records = [make_record("proj/model.step")]
        items = classify_archive(records)
        # Confirm classification
        assert items[0].kind_is_inferred is False
        ledger = EvidenceLedger.from_archive_items("proj", items)
        fact_claims = [e.claim for e in ledger.facts()]
        assert any("cad" in c for c in fact_claims)

    def test_unknown_extension_generates_inferred_kind_entry(self):
        records = [make_record("proj/weird.xyzzy")]
        items = classify_archive(records)
        assert items[0].kind_is_inferred is True
        ledger = EvidenceLedger.from_archive_items("proj", items)
        inferred_claims = [e.claim for e in ledger.inferences()]
        assert any("inferred" in c for c in inferred_claims)

    def test_project_grouping_always_inferred(self):
        records = [make_record("my_proj/design.step")]
        items = classify_archive(records)
        ledger = EvidenceLedger.from_archive_items("my_proj", items)
        inferred_claims = [e.claim for e in ledger.inferences()]
        assert any("my_proj" in c for c in inferred_claims)

    def test_audit_counts_match(self):
        ledger = EvidenceLedger(project="p")
        ledger.add(EvidenceEntry(
            kind=EvidenceKind.FACT, subject="a", claim="x", source="src"
        ))
        ledger.add(EvidenceEntry(
            kind=EvidenceKind.FACT, subject="b", claim="y", source="src"
        ))
        ledger.add(EvidenceEntry(
            kind=EvidenceKind.INFERRED, subject="c", claim="z", source="heuristic"
        ))
        audit = ledger.audit()
        assert audit["total"]    == 3
        assert audit["facts"]    == 2
        assert audit["inferred"] == 1

    def test_scaffold_plan_includes_ledger(self):
        records = [make_record("proj/code.py"), make_record("proj/img.jpg")]
        items = classify_archive(records)
        plan = plan_scaffold("proj", items)
        assert isinstance(plan.evidence_ledger, EvidenceLedger)
        assert len(plan.evidence_ledger.entries) > 0

    def test_scaffold_lfs_decision_recorded_as_inferred(self):
        records = [make_record("proj/huge.stl", LARGE)]
        items = classify_archive(records)
        plan = plan_scaffold("proj", items)
        inferred = [e.claim for e in plan.evidence_ledger.inferences()]
        assert any("LFS" in c or "lfs" in c.lower() for c in inferred)

    def test_scaffold_dir_decision_recorded_as_inferred(self):
        records = [make_record("proj/model.step")]
        items = classify_archive(records)
        plan = plan_scaffold("proj", items)
        inferred = [e.claim for e in plan.evidence_ledger.inferences()]
        assert any("cad" in c for c in inferred)

    def test_ledger_chaining(self):
        """add() returns self → fluent chaining should work."""
        ledger = EvidenceLedger(project="chain")
        result = (
            ledger
            .add(EvidenceEntry(kind=EvidenceKind.FACT, subject="f", claim="c", source="s"))
            .add(EvidenceEntry(kind=EvidenceKind.INFERRED, subject="f2", claim="c2", source="s2"))
        )
        assert result is ledger
        assert len(ledger.entries) == 2

    def test_export_dict_structure(self):
        ledger = EvidenceLedger(project="export_test")
        ledger.add(EvidenceEntry(
            kind=EvidenceKind.FACT, subject="x", claim="y", source="z"
        ))
        d = ledger.export_dict()
        assert "project"  in d
        assert "total"    in d
        assert "facts"    in d
        assert "inferred" in d
        assert "entries"  in d
        assert d["project"] == "export_test"


# ===========================================================================
# 5. Determinism
# ===========================================================================

class TestDeterminism:

    def test_classify_archive_is_deterministic(self):
        records = [
            make_record("proj/model.step", 1000, 1700000000.0),
            make_record("proj/firmware.ino", 2048, 1700000001.0),
            make_record("proj/notes.pdf", 512, 1700000002.0),
            make_record("archive/proj/img.jpg", 409600, 1700000003.0),
        ]
        first  = classify_archive(records)
        second = classify_archive(records)
        for a, b in zip(first, second):
            assert a.model_dump() == b.model_dump()

    def test_plan_scaffold_is_deterministic(self):
        records = [
            make_record("proj/model.step", LARGE),
            make_record("proj/main.py", 0),
            make_record("proj/notes.md", 0),
        ]
        items = classify_archive(records)
        plan1 = plan_scaffold("proj", items)
        plan2 = plan_scaffold("proj", items)
        assert plan1.export_dict() == plan2.export_dict()

    def test_evidence_ledger_from_items_is_deterministic(self):
        records = [make_record("proj/model.step"), make_record("proj/main.py")]
        items = classify_archive(records)
        l1 = EvidenceLedger.from_archive_items("proj", items)
        l2 = EvidenceLedger.from_archive_items("proj", items)
        assert l1.audit() == l2.audit()

    def test_output_order_matches_input_order(self):
        paths = [
            "proj/zebra.jpg",
            "proj/alpha.py",
            "proj/model.step",
        ]
        records = [make_record(p) for p in paths]
        items = classify_archive(records)
        assert [i.path for i in items] == paths


# ===========================================================================
# 6. Integration smoke test
# ===========================================================================

class TestIntegration:
    """End-to-end: records → classify → plan → evidence ledger."""

    def test_full_pipeline(self):
        records = [
            make_record("archive/synth_v3/case.step",    0),
            make_record("archive/synth_v3/firmware.ino", 0),
            make_record("archive/synth_v3/schematic.dxf",0),
            make_record("archive/synth_v3/bom.csv",      0),
            make_record("archive/synth_v3/build01.jpg",  0),
            make_record("archive/synth_v3/demo.mp4",     LARGE),
            make_record("archive/synth_v3/notes.md",     0),
        ]
        items = classify_archive(records)

        # All items grouped under synth_v3
        projects = {i.inferred_project for i in items}
        assert projects == {"synth_v3"}

        plan = plan_scaffold("synth_v3", items)

        # Dirs: cad, src, docs, photos, media
        dir_paths = {d.path for d in plan.dirs}
        assert {"cad", "src", "docs", "photos", "media"}.issubset(dir_paths)

        # LFS rule for demo.mp4 (>100 MB)
        assert plan.large_binary_count == 1
        assert any("demo.mp4" in r.pattern for r in plan.lfs_rules)

        # Evidence ledger has both facts and inferences
        assert len(plan.evidence_ledger.facts()) > 0
        assert len(plan.evidence_ledger.inferences()) > 0

        # Plan is serialisable
        import json
        json.dumps(plan.export_dict())  # must not raise

    def test_mixed_archive_prefix_paths(self):
        records = [
            make_record("backup/laser_project/design.dxf"),
            make_record("exports/laser_project/gcode.txt"),
            make_record("laser_project/photo.jpg"),
        ]
        items = classify_archive(records)
        projects = {i.inferred_project for i in items}
        assert projects == {"laser_project"}
