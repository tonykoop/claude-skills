"""Tests for plant_care.scan — photogrammetry/scan-metadata model."""

from __future__ import annotations

import datetime
import json
import pytest

from plant_care.scan import (
    CONFIDENCE_LEVELS,
    ScaleCalibration,
    ScanLog,
    ScanMeasurement,
    ScanSession,
    growth_delta,
    growth_rate,
    latest_measurement,
    measurement_history,
    measurement_summary,
)

DATE_1 = datetime.date(2024, 3, 1)
DATE_2 = datetime.date(2024, 6, 1)   # 92 days later
DATE_3 = datetime.date(2024, 9, 1)   # 184 days from DATE_1


# ── Helpers ───────────────────────────────────────────────────────────────────


def _cal(real_mm=10.0, units=47.3) -> ScaleCalibration:
    return ScaleCalibration(
        reference_name="10mm hex nut",
        reference_real_mm=real_mm,
        reference_measured_units=units,
    )


def _meas(name="trunk_diameter_mm", value_mm=18.5, confidence="medium") -> ScanMeasurement:
    return ScanMeasurement(name=name, value_mm=value_mm, confidence=confidence)


def _session(
    sid="s01", specimen="jp-01", date=DATE_1,
    measurements=None, calibration=None,
) -> ScanSession:
    return ScanSession(
        session_id=sid,
        specimen_id=specimen,
        date=date,
        measurements=measurements or [],
        calibration=calibration,
    )


def _log_two_sessions() -> ScanLog:
    log = ScanLog("jp-01")
    s1 = _session("s01", date=DATE_1, measurements=[
        _meas("trunk_diameter_mm", 18.5),
        _meas("height_mm", 310.0),
    ])
    s2 = _session("s02", date=DATE_2, measurements=[
        _meas("trunk_diameter_mm", 19.2),
        _meas("height_mm", 315.0),
    ])
    log.add_session(s1)
    log.add_session(s2)
    return log


# ── 1. ScaleCalibration ───────────────────────────────────────────────────────


class TestScaleCalibration:
    def test_mm_per_unit(self):
        cal = _cal(real_mm=10.0, units=50.0)
        assert abs(cal.mm_per_unit - 0.2) < 1e-9

    def test_to_real_mm(self):
        cal = _cal(real_mm=10.0, units=50.0)
        assert abs(cal.to_real_mm(100) - 20.0) < 1e-9

    def test_real_mm_zero_raises(self):
        with pytest.raises(ValueError, match="reference_real_mm"):
            ScaleCalibration("ref", reference_real_mm=0, reference_measured_units=10)

    def test_measured_units_zero_raises(self):
        with pytest.raises(ValueError, match="reference_measured_units"):
            ScaleCalibration("ref", reference_real_mm=10, reference_measured_units=0)

    def test_negative_real_mm_raises(self):
        with pytest.raises(ValueError):
            ScaleCalibration("ref", reference_real_mm=-1, reference_measured_units=10)

    def test_to_dict_keys(self):
        d = _cal().to_dict()
        for k in ("reference_name", "reference_real_mm", "reference_measured_units",
                  "mm_per_unit", "notes"):
            assert k in d

    def test_to_dict_mm_per_unit_matches_property(self):
        cal = _cal()
        assert cal.to_dict()["mm_per_unit"] == cal.mm_per_unit

    def test_notes_default_empty(self):
        cal = _cal()
        assert cal.notes == ""


# ── 2. ScanMeasurement ────────────────────────────────────────────────────────


class TestScanMeasurement:
    def test_basic_construction(self):
        m = _meas()
        assert m.name == "trunk_diameter_mm"
        assert m.value_mm == 18.5

    def test_negative_value_mm_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            ScanMeasurement(name="x", value_mm=-1.0)

    def test_invalid_confidence_raises(self):
        with pytest.raises(ValueError, match="confidence"):
            ScanMeasurement(name="x", value_mm=1.0, confidence="excellent")

    def test_all_confidence_levels_accepted(self):
        for conf in CONFIDENCE_LEVELS:
            m = ScanMeasurement(name="x", value_mm=1.0, confidence=conf)
            assert m.confidence == conf

    def test_to_dict_keys(self):
        d = _meas().to_dict()
        for k in ("name", "value_mm", "confidence", "notes"):
            assert k in d

    def test_to_dict_json_safe(self):
        json.dumps(_meas().to_dict())  # must not raise

    def test_from_dict_round_trip(self):
        m = ScanMeasurement(name="height_mm", value_mm=310.5, confidence="high",
                            notes="measured at trunk base")
        restored = ScanMeasurement.from_dict(m.to_dict())
        assert restored.name == m.name
        assert restored.value_mm == m.value_mm
        assert restored.confidence == m.confidence

    def test_from_scan_units_converts(self):
        cal = _cal(real_mm=10.0, units=50.0)  # 0.2 mm/unit
        m = ScanMeasurement.from_scan_units("trunk_diameter_mm", 100.0, cal)
        assert abs(m.value_mm - 20.0) < 1e-9

    def test_from_scan_units_inherits_confidence(self):
        cal = _cal()
        m = ScanMeasurement.from_scan_units("x", 50.0, cal, confidence="high")
        assert m.confidence == "high"


# ── 3. ScanSession ────────────────────────────────────────────────────────────


class TestScanSession:
    def test_empty_session(self):
        s = _session()
        assert len(s.measurements) == 0

    def test_add_measurement(self):
        s = _session()
        s.add_measurement(_meas())
        assert len(s.measurements) == 1

    def test_add_returns_self(self):
        s = _session()
        result = s.add_measurement(_meas())
        assert result is s

    def test_get_measurement_found(self):
        m = _meas("trunk_diameter_mm")
        s = _session(measurements=[m])
        found = s.get_measurement("trunk_diameter_mm")
        assert found is m

    def test_get_measurement_not_found(self):
        s = _session()
        assert s.get_measurement("nonexistent") is None

    def test_value_mm_returns_float(self):
        s = _session(measurements=[_meas("height_mm", 310.0)])
        assert s.value_mm("height_mm") == 310.0

    def test_value_mm_none_for_missing(self):
        s = _session()
        assert s.value_mm("missing") is None

    def test_measurement_names_deduped(self):
        s = _session(measurements=[
            _meas("trunk_diameter_mm", 18.5),
            _meas("trunk_diameter_mm", 18.7),  # duplicate name
            _meas("height_mm", 310.0),
        ])
        names = s.measurement_names()
        assert names.count("trunk_diameter_mm") == 1
        assert "height_mm" in names

    def test_to_dict_keys(self):
        d = _session().to_dict()
        for k in ("session_id", "specimen_id", "date", "measurements",
                  "calibration", "notes"):
            assert k in d

    def test_to_dict_date_is_string(self):
        d = _session(date=DATE_1).to_dict()
        assert d["date"] == "2024-03-01"

    def test_to_dict_json_safe(self):
        s = _session(measurements=[_meas()], calibration=_cal())
        json.dumps(s.to_dict())

    def test_calibration_none_in_dict(self):
        d = _session().to_dict()
        assert d["calibration"] is None

    def test_calibration_dict_included(self):
        s = _session(calibration=_cal())
        d = s.to_dict()
        assert d["calibration"] is not None
        assert "reference_name" in d["calibration"]

    def test_from_dict_round_trip(self):
        s = ScanSession(
            session_id="s01",
            specimen_id="jp-01",
            date=DATE_1,
            measurements=[_meas("trunk_diameter_mm", 18.5)],
            calibration=_cal(),
            notes="first scan",
        )
        restored = ScanSession.from_dict(s.to_dict())
        assert restored.session_id == "s01"
        assert restored.date == DATE_1
        assert len(restored.measurements) == 1
        assert restored.calibration is not None
        assert abs(restored.calibration.mm_per_unit - _cal().mm_per_unit) < 1e-9

    def test_from_dict_no_calibration(self):
        s = _session()
        restored = ScanSession.from_dict(s.to_dict())
        assert restored.calibration is None


# ── 4. ScanLog ────────────────────────────────────────────────────────────────


class TestScanLog:
    def test_empty_len(self):
        log = ScanLog("jp-01")
        assert len(log) == 0

    def test_add_increases_len(self):
        log = ScanLog("jp-01")
        log.add_session(_session())
        assert len(log) == 1

    def test_add_returns_self(self):
        log = ScanLog("jp-01")
        result = log.add_session(_session())
        assert result is log

    def test_add_duplicate_raises(self):
        log = ScanLog("jp-01")
        log.add_session(_session("s01"))
        with pytest.raises(ValueError, match="already exists"):
            log.add_session(_session("s01"))

    def test_sessions_sorted_by_date(self):
        log = ScanLog("jp-01")
        log.add_session(_session("s02", date=DATE_2))
        log.add_session(_session("s01", date=DATE_1))  # added second, earlier date
        sessions = log.all_sessions()
        assert sessions[0].session_id == "s01"
        assert sessions[1].session_id == "s02"

    def test_latest_session(self):
        log = _log_two_sessions()
        assert log.latest_session().session_id == "s02"

    def test_earliest_session(self):
        log = _log_two_sessions()
        assert log.earliest_session().session_id == "s01"

    def test_latest_session_empty(self):
        assert ScanLog("jp-01").latest_session() is None

    def test_earliest_session_empty(self):
        assert ScanLog("jp-01").earliest_session() is None

    def test_get_session_found(self):
        log = _log_two_sessions()
        s = log.get_session("s01")
        assert s.session_id == "s01"

    def test_get_session_not_found(self):
        log = ScanLog("jp-01")
        with pytest.raises(KeyError):
            log.get_session("ghost")

    def test_all_sessions_returns_list(self):
        log = _log_two_sessions()
        assert isinstance(log.all_sessions(), list)
        assert len(log.all_sessions()) == 2

    def test_to_list_json_safe(self):
        log = _log_two_sessions()
        json.dumps(log.to_list())

    def test_from_list_round_trip(self):
        log = _log_two_sessions()
        restored = ScanLog.from_list("jp-01", log.to_list())
        assert len(restored) == 2
        assert restored.latest_session().session_id == "s02"

    def test_from_list_preserves_measurements(self):
        log = _log_two_sessions()
        restored = ScanLog.from_list("jp-01", log.to_list())
        assert restored.get_session("s01").value_mm("trunk_diameter_mm") == 18.5


# ── 5. growth_delta ───────────────────────────────────────────────────────────


class TestGrowthDelta:
    def test_basic_delta(self):
        s1 = _session("s01", date=DATE_1, measurements=[
            _meas("trunk_diameter_mm", 18.5),
        ])
        s2 = _session("s02", date=DATE_2, measurements=[
            _meas("trunk_diameter_mm", 19.2),
        ])
        delta = growth_delta(s1, s2)
        assert abs(delta["trunk_diameter_mm"] - 0.7) < 1e-9

    def test_delta_only_shared_keys(self):
        s1 = _session("s01", measurements=[
            _meas("trunk_diameter_mm", 18.5),
            _meas("height_mm", 310.0),
        ])
        s2 = _session("s02", measurements=[
            _meas("trunk_diameter_mm", 19.2),
            _meas("nebari_spread_mm", 55.0),  # not in s1
        ])
        delta = growth_delta(s1, s2)
        assert "trunk_diameter_mm" in delta
        assert "height_mm" not in delta
        assert "nebari_spread_mm" not in delta

    def test_empty_sessions_return_empty_dict(self):
        s1 = _session("s01")
        s2 = _session("s02")
        assert growth_delta(s1, s2) == {}

    def test_negative_delta_allowed(self):
        s1 = _session("s01", measurements=[_meas("height_mm", 320.0)])
        s2 = _session("s02", measurements=[_meas("height_mm", 310.0)])  # pruned
        delta = growth_delta(s1, s2)
        assert delta["height_mm"] < 0

    def test_zero_delta(self):
        s1 = _session("s01", measurements=[_meas("trunk_diameter_mm", 18.5)])
        s2 = _session("s02", measurements=[_meas("trunk_diameter_mm", 18.5)])
        delta = growth_delta(s1, s2)
        assert delta["trunk_diameter_mm"] == 0.0


# ── 6. measurement_history ────────────────────────────────────────────────────


class TestMeasurementHistory:
    def test_returns_ordered_pairs(self):
        log = _log_two_sessions()
        hist = measurement_history(log, "trunk_diameter_mm")
        assert len(hist) == 2
        assert hist[0] == (DATE_1, 18.5)
        assert hist[1] == (DATE_2, 19.2)

    def test_missing_measurement_skipped(self):
        log = _log_two_sessions()
        hist = measurement_history(log, "nebari_spread_mm")
        assert hist == []

    def test_partial_sessions_included(self):
        log = ScanLog("jp-01")
        log.add_session(_session("s01", date=DATE_1, measurements=[
            _meas("trunk_diameter_mm", 18.5),
        ]))
        log.add_session(_session("s02", date=DATE_2))  # no trunk measurement
        log.add_session(_session("s03", date=DATE_3, measurements=[
            _meas("trunk_diameter_mm", 19.2),
        ]))
        hist = measurement_history(log, "trunk_diameter_mm")
        assert len(hist) == 2
        assert hist[0][0] == DATE_1
        assert hist[1][0] == DATE_3


# ── 7. latest_measurement ─────────────────────────────────────────────────────


class TestLatestMeasurement:
    def test_returns_latest(self):
        log = _log_two_sessions()
        assert latest_measurement(log, "trunk_diameter_mm") == 19.2

    def test_returns_none_if_not_present(self):
        log = _log_two_sessions()
        assert latest_measurement(log, "nebari_spread_mm") is None

    def test_returns_none_for_empty_log(self):
        log = ScanLog("jp-01")
        assert latest_measurement(log, "trunk_diameter_mm") is None


# ── 8. growth_rate ────────────────────────────────────────────────────────────


class TestGrowthRate:
    def test_basic_rate(self):
        log = _log_two_sessions()
        # 0.7 mm over 92 days
        rate = growth_rate(log, "trunk_diameter_mm", DATE_2)
        expected = 0.7 / 92
        assert abs(rate - expected) < 1e-9

    def test_none_for_single_session(self):
        log = ScanLog("jp-01")
        log.add_session(_session("s01", date=DATE_1, measurements=[_meas("height_mm", 310.0)]))
        assert growth_rate(log, "height_mm", DATE_1) is None

    def test_none_for_missing_measurement(self):
        log = _log_two_sessions()
        assert growth_rate(log, "nebari_spread_mm", DATE_2) is None

    def test_none_for_same_date_sessions(self):
        log = ScanLog("jp-01")
        log.add_session(_session("s01", date=DATE_1, measurements=[_meas("height_mm", 310.0)]))
        log.add_session(_session("s02", date=DATE_1, measurements=[_meas("height_mm", 311.0)]))
        # Both on same date → total_days = 0 → None
        assert growth_rate(log, "height_mm", DATE_1) is None

    def test_negative_growth_rate(self):
        log = ScanLog("jp-01")
        log.add_session(_session("s01", date=DATE_1, measurements=[_meas("height_mm", 320.0)]))
        log.add_session(_session("s02", date=DATE_2, measurements=[_meas("height_mm", 310.0)]))
        rate = growth_rate(log, "height_mm", DATE_2)
        assert rate < 0


# ── 9. measurement_summary ────────────────────────────────────────────────────


class TestMeasurementSummary:
    def test_basic_summary(self):
        log = _log_two_sessions()
        s = measurement_summary(log, "trunk_diameter_mm")
        assert s["count"] == 2
        assert s["latest_mm"] == 19.2
        assert s["earliest_mm"] == 18.5
        assert abs(s["total_delta_mm"] - 0.7) < 1e-9

    def test_empty_summary_when_not_present(self):
        log = _log_two_sessions()
        s = measurement_summary(log, "ghost")
        assert s["count"] == 0
        assert s["latest_mm"] is None
        assert s["total_delta_mm"] is None

    def test_history_included(self):
        log = _log_two_sessions()
        s = measurement_summary(log, "trunk_diameter_mm")
        assert len(s["history"]) == 2
        assert s["history"][0]["date"] == DATE_1.isoformat()
        assert s["history"][0]["value_mm"] == 18.5

    def test_min_max(self):
        log = ScanLog("jp-01")
        log.add_session(_session("s01", date=DATE_1, measurements=[_meas("height_mm", 310.0)]))
        log.add_session(_session("s02", date=DATE_2, measurements=[_meas("height_mm", 315.0)]))
        log.add_session(_session("s03", date=DATE_3, measurements=[_meas("height_mm", 312.0)]))
        s = measurement_summary(log, "height_mm")
        assert s["min_mm"] == 310.0
        assert s["max_mm"] == 315.0

    def test_growth_rate_in_summary(self):
        log = _log_two_sessions()
        s = measurement_summary(log, "trunk_diameter_mm")
        assert s["growth_rate_mm_per_day"] is not None
        assert s["growth_rate_mm_per_day"] > 0

    def test_single_session_summary(self):
        log = ScanLog("jp-01")
        log.add_session(_session("s01", date=DATE_1, measurements=[_meas("height_mm", 310.0)]))
        s = measurement_summary(log, "height_mm")
        assert s["count"] == 1
        assert s["total_delta_mm"] is None
        assert s["growth_rate_mm_per_day"] is None
