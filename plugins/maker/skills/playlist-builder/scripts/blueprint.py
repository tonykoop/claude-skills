#!/usr/bin/env python3
"""
Sonic blueprint — per-week BPM scaling and energy ceilings.

Reads the shared SERIES_BLUEPRINT (baseline BPM ranges per phase) and
applies a week-specific scale factor + energy ceiling to a list of phases.
The result is a new list of phase dicts with `bpm_min`, `bpm_max`,
`energy_effective`, `bpm_scale`, and `energy_ceiling` added.

Usage as a module:
    from blueprint import BlueprintConfig, SERIES_BLUEPRINT

    cfg = BlueprintConfig.for_week(week=3, blueprint=SERIES_BLUEPRINT)
    scaled_phases = cfg.apply(episode["phases"])
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# Baseline BPM range per phase name (matches 4week-yoga-progression.json).
# Keys are matched case-insensitively / by substring.
_PHASE_BPM_BASELINE: dict[str, tuple[float, float]] = {
    "Opening / Centering": (60.0, 80.0),
    "Sun A (Rising)": (100.0, 118.0),
    "Sun B (Peak)": (118.0, 132.0),
    "Heart Opener": (100.0, 115.0),
    "Balance Series": (108.0, 120.0),
    "Cool Down (Descent)": (85.0, 105.0),
    "Savasana": (55.0, 72.0),
    "Savasana (Extended)": (55.0, 72.0),
}

_WEEK_CONFIG: dict[int, dict[str, Any]] = {
    1: {"bpm_scale": 1.00, "energy_ceiling": 7, "theme": "Rooting"},
    2: {"bpm_scale": 1.02, "energy_ceiling": 9, "theme": "Expanding"},
    3: {"bpm_scale": 1.03, "energy_ceiling": 9, "theme": "Refining"},
    4: {"bpm_scale": 0.98, "energy_ceiling": 8, "theme": "Integrating"},
}


def _bpm_baseline(phase_name: str) -> tuple[float, float] | None:
    """Return (min, max) BPM for a phase name, or None if unknown."""
    name_lower = phase_name.lower()
    for key, val in _PHASE_BPM_BASELINE.items():
        if key.lower() in name_lower or name_lower in key.lower():
            return val
    return None


# Exported singleton — callers may supply a custom dict instead.
SERIES_BLUEPRINT: dict[str, Any] = {
    "phase_bpm_baseline": _PHASE_BPM_BASELINE,
    "week_config": _WEEK_CONFIG,
}


@dataclass
class BlueprintConfig:
    week: int
    bpm_scale: float
    energy_ceiling: int
    theme: str
    blueprint: dict[str, Any]

    @classmethod
    def for_week(cls, week: int,
                 blueprint: dict[str, Any] | None = None) -> "BlueprintConfig":
        if blueprint is None:
            blueprint = SERIES_BLUEPRINT
        cfg = blueprint["week_config"].get(week)
        if cfg is None:
            raise ValueError(f"No blueprint config for week {week}. "
                             f"Valid weeks: {list(blueprint['week_config'])}")
        return cls(
            week=week,
            bpm_scale=cfg["bpm_scale"],
            energy_ceiling=cfg["energy_ceiling"],
            theme=cfg["theme"],
            blueprint=blueprint,
        )

    def apply(self, phases: list[dict]) -> list[dict]:
        """Return a new list of phase dicts with BPM and energy fields added."""
        result = []
        for phase in phases:
            p = dict(phase)
            baseline = _bpm_baseline(p.get("name", ""))
            if baseline is not None:
                p["bpm_min"] = round(baseline[0] * self.bpm_scale, 1)
                p["bpm_max"] = round(baseline[1] * self.bpm_scale, 1)
            p["energy_effective"] = min(p.get("energy", 10), self.energy_ceiling)
            p["bpm_scale"] = self.bpm_scale
            p["energy_ceiling"] = self.energy_ceiling
            result.append(p)
        return result
