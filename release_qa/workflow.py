"""Multi-stage gate workflow state machine for release pipeline."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional

from release_qa.manifest import ReleaseBundle, SEMVER_RE

class ReleaseState(Enum):
    DRAFT = "draft"
    BUILD = "build"
    QA = "qa"
    REVIEW = "review"
    APPROVED = "approved"
    RELEASED = "released"
    REJECTED = "rejected"
    BLOCKED = "blocked"


@dataclass
class GateResult:
    gate_id: str
    passed: bool
    score: float   # 0-1
    evidence: str
    blocker: bool


@dataclass
class StageResult:
    stage: str
    passed: bool
    gate_results: List[GateResult] = field(default_factory=list)
    entered_at: str = ""
    completed_at: Optional[str] = None


# ---- Gate implementations ----

def _gate_manifest_complete(bundle: ReleaseBundle) -> GateResult:
    ok = bool(bundle.id and bundle.title and bundle.version and bundle.release_type)
    return GateResult(
        gate_id="manifest_complete",
        passed=ok,
        score=1.0 if ok else 0.0,
        evidence="All required manifest fields present." if ok else "One or more required manifest fields are missing.",
        blocker=True,
    )

def _gate_all_required_artifacts(bundle: ReleaseBundle) -> GateResult:
    from release_qa.manifest import REQUIRED_ARTIFACTS
    required = set(REQUIRED_ARTIFACTS.get(bundle.release_type, []))
    present = {a.artifact_type for a in bundle.artifacts}
    missing = required - present
    ok = len(missing) == 0
    return GateResult(
        gate_id="all_required_artifacts",
        passed=ok,
        score=1.0 if ok else max(0.0, 1.0 - len(missing) / max(len(required), 1)),
        evidence=f"All required artifact types present: {sorted(present)}." if ok else f"Missing required artifact types: {sorted(missing)}.",
        blocker=True,
    )

def _gate_version_valid(bundle: ReleaseBundle) -> GateResult:
    ok = bool(SEMVER_RE.match(bundle.version))
    return GateResult(
        gate_id="version_valid",
        passed=ok,
        score=1.0 if ok else 0.0,
        evidence=f"Version '{bundle.version}' is valid semver." if ok else f"Version '{bundle.version}' is not valid semver.",
        blocker=True,
    )

def _gate_video_resolution(bundle: ReleaseBundle) -> GateResult:
    videos = [a for a in bundle.artifacts if a.artifact_type == "video"]
    if not videos:
        return GateResult(gate_id="video_resolution", passed=True, score=1.0, evidence="No video artifacts to check.", blocker=False)
    failing = []
    for v in videos:
        if not v.resolution:
            failing.append(v.id)
            continue
        try:
            parts = v.resolution.lower().replace("x", "x").split("x")
            height = int(parts[1]) if len(parts) >= 2 else 0
            if height < 720:
                failing.append(v.id)
        except (ValueError, IndexError):
            failing.append(v.id)
    ok = len(failing) == 0
    return GateResult(
        gate_id="video_resolution",
        passed=ok,
        score=1.0 if ok else 0.0,
        evidence="All videos are >= 720p." if ok else f"Video(s) below 720p or missing resolution: {failing}.",
        blocker=False,
    )

def _gate_audio_present(bundle: ReleaseBundle) -> GateResult:
    has_audio = any(a.artifact_type == "audio" for a in bundle.artifacts)
    return GateResult(
        gate_id="audio_present",
        passed=has_audio,
        score=1.0 if has_audio else 0.0,
        evidence="Audio artifact present." if has_audio else "No audio artifact found.",
        blocker=False,
    )

def _gate_captions_for_stable(bundle: ReleaseBundle) -> GateResult:
    if bundle.release_type != "stable":
        return GateResult(gate_id="captions_for_stable", passed=True, score=1.0, evidence="Not a stable release; caption check skipped.", blocker=False)
    has_captions = any(a.artifact_type == "caption" for a in bundle.artifacts)
    return GateResult(
        gate_id="captions_for_stable",
        passed=has_captions,
        score=1.0 if has_captions else 0.0,
        evidence="Caption artifact present for stable release." if has_captions else "Stable release requires caption artifact.",
        blocker=True,
    )

def _gate_no_duplicate_artifact_ids(bundle: ReleaseBundle) -> GateResult:
    ids = [a.id for a in bundle.artifacts]
    seen = set()
    dupes = []
    for i in ids:
        if i in seen:
            dupes.append(i)
        seen.add(i)
    ok = len(dupes) == 0
    return GateResult(
        gate_id="no_duplicate_artifact_ids",
        passed=ok,
        score=1.0 if ok else 0.0,
        evidence="No duplicate artifact IDs." if ok else f"Duplicate artifact IDs found: {dupes}.",
        blocker=True,
    )

def _gate_adversarial_panel_score(bundle: ReleaseBundle) -> GateResult:
    # Try to call existing adversarial panel if available; else use stub
    try:
        from release_qa.adversarial_panel import AdversarialPanel
        panel = AdversarialPanel()
        report = panel.review(bundle)
        score = report.consensus_score
        ok = score >= 0.7
        return GateResult(
            gate_id="adversarial_panel_score",
            passed=ok,
            score=score,
            evidence=f"Panel consensus score: {score:.2f}. Recommendation: {report.recommendation}.",
            blocker=True,
        )
    except Exception as e:
        # Stub: check metadata for pre-computed score
        score = float(bundle.metadata.get("panel_score", 0.0))
        ok = score >= 0.7
        return GateResult(
            gate_id="adversarial_panel_score",
            passed=ok,
            score=score,
            evidence=f"Panel score from metadata: {score:.2f}." if score > 0 else f"No panel score available (stub). Error: {e}",
            blocker=True,
        )

def _gate_human_approval(bundle: ReleaseBundle) -> GateResult:
    token = bundle.metadata.get("human_approval_token", "")
    ok = bool(token and str(token).strip())
    return GateResult(
        gate_id="human_approval",
        passed=ok,
        score=1.0 if ok else 0.0,
        evidence="Human approval token present." if ok else "No human approval token in bundle metadata.",
        blocker=True,
    )


# Stage -> gates mapping
_STAGE_GATES = {
    ReleaseState.BUILD: [_gate_manifest_complete, _gate_all_required_artifacts, _gate_version_valid],
    ReleaseState.QA: [_gate_video_resolution, _gate_audio_present, _gate_captions_for_stable, _gate_no_duplicate_artifact_ids],
    ReleaseState.REVIEW: [_gate_adversarial_panel_score],
    ReleaseState.APPROVED: [_gate_human_approval],
}

_NEXT_STATE = {
    ReleaseState.DRAFT: ReleaseState.BUILD,
    ReleaseState.BUILD: ReleaseState.QA,
    ReleaseState.QA: ReleaseState.REVIEW,
    ReleaseState.REVIEW: ReleaseState.APPROVED,
    ReleaseState.APPROVED: ReleaseState.RELEASED,
}


class WorkflowEngine:
    def advance(self, bundle: ReleaseBundle, current_state: ReleaseState) -> Tuple[ReleaseState, StageResult]:
        """Run all gates for current_state and return (new_state, StageResult)."""
        entered_at = bundle.metadata.get("workflow_timestamp", "2026-06-19T00:00:00Z")

        next_state = _NEXT_STATE.get(current_state)
        if next_state is None:
            # Terminal or unknown state
            sr = StageResult(stage=current_state.value, passed=False, entered_at=entered_at, completed_at=entered_at)
            return current_state, sr

        gates = _STAGE_GATES.get(current_state, [])
        gate_results = [g(bundle) for g in gates]

        # All blocker gates must pass, and all gates must pass
        all_passed = all(gr.passed for gr in gate_results)

        completed_at = bundle.metadata.get("workflow_timestamp", "2026-06-19T00:00:00Z")
        sr = StageResult(
            stage=current_state.value,
            passed=all_passed,
            gate_results=gate_results,
            entered_at=entered_at,
            completed_at=completed_at,
        )

        if all_passed:
            return next_state, sr
        else:
            # Check if any blocker failed
            blocker_failed = any(gr.blocker and not gr.passed for gr in gate_results)
            return ReleaseState.BLOCKED if blocker_failed else ReleaseState.REJECTED, sr

    def run_full(self, bundle: ReleaseBundle) -> List[StageResult]:
        """Run from DRAFT through to completion."""
        results = []
        state = ReleaseState.DRAFT
        # DRAFT has no gates, advance directly
        state = ReleaseState.BUILD

        terminal = {ReleaseState.RELEASED, ReleaseState.REJECTED, ReleaseState.BLOCKED}
        visited = set()

        while state not in terminal:
            if state in visited:
                break
            visited.add(state)
            new_state, sr = self.advance(bundle, state)
            results.append(sr)
            if new_state == state:
                break
            state = new_state

        return results
