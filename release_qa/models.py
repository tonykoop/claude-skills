"""Pydantic v2 models for the release-QA gate engine.

These models represent an agent-produced release bundle and its declared
test evidence. The gate engine in ``rules.py`` evaluates a
:class:`ReleaseBundleManifest` against a set of adversarial rules and
emits a structured :class:`GateResult`.
"""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class ArtifactDeclaration(BaseModel):
    """A single artifact included in the release bundle."""

    model_config = ConfigDict(frozen=True)

    name: str
    path: str
    checksum_sha256: Optional[str] = None


class TestRunRecord(BaseModel):
    """Evidence record for a single test-suite run."""

    model_config = ConfigDict(frozen=True)

    suite_name: str
    claimed_passed: int
    claimed_failed: int
    evidence_url: Optional[str] = None
    self_certified: bool = False


class ReleaseBundleManifest(BaseModel):
    """Top-level manifest for an agent-produced release bundle.

    This is the input to :func:`release_qa.rules.evaluate_release`.
    """

    model_config = ConfigDict(frozen=True)

    bundle_id: str
    version: str
    changelog_entry: Optional[str] = None
    artifacts: List[ArtifactDeclaration] = []
    test_runs: List[TestRunRecord] = []
    claimed_status: Literal["green", "yellow", "red"] = "yellow"
    adversarial_review_present: bool = False
    declared_files: List[str] = []

    @field_validator("version")
    @classmethod
    def version_must_be_nonempty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("version must be a non-empty string")
        return v
