"""Tests for plant_care.bonsai — wire_reminders() and prune_recovery_status()."""
from __future__ import annotations

import datetime
import pytest

from plant_care.models import BonsaiExtras
from plant_care.bonsai import (
    PRUNE_RECOVERY_DAYS,
    WIRE_CHECK_THRESHOLD_DAYS,
    prune_recovery_status,
    wire_reminders,
)

TODAY = datetime.date(2026, 6, 19)


def days_ago(n: int) -> datetime.date:
    return TODAY - datetime.timedelta(days=n)


# ---------------------------------------------------------------------------
# wire_reminders()
# ---------------------------------------------------------------------------

def test_wire_applied_91_days_ago_reminder_triggered():
    """Wire applied 91 days ago (> 90-day threshold) → reminder returned."""
    extras = BonsaiExtras(wire_applied=days_ago(91))
    reminders = wire_reminders(extras, TODAY)
    assert len(reminders) == 1
    assert "cutting in" in reminders[0].lower() or "may be cutting" in reminders[0].lower()


def test_wire_applied_exactly_at_threshold_reminder_triggered():
    """Wire applied exactly 90 days ago → threshold reached, reminder triggered."""
    extras = BonsaiExtras(wire_applied=days_ago(WIRE_CHECK_THRESHOLD_DAYS))
    reminders = wire_reminders(extras, TODAY)
    assert len(reminders) == 1


def test_wire_applied_89_days_ago_no_reminder():
    """Wire applied 89 days ago (< 90-day threshold) → no reminder."""
    extras = BonsaiExtras(wire_applied=days_ago(89))
    reminders = wire_reminders(extras, TODAY)
    assert reminders == []


def test_no_wire_applied_no_reminder():
    """wire_applied is None → no reminder."""
    extras = BonsaiExtras(wire_applied=None)
    reminders = wire_reminders(extras, TODAY)
    assert reminders == []


def test_wire_reminder_mentions_applied_date():
    """Reminder string includes the applied date for traceability."""
    applied = days_ago(100)
    extras = BonsaiExtras(wire_applied=applied)
    reminders = wire_reminders(extras, TODAY)
    assert applied.isoformat() in reminders[0]


def test_wire_reminder_returns_list_of_strings():
    """Return type is always a list of strings."""
    extras = BonsaiExtras(wire_applied=days_ago(95))
    result = wire_reminders(extras, TODAY)
    assert isinstance(result, list)
    assert all(isinstance(r, str) for r in result)


# ---------------------------------------------------------------------------
# prune_recovery_status()
# ---------------------------------------------------------------------------

def test_prune_10_days_ago_in_recovery():
    """Pruned 10 days ago → in recovery window (4 days remaining)."""
    extras = BonsaiExtras(last_pruned=days_ago(10))
    status = prune_recovery_status(extras, TODAY)
    assert "In recovery window" in status
    assert "4 days remaining" in status


def test_prune_15_days_ago_recovery_complete():
    """Pruned 15 days ago (> 14-day window) → recovery complete."""
    extras = BonsaiExtras(last_pruned=days_ago(15))
    status = prune_recovery_status(extras, TODAY)
    assert status == "Recovery complete"


def test_prune_exactly_14_days_ago_recovery_complete():
    """Pruned exactly 14 days ago → window has elapsed, recovery complete."""
    extras = BonsaiExtras(last_pruned=days_ago(PRUNE_RECOVERY_DAYS))
    status = prune_recovery_status(extras, TODAY)
    assert status == "Recovery complete"


def test_prune_1_day_ago_in_recovery():
    """Pruned yesterday → in recovery window (13 days remaining)."""
    extras = BonsaiExtras(last_pruned=days_ago(1))
    status = prune_recovery_status(extras, TODAY)
    assert "In recovery window" in status
    assert "13 days remaining" in status


def test_no_prune_recovery_complete():
    """last_pruned is None → safe default: recovery complete."""
    extras = BonsaiExtras(last_pruned=None)
    status = prune_recovery_status(extras, TODAY)
    assert status == "Recovery complete"


def test_prune_today_in_recovery():
    """Pruned today → in recovery window (14 days remaining)."""
    extras = BonsaiExtras(last_pruned=TODAY)
    status = prune_recovery_status(extras, TODAY)
    assert "In recovery window" in status
    assert f"{PRUNE_RECOVERY_DAYS} days remaining" in status


# ---------------------------------------------------------------------------
# Combined BonsaiExtras state
# ---------------------------------------------------------------------------

def test_both_wire_and_prune_independent():
    """wire_reminders and prune_recovery_status are independent of each other."""
    extras = BonsaiExtras(
        wire_applied=days_ago(95),
        last_pruned=days_ago(5),
        nebari_notes="nebari developing nicely",
    )
    reminders = wire_reminders(extras, TODAY)
    recovery = prune_recovery_status(extras, TODAY)
    assert len(reminders) == 1  # wire past threshold
    assert "In recovery window" in recovery  # 9 days remaining
