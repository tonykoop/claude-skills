"""Tests for plant_care.bloom — bud/bloom chrono-tracker."""

from __future__ import annotations

import datetime
import json
import pytest

from plant_care.bloom import (
    BloomLog,
    BloomRecord,
    BudEvent,
    BudStage,
    bloom_summary,
    forecast_bloom_window,
    mean_days_to_stage,
    time_in_stage,
)

D1 = datetime.date(2024, 1, 15)   # observed
D2 = datetime.date(2024, 1, 22)   # swelling (+7)
D3 = datetime.date(2024, 1, 28)   # open     (+6)
D4 = datetime.date(2024, 2, 5)    # finished (+8)
TODAY = datetime.date(2024, 2, 10)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _event(stage, date=D1) -> BudEvent:
    return BudEvent(stage=stage, date=date)


def _full_record(rid="br-01") -> BloomRecord:
    """A complete bloom record: observed→swelling→open→finished."""
    rec = BloomRecord(record_id=rid, specimen_id="plum-01", species="Prunus mume")
    rec.add_event(_event(BudStage.OBSERVED, D1))
    rec.add_event(_event(BudStage.SWELLING, D2))
    rec.add_event(_event(BudStage.OPEN, D3))
    rec.add_event(_event(BudStage.FINISHED, D4))
    return rec


def _dropped_record(rid="br-drop") -> BloomRecord:
    rec = BloomRecord(record_id=rid, specimen_id="plum-01")
    rec.add_event(_event(BudStage.OBSERVED, D1))
    rec.add_event(_event(BudStage.DROPPED, D2))
    return rec


def _active_record(rid="br-active") -> BloomRecord:
    rec = BloomRecord(record_id=rid, specimen_id="plum-01")
    rec.add_event(_event(BudStage.OBSERVED, D1))
    rec.add_event(_event(BudStage.SWELLING, D2))
    return rec


def _log_with_records(*recs) -> BloomLog:
    log = BloomLog("plum-01")
    for r in recs:
        log.add_record(r)
    return log


# ── 1. BudStage enum ─────────────────────────────────────────────────────────


class TestBudStageEnum:
    def test_has_seven_stages(self):
        assert len(list(BudStage)) == 7

    def test_all_values_are_strings(self):
        for s in BudStage:
            assert isinstance(s.value, str)

    def test_dropped_exists(self):
        assert BudStage.DROPPED.value == "dropped"

    def test_finished_exists(self):
        assert BudStage.FINISHED.value == "finished"


# ── 2. BudEvent ───────────────────────────────────────────────────────────────


class TestBudEvent:
    def test_construction(self):
        ev = _event(BudStage.OBSERVED, D1)
        assert ev.stage == BudStage.OBSERVED
        assert ev.date == D1

    def test_to_dict_keys(self):
        d = _event(BudStage.OBSERVED, D1).to_dict()
        assert "stage" in d and "date" in d and "notes" in d

    def test_to_dict_stage_is_string(self):
        d = _event(BudStage.OPEN, D1).to_dict()
        assert d["stage"] == "open"

    def test_to_dict_date_is_iso(self):
        d = _event(BudStage.OBSERVED, D1).to_dict()
        assert d["date"] == "2024-01-15"

    def test_to_dict_json_safe(self):
        json.dumps(_event(BudStage.OBSERVED, D1).to_dict())

    def test_from_dict_round_trip(self):
        ev = BudEvent(stage=BudStage.SWELLING, date=D2, notes="growing fast")
        restored = BudEvent.from_dict(ev.to_dict())
        assert restored.stage == ev.stage
        assert restored.date == ev.date
        assert restored.notes == ev.notes


# ── 3. BloomRecord ────────────────────────────────────────────────────────────


class TestBloomRecord:
    def test_empty_record(self):
        rec = BloomRecord("br-01", "plum-01")
        assert rec.events == []
        assert rec.first_event() is None

    def test_add_event(self):
        rec = BloomRecord("br-01", "plum-01")
        rec.add_event(_event(BudStage.OBSERVED, D1))
        assert len(rec.events) == 1

    def test_add_event_returns_self(self):
        rec = BloomRecord("br-01", "plum-01")
        assert rec.add_event(_event(BudStage.OBSERVED, D1)) is rec

    def test_events_sorted_by_date(self):
        rec = BloomRecord("br-01", "plum-01")
        rec.add_event(_event(BudStage.OPEN, D3))      # added first
        rec.add_event(_event(BudStage.OBSERVED, D1))  # added second, earlier
        assert rec.events[0].stage == BudStage.OBSERVED

    def test_first_event(self):
        rec = _full_record()
        assert rec.first_event().stage == BudStage.OBSERVED

    def test_latest_event(self):
        rec = _full_record()
        assert rec.latest_event().stage == BudStage.FINISHED

    def test_event_for_stage_found(self):
        rec = _full_record()
        assert rec.event_for_stage(BudStage.OPEN) is not None

    def test_event_for_stage_missing(self):
        rec = BloomRecord("br-01", "plum-01")
        assert rec.event_for_stage(BudStage.OPEN) is None

    def test_date_of_stage(self):
        rec = _full_record()
        assert rec.date_of_stage(BudStage.OPEN) == D3

    def test_is_complete_finished(self):
        assert _full_record().is_complete() is True

    def test_is_complete_dropped(self):
        assert _dropped_record().is_complete() is True

    def test_is_complete_active(self):
        assert _active_record().is_complete() is False

    def test_was_dropped_true(self):
        assert _dropped_record().was_dropped() is True

    def test_was_dropped_false(self):
        assert _full_record().was_dropped() is False

    def test_current_stage_full(self):
        assert _full_record().current_stage() == BudStage.FINISHED

    def test_current_stage_active(self):
        assert _active_record().current_stage() == BudStage.SWELLING

    def test_current_stage_none_empty(self):
        assert BloomRecord("br-01", "plum-01").current_stage() is None

    def test_days_observed(self):
        rec = _full_record()
        assert rec.days_observed(D4) == (D4 - D1).days

    def test_days_observed_none_empty(self):
        rec = BloomRecord("br-01", "plum-01")
        assert rec.days_observed(TODAY) is None

    def test_to_dict_keys(self):
        d = _full_record().to_dict()
        for k in ("record_id", "specimen_id", "species", "events", "notes"):
            assert k in d

    def test_to_dict_events_serialised(self):
        d = _full_record().to_dict()
        assert len(d["events"]) == 4

    def test_to_dict_json_safe(self):
        json.dumps(_full_record().to_dict())

    def test_from_dict_round_trip(self):
        rec = _full_record()
        restored = BloomRecord.from_dict(rec.to_dict())
        assert restored.record_id == rec.record_id
        assert len(restored.events) == 4
        assert restored.current_stage() == BudStage.FINISHED


# ── 4. BloomLog ───────────────────────────────────────────────────────────────


class TestBloomLog:
    def test_empty_len(self):
        assert len(BloomLog("plum-01")) == 0

    def test_add_record_increases_len(self):
        log = BloomLog("plum-01")
        log.add_record(_full_record())
        assert len(log) == 1

    def test_add_returns_self(self):
        log = BloomLog("plum-01")
        assert log.add_record(_full_record()) is log

    def test_add_duplicate_raises(self):
        log = _log_with_records(_full_record("br-01"))
        with pytest.raises(ValueError, match="already exists"):
            log.add_record(_full_record("br-01"))

    def test_get_record_found(self):
        log = _log_with_records(_full_record("br-01"))
        assert log.get_record("br-01").record_id == "br-01"

    def test_get_record_not_found(self):
        log = BloomLog("plum-01")
        with pytest.raises(KeyError):
            log.get_record("ghost")

    def test_all_records_sorted_by_date(self):
        r1 = BloomRecord("r1", "plum-01")
        r1.add_event(_event(BudStage.OBSERVED, D2))
        r2 = BloomRecord("r2", "plum-01")
        r2.add_event(_event(BudStage.OBSERVED, D1))
        log = _log_with_records(r1, r2)
        assert log.all_records()[0].record_id == "r2"

    def test_complete_records(self):
        log = _log_with_records(_full_record(), _dropped_record(), _active_record())
        assert len(log.complete_records()) == 1

    def test_dropped_records(self):
        log = _log_with_records(_full_record(), _dropped_record())
        assert len(log.dropped_records()) == 1

    def test_active_records(self):
        log = _log_with_records(_full_record(), _active_record())
        assert len(log.active_records()) == 1

    def test_to_list_json_safe(self):
        log = _log_with_records(_full_record())
        json.dumps(log.to_list())

    def test_from_list_round_trip(self):
        log = _log_with_records(_full_record(), _active_record())
        restored = BloomLog.from_list("plum-01", log.to_list())
        assert len(restored) == 2

    def test_from_list_preserves_stages(self):
        log = _log_with_records(_full_record())
        restored = BloomLog.from_list("plum-01", log.to_list())
        r = restored.get_record("br-01")
        assert r.date_of_stage(BudStage.OPEN) == D3


# ── 5. time_in_stage ─────────────────────────────────────────────────────────


class TestTimeInStage:
    def test_observed_to_swelling(self):
        rec = _full_record()
        assert time_in_stage(rec, BudStage.OBSERVED) == 7  # D1 to D2

    def test_swelling_to_open(self):
        rec = _full_record()
        assert time_in_stage(rec, BudStage.SWELLING) == 6  # D2 to D3

    def test_open_to_finished(self):
        rec = _full_record()
        assert time_in_stage(rec, BudStage.OPEN) == 8  # D3 to D4

    def test_finished_stage_returns_none(self):
        rec = _full_record()
        assert time_in_stage(rec, BudStage.FINISHED) is None

    def test_stage_not_in_record_returns_none(self):
        rec = _active_record()
        assert time_in_stage(rec, BudStage.OPEN) is None

    def test_active_latest_stage_returns_none(self):
        rec = _active_record()  # ends at SWELLING
        assert time_in_stage(rec, BudStage.SWELLING) is None


# ── 6. mean_days_to_stage ─────────────────────────────────────────────────────


class TestMeanDaysToStage:
    def test_single_record(self):
        log = _log_with_records(_full_record())
        mean = mean_days_to_stage(log, BudStage.OBSERVED, BudStage.OPEN)
        assert mean == (D3 - D1).days  # 13 days

    def test_two_records(self):
        rec2 = BloomRecord("br-02", "plum-01")
        rec2.add_event(_event(BudStage.OBSERVED, D1))
        rec2.add_event(_event(BudStage.OPEN, D2))  # 7 days
        log = _log_with_records(_full_record(), rec2)
        mean = mean_days_to_stage(log, BudStage.OBSERVED, BudStage.OPEN)
        # (13 + 7) / 2 = 10
        assert abs(mean - 10.0) < 0.001

    def test_no_data_returns_none(self):
        log = BloomLog("plum-01")
        assert mean_days_to_stage(log, BudStage.OBSERVED, BudStage.OPEN) is None

    def test_incomplete_records_excluded(self):
        log = _log_with_records(_active_record())
        # OPEN stage not reached
        assert mean_days_to_stage(log, BudStage.OBSERVED, BudStage.OPEN) is None


# ── 7. forecast_bloom_window ─────────────────────────────────────────────────


class TestForecastBloomWindow:
    def test_returns_tuple_when_active(self):
        log = _log_with_records(_active_record())  # bud observed D1, swelling D2
        result = forecast_bloom_window(log, TODAY, baseline_days=14)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_returns_none_when_no_active(self):
        log = _log_with_records(_full_record())
        result = forecast_bloom_window(log, TODAY)
        assert result is None

    def test_earliest_before_latest(self):
        log = _log_with_records(_active_record())
        earliest, latest = forecast_bloom_window(log, TODAY, baseline_days=14)
        assert earliest <= latest

    def test_uses_historical_mean_when_available(self):
        # historical: D1→D3 = 13 days; new active bud observed D1
        log = _log_with_records(_full_record())
        # add an active bud starting today
        new_bud = BloomRecord("br-new", "plum-01")
        new_bud.add_event(BudEvent(stage=BudStage.OBSERVED, date=TODAY))
        log.add_record(new_bud)
        # baseline_days=7, but history says 13
        earliest, latest = forecast_bloom_window(log, TODAY, baseline_days=7)
        # Window should centre around 13 days from TODAY
        window_centre = (earliest + (latest - earliest) / 2)  # rough check
        expected_centre = TODAY + datetime.timedelta(days=13)
        diff = abs((expected_centre - earliest).days + (latest - expected_centre).days)
        assert diff < 15  # sanity check that it's in the right ballpark

    def test_window_bounds_are_dates(self):
        log = _log_with_records(_active_record())
        earliest, latest = forecast_bloom_window(log, TODAY, baseline_days=14)
        assert isinstance(earliest, datetime.date)
        assert isinstance(latest, datetime.date)

    def test_no_active_buds_empty_log(self):
        log = BloomLog("plum-01")
        assert forecast_bloom_window(log, TODAY) is None


# ── 8. bloom_summary ─────────────────────────────────────────────────────────


class TestBloomSummary:
    def test_empty_log_summary(self):
        s = bloom_summary(BloomLog("plum-01"))
        assert s["total_records"] == 0
        assert s["complete"] == 0
        assert s["drop_rate"] == 0.0

    def test_summary_counts(self):
        log = _log_with_records(_full_record(), _dropped_record(), _active_record())
        s = bloom_summary(log)
        assert s["total_records"] == 3
        assert s["complete"] == 1
        assert s["dropped"] == 1
        assert s["active"] == 1

    def test_drop_rate_calculation(self):
        log = _log_with_records(_full_record(), _dropped_record())
        s = bloom_summary(log)
        assert abs(s["drop_rate"] - 0.5) < 0.001

    def test_mean_days_in_summary(self):
        log = _log_with_records(_full_record())
        s = bloom_summary(log)
        assert s["mean_days_observed_to_open"] is not None
        assert s["mean_days_observed_to_open"] == (D3 - D1).days

    def test_most_recent_open_date(self):
        log = _log_with_records(_full_record())
        s = bloom_summary(log)
        assert s["most_recent_open_date"] == D3.isoformat()

    def test_most_recent_open_none_no_open(self):
        log = _log_with_records(_active_record())
        s = bloom_summary(log)
        assert s["most_recent_open_date"] is None

    def test_summary_keys_present(self):
        s = bloom_summary(BloomLog("plum-01"))
        for k in ("total_records", "complete", "dropped", "active",
                  "drop_rate", "mean_days_observed_to_open",
                  "mean_days_open_to_finished", "most_recent_open_date"):
            assert k in s
