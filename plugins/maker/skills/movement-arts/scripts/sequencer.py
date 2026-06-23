"""
Movement Arts — core sequencer.

MovementSequencer(domain, objective_fn, clock) → .compile(duration_min) → CompiledRoutine

The engine is domain-agnostic. Swap the domain JSON and objective function;
the arc logic (intensity curve, block transitions, state tracking) stays fixed.
"""

from __future__ import annotations
import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List, Optional

# Allow running as a script from the repo root
_HERE = os.path.dirname(__file__)
sys.path.insert(0, _HERE)

from tracker import MovementTracker, BreathClock, BeatClock, clock_for_domain


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Block:
    primitive_id: str
    primitive_name: str
    duration_s: float
    energy: float
    cue_density: str
    weight_shift: str
    facing: str
    domain: str


@dataclass
class CompiledRoutine:
    domain: str
    duration_min: float
    clock_type: str
    objective: str
    blocks: List[Block]
    tracker_final_state: dict

    def to_dict(self) -> dict:
        d = asdict(self)
        d["blocks"] = [asdict(b) for b in self.blocks]
        return d


# ---------------------------------------------------------------------------
# Intensity curve
# ---------------------------------------------------------------------------

def sigmoid_intensity(t_norm: float, steepness: float = 6.0) -> float:
    """
    t_norm in [0, 1] → intensity [0, 1] following a bell curve.
    Peaks at t=0.6 (late-class peak), falls off toward cooldown.
    """
    peak = 0.6
    if t_norm <= peak:
        return 1 / (1 + math.exp(-steepness * (t_norm / peak - 0.5)))
    else:
        decay = (t_norm - peak) / (1.0 - peak)
        return max(0.0, 1.0 - decay * 0.85)


CUE_DENSITY_THRESHOLDS = [
    (0.0, 0.2, "sparse"),
    (0.2, 0.5, "moderate"),
    (0.5, 0.75, "rhythmic"),
    (0.75, 0.9, "focused"),
    (0.9, 1.01, "minimal"),
]


def intensity_to_cue_density(intensity: float) -> str:
    for lo, hi, label in CUE_DENSITY_THRESHOLDS:
        if lo <= intensity < hi:
            return label
    return "minimal"


# ---------------------------------------------------------------------------
# Sequencer
# ---------------------------------------------------------------------------

class MovementSequencer:
    """
    Compiles a movement routine from a domain library.

    Parameters
    ----------
    domain : dict
        Parsed domain JSON (or None for demo mode).
    objective_fn : callable, optional
        Function (valid_primitives, tracker) → primitive dict.
        Defaults to round-robin selection.
    clock : BreathClock | BeatClock, optional
        Derived from domain metadata if not provided.
    """

    def __init__(
        self,
        domain: Optional[dict] = None,
        objective_fn: Optional[Callable] = None,
        clock=None,
    ):
        self._domain = domain or {}
        self._primitives: List[dict] = self._domain.get("primitives", [])
        self._domain_name: str = self._domain.get("domain", "unknown")
        self._objective_name: str = self._domain.get("objective", "none")
        self._requires_clinical_review: bool = self._domain.get("requires_clinical_review", False)

        self._clock = clock or (
            clock_for_domain(self._domain) if self._domain else BreathClock()
        )
        self._objective_fn = objective_fn or self._default_select

        self._tracker = MovementTracker()
        self._cursor = 0

    # ------------------------------------------------------------------
    # Default primitive selector — round-robin over valid_next chain
    # ------------------------------------------------------------------

    def _default_select(self, valid_primitives: List[dict], tracker: MovementTracker) -> Optional[dict]:
        if not valid_primitives:
            return None
        state = tracker.current_state
        prim_map = {p["id"]: p for p in self._primitives}

        # prefer primitives whose energy_delta moves intensity toward target
        intensity = state["intensity"]
        best = None
        best_score = float("inf")
        for p in valid_primitives:
            delta = p.get("energy_delta", 0.0)
            # we'll set target from outside via compile(); use 0.5 as neutral
            target = getattr(self, "_intensity_target", 0.5)
            score = abs((intensity + delta) - target)
            if score < best_score:
                best_score = score
                best = p
        return best or valid_primitives[0]

    # ------------------------------------------------------------------
    # Main compile
    # ------------------------------------------------------------------

    def compile(self, duration_min: float, safety_acknowledged: bool = False) -> CompiledRoutine:
        """
        Build a sequence filling `duration_min` minutes.

        Raises
        ------
        PermissionError
            If the domain requires clinical review and safety_acknowledged is False.
        ValueError
            If no primitives are available (use demo mode instead).
        """
        if self._requires_clinical_review and not safety_acknowledged:
            raise PermissionError(
                "The physical_therapy domain requires safety_acknowledged=True. "
                "Confirm the user understands this is an informational movement "
                "pattern library, not a clinical rehabilitation protocol."
            )

        if not self._primitives:
            raise ValueError(
                "No primitives loaded. Use --demo for a synthetic demo sequence, "
                "or supply a domain JSON file with 'primitives'."
            )

        total_s = duration_min * 60.0
        elapsed_s = 0.0
        blocks: List[Block] = []
        prim_map = {p["id"]: p for p in self._primitives}

        # Start with the first primitive
        current_prim = self._primitives[0]

        while elapsed_s < total_s:
            t_norm = elapsed_s / total_s
            target_intensity = sigmoid_intensity(t_norm)
            self._intensity_target = target_intensity

            # Determine duration for this block (30–120s based on intensity)
            block_s = max(30.0, min(120.0, 90.0 - target_intensity * 60.0))
            if elapsed_s + block_s > total_s:
                block_s = total_s - elapsed_s
            if block_s < 5.0:
                break

            # Compute valid next maneuvers
            valid_next_ids = current_prim.get("valid_next", [])
            if valid_next_ids:
                valid_next = [prim_map[i] for i in valid_next_ids if i in prim_map]
            else:
                valid_next = self._primitives

            # Select next primitive via objective function
            next_prim = self._objective_fn(valid_next, self._tracker)
            if next_prim is None:
                break

            # Apply to tracker
            beats = self._clock.tick(block_s)
            prim_with_beats = dict(next_prim)
            prim_with_beats["duration_beats"] = beats
            state = self._tracker.apply_primitive(prim_with_beats)

            energy = state["intensity"]
            block = Block(
                primitive_id=next_prim["id"],
                primitive_name=next_prim.get("name", next_prim["id"]),
                duration_s=round(block_s, 1),
                energy=round(energy, 3),
                cue_density=intensity_to_cue_density(energy),
                weight_shift=next_prim.get("weight_shift", "bilateral"),
                facing=next_prim.get("facing", "any"),
                domain=self._domain_name,
            )
            blocks.append(block)
            elapsed_s += block_s
            current_prim = next_prim

        return CompiledRoutine(
            domain=self._domain_name,
            duration_min=duration_min,
            clock_type=type(self._clock).__name__,
            objective=self._objective_name,
            blocks=blocks,
            tracker_final_state=self._tracker.current_state,
        )


# ---------------------------------------------------------------------------
# Demo mode — synthetic primitives, no domain file needed
# ---------------------------------------------------------------------------

_DEMO_PRIMITIVES = [
    {"id": "neutral_stand", "name": "Neutral Stand", "weight_shift": "bilateral", "facing": "north", "energy_delta": 0.02, "valid_next": ["step_touch", "wide_squat"]},
    {"id": "step_touch", "name": "Step Touch", "weight_shift": "left", "facing": "north", "energy_delta": 0.08, "valid_next": ["wide_squat", "isolations", "neutral_stand"]},
    {"id": "wide_squat", "name": "Wide Squat", "weight_shift": "bilateral", "facing": "north", "energy_delta": 0.1, "valid_next": ["isolations", "step_touch", "pivot_step"]},
    {"id": "isolations", "name": "Isolations", "weight_shift": "bilateral", "facing": "north", "energy_delta": 0.05, "valid_next": ["pivot_step", "wide_squat", "step_touch"]},
    {"id": "pivot_step", "name": "Pivot Step", "weight_shift": "right", "facing": "east", "energy_delta": 0.12, "valid_next": ["isolations", "wide_squat", "cooldown_sway"]},
    {"id": "cooldown_sway", "name": "Cooldown Sway", "weight_shift": "bilateral", "facing": "north", "energy_delta": -0.15, "valid_next": ["neutral_stand", "cooldown_sway"]},
]

_DEMO_DOMAIN = {
    "domain": "demo",
    "clock": {"type": "beat", "bpm_range": [100, 110], "count_unit": 8},
    "objective": "style_expression",
    "primitives": _DEMO_PRIMITIVES,
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="movement-arts sequencer")
    parser.add_argument("--demo", action="store_true", help="use built-in demo primitives")
    parser.add_argument("--domain", help="path to a domain JSON file")
    parser.add_argument("--duration", type=float, default=60.0, help="duration in minutes")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    parser.add_argument("--safety-acknowledged", action="store_true",
                        help="acknowledge PT clinical review gate")
    args = parser.parse_args()

    if args.demo:
        domain = _DEMO_DOMAIN
    elif args.domain:
        with open(args.domain) as f:
            domain = json.load(f)
    else:
        print("Provide --demo or --domain <path>", file=sys.stderr)
        sys.exit(1)

    seq = MovementSequencer(domain=domain)
    routine = seq.compile(args.duration, safety_acknowledged=args.safety_acknowledged)

    if args.json:
        print(json.dumps(routine.to_dict(), indent=2))
    else:
        print(f"Domain: {routine.domain} | Duration: {routine.duration_min}m | Clock: {routine.clock_type}")
        print(f"Objective: {routine.objective} | Blocks: {len(routine.blocks)}")
        for b in routine.blocks:
            print(f"  [{b.cue_density:9s}] {b.primitive_name:25s} {b.duration_s:5.0f}s  energy={b.energy:.2f}")
        s = routine.tracker_final_state
        print(f"\nFinal state: intensity={s['intensity']:.2f} weight={s['weight_distribution']} beat={s['clock_beat']}")


if __name__ == "__main__":
    main()
