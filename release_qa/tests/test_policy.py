"""Tests for release_qa.policy — PolicyEngine, Policy, PolicyViolation."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from release_qa.manifest import Artifact, ReleaseBundle
from release_qa.policy import Policy, PolicyEngine, PolicyViolation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _art(aid: str, atype: str, size: int = 1000, resolution: str = None,
         checksum: str = "cs") -> Artifact:
    return Artifact(
        id=aid, artifact_type=atype, path=f"/{aid}.out",
        size_bytes=size, checksum_sha256=checksum, resolution=resolution,
    )


def _stable_bundle(**kwargs) -> ReleaseBundle:
    defaults = dict(
        id="sb1",
        title="My Stable Release",
        version="1.0.0",
        release_type="stable",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[
            _art("s1", "script"),
            _art("v1", "video", resolution="1920x1080"),
            _art("a1", "audio"),
            _art("c1", "caption"),
        ],
        metadata={"project": "myshow", "episode": 1},
        tags=["tech", "maker", "crafts"],
    )
    defaults.update(kwargs)
    return ReleaseBundle(**defaults)


def _alpha_bundle(**kwargs) -> ReleaseBundle:
    defaults = dict(
        id="ab1",
        title="Alpha Release",
        version="0.1.0",
        release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_art("s1", "script")],
        metadata={"project": "myshow", "episode": 1},
        tags=["alpha"],
    )
    defaults.update(kwargs)
    return ReleaseBundle(**defaults)


def _make_engine() -> PolicyEngine:
    engine = PolicyEngine()
    engine.load_policies()
    return engine


# ---------------------------------------------------------------------------
# Policy / PolicyViolation dataclasses
# ---------------------------------------------------------------------------

def test_policy_fields():
    p = Policy(id="p1", name="Test Policy", applies_to=["stable"], severity="error", rule={"type": "artifact_required"})
    assert p.id == "p1"
    assert p.severity == "error"
    assert "stable" in p.applies_to


def test_policy_violation_fields():
    v = PolicyViolation(policy_id="p1", policy_name="Test", severity="error", detail="Missing thing.")
    assert v.policy_id == "p1"
    assert v.severity == "error"
    assert "Missing" in v.detail


# ---------------------------------------------------------------------------
# PolicyEngine — load_policies
# ---------------------------------------------------------------------------

def test_load_policies_loads_8_policies():
    engine = _make_engine()
    assert len(engine.policies) == 8


def test_load_policies_ids():
    engine = _make_engine()
    ids = {p.id for p in engine.policies}
    expected = {
        "require_captions_stable",
        "min_video_resolution",
        "prohibited_tags",
        "version_format",
        "required_metadata_fields",
        "artifact_size_limit_video",
        "min_artifact_count",
        "require_audio_rc_stable",
    }
    assert ids == expected


def test_load_policies_severities():
    engine = _make_engine()
    severity_map = {p.id: p.severity for p in engine.policies}
    assert severity_map["prohibited_tags"] == "blocker"
    assert severity_map["require_captions_stable"] == "error"
    assert severity_map["min_video_resolution"] == "warning"


def test_load_empty_directory(tmp_path):
    engine = PolicyEngine(policy_dir=str(tmp_path))
    engine.load_policies()
    assert engine.policies == []


def test_load_nonexistent_directory():
    engine = PolicyEngine(policy_dir="/nonexistent/path/policies")
    engine.load_policies()
    assert engine.policies == []


# ---------------------------------------------------------------------------
# PolicyEngine — applicable_policies
# ---------------------------------------------------------------------------

def test_applicable_policies_stable():
    engine = _make_engine()
    policies = engine.applicable_policies("stable")
    ids = {p.id for p in policies}
    assert "require_captions_stable" in ids
    assert "require_audio_rc_stable" in ids


def test_applicable_policies_alpha():
    engine = _make_engine()
    policies = engine.applicable_policies("alpha")
    ids = {p.id for p in policies}
    # Caption requirement is stable only
    assert "require_captions_stable" not in ids
    # Audio requirement is rc/stable only
    assert "require_audio_rc_stable" not in ids
    # Version format applies to all
    assert "version_format" in ids


def test_applicable_policies_rc():
    engine = _make_engine()
    policies = engine.applicable_policies("rc")
    ids = {p.id for p in policies}
    assert "require_audio_rc_stable" in ids
    assert "require_captions_stable" not in ids


# ---------------------------------------------------------------------------
# PolicyEngine — evaluate (stable good bundle passes)
# ---------------------------------------------------------------------------

def test_evaluate_good_stable_no_violations():
    engine = _make_engine()
    bundle = _stable_bundle()
    violations = engine.evaluate(bundle)
    assert violations == []


def test_evaluate_good_alpha_no_violations():
    engine = _make_engine()
    bundle = _alpha_bundle()
    violations = engine.evaluate(bundle)
    assert violations == []


# ---------------------------------------------------------------------------
# Rule: artifact_required
# ---------------------------------------------------------------------------

def test_evaluate_stable_missing_caption():
    engine = _make_engine()
    bundle = _stable_bundle(artifacts=[
        _art("s1", "script"), _art("v1", "video", resolution="1920x1080"), _art("a1", "audio"),
    ])
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "require_captions_stable" in violation_ids


def test_evaluate_rc_missing_audio():
    engine = _make_engine()
    bundle = ReleaseBundle(
        id="rc1", title="RC", version="1.0.0", release_type="rc",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_art("s1", "script"), _art("v1", "video", resolution="1920x1080")],
        metadata={"project": "x", "episode": 1},
        tags=["rc"],
    )
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "require_audio_rc_stable" in violation_ids


# ---------------------------------------------------------------------------
# Rule: min_resolution
# ---------------------------------------------------------------------------

def test_evaluate_low_resolution_video():
    engine = _make_engine()
    bundle = _stable_bundle(artifacts=[
        _art("s1", "script"),
        _art("v1", "video", resolution="640x480"),
        _art("a1", "audio"),
        _art("c1", "caption"),
    ])
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "min_video_resolution" in violation_ids


def test_evaluate_720p_video_passes():
    engine = _make_engine()
    bundle = _stable_bundle(artifacts=[
        _art("s1", "script"),
        _art("v1", "video", resolution="1280x720"),
        _art("a1", "audio"),
        _art("c1", "caption"),
    ])
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "min_video_resolution" not in violation_ids


# ---------------------------------------------------------------------------
# Rule: prohibited_tags
# ---------------------------------------------------------------------------

def test_evaluate_prohibited_tag():
    engine = _make_engine()
    bundle = _stable_bundle(tags=["tech", "nsfw"])
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "prohibited_tags" in violation_ids


def test_evaluate_no_prohibited_tags():
    engine = _make_engine()
    bundle = _stable_bundle(tags=["tech", "maker"])
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "prohibited_tags" not in violation_ids


# ---------------------------------------------------------------------------
# Rule: version_format
# ---------------------------------------------------------------------------

def test_evaluate_invalid_version():
    engine = _make_engine()
    bundle = _stable_bundle(version="not-valid")
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "version_format" in violation_ids


def test_evaluate_valid_version_passes():
    engine = _make_engine()
    bundle = _alpha_bundle(version="1.2.3-rc1")
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "version_format" not in violation_ids


# ---------------------------------------------------------------------------
# Rule: required_metadata_fields
# ---------------------------------------------------------------------------

def test_evaluate_missing_metadata_fields():
    engine = _make_engine()
    bundle = _stable_bundle(metadata={"project": "x"})  # missing "episode"
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "required_metadata_fields" in violation_ids


def test_evaluate_metadata_present_passes():
    engine = _make_engine()
    bundle = _stable_bundle(metadata={"project": "myshow", "episode": 5})
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "required_metadata_fields" not in violation_ids


# ---------------------------------------------------------------------------
# Rule: artifact_size_limit
# ---------------------------------------------------------------------------

def test_evaluate_video_oversized():
    engine = _make_engine()
    huge_video = _art("v1", "video", size=20_000_000_000, resolution="1920x1080")  # 20 GB
    bundle = _stable_bundle(artifacts=[
        _art("s1", "script"), huge_video, _art("a1", "audio"), _art("c1", "caption"),
    ])
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "artifact_size_limit_video" in violation_ids


def test_evaluate_video_within_size_limit():
    engine = _make_engine()
    bundle = _stable_bundle()  # default 1000 bytes
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "artifact_size_limit_video" not in violation_ids


# ---------------------------------------------------------------------------
# Rule: min_artifact_count
# ---------------------------------------------------------------------------

def test_evaluate_no_artifacts():
    engine = _make_engine()
    bundle = _alpha_bundle(artifacts=[])
    violations = engine.evaluate(bundle)
    violation_ids = [v.policy_id for v in violations]
    assert "min_artifact_count" in violation_ids


# ---------------------------------------------------------------------------
# is_release_blocked
# ---------------------------------------------------------------------------

def test_is_release_blocked_true_on_prohibited_tag():
    engine = _make_engine()
    bundle = _stable_bundle(tags=["nsfw"])  # blocker severity
    assert engine.is_release_blocked(bundle) is True


def test_is_release_blocked_true_on_missing_caption():
    engine = _make_engine()
    bundle = _stable_bundle(artifacts=[
        _art("s1", "script"), _art("v1", "video", resolution="1920x1080"), _art("a1", "audio"),
    ])
    assert engine.is_release_blocked(bundle) is True


def test_is_release_blocked_false_on_good_bundle():
    engine = _make_engine()
    bundle = _stable_bundle()
    assert engine.is_release_blocked(bundle) is False


def test_is_release_blocked_warning_not_blocking():
    engine = _make_engine()
    # Only violation: min_video_resolution (warning severity) — should not block
    bundle = _stable_bundle(artifacts=[
        _art("s1", "script"),
        _art("v1", "video", resolution="640x480"),  # low res → warning
        _art("a1", "audio"),
        _art("c1", "caption"),
    ])
    violations = engine.evaluate(bundle)
    warning_violations = [v for v in violations if v.severity == "warning"]
    assert len(warning_violations) > 0
    # "warning" is not in blocking severities
    assert engine.is_release_blocked(bundle) is False
