"""
Movement Arts — polymorphic objective functions.

Each ObjectiveFn implements the selection strategy for a discipline.
The sequencer loads the right one from the domain's "objective" field
via load_objective(name), so no code change is needed to swap domains.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional


class ObjectiveFn(ABC):
    """
    Abstract base for objective functions.

    select_next is called each block; it receives the list of transition-valid
    primitives and the live tracker, and returns which primitive to emit next.

    score() is optional — callers may use it to evaluate a completed sequence.
    """

    @abstractmethod
    def select_next(self, valid_primitives: List[dict], tracker) -> Optional[dict]:
        ...

    def __call__(self, valid_primitives: List[dict], tracker) -> Optional[dict]:
        return self.select_next(valid_primitives, tracker)

    def score(self, sequence: List[dict], tracker_history: List[dict]) -> float:
        return 0.0


class StyleObjective(ObjectiveFn):
    """
    Dance objective — style_expression.

    Prefers variety (avoids immediate repetition) and energy moves that track
    the sigmoid intensity curve without bouncing.
    Tracks the last-selected primitive ID internally to avoid consecutive repeats.
    """

    def __init__(self) -> None:
        self._last_id: Optional[str] = None

    def select_next(self, valid_primitives: List[dict], tracker) -> Optional[dict]:
        if not valid_primitives:
            return None
        state = tracker.current_state
        intensity = state.get("intensity", 0.5)
        target = getattr(tracker, "_intensity_target", 0.5)

        candidates = [p for p in valid_primitives if p["id"] != self._last_id] or valid_primitives
        result = min(candidates, key=lambda p: abs((intensity + p.get("energy_delta", 0.0)) - target))
        self._last_id = result["id"]
        return result

    def score(self, sequence: List[dict], tracker_history: List[dict]) -> float:
        if len(sequence) < 2:
            return 0.0
        variety = len({b["primitive_id"] for b in sequence}) / len(sequence)
        return variety


class ForceObjective(ObjectiveFn):
    """
    Martial-arts objective — force_output.

    At peak intensity, prefers explosive/snap moves (via acceleration_curve).
    During ramp-up and cool-down, prefers sustained or flat curves.
    """

    _CURVE_WEIGHT = {
        "explosive": 1.0,
        "impact": 0.9,
        "snap": 0.8,
        "fast_finish": 0.6,
        "sustained": 0.4,
        "flat": 0.2,
    }

    def select_next(self, valid_primitives: List[dict], tracker) -> Optional[dict]:
        if not valid_primitives:
            return None
        state = tracker.current_state
        intensity = state.get("intensity", 0.5)
        best = None
        best_score = float("-inf")
        for p in valid_primitives:
            curve = p.get("acceleration_curve", "flat")
            force_weight = self._CURVE_WEIGHT.get(curve, 0.3)
            score = force_weight * intensity + p.get("energy_delta", 0.0)
            if score > best_score:
                best_score = score
                best = p
        return best or valid_primitives[0]

    def score(self, sequence: List[dict], tracker_history: List[dict]) -> float:
        if not sequence:
            return 0.0
        explosive_count = sum(
            1 for b in sequence if b.get("acceleration_curve") in {"explosive", "snap", "impact"}
        )
        return explosive_count / len(sequence)


class JointSafetyObjective(ObjectiveFn):
    """
    PT objective — joint_safety.

    Prefers moves with low velocity_cap.
    Penalises unilateral_load moves when weight distribution is already imbalanced
    to avoid overloading a compromised side.
    """

    _IMBALANCE_THRESHOLD = 0.35

    def select_next(self, valid_primitives: List[dict], tracker) -> Optional[dict]:
        if not valid_primitives:
            return None
        state = tracker.current_state
        weight = state.get("weight_distribution", {"left": 0.5, "right": 0.5})
        left_load = weight.get("left", 0.5)
        right_load = weight.get("right", 0.5)
        imbalance = abs(left_load - right_load)

        best = None
        best_score = float("-inf")
        for p in valid_primitives:
            vel = p.get("velocity_cap_m_per_s", 0.3)
            unilateral = p.get("unilateral_load", False)
            score = -vel
            if unilateral and imbalance > self._IMBALANCE_THRESHOLD:
                score -= 0.5
            if score > best_score:
                best_score = score
                best = p
        return best or valid_primitives[0]

    def score(self, sequence: List[dict], tracker_history: List[dict]) -> float:
        if not sequence:
            return 0.0
        max_vel = max(b.get("velocity_cap_m_per_s", 0.0) for b in sequence)
        return 1.0 - min(1.0, max_vel)


class BreathAlignmentObjective(ObjectiveFn):
    """
    Yoga / tai chi objective — breath_alignment.

    Follows the breath arc with minimal energy variance per block,
    producing a smooth inhale-to-exhale flow.
    """

    def select_next(self, valid_primitives: List[dict], tracker) -> Optional[dict]:
        if not valid_primitives:
            return None
        state = tracker.current_state
        intensity = state.get("intensity", 0.5)
        target = getattr(tracker, "_intensity_target", intensity)
        return min(
            valid_primitives,
            key=lambda p: abs((intensity + p.get("energy_delta", 0.0)) - target),
        )

    def score(self, sequence: List[dict], tracker_history: List[dict]) -> float:
        if len(tracker_history) < 2:
            return 1.0
        deltas = [
            abs(tracker_history[i]["intensity"] - tracker_history[i - 1]["intensity"])
            for i in range(1, len(tracker_history))
        ]
        smoothness = 1.0 - min(1.0, sum(deltas) / len(deltas) * 10)
        return max(0.0, smoothness)


# ---------------------------------------------------------------------------
# Registry and factory
# ---------------------------------------------------------------------------

_OBJECTIVE_REGISTRY: dict[str, type] = {
    "style_expression": StyleObjective,
    "force_output": ForceObjective,
    "joint_safety": JointSafetyObjective,
    "breath_alignment": BreathAlignmentObjective,
}


def load_objective(name: str) -> ObjectiveFn:
    """
    Instantiate an ObjectiveFn by domain objective name.

    Parameters
    ----------
    name : str
        One of: style_expression, force_output, joint_safety, breath_alignment.

    Raises
    ------
    ValueError
        If name is not registered.
    """
    cls = _OBJECTIVE_REGISTRY.get(name)
    if cls is None:
        raise ValueError(
            f"Unknown objective '{name}'. Valid: {sorted(_OBJECTIVE_REGISTRY)}"
        )
    return cls()
