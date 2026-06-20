"""Tests for release_qa.workflow — WorkflowEngine, gates, state machine."""
from __future__ import annotations

import pytest

from release_qa.manifest import Artifact, ReleaseBundle
from release_qa.workflow import (
    ReleaseState,
    GateResult,
    StageResult,
    WorkflowEngine,
    _gate_manifest_complete,
    _gate_all_required_artifacts,
    _gate_version_valid,
    _gate_video_resolution,
    _gate_audio_present,
    _gate_captions_for_stable,
    _gate_no_duplicate_artifact_ids,
    _gate_human_approval,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_artifact(aid: str, atype: str, resolution: str = None, checksum: str = "cs") -> Artifact:
    return Artifact(
        id=aid,
        artifact_type=atype,
        path=f"/{aid}.out",
        size_bytes=1000,
        checksum_sha256=checksum,
        resolution=resolution,
    )


def _full_stable_bundle(panel_score: float = 0.9, with_approval: bool = True) -> ReleaseBundle:
    meta = {"project": "show", "episode": 1, "panel_score": panel_score}
    if with_approval:
        meta["human_approval_token"] = "tok-abc123"
    return ReleaseBundle(
        id="full-stable",
        title="Full Stable",
        version="1.0.0",
        release_type="stable",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[
            _make_artifact("s1", "script"),
            _make_artifact("v1", "video", resolution="1920x1080"),
            _make_artifact("a1", "audio"),
            _make_artifact("c1", "caption"),
        ],
        metadata=meta,
        tags=["stable"],
    )


def _alpha_bundle(panel_score: float = 0.9, with_approval: bool = True) -> ReleaseBundle:
    meta = {"panel_score": panel_score}
    if with_approval:
        meta["human_approval_token"] = "tok-alpha"
    return ReleaseBundle(
        id="alpha-1",
        title="Alpha Bundle",
        version="0.1.0",
        release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_make_artifact("s1", "script")],
        metadata=meta,
        tags=["alpha"],
    )


engine = WorkflowEngine()


# ---------------------------------------------------------------------------
# ReleaseState enum
# ---------------------------------------------------------------------------

def test_release_states_exist():
    assert ReleaseState.DRAFT.value == "draft"
    assert ReleaseState.BUILD.value == "build"
    assert ReleaseState.QA.value == "qa"
    assert ReleaseState.REVIEW.value == "review"
    assert ReleaseState.APPROVED.value == "approved"
    assert ReleaseState.RELEASED.value == "released"
    assert ReleaseState.REJECTED.value == "rejected"
    assert ReleaseState.BLOCKED.value == "blocked"


# ---------------------------------------------------------------------------
# GateResult and StageResult dataclasses
# ---------------------------------------------------------------------------

def test_gate_result_fields():
    gr = GateResult(gate_id="test", passed=True, score=1.0, evidence="ok", blocker=True)
    assert gr.gate_id == "test"
    assert gr.passed is True
    assert gr.score == 1.0
    assert gr.blocker is True


def test_stage_result_fields():
    sr = StageResult(stage="build", passed=True)
    assert sr.stage == "build"
    assert sr.passed is True
    assert sr.gate_results == []
    assert sr.completed_at is None


# ---------------------------------------------------------------------------
# Individual gate: manifest_complete
# ---------------------------------------------------------------------------

def test_gate_manifest_complete_passes():
    b = _alpha_bundle()
    gr = _gate_manifest_complete(b)
    assert gr.passed is True
    assert gr.score == 1.0
    assert gr.blocker is True


def test_gate_manifest_complete_fails_empty_id():
    b = ReleaseBundle(
        id="", title="T", version="1.0.0", release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
    )
    gr = _gate_manifest_complete(b)
    assert gr.passed is False
    assert gr.score == 0.0


# ---------------------------------------------------------------------------
# Individual gate: all_required_artifacts
# ---------------------------------------------------------------------------

def test_gate_all_required_artifacts_alpha_passes():
    b = _alpha_bundle()
    gr = _gate_all_required_artifacts(b)
    assert gr.passed is True


def test_gate_all_required_artifacts_stable_missing_audio():
    b = ReleaseBundle(
        id="x", title="T", version="1.0.0", release_type="stable",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[
            _make_artifact("s1", "script"),
            _make_artifact("v1", "video"),
            _make_artifact("c1", "caption"),
        ],
        metadata={}, tags=[],
    )
    gr = _gate_all_required_artifacts(b)
    assert gr.passed is False
    assert "audio" in gr.evidence
    assert gr.blocker is True


def test_gate_all_required_artifacts_score_partial():
    # rc needs script, video, audio — only script present
    b = ReleaseBundle(
        id="x", title="T", version="1.0.0", release_type="rc",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_make_artifact("s1", "script")],
        metadata={}, tags=[],
    )
    gr = _gate_all_required_artifacts(b)
    assert gr.passed is False
    assert 0.0 <= gr.score < 1.0


# ---------------------------------------------------------------------------
# Individual gate: version_valid
# ---------------------------------------------------------------------------

def test_gate_version_valid_passes():
    b = _alpha_bundle()
    gr = _gate_version_valid(b)
    assert gr.passed is True


def test_gate_version_valid_fails():
    b = ReleaseBundle(
        id="x", title="T", version="bad-version", release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
    )
    gr = _gate_version_valid(b)
    assert gr.passed is False
    assert gr.blocker is True


# ---------------------------------------------------------------------------
# Individual gate: video_resolution
# ---------------------------------------------------------------------------

def test_gate_video_resolution_no_videos():
    b = _alpha_bundle()
    gr = _gate_video_resolution(b)
    assert gr.passed is True
    assert "No video" in gr.evidence


def test_gate_video_resolution_hd_passes():
    b = ReleaseBundle(
        id="x", title="T", version="1.0.0", release_type="beta",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_make_artifact("v1", "video", resolution="1920x1080")],
        metadata={}, tags=[],
    )
    gr = _gate_video_resolution(b)
    assert gr.passed is True


def test_gate_video_resolution_low_fails():
    b = ReleaseBundle(
        id="x", title="T", version="1.0.0", release_type="beta",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_make_artifact("v1", "video", resolution="640x480")],
        metadata={}, tags=[],
    )
    gr = _gate_video_resolution(b)
    assert gr.passed is False
    assert gr.blocker is False  # non-blocker


def test_gate_video_resolution_missing_resolution_fails():
    b = ReleaseBundle(
        id="x", title="T", version="1.0.0", release_type="beta",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_make_artifact("v1", "video", resolution=None)],
        metadata={}, tags=[],
    )
    gr = _gate_video_resolution(b)
    assert gr.passed is False


# ---------------------------------------------------------------------------
# Individual gate: audio_present
# ---------------------------------------------------------------------------

def test_gate_audio_present_passes():
    b = ReleaseBundle(
        id="x", title="T", version="1.0.0", release_type="rc",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_make_artifact("a1", "audio")],
        metadata={}, tags=[],
    )
    gr = _gate_audio_present(b)
    assert gr.passed is True
    assert gr.blocker is False


def test_gate_audio_present_fails():
    b = _alpha_bundle()  # no audio
    gr = _gate_audio_present(b)
    assert gr.passed is False


# ---------------------------------------------------------------------------
# Individual gate: captions_for_stable
# ---------------------------------------------------------------------------

def test_gate_captions_for_stable_skipped_for_alpha():
    b = _alpha_bundle()
    gr = _gate_captions_for_stable(b)
    assert gr.passed is True
    assert "skipped" in gr.evidence


def test_gate_captions_for_stable_fails_no_caption():
    b = ReleaseBundle(
        id="x", title="T", version="1.0.0", release_type="stable",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_make_artifact("s1", "script"), _make_artifact("v1", "video"), _make_artifact("a1", "audio")],
        metadata={}, tags=[],
    )
    gr = _gate_captions_for_stable(b)
    assert gr.passed is False
    assert gr.blocker is True


def test_gate_captions_for_stable_passes_with_caption():
    b = _full_stable_bundle()
    gr = _gate_captions_for_stable(b)
    assert gr.passed is True


# ---------------------------------------------------------------------------
# Individual gate: no_duplicate_artifact_ids
# ---------------------------------------------------------------------------

def test_gate_no_duplicate_ids_passes():
    b = _alpha_bundle()
    gr = _gate_no_duplicate_artifact_ids(b)
    assert gr.passed is True


def test_gate_no_duplicate_ids_fails():
    b = ReleaseBundle(
        id="x", title="T", version="1.0.0", release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[
            _make_artifact("s1", "script"),
            _make_artifact("s1", "script"),  # duplicate ID
        ],
        metadata={}, tags=[],
    )
    gr = _gate_no_duplicate_artifact_ids(b)
    assert gr.passed is False
    assert "s1" in gr.evidence
    assert gr.blocker is True


# ---------------------------------------------------------------------------
# Individual gate: human_approval
# ---------------------------------------------------------------------------

def test_gate_human_approval_passes():
    b = _full_stable_bundle(with_approval=True)
    gr = _gate_human_approval(b)
    assert gr.passed is True


def test_gate_human_approval_fails():
    b = _full_stable_bundle(with_approval=False)
    gr = _gate_human_approval(b)
    assert gr.passed is False
    assert gr.blocker is True


# ---------------------------------------------------------------------------
# WorkflowEngine.advance — BUILD stage
# ---------------------------------------------------------------------------

def test_advance_build_passes_for_good_bundle():
    b = _alpha_bundle()
    new_state, sr = engine.advance(b, ReleaseState.BUILD)
    assert sr.passed is True
    assert new_state == ReleaseState.QA
    assert sr.stage == "build"


def test_advance_build_blocked_missing_artifacts():
    b = ReleaseBundle(
        id="x", title="T", version="1.0.0", release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[],  # no script required by alpha
        metadata={}, tags=[],
    )
    new_state, sr = engine.advance(b, ReleaseState.BUILD)
    assert sr.passed is False
    assert new_state == ReleaseState.BLOCKED


def test_advance_build_blocked_bad_version():
    b = ReleaseBundle(
        id="x", title="T", version="not-semver", release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_make_artifact("s1", "script")],
        metadata={}, tags=[],
    )
    new_state, sr = engine.advance(b, ReleaseState.BUILD)
    assert new_state == ReleaseState.BLOCKED


# ---------------------------------------------------------------------------
# WorkflowEngine.advance — APPROVED stage
# ---------------------------------------------------------------------------

def test_advance_approved_to_released():
    b = _full_stable_bundle(with_approval=True)
    new_state, sr = engine.advance(b, ReleaseState.APPROVED)
    assert new_state == ReleaseState.RELEASED
    assert sr.passed is True


def test_advance_approved_blocked_no_token():
    b = _full_stable_bundle(with_approval=False)
    new_state, sr = engine.advance(b, ReleaseState.APPROVED)
    assert new_state == ReleaseState.BLOCKED


# ---------------------------------------------------------------------------
# WorkflowEngine.advance — terminal states
# ---------------------------------------------------------------------------

def test_advance_released_stays():
    b = _alpha_bundle()
    new_state, sr = engine.advance(b, ReleaseState.RELEASED)
    assert new_state == ReleaseState.RELEASED
    assert sr.passed is False


def test_advance_rejected_stays():
    b = _alpha_bundle()
    new_state, sr = engine.advance(b, ReleaseState.REJECTED)
    assert new_state == ReleaseState.REJECTED


# ---------------------------------------------------------------------------
# WorkflowEngine.run_full — happy path alpha
# ---------------------------------------------------------------------------

def test_run_full_alpha_happy_path():
    b = _alpha_bundle(panel_score=0.9, with_approval=True)
    results = engine.run_full(b)
    stages = [sr.stage for sr in results]
    assert "build" in stages
    # Last result should have passed = True if it reached RELEASED
    final = results[-1]
    # Check overall flow progressed
    assert len(results) >= 2


def test_run_full_stable_happy_path():
    b = _full_stable_bundle(panel_score=0.9, with_approval=True)
    results = engine.run_full(b)
    stages = [sr.stage for sr in results]
    assert "build" in stages
    assert "qa" in stages


def test_run_full_blocked_early():
    b = ReleaseBundle(
        id="x", title="T", version="1.0.0", release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[],  # missing script
        metadata={}, tags=[],
    )
    results = engine.run_full(b)
    # Should stop at BUILD stage blocked
    assert len(results) == 1
    assert results[0].stage == "build"
    assert results[0].passed is False


def test_run_full_returns_list_of_stage_results():
    b = _alpha_bundle()
    results = engine.run_full(b)
    assert isinstance(results, list)
    for r in results:
        assert isinstance(r, StageResult)


def test_run_full_gate_results_populated():
    b = _alpha_bundle()
    results = engine.run_full(b)
    build_stage = next((r for r in results if r.stage == "build"), None)
    assert build_stage is not None
    assert len(build_stage.gate_results) > 0
    for gr in build_stage.gate_results:
        assert isinstance(gr, GateResult)


# ---------------------------------------------------------------------------
# Non-blocker gates don't block the stage
# ---------------------------------------------------------------------------

def test_non_blocker_gate_doesnt_block_qa():
    # Bundle with no audio (non-blocker) but otherwise valid for QA
    # (QA gates: video_resolution, audio_present[non-blocker], captions_for_stable, no_dup_ids)
    b = ReleaseBundle(
        id="x", title="T", version="1.0.0", release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_make_artifact("s1", "script")],
        metadata={}, tags=[],
    )
    new_state, sr = engine.advance(b, ReleaseState.QA)
    # audio_present fails but is non-blocker; no blocker gates fail
    # So should not be BLOCKED
    assert new_state != ReleaseState.BLOCKED
