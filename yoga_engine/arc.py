"""
arc.py — energy-curve (intensity arc) analyser for a Sequence.

The arc analyser examines the intensity curve of a sequence and classifies
its overall shape. This is useful for:
  - Confirming a class "breathes" correctly (builds → peaks → releases)
  - Detecting flat, inverted, or spikey arcs that may signal sequencing issues
  - Feeding back into the sequencer for auto-balancing

Arc shapes (generic vinyasa vocabulary):
  mountain  — gradual build to a single peak then tapering descent (ideal)
  plateau   — long middle section at sustained high intensity, then drop
  spike     — one sharp high point surrounded by much lower intensity
  flat      — little variation throughout (low variance)
  inverted  — starts high, ends high, dips in the middle (counter-arc)
  wave      — multiple distinct rises and falls (may be intentional)
"""

from __future__ import annotations

import statistics
from typing import List

from .schema import ArcReport, Phase, Sequence


_FLAT_STDEV_THRESHOLD = 1.2   # stdev below this → "flat"
_SPIKE_RATIO = 0.60           # if peak pose > 60 % above the mean → "spike"


# ---------------------------------------------------------------------------
# Arc shape classifier
# ---------------------------------------------------------------------------


def _classify_arc(curve: List[int]) -> str:
    if len(curve) < 3:
        return "flat"

    mean_val = statistics.mean(curve)
    stdev_val = statistics.pstdev(curve)

    if stdev_val < _FLAT_STDEV_THRESHOLD:
        return "flat"

    peak_idx = curve.index(max(curve))
    peak_val = curve[peak_idx]
    total = len(curve)

    # Spike: peak is ≥ 60% above mean, narrow (≤ 15% of total),
    # the entry is abrupt (left approach drops > 2), AND there is no
    # meaningful build-up window before the peak (build window avg < mean).
    if peak_val >= mean_val * (1 + _SPIKE_RATIO):
        near_peak_count = sum(1 for v in curve if v >= peak_val - 1)
        if near_peak_count / total <= 0.15:
            left_val = curve[peak_idx - 1] if peak_idx > 0 else 0
            if (peak_val - left_val) > 2:
                # Check that there is no gradual build-up before the peak.
                # Look at the 5 poses leading to the peak (or all if < 5).
                window = max(1, min(5, peak_idx))
                build_window = curve[peak_idx - window: peak_idx]
                build_avg = sum(build_window) / len(build_window) if build_window else 0
                if build_avg <= mean_val:
                    return "spike"

    # Inverted: first third and last third are both higher than middle third
    third = total // 3
    start_mean = statistics.mean(curve[:third]) if third else mean_val
    mid_mean = statistics.mean(curve[third:2 * third]) if third else mean_val
    end_mean = statistics.mean(curve[2 * third:]) if third else mean_val

    if start_mean > mid_mean and end_mean > mid_mean:
        return "inverted"

    # Plateau: peak is in the middle third and stdev of middle > outer thirds
    if third <= peak_idx < 2 * third:
        outer_vals = curve[:third] + curve[2 * third:]
        if outer_vals:
            outer_stdev = statistics.pstdev(outer_vals)
            inner_stdev = statistics.pstdev(curve[third:2 * third])
            if inner_stdev < outer_stdev and (end_mean < start_mean - 0.5):
                return "plateau"

    # Wave: multiple local maxima
    local_maxima = [
        i for i in range(1, total - 1)
        if curve[i] > curve[i - 1] and curve[i] > curve[i + 1]
        and curve[i] >= mean_val + 1
    ]
    if len(local_maxima) >= 2:
        return "wave"

    # Mountain: default — has a meaningful rise and fall
    if peak_idx > total * 0.25 and peak_idx < total * 0.80:
        if end_mean < peak_val - 1.5:
            return "mountain"

    return "mountain"  # reasonable default


# ---------------------------------------------------------------------------
# Phase-level stats
# ---------------------------------------------------------------------------


def _phase_avg(seq: Sequence, phase: Phase) -> float:
    block = seq.get_phase(phase)
    if not block or not block.poses:
        return 0.0
    return statistics.mean(p.pose.intensity for p in block.poses)


# ---------------------------------------------------------------------------
# Public analyser
# ---------------------------------------------------------------------------


def analyze_arc(seq: Sequence) -> ArcReport:
    """
    Analyse the energy curve of a :class:`~yoga_engine.schema.Sequence`.

    Returns an :class:`~yoga_engine.schema.ArcReport` with curve data,
    arc shape classification, and annotated notes.
    """
    all_poses = seq.all_poses
    if not all_poses:
        return ArcReport(
            intensity_curve=[],
            phase_labels=[],
            peak_index=0,
            peak_intensity=0,
            warmup_plateau=0.0,
            cooldown_plateau=0.0,
            arc_shape="flat",
            notes=["Sequence is empty."],
        )

    curve: List[int] = []
    labels: List[str] = []

    for block in seq.phases:
        for inst in block.poses:
            curve.append(inst.pose.intensity)
            labels.append(f"{block.label}:{inst.pose.token}")

    peak_intensity = max(curve)
    peak_index = curve.index(peak_intensity)
    arc_shape = _classify_arc(curve)
    warmup_avg = _phase_avg(seq, Phase.WARMUP)
    cooldown_avg = _phase_avg(seq, Phase.COOLDOWN)

    notes: List[str] = []

    # Annotated notes — generic sequencing guidance
    if arc_shape == "mountain":
        notes.append("Arc is a classic mountain — gradual rise, clear peak, tapering descent.")
    elif arc_shape == "flat":
        notes.append("Arc is flat: the intensity barely varies. Consider adding more contrast.")
    elif arc_shape == "spike":
        notes.append(
            "Arc has a sharp spike: one high-intensity pose surrounded by much lower intensity. "
            "Build more gradually to the peak."
        )
    elif arc_shape == "plateau":
        notes.append(
            "Arc is a plateau: high intensity sustained for a long middle section. "
            "Ensure adequate recovery before cooldown."
        )
    elif arc_shape == "inverted":
        notes.append(
            "Arc is inverted: starts and ends high with a lower middle. "
            "This is unusual — confirm it is intentional."
        )
    elif arc_shape == "wave":
        notes.append(
            "Arc has multiple waves: two or more intensity peaks. "
            "Works for circuits or multi-theme classes; otherwise simplify."
        )

    # Check cooldown is actually lower than peak
    if cooldown_avg >= peak_intensity - 1:
        notes.append(
            "Cooldown intensity is close to peak level — the class may not wind down "
            "sufficiently before savasana."
        )

    # Check warmup doesn't start too high
    if warmup_avg >= 6:
        notes.append(
            "Warmup average intensity is 6+. Consider easing into the class more gently."
        )

    # Note if no cooldown data found
    if cooldown_avg == 0.0:
        notes.append("No cooldown phase data found; cooldown plateau reported as 0.")

    if seq.heated_room and arc_shape in ("spike", "plateau"):
        notes.append(
            "Heated class with a spike or plateau arc: insert explicit rest poses "
            "(DD, CB) to manage heat accumulation."
        )

    return ArcReport(
        intensity_curve=curve,
        phase_labels=labels,
        peak_index=peak_index,
        peak_intensity=peak_intensity,
        warmup_plateau=warmup_avg,
        cooldown_plateau=cooldown_avg,
        arc_shape=arc_shape,
        notes=notes,
    )
