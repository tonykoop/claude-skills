"""Tests for plant_care.models — serialization/deserialization round-trips.

These tests rely on Pydantic being available (the CI install includes it).
They verify that the model contracts are stable: field names, types, and
defaults all survive a .model_dump() / .model_validate() round-trip.
"""
from __future__ import annotations

import datetime
import pytest

pytest.importorskip("pydantic", reason="serialization tests require pydantic")

from plant_care.models import (
    BonsaiExtras,
    CareEvent,
    CareProfile,
    DueAction,
    HealthState,
    Observations,
    Specimen,
)


# ---------------------------------------------------------------------------
# Specimen
# ---------------------------------------------------------------------------

def test_specimen_round_trip():
    """Specimen serializes and deserializes without data loss."""
    s = Specimen(
        id="sp-100",
        species="Juniperus procumbens",
        acquired=datetime.date(2022, 5, 10),
        location="balcony",
        light_level="full-sun",
        pot_size="5in",
        is_bonsai=True,
    )
    data = s.model_dump()
    restored = Specimen.model_validate(data)
    assert restored.id == s.id
    assert restored.species == s.species
    assert restored.acquired == s.acquired
    assert restored.location == s.location
    assert restored.light_level == s.light_level
    assert restored.pot_size == s.pot_size
    assert restored.is_bonsai == s.is_bonsai


def test_specimen_default_is_bonsai_false():
    """Specimen.is_bonsai defaults to False."""
    s = Specimen(
        id="sp-101",
        species="Pothos",
        acquired=datetime.date(2025, 1, 1),
        location="shelf",
        light_level="low",
        pot_size="4in",
    )
    assert s.is_bonsai is False


def test_specimen_serializes_dates_as_date():
    """Specimen.acquired is preserved as a datetime.date through round-trip."""
    s = Specimen(
        id="sp-102",
        species="Ficus lyrata",
        acquired=datetime.date(2023, 8, 15),
        location="office",
        light_level="bright-indirect",
        pot_size="12in",
    )
    data = s.model_dump()
    restored = Specimen.model_validate(data)
    assert isinstance(restored.acquired, datetime.date)


# ---------------------------------------------------------------------------
# CareEvent
# ---------------------------------------------------------------------------

def test_care_event_round_trip():
    """CareEvent serializes and deserializes without data loss."""
    ev = CareEvent(type="water", date=datetime.date(2026, 6, 15), note="soil felt dry")
    data = ev.model_dump()
    restored = CareEvent.model_validate(data)
    assert restored.type == ev.type
    assert restored.date == ev.date
    assert restored.note == ev.note


def test_care_event_default_note_empty():
    """CareEvent.note defaults to empty string."""
    ev = CareEvent(type="fertilize", date=datetime.date(2026, 6, 1))
    assert ev.note == ""


def test_care_event_all_types_valid():
    """All five event types are accepted by the model."""
    today = datetime.date(2026, 6, 19)
    for event_type in ("water", "fertilize", "prune", "repot", "wire"):
        ev = CareEvent(type=event_type, date=today)
        assert ev.type == event_type


# ---------------------------------------------------------------------------
# BonsaiExtras
# ---------------------------------------------------------------------------

def test_bonsai_extras_round_trip_with_dates():
    """BonsaiExtras with dates serializes and deserializes correctly."""
    extras = BonsaiExtras(
        wire_applied=datetime.date(2026, 3, 1),
        last_pruned=datetime.date(2026, 6, 5),
        nebari_notes="Left nebari root gaining definition.",
    )
    data = extras.model_dump()
    restored = BonsaiExtras.model_validate(data)
    assert restored.wire_applied == extras.wire_applied
    assert restored.last_pruned == extras.last_pruned
    assert restored.nebari_notes == extras.nebari_notes


def test_bonsai_extras_defaults():
    """BonsaiExtras fields default to None / empty string."""
    extras = BonsaiExtras()
    assert extras.wire_applied is None
    assert extras.last_pruned is None
    assert extras.nebari_notes == ""


def test_bonsai_extras_none_dates_round_trip():
    """BonsaiExtras with None dates survives round-trip cleanly."""
    extras = BonsaiExtras(wire_applied=None, last_pruned=None)
    data = extras.model_dump()
    restored = BonsaiExtras.model_validate(data)
    assert restored.wire_applied is None
    assert restored.last_pruned is None


# ---------------------------------------------------------------------------
# DueAction
# ---------------------------------------------------------------------------

def test_due_action_priority_field_present():
    """DueAction exposes a priority field."""
    action = DueAction(
        action_type="water",
        due_date=datetime.date(2026, 6, 12),
        days_overdue=7,
        priority=7,
    )
    assert hasattr(action, "priority")
    assert action.priority == 7


def test_due_action_zero_overdue():
    """DueAction with days_overdue == 0 is valid (due today)."""
    action = DueAction(
        action_type="fertilize",
        due_date=datetime.date(2026, 6, 19),
        days_overdue=0,
        priority=0,
    )
    assert action.days_overdue == 0


def test_due_action_round_trip():
    """DueAction serializes and deserializes without data loss."""
    action = DueAction(
        action_type="water",
        due_date=datetime.date(2026, 6, 15),
        days_overdue=4,
        priority=4,
    )
    data = action.model_dump()
    restored = DueAction.model_validate(data)
    assert restored.action_type == action.action_type
    assert restored.due_date == action.due_date
    assert restored.days_overdue == action.days_overdue
    assert restored.priority == action.priority


# ---------------------------------------------------------------------------
# CareProfile
# ---------------------------------------------------------------------------

def test_care_profile_round_trip():
    """CareProfile serializes and deserializes correctly."""
    profile = CareProfile(
        watering_interval_days=7,
        fertilize_interval_days=14,
        light_needs="bright-indirect",
        humidity="moderate",
    )
    data = profile.model_dump()
    restored = CareProfile.model_validate(data)
    assert restored.watering_interval_days == profile.watering_interval_days
    assert restored.fertilize_interval_days == profile.fertilize_interval_days
    assert restored.light_needs == profile.light_needs
    assert restored.humidity == profile.humidity


# ---------------------------------------------------------------------------
# Observations
# ---------------------------------------------------------------------------

def test_observations_all_defaults_false():
    """Observations defaults all flags to False."""
    obs = Observations()
    assert obs.yellowing is False
    assert obs.drooping is False
    assert obs.pests is False
    assert obs.dry_soil is False
    assert obs.leaf_drop is False
    assert obs.mold is False


def test_observations_round_trip():
    """Observations serializes and deserializes correctly."""
    obs = Observations(yellowing=True, pests=True, mold=True)
    data = obs.model_dump()
    restored = Observations.model_validate(data)
    assert restored.yellowing is True
    assert restored.pests is True
    assert restored.mold is True
    assert restored.drooping is False
