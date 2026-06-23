"""
Movement state tracker — domain-agnostic.

Holds: weight_distribution, facing_direction, clock_beat, intensity.
Call apply_primitive(p) after every sequenced block to advance state.
"""

from __future__ import annotations
import argparse
import json
import math
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional


@dataclass
class TrackerState:
    weight_distribution: Dict[str, float] = field(
        default_factory=lambda: {"left": 0.5, "right": 0.5}
    )
    facing_direction: str = "north"
    clock_beat: int = 0
    intensity: float = 0.0

    def snapshot(self) -> dict:
        return asdict(self)


VALID_FACING = {"north", "south", "east", "west", "any"}
VALID_WEIGHT_SHIFTS = {"left", "right", "bilateral", "unweighted"}


class MovementTracker:
    """Tracks physical state across a movement sequence."""

    def __init__(self, initial_intensity: float = 0.0):
        self._state = TrackerState(intensity=initial_intensity)
        self._history: list[dict] = []

    @property
    def current_state(self) -> dict:
        return self._state.snapshot()

    @property
    def history(self) -> list[dict]:
        return list(self._history)

    def apply_primitive(self, primitive: dict) -> dict:
        """
        Advance tracker state by applying a movement primitive.

        primitive keys used:
          weight_shift: "left" | "right" | "bilateral" | "unweighted"
          facing: "north" | "south" | "east" | "west" | "any"
          energy_delta: float (+/- change in intensity, clamped 0..1)
          duration_beats: int (optional, advance clock_beat)
        """
        self._history.append(self._state.snapshot())

        ws = primitive.get("weight_shift", "bilateral")
        if ws == "left":
            self._state.weight_distribution = {"left": 1.0, "right": 0.0}
        elif ws == "right":
            self._state.weight_distribution = {"left": 0.0, "right": 1.0}
        elif ws == "bilateral":
            self._state.weight_distribution = {"left": 0.5, "right": 0.5}
        elif ws == "unweighted":
            self._state.weight_distribution = {"left": 0.0, "right": 0.0}

        facing = primitive.get("facing", "any")
        if facing != "any":
            self._state.facing_direction = facing

        delta = float(primitive.get("energy_delta", 0.0))
        self._state.intensity = max(0.0, min(1.0, self._state.intensity + delta))

        beats = int(primitive.get("duration_beats", 1))
        self._state.clock_beat += beats

        return self._state.snapshot()

    def reset(self):
        self._history.append(self._state.snapshot())
        self._state = TrackerState(intensity=0.0)

    def __repr__(self) -> str:
        s = self._state
        return (
            f"MovementTracker(intensity={s.intensity:.2f}, "
            f"weight={s.weight_distribution}, "
            f"facing={s.facing_direction}, "
            f"beat={s.clock_beat})"
        )


# ---------------------------------------------------------------------------
# Clocks
# ---------------------------------------------------------------------------

class BreathClock:
    """Breath-cycle clock (yoga / tai chi / PT). Tick unit = one breath."""

    def __init__(self, breaths_per_minute: float = 12.0):
        self.bpm = breaths_per_minute
        self._beats = 0

    def tick(self, seconds: float) -> int:
        beats = int(seconds / (60.0 / self.bpm))
        self._beats += beats
        return beats

    @property
    def total_beats(self) -> int:
        return self._beats

    def __repr__(self) -> str:
        return f"BreathClock(bpm={self.bpm}, total_beats={self._beats})"


class BeatClock:
    """Musical-meter clock (dance / hip-hop / ballet). Tick unit = one count."""

    def __init__(self, bpm: float = 100.0, count_unit: int = 8):
        self.bpm = bpm
        self.count_unit = count_unit
        self._beats = 0

    def tick(self, seconds: float) -> int:
        beats = int(seconds / (60.0 / self.bpm))
        self._beats += beats
        return beats

    @property
    def total_beats(self) -> int:
        return self._beats

    @property
    def phrases(self) -> int:
        return self._beats // self.count_unit

    def __repr__(self) -> str:
        return f"BeatClock(bpm={self.bpm}, count_unit={self.count_unit}, total_beats={self._beats})"


def clock_for_domain(domain_meta: dict):
    """Factory: return the right clock for a domain's clock spec."""
    spec = domain_meta.get("clock", {})
    clock_type = spec.get("type", "breath")
    if clock_type == "beat":
        bpm_range = spec.get("bpm_range", [100, 120])
        bpm = (bpm_range[0] + bpm_range[1]) / 2
        return BeatClock(bpm=bpm, count_unit=spec.get("count_unit", 8))
    else:
        return BreathClock(breaths_per_minute=spec.get("breaths_per_minute", 12))


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

def _demo():
    tracker = MovementTracker()
    primitives = [
        {"id": "mountain", "weight_shift": "bilateral", "facing": "north", "energy_delta": 0.05, "duration_beats": 4},
        {"id": "warrior_ii", "weight_shift": "left", "facing": "east", "energy_delta": 0.1, "duration_beats": 8},
        {"id": "side_angle", "weight_shift": "left", "facing": "east", "energy_delta": 0.05, "duration_beats": 8},
        {"id": "downward_dog", "weight_shift": "bilateral", "facing": "any", "energy_delta": -0.05, "duration_beats": 4},
    ]
    history = []
    for p in primitives:
        state = tracker.apply_primitive(p)
        history.append({"primitive": p["id"], "state": state})
    return {"tracker": repr(tracker), "history": history}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="movement-arts tracker demo")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.demo:
        result = _demo()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result["tracker"])
            for h in result["history"]:
                print(f"  {h['primitive']}: intensity={h['state']['intensity']:.2f} weight={h['state']['weight_distribution']} facing={h['state']['facing_direction']}")
