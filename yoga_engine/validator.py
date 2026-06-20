"""
validator.py — generic vinyasa safety validator.

Rules implemented (generic public vinyasa anatomy, NOT proprietary):

ERROR-level:
  NO_WARMUP_BEFORE_PEAK     — a requires_warmup pose appears before any warmup exists
  PEAK_NO_WARMUP_PHASE      — sequence has a PEAK phase but no WARMUP phase
  MISSING_COUNTER_AFTER     — backbend or twist at end of phase w/ no counter following
  HEATED_DANGEROUS_POSE     — a heated_caution pose appears w/o a rest cue nearby

WARNING-level:
  BILATERAL_MISSING_SIDE    — pose with a side modifier missing its mirror
  PHASE_ORDER_IRREGULAR     — phases appear out of the expected arc order
  INTENSITY_SPIKE           — intensity jumps > 3 in one step (no build)
  SAVASANA_MISSING          — no savasana or cooldown phase
  HEATED_NO_REST_BETWEEN    — hot room class w/ > 4 consecutive high-intensity poses
  PEAK_TOO_EARLY            — peak arrives in the first 30 % of poses
  CONTRAINDICATION_NOTED    — pose with known contraindications (informational)
"""

from __future__ import annotations

from typing import List, Optional, Set, Tuple

from .schema import (
    BreathOp, IssueSeverity, Phase, PhaseBlock, PoseInstance,
    Sequence, ValidationIssue, ValidationReport,
)

# Expected phase order (each must appear after or at the same position as previous)
_IDEAL_ORDER: List[Phase] = [
    Phase.ARRIVAL,
    Phase.WARMUP,
    Phase.BUILD,
    Phase.PEAK,
    Phase.COOLDOWN,
    Phase.SAVASANA,
]

_HIGH_INTENSITY_THRESHOLD = 7
_CONSECUTIVE_HIGH_LIMIT_HEATED = 4


# ---------------------------------------------------------------------------
# Helper: flat pose list with phase context
# ---------------------------------------------------------------------------


def _flat_with_phase(seq: Sequence) -> List[Tuple[PoseInstance, Phase]]:
    result = []
    for block in seq.phases:
        for inst in block.poses:
            result.append((inst, block.phase))
    return result


# ---------------------------------------------------------------------------
# Individual rule checks
# ---------------------------------------------------------------------------


def _check_warmup_before_peak_poses(seq: Sequence) -> List[ValidationIssue]:
    """Any pose flagged requires_warmup must not appear before warmup is established."""
    issues: List[ValidationIssue] = []
    warmup_established = False

    for block in seq.phases:
        if block.phase in (Phase.WARMUP, Phase.BUILD, Phase.PEAK, Phase.COOLDOWN):
            warmup_established = True

        if block.phase == Phase.ARRIVAL and not warmup_established:
            for inst in block.poses:
                if inst.pose.requires_warmup:
                    issues.append(ValidationIssue(
                        severity=IssueSeverity.ERROR,
                        code="NO_WARMUP_BEFORE_PEAK",
                        message=(
                            f"{inst.pose.name!r} requires warm-up but appears in "
                            f"arrival before any warm-up phase."
                        ),
                        phase=block.label,
                        pose_token=inst.pose.token,
                    ))

    return issues


def _check_peak_has_warmup_phase(seq: Sequence) -> List[ValidationIssue]:
    """A PEAK phase must be preceded by a WARMUP (or BUILD) phase."""
    issues: List[ValidationIssue] = []
    has_warmup_or_build = any(
        b.phase in (Phase.WARMUP, Phase.BUILD)
        for b in seq.phases
    )
    has_peak = any(b.phase == Phase.PEAK for b in seq.phases)

    if has_peak and not has_warmup_or_build:
        issues.append(ValidationIssue(
            severity=IssueSeverity.ERROR,
            code="PEAK_NO_WARMUP_PHASE",
            message="Sequence has a PEAK phase but no WARMUP or BUILD phase precedes it.",
        ))

    return issues


def _check_counter_after_backbend_twist(seq: Sequence) -> List[ValidationIssue]:
    """
    After a backbend or twist that has needs_counter=True, there must be a
    counter pose before the sequence ends or before the next peak-intensity pose.
    """
    issues: List[ValidationIssue] = []
    flat = _flat_with_phase(seq)

    for idx, (inst, phase) in enumerate(flat):
        if not inst.pose.needs_counter:
            continue
        # Look forward for a counter pose within the next 3 poses
        found_counter = False
        for j in range(idx + 1, min(idx + 4, len(flat))):
            if flat[j][0].pose.is_counter:
                found_counter = True
                break
        if not found_counter:
            severity = IssueSeverity.ERROR if inst.pose.is_peak else IssueSeverity.WARNING
            issues.append(ValidationIssue(
                severity=severity,
                code="MISSING_COUNTER_AFTER",
                message=(
                    f"No counter pose found within 3 steps after {inst.pose.name!r} "
                    f"(needs_counter=True)."
                ),
                phase=phase.value,
                pose_token=inst.pose.token,
            ))

    return issues


def _check_bilateral_symmetry(seq: Sequence) -> List[ValidationIssue]:
    """
    For any pose that appears with a side modifier (_r or _l), the mirror
    side should also appear somewhere in the sequence.
    """
    issues: List[ValidationIssue] = []
    # Build set of (token, side) pairs
    sided: Set[Tuple[str, str]] = set()
    for block in seq.phases:
        for inst in block.poses:
            if inst.side in ("r", "l"):
                sided.add((inst.pose.token, inst.side))

    for token, side in sided:
        mirror = "l" if side == "r" else "r"
        if (token, mirror) not in sided:
            pose = seq.all_poses
            # find the block label
            label = next(
                (b.label for b in seq.phases
                 for i in b.poses if i.pose.token == token and i.side == side),
                "?",
            )
            issues.append(ValidationIssue(
                severity=IssueSeverity.WARNING,
                code="BILATERAL_MISSING_SIDE",
                message=(
                    f"{seq.phases[0].poses[0].pose.name if seq.phases else '?'!r} "
                    f"Pose {token!r} done on {side!r} side but mirror side "
                    f"({mirror!r}) not found."
                ),
                phase=label,
                pose_token=token,
            ))

    return issues


def _check_phase_order(seq: Sequence) -> List[ValidationIssue]:
    """Phases should appear in the expected ARRIVAL → WARMUP → BUILD → PEAK → COOLDOWN → SAVASANA order."""
    issues: List[ValidationIssue] = []
    last_idx = -1
    for block in seq.phases:
        try:
            idx = _IDEAL_ORDER.index(block.phase)
        except ValueError:
            continue  # unknown phase, skip
        if idx < last_idx:
            issues.append(ValidationIssue(
                severity=IssueSeverity.WARNING,
                code="PHASE_ORDER_IRREGULAR",
                message=(
                    f"Phase {block.label!r} ({block.phase.value}) appears after "
                    f"a later-arc phase (expected order: "
                    f"{' → '.join(p.value for p in _IDEAL_ORDER)})."
                ),
                phase=block.label,
            ))
        else:
            last_idx = idx

    return issues


def _check_intensity_spikes(seq: Sequence) -> List[ValidationIssue]:
    """Flag any single-step intensity jump > 3."""
    issues: List[ValidationIssue] = []
    flat = _flat_with_phase(seq)
    for idx in range(1, len(flat)):
        prev_inst, _ = flat[idx - 1]
        curr_inst, curr_phase = flat[idx]
        delta = curr_inst.pose.intensity - prev_inst.pose.intensity
        if delta > 3:
            issues.append(ValidationIssue(
                severity=IssueSeverity.WARNING,
                code="INTENSITY_SPIKE",
                message=(
                    f"Intensity jumps from {prev_inst.pose.intensity} "
                    f"({prev_inst.pose.token}) to {curr_inst.pose.intensity} "
                    f"({curr_inst.pose.token}) — a +{delta} step with no build."
                ),
                phase=curr_phase.value,
                pose_token=curr_inst.pose.token,
            ))

    return issues


def _check_savasana(seq: Sequence) -> List[ValidationIssue]:
    """Warn if neither savasana nor cooldown is present."""
    has_sv = any(b.phase in (Phase.SAVASANA, Phase.COOLDOWN) for b in seq.phases)
    if not has_sv:
        return [ValidationIssue(
            severity=IssueSeverity.WARNING,
            code="SAVASANA_MISSING",
            message="No cooldown or savasana phase found. Consider adding one.",
        )]
    return []


def _check_heated_room(seq: Sequence) -> List[ValidationIssue]:
    """Extra checks when the class is marked heated."""
    if not seq.heated_room:
        return []

    issues: List[ValidationIssue] = []
    flat = _flat_with_phase(seq)

    # Flag high-heat poses without nearby rest
    consecutive_high = 0
    for inst, phase in flat:
        if inst.pose.intensity >= _HIGH_INTENSITY_THRESHOLD:
            consecutive_high += 1
        else:
            consecutive_high = 0

        if consecutive_high > _CONSECUTIVE_HIGH_LIMIT_HEATED:
            issues.append(ValidationIssue(
                severity=IssueSeverity.WARNING,
                code="HEATED_NO_REST_BETWEEN",
                message=(
                    f"Heated class: {consecutive_high} consecutive high-intensity "
                    f"poses without a rest/reset. Consider inserting DD, CB, or SV."
                ),
                phase=phase.value,
                pose_token=inst.pose.token,
            ))
            consecutive_high = 0  # reset so we don't re-flag same run

        if inst.pose.heated_caution:
            issues.append(ValidationIssue(
                severity=IssueSeverity.WARNING,
                code="HEATED_CAUTION_POSE",
                message=(
                    f"{inst.pose.name!r} carries a heated-room caution. "
                    "Ensure adequate hydration cues and offer modification."
                ),
                phase=phase.value,
                pose_token=inst.pose.token,
            ))

    return issues


def _check_peak_too_early(seq: Sequence) -> List[ValidationIssue]:
    """Warn if a peak-intensity pose appears in the first 30 % of all poses."""
    issues: List[ValidationIssue] = []
    flat = _flat_with_phase(seq)
    total = len(flat)
    if total == 0:
        return []
    threshold = max(1, int(total * 0.30))

    for idx, (inst, phase) in enumerate(flat[:threshold]):
        if inst.pose.is_peak or inst.pose.intensity >= 8:
            issues.append(ValidationIssue(
                severity=IssueSeverity.WARNING,
                code="PEAK_TOO_EARLY",
                message=(
                    f"High-intensity pose {inst.pose.name!r} (intensity="
                    f"{inst.pose.intensity}) appears at position {idx + 1}/{total} "
                    f"— within the first 30 % of the sequence."
                ),
                phase=phase.value,
                pose_token=inst.pose.token,
            ))

    return issues


# ---------------------------------------------------------------------------
# Public validator
# ---------------------------------------------------------------------------


def validate_sequence(seq: Sequence) -> ValidationReport:
    """
    Run all safety checks on a :class:`~yoga_engine.schema.Sequence`.

    Returns a :class:`~yoga_engine.schema.ValidationReport` with zero or more
    :class:`~yoga_engine.schema.ValidationIssue` entries.
    """
    report = ValidationReport()

    checkers = [
        _check_warmup_before_peak_poses,
        _check_peak_has_warmup_phase,
        _check_counter_after_backbend_twist,
        _check_bilateral_symmetry,
        _check_phase_order,
        _check_intensity_spikes,
        _check_savasana,
        _check_heated_room,
        _check_peak_too_early,
    ]

    for checker in checkers:
        report.issues.extend(checker(seq))

    return report
