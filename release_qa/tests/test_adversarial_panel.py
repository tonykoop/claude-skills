"""Tests for release_qa.adversarial_panel — 5-persona review panel."""
from __future__ import annotations

import pytest

from release_qa.manifest import Artifact, ReleaseBundle
from release_qa.adversarial_panel import (
    AdversarialPanel,
    Critique,
    PanelReport,
    ReviewerPersona,
    DEFAULT_PERSONAS,
    PROHIBITED_KEYWORDS,
    _review_technical_auditor,
    _review_audience_fit_critic,
    _review_brand_safety,
    _review_pacing_analyst,
    _review_metadata_completeness,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _art(aid: str, atype: str, resolution: str = None,
         duration: float = None, checksum: str = "cs123", required: bool = True) -> Artifact:
    return Artifact(
        id=aid, artifact_type=atype, path=f"/{aid}.out",
        size_bytes=1000, checksum_sha256=checksum,
        resolution=resolution, duration_seconds=duration, required=required,
    )


def _good_bundle(**kwargs) -> ReleaseBundle:
    defaults = dict(
        id="good-1",
        title="My Excellent Episode Title",
        version="1.0.0",
        release_type="stable",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[
            _art("s1", "script"),
            _art("v1", "video", resolution="1920x1080", duration=600.0),
            _art("a1", "audio", duration=600.0),
            _art("c1", "caption"),
        ],
        metadata={"project": "show", "episode": 1},
        tags=["tech", "maker", "episode"],
    )
    defaults.update(kwargs)
    return ReleaseBundle(**defaults)


panel = AdversarialPanel()


# ---------------------------------------------------------------------------
# Reviewer dataclasses
# ---------------------------------------------------------------------------

def test_reviewer_persona_fields():
    p = ReviewerPersona(id="x", name="X", lens="y", severity_bias="strict")
    assert p.id == "x"
    assert p.lens == "y"


def test_critique_fields():
    c = Critique(reviewer_id="r1", lens="tech", finding="ok", severity="info", score=1.0)
    assert c.reviewer_id == "r1"
    assert c.severity == "info"
    assert c.score == 1.0


def test_panel_report_fields():
    r = PanelReport(bundle_id="b1")
    assert r.bundle_id == "b1"
    assert r.critiques == []
    assert r.recommendation == "revise"
    assert r.dissenting_reviewers == []


def test_default_personas_count():
    assert len(DEFAULT_PERSONAS) == 5


def test_default_persona_ids():
    ids = {p.id for p in DEFAULT_PERSONAS}
    assert "tech_auditor" in ids
    assert "brand_safety" in ids
    assert "pacing" in ids
    assert "metadata" in ids
    assert "audience_fit" in ids


# ---------------------------------------------------------------------------
# TechnicalAuditor persona
# ---------------------------------------------------------------------------

def test_tech_auditor_good_bundle():
    b = _good_bundle()
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "tech_auditor")
    critiques, score = _review_technical_auditor(b, persona)
    assert score > 0.8


def test_tech_auditor_missing_checksum():
    b = _good_bundle(artifacts=[
        _art("s1", "script", checksum=None),
    ])
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "tech_auditor")
    critiques, score = _review_technical_auditor(b, persona)
    assert score == 0.0
    severities = [c.severity for c in critiques]
    assert "blocker" in severities


def test_tech_auditor_low_resolution_video():
    b = _good_bundle(artifacts=[
        _art("v1", "video", resolution="640x480", checksum="cs"),
    ])
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "tech_auditor")
    critiques, score = _review_technical_auditor(b, persona)
    assert score <= 0.5


def test_tech_auditor_no_audio_warning():
    b = _good_bundle(artifacts=[_art("s1", "script")])
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "tech_auditor")
    critiques, score = _review_technical_auditor(b, persona)
    findings = " ".join(c.finding for c in critiques)
    assert "audio" in findings.lower()


# ---------------------------------------------------------------------------
# AudienceFitCritic persona
# ---------------------------------------------------------------------------

def test_audience_fit_good_bundle():
    b = _good_bundle()
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "audience_fit")
    critiques, score = _review_audience_fit_critic(b, persona)
    assert score >= 0.6


def test_audience_fit_short_title():
    b = _good_bundle(title="Hi")
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "audience_fit")
    critiques, score = _review_audience_fit_critic(b, persona)
    assert score < 1.0


def test_audience_fit_few_tags():
    b = _good_bundle(tags=["one"])
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "audience_fit")
    critiques, score = _review_audience_fit_critic(b, persona)
    assert score < 1.0


def test_audience_fit_no_caption():
    b = _good_bundle(artifacts=[_art("s1", "script"), _art("v1", "video", resolution="1920x1080")])
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "audience_fit")
    critiques, score = _review_audience_fit_critic(b, persona)
    assert score <= 0.7


# ---------------------------------------------------------------------------
# BrandSafetyReviewer persona
# ---------------------------------------------------------------------------

def test_brand_safety_good_bundle():
    b = _good_bundle()
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "brand_safety")
    critiques, score = _review_brand_safety(b, persona)
    assert score == 1.0


def test_brand_safety_prohibited_tag():
    b = _good_bundle(tags=["tech", "nsfw"])
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "brand_safety")
    critiques, score = _review_brand_safety(b, persona)
    assert score == 0.0
    severities = [c.severity for c in critiques]
    assert "blocker" in severities


def test_brand_safety_prohibited_title():
    b = _good_bundle(title="Explicit Content Guide")
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "brand_safety")
    critiques, score = _review_brand_safety(b, persona)
    assert score == 0.0


def test_brand_safety_all_prohibited_keywords():
    for kw in PROHIBITED_KEYWORDS:
        b = _good_bundle(tags=[kw])
        persona = next(p for p in DEFAULT_PERSONAS if p.id == "brand_safety")
        critiques, score = _review_brand_safety(b, persona)
        assert score == 0.0, f"Expected 0 score for prohibited keyword '{kw}'"


# ---------------------------------------------------------------------------
# PacingAnalyst persona
# ---------------------------------------------------------------------------

def test_pacing_good_duration():
    b = _good_bundle()
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "pacing")
    critiques, score = _review_pacing_analyst(b, persona)
    assert score >= 0.7


def test_pacing_no_video():
    b = _good_bundle(artifacts=[_art("s1", "script")])
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "pacing")
    critiques, score = _review_pacing_analyst(b, persona)
    assert score == 1.0
    assert any("No video" in c.finding for c in critiques)


def test_pacing_too_long():
    b = _good_bundle(artifacts=[
        _art("v1", "video", resolution="1920x1080", duration=4000.0),
    ])
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "pacing")
    critiques, score = _review_pacing_analyst(b, persona)
    assert score <= 0.7


def test_pacing_too_short():
    b = _good_bundle(artifacts=[
        _art("v1", "video", resolution="1920x1080", duration=30.0),
    ])
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "pacing")
    critiques, score = _review_pacing_analyst(b, persona)
    assert score <= 0.6


def test_pacing_no_duration():
    b = _good_bundle(artifacts=[
        _art("v1", "video", resolution="1920x1080", duration=None),
    ])
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "pacing")
    critiques, score = _review_pacing_analyst(b, persona)
    assert score <= 0.7


# ---------------------------------------------------------------------------
# MetadataCompleteness persona
# ---------------------------------------------------------------------------

def test_metadata_good_bundle():
    b = _good_bundle()
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "metadata")
    critiques, score = _review_metadata_completeness(b, persona)
    assert score >= 0.8


def test_metadata_empty_tags():
    b = _good_bundle(tags=[])
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "metadata")
    critiques, score = _review_metadata_completeness(b, persona)
    assert score < 1.0


def test_metadata_empty_metadata():
    b = _good_bundle(metadata={})
    persona = next(p for p in DEFAULT_PERSONAS if p.id == "metadata")
    critiques, score = _review_metadata_completeness(b, persona)
    assert score < 1.0


# ---------------------------------------------------------------------------
# AdversarialPanel.review — full panel
# ---------------------------------------------------------------------------

def test_panel_review_good_bundle_approve():
    b = _good_bundle()
    report = panel.review(b)
    assert isinstance(report, PanelReport)
    assert report.bundle_id == "good-1"
    assert report.recommendation in ("approve", "revise")
    assert 0.0 <= report.consensus_score <= 1.0


def test_panel_review_prohibited_tags_low_score():
    b = _good_bundle(tags=["nsfw", "explicit"])
    report = panel.review(b)
    assert report.consensus_score < 0.8


def test_panel_review_returns_critiques():
    b = _good_bundle()
    report = panel.review(b)
    assert len(report.critiques) > 0
    for c in report.critiques:
        assert isinstance(c, Critique)
        assert c.severity in ("info", "warning", "error", "blocker")


def test_panel_review_reject_on_very_bad_bundle():
    b = ReleaseBundle(
        id="bad",
        title="Hi",  # too short
        version="1.0.0",
        release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_art("s1", "script", checksum=None)],  # missing checksum
        metadata={},
        tags=["nsfw"],  # prohibited
    )
    report = panel.review(b)
    assert report.consensus_score < 0.5
    assert report.recommendation in ("reject", "revise")


def test_panel_review_consensus_score_in_range():
    for _ in range(3):
        b = _good_bundle()
        report = panel.review(b)
        assert 0.0 <= report.consensus_score <= 1.0


def test_panel_custom_personas():
    custom = [ReviewerPersona(id="brand_safety", name="Custom BS", lens="brand_safety", severity_bias="strict")]
    custom_panel = AdversarialPanel(personas=custom)
    b = _good_bundle(tags=["nsfw"])
    report = custom_panel.review(b)
    assert report.consensus_score == 0.0
