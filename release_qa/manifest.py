"""Release Bundle Manifest — rich structured manifest for studio release packages."""
from __future__ import annotations
import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

VALID_RELEASE_TYPES = {"alpha", "beta", "rc", "stable"}
VALID_ARTIFACT_TYPES = {"video", "audio", "script", "thumbnail", "caption", "asset"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-.].+)?$")

# Required artifact types per release_type
REQUIRED_ARTIFACTS: Dict[str, List[str]] = {
    "alpha": ["script"],
    "beta": ["script", "video"],
    "rc": ["script", "video", "audio"],
    "stable": ["script", "video", "audio", "caption"],
}


@dataclass
class Artifact:
    id: str
    artifact_type: str   # video/audio/script/thumbnail/caption/asset
    path: str
    size_bytes: int
    checksum_sha256: Optional[str] = None
    duration_seconds: Optional[float] = None   # video/audio
    resolution: Optional[str] = None            # video e.g. "1920x1080"
    language: Optional[str] = None              # caption
    required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Artifact":
        return cls(**d)


@dataclass
class ReleaseBundle:
    id: str
    title: str
    version: str
    release_type: str   # alpha/beta/rc/stable
    created_at: str     # ISO string
    artifacts: List[Artifact] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ReleaseBundle":
        artifacts = [Artifact.from_dict(a) for a in d.pop("artifacts", [])]
        bundle = cls(**d)
        bundle.artifacts = artifacts
        return bundle

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, s: str) -> "ReleaseBundle":
        return cls.from_dict(json.loads(s))


@dataclass
class ManifestReport:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ManifestValidator:
    def validate(self, bundle: ReleaseBundle) -> ManifestReport:
        errors: List[str] = []
        warnings: List[str] = []

        # release_type
        if bundle.release_type not in VALID_RELEASE_TYPES:
            errors.append(f"Invalid release_type: '{bundle.release_type}'. Must be one of {sorted(VALID_RELEASE_TYPES)}.")

        # version semver
        if not SEMVER_RE.match(bundle.version):
            errors.append(f"Version '{bundle.version}' is not valid semver (e.g. 1.2.3).")

        # artifact types valid
        artifact_ids = []
        artifact_types_present = set()
        for a in bundle.artifacts:
            if a.artifact_type not in VALID_ARTIFACT_TYPES:
                errors.append(f"Artifact '{a.id}' has invalid type '{a.artifact_type}'.")
            if a.required and not a.checksum_sha256:
                errors.append(f"Required artifact '{a.id}' is missing checksum_sha256.")
            artifact_ids.append(a.id)
            artifact_types_present.add(a.artifact_type)

        # required artifacts per release_type
        required = REQUIRED_ARTIFACTS.get(bundle.release_type, [])
        for req_type in required:
            if req_type not in artifact_types_present:
                errors.append(f"Release type '{bundle.release_type}' requires an artifact of type '{req_type}' but none is present.")

        # warnings
        if not bundle.metadata:
            warnings.append("metadata dict is empty — consider adding episode/project metadata.")
        if not bundle.tags:
            warnings.append("tags list is empty — consider adding descriptive tags.")
        if not bundle.title.strip():
            errors.append("title must not be empty.")
        if not bundle.id.strip():
            errors.append("id must not be empty.")

        return ManifestReport(valid=len(errors) == 0, errors=errors, warnings=warnings)
