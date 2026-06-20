"""Tests for release_qa.manifest — ReleaseBundle, Artifact, ManifestValidator."""
from __future__ import annotations

import json
import pytest

from release_qa.manifest import (
    Artifact,
    ReleaseBundle,
    ManifestReport,
    ManifestValidator,
    VALID_RELEASE_TYPES,
    VALID_ARTIFACT_TYPES,
    REQUIRED_ARTIFACTS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _script_artifact(aid: str = "s1", required: bool = True, checksum: str = "abc123") -> Artifact:
    return Artifact(
        id=aid,
        artifact_type="script",
        path="scripts/episode.md",
        size_bytes=1024,
        checksum_sha256=checksum,
        required=required,
    )


def _video_artifact(aid: str = "v1", resolution: str = "1920x1080", checksum: str = "vid123") -> Artifact:
    return Artifact(
        id=aid,
        artifact_type="video",
        path="exports/episode.mp4",
        size_bytes=500_000_000,
        checksum_sha256=checksum,
        duration_seconds=600.0,
        resolution=resolution,
    )


def _audio_artifact(aid: str = "a1", checksum: str = "aud123") -> Artifact:
    return Artifact(
        id=aid,
        artifact_type="audio",
        path="exports/episode.mp3",
        size_bytes=50_000_000,
        checksum_sha256=checksum,
        duration_seconds=600.0,
    )


def _caption_artifact(aid: str = "c1", checksum: str = "cap123") -> Artifact:
    return Artifact(
        id=aid,
        artifact_type="caption",
        path="exports/episode.srt",
        size_bytes=10_000,
        checksum_sha256=checksum,
        language="en",
    )


def _alpha_bundle(**kwargs) -> ReleaseBundle:
    defaults = dict(
        id="bundle-alpha-1",
        title="My Alpha Release",
        version="0.1.0",
        release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_script_artifact()],
        metadata={"project": "test", "episode": 1},
        tags=["alpha", "test"],
    )
    defaults.update(kwargs)
    return ReleaseBundle(**defaults)


def _stable_bundle(**kwargs) -> ReleaseBundle:
    defaults = dict(
        id="bundle-stable-1",
        title="My Stable Release",
        version="1.0.0",
        release_type="stable",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[
            _script_artifact(),
            _video_artifact(),
            _audio_artifact(),
            _caption_artifact(),
        ],
        metadata={"project": "test", "episode": 1},
        tags=["stable", "production"],
    )
    defaults.update(kwargs)
    return ReleaseBundle(**defaults)


validator = ManifestValidator()


# ---------------------------------------------------------------------------
# Story 1: Artifact dataclass
# ---------------------------------------------------------------------------

def test_artifact_creation():
    a = Artifact(id="a1", artifact_type="video", path="v.mp4", size_bytes=100)
    assert a.id == "a1"
    assert a.artifact_type == "video"
    assert a.size_bytes == 100
    assert a.checksum_sha256 is None
    assert a.required is True


def test_artifact_to_dict():
    a = _script_artifact()
    d = a.to_dict()
    assert d["id"] == "s1"
    assert d["artifact_type"] == "script"
    assert d["checksum_sha256"] == "abc123"


def test_artifact_from_dict_round_trip():
    a = _video_artifact()
    d = a.to_dict()
    restored = Artifact.from_dict(d)
    assert restored.id == a.id
    assert restored.artifact_type == a.artifact_type
    assert restored.resolution == a.resolution
    assert restored.duration_seconds == a.duration_seconds


# ---------------------------------------------------------------------------
# Story 2: ManifestReport fields
# ---------------------------------------------------------------------------

def test_manifest_report_valid():
    r = ManifestReport(valid=True)
    assert r.valid is True
    assert r.errors == []
    assert r.warnings == []


def test_manifest_report_with_errors():
    r = ManifestReport(valid=False, errors=["err1", "err2"], warnings=["warn1"])
    assert not r.valid
    assert len(r.errors) == 2
    assert len(r.warnings) == 1


# ---------------------------------------------------------------------------
# Story 3: Valid alpha bundle
# ---------------------------------------------------------------------------

def test_valid_alpha_bundle():
    bundle = _alpha_bundle()
    report = validator.validate(bundle)
    assert report.valid is True
    assert report.errors == []


# ---------------------------------------------------------------------------
# Story 4: Valid beta bundle
# ---------------------------------------------------------------------------

def test_valid_beta_bundle():
    bundle = ReleaseBundle(
        id="bundle-beta-1",
        title="My Beta Release",
        version="0.2.0",
        release_type="beta",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_script_artifact(), _video_artifact()],
        metadata={"project": "test"},
        tags=["beta"],
    )
    report = validator.validate(bundle)
    assert report.valid is True


# ---------------------------------------------------------------------------
# Story 5: Valid rc bundle
# ---------------------------------------------------------------------------

def test_valid_rc_bundle():
    bundle = ReleaseBundle(
        id="bundle-rc-1",
        title="My RC Release",
        version="1.0.0-rc1",
        release_type="rc",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_script_artifact(), _video_artifact(), _audio_artifact()],
        metadata={"project": "test"},
        tags=["rc"],
    )
    report = validator.validate(bundle)
    assert report.valid is True


# ---------------------------------------------------------------------------
# Story 6: Valid stable bundle
# ---------------------------------------------------------------------------

def test_valid_stable_bundle():
    bundle = _stable_bundle()
    report = validator.validate(bundle)
    assert report.valid is True


# ---------------------------------------------------------------------------
# Story 7: Missing script for alpha → error
# ---------------------------------------------------------------------------

def test_alpha_missing_script_artifact():
    bundle = _alpha_bundle(artifacts=[])
    report = validator.validate(bundle)
    assert not report.valid
    assert any("script" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Story 8: Missing video for beta → error
# ---------------------------------------------------------------------------

def test_beta_missing_video_artifact():
    bundle = ReleaseBundle(
        id="b1",
        title="Beta",
        version="0.2.0",
        release_type="beta",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_script_artifact()],  # missing video
        metadata={"p": "x"},
        tags=["t"],
    )
    report = validator.validate(bundle)
    assert not report.valid
    assert any("video" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Story 9: Missing audio for rc → error
# ---------------------------------------------------------------------------

def test_rc_missing_audio_artifact():
    bundle = ReleaseBundle(
        id="r1",
        title="RC",
        version="1.0.0",
        release_type="rc",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_script_artifact(), _video_artifact()],  # missing audio
        metadata={"p": "x"},
        tags=["t"],
    )
    report = validator.validate(bundle)
    assert not report.valid
    assert any("audio" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Story 10: Missing captions for stable → error
# ---------------------------------------------------------------------------

def test_stable_missing_caption_artifact():
    bundle = ReleaseBundle(
        id="s1",
        title="Stable",
        version="1.0.0",
        release_type="stable",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_script_artifact(), _video_artifact(), _audio_artifact()],  # no caption
        metadata={"p": "x"},
        tags=["t"],
    )
    report = validator.validate(bundle)
    assert not report.valid
    assert any("caption" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Story 11: Invalid release_type
# ---------------------------------------------------------------------------

def test_invalid_release_type():
    bundle = _alpha_bundle(release_type="nightly")
    report = validator.validate(bundle)
    assert not report.valid
    assert any("release_type" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Story 12: Invalid semver
# ---------------------------------------------------------------------------

def test_invalid_semver():
    bundle = _alpha_bundle(version="not-a-version")
    report = validator.validate(bundle)
    assert not report.valid
    assert any("semver" in e for e in report.errors)


def test_invalid_semver_missing_patch():
    bundle = _alpha_bundle(version="1.0")
    report = validator.validate(bundle)
    assert not report.valid


# ---------------------------------------------------------------------------
# Story 13: Valid semver variants
# ---------------------------------------------------------------------------

def test_valid_semver_with_prerelease():
    bundle = _alpha_bundle(version="1.0.0-rc1")
    report = validator.validate(bundle)
    # only version-related errors should not appear
    version_errors = [e for e in report.errors if "semver" in e.lower() or "version" in e.lower()]
    assert version_errors == []


def test_valid_semver_with_dot_prerelease():
    bundle = _alpha_bundle(version="2.3.4-beta.1")
    report = validator.validate(bundle)
    version_errors = [e for e in report.errors if "semver" in e.lower() or "version" in e.lower()]
    assert version_errors == []


# ---------------------------------------------------------------------------
# Story 14: Checksum required for required artifacts
# ---------------------------------------------------------------------------

def test_required_artifact_missing_checksum():
    a = Artifact(
        id="no-cs",
        artifact_type="script",
        path="s.md",
        size_bytes=100,
        checksum_sha256=None,
        required=True,
    )
    bundle = _alpha_bundle(artifacts=[a])
    report = validator.validate(bundle)
    assert not report.valid
    assert any("checksum" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Story 15: No checksum on non-required artifact is OK (no error)
# ---------------------------------------------------------------------------

def test_non_required_artifact_missing_checksum_ok():
    a = Artifact(
        id="opt-no-cs",
        artifact_type="script",
        path="s.md",
        size_bytes=100,
        checksum_sha256=None,
        required=False,
    )
    bundle = _alpha_bundle(artifacts=[a])
    report = validator.validate(bundle)
    checksum_errors = [e for e in report.errors if "checksum" in e]
    assert checksum_errors == []


# ---------------------------------------------------------------------------
# Story 16: Empty title error
# ---------------------------------------------------------------------------

def test_empty_title_error():
    bundle = _alpha_bundle(title="   ")
    report = validator.validate(bundle)
    assert not report.valid
    assert any("title" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Story 17: Empty id error
# ---------------------------------------------------------------------------

def test_empty_id_error():
    bundle = _alpha_bundle(id="   ")
    report = validator.validate(bundle)
    assert not report.valid
    assert any("id must not be empty" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Story 18: Metadata warnings
# ---------------------------------------------------------------------------

def test_empty_metadata_warning():
    bundle = _alpha_bundle(metadata={})
    report = validator.validate(bundle)
    assert any("metadata" in w for w in report.warnings)


# ---------------------------------------------------------------------------
# Story 19: Tags warnings
# ---------------------------------------------------------------------------

def test_empty_tags_warning():
    bundle = _alpha_bundle(tags=[])
    report = validator.validate(bundle)
    assert any("tags" in w for w in report.warnings)


# ---------------------------------------------------------------------------
# Story 20: JSON round-trip
# ---------------------------------------------------------------------------

def test_release_bundle_json_round_trip():
    bundle = _stable_bundle()
    json_str = bundle.to_json()
    restored = ReleaseBundle.from_json(json_str)
    assert restored.id == bundle.id
    assert restored.title == bundle.title
    assert restored.version == bundle.version
    assert restored.release_type == bundle.release_type
    assert len(restored.artifacts) == len(bundle.artifacts)
    assert restored.artifacts[0].id == bundle.artifacts[0].id


# ---------------------------------------------------------------------------
# Story 21: to_dict / from_dict round-trip
# ---------------------------------------------------------------------------

def test_release_bundle_dict_round_trip():
    bundle = _alpha_bundle()
    d = bundle.to_dict()
    restored = ReleaseBundle.from_dict(d)
    assert restored.id == bundle.id
    assert restored.version == bundle.version
    assert len(restored.artifacts) == 1


# ---------------------------------------------------------------------------
# Story 22: Multiple artifacts
# ---------------------------------------------------------------------------

def test_multiple_artifacts_stable_valid():
    bundle = _stable_bundle()
    assert len(bundle.artifacts) == 4
    report = validator.validate(bundle)
    assert report.valid


def test_multiple_artifacts_with_thumbnail():
    thumb = Artifact(
        id="th1",
        artifact_type="thumbnail",
        path="thumb.jpg",
        size_bytes=200_000,
        checksum_sha256="thumb_cs",
    )
    bundle = _stable_bundle()
    bundle.artifacts.append(thumb)
    report = validator.validate(bundle)
    assert report.valid


# ---------------------------------------------------------------------------
# Story 23: Invalid artifact type
# ---------------------------------------------------------------------------

def test_invalid_artifact_type():
    a = Artifact(
        id="bad",
        artifact_type="spreadsheet",
        path="data.xlsx",
        size_bytes=1000,
        checksum_sha256="x",
    )
    bundle = _alpha_bundle(artifacts=[_script_artifact(), a])
    report = validator.validate(bundle)
    assert not report.valid
    assert any("spreadsheet" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Story 24: JSON is parseable and has expected fields
# ---------------------------------------------------------------------------

def test_json_structure():
    bundle = _alpha_bundle()
    data = json.loads(bundle.to_json())
    assert "id" in data
    assert "title" in data
    assert "version" in data
    assert "release_type" in data
    assert "artifacts" in data
    assert isinstance(data["artifacts"], list)
