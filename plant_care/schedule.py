"""Schedule engine: compute due and overdue care actions.

next_actions() is a pure function — it takes a frozen view of the specimen,
its care profile, the full history, and an explicit today date. No real-clock
calls, so tests are fully deterministic and the agent can inject any date.
"""
from __future__ import annotations

import datetime
from typing import Optional

from .models import CareEvent, CareProfile, DueAction, Specimen

# Action types driven by the interval-based scheduling logic.
_SCHEDULED_ACTIONS = ["water", "fertilize"]


def _last_event(history: list[CareEvent], action_type: str) -> Optional[datetime.date]:
    """Return the most-recent event date for the given action type, or None."""
    dates = [ev.date for ev in history if ev.type == action_type]
    return max(dates) if dates else None


def next_actions(
    specimen: Specimen,
    profile: CareProfile,
    history: list[CareEvent],
    today: datetime.date,
) -> list[DueAction]:
    """Return all care actions that are due or overdue today.

    Args:
        specimen:  The target plant (used for identity; extensible for per-plant
                   overrides in future slices).
        profile:   Care intervals for the specimen's species/conditions.
        history:   Full list of recorded care events for this specimen.
        today:     The reference date (injected; never calls datetime.date.today()).

    Returns:
        List of DueAction objects sorted by days_overdue descending (most
        overdue first). Actions that are not yet due are excluded.
    """
    intervals: dict[str, int] = {
        "water": profile.watering_interval_days,
        "fertilize": profile.fertilize_interval_days,
    }

    due: list[DueAction] = []
    for action_type, interval in intervals.items():
        last = _last_event(history, action_type)
        if last is None:
            # Never performed: due today.
            due_date = today
        else:
            due_date = last + datetime.timedelta(days=interval)

        if due_date <= today:
            days_overdue = (today - due_date).days
            # Priority: more overdue = higher priority number.
            priority = days_overdue
            due.append(
                DueAction(
                    action_type=action_type,
                    due_date=due_date,
                    days_overdue=days_overdue,
                    priority=priority,
                )
            )

    # Sort most-overdue first.
    due.sort(key=lambda a: a.days_overdue, reverse=True)
    return due
