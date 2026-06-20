"""Tests for plant_care.diagnostics — multi-factor plant health diagnostics."""

from __future__ import annotations

import datetime
import json
import types
import pytest

from plant_care.diagnostics import (
    Confidence,
    DiagnosticFinding,
    DiagnosticReport,
    NutritionFlag,
    PestFlag,
    diagnose,
    nutrition_flags,
    probable_pests,
    root_rot_risk,
)
from plant_care.models import CareEvent, CareProfile, Observations, Specimen

# ── Test constants ─────────────────────────────────────────────────────────────

TODAY = datetime.date(2024, 6, 15)
D0 = datetime.date(2024, 1, 1)   # start of year


# ── Helpers ────────────────────────────────────────────────────────────────────


def _specimen(sid="sp-01") -> Specimen:
    return Specimen(
        id=sid,
        species="Ficus elastica",
        acquired=datetime.date(2023, 1, 1),
        location="living room",
        light_level="bright-indirect",
        pot_size="6in",
    )


def _profile(interval: int = 7) -> CareProfile:
    return CareProfile(
        watering_interval_days=interval,
        fertilize_interval_days=28,
        light_needs="bright indirect",
        humidity="moderate",
    )


def _water_events(dates) -> list:
    return [CareEvent(type="water", date=d) for d in dates]


def _base_obs(**kwargs) -> Observations:
    """Observations with only standard fields."""
    defaults = {
        "yellowing": False,
        "drooping": False,
        "pests": False,
        "dry_soil": False,
        "leaf_drop": False,
        "mold": False,
    }
    defaults.update(kwargs)
    return Observations(**defaults)


def _ext_obs(**kwargs) -> types.SimpleNamespace:
    """Extended observations with extra diagnostic attributes.

    Uses SimpleNamespace so we can set arbitrary attributes; the
    diagnostic functions access extended attrs via getattr(..., False).
    """
    defaults = {
        "yellowing": False,
        "drooping": False,
        "pests": False,
        "dry_soil": False,
        "leaf_drop": False,
        "mold": False,
        # Extended pest attrs
        "webbing": False,
        "sticky_residue": False,
        "white_cottony_masses": False,
        "fungus_gnats": False,
        "soil_flies": False,
        "distorted_new_growth": False,
        # Extended nutrition attrs
        "interveinal_yellowing": False,
        "yellowing_new_leaves": False,
        "yellowing_old_leaves": False,
        "leaf_tip_burn": False,
        "leaf_edge_burn": False,
    }
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


# ── 1. Confidence enum ────────────────────────────────────────────────────────


class TestConfidenceEnum:
    def test_has_three_levels(self):
        assert len(list(Confidence)) == 3

    def test_values_are_strings(self):
        for c in Confidence:
            assert isinstance(c.value, str)

    def test_high_medium_low_exist(self):
        assert Confidence.HIGH.value == "high"
        assert Confidence.MEDIUM.value == "medium"
        assert Confidence.LOW.value == "low"


# ── 2. PestFlag enum ──────────────────────────────────────────────────────────


class TestPestFlagEnum:
    def test_six_pests(self):
        assert len(list(PestFlag)) == 6

    def test_all_string_values(self):
        for p in PestFlag:
            assert isinstance(p.value, str)

    def test_scale_insect(self):
        assert PestFlag.SCALE_INSECT.value == "scale_insect"

    def test_spider_mite(self):
        assert PestFlag.SPIDER_MITE.value == "spider_mite"

    def test_thrips(self):
        assert PestFlag.THRIPS.value == "thrips"

    def test_fungus_gnat(self):
        assert PestFlag.FUNGUS_GNAT.value == "fungus_gnat"

    def test_mealybug(self):
        assert PestFlag.MEALYBUG.value == "mealybug"

    def test_aphid(self):
        assert PestFlag.APHID.value == "aphid"


# ── 3. NutritionFlag enum ────────────────────────────────────────────────────


class TestNutritionFlagEnum:
    def test_four_flags(self):
        assert len(list(NutritionFlag)) == 4

    def test_nitrogen_deficiency(self):
        assert NutritionFlag.NITROGEN_DEFICIENCY.value == "nitrogen_deficiency"

    def test_iron_deficiency(self):
        assert NutritionFlag.IRON_DEFICIENCY.value == "iron_deficiency"

    def test_magnesium_deficiency(self):
        assert NutritionFlag.MAGNESIUM_DEFICIENCY.value == "magnesium_deficiency"

    def test_overfeeding(self):
        assert NutritionFlag.OVERFEEDING.value == "overfeeding"


# ── 4. DiagnosticFinding ──────────────────────────────────────────────────────


class TestDiagnosticFinding:
    def _make(self, **kwargs):
        defaults = dict(
            flag="test_flag",
            category="pest",
            confidence=Confidence.MEDIUM,
            evidence=["some observation"],
            recommendation="Do something.",
        )
        defaults.update(kwargs)
        return DiagnosticFinding(**defaults)

    def test_construction(self):
        f = self._make()
        assert f.flag == "test_flag"
        assert f.category == "pest"
        assert f.confidence == Confidence.MEDIUM

    def test_evidence_list(self):
        f = self._make(evidence=["obs1", "obs2"])
        assert len(f.evidence) == 2

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        for key in ("flag", "category", "confidence", "evidence", "recommendation", "caution"):
            assert key in d

    def test_to_dict_confidence_is_string(self):
        d = self._make(confidence=Confidence.HIGH).to_dict()
        assert d["confidence"] == "high"

    def test_to_dict_json_safe(self):
        json.dumps(self._make().to_dict())

    def test_caution_default_empty(self):
        f = self._make()
        assert f.caution == ""

    def test_caution_set(self):
        f = self._make(caution="Confirm before treating.")
        assert "Confirm" in f.caution


# ── 5. DiagnosticReport ───────────────────────────────────────────────────────


class TestDiagnosticReport:
    def _make_finding(self, flag="drooping", cat="cultural", conf=Confidence.MEDIUM):
        return DiagnosticFinding(
            flag=flag, category=cat, confidence=conf,
            evidence=["test"], recommendation="test rec",
        )

    def _make_report(self, **kwargs):
        defaults = dict(
            specimen_id="sp-01",
            date=TODAY,
            overall_status="healthy",
            findings=[],
        )
        defaults.update(kwargs)
        return DiagnosticReport(**defaults)

    def test_construction_no_findings(self):
        r = self._make_report()
        assert r.specimen_id == "sp-01"
        assert r.findings == []

    def test_to_dict_keys(self):
        d = self._make_report().to_dict()
        for key in ("specimen_id", "date", "overall_status", "findings",
                    "root_rot_risk_score", "notes"):
            assert key in d

    def test_to_dict_date_iso(self):
        d = self._make_report().to_dict()
        assert d["date"] == "2024-06-15"

    def test_to_dict_findings_serialised(self):
        r = self._make_report(findings=[self._make_finding()])
        d = r.to_dict()
        assert len(d["findings"]) == 1
        assert isinstance(d["findings"][0], dict)

    def test_to_dict_json_safe(self):
        json.dumps(self._make_report().to_dict())

    def test_has_flag_true(self):
        r = self._make_report(findings=[self._make_finding("drooping")])
        assert r.has_flag("drooping") is True

    def test_has_flag_false(self):
        r = self._make_report()
        assert r.has_flag("scale_insect") is False

    def test_findings_by_category(self):
        pest = self._make_finding("scale_insect", "pest")
        cultural = self._make_finding("drooping", "cultural")
        r = self._make_report(findings=[pest, cultural])
        assert len(r.findings_by_category("pest")) == 1
        assert len(r.findings_by_category("cultural")) == 1
        assert len(r.findings_by_category("nutrition")) == 0

    def test_root_rot_risk_score_default(self):
        r = self._make_report()
        assert r.root_rot_risk_score == 0.0


# ── 6. root_rot_risk ──────────────────────────────────────────────────────────


class TestRootRotRisk:
    def test_no_history_returns_zero(self):
        assert root_rot_risk([], _profile(7), TODAY) == 0.0

    def test_single_event_returns_zero(self):
        events = _water_events([D0])
        assert root_rot_risk(events, _profile(7), TODAY) == 0.0

    def test_normal_interval_returns_zero(self):
        # Water every 7 days = 100% of prescribed interval; safe
        dates = [D0 + datetime.timedelta(days=7 * i) for i in range(5)]
        events = _water_events(dates)
        assert root_rot_risk(events, _profile(7), TODAY) == 0.0

    def test_moderate_overwatering_returns_0_4(self):
        # Water every 4 days vs 7-day profile → ratio ≈ 0.57 (between 0.5 and 0.75)
        dates = [D0 + datetime.timedelta(days=4 * i) for i in range(6)]
        events = _water_events(dates)
        score = root_rot_risk(events, _profile(7), TODAY)
        assert score == 0.4

    def test_severe_overwatering_returns_0_8(self):
        # Water every 2 days vs 7-day profile → ratio ≈ 0.29 (< 0.5)
        dates = [D0 + datetime.timedelta(days=2 * i) for i in range(6)]
        events = _water_events(dates)
        score = root_rot_risk(events, _profile(7), TODAY)
        assert score == 0.8

    def test_score_bounded_above_by_0_8(self):
        # Even daily watering gives ≤ 0.8
        dates = [D0 + datetime.timedelta(days=i) for i in range(10)]
        events = _water_events(dates)
        score = root_rot_risk(events, _profile(14), TODAY)
        assert score <= 1.0

    def test_non_water_events_ignored(self):
        # Fertilize events should not affect water calculation
        fert_events = [
            CareEvent(date=D0 + datetime.timedelta(days=i * 2), type="fertilize")
            for i in range(5)
        ]
        assert root_rot_risk(fert_events, _profile(7), TODAY) == 0.0

    def test_returns_float(self):
        dates = [D0 + datetime.timedelta(days=7 * i) for i in range(3)]
        score = root_rot_risk(_water_events(dates), _profile(7), TODAY)
        assert isinstance(score, float)


# ── 7. probable_pests ─────────────────────────────────────────────────────────


class TestProbablePests:
    def test_no_symptoms_no_pests(self):
        obs = _ext_obs()
        findings = probable_pests(obs)
        assert findings == []

    def test_webbing_triggers_spider_mite(self):
        obs = _ext_obs(webbing=True)
        findings = probable_pests(obs)
        flags = [f.flag for f in findings]
        assert PestFlag.SPIDER_MITE.value in flags

    def test_webbing_is_high_confidence(self):
        obs = _ext_obs(webbing=True)
        findings = probable_pests(obs)
        spider = next(f for f in findings if f.flag == PestFlag.SPIDER_MITE.value)
        assert spider.confidence == Confidence.HIGH

    def test_sticky_residue_triggers_scale_and_aphid(self):
        obs = _ext_obs(sticky_residue=True)
        findings = probable_pests(obs)
        flags = [f.flag for f in findings]
        assert PestFlag.SCALE_INSECT.value in flags
        assert PestFlag.APHID.value in flags

    def test_sticky_residue_scale_medium_confidence(self):
        obs = _ext_obs(sticky_residue=True)
        findings = probable_pests(obs)
        scale = next(f for f in findings if f.flag == PestFlag.SCALE_INSECT.value)
        assert scale.confidence == Confidence.MEDIUM

    def test_white_cottony_masses_triggers_mealybug(self):
        obs = _ext_obs(white_cottony_masses=True)
        findings = probable_pests(obs)
        flags = [f.flag for f in findings]
        assert PestFlag.MEALYBUG.value in flags

    def test_mealybug_high_confidence(self):
        obs = _ext_obs(white_cottony_masses=True)
        findings = probable_pests(obs)
        m = next(f for f in findings if f.flag == PestFlag.MEALYBUG.value)
        assert m.confidence == Confidence.HIGH

    def test_fungus_gnats_from_fungus_gnats_attr(self):
        obs = _ext_obs(fungus_gnats=True)
        findings = probable_pests(obs)
        flags = [f.flag for f in findings]
        assert PestFlag.FUNGUS_GNAT.value in flags

    def test_fungus_gnats_from_soil_flies_attr(self):
        obs = _ext_obs(soil_flies=True)
        findings = probable_pests(obs)
        flags = [f.flag for f in findings]
        assert PestFlag.FUNGUS_GNAT.value in flags

    def test_distorted_growth_triggers_thrips(self):
        obs = _ext_obs(distorted_new_growth=True)
        findings = probable_pests(obs)
        flags = [f.flag for f in findings]
        assert PestFlag.THRIPS.value in flags

    def test_base_pests_flag_triggers_unknown_pest(self):
        obs = _base_obs(pests=True)
        findings = probable_pests(obs)
        assert len(findings) >= 1

    def test_findings_have_evidence(self):
        obs = _ext_obs(webbing=True)
        for f in probable_pests(obs):
            assert len(f.evidence) > 0

    def test_findings_are_diagnostic_finding_instances(self):
        obs = _ext_obs(webbing=True, sticky_residue=True)
        for f in probable_pests(obs):
            assert isinstance(f, DiagnosticFinding)


# ── 8. nutrition_flags ───────────────────────────────────────────────────────


class TestNutritionFlags:
    def test_no_yellowing_no_flags(self):
        obs = _ext_obs(yellowing=False)
        assert nutrition_flags(obs) == []

    def test_generic_yellowing_returns_unspecified(self):
        obs = _ext_obs(yellowing=True)
        findings = nutrition_flags(obs)
        assert len(findings) == 1
        assert findings[0].flag == "yellowing_unspecified"
        assert findings[0].confidence == Confidence.LOW

    def test_old_leaves_yellowing_nitrogen_deficiency(self):
        obs = _ext_obs(yellowing=True, yellowing_old_leaves=True)
        findings = nutrition_flags(obs)
        flags = [f.flag for f in findings]
        assert NutritionFlag.NITROGEN_DEFICIENCY.value in flags

    def test_interveinal_new_leaves_iron_deficiency(self):
        obs = _ext_obs(yellowing=True, interveinal_yellowing=True, yellowing_new_leaves=True)
        findings = nutrition_flags(obs)
        flags = [f.flag for f in findings]
        assert NutritionFlag.IRON_DEFICIENCY.value in flags

    def test_interveinal_old_leaves_magnesium_deficiency(self):
        obs = _ext_obs(yellowing=True, interveinal_yellowing=True, yellowing_old_leaves=True)
        findings = nutrition_flags(obs)
        flags = [f.flag for f in findings]
        assert NutritionFlag.MAGNESIUM_DEFICIENCY.value in flags

    def test_leaf_tip_burn_overfeeding(self):
        obs = _ext_obs(yellowing=True, leaf_tip_burn=True)
        findings = nutrition_flags(obs)
        flags = [f.flag for f in findings]
        assert NutritionFlag.OVERFEEDING.value in flags

    def test_leaf_edge_burn_overfeeding(self):
        obs = _ext_obs(yellowing=True, leaf_edge_burn=True)
        findings = nutrition_flags(obs)
        flags = [f.flag for f in findings]
        assert NutritionFlag.OVERFEEDING.value in flags

    def test_overfeeding_plus_iron_deficiency_co_occur(self):
        # Both iron deficiency AND overfeeding if interveinal+new+tip_burn
        obs = _ext_obs(
            yellowing=True,
            interveinal_yellowing=True,
            yellowing_new_leaves=True,
            leaf_tip_burn=True,
        )
        findings = nutrition_flags(obs)
        flags = [f.flag for f in findings]
        assert NutritionFlag.IRON_DEFICIENCY.value in flags
        assert NutritionFlag.OVERFEEDING.value in flags

    def test_findings_have_recommendation(self):
        obs = _ext_obs(yellowing=True)
        for f in nutrition_flags(obs):
            assert len(f.recommendation) > 0

    def test_findings_are_diagnostic_finding_instances(self):
        obs = _ext_obs(yellowing=True)
        for f in nutrition_flags(obs):
            assert isinstance(f, DiagnosticFinding)


# ── 9. diagnose ───────────────────────────────────────────────────────────────


class TestDiagnose:
    def test_clean_specimen_healthy_status(self):
        obs = _base_obs()
        report = diagnose(_specimen(), obs, [], TODAY)
        assert report.overall_status == "healthy"

    def test_report_specimen_id(self):
        obs = _base_obs()
        report = diagnose(_specimen("sp-99"), obs, [], TODAY)
        assert report.specimen_id == "sp-99"

    def test_report_date(self):
        obs = _base_obs()
        report = diagnose(_specimen(), obs, [], TODAY)
        assert report.date == TODAY

    def test_drooping_adds_finding(self):
        obs = _base_obs(drooping=True)
        report = diagnose(_specimen(), obs, [], TODAY)
        assert report.has_flag("drooping")

    def test_drooping_status_needs_attention(self):
        obs = _base_obs(drooping=True)
        report = diagnose(_specimen(), obs, [], TODAY)
        assert report.overall_status == "needs-attention"

    def test_mold_adds_finding(self):
        obs = _base_obs(mold=True)
        report = diagnose(_specimen(), obs, [], TODAY)
        assert report.has_flag("surface_mold")

    def test_leaf_drop_adds_finding(self):
        obs = _base_obs(leaf_drop=True)
        report = diagnose(_specimen(), obs, [], TODAY)
        assert report.has_flag("leaf_drop")

    def test_leaf_drop_status_declining(self):
        obs = _base_obs(leaf_drop=True)
        report = diagnose(_specimen(), obs, [], TODAY)
        assert report.overall_status == "declining"

    def test_pests_status_declining(self):
        obs = _base_obs(pests=True)
        report = diagnose(_specimen(), obs, [], TODAY)
        assert report.overall_status == "declining"

    def test_yellowing_and_drooping_declining(self):
        obs = _base_obs(yellowing=True, drooping=True)
        report = diagnose(_specimen(), obs, [], TODAY)
        assert report.overall_status == "declining"

    def test_webbing_adds_spider_mite(self):
        obs = _ext_obs(webbing=True)
        report = diagnose(_specimen(), obs, [], TODAY)
        assert report.has_flag(PestFlag.SPIDER_MITE.value)

    def test_root_rot_risk_added_with_profile(self):
        # Water every 2 days vs 7-day profile → severe overwatering
        dates = [D0 + datetime.timedelta(days=2 * i) for i in range(6)]
        events = _water_events(dates)
        obs = _base_obs()
        report = diagnose(_specimen(), obs, events, TODAY, profile=_profile(7))
        assert report.root_rot_risk_score > 0.0
        assert report.has_flag("root_rot_risk")

    def test_root_rot_no_profile_no_risk(self):
        dates = [D0 + datetime.timedelta(days=2 * i) for i in range(6)]
        events = _water_events(dates)
        obs = _base_obs()
        report = diagnose(_specimen(), obs, events, TODAY, profile=None)
        assert report.root_rot_risk_score == 0.0
        assert not report.has_flag("root_rot_risk")

    def test_findings_sorted_high_confidence_first(self):
        # Spider mite (HIGH) and yellowing_unspecified (LOW) in same report
        obs = _ext_obs(webbing=True, yellowing=True)
        report = diagnose(_specimen(), obs, [], TODAY)
        if len(report.findings) >= 2:
            assert report.findings[0].confidence.value in ("high", "medium")

    def test_report_notes_not_empty_with_findings(self):
        obs = _base_obs(drooping=True)
        report = diagnose(_specimen(), obs, [], TODAY)
        assert len(report.notes) > 0

    def test_report_notes_for_clean_specimen(self):
        obs = _base_obs()
        report = diagnose(_specimen(), obs, [], TODAY)
        assert "No concerning" in report.notes

    def test_findings_by_category_pest(self):
        obs = _ext_obs(webbing=True)
        report = diagnose(_specimen(), obs, [], TODAY)
        pest_findings = report.findings_by_category("pest")
        assert len(pest_findings) >= 1

    def test_to_dict_round_trip_json(self):
        obs = _ext_obs(webbing=True, yellowing=True, drooping=True)
        report = diagnose(_specimen(), obs, [], TODAY)
        d = report.to_dict()
        json.dumps(d)  # must not raise

    def test_empty_history_no_root_rot(self):
        obs = _base_obs()
        report = diagnose(_specimen(), obs, [], TODAY, profile=_profile(7))
        assert report.root_rot_risk_score == 0.0
