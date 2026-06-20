"""Tests for plant_care.cli — command-line interface."""

from __future__ import annotations

import json
import sys
import tempfile
import os
import pytest

from plant_care.cli import build_parser, main


# ── Helpers ───────────────────────────────────────────────────────────────────


def run(argv, capsys=None):
    """Run main() with *argv*; return parsed JSON stdout."""
    main(argv)
    if capsys:
        captured = capsys.readouterr()
        return json.loads(captured.out)
    return None


def run_json(argv, capsys):
    """Run main() with *argv*; return parsed JSON dict/list from stdout."""
    main(argv)
    captured = capsys.readouterr()
    return json.loads(captured.out)


def run_exit(argv):
    """Expect a SystemExit and return its code."""
    with pytest.raises(SystemExit) as exc:
        main(argv)
    return exc.value.code


# ── 1. build_parser ──────────────────────────────────────────────────────────


class TestBuildParser:
    def test_returns_parser(self):
        p = build_parser()
        assert p is not None

    def test_has_due_subcommand(self):
        p = build_parser()
        ns = p.parse_args([
            "due", "--today", "2024-06-15",
            "--water-interval", "7",
            "--fert-interval", "30",
        ])
        assert ns.command == "due"
        assert ns.today == "2024-06-15"

    def test_has_health_subcommand(self):
        p = build_parser()
        ns = p.parse_args(["health"])
        assert ns.command == "health"

    def test_has_seasonal_subcommand(self):
        p = build_parser()
        ns = p.parse_args([
            "seasonal", "--water-interval", "7", "--fert-interval", "30",
            "--season", "summer",
        ])
        assert ns.command == "seasonal"

    def test_has_calendar_subcommand(self):
        p = build_parser()
        ns = p.parse_args([
            "calendar", "--water-interval", "7", "--fert-interval", "30",
        ])
        assert ns.command == "calendar"

    def test_has_zones_subcommand(self):
        p = build_parser()
        ns = p.parse_args([
            "zones", "--light-needs", "medium", "--humidity", "moderate",
        ])
        assert ns.command == "zones"

    def test_has_propagation_subcommand(self):
        p = build_parser()
        ns = p.parse_args(["propagation", "-"])
        assert ns.command == "propagation"

    def test_no_command_exits(self):
        p = build_parser()
        with pytest.raises(SystemExit):
            p.parse_args([])


# ── 2. due subcommand ─────────────────────────────────────────────────────────


class TestDueCommand:
    def test_overdue_water_returned(self, capsys):
        result = run_json([
            "due",
            "--today", "2024-06-15",
            "--water-interval", "7",
            "--fert-interval", "30",
            "--last-watered", "2024-06-01",  # 14 days ago — 7 days overdue
        ], capsys)
        assert isinstance(result, list)
        water_items = [a for a in result if a["action_type"] == "water"]
        assert len(water_items) == 1
        assert water_items[0]["days_overdue"] == 7

    def test_not_yet_due_excluded(self, capsys):
        result = run_json([
            "due",
            "--today", "2024-06-15",
            "--water-interval", "7",
            "--fert-interval", "30",
            "--last-watered", "2024-06-14",  # 1 day ago — not due
        ], capsys)
        water_items = [a for a in result if a["action_type"] == "water"]
        assert len(water_items) == 0

    def test_never_watered_due_today(self, capsys):
        result = run_json([
            "due",
            "--today", "2024-06-15",
            "--water-interval", "7",
            "--fert-interval", "30",
        ], capsys)
        types = [a["action_type"] for a in result]
        assert "water" in types

    def test_output_is_list(self, capsys):
        result = run_json([
            "due",
            "--today", "2024-06-15",
            "--water-interval", "7",
            "--fert-interval", "30",
        ], capsys)
        assert isinstance(result, list)

    def test_output_keys_present(self, capsys):
        result = run_json([
            "due",
            "--today", "2024-06-15",
            "--water-interval", "7",
            "--fert-interval", "30",
        ], capsys)
        for item in result:
            for k in ("action_type", "due_date", "days_overdue", "priority"):
                assert k in item

    def test_both_actions_overdue(self, capsys):
        result = run_json([
            "due",
            "--today", "2024-06-15",
            "--water-interval", "7",
            "--fert-interval", "30",
        ], capsys)
        types = {a["action_type"] for a in result}
        assert "water" in types
        assert "fertilize" in types

    def test_invalid_today_exits(self):
        code = run_exit([
            "due", "--today", "not-a-date",
            "--water-interval", "7", "--fert-interval", "30",
        ])
        assert code != 0

    def test_species_flag_accepted(self, capsys):
        result = run_json([
            "due",
            "--today", "2024-06-15",
            "--water-interval", "7",
            "--fert-interval", "30",
            "--species", "Ficus lyrata",
        ], capsys)
        assert isinstance(result, list)

    def test_last_fertilized_flag(self, capsys):
        result = run_json([
            "due",
            "--today", "2024-06-15",
            "--water-interval", "7",
            "--fert-interval", "30",
            "--last-fertilized", "2024-05-01",  # 45 days ago
        ], capsys)
        fert = [a for a in result if a["action_type"] == "fertilize"]
        assert len(fert) == 1
        assert fert[0]["days_overdue"] == 15


# ── 3. health subcommand ──────────────────────────────────────────────────────


class TestHealthCommand:
    def test_healthy_with_no_flags(self, capsys):
        result = run_json(["health"], capsys)
        assert result["status"] == "healthy"

    def test_pests_causes_declining(self, capsys):
        result = run_json(["health", "--pests"], capsys)
        assert result["status"] == "declining"

    def test_yellowing_alone_needs_attention(self, capsys):
        result = run_json(["health", "--yellowing"], capsys)
        assert result["status"] == "needs-attention"

    def test_yellowing_plus_drooping_declining(self, capsys):
        result = run_json(["health", "--yellowing", "--drooping"], capsys)
        assert result["status"] == "declining"

    def test_leaf_drop_declining(self, capsys):
        result = run_json(["health", "--leaf-drop"], capsys)
        assert result["status"] == "declining"

    def test_dry_soil_needs_attention(self, capsys):
        result = run_json(["health", "--dry-soil"], capsys)
        assert result["status"] == "needs-attention"

    def test_mold_needs_attention(self, capsys):
        result = run_json(["health", "--mold"], capsys)
        assert result["status"] == "needs-attention"

    def test_output_has_flags_key(self, capsys):
        result = run_json(["health", "--pests"], capsys)
        assert "flags" in result
        assert "pests" in result["flags"]

    def test_output_has_notes(self, capsys):
        result = run_json(["health"], capsys)
        assert isinstance(result["notes"], str)
        assert len(result["notes"]) > 0

    def test_species_flag_accepted(self, capsys):
        result = run_json(["health", "--species", "Acer palmatum"], capsys)
        assert result["status"] == "healthy"


# ── 4. seasonal subcommand ────────────────────────────────────────────────────


class TestSeasonalCommand:
    def test_explicit_season_summer(self, capsys):
        result = run_json([
            "seasonal",
            "--water-interval", "7", "--fert-interval", "30",
            "--season", "summer",
        ], capsys)
        assert result["season"] == "summer"
        assert result["active_growth"] is True
        assert result["watering_interval_days"] < 7  # more frequent in summer

    def test_explicit_season_winter(self, capsys):
        result = run_json([
            "seasonal",
            "--water-interval", "7", "--fert-interval", "30",
            "--season", "winter",
        ], capsys)
        assert result["season"] == "winter"
        assert result["active_growth"] is False
        assert result["watering_interval_days"] > 7  # less frequent in winter

    def test_today_flag_derives_season(self, capsys):
        # June in northern hemisphere = summer
        result = run_json([
            "seasonal",
            "--water-interval", "7", "--fert-interval", "30",
            "--today", "2024-06-15",
        ], capsys)
        assert result["season"] == "summer"

    def test_southern_hemisphere_june_is_winter(self, capsys):
        result = run_json([
            "seasonal",
            "--water-interval", "7", "--fert-interval", "30",
            "--today", "2024-06-15",
            "--hemisphere", "southern",
        ], capsys)
        assert result["season"] == "winter"

    def test_output_keys_present(self, capsys):
        result = run_json([
            "seasonal",
            "--water-interval", "7", "--fert-interval", "30",
            "--season", "spring",
        ], capsys)
        for k in ("season", "hemisphere", "watering_interval_days",
                  "fertilize_interval_days", "active_growth", "notes"):
            assert k in result

    def test_notes_nonempty(self, capsys):
        result = run_json([
            "seasonal",
            "--water-interval", "7", "--fert-interval", "30",
            "--season", "autumn",
        ], capsys)
        assert len(result["notes"]) > 10

    def test_invalid_today_exits(self):
        code = run_exit([
            "seasonal",
            "--water-interval", "7", "--fert-interval", "30",
            "--today", "bad-date",
        ])
        assert code != 0

    def test_season_and_today_mutually_exclusive(self):
        """Parser should reject both --season and --today."""
        code = run_exit([
            "seasonal",
            "--water-interval", "7", "--fert-interval", "30",
            "--season", "summer", "--today", "2024-06-15",
        ])
        assert code != 0

    def test_neither_season_nor_today_exits(self):
        code = run_exit([
            "seasonal",
            "--water-interval", "7", "--fert-interval", "30",
        ])
        assert code != 0

    def test_all_four_seasons_accepted(self, capsys):
        for s in ("spring", "summer", "autumn", "winter"):
            result = run_json([
                "seasonal",
                "--water-interval", "7", "--fert-interval", "30",
                "--season", s,
            ], capsys)
            assert result["season"] == s


# ── 5. calendar subcommand ────────────────────────────────────────────────────


class TestCalendarCommand:
    def test_returns_12_entries(self, capsys):
        result = run_json([
            "calendar",
            "--water-interval", "7", "--fert-interval", "30",
        ], capsys)
        assert isinstance(result, list)
        assert len(result) == 12

    def test_months_1_to_12(self, capsys):
        result = run_json([
            "calendar",
            "--water-interval", "7", "--fert-interval", "30",
        ], capsys)
        months = [e["month"] for e in result]
        assert months == list(range(1, 13))

    def test_entry_has_required_keys(self, capsys):
        result = run_json([
            "calendar",
            "--water-interval", "7", "--fert-interval", "30",
        ], capsys)
        for entry in result:
            for k in ("month", "season", "watering_interval_days",
                      "fertilize_interval_days", "active_growth"):
                assert k in entry

    def test_northern_june_is_summer(self, capsys):
        result = run_json([
            "calendar",
            "--water-interval", "7", "--fert-interval", "30",
        ], capsys)
        june = result[5]  # index 5 = month 6
        assert june["season"] == "summer"

    def test_southern_june_is_winter(self, capsys):
        result = run_json([
            "calendar",
            "--water-interval", "7", "--fert-interval", "30",
            "--hemisphere", "southern",
        ], capsys)
        june = result[5]
        assert june["season"] == "winter"

    def test_summer_shorter_interval_than_winter(self, capsys):
        result = run_json([
            "calendar",
            "--water-interval", "7", "--fert-interval", "30",
        ], capsys)
        june_entry = next(e for e in result if e["month"] == 6)
        jan_entry = next(e for e in result if e["month"] == 1)
        assert june_entry["watering_interval_days"] < jan_entry["watering_interval_days"]


# ── 6. zones subcommand ───────────────────────────────────────────────────────


class TestZonesCommand:
    def test_no_zones_returns_empty(self, capsys):
        result = run_json([
            "zones",
            "--light-needs", "bright-indirect",
            "--humidity", "moderate",
        ], capsys)
        assert result["ranked"] == []
        assert result["best"] is None

    def test_single_zone_returned(self, capsys):
        result = run_json([
            "zones",
            "--light-needs", "bright-indirect",
            "--humidity", "moderate",
            "--zone", "South window:bright-indirect:55",
        ], capsys)
        assert len(result["ranked"]) == 1
        assert result["best"] == "South window"

    def test_best_is_good_match(self, capsys):
        result = run_json([
            "zones",
            "--light-needs", "bright-indirect",
            "--humidity", "moderate",
            "--zone", "Perfect:bright-indirect:55",
            "--zone", "Poor:dark:10",
        ], capsys)
        assert result["best"] == "Perfect"

    def test_ranked_order_best_first(self, capsys):
        result = run_json([
            "zones",
            "--light-needs", "bright-indirect",
            "--humidity", "moderate",
            "--zone", "Good:bright-indirect:55",
            "--zone", "Bad:dark:20",
        ], capsys)
        ranked = result["ranked"]
        assert ranked[0]["zone"]["name"] == "Good"
        assert ranked[-1]["zone"]["name"] == "Bad"

    def test_output_has_match_quality(self, capsys):
        result = run_json([
            "zones",
            "--light-needs", "medium",
            "--humidity", "moderate",
            "--zone", "Kitchen:medium:55",
        ], capsys)
        match = result["ranked"][0]["match"]
        assert "quality" in match
        assert match["quality"] in ("good", "acceptable", "poor")

    def test_invalid_zone_spec_exits(self):
        code = run_exit([
            "zones",
            "--light-needs", "medium",
            "--humidity", "moderate",
            "--zone", "BadSpec",  # missing colons
        ])
        assert code != 0

    def test_invalid_light_level_exits(self):
        code = run_exit([
            "zones",
            "--light-needs", "medium",
            "--humidity", "moderate",
            "--zone", "Kitchen:superbright:55",
        ])
        assert code != 0

    def test_multiple_zones_accepted(self, capsys):
        result = run_json([
            "zones",
            "--light-needs", "medium",
            "--humidity", "moderate",
            "--zone", "A:medium:55",
            "--zone", "B:low:45",
            "--zone", "C:bright-indirect:60",
        ], capsys)
        assert len(result["ranked"]) == 3

    def test_all_light_levels_accepted(self, capsys):
        for light in ("dark", "low", "medium", "bright-indirect",
                      "bright-direct", "full-sun"):
            result = run_json([
                "zones",
                "--light-needs", light,
                "--humidity", "moderate",
            ], capsys)
            assert result["ranked"] == []


# ── 7. propagation subcommand ─────────────────────────────────────────────────


class TestPropagationCommand:
    def _make_log_file(self, data):
        """Write *data* to a temp JSON file; return its path."""
        fh = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        json.dump(data, fh)
        fh.close()
        return fh.name

    def _sample_attempts(self):
        return [
            {
                "attempt_id": "p01",
                "parent_id": "jp-01",
                "child_id": "jp-02",
                "method": "cutting",
                "date": "2024-03-01",
                "success": True,
                "notes": "worked",
                "outcome_date": "2024-04-01",
            },
            {
                "attempt_id": "p02",
                "parent_id": "jp-01",
                "child_id": None,
                "method": "cutting",
                "date": "2024-03-15",
                "success": False,
                "notes": "rotted",
                "outcome_date": None,
            },
            {
                "attempt_id": "p03",
                "parent_id": "jp-01",
                "child_id": None,
                "method": "seed",
                "date": "2024-04-01",
                "success": None,
                "notes": "",
                "outcome_date": None,
            },
        ]

    def test_reads_file_and_returns_stats(self, capsys):
        path = self._make_log_file(self._sample_attempts())
        try:
            result = run_json(["propagation", path], capsys)
            assert result["total_attempts"] == 3
        finally:
            os.unlink(path)

    def test_successful_count(self, capsys):
        path = self._make_log_file(self._sample_attempts())
        try:
            result = run_json(["propagation", path], capsys)
            assert result["successful"] == 1
        finally:
            os.unlink(path)

    def test_failed_count(self, capsys):
        path = self._make_log_file(self._sample_attempts())
        try:
            result = run_json(["propagation", path], capsys)
            assert result["failed"] == 1
        finally:
            os.unlink(path)

    def test_pending_count(self, capsys):
        path = self._make_log_file(self._sample_attempts())
        try:
            result = run_json(["propagation", path], capsys)
            assert result["pending"] == 1
        finally:
            os.unlink(path)

    def test_overall_success_rate(self, capsys):
        path = self._make_log_file(self._sample_attempts())
        try:
            result = run_json(["propagation", path], capsys)
            # 1 success out of 2 resolved (1 pending excluded)
            assert abs(result["success_rate_overall"] - 0.5) < 0.001
        finally:
            os.unlink(path)

    def test_by_method_keys_present(self, capsys):
        path = self._make_log_file(self._sample_attempts())
        try:
            result = run_json(["propagation", path], capsys)
            assert "by_method" in result
            assert "cutting" in result["by_method"]
            assert "seed" in result["by_method"]
        finally:
            os.unlink(path)

    def test_by_method_cutting_stats(self, capsys):
        path = self._make_log_file(self._sample_attempts())
        try:
            result = run_json(["propagation", path], capsys)
            cutting = result["by_method"]["cutting"]
            assert cutting["total"] == 2
            assert cutting["successful"] == 1
            assert cutting["failed"] == 1
        finally:
            os.unlink(path)

    def test_empty_log_file(self, capsys):
        path = self._make_log_file([])
        try:
            result = run_json(["propagation", path], capsys)
            assert result["total_attempts"] == 0
            assert result["success_rate_overall"] == 0.0
        finally:
            os.unlink(path)

    def test_nonexistent_file_exits(self):
        code = run_exit(["propagation", "/no/such/file.json"])
        assert code != 0

    def test_invalid_json_exits(self):
        path = self._make_log_file({"not": "a list"})
        try:
            code = run_exit(["propagation", path])
            assert code != 0
        finally:
            os.unlink(path)
