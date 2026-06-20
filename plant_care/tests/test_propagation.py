"""Tests for plant_care.propagation — PropagationLog and lineage tracker."""

from __future__ import annotations

import datetime
import json
import pytest

from plant_care.propagation import PropagationAttempt, PropagationLog, PropagationMethod

TODAY = datetime.date(2024, 6, 15)
BASE_DATE = datetime.date(2024, 3, 1)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _log_with_one(success=None, child_id=None) -> PropagationLog:
    log = PropagationLog()
    log.add_attempt(
        attempt_id="p01",
        parent_id="jp-01",
        method=PropagationMethod.CUTTING,
        date=BASE_DATE,
        child_id=child_id,
        success=success,
        notes="first cutting",
    )
    return log


# ── 1. PropagationAttempt ─────────────────────────────────────────────────────


class TestPropagationAttempt:
    def test_is_pending_when_success_none(self):
        a = PropagationAttempt(
            attempt_id="x", parent_id="p", child_id=None,
            method=PropagationMethod.SEED, date=BASE_DATE,
        )
        assert a.is_pending is True

    def test_is_pending_false_when_outcome(self):
        a = PropagationAttempt(
            attempt_id="x", parent_id="p", child_id=None,
            method=PropagationMethod.SEED, date=BASE_DATE, success=False,
        )
        assert a.is_pending is False

    def test_age_days(self):
        a = PropagationAttempt(
            attempt_id="x", parent_id="p", child_id=None,
            method=PropagationMethod.CUTTING, date=BASE_DATE,
        )
        assert a.age_days(BASE_DATE + datetime.timedelta(days=30)) == 30

    def test_to_dict_keys(self):
        a = PropagationAttempt(
            attempt_id="p01", parent_id="jp-01", child_id="jp-02",
            method=PropagationMethod.CUTTING, date=BASE_DATE,
            success=True, notes="worked",
        )
        d = a.to_dict()
        for k in ("attempt_id", "parent_id", "child_id", "method",
                  "date", "success", "notes", "outcome_date"):
            assert k in d

    def test_to_dict_method_is_string(self):
        a = PropagationAttempt(
            attempt_id="x", parent_id="p", child_id=None,
            method=PropagationMethod.AIR_LAYER, date=BASE_DATE,
        )
        assert a.to_dict()["method"] == "air-layer"

    def test_to_dict_json_safe(self):
        a = PropagationAttempt(
            attempt_id="x", parent_id="p", child_id=None,
            method=PropagationMethod.CUTTING, date=BASE_DATE,
        )
        json.dumps(a.to_dict())  # must not raise


# ── 2. PropagationLog — add_attempt ──────────────────────────────────────────


class TestAddAttempt:
    def test_add_increases_len(self):
        log = _log_with_one()
        assert len(log) == 1

    def test_add_duplicate_raises(self):
        log = _log_with_one()
        with pytest.raises(ValueError, match="already exists"):
            log.add_attempt(
                attempt_id="p01",
                parent_id="jp-01",
                method=PropagationMethod.CUTTING,
                date=BASE_DATE,
            )

    def test_add_returns_self(self):
        log = PropagationLog()
        result = log.add_attempt(
            attempt_id="p01", parent_id="jp-01",
            method=PropagationMethod.SEED, date=BASE_DATE,
        )
        assert result is log

    def test_add_with_success_updates_lineage(self):
        log = PropagationLog()
        log.add_attempt(
            attempt_id="p01", parent_id="jp-01",
            method=PropagationMethod.CUTTING, date=BASE_DATE,
            success=True, child_id="jp-02",
        )
        assert log.parent_of("jp-02") == "jp-01"

    def test_add_failed_no_lineage(self):
        log = PropagationLog()
        log.add_attempt(
            attempt_id="p01", parent_id="jp-01",
            method=PropagationMethod.CUTTING, date=BASE_DATE,
            success=False,
        )
        assert log.parent_of("jp-02") is None


# ── 3. record_outcome ─────────────────────────────────────────────────────────


class TestRecordOutcome:
    def test_record_success_updates_child_id(self):
        log = _log_with_one()
        log.record_outcome("p01", success=True, child_id="jp-02")
        assert log.get("p01").child_id == "jp-02"

    def test_record_success_updates_lineage(self):
        log = _log_with_one()
        log.record_outcome("p01", success=True, child_id="jp-02")
        assert log.parent_of("jp-02") == "jp-01"

    def test_record_failure_no_lineage(self):
        log = _log_with_one()
        log.record_outcome("p01", success=False)
        assert len(log.successful()) == 0

    def test_record_unknown_raises(self):
        log = PropagationLog()
        with pytest.raises(KeyError):
            log.record_outcome("ghost", success=True, child_id="x")

    def test_record_already_recorded_raises(self):
        log = _log_with_one(success=True, child_id="jp-02")
        with pytest.raises(ValueError, match="already recorded"):
            log.record_outcome("p01", success=True, child_id="jp-03")

    def test_record_success_without_child_id_raises(self):
        log = _log_with_one()
        with pytest.raises(ValueError, match="child_id is required"):
            log.record_outcome("p01", success=True)

    def test_record_updates_notes(self):
        log = _log_with_one()
        log.record_outcome("p01", success=False, notes="rotted off")
        assert log.get("p01").notes == "rotted off"

    def test_record_stores_outcome_date(self):
        log = _log_with_one()
        log.record_outcome("p01", success=True, child_id="jp-02", outcome_date=TODAY)
        assert log.get("p01").outcome_date == TODAY

    def test_record_returns_self(self):
        log = _log_with_one()
        result = log.record_outcome("p01", success=False)
        assert result is log


# ── 4. Lookup / filter API ────────────────────────────────────────────────────


class TestLookupAPI:
    def _log(self) -> PropagationLog:
        log = PropagationLog()
        log.add_attempt(attempt_id="a", parent_id="p1",
                        method=PropagationMethod.CUTTING, date=BASE_DATE,
                        success=True, child_id="c1")
        log.add_attempt(attempt_id="b", parent_id="p1",
                        method=PropagationMethod.CUTTING, date=BASE_DATE,
                        success=False)
        log.add_attempt(attempt_id="c", parent_id="p2",
                        method=PropagationMethod.SEED, date=BASE_DATE)
        return log

    def test_all_attempts(self):
        log = self._log()
        assert len(log.all_attempts()) == 3

    def test_successful(self):
        log = self._log()
        s = log.successful()
        assert len(s) == 1
        assert s[0].attempt_id == "a"

    def test_failed(self):
        log = self._log()
        f = log.failed()
        assert len(f) == 1
        assert f[0].attempt_id == "b"

    def test_pending(self):
        log = self._log()
        p = log.pending()
        assert len(p) == 1
        assert p[0].attempt_id == "c"

    def test_attempts_from(self):
        log = self._log()
        from_p1 = log.attempts_from("p1")
        assert len(from_p1) == 2
        assert all(a.parent_id == "p1" for a in from_p1)

    def test_by_method(self):
        log = self._log()
        cuttings = log.by_method(PropagationMethod.CUTTING)
        assert len(cuttings) == 2

    def test_by_method_seed(self):
        log = self._log()
        seeds = log.by_method(PropagationMethod.SEED)
        assert len(seeds) == 1

    def test_get_known(self):
        log = self._log()
        a = log.get("a")
        assert a.attempt_id == "a"

    def test_get_unknown_raises(self):
        log = PropagationLog()
        with pytest.raises(KeyError):
            log.get("ghost")


# ── 5. Lineage queries ────────────────────────────────────────────────────────


class TestLineage:
    def _three_gen_log(self) -> PropagationLog:
        """Build a 3-generation lineage: grandparent → parent → child."""
        log = PropagationLog()
        log.add_attempt(attempt_id="p1", parent_id="gp", method=PropagationMethod.CUTTING,
                        date=BASE_DATE, success=True, child_id="par")
        log.add_attempt(attempt_id="p2", parent_id="par", method=PropagationMethod.CUTTING,
                        date=BASE_DATE, success=True, child_id="chi")
        return log

    def test_parent_of_direct(self):
        log = _log_with_one(success=True, child_id="jp-02")
        assert log.parent_of("jp-02") == "jp-01"

    def test_parent_of_unknown(self):
        log = PropagationLog()
        assert log.parent_of("ghost") is None

    def test_ancestors_empty_when_root(self):
        log = self._three_gen_log()
        assert log.ancestors_of("gp") == []

    def test_ancestors_one_level(self):
        log = self._three_gen_log()
        ancs = log.ancestors_of("par")
        assert ancs == ["gp"]

    def test_ancestors_two_levels(self):
        log = self._three_gen_log()
        ancs = log.ancestors_of("chi")
        assert ancs == ["par", "gp"]

    def test_descendants_empty_when_leaf(self):
        log = self._three_gen_log()
        assert log.descendants_of("chi") == []

    def test_descendants_one_level(self):
        log = self._three_gen_log()
        desc = log.descendants_of("par")
        assert "chi" in desc

    def test_descendants_full_tree(self):
        log = self._three_gen_log()
        desc = log.descendants_of("gp")
        assert "par" in desc
        assert "chi" in desc

    def test_lineage_tree_root_only(self):
        log = PropagationLog()
        tree = log.lineage_tree("lone-wolf")
        assert tree["id"] == "lone-wolf"
        assert tree["children"] == []

    def test_lineage_tree_with_children(self):
        log = self._three_gen_log()
        tree = log.lineage_tree("gp")
        assert tree["id"] == "gp"
        assert len(tree["children"]) == 1
        child = tree["children"][0]
        assert child["id"] == "par"
        assert len(child["children"]) == 1
        assert child["children"][0]["id"] == "chi"

    def test_lineage_tree_method_recorded(self):
        log = self._three_gen_log()
        tree = log.lineage_tree("gp")
        assert tree["children"][0]["method"] == "cutting"


# ── 6. Statistics ─────────────────────────────────────────────────────────────


class TestStatistics:
    def _log(self) -> PropagationLog:
        log = PropagationLog()
        log.add_attempt(attempt_id="a", parent_id="p", method=PropagationMethod.CUTTING,
                        date=BASE_DATE, success=True, child_id="c1")
        log.add_attempt(attempt_id="b", parent_id="p", method=PropagationMethod.CUTTING,
                        date=BASE_DATE, success=False)
        log.add_attempt(attempt_id="c", parent_id="p", method=PropagationMethod.SEED,
                        date=BASE_DATE, success=True, child_id="c2")
        log.add_attempt(attempt_id="d", parent_id="p", method=PropagationMethod.SEED,
                        date=BASE_DATE)  # pending
        return log

    def test_success_rate_all(self):
        log = self._log()
        # 2 successes out of 3 resolved (1 pending excluded)
        rate = log.success_rate()
        assert abs(rate - 2 / 3) < 0.001

    def test_success_rate_by_method_cutting(self):
        log = self._log()
        rate = log.success_rate(PropagationMethod.CUTTING)
        assert rate == 0.5  # 1 success, 1 failure

    def test_success_rate_by_method_seed(self):
        log = self._log()
        # 1 success, 1 pending (pending excluded from resolved count)
        rate = log.success_rate(PropagationMethod.SEED)
        assert rate == 1.0

    def test_success_rate_empty(self):
        assert PropagationLog().success_rate() == 0.0

    def test_success_rate_all_pending(self):
        log = PropagationLog()
        log.add_attempt(attempt_id="x", parent_id="p",
                        method=PropagationMethod.CUTTING, date=BASE_DATE)
        assert log.success_rate() == 0.0

    def test_attempt_count_by_method(self):
        log = self._log()
        counts = log.attempt_count_by_method()
        assert counts["cutting"] == 2
        assert counts["seed"] == 2

    def test_pending_older_than(self):
        log = PropagationLog()
        # Attempt started 60 days before today
        log.add_attempt(attempt_id="old", parent_id="p",
                        method=PropagationMethod.CUTTING,
                        date=TODAY - datetime.timedelta(days=60))
        log.add_attempt(attempt_id="new", parent_id="p",
                        method=PropagationMethod.CUTTING,
                        date=TODAY - datetime.timedelta(days=5))
        old = log.pending_older_than(TODAY, days=30)
        assert len(old) == 1
        assert old[0].attempt_id == "old"

    def test_pending_older_than_excludes_resolved(self):
        log = PropagationLog()
        log.add_attempt(attempt_id="p", parent_id="x",
                        method=PropagationMethod.SEED,
                        date=TODAY - datetime.timedelta(days=90),
                        success=False)  # resolved — should be excluded
        old = log.pending_older_than(TODAY, days=30)
        assert old == []


# ── 7. PropagationMethod enum completeness ────────────────────────────────────


class TestPropagationMethodEnum:
    def test_all_have_string_values(self):
        for m in PropagationMethod:
            assert isinstance(m.value, str) and len(m.value) > 0

    def test_at_least_five_methods(self):
        assert len(list(PropagationMethod)) >= 5

    def test_values_unique(self):
        vals = [m.value for m in PropagationMethod]
        assert len(vals) == len(set(vals))


# ── 8. Serialisation round-trip ──────────────────────────────────────────────


class TestSerialisation:
    def test_to_list_returns_list(self):
        log = _log_with_one()
        result = log.to_list()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_to_list_json_safe(self):
        log = _log_with_one(success=True, child_id="jp-02")
        json.dumps(log.to_list())  # must not raise

    def test_round_trip_empty(self):
        restored = PropagationLog.from_list([])
        assert len(restored) == 0

    def test_round_trip_one(self):
        log = _log_with_one(success=True, child_id="jp-02")
        restored = PropagationLog.from_list(log.to_list())
        assert len(restored) == 1
        a = restored.get("p01")
        assert a.parent_id == "jp-01"
        assert a.child_id == "jp-02"
        assert a.success is True

    def test_round_trip_lineage_preserved(self):
        log = PropagationLog()
        log.add_attempt(attempt_id="p1", parent_id="gp",
                        method=PropagationMethod.CUTTING, date=BASE_DATE,
                        success=True, child_id="par")
        restored = PropagationLog.from_list(log.to_list())
        assert restored.parent_of("par") == "gp"

    def test_round_trip_pending(self):
        log = _log_with_one()  # success=None
        restored = PropagationLog.from_list(log.to_list())
        assert restored.get("p01").success is None
