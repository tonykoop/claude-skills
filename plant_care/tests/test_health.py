"""Tests for plant_care.health — assess_health() rule-based status logic."""
from __future__ import annotations

import datetime
import pytest

from plant_care.models import Observations, Specimen
from plant_care.health import assess_health


@pytest.fixture
def specimen():
    return Specimen(
        id="sp-002",
        species="Ficus retusa",
        acquired=datetime.date(2023, 3, 15),
        location="south-window",
        light_level="bright-indirect",
        pot_size="6in",
        is_bonsai=True,
    )


# ---------------------------------------------------------------------------
# DECLINING status
# ---------------------------------------------------------------------------

def test_pests_alone_declining(specimen):
    """Pests alone → declining."""
    obs = Observations(pests=True)
    result = assess_health(specimen, obs)
    assert result.status == "declining"
    assert "pests" in result.flags


def test_yellowing_and_drooping_declining(specimen):
    """Yellowing + drooping together → declining."""
    obs = Observations(yellowing=True, drooping=True)
    result = assess_health(specimen, obs)
    assert result.status == "declining"
    assert "yellowing" in result.flags
    assert "drooping" in result.flags


def test_leaf_drop_declining(specimen):
    """Leaf drop alone → declining."""
    obs = Observations(leaf_drop=True)
    result = assess_health(specimen, obs)
    assert result.status == "declining"
    assert "leaf_drop" in result.flags


def test_pests_with_other_flags_still_declining(specimen):
    """Pests combined with other flags → still declining (not double-counted)."""
    obs = Observations(pests=True, yellowing=True, mold=True)
    result = assess_health(specimen, obs)
    assert result.status == "declining"


def test_leaf_drop_with_yellowing_declining(specimen):
    """Leaf drop + yellowing → declining (leaf_drop triggers decline regardless)."""
    obs = Observations(leaf_drop=True, yellowing=True)
    result = assess_health(specimen, obs)
    assert result.status == "declining"


# ---------------------------------------------------------------------------
# NEEDS-ATTENTION status
# ---------------------------------------------------------------------------

def test_yellowing_alone_needs_attention(specimen):
    """Yellowing without drooping → needs-attention (not declining)."""
    obs = Observations(yellowing=True)
    result = assess_health(specimen, obs)
    assert result.status == "needs-attention"
    assert "yellowing" in result.flags


def test_drooping_alone_needs_attention(specimen):
    """Drooping without yellowing → needs-attention."""
    obs = Observations(drooping=True)
    result = assess_health(specimen, obs)
    assert result.status == "needs-attention"
    assert "drooping" in result.flags


def test_dry_soil_needs_attention(specimen):
    """Dry soil → needs-attention."""
    obs = Observations(dry_soil=True)
    result = assess_health(specimen, obs)
    assert result.status == "needs-attention"
    assert "dry_soil" in result.flags


def test_mold_needs_attention(specimen):
    """Mold → needs-attention."""
    obs = Observations(mold=True)
    result = assess_health(specimen, obs)
    assert result.status == "needs-attention"
    assert "mold" in result.flags


def test_dry_soil_and_mold_needs_attention(specimen):
    """Dry soil + mold (no declining triggers) → needs-attention."""
    obs = Observations(dry_soil=True, mold=True)
    result = assess_health(specimen, obs)
    assert result.status == "needs-attention"


# ---------------------------------------------------------------------------
# HEALTHY status
# ---------------------------------------------------------------------------

def test_no_flags_healthy(specimen):
    """No observations → healthy."""
    obs = Observations()
    result = assess_health(specimen, obs)
    assert result.status == "healthy"
    assert result.flags == []


def test_all_false_healthy(specimen):
    """Explicitly false observations → healthy."""
    obs = Observations(
        yellowing=False,
        drooping=False,
        pests=False,
        dry_soil=False,
        leaf_drop=False,
        mold=False,
    )
    result = assess_health(specimen, obs)
    assert result.status == "healthy"


# ---------------------------------------------------------------------------
# Flags list accuracy
# ---------------------------------------------------------------------------

def test_flags_list_contains_all_triggered(specimen):
    """All triggered observations appear in the flags list."""
    obs = Observations(yellowing=True, dry_soil=True, mold=True)
    result = assess_health(specimen, obs)
    # status is needs-attention (no declining trigger)
    assert result.status == "needs-attention"
    assert set(result.flags) == {"yellowing", "dry_soil", "mold"}


def test_flags_list_empty_when_healthy(specimen):
    """Flags list is empty when all observations are false."""
    obs = Observations()
    result = assess_health(specimen, obs)
    assert result.flags == []


# ---------------------------------------------------------------------------
# Notes field
# ---------------------------------------------------------------------------

def test_declining_notes_nonempty(specimen):
    """HealthState notes are non-empty for declining status."""
    obs = Observations(pests=True)
    result = assess_health(specimen, obs)
    assert len(result.notes) > 0


def test_healthy_notes_nonempty(specimen):
    """HealthState notes are non-empty even for healthy status."""
    obs = Observations()
    result = assess_health(specimen, obs)
    assert len(result.notes) > 0
