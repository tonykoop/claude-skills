"""Tests for plant_care.schedule — next_actions() scheduling logic.

All tests inject an explicit `today` date so there is no dependency on the
system clock. The specimen object is a minimal fixture; scheduling logic does
not currently branch on specimen attributes.
"""
from __future__ import annotations

import datetime
import pytest

from plant_care.models import CareEvent, CareProfile, Specimen
from plant_care.schedule import next_actions


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def specimen():
    return Specimen(
        id="sp-001",
        species="Ficus benjamina",
        acquired=datetime.date(2024, 1, 1),
        location="living-room-east",
        light_level="bright-indirect",
        pot_size="8in",
        is_bonsai=False,
    )


@pytest.fixture
def profile():
    """7-day watering, 14-day fertilizing."""
    return CareProfile(
        watering_interval_days=7,
        fertilize_interval_days=14,
        light_needs="bright-indirect",
        humidity="moderate",
    )


TODAY = datetime.date(2026, 6, 19)


def make_event(action_type: str, days_ago: int) -> CareEvent:
    return CareEvent(type=action_type, date=TODAY - datetime.timedelta(days=days_ago))


# ---------------------------------------------------------------------------
# No-history tests
# ---------------------------------------------------------------------------

def test_no_history_water_due_today(specimen, profile):
    """With no prior water event, watering is due today."""
    actions = next_actions(specimen, profile, [], TODAY)
    types = [a.action_type for a in actions]
    assert "water" in types


def test_no_history_fertilize_due_today(specimen, profile):
    """With no prior fertilize event, fertilizing is due today."""
    actions = next_actions(specimen, profile, [], TODAY)
    types = [a.action_type for a in actions]
    assert "fertilize" in types


def test_no_history_both_due(specimen, profile):
    """With no history at all, both water and fertilize are due."""
    actions = next_actions(specimen, profile, [], TODAY)
    assert len(actions) == 2


def test_no_history_days_overdue_is_zero(specimen, profile):
    """No-history actions are due today, so days_overdue == 0."""
    actions = next_actions(specimen, profile, [], TODAY)
    for a in actions:
        assert a.days_overdue == 0


# ---------------------------------------------------------------------------
# Exactly on due date
# ---------------------------------------------------------------------------

def test_water_due_exactly_on_interval(specimen, profile):
    """Watered exactly 7 days ago → due today, days_overdue == 0."""
    history = [make_event("water", 7)]
    actions = next_actions(specimen, profile, history, TODAY)
    water_actions = [a for a in actions if a.action_type == "water"]
    assert len(water_actions) == 1
    assert water_actions[0].days_overdue == 0


def test_fertilize_due_exactly_on_interval(specimen, profile):
    """Fertilized exactly 14 days ago → due today, days_overdue == 0."""
    history = [make_event("fertilize", 14)]
    actions = next_actions(specimen, profile, history, TODAY)
    fert_actions = [a for a in actions if a.action_type == "fertilize"]
    assert len(fert_actions) == 1
    assert fert_actions[0].days_overdue == 0


# ---------------------------------------------------------------------------
# Overdue tests
# ---------------------------------------------------------------------------

def test_water_overdue(specimen, profile):
    """Watered 10 days ago with 7-day interval → overdue by 3 days."""
    history = [make_event("water", 10)]
    actions = next_actions(specimen, profile, history, TODAY)
    water_actions = [a for a in actions if a.action_type == "water"]
    assert len(water_actions) == 1
    assert water_actions[0].days_overdue == 3


def test_fertilize_overdue(specimen, profile):
    """Fertilized 20 days ago with 14-day interval → overdue by 6 days."""
    history = [make_event("fertilize", 20)]
    actions = next_actions(specimen, profile, history, TODAY)
    fert_actions = [a for a in actions if a.action_type == "fertilize"]
    assert len(fert_actions) == 1
    assert fert_actions[0].days_overdue == 6


# ---------------------------------------------------------------------------
# Not-yet-due tests
# ---------------------------------------------------------------------------

def test_water_not_due_excluded(specimen, profile):
    """Watered 3 days ago with 7-day interval → not yet due, excluded."""
    history = [make_event("water", 3)]
    actions = next_actions(specimen, profile, history, TODAY)
    types = [a.action_type for a in actions]
    assert "water" not in types


def test_fertilize_not_due_excluded(specimen, profile):
    """Fertilized 5 days ago with 14-day interval → not yet due, excluded."""
    history = [make_event("fertilize", 5)]
    actions = next_actions(specimen, profile, history, TODAY)
    types = [a.action_type for a in actions]
    assert "fertilize" not in types


# ---------------------------------------------------------------------------
# Independent action types
# ---------------------------------------------------------------------------

def test_water_due_fertilize_not_due(specimen, profile):
    """Water overdue, fertilize not yet due → only water returned."""
    history = [
        make_event("water", 8),      # overdue by 1
        make_event("fertilize", 5),  # 9 days remaining
    ]
    actions = next_actions(specimen, profile, history, TODAY)
    types = [a.action_type for a in actions]
    assert "water" in types
    assert "fertilize" not in types


def test_fertilize_due_water_not_due(specimen, profile):
    """Fertilize overdue, water not yet due → only fertilize returned."""
    history = [
        make_event("water", 2),       # 5 days remaining
        make_event("fertilize", 15),  # overdue by 1
    ]
    actions = next_actions(specimen, profile, history, TODAY)
    types = [a.action_type for a in actions]
    assert "fertilize" in types
    assert "water" not in types


# ---------------------------------------------------------------------------
# Sorting: most overdue first
# ---------------------------------------------------------------------------

def test_sort_most_overdue_first(specimen, profile):
    """Most-overdue action appears first in the returned list."""
    # water overdue 3 days, fertilize overdue 6 days → fertilize first
    history = [
        make_event("water", 10),      # 10-7=3 days overdue
        make_event("fertilize", 20),  # 20-14=6 days overdue
    ]
    actions = next_actions(specimen, profile, history, TODAY)
    assert len(actions) == 2
    assert actions[0].action_type == "fertilize"
    assert actions[1].action_type == "water"


# ---------------------------------------------------------------------------
# History with multiple events of the same type
# ---------------------------------------------------------------------------

def test_uses_most_recent_event(specimen, profile):
    """When history has multiple water events, the most recent one is used."""
    history = [
        make_event("water", 30),  # old — should be ignored
        make_event("water", 3),   # recent — not yet due
    ]
    actions = next_actions(specimen, profile, history, TODAY)
    types = [a.action_type for a in actions]
    assert "water" not in types  # recent event means not due yet


def test_non_scheduled_events_ignored(specimen, profile):
    """Prune/repot/wire events in history do not affect water/fertilize scheduling."""
    history = [
        make_event("prune", 1),
        make_event("repot", 2),
        make_event("wire", 3),
    ]
    actions = next_actions(specimen, profile, history, TODAY)
    # No water or fertilize events → both should be due
    types = [a.action_type for a in actions]
    assert "water" in types
    assert "fertilize" in types
