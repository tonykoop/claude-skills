"""Compute wire-removal inspection windows for the chrono-horticultural engine.

Given the date wire was applied, the species growth-speed class, and whether
the plant is in active growth, return a first-inspection date and a recheck
cadence. Wire bites in as the branch thickens, and thickening rate is species-
and season-dependent, so we emit a *check window* rather than a fixed removal
date (see references/chrono-engine.md).

This module is pure Python (no bpy) so it is unit-testable and can also be run
or imported by the agent directly to produce calendar-ready inspection dates.

Usage as a script (globals overridable before exec):
    WIRED_DATE = "2026-06-15"
    GROWTH_CLASS = "fast"        # one of: fast, moderate, slow
    ACTIVE_GROWTH = True
    exec(open(r"<path>/scripts/wire_window.py").read())

Or import:
    from wire_window import wire_inspection_window
    plan = wire_inspection_window("2026-06-15", "fast", active_growth=True)
"""
from __future__ import annotations

import datetime

# Growth-speed class -> (first_inspection_days, recheck_cadence_days) during
# ACTIVE growth. These mirror the table in references/chrono-engine.md.
GROWTH_CLASS_WINDOWS = {
    "fast":     (7, 7),    # vigorous tropical (Ficus benjamina/microcarpa, Schefflera)
    "moderate": (14, 14),  # Carmona, Chinese elm, most foliage houseplants
    "slow":     (28, 21),  # pines, junipers, maples, succulents
}

# When the plant is NOT in active growth, cambium thickens slowly: stretch the
# windows. Multiplier applied to both first-inspection and recheck cadence.
DORMANT_STRETCH = 2.5


def _parse_date(d):
    if isinstance(d, datetime.date):
        return d
    return datetime.date.fromisoformat(str(d))


def wire_inspection_window(wired_date, growth_class="moderate", active_growth=True):
    """Return a dict describing when to inspect wired branches for bite-in.

    Args:
        wired_date: ISO date string ("YYYY-MM-DD") or datetime.date.
        growth_class: "fast", "moderate", or "slow".
        active_growth: True if the plant is actively growing (warm season).

    Returns:
        dict with first_inspection (date), recheck_cadence_days (int), and a
        list of up to four suggested inspection dates leading into removal.
    """
    gc = str(growth_class).lower()
    if gc not in GROWTH_CLASS_WINDOWS:
        raise ValueError(
            f"Unknown growth_class {growth_class!r}. "
            f"Allowed: {list(GROWTH_CLASS_WINDOWS)}"
        )
    first_days, recheck_days = GROWTH_CLASS_WINDOWS[gc]
    if not active_growth:
        first_days = int(round(first_days * DORMANT_STRETCH))
        recheck_days = int(round(recheck_days * DORMANT_STRETCH))

    start = _parse_date(wired_date)
    first = start + datetime.timedelta(days=first_days)
    # Suggest a short ladder of inspection dates the user can drop into a calendar.
    ladder = [first + datetime.timedelta(days=recheck_days * i) for i in range(4)]
    return {
        "wired_date": start.isoformat(),
        "growth_class": gc,
        "active_growth": bool(active_growth),
        "first_inspection_days": first_days,
        "first_inspection": first.isoformat(),
        "recheck_cadence_days": recheck_days,
        "inspection_ladder": [d.isoformat() for d in ladder],
        "guidance": (
            f"Inspect wired branches for bite-in starting {first.isoformat()}, "
            f"then every {recheck_days} days. Remove or reapply the moment the "
            f"bark begins to swell around the wire."
        ),
    }


WIRED_DATE = globals().get("WIRED_DATE")
GROWTH_CLASS = globals().get("GROWTH_CLASS", "moderate")
ACTIVE_GROWTH = globals().get("ACTIVE_GROWTH", True)

if WIRED_DATE:
    _plan = wire_inspection_window(WIRED_DATE, GROWTH_CLASS, ACTIVE_GROWTH)
    print("Wire-removal inspection window:")
    for k, v in _plan.items():
        print(f"  {k}: {v}")
