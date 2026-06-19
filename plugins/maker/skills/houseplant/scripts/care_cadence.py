"""Watering + fertilizing CHECK-cadence engine for the chrono-horticultural module.

Completes the watering/fertilizing half of the Chrono-Horticultural Engine
(claude-skills#172). `wire_window.py` already covers wire-removal inspection
windows; this module turns a species growth-speed class + season/phase + heat
signal + recent stressors into calendar-ready **check** cadences — observation
loops ("check soil moisture every N days, water only when ...") rather than
fixed timers — plus a fertilizing cadence that suspends in dormancy and after a
repot. See references/chrono-engine.md; values mirror its growth-speed table.

Pure Python (no bpy) so it is unit-testable and importable. It can also be run
via exec() with caller-overridable globals (same contract as the other bundled
scripts):

    GROWTH_CLASS = "fast"           # fast | moderate | slow
    PHASE = "active_growth"         # active_growth | hardening | dormancy | repot_recovery
    HEAT = True                     # hot spell / balcony heat tightens watering checks
    STRESSORS = ["repot"]           # repot | root_reduction | hard_prune | defoliation | small_pot | free_draining
    exec(open(r"<path>/scripts/care_cadence.py").read())

Or import:
    from care_cadence import care_schedule
    plan = care_schedule("fast", phase="active_growth", heat=True)
"""
from __future__ import annotations

import json

# Growing-season watering CHECK cadence in days, per growth-speed class:
# (mild conditions, hot conditions). Representative values drawn from the ranges
# in references/chrono-engine.md ("every 1-2 days in heat, 3-4 days mild", etc.).
WATERING_CHECK_DAYS = {
    "fast":     {"mild": 3, "heat": 1},   # vigorous tropical (Ficus, Schefflera)
    "moderate": {"mild": 5, "heat": 2},   # Carmona, Chinese elm, most foliage
    "slow":     {"mild": 7, "heat": 4},   # pines, junipers, maples, succulents
}

# Fertilizing cadence (days) during ACTIVE growth only; suspended otherwise.
FERTILIZE_DAYS = {"fast": 14, "moderate": 21, "slow": 28}

# Phase multipliers applied to the watering-check cadence. Widen when cool/dim
# or dormant; tighten right after a repot (fresh roots, careful moisture).
PHASE_WATERING_FACTOR = {
    "active_growth": 1.0,
    "hardening": 1.3,
    "dormancy": 1.8,
    "repot_recovery": 0.7,
}

# Stressor multipliers on the watering-check cadence (<1 tightens = check more
# often). "repot"/"root_reduction" raise rot risk on fresh roots -> check more;
# small pots and free-draining substrate dry faster -> check more.
STRESSOR_WATERING_FACTOR = {
    "repot": 0.7,
    "root_reduction": 0.7,
    "hard_prune": 0.85,
    "defoliation": 0.85,
    "small_pot": 0.8,
    "free_draining": 0.8,
}

# Fertilizing is suspended for this many days after a repot/root reduction:
# fresh roots burn on fertilizer salts.
REPOT_FERTILIZE_SUSPEND_DAYS = 42

VALID_CLASSES = frozenset(WATERING_CHECK_DAYS)
VALID_PHASES = frozenset(PHASE_WATERING_FACTOR)


def _round_days(value: float) -> int:
    """Round to whole days, never below 1 (you can't check less than daily here)."""
    return max(1, round(value))


def _check_class(growth_class: str) -> None:
    if growth_class not in VALID_CLASSES:
        raise ValueError(f"growth_class must be one of {sorted(VALID_CLASSES)}, got {growth_class!r}")


def _check_phase(phase: str) -> None:
    if phase not in VALID_PHASES:
        raise ValueError(f"phase must be one of {sorted(VALID_PHASES)}, got {phase!r}")


def watering_check(growth_class, phase="active_growth", heat=False, stressors=()):
    """Calendar-ready watering CHECK cadence (an observation loop, not a timer)."""
    _check_class(growth_class)
    _check_phase(phase)
    base = WATERING_CHECK_DAYS[growth_class]["heat" if heat else "mild"]
    factor = PHASE_WATERING_FACTOR[phase]
    applied = []
    for s in stressors:
        if s in STRESSOR_WATERING_FACTOR:
            factor *= STRESSOR_WATERING_FACTOR[s]
            applied.append(s)
    cadence = _round_days(base * factor)
    cond = "while it stays hot" if heat else "in current conditions"
    return {
        "task": "watering",
        "cadence_days": cadence,
        "reminder": (
            f"Check soil moisture at root depth every {cadence} day(s) {cond}; "
            f"water only when the top 2-3 cm is dry and the pot feels light."
        ),
        "trigger": "top 2-3 cm dry AND pot noticeably lighter",
        "done_when": "water runs from the drainage holes, then resume checks",
        "applied_stressors": applied,
    }


def fertilizing_plan(growth_class, phase="active_growth", stressors=()):
    """Fertilizing cadence; suspended in dormancy and for a window after a repot."""
    _check_class(growth_class)
    _check_phase(phase)
    if "repot" in stressors or "root_reduction" in stressors:
        return {
            "task": "fertilizing",
            "cadence_days": None,
            "suspended": True,
            "resume_after_days": REPOT_FERTILIZE_SUSPEND_DAYS,
            "reminder": (
                f"Hold all fertilizer for ~{REPOT_FERTILIZE_SUSPEND_DAYS} days after a "
                f"repot/root reduction — fresh roots burn on fertilizer salts. "
                f"Resume a dilute feed once new growth appears."
            ),
        }
    if phase != "active_growth":
        return {
            "task": "fertilizing",
            "cadence_days": None,
            "suspended": True,
            "resume_after_days": None,
            "reminder": (
                f"Hold fertilizer outside active growth ({phase}); resume a dilute "
                f"feed when new growth resumes."
            ),
        }
    cadence = FERTILIZE_DAYS[growth_class]
    return {
        "task": "fertilizing",
        "cadence_days": cadence,
        "suspended": False,
        "resume_after_days": None,
        "reminder": (
            f"Feed a dilute balanced fertilizer about every {cadence} day(s) during "
            f"active growth; skip if the plant looks stressed or the soil is dry."
        ),
    }


def care_schedule(growth_class, phase="active_growth", heat=False, stressors=()):
    """Combined watering + fertilizing schedule, plus a wire-window pointer."""
    stressors = tuple(stressors or ())
    return {
        "growth_class": growth_class,
        "phase": phase,
        "heat": bool(heat),
        "stressors": list(stressors),
        "watering": watering_check(growth_class, phase, heat, stressors),
        "fertilizing": fertilizing_plan(growth_class, phase, stressors),
        "wire_removal": "for wire-removal inspection windows, use scripts/wire_window.py",
    }


# --- exec()-style entry point (caller-overridable globals) -------------------
if __name__ == "__main__" or "GROWTH_CLASS" in globals():
    _growth = globals().get("GROWTH_CLASS", "moderate")
    _phase = globals().get("PHASE", "active_growth")
    _heat = globals().get("HEAT", False)
    _stressors = globals().get("STRESSORS", [])
    print(json.dumps(care_schedule(_growth, _phase, _heat, _stressors), indent=2))
