"""Tests for plant_care.zones — environment-zone model."""

from __future__ import annotations

import pytest

from plant_care.models import CareProfile
from plant_care.zones import (
    LightLevel,
    MatchQuality,
    Zone,
    ZoneCollection,
    ZoneMatch,
    best_zone,
    match_zone,
    rank_zones,
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _profile(light="bright-indirect", humidity="moderate") -> CareProfile:
    return CareProfile(
        watering_interval_days=7,
        fertilize_interval_days=30,
        light_needs=light,
        humidity=humidity,
    )


def _zone(
    name="South windowsill",
    light=LightLevel.BRIGHT_INDIRECT,
    humidity=55.0,
    tmin=10.0,
    tmax=30.0,
) -> Zone:
    return Zone(
        name=name,
        light_level=light,
        humidity_percent=humidity,
        temp_min_c=tmin,
        temp_max_c=tmax,
    )


def _zcol(*zones: Zone) -> ZoneCollection:
    col = ZoneCollection()
    for z in zones:
        col.add(z)
    return col


# ── 1. Zone construction ──────────────────────────────────────────────────────


class TestZoneConstruction:
    def test_valid_zone(self):
        z = _zone()
        assert z.name == "South windowsill"

    def test_humidity_out_of_range_raises(self):
        with pytest.raises(ValueError, match="humidity_percent"):
            Zone("test", LightLevel.MEDIUM, humidity_percent=110)

    def test_humidity_negative_raises(self):
        with pytest.raises(ValueError):
            Zone("test", LightLevel.MEDIUM, humidity_percent=-1)

    def test_temp_min_ge_max_raises(self):
        with pytest.raises(ValueError, match="temp_min_c"):
            Zone("test", LightLevel.MEDIUM, humidity_percent=50,
                 temp_min_c=30, temp_max_c=30)

    def test_light_rank_full_sun(self):
        z = Zone("sunny", LightLevel.FULL_SUN, humidity_percent=40)
        assert z.light_rank == 5

    def test_light_rank_dark(self):
        z = Zone("dark", LightLevel.DARK, humidity_percent=40)
        assert z.light_rank == 0

    def test_to_dict_keys(self):
        z = _zone()
        d = z.to_dict()
        for k in ("name", "light_level", "humidity_percent", "temp_min_c", "temp_max_c"):
            assert k in d

    def test_to_dict_light_level_is_string(self):
        z = _zone()
        assert isinstance(z.to_dict()["light_level"], str)


# ── 2. ZoneCollection ─────────────────────────────────────────────────────────


class TestZoneCollection:
    def test_empty_len(self):
        assert len(ZoneCollection()) == 0

    def test_add_increases_len(self):
        col = ZoneCollection()
        col.add(_zone())
        assert len(col) == 1

    def test_add_duplicate_raises(self):
        col = ZoneCollection()
        col.add(_zone("Z"))
        with pytest.raises(ValueError, match="already exists"):
            col.add(_zone("Z"))

    def test_add_returns_self(self):
        col = ZoneCollection()
        result = col.add(_zone())
        assert result is col

    def test_remove_existing(self):
        col = ZoneCollection()
        col.add(_zone("Z"))
        assert col.remove("Z") is True
        assert len(col) == 0

    def test_remove_nonexistent(self):
        col = ZoneCollection()
        assert col.remove("ghost") is False

    def test_get_known(self):
        col = ZoneCollection()
        z = _zone("Z")
        col.add(z)
        assert col.get("Z") is z

    def test_get_unknown_raises(self):
        col = ZoneCollection()
        with pytest.raises(KeyError):
            col.get("ghost")

    def test_contains(self):
        col = ZoneCollection()
        col.add(_zone("Z"))
        assert "Z" in col
        assert "X" not in col

    def test_all_zones(self):
        col = _zcol(_zone("A"), _zone("B"))
        assert len(col.all_zones()) == 2

    def test_zones_by_light(self):
        col = _zcol(
            Zone("bright", LightLevel.BRIGHT_INDIRECT, 50),
            Zone("sunny", LightLevel.FULL_SUN, 40),
            Zone("dark", LightLevel.LOW, 50),
        )
        bright = col.zones_by_light(LightLevel.BRIGHT_INDIRECT)
        assert len(bright) == 1
        assert bright[0].name == "bright"

    def test_brightest(self):
        col = _zcol(
            Zone("A", LightLevel.LOW, 50),
            Zone("B", LightLevel.FULL_SUN, 40),
            Zone("C", LightLevel.MEDIUM, 50),
        )
        assert col.brightest().name == "B"

    def test_darkest(self):
        col = _zcol(
            Zone("A", LightLevel.LOW, 50),
            Zone("B", LightLevel.FULL_SUN, 40),
        )
        assert col.darkest().name == "A"

    def test_brightest_empty(self):
        assert ZoneCollection().brightest() is None

    def test_to_dict_keys(self):
        col = _zcol(_zone("Z"))
        d = col.to_dict()
        assert "name" in d
        assert "zones" in d


# ── 3. match_zone — light checks ─────────────────────────────────────────────


class TestMatchZoneLight:
    def test_exact_match_is_good(self):
        profile = _profile(light="bright-indirect", humidity="moderate")
        zone = _zone(light=LightLevel.BRIGHT_INDIRECT, humidity=55)
        result = match_zone(profile, zone)
        assert result.quality == MatchQuality.GOOD
        assert result.light_ok is True

    def test_one_rank_below_is_acceptable(self):
        profile = _profile(light="bright-indirect")
        zone = _zone(light=LightLevel.MEDIUM, humidity=55)  # one rank below
        result = match_zone(profile, zone)
        assert result.quality == MatchQuality.ACCEPTABLE
        assert result.light_ok is False
        assert any("one level" in r for r in result.reasons)

    def test_two_ranks_below_is_poor(self):
        profile = _profile(light="full-sun")
        zone = _zone(light=LightLevel.MEDIUM, humidity=40)  # 3 ranks below
        result = match_zone(profile, zone)
        assert result.quality == MatchQuality.POOR
        assert result.light_ok is False

    def test_zone_too_bright_acceptable(self):
        # Zone much brighter than needed → scorch risk → acceptable
        profile = _profile(light="low")
        zone = _zone(light=LightLevel.FULL_SUN, humidity=45)
        result = match_zone(profile, zone)
        assert result.quality in (MatchQuality.ACCEPTABLE, MatchQuality.POOR)

    def test_zone_slightly_brighter_still_good(self):
        # One rank brighter should not trigger a penalty (tolerant)
        profile = _profile(light="medium")
        zone = _zone(light=LightLevel.BRIGHT_INDIRECT, humidity=55)
        result = match_zone(profile, zone)
        # Slightly brighter: no penalty for being one rank above
        assert result.light_ok is True


# ── 4. match_zone — humidity checks ──────────────────────────────────────────


class TestMatchZoneHumidity:
    def test_humidity_in_range_good(self):
        profile = _profile(humidity="moderate")  # range 40-70
        zone = _zone(light=LightLevel.BRIGHT_INDIRECT, humidity=55)
        result = match_zone(profile, zone)
        assert result.humidity_ok is True

    def test_humidity_slightly_below_acceptable(self):
        profile = _profile(humidity="high")  # range 60-100
        zone = _zone(light=LightLevel.BRIGHT_INDIRECT, humidity=55)  # 5pp below
        result = match_zone(profile, zone)
        assert result.humidity_ok is False
        assert result.quality != MatchQuality.GOOD

    def test_humidity_far_below_poor(self):
        profile = _profile(humidity="high")  # range 60-100
        zone = _zone(light=LightLevel.BRIGHT_INDIRECT, humidity=30)  # 30pp below
        result = match_zone(profile, zone)
        assert result.humidity_ok is False
        assert result.quality == MatchQuality.POOR

    def test_humidity_boundary_exact(self):
        profile = _profile(humidity="moderate")  # 40-70
        zone = _zone(light=LightLevel.BRIGHT_INDIRECT, humidity=40)
        result = match_zone(profile, zone)
        assert result.humidity_ok is True

    def test_humidity_mitigation_when_acceptable(self):
        profile = _profile(humidity="high")
        zone = _zone(light=LightLevel.BRIGHT_INDIRECT, humidity=55)
        result = match_zone(profile, zone)
        if result.quality == MatchQuality.ACCEPTABLE:
            assert len(result.mitigations) > 0


# ── 5. match_zone — combined ──────────────────────────────────────────────────


class TestMatchZoneCombined:
    def test_both_ok_is_good(self):
        profile = _profile(light="bright-indirect", humidity="moderate")
        zone = Zone("perfect", LightLevel.BRIGHT_INDIRECT, humidity_percent=55)
        result = match_zone(profile, zone)
        assert result.quality == MatchQuality.GOOD
        assert result.reasons == []

    def test_light_ok_humidity_poor_is_poor(self):
        profile = _profile(light="medium", humidity="high")
        zone = Zone("dry", LightLevel.MEDIUM, humidity_percent=20)  # too dry
        result = match_zone(profile, zone)
        assert result.quality == MatchQuality.POOR

    def test_to_dict_shape(self):
        profile = _profile()
        zone = _zone()
        result = match_zone(profile, zone)
        d = result.to_dict()
        for k in ("zone_name", "quality", "reasons", "mitigations",
                  "light_ok", "humidity_ok"):
            assert k in d

    def test_to_dict_quality_is_string(self):
        result = match_zone(_profile(), _zone())
        assert isinstance(result.to_dict()["quality"], str)


# ── 6. best_zone ─────────────────────────────────────────────────────────────


class TestBestZone:
    def test_returns_none_for_empty(self):
        assert best_zone(_profile(), ZoneCollection()) is None

    def test_returns_zone(self):
        col = _zcol(_zone())
        result = best_zone(_profile(), col)
        assert isinstance(result, Zone)

    def test_perfect_match_preferred(self):
        perfect = Zone("perfect", LightLevel.BRIGHT_INDIRECT, humidity_percent=55)
        poor = Zone("poor", LightLevel.DARK, humidity_percent=20)
        col = _zcol(perfect, poor)
        result = best_zone(_profile(light="bright-indirect", humidity="moderate"), col)
        assert result.name == "perfect"

    def test_good_over_acceptable(self):
        good = Zone("good", LightLevel.BRIGHT_INDIRECT, humidity_percent=55)
        acceptable = Zone("ok", LightLevel.MEDIUM, humidity_percent=55)
        col = _zcol(good, acceptable)
        result = best_zone(_profile(light="bright-indirect", humidity="moderate"), col)
        assert result.name == "good"

    def test_tiebreaker_light_proximity(self):
        # Both ACCEPTABLE but different light distances
        z1 = Zone("z1", LightLevel.MEDIUM, humidity_percent=55)   # 1 rank below
        z2 = Zone("z2", LightLevel.LOW, humidity_percent=55)       # 2 ranks below
        col = _zcol(z1, z2)
        result = best_zone(_profile(light="bright-indirect", humidity="moderate"), col)
        assert result.name == "z1"


# ── 7. rank_zones ────────────────────────────────────────────────────────────


class TestRankZones:
    def test_returns_list(self):
        col = _zcol(_zone("A"), _zone("B"))
        result = rank_zones(_profile(), col)
        assert isinstance(result, list)

    def test_each_item_is_zone_match_pair(self):
        col = _zcol(_zone())
        result = rank_zones(_profile(), col)
        assert len(result) == 1
        zone, match = result[0]
        assert isinstance(zone, Zone)
        assert isinstance(match, ZoneMatch)

    def test_best_first(self):
        good = Zone("good", LightLevel.BRIGHT_INDIRECT, humidity_percent=55)
        bad = Zone("bad", LightLevel.DARK, humidity_percent=10)
        col = _zcol(good, bad)
        ranked = rank_zones(_profile(light="bright-indirect", humidity="moderate"), col)
        assert ranked[0][0].name == "good"
        assert ranked[-1][0].name == "bad"

    def test_empty_collection(self):
        result = rank_zones(_profile(), ZoneCollection())
        assert result == []


# ── 8. LightLevel enum ───────────────────────────────────────────────────────


class TestLightLevelEnum:
    def test_has_six_levels(self):
        assert len(list(LightLevel)) == 6

    def test_values_are_strings(self):
        for ll in LightLevel:
            assert isinstance(ll.value, str)

    def test_values_unique(self):
        vals = [ll.value for ll in LightLevel]
        assert len(vals) == len(set(vals))


# ── 9. MatchQuality enum ──────────────────────────────────────────────────────


class TestMatchQualityEnum:
    def test_has_three_values(self):
        assert len(list(MatchQuality)) == 3

    def test_good_acceptable_poor(self):
        vals = {q.value for q in MatchQuality}
        assert "good" in vals
        assert "acceptable" in vals
        assert "poor" in vals
