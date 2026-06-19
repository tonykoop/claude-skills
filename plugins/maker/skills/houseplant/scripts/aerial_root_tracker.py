#!/usr/bin/env python3
"""Aerial-root lifecycle + intervention gate + thickening forecast (#174).

The aerial-roots/nebari reference (`references/aerial-roots-nebari.md`) defines
the lifecycle (`tip_promising -> guided -> reached_soil -> thickening -> fused`,
or `-> failed`), a health-and-warmth gate on interventions, and a thickening /
time-to-fused estimate. `aerial_root_trace.py` draws the guided path in Blender
and stamps a state; this script makes the *decision* parts deterministic and
testable (no Blender), mirroring propagation_tracker.py / wire_window.py:

  * **Lifecycle** — validate/advance the aerial-root state machine.
  * **Intervention gate** — suggest sphagnum / tube-guide / humidity-tent only
    when the plant is healthy AND warm enough for active growth (per the
    reference); otherwise hold.
  * **Thickening forecast** — estimate the *remaining* time-to-fused as a window
    (a range, never a single date) with explicit confidence, from the current
    state + species growth class + conditions.

Pure stdlib; no Blender. Run via exec() with caller-overridable globals, or
import the functions, or pass JSON on the CLI.

    STATE = "guided"               # tip_promising|guided|reached_soil|thickening|fused
    GROWTH_CLASS = "fast"          # fast|moderate|slow
    CONDITION = "warm"             # warm|neutral|cool
    HEALTHY = True
    WARM = True
    exec(open(r"<path>/scripts/aerial_root_tracker.py").read())
"""
from __future__ import annotations

import datetime
import json

LIFECYCLE = ["tip_promising", "guided", "reached_soil", "thickening", "fused"]
TERMINAL = {"failed"}

# Total tip->fused baseline (min_days, max_days) by growth-speed class. Aerial
# roots fusing into structural trunk wood is slow — months to over a year — and
# strongly species/vigor dependent. These are deliberately wide heuristics.
FUSE_BASELINE_DAYS: dict[str, tuple[int, int]] = {
    "fast": (180, 365),     # vigorous tropical (Ficus benjamina/microcarpa)
    "moderate": (365, 730),
    "slow": (730, 1460),
}
# Ficus aerial roots are unusually vigorous — they fuse faster than the generic
# fast-class baseline.
SPECIES_TUNING: dict[str, float] = {"ficus": 0.8}
CONDITION_FACTOR = {"warm": 0.85, "neutral": 1.0, "cool": 1.2}

# Fraction of the total tip->fused timeline still REMAINING at the entry of each
# state. Used to scale the baseline into a remaining-time window.
REMAINING_FRACTION = {
    "tip_promising": 1.0,
    "guided": 0.8,
    "reached_soil": 0.55,
    "thickening": 0.3,
    "fused": 0.0,
}

# Intervention suggested at each state when the plant is healthy + warm.
INTERVENTIONS = {
    "tip_promising": "mist the tip and raise local humidity (humidity tent) to coax the aerial root to extend",
    "guided": "apply a straw/tube guide or sphagnum wrap to steer the root toward the substrate",
    "reached_soil": "secure the contact point and keep the substrate evenly moist so the tip establishes",
    "thickening": "remove any guide that could girdle the root; give it light and airflow to thicken",
    "fused": "structural now — treat as trunk/nebari; no further guidance needed",
}


# --- lifecycle --------------------------------------------------------------
def is_terminal(state: str) -> bool:
    return state in TERMINAL or state == LIFECYCLE[-1]


def next_state(state: str) -> str:
    if state in TERMINAL:
        raise ValueError(f"{state!r} is terminal; no next state")
    if state not in LIFECYCLE:
        raise ValueError(f"unknown state {state!r}")
    idx = LIFECYCLE.index(state)
    if idx == len(LIFECYCLE) - 1:
        raise ValueError(f"{state!r} is already the final state")
    return LIFECYCLE[idx + 1]


def valid_transition(src: str, dst: str) -> bool:
    if dst == "failed":
        return src in LIFECYCLE and src != "fused"  # can fail until fused
    try:
        return next_state(src) == dst
    except ValueError:
        return False


# --- intervention gate ------------------------------------------------------
def intervention_for(state: str, healthy: bool = True, warm: bool = True) -> dict:
    """Suggest an intervention, gated on plant health + warmth (active growth)."""
    if state in TERMINAL:
        return {"state": state, "act": False,
                "guidance": "aerial root failed/aborted — log the cause; no intervention"}
    if state not in LIFECYCLE:
        raise ValueError(f"unknown state {state!r}")
    if not (healthy and warm):
        reason = []
        if not healthy:
            reason.append("plant not healthy")
        if not warm:
            reason.append("not warm enough for active growth")
        return {
            "state": state, "act": False,
            "guidance": f"HOLD interventions ({' and '.join(reason)}) — only guide aerial "
                        f"roots on a healthy plant in warm active growth",
        }
    return {"state": state, "act": True, "guidance": INTERVENTIONS[state]}


# --- thickening / time-to-fused forecast ------------------------------------
def _parse_date(d):
    if isinstance(d, datetime.date):
        return d
    return datetime.date.fromisoformat(d)


def thickening_forecast(state: str, growth_class: str, condition: str = "neutral",
                        species: str = "", from_date: str | None = None) -> dict:
    """Remaining time-to-fused as a window (range) with explicit confidence."""
    if state in TERMINAL:
        return {"state": state, "fused": False, "confidence": "n/a",
                "note": "terminal state; no forecast"}
    if state == "fused":
        return {"state": state, "fused": True, "confidence": "high",
                "note": "already fused/structural"}
    if growth_class not in FUSE_BASELINE_DAYS:
        raise ValueError(f"growth_class must be one of {sorted(FUSE_BASELINE_DAYS)}")
    lo, hi = FUSE_BASELINE_DAYS[growth_class]
    factor = CONDITION_FACTOR.get(condition, 1.0) * SPECIES_TUNING.get(species.lower(), 1.0)
    frac = REMAINING_FRACTION[state]
    lo_d = round(lo * factor * frac)
    hi_d = round(hi * factor * frac)
    # Confidence is intrinsically low this far out; a little better once thickening.
    confidence = "medium" if state in ("thickening", "reached_soil") else "low"
    out = {
        "state": state,
        "growth_class": growth_class,
        "condition": condition,
        "remaining_days_min": lo_d,
        "remaining_days_max": hi_d,
        "confidence": confidence,
        "note": "time-to-fused is a wide estimate; aerial-root fusion is slow and observation-driven",
    }
    if from_date:
        base = _parse_date(from_date)
        out["window_start"] = (base + datetime.timedelta(days=lo_d)).isoformat()
        out["window_end"] = (base + datetime.timedelta(days=hi_d)).isoformat()
    return out


def track(state: str, growth_class: str = "fast", condition: str = "neutral",
          species: str = "", healthy: bool = True, warm: bool = True,
          from_date: str | None = None) -> dict:
    """Combined lifecycle + intervention + forecast view for one aerial root."""
    return {
        "state": state,
        "is_terminal": is_terminal(state),
        "next_state": (None if is_terminal(state) else next_state(state)),
        "intervention": intervention_for(state, healthy, warm),
        "forecast": thickening_forecast(state, growth_class, condition, species, from_date),
    }


# --- CLI / exec entry point -------------------------------------------------
def main(argv: list | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Aerial-root lifecycle + forecast (#174)")
    ap.add_argument("--state", default="guided")
    ap.add_argument("--growth-class", default="fast")
    ap.add_argument("--condition", default="neutral")
    ap.add_argument("--species", default="")
    ap.add_argument("--from-date", default=None)
    ap.add_argument("--unhealthy", action="store_true")
    ap.add_argument("--cool", action="store_true")
    args = ap.parse_args(argv)
    out = track(args.state, args.growth_class, args.condition, args.species,
                healthy=not args.unhealthy, warm=not args.cool, from_date=args.from_date)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__" or "STATE" in globals():
    if "STATE" in globals():
        _out = track(
            globals().get("STATE", "guided"),
            globals().get("GROWTH_CLASS", "fast"),
            globals().get("CONDITION", "neutral"),
            globals().get("SPECIES", ""),
            healthy=globals().get("HEALTHY", True),
            warm=globals().get("WARM", True),
            from_date=globals().get("FROM_DATE"),
        )
        print(json.dumps(_out, indent=2))
    else:
        raise SystemExit(main())
