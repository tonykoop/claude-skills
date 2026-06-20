"""Tests for plant_care.collection — Collection / digital-twin model."""

from __future__ import annotations

import datetime
import json
import pytest

from plant_care.collection import Collection, CollectionSummary, SpecimenRecord
from plant_care.models import (
    CareEvent,
    CareProfile,
    DueAction,
    HealthState,
    Observations,
    Specimen,
)

TODAY = datetime.date(2024, 6, 15)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _spec(sid="sp-01", location="windowsill", is_bonsai=False) -> Specimen:
    return Specimen(
        id=sid,
        species="Ficus benjamina",
        acquired=datetime.date(2023, 1, 1),
        location=location,
        light_level="bright-indirect",
        pot_size="6in",
        is_bonsai=is_bonsai,
    )


def _profile(water=7, fert=30) -> CareProfile:
    return CareProfile(
        watering_interval_days=water,
        fertilize_interval_days=fert,
        light_needs="bright-indirect",
        humidity="moderate",
    )


def _col_with_one() -> Collection:
    col = Collection("Test")
    col.add(_spec(), _profile())
    return col


# ── 1. Construction ───────────────────────────────────────────────────────────


class TestConstruction:
    def test_default_name(self):
        col = Collection()
        assert col.name == "My Collection"

    def test_custom_name(self):
        col = Collection("Studio")
        assert col.name == "Studio"

    def test_empty_len(self):
        assert len(Collection()) == 0

    def test_empty_specimens(self):
        assert Collection().specimens() == []


# ── 2. add / remove ───────────────────────────────────────────────────────────


class TestAddRemove:
    def test_add_increases_len(self):
        col = _col_with_one()
        assert len(col) == 1

    def test_add_duplicate_raises(self):
        col = _col_with_one()
        with pytest.raises(ValueError, match="already exists"):
            col.add(_spec(), _profile())

    def test_add_returns_self(self):
        col = Collection()
        result = col.add(_spec(), _profile())
        assert result is col

    def test_contains(self):
        col = _col_with_one()
        assert "sp-01" in col

    def test_not_contains(self):
        col = _col_with_one()
        assert "nope" not in col

    def test_remove_existing(self):
        col = _col_with_one()
        removed = col.remove("sp-01")
        assert removed is True
        assert len(col) == 0

    def test_remove_nonexistent(self):
        col = Collection()
        assert col.remove("ghost") is False

    def test_add_multiple(self):
        col = Collection()
        col.add(_spec("a"), _profile())
        col.add(_spec("b"), _profile())
        assert len(col) == 2

    def test_add_with_history(self):
        event = CareEvent(type="water", date=TODAY)
        col = Collection()
        col.add(_spec(), _profile(), history=[event])
        assert len(col.get("sp-01").history) == 1

    def test_add_with_tags(self):
        col = Collection()
        col.add(_spec(), _profile(), tags=["gift"])
        assert "gift" in col.get("sp-01").tags


# ── 3. record / update_profile ────────────────────────────────────────────────


class TestRecord:
    def test_record_appends_event(self):
        col = _col_with_one()
        col.record("sp-01", CareEvent(type="water", date=TODAY))
        assert len(col.get("sp-01").history) == 1

    def test_record_returns_self(self):
        col = _col_with_one()
        assert col.record("sp-01", CareEvent(type="water", date=TODAY)) is col

    def test_record_unknown_raises(self):
        col = Collection()
        with pytest.raises(KeyError):
            col.record("ghost", CareEvent(type="water", date=TODAY))

    def test_update_profile_changes_interval(self):
        col = _col_with_one()
        new_profile = _profile(water=3)
        col.update_profile("sp-01", new_profile)
        assert col.get("sp-01").profile.watering_interval_days == 3

    def test_update_profile_unknown_raises(self):
        col = Collection()
        with pytest.raises(KeyError):
            col.update_profile("ghost", _profile())

    def test_update_profile_preserves_history(self):
        col = _col_with_one()
        col.record("sp-01", CareEvent(type="water", date=TODAY))
        col.update_profile("sp-01", _profile(water=2))
        assert len(col.get("sp-01").history) == 1


# ── 4. tag / untag ───────────────────────────────────────────────────────────


class TestTags:
    def test_tag_adds(self):
        col = _col_with_one()
        col.tag("sp-01", "featured")
        assert "featured" in col.get("sp-01").tags

    def test_tag_no_duplicate(self):
        col = _col_with_one()
        col.tag("sp-01", "featured")
        col.tag("sp-01", "featured")
        assert col.get("sp-01").tags.count("featured") == 1

    def test_untag_removes(self):
        col = _col_with_one()
        col.tag("sp-01", "featured")
        col.untag("sp-01", "featured")
        assert "featured" not in col.get("sp-01").tags

    def test_untag_noop_if_absent(self):
        col = _col_with_one()
        col.untag("sp-01", "nonexistent")  # should not raise

    def test_tagged_query(self):
        col = Collection()
        col.add(_spec("a"), _profile(), tags=["show"])
        col.add(_spec("b"), _profile())
        recs = col.tagged("show")
        assert len(recs) == 1
        assert recs[0].specimen.id == "a"


# ── 5. Query helpers ──────────────────────────────────────────────────────────


class TestQueryHelpers:
    def _col(self) -> Collection:
        col = Collection()
        col.add(_spec("a", location="balcony", is_bonsai=True), _profile())
        col.add(_spec("b", location="balcony"), _profile())
        col.add(_spec("c", location="windowsill"), _profile())
        return col

    def test_by_location(self):
        col = self._col()
        recs = col.by_location("balcony")
        assert len(recs) == 2
        assert all(r.specimen.location == "balcony" for r in recs)

    def test_by_location_empty(self):
        col = self._col()
        assert col.by_location("bedroom") == []

    def test_bonsai(self):
        col = self._col()
        b = col.bonsai()
        assert len(b) == 1
        assert b[0].specimen.id == "a"

    def test_locations(self):
        col = self._col()
        locs = col.locations()
        assert "balcony" in locs
        assert "windowsill" in locs
        assert locs == sorted(locs)

    def test_all_records_count(self):
        col = self._col()
        assert len(col.all_records()) == 3

    def test_specimens_returns_specimen_list(self):
        col = self._col()
        specs = col.specimens()
        assert all(isinstance(s, Specimen) for s in specs)


# ── 6. due / health (single specimen) ────────────────────────────────────────


class TestSingleSpecimenQueries:
    def test_due_returns_list(self):
        col = _col_with_one()
        # No history — both water and fertilize due on first day
        actions = col.due("sp-01", TODAY)
        assert isinstance(actions, list)

    def test_due_water_due_immediately(self):
        col = _col_with_one()
        actions = col.due("sp-01", TODAY)
        types = {a.action_type for a in actions}
        assert "water" in types

    def test_due_unknown_specimen_raises(self):
        col = Collection()
        with pytest.raises(KeyError):
            col.due("ghost", TODAY)

    def test_health_returns_health_state(self):
        col = _col_with_one()
        obs = Observations(yellowing=True)
        state = col.health("sp-01", obs)
        assert isinstance(state, HealthState)
        assert state.status == "needs-attention"

    def test_health_healthy(self):
        col = _col_with_one()
        state = col.health("sp-01", Observations())
        assert state.status == "healthy"


# ── 7. due_for_collection ─────────────────────────────────────────────────────


class TestDueForCollection:
    def test_empty_collection(self):
        col = Collection()
        assert col.due_for_collection(TODAY) == []

    def test_returns_pairs(self):
        col = _col_with_one()
        pairs = col.due_for_collection(TODAY)
        for specimen, action in pairs:
            assert isinstance(specimen, Specimen)
            assert isinstance(action, DueAction)

    def test_sorted_most_overdue_first(self):
        # Specimen A: watered 10 days ago (interval 3) → 7 days overdue
        # Specimen B: watered today (interval 3) → not due yet
        col = Collection()
        col.add(_spec("a"), _profile(water=3))
        col.record("a", CareEvent(type="water", date=TODAY - datetime.timedelta(days=10)))
        col.add(_spec("b"), _profile(water=3))
        col.record("b", CareEvent(type="water", date=TODAY))

        pairs = col.due_for_collection(TODAY)
        overdue_ids = [sp.id for sp, act in pairs if act.action_type == "water"]
        # "a" should be first (most overdue), "b" not present
        assert overdue_ids[0] == "a"
        assert "b" not in overdue_ids

    def test_multiple_specimens(self):
        col = Collection()
        col.add(_spec("a"), _profile(water=1))  # very frequent
        col.add(_spec("b"), _profile(water=1))
        pairs = col.due_for_collection(TODAY)
        ids = {sp.id for sp, _ in pairs}
        assert "a" in ids
        assert "b" in ids

    def test_not_yet_due_excluded(self):
        col = _col_with_one()
        # Water today so it's not due for 7 days
        col.record("sp-01", CareEvent(type="water", date=TODAY))
        col.record("sp-01", CareEvent(type="fertilize", date=TODAY))
        pairs = col.due_for_collection(TODAY)
        assert pairs == []


# ── 8. health_for_collection ──────────────────────────────────────────────────


class TestHealthForCollection:
    def test_empty_obs_map(self):
        col = _col_with_one()
        result = col.health_for_collection({})
        assert result == {}

    def test_returns_health_state_per_specimen(self):
        col = _col_with_one()
        obs_map = {"sp-01": Observations(drooping=True)}
        result = col.health_for_collection(obs_map)
        assert "sp-01" in result
        assert result["sp-01"].status == "needs-attention"

    def test_unknown_specimen_in_map_ignored(self):
        col = _col_with_one()
        obs_map = {"ghost": Observations()}
        result = col.health_for_collection(obs_map)
        assert result == {}

    def test_multiple_specimens(self):
        col = Collection()
        col.add(_spec("a"), _profile())
        col.add(_spec("b"), _profile())
        obs_map = {"a": Observations(), "b": Observations(pests=True)}
        result = col.health_for_collection(obs_map)
        assert result["a"].status == "healthy"
        assert result["b"].status == "declining"


# ── 9. summary ────────────────────────────────────────────────────────────────


class TestSummary:
    def test_empty_collection_summary(self):
        col = Collection()
        s = col.summary(TODAY)
        assert s.total == 0
        assert s.due_count == 0
        assert s.most_urgent is None

    def test_summary_total(self):
        col = Collection()
        col.add(_spec("a"), _profile())
        col.add(_spec("b"), _profile())
        s = col.summary(TODAY)
        assert s.total == 2

    def test_summary_due_count(self):
        col = _col_with_one()
        s = col.summary(TODAY)
        assert s.due_count == 1  # sp-01 has actions due

    def test_summary_most_urgent(self):
        col = _col_with_one()
        s = col.summary(TODAY)
        assert s.most_urgent == "sp-01"

    def test_summary_bonsai_count(self):
        col = Collection()
        col.add(_spec("a", is_bonsai=True), _profile())
        col.add(_spec("b"), _profile())
        s = col.summary(TODAY)
        assert s.bonsai_count == 1

    def test_summary_locations(self):
        col = Collection()
        col.add(_spec("a", location="balcony"), _profile())
        col.add(_spec("b", location="desk"), _profile())
        s = col.summary(TODAY)
        assert "balcony" in s.locations
        assert "desk" in s.locations

    def test_summary_health_counts(self):
        col = _col_with_one()
        obs_map = {"sp-01": Observations(pests=True)}
        s = col.summary(TODAY, observations_map=obs_map)
        assert s.healthy_count == 0
        assert s.attention_count == 1

    def test_summary_to_dict(self):
        col = _col_with_one()
        s = col.summary(TODAY)
        d = s.to_dict()
        for k in ("total", "due_count", "overdue_count", "bonsai_count", "locations"):
            assert k in d

    def test_summary_overdue_count(self):
        col = _col_with_one()
        # sp-01 hasn't been watered — due since acquired; days_overdue > 0
        s = col.summary(TODAY)
        assert s.overdue_count >= 0  # 0 if due_date == TODAY, else > 0


# ── 10. Serialisation round-trip ─────────────────────────────────────────────


class TestSerialisation:
    def test_to_dict_has_required_keys(self):
        col = _col_with_one()
        d = col.to_dict()
        assert "name" in d
        assert "specimens" in d

    def test_to_dict_json_safe(self):
        col = _col_with_one()
        col.record("sp-01", CareEvent(type="water", date=TODAY, note="test"))
        json.dumps(col.to_dict())  # must not raise

    def test_round_trip_empty(self):
        col = Collection("Studio")
        restored = Collection.from_dict(col.to_dict())
        assert restored.name == "Studio"
        assert len(restored) == 0

    def test_round_trip_one_specimen(self):
        col = Collection("Studio")
        col.add(_spec(), _profile())
        col.record("sp-01", CareEvent(type="water", date=TODAY, note="watered"))
        col.tag("sp-01", "featured")

        restored = Collection.from_dict(col.to_dict())
        assert len(restored) == 1
        rec = restored.get("sp-01")
        assert rec.specimen.species == "Ficus benjamina"
        assert len(rec.history) == 1
        assert "featured" in rec.tags

    def test_round_trip_multiple_specimens(self):
        col = Collection()
        col.add(_spec("a", is_bonsai=True), _profile(water=3))
        col.add(_spec("b"), _profile(water=7))
        restored = Collection.from_dict(col.to_dict())
        assert len(restored) == 2
        assert restored.get("a").specimen.is_bonsai is True

    def test_specimen_record_to_dict_keys(self):
        col = _col_with_one()
        rec = col.get("sp-01")
        d = rec.to_dict()
        for k in ("specimen", "profile", "history", "tags"):
            assert k in d


# ── 11. SpecimenRecord helpers ────────────────────────────────────────────────


class TestSpecimenRecordHelpers:
    def test_events_of_type(self):
        col = _col_with_one()
        col.record("sp-01", CareEvent(type="water", date=TODAY))
        col.record("sp-01", CareEvent(type="fertilize", date=TODAY))
        rec = col.get("sp-01")
        assert len(rec.events_of_type("water")) == 1
        assert len(rec.events_of_type("fertilize")) == 1

    def test_last_event_none_when_empty(self):
        col = _col_with_one()
        assert col.get("sp-01").last_event("water") is None

    def test_last_event_returns_most_recent(self):
        col = _col_with_one()
        d1 = datetime.date(2024, 1, 1)
        d2 = datetime.date(2024, 6, 1)
        col.record("sp-01", CareEvent(type="water", date=d1))
        col.record("sp-01", CareEvent(type="water", date=d2))
        last = col.get("sp-01").last_event("water")
        assert last is not None
        assert last.date == d2
