"""
Tests for archive_recovery.inventory_csv and archive_recovery.project_router.

Story #53 — Full inventory pass of D:\\ archive
Story #54 — Betabrand shacket → sewing repo organization
"""

from __future__ import annotations

import textwrap

import pytest

from archive_recovery.models import ArchiveItem, FileKind, FileRecord
from archive_recovery.inventory_csv import (
    InventoryParseResult,
    InventoryRow,
    FileInventoryRow,
    ArchiveSummary,
    _parse_mtime,
    parse_directory_csv,
    rows_to_file_records,
    summarise_inventory,
)
from archive_recovery.project_router import (
    KeywordRule,
    KindRule,
    RouterConfig,
    RoutingDecision,
    ProjectRouter,
)


# ===========================================================================
# Helpers
# ===========================================================================

DIR_CSV_HEADER = "Path,Depth,FileCount,SizeBytes,Modified,Extensions"
FILE_CSV_HEADER = "Path,SizeBytes,Modified,Extension"


def make_dir_csv(*data_rows: str) -> str:
    return "\n".join([DIR_CSV_HEADER] + list(data_rows))


def make_file_csv(*data_rows: str) -> str:
    return "\n".join([FILE_CSV_HEADER] + list(data_rows))


def make_item(kind: FileKind, project: str = "proj") -> ArchiveItem:
    return ArchiveItem(
        path=f"archive/{project}/file.txt",
        kind=kind,
        inferred_project=project,
    )


# ===========================================================================
# _parse_mtime
# ===========================================================================

class TestParseMtime:
    def test_valid_iso_with_T(self):
        ts = _parse_mtime("2026-05-09T14:23:00")
        assert ts > 0.0

    def test_valid_iso_with_space(self):
        ts = _parse_mtime("2026-05-09 14:23:00")
        assert ts > 0.0

    def test_date_only(self):
        ts = _parse_mtime("2026-05-09")
        assert ts > 0.0

    def test_empty_string_returns_zero(self):
        assert _parse_mtime("") == 0.0

    def test_bad_string_returns_zero(self):
        assert _parse_mtime("not-a-date") == 0.0

    def test_none_like_blank_returns_zero(self):
        assert _parse_mtime("   ") == 0.0

    def test_consistent_value(self):
        ts1 = _parse_mtime("2026-05-09T14:23:00")
        ts2 = _parse_mtime("2026-05-09T14:23:00")
        assert ts1 == ts2

    def test_microseconds(self):
        ts = _parse_mtime("2026-05-09T14:23:00.123456")
        assert ts > 0.0


# ===========================================================================
# parse_directory_csv — variant detection
# ===========================================================================

class TestParseDirectoryCsvVariant:
    def test_detects_directory_variant(self):
        csv_text = make_dir_csv(
            "projects/cad,1,10,2048,2026-05-09T10:00:00,.step;.stl"
        )
        result = parse_directory_csv(csv_text)
        assert result.variant == "directory"

    def test_detects_file_variant(self):
        csv_text = make_file_csv(
            "projects/cad/part.step,2048,2026-05-09T10:00:00,.step"
        )
        result = parse_directory_csv(csv_text)
        assert result.variant == "file"

    def test_unknown_variant_on_no_matching_headers(self):
        csv_text = "Name,Size\nfoo,100"
        result = parse_directory_csv(csv_text)
        assert result.variant == "unknown"

    def test_directory_variant_populates_rows(self):
        csv_text = make_dir_csv(
            "projects/cad,1,5,1024,2026-05-09T10:00:00,.step;.stl"
        )
        result = parse_directory_csv(csv_text)
        assert len(result.rows) == 1
        assert result.file_rows == []

    def test_file_variant_populates_file_rows(self):
        csv_text = make_file_csv(
            "projects/cad/part.step,1024,2026-05-09T10:00:00,.step"
        )
        result = parse_directory_csv(csv_text)
        assert len(result.file_rows) == 1
        assert result.rows == []


# ===========================================================================
# parse_directory_csv — directory CSV parsing
# ===========================================================================

class TestParseDirectoryCsvDirectory:
    def test_extensions_parsed_from_semicolon(self):
        csv_text = make_dir_csv(
            "dir/a,2,3,500,2026-01-01T00:00:00,.step;.stl;.pdf"
        )
        result = parse_directory_csv(csv_text)
        assert result.rows[0].extensions == ["step", "stl", "pdf"]

    def test_extensions_leading_dot_stripped(self):
        csv_text = make_dir_csv(
            "dir/a,2,3,500,2026-01-01T00:00:00,.STEP;.STL"
        )
        result = parse_directory_csv(csv_text)
        assert result.rows[0].extensions == ["step", "stl"]

    def test_extensions_lowercased(self):
        csv_text = make_dir_csv(
            "dir/a,0,1,100,2026-01-01T00:00:00,.PDF"
        )
        result = parse_directory_csv(csv_text)
        assert result.rows[0].extensions == ["pdf"]

    def test_path_normalised_backslashes(self):
        csv_text = make_dir_csv(
            r"projects\cad\parts,2,5,2048,2026-05-09T10:00:00,.step"
        )
        result = parse_directory_csv(csv_text)
        assert "/" in result.rows[0].path
        assert "\\" not in result.rows[0].path

    def test_blank_rows_skipped(self):
        csv_text = make_dir_csv(
            "dir/a,1,2,100,2026-01-01T00:00:00,.step",
            "",
            "dir/b,1,1,50,2026-01-02T00:00:00,.pdf",
        )
        result = parse_directory_csv(csv_text)
        assert result.total_rows == 2  # blank skipped
        assert len(result.rows) == 2

    def test_malformed_row_goes_to_parse_errors(self):
        csv_text = make_dir_csv(
            "dir/a,NOT_INT,bad,bad,2026-01-01T00:00:00,.step",
        )
        result = parse_directory_csv(csv_text)
        # "NOT_INT" cannot be parsed as int → parse_error
        assert len(result.parse_errors) == 1

    def test_total_rows_count(self):
        csv_text = make_dir_csv(
            "dir/a,1,2,100,2026-01-01T00:00:00,.step",
            "dir/b,1,3,200,2026-01-02T00:00:00,.stl",
        )
        result = parse_directory_csv(csv_text)
        assert result.total_rows == 2

    def test_depth_parsed(self):
        csv_text = make_dir_csv(
            "dir/deep/a,5,1,100,2026-01-01T00:00:00,.step"
        )
        result = parse_directory_csv(csv_text)
        assert result.rows[0].depth == 5

    def test_size_bytes_parsed(self):
        csv_text = make_dir_csv(
            "dir/a,1,1,999999,2026-01-01T00:00:00,.pdf"
        )
        result = parse_directory_csv(csv_text)
        assert result.rows[0].size_bytes == 999999

    def test_no_extensions_produces_empty_list(self):
        csv_text = make_dir_csv(
            "dir/a,1,0,0,2026-01-01T00:00:00,"
        )
        result = parse_directory_csv(csv_text)
        assert result.rows[0].extensions == []


# ===========================================================================
# parse_directory_csv — file CSV parsing
# ===========================================================================

class TestParseDirectoryCsvFile:
    def test_file_row_extension_stripped_and_lowercased(self):
        csv_text = make_file_csv(
            "docs/report.PDF,1024,2026-01-01T00:00:00,.PDF"
        )
        result = parse_directory_csv(csv_text)
        assert result.file_rows[0].extension == "pdf"

    def test_file_row_path_normalised(self):
        csv_text = make_file_csv(
            r"docs\report.pdf,1024,2026-01-01T00:00:00,.pdf"
        )
        result = parse_directory_csv(csv_text)
        assert "\\" not in result.file_rows[0].path

    def test_multiple_file_rows(self):
        csv_text = make_file_csv(
            "a/b.step,100,2026-01-01T00:00:00,.step",
            "c/d.pdf,200,2026-01-02T00:00:00,.pdf",
        )
        result = parse_directory_csv(csv_text)
        assert len(result.file_rows) == 2


# ===========================================================================
# rows_to_file_records
# ===========================================================================

class TestRowsToFileRecords:
    def test_directory_variant_one_record_per_extension(self):
        csv_text = make_dir_csv(
            "dir/cad,1,10,5000,2026-01-01T00:00:00,.step;.stl;.pdf"
        )
        result = parse_directory_csv(csv_text)
        records = rows_to_file_records(result)
        assert len(records) == 3

    def test_directory_variant_path_contains_extension(self):
        csv_text = make_dir_csv(
            "dir/cad,1,10,5000,2026-01-01T00:00:00,.step"
        )
        result = parse_directory_csv(csv_text)
        records = rows_to_file_records(result)
        assert "step" in records[0].path

    def test_directory_variant_no_extensions_produces_no_records(self):
        csv_text = make_dir_csv(
            "dir/cad,1,0,0,2026-01-01T00:00:00,"
        )
        result = parse_directory_csv(csv_text)
        records = rows_to_file_records(result)
        assert records == []

    def test_file_variant_one_record_per_row(self):
        csv_text = make_file_csv(
            "a/b.step,100,2026-01-01T00:00:00,.step",
            "c/d.pdf,200,2026-01-02T00:00:00,.pdf",
        )
        result = parse_directory_csv(csv_text)
        records = rows_to_file_records(result)
        assert len(records) == 2

    def test_file_variant_size_preserved(self):
        csv_text = make_file_csv(
            "a/b.step,12345,2026-01-01T00:00:00,.step"
        )
        result = parse_directory_csv(csv_text)
        records = rows_to_file_records(result)
        assert records[0].size_bytes == 12345

    def test_archive_root_stripped(self):
        csv_text = make_file_csv(
            "D:/archive/projects/a.step,100,2026-01-01T00:00:00,.step"
        )
        result = parse_directory_csv(csv_text)
        records = rows_to_file_records(result, archive_root="D:/archive")
        assert not records[0].path.startswith("D:/archive")
        assert "projects" in records[0].path

    def test_archive_root_not_stripped_when_not_matching(self):
        csv_text = make_file_csv(
            "other/path/a.step,100,2026-01-01T00:00:00,.step"
        )
        result = parse_directory_csv(csv_text)
        records = rows_to_file_records(result, archive_root="D:/archive")
        assert records[0].path.startswith("other/")

    def test_mtime_set_from_modified_field(self):
        csv_text = make_file_csv(
            "a/b.step,100,2026-05-09T14:23:00,.step"
        )
        result = parse_directory_csv(csv_text)
        records = rows_to_file_records(result)
        assert records[0].mtime > 0.0

    def test_unknown_variant_returns_empty(self):
        result = InventoryParseResult(variant="unknown", total_rows=0)
        records = rows_to_file_records(result)
        assert records == []


# ===========================================================================
# summarise_inventory
# ===========================================================================

class TestSummariseInventory:
    def _make_result(self) -> InventoryParseResult:
        csv_text = make_dir_csv(
            "dir/a,1,5,1000,2026-01-01T00:00:00,.step;.stl",
            "dir/b,2,3,2000,2026-01-02T00:00:00,.step;.pdf",
            "dir/c,3,1,500,2026-01-03T00:00:00,.png",
        )
        return parse_directory_csv(csv_text)

    def test_total_dirs(self):
        result = self._make_result()
        summary = summarise_inventory(result)
        assert summary.total_dirs == 3

    def test_total_size_bytes(self):
        result = self._make_result()
        summary = summarise_inventory(result)
        assert summary.total_size_bytes == 3500

    def test_max_depth(self):
        result = self._make_result()
        summary = summarise_inventory(result)
        assert summary.max_depth == 3

    def test_extension_counts(self):
        result = self._make_result()
        summary = summarise_inventory(result)
        # "step" appears in dir/a and dir/b → count 2
        assert summary.extension_counts["step"] == 2
        assert summary.extension_counts["stl"] == 1
        assert summary.extension_counts["pdf"] == 1
        assert summary.extension_counts["png"] == 1

    def test_top_extensions_top_5(self):
        rows = [
            f"dir/{i},1,1,100,2026-01-01T00:00:00,.step" for i in range(10)
        ] + [
            f"dir/x{i},1,1,100,2026-01-01T00:00:00,.stl" for i in range(7)
        ] + [
            f"dir/y{i},1,1,100,2026-01-01T00:00:00,.pdf" for i in range(5)
        ] + [
            f"dir/z{i},1,1,100,2026-01-01T00:00:00,.png" for i in range(3)
        ] + [
            f"dir/w{i},1,1,100,2026-01-01T00:00:00,.jpg" for i in range(2)
        ] + [
            "dir/v0,1,1,100,2026-01-01T00:00:00,.bmp",
        ]
        csv_text = make_dir_csv(*rows)
        result = parse_directory_csv(csv_text)
        summary = summarise_inventory(result)
        assert len(summary.top_extensions) == 5
        assert summary.top_extensions[0] == "step"
        assert summary.top_extensions[1] == "stl"

    def test_top_extensions_fewer_than_5(self):
        csv_text = make_dir_csv(
            "dir/a,1,1,100,2026-01-01T00:00:00,.step",
        )
        result = parse_directory_csv(csv_text)
        summary = summarise_inventory(result)
        assert len(summary.top_extensions) == 1

    def test_empty_result_gives_zero_stats(self):
        result = InventoryParseResult(variant="directory", total_rows=0)
        summary = summarise_inventory(result)
        assert summary.total_dirs == 0
        assert summary.total_size_bytes == 0
        assert summary.max_depth == 0
        assert summary.top_extensions == []


# ===========================================================================
# ProjectRouter — explicit override
# ===========================================================================

class TestProjectRouterExplicitOverride:
    def test_explicit_override_high_confidence(self):
        cfg = RouterConfig(explicit_overrides={"synth_v2": "electronics"})
        router = ProjectRouter(cfg)
        dec = router.route("synth_v2", [])
        assert dec.destination_repo == "electronics"
        assert dec.confidence == "high"
        assert dec.rule_used == "explicit override"

    def test_explicit_override_sub_path_contains_project(self):
        cfg = RouterConfig(explicit_overrides={"synth_v2": "electronics"})
        router = ProjectRouter(cfg)
        dec = router.route("synth_v2", [])
        assert "synth_v2" in dec.sub_path


# ===========================================================================
# ProjectRouter — keyword rules
# ===========================================================================

class TestProjectRouterKeywordRules:
    def _sewing_router(self) -> ProjectRouter:
        cfg = RouterConfig(
            keyword_rules=[
                KeywordRule(pattern="shacket", destination_repo="sewing"),
                KeywordRule(pattern="vest", destination_repo="sewing"),
            ]
        )
        return ProjectRouter(cfg)

    def test_keyword_match_shacket(self):
        router = self._sewing_router()
        dec = router.route("2015-betabrand-shacket", [])
        assert dec.destination_repo == "sewing"
        assert dec.confidence == "high"

    def test_keyword_match_case_insensitive(self):
        router = self._sewing_router()
        dec = router.route("SHACKET_PROTO", [])
        assert dec.destination_repo == "sewing"

    def test_keyword_first_match_wins(self):
        cfg = RouterConfig(
            keyword_rules=[
                KeywordRule(pattern="shacket", destination_repo="sewing"),
                KeywordRule(pattern="shacket", destination_repo="other"),
            ]
        )
        router = ProjectRouter(cfg)
        dec = router.route("shacket-v2", [])
        assert dec.destination_repo == "sewing"

    def test_keyword_rule_description_in_rule_used(self):
        router = self._sewing_router()
        dec = router.route("2015-betabrand-shacket", [])
        assert "shacket" in dec.rule_used

    def test_keyword_sub_path_template_project_substituted(self):
        cfg = RouterConfig(
            keyword_rules=[
                KeywordRule(
                    pattern="shacket",
                    destination_repo="sewing",
                    sub_path_template="garments/{project}/",
                )
            ]
        )
        router = ProjectRouter(cfg)
        dec = router.route("my-shacket", [])
        assert dec.sub_path == "garments/my-shacket/"


# ===========================================================================
# ProjectRouter — kind rules
# ===========================================================================

class TestProjectRouterKindRules:
    def _cad_router(self) -> ProjectRouter:
        cfg = RouterConfig(
            kind_rules=[
                KindRule(kind=FileKind.CAD, destination_repo="cad-projects"),
                KindRule(kind=FileKind.CODE, destination_repo="code-projects"),
            ]
        )
        return ProjectRouter(cfg)

    def test_kind_cad_routes_to_cad_projects(self):
        router = self._cad_router()
        items = [make_item(FileKind.CAD)] * 5
        dec = router.route("my-cad-project", items)
        assert dec.destination_repo == "cad-projects"
        assert dec.confidence == "medium"

    def test_kind_rule_dominant_kind_set(self):
        router = self._cad_router()
        items = [make_item(FileKind.CAD)] * 3 + [make_item(FileKind.CODE)]
        dec = router.route("mixed", items)
        assert dec.dominant_kind == FileKind.CAD

    def test_kind_tie_break_cad_beats_code(self):
        router = self._cad_router()
        items = [make_item(FileKind.CAD), make_item(FileKind.CODE)]
        dec = router.route("mixed", items)
        assert dec.dominant_kind == FileKind.CAD
        assert dec.destination_repo == "cad-projects"

    def test_kind_rule_medium_confidence(self):
        router = self._cad_router()
        items = [make_item(FileKind.CODE)] * 3
        dec = router.route("code-thing", items)
        assert dec.confidence == "medium"
        assert dec.destination_repo == "code-projects"


# ===========================================================================
# ProjectRouter — fallback
# ===========================================================================

class TestProjectRouterFallback:
    def test_fallback_when_no_rule_matches(self):
        router = ProjectRouter(RouterConfig(fallback_repo="archive-misc"))
        dec = router.route("random-project", [])
        assert dec.destination_repo == "archive-misc"
        assert dec.confidence == "low"
        assert dec.rule_used == "fallback"

    def test_fallback_sub_path(self):
        router = ProjectRouter(RouterConfig(fallback_repo="archive-misc"))
        dec = router.route("my-project", [])
        assert dec.sub_path == "archive/my-project/"

    def test_empty_items_unknown_dominant_kind(self):
        router = ProjectRouter()
        dec = router.route("empty-proj", [])
        assert dec.dominant_kind == FileKind.UNKNOWN

    def test_all_unknown_items_do_not_fire_kind_rule(self):
        cfg = RouterConfig(
            kind_rules=[KindRule(kind=FileKind.UNKNOWN, destination_repo="mystery")]
        )
        router = ProjectRouter(cfg)
        items = [make_item(FileKind.UNKNOWN)] * 5
        dec = router.route("unknown-proj", items)
        # UNKNOWN items excluded from kind counting → dominant_kind stays UNKNOWN
        # kind_rules should NOT fire for UNKNOWN
        assert dec.confidence == "low"

    def test_only_unknown_kind_items_falls_back(self):
        cfg = RouterConfig(fallback_repo="catch-all")
        router = ProjectRouter(cfg)
        items = [make_item(FileKind.UNKNOWN)] * 3
        dec = router.route("mystery", items)
        assert dec.destination_repo == "catch-all"


# ===========================================================================
# ProjectRouter — route_all and decisions_to_repo
# ===========================================================================

class TestProjectRouterRouteAll:
    def test_route_all_returns_all_decisions(self):
        router = ProjectRouter()
        groups = {
            "proj_b": [make_item(FileKind.CAD)],
            "proj_a": [make_item(FileKind.CODE)],
        }
        decisions = router.route_all(groups)
        assert len(decisions) == 2

    def test_route_all_sorted_by_project_name(self):
        router = ProjectRouter()
        groups = {
            "proj_z": [],
            "proj_a": [],
            "proj_m": [],
        }
        decisions = router.route_all(groups)
        names = [d.project for d in decisions]
        assert names == sorted(names)

    def test_decisions_to_repo_groups_by_repo(self):
        cfg = RouterConfig(
            keyword_rules=[
                KeywordRule(pattern="sew", destination_repo="sewing"),
            ],
            fallback_repo="misc",
        )
        router = ProjectRouter(cfg)
        groups = {
            "sewn-vest": [],
            "random": [],
            "another-sew": [],
        }
        decisions = router.route_all(groups)
        by_repo = router.decisions_to_repo(decisions)
        assert "sewing" in by_repo
        assert len(by_repo["sewing"]) == 2
        assert "misc" in by_repo
        assert len(by_repo["misc"]) == 1

    def test_decisions_to_repo_empty_list(self):
        router = ProjectRouter()
        result = router.decisions_to_repo([])
        assert result == {}

    def test_item_count_set(self):
        router = ProjectRouter()
        items = [make_item(FileKind.CAD)] * 7
        dec = router.route("my-proj", items)
        assert dec.item_count == 7


# ===========================================================================
# Integration: all three rule types wired together
# ===========================================================================

class TestRouterIntegration:
    def _full_router(self) -> ProjectRouter:
        cfg = RouterConfig(
            keyword_rules=[
                KeywordRule(pattern="shacket", destination_repo="sewing"),
            ],
            kind_rules=[
                KindRule(kind=FileKind.CAD, destination_repo="cad-projects"),
                KindRule(kind=FileKind.CODE, destination_repo="code-projects"),
            ],
            explicit_overrides={"special-proj": "vip-repo"},
            fallback_repo="archive-misc",
        )
        return ProjectRouter(cfg)

    def test_explicit_beats_keyword(self):
        router = self._full_router()
        # Even if project name contains "shacket", explicit override wins
        cfg = RouterConfig(
            keyword_rules=[KeywordRule(pattern="shacket", destination_repo="sewing")],
            explicit_overrides={"shacket-override": "vip-repo"},
        )
        r2 = ProjectRouter(cfg)
        dec = r2.route("shacket-override", [])
        assert dec.destination_repo == "vip-repo"
        assert dec.confidence == "high"
        assert dec.rule_used == "explicit override"

    def test_keyword_beats_kind(self):
        router = self._full_router()
        items = [make_item(FileKind.CAD)] * 5
        dec = router.route("my-shacket-cad", items)
        # keyword rule fires before kind rule
        assert dec.destination_repo == "sewing"
        assert dec.confidence == "high"

    def test_kind_fires_when_no_keyword_match(self):
        router = self._full_router()
        items = [make_item(FileKind.CAD)] * 5
        dec = router.route("robot-arm", items)
        assert dec.destination_repo == "cad-projects"
        assert dec.confidence == "medium"

    def test_fallback_fires_when_nothing_matches(self):
        router = self._full_router()
        dec = router.route("mystery-project", [])
        assert dec.destination_repo == "archive-misc"
        assert dec.confidence == "low"
