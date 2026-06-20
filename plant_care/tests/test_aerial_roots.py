"""Tests for plant_care.aerial_roots — aerial-root/nebari lifecycle tracker."""

from __future__ import annotations

import datetime
import json
import pytest

from plant_care.aerial_roots import (
    AerialRoot,
    GuidanceNote,
    NebariLog,
    RootEntry,
    RootStage,
    days_in_current_stage,
    days_in_stage,
    guidance_for,
    is_ready_to_guide,
    nebari_summary,
)

D1 = datetime.date(2024, 3, 1)    # tip_promising
D2 = datetime.date(2024, 3, 22)   # guided (+21)
D3 = datetime.date(2024, 5, 1)    # reached_soil (+40)
D4 = datetime.date(2024, 7, 1)    # thickening (+61)
D5 = datetime.date(2024, 11, 1)   # fused (+123)
TODAY = datetime.date(2024, 11, 10)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _entry(stage, date=D1) -> RootEntry:
    return RootEntry(stage=stage, date=date)


def _full_root(rid="ar-01") -> AerialRoot:
    """tip_promising → guided → reached_soil → thickening → fused."""
    r = AerialRoot(root_id=rid, specimen_id="ficus-01",
                   origin_description="left fork")
    r.add_entry(_entry(RootStage.TIP_PROMISING, D1))
    r.add_entry(_entry(RootStage.GUIDED, D2))
    r.add_entry(_entry(RootStage.REACHED_SOIL, D3))
    r.add_entry(_entry(RootStage.THICKENING, D4))
    r.add_entry(_entry(RootStage.FUSED, D5))
    return r


def _active_root(rid="ar-active") -> AerialRoot:
    r = AerialRoot(root_id=rid, specimen_id="ficus-01")
    r.add_entry(_entry(RootStage.TIP_PROMISING, D1))
    r.add_entry(_entry(RootStage.GUIDED, D2))
    return r


def _abandoned_root(rid="ar-abandon") -> AerialRoot:
    r = AerialRoot(root_id=rid, specimen_id="ficus-01")
    r.add_entry(_entry(RootStage.TIP_PROMISING, D1))
    r.add_entry(_entry(RootStage.ABANDONED, D2))
    return r


def _log(*roots) -> NebariLog:
    log = NebariLog("ficus-01")
    for r in roots:
        log.add_root(r)
    return log


# ── 1. RootStage enum ─────────────────────────────────────────────────────────


class TestRootStageEnum:
    def test_six_stages(self):
        assert len(list(RootStage)) == 6

    def test_all_values_strings(self):
        for s in RootStage:
            assert isinstance(s.value, str)

    def test_fused_exists(self):
        assert RootStage.FUSED.value == "fused"

    def test_abandoned_exists(self):
        assert RootStage.ABANDONED.value == "abandoned"

    def test_tip_promising_exists(self):
        assert RootStage.TIP_PROMISING.value == "tip_promising"


# ── 2. RootEntry ─────────────────────────────────────────────────────────────


class TestRootEntry:
    def test_construction(self):
        e = _entry(RootStage.GUIDED, D2)
        assert e.stage == RootStage.GUIDED
        assert e.date == D2

    def test_to_dict_keys(self):
        d = _entry(RootStage.GUIDED, D2).to_dict()
        for k in ("stage", "date", "notes"):
            assert k in d

    def test_to_dict_stage_string(self):
        d = _entry(RootStage.GUIDED, D2).to_dict()
        assert d["stage"] == "guided"

    def test_to_dict_date_iso(self):
        d = _entry(RootStage.GUIDED, D2).to_dict()
        assert d["date"] == "2024-03-22"

    def test_json_safe(self):
        json.dumps(_entry(RootStage.TIP_PROMISING, D1).to_dict())

    def test_from_dict_round_trip(self):
        e = RootEntry(stage=RootStage.REACHED_SOIL, date=D3, notes="soil contact")
        restored = RootEntry.from_dict(e.to_dict())
        assert restored.stage == e.stage
        assert restored.date == e.date
        assert restored.notes == e.notes


# ── 3. GuidanceNote ──────────────────────────────────────────────────────────


class TestGuidanceNote:
    def test_to_dict_keys(self):
        g = guidance_for(RootStage.GUIDED)
        d = g.to_dict()
        for k in ("stage", "action", "notes", "conditions"):
            assert k in d

    def test_all_stages_have_guidance(self):
        for stage in RootStage:
            g = guidance_for(stage)
            assert isinstance(g, GuidanceNote)
            assert len(g.notes) > 20

    def test_guidance_stage_matches(self):
        for stage in RootStage:
            g = guidance_for(stage)
            assert g.stage == stage

    def test_tip_promising_action(self):
        g = guidance_for(RootStage.TIP_PROMISING)
        assert len(g.action) > 0

    def test_fused_action(self):
        g = guidance_for(RootStage.FUSED)
        assert len(g.action) > 0


# ── 4. AerialRoot ────────────────────────────────────────────────────────────


class TestAerialRoot:
    def test_empty_root(self):
        r = AerialRoot("ar-01", "ficus-01")
        assert r.entries == []
        assert r.current_stage() is None

    def test_add_entry_increases_count(self):
        r = AerialRoot("ar-01", "ficus-01")
        r.add_entry(_entry(RootStage.TIP_PROMISING, D1))
        assert len(r.entries) == 1

    def test_add_entry_returns_self(self):
        r = AerialRoot("ar-01", "ficus-01")
        assert r.add_entry(_entry(RootStage.TIP_PROMISING, D1)) is r

    def test_entries_sorted_by_date(self):
        r = AerialRoot("ar-01", "ficus-01")
        r.add_entry(_entry(RootStage.GUIDED, D2))      # added first
        r.add_entry(_entry(RootStage.TIP_PROMISING, D1))  # earlier date
        assert r.entries[0].stage == RootStage.TIP_PROMISING

    def test_advance_stage(self):
        r = AerialRoot("ar-01", "ficus-01")
        r.advance_stage(RootStage.TIP_PROMISING, D1)
        assert r.current_stage() == RootStage.TIP_PROMISING

    def test_current_stage_full(self):
        assert _full_root().current_stage() == RootStage.FUSED

    def test_current_stage_active(self):
        assert _active_root().current_stage() == RootStage.GUIDED

    def test_first_entry(self):
        r = _full_root()
        assert r.first_entry().stage == RootStage.TIP_PROMISING

    def test_latest_entry(self):
        r = _full_root()
        assert r.latest_entry().stage == RootStage.FUSED

    def test_entry_for_stage_found(self):
        r = _full_root()
        e = r.entry_for_stage(RootStage.REACHED_SOIL)
        assert e is not None
        assert e.date == D3

    def test_entry_for_stage_missing(self):
        r = _active_root()
        assert r.entry_for_stage(RootStage.FUSED) is None

    def test_date_of_stage(self):
        assert _full_root().date_of_stage(RootStage.GUIDED) == D2

    def test_is_active_true(self):
        assert _active_root().is_active() is True

    def test_is_active_false_fused(self):
        assert _full_root().is_active() is False

    def test_is_active_false_abandoned(self):
        assert _abandoned_root().is_active() is False

    def test_is_fused(self):
        assert _full_root().is_fused() is True
        assert _active_root().is_fused() is False

    def test_is_abandoned(self):
        assert _abandoned_root().is_abandoned() is True
        assert _full_root().is_abandoned() is False

    def test_age_days(self):
        r = _full_root()
        assert r.age_days(D5) == (D5 - D1).days

    def test_age_days_none_empty(self):
        r = AerialRoot("ar-01", "ficus-01")
        assert r.age_days(TODAY) is None

    def test_to_dict_keys(self):
        d = _full_root().to_dict()
        for k in ("root_id", "specimen_id", "origin_description", "entries", "notes"):
            assert k in d

    def test_to_dict_entries_count(self):
        assert len(_full_root().to_dict()["entries"]) == 5

    def test_to_dict_json_safe(self):
        json.dumps(_full_root().to_dict())

    def test_from_dict_round_trip(self):
        r = _full_root()
        restored = AerialRoot.from_dict(r.to_dict())
        assert restored.root_id == r.root_id
        assert len(restored.entries) == 5
        assert restored.current_stage() == RootStage.FUSED


# ── 5. NebariLog ─────────────────────────────────────────────────────────────


class TestNebariLog:
    def test_empty_len(self):
        assert len(NebariLog("ficus-01")) == 0

    def test_add_root_increases_len(self):
        log = NebariLog("ficus-01")
        log.add_root(_full_root())
        assert len(log) == 1

    def test_add_returns_self(self):
        log = NebariLog("ficus-01")
        assert log.add_root(_full_root()) is log

    def test_add_duplicate_raises(self):
        log = _log(_full_root("ar-01"))
        with pytest.raises(ValueError, match="already exists"):
            log.add_root(_full_root("ar-01"))

    def test_remove_existing(self):
        log = _log(_full_root("ar-01"))
        assert log.remove_root("ar-01") is True
        assert len(log) == 0

    def test_remove_nonexistent(self):
        assert NebariLog("ficus-01").remove_root("ghost") is False

    def test_get_root_found(self):
        log = _log(_full_root("ar-01"))
        assert log.get_root("ar-01").root_id == "ar-01"

    def test_get_root_not_found(self):
        with pytest.raises(KeyError):
            NebariLog("ficus-01").get_root("ghost")

    def test_active_roots(self):
        log = _log(_full_root(), _active_root(), _abandoned_root())
        assert len(log.active_roots()) == 1

    def test_fused_roots(self):
        log = _log(_full_root(), _active_root())
        assert len(log.fused_roots()) == 1

    def test_abandoned_roots(self):
        log = _log(_active_root(), _abandoned_root())
        assert len(log.abandoned_roots()) == 1

    def test_roots_at_stage(self):
        log = _log(_active_root(), _full_root())
        at_guided = log.roots_at_stage(RootStage.GUIDED)
        assert len(at_guided) == 1

    def test_to_list_json_safe(self):
        log = _log(_full_root(), _active_root())
        json.dumps(log.to_list())

    def test_from_list_round_trip(self):
        log = _log(_full_root(), _active_root())
        restored = NebariLog.from_list("ficus-01", log.to_list())
        assert len(restored) == 2

    def test_from_list_preserves_stages(self):
        log = _log(_full_root())
        restored = NebariLog.from_list("ficus-01", log.to_list())
        assert restored.get_root("ar-01").current_stage() == RootStage.FUSED


# ── 6. days_in_stage ─────────────────────────────────────────────────────────


class TestDaysInStage:
    def test_tip_to_guided(self):
        r = _full_root()
        assert days_in_stage(r, RootStage.TIP_PROMISING) == (D2 - D1).days  # 21

    def test_guided_to_reached_soil(self):
        r = _full_root()
        assert days_in_stage(r, RootStage.GUIDED) == (D3 - D2).days  # 40

    def test_fused_returns_none(self):
        r = _full_root()
        assert days_in_stage(r, RootStage.FUSED) is None

    def test_stage_not_in_root(self):
        r = _active_root()
        assert days_in_stage(r, RootStage.REACHED_SOIL) is None

    def test_current_active_stage_returns_none(self):
        r = _active_root()  # current = GUIDED; no subsequent entry
        assert days_in_stage(r, RootStage.GUIDED) is None


# ── 7. days_in_current_stage ─────────────────────────────────────────────────


class TestDaysInCurrentStage:
    def test_active_root(self):
        # Active root: last entry at D2 (guided)
        r = _active_root()
        expected = (TODAY - D2).days
        assert days_in_current_stage(r, TODAY) == expected

    def test_empty_root(self):
        r = AerialRoot("ar-01", "ficus-01")
        assert days_in_current_stage(r, TODAY) is None


# ── 8. is_ready_to_guide ─────────────────────────────────────────────────────


class TestIsReadyToGuide:
    def test_ready_after_min_days(self):
        r = AerialRoot("ar-01", "ficus-01")
        r.add_entry(_entry(RootStage.TIP_PROMISING, D1))
        # D1 + 21 days = D2; check at D2 with min_days=14
        assert is_ready_to_guide(r, D2, min_days_observed=14) is True

    def test_not_ready_too_soon(self):
        r = AerialRoot("ar-01", "ficus-01")
        r.add_entry(_entry(RootStage.TIP_PROMISING, D1))
        # 5 days after observation
        too_soon = D1 + datetime.timedelta(days=5)
        assert is_ready_to_guide(r, too_soon, min_days_observed=14) is False

    def test_not_ready_wrong_stage(self):
        # Root is at GUIDED, not TIP_PROMISING
        assert is_ready_to_guide(_active_root(), TODAY) is False

    def test_not_ready_empty_root(self):
        r = AerialRoot("ar-01", "ficus-01")
        assert is_ready_to_guide(r, TODAY) is False

    def test_fused_root_not_ready(self):
        assert is_ready_to_guide(_full_root(), TODAY) is False


# ── 9. nebari_summary ────────────────────────────────────────────────────────


class TestNebariSummary:
    def test_empty_log(self):
        s = nebari_summary(NebariLog("ficus-01"))
        assert s["total_roots"] == 0
        assert s["fused"] == 0
        assert s["success_rate"] == 0.0

    def test_counts(self):
        log = _log(_full_root(), _active_root(), _abandoned_root())
        s = nebari_summary(log)
        assert s["total_roots"] == 3
        assert s["fused"] == 1
        assert s["active"] == 1
        assert s["abandoned"] == 1

    def test_success_rate(self):
        log = _log(_full_root(), _abandoned_root())
        s = nebari_summary(log)
        # 1 fused, 1 abandoned → 0.5
        assert abs(s["success_rate"] - 0.5) < 0.001

    def test_by_stage_keys(self):
        log = _log(_active_root())
        s = nebari_summary(log)
        for stage in RootStage:
            assert stage.value in s["by_stage"]

    def test_by_stage_counts(self):
        log = _log(_active_root(), _full_root())
        s = nebari_summary(log)
        assert s["by_stage"]["guided"] == 1
        assert s["by_stage"]["fused"] == 1

    def test_summary_keys_present(self):
        s = nebari_summary(NebariLog("ficus-01"))
        for k in ("total_roots", "active", "fused", "abandoned",
                  "by_stage", "success_rate"):
            assert k in s
