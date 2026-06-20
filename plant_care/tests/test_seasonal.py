"""Tests for plant_care.seasonal — seasonal care-plan generator."""

from __future__ import annotations

import datetime
import pytest

from plant_care.models import CareProfile
from plant_care.seasonal import (
    Hemisphere,
    Season,
    SeasonalAdjustment,
    adjusted_profile_for_date,
    adjustment_for,
    care_calendar,
    months_in_season,
    season_for,
    seasonal_plan,
    year_plan,
)

BASE_PROFILE = CareProfile(
    watering_interval_days=7,
    fertilize_interval_days=30,
    light_needs="bright-indirect",
    humidity="moderate",
)


# ── 1. season_for ──────────────────────────────────────────────────────────────


class TestSeasonFor:
    # Northern hemisphere
    def test_winter_december(self):
        assert season_for(datetime.date(2024, 12, 1)) == Season.WINTER

    def test_winter_january(self):
        assert season_for(datetime.date(2024, 1, 15)) == Season.WINTER

    def test_winter_february(self):
        assert season_for(datetime.date(2024, 2, 28)) == Season.WINTER

    def test_spring_march(self):
        assert season_for(datetime.date(2024, 3, 20)) == Season.SPRING

    def test_spring_may(self):
        assert season_for(datetime.date(2024, 5, 31)) == Season.SPRING

    def test_summer_june(self):
        assert season_for(datetime.date(2024, 6, 15)) == Season.SUMMER

    def test_summer_august(self):
        assert season_for(datetime.date(2024, 8, 1)) == Season.SUMMER

    def test_autumn_september(self):
        assert season_for(datetime.date(2024, 9, 1)) == Season.AUTUMN

    def test_autumn_november(self):
        assert season_for(datetime.date(2024, 11, 30)) == Season.AUTUMN

    # Southern hemisphere
    def test_southern_june_is_winter(self):
        assert season_for(datetime.date(2024, 6, 1), Hemisphere.SOUTHERN) == Season.WINTER

    def test_southern_december_is_summer(self):
        assert season_for(datetime.date(2024, 12, 15), Hemisphere.SOUTHERN) == Season.SUMMER

    def test_southern_march_is_autumn(self):
        assert season_for(datetime.date(2024, 3, 1), Hemisphere.SOUTHERN) == Season.AUTUMN

    def test_southern_september_is_spring(self):
        assert season_for(datetime.date(2024, 9, 1), Hemisphere.SOUTHERN) == Season.SPRING

    def test_default_hemisphere_is_northern(self):
        # June → SUMMER in northern
        assert season_for(datetime.date(2024, 6, 15)) == Season.SUMMER


# ── 2. months_in_season ───────────────────────────────────────────────────────


class TestMonthsInSeason:
    def test_northern_winter(self):
        months = months_in_season(Season.WINTER, Hemisphere.NORTHERN)
        assert set(months) == {12, 1, 2}
        assert months == sorted(months)

    def test_northern_summer(self):
        months = months_in_season(Season.SUMMER, Hemisphere.NORTHERN)
        assert set(months) == {6, 7, 8}

    def test_northern_spring(self):
        months = months_in_season(Season.SPRING, Hemisphere.NORTHERN)
        assert set(months) == {3, 4, 5}

    def test_northern_autumn(self):
        months = months_in_season(Season.AUTUMN, Hemisphere.NORTHERN)
        assert set(months) == {9, 10, 11}

    def test_southern_winter(self):
        months = months_in_season(Season.WINTER, Hemisphere.SOUTHERN)
        assert set(months) == {6, 7, 8}

    def test_each_month_appears_exactly_once(self):
        all_months = []
        for s in Season:
            all_months.extend(months_in_season(s, Hemisphere.NORTHERN))
        assert sorted(all_months) == list(range(1, 13))

    def test_returns_three_months(self):
        for s in Season:
            assert len(months_in_season(s)) == 3


# ── 3. adjustment_for ─────────────────────────────────────────────────────────


class TestAdjustmentFor:
    def test_returns_seasonal_adjustment(self):
        adj = adjustment_for(Season.SPRING)
        assert isinstance(adj, SeasonalAdjustment)

    def test_summer_active_growth(self):
        assert adjustment_for(Season.SUMMER).active_growth is True

    def test_winter_not_active_growth(self):
        assert adjustment_for(Season.WINTER).active_growth is False

    def test_spring_active_growth(self):
        assert adjustment_for(Season.SPRING).active_growth is True

    def test_autumn_not_active_growth(self):
        assert adjustment_for(Season.AUTUMN).active_growth is False

    def test_winter_watering_multiplier_gt_1(self):
        # Winter = less frequent watering
        assert adjustment_for(Season.WINTER).watering_multiplier > 1.0

    def test_summer_watering_multiplier_lt_1(self):
        # Summer = more frequent watering
        assert adjustment_for(Season.SUMMER).watering_multiplier < 1.0

    def test_winter_fertilize_multiplier_gt_1(self):
        # Winter = less frequent fertilising
        assert adjustment_for(Season.WINTER).fertilize_multiplier > 1.0

    def test_summer_fertilize_multiplier_lt_1(self):
        # Summer = more frequent fertilising
        assert adjustment_for(Season.SUMMER).fertilize_multiplier < 1.0

    def test_all_seasons_have_notes(self):
        for s in Season:
            adj = adjustment_for(s)
            assert len(adj.notes) > 10

    def test_to_dict_keys(self):
        adj = adjustment_for(Season.SPRING)
        d = adj.to_dict()
        for key in ("season", "watering_multiplier", "fertilize_multiplier",
                    "active_growth", "notes"):
            assert key in d

    def test_to_dict_season_is_string(self):
        d = adjustment_for(Season.WINTER).to_dict()
        assert d["season"] == "winter"


# ── 4. seasonal_plan ──────────────────────────────────────────────────────────


class TestSeasonalPlan:
    def test_returns_care_profile(self):
        result = seasonal_plan(BASE_PROFILE, Season.SUMMER)
        assert isinstance(result, CareProfile)

    def test_does_not_mutate_original(self):
        original_water = BASE_PROFILE.watering_interval_days
        seasonal_plan(BASE_PROFILE, Season.SUMMER)
        assert BASE_PROFILE.watering_interval_days == original_water

    def test_summer_watering_more_frequent(self):
        result = seasonal_plan(BASE_PROFILE, Season.SUMMER)
        assert result.watering_interval_days < BASE_PROFILE.watering_interval_days

    def test_winter_watering_less_frequent(self):
        result = seasonal_plan(BASE_PROFILE, Season.WINTER)
        assert result.watering_interval_days > BASE_PROFILE.watering_interval_days

    def test_winter_fertilize_less_frequent(self):
        result = seasonal_plan(BASE_PROFILE, Season.WINTER)
        assert result.fertilize_interval_days > BASE_PROFILE.fertilize_interval_days

    def test_summer_fertilize_more_frequent(self):
        result = seasonal_plan(BASE_PROFILE, Season.SUMMER)
        assert result.fertilize_interval_days < BASE_PROFILE.fertilize_interval_days

    def test_light_needs_preserved(self):
        result = seasonal_plan(BASE_PROFILE, Season.WINTER)
        assert result.light_needs == BASE_PROFILE.light_needs

    def test_humidity_preserved(self):
        result = seasonal_plan(BASE_PROFILE, Season.SUMMER)
        assert result.humidity == BASE_PROFILE.humidity

    def test_watering_at_least_1_day(self):
        # Very short interval profile should not go below 1 day
        short_profile = CareProfile(
            watering_interval_days=1,
            fertilize_interval_days=7,
            light_needs="full-sun",
            humidity="low",
        )
        result = seasonal_plan(short_profile, Season.SUMMER)
        assert result.watering_interval_days >= 1

    def test_fertilize_at_least_7_days(self):
        short_profile = CareProfile(
            watering_interval_days=7,
            fertilize_interval_days=7,
            light_needs="full-sun",
            humidity="low",
        )
        result = seasonal_plan(short_profile, Season.SUMMER)
        assert result.fertilize_interval_days >= 7

    def test_seasonal_ordering(self):
        # summer < spring < autumn < winter in terms of watering frequency
        summer = seasonal_plan(BASE_PROFILE, Season.SUMMER)
        spring = seasonal_plan(BASE_PROFILE, Season.SPRING)
        autumn = seasonal_plan(BASE_PROFILE, Season.AUTUMN)
        winter = seasonal_plan(BASE_PROFILE, Season.WINTER)
        assert summer.watering_interval_days <= spring.watering_interval_days
        assert spring.watering_interval_days <= autumn.watering_interval_days
        assert autumn.watering_interval_days <= winter.watering_interval_days


# ── 5. year_plan ──────────────────────────────────────────────────────────────


class TestYearPlan:
    def test_returns_dict(self):
        plan = year_plan(BASE_PROFILE)
        assert isinstance(plan, dict)

    def test_all_seasons_present(self):
        plan = year_plan(BASE_PROFILE)
        for s in Season:
            assert s in plan

    def test_values_are_seasonal_adjustments(self):
        plan = year_plan(BASE_PROFILE)
        for adj in plan.values():
            assert isinstance(adj, SeasonalAdjustment)

    def test_hemisphere_does_not_change_adjustment_content(self):
        # year_plan returns the same seasonal adjustments regardless of hemisphere
        # (the hemisphere only affects date→season mapping, not the adjustment itself)
        north = year_plan(BASE_PROFILE, Hemisphere.NORTHERN)
        south = year_plan(BASE_PROFILE, Hemisphere.SOUTHERN)
        assert north.keys() == south.keys()


# ── 6. adjusted_profile_for_date ─────────────────────────────────────────────


class TestAdjustedProfileForDate:
    def test_june_northern_is_summer(self):
        june = datetime.date(2024, 6, 15)
        result = adjusted_profile_for_date(BASE_PROFILE, june, Hemisphere.NORTHERN)
        summer = seasonal_plan(BASE_PROFILE, Season.SUMMER)
        assert result.watering_interval_days == summer.watering_interval_days

    def test_december_northern_is_winter(self):
        dec = datetime.date(2024, 12, 25)
        result = adjusted_profile_for_date(BASE_PROFILE, dec, Hemisphere.NORTHERN)
        winter = seasonal_plan(BASE_PROFILE, Season.WINTER)
        assert result.watering_interval_days == winter.watering_interval_days

    def test_june_southern_is_winter(self):
        june = datetime.date(2024, 6, 15)
        result = adjusted_profile_for_date(BASE_PROFILE, june, Hemisphere.SOUTHERN)
        winter = seasonal_plan(BASE_PROFILE, Season.WINTER)
        assert result.watering_interval_days == winter.watering_interval_days

    def test_default_is_northern(self):
        june = datetime.date(2024, 6, 15)
        default = adjusted_profile_for_date(BASE_PROFILE, june)
        explicit = adjusted_profile_for_date(BASE_PROFILE, june, Hemisphere.NORTHERN)
        assert default.watering_interval_days == explicit.watering_interval_days


# ── 7. care_calendar ─────────────────────────────────────────────────────────


class TestCareCalendar:
    def test_returns_12_entries(self):
        cal = care_calendar(BASE_PROFILE)
        assert len(cal) == 12

    def test_each_entry_has_required_keys(self):
        cal = care_calendar(BASE_PROFILE)
        for entry in cal:
            for k in ("month", "season", "watering_interval_days",
                      "fertilize_interval_days", "active_growth", "notes"):
                assert k in entry

    def test_months_1_to_12(self):
        cal = care_calendar(BASE_PROFILE)
        months = [e["month"] for e in cal]
        assert months == list(range(1, 13))

    def test_northern_june_is_summer(self):
        cal = care_calendar(BASE_PROFILE, Hemisphere.NORTHERN)
        june_entry = cal[5]  # index 5 = month 6
        assert june_entry["season"] == "summer"

    def test_southern_june_is_winter(self):
        cal = care_calendar(BASE_PROFILE, Hemisphere.SOUTHERN)
        june_entry = cal[5]
        assert june_entry["season"] == "winter"

    def test_active_growth_true_in_summer(self):
        cal = care_calendar(BASE_PROFILE)
        june_entry = next(e for e in cal if e["month"] == 6)
        assert june_entry["active_growth"] is True

    def test_active_growth_false_in_winter(self):
        cal = care_calendar(BASE_PROFILE)
        jan_entry = next(e for e in cal if e["month"] == 1)
        assert jan_entry["active_growth"] is False

    def test_summer_watering_shorter_than_winter(self):
        cal = care_calendar(BASE_PROFILE)
        june = next(e for e in cal if e["month"] == 6)
        jan = next(e for e in cal if e["month"] == 1)
        assert june["watering_interval_days"] < jan["watering_interval_days"]

    def test_notes_nonempty(self):
        cal = care_calendar(BASE_PROFILE)
        for entry in cal:
            assert len(entry["notes"]) > 10


# ── 8. Season / Hemisphere enum completeness ─────────────────────────────────


class TestEnums:
    def test_season_has_four_values(self):
        assert len(list(Season)) == 4

    def test_hemisphere_has_two_values(self):
        assert len(list(Hemisphere)) == 2

    def test_season_values_are_strings(self):
        for s in Season:
            assert isinstance(s.value, str)

    def test_hemisphere_values_are_strings(self):
        for h in Hemisphere:
            assert isinstance(h.value, str)
