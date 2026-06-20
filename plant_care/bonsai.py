"""Bonsai training-state utilities: wire reminders and prune-recovery windows.

Both functions are pure Python, no I/O, no real-clock calls — all date logic
is driven by the BonsaiExtras record and an explicit today argument so tests
remain fully deterministic.
"""
from __future__ import annotations

import datetime

from .models import BonsaiExtras

# Wire inspection threshold: after this many days the coil may be biting in.
WIRE_CHECK_THRESHOLD_DAYS = 90

# Prune recovery window: during this period the specimen should not receive
# additional major interventions.
PRUNE_RECOVERY_DAYS = 14


def wire_reminders(extras: BonsaiExtras, today: datetime.date) -> list[str]:
    """Return a list of reminder strings about wire coils that may need checking.

    Logic:
      - If wire_applied is set and today >= wire_applied + WIRE_CHECK_THRESHOLD_DAYS,
        emit a warning that the wire may be cutting into the bark.
      - If wire was applied but the threshold is not yet reached, no reminder.
      - If wire_applied is None, no reminder.

    Args:
        extras:  Bonsai-specific training state.
        today:   Reference date (injected; never calls datetime.date.today()).

    Returns:
        List of human-readable reminder strings (empty if no action needed).
    """
    if extras.wire_applied is None:
        return []

    check_date = extras.wire_applied + datetime.timedelta(days=WIRE_CHECK_THRESHOLD_DAYS)
    if today >= check_date:
        days_since = (today - extras.wire_applied).days
        return [
            f"Wire check due: wire applied {extras.wire_applied.isoformat()} "
            f"({days_since} days ago) — may be cutting in. "
            "Inspect bark around coils and remove or reapply before scarring occurs."
        ]
    return []


def prune_recovery_status(extras: BonsaiExtras, today: datetime.date) -> str:
    """Return a plain-language prune-recovery status string.

    Logic:
      - If last_pruned is None: "Recovery complete" (safe default — no known prune).
      - If today < last_pruned + PRUNE_RECOVERY_DAYS: "In recovery window (N days remaining)".
      - Otherwise: "Recovery complete".

    Args:
        extras:  Bonsai-specific training state.
        today:   Reference date (injected; never calls datetime.date.today()).

    Returns:
        A human-readable status string.
    """
    if extras.last_pruned is None:
        return "Recovery complete"

    recovery_end = extras.last_pruned + datetime.timedelta(days=PRUNE_RECOVERY_DAYS)
    if today < recovery_end:
        days_remaining = (recovery_end - today).days
        return f"In recovery window ({days_remaining} days remaining)"
    return "Recovery complete"
