"""Pydantic/dataclass models for the plant-care engine.

These models are the shared data layer used by schedule.py, health.py, and
bonsai.py. They are serialisable via Pydantic's .model_dump() / .model_validate()
so that upstream callers (agents, scripts, tests) can round-trip JSON without
extra wiring.
"""
from __future__ import annotations

import datetime
from typing import Literal, Optional

try:
    from pydantic import BaseModel, Field
    _PYDANTIC = True
except ImportError:  # pragma: no cover — fallback keeps engine importable w/o pydantic
    _PYDANTIC = False

if _PYDANTIC:
    class Specimen(BaseModel):
        """A single plant in the collection."""
        id: str
        species: str
        acquired: datetime.date
        location: str
        light_level: str  # e.g. "bright-indirect", "low", "full-sun"
        pot_size: str     # e.g. "6in", "10in"
        is_bonsai: bool = False

    class CareProfile(BaseModel):
        """Species/specimen care preferences."""
        watering_interval_days: int
        fertilize_interval_days: int
        light_needs: str
        humidity: str  # e.g. "high", "moderate", "low"

    class CareEvent(BaseModel):
        """A timestamped care action recorded in the plant's history."""
        type: Literal["water", "fertilize", "prune", "repot", "wire"]
        date: datetime.date
        note: str = ""

    class BonsaiExtras(BaseModel):
        """Bonsai-specific training state that supplements CareProfile."""
        wire_applied: Optional[datetime.date] = None
        last_pruned: Optional[datetime.date] = None
        nebari_notes: str = ""

    class DueAction(BaseModel):
        """An action that is due or overdue for a specimen."""
        action_type: str
        due_date: datetime.date
        days_overdue: int  # 0 if due today, positive if past-due
        priority: int      # higher = more urgent; computed by schedule.py

    class HealthState(BaseModel):
        """Result of a rule-based health assessment."""
        status: Literal["healthy", "needs-attention", "declining"]
        flags: list[str]
        notes: str

    class Observations(BaseModel):
        """Visual observations supplied by the user or agent."""
        yellowing: bool = False
        drooping: bool = False
        pests: bool = False
        dry_soil: bool = False
        leaf_drop: bool = False
        mold: bool = False

else:  # pragma: no cover
    # Minimal dataclass fallback so the engine is importable in stdlib-only envs.
    from dataclasses import dataclass, field

    @dataclass
    class Specimen:
        id: str
        species: str
        acquired: datetime.date
        location: str
        light_level: str
        pot_size: str
        is_bonsai: bool = False

    @dataclass
    class CareProfile:
        watering_interval_days: int
        fertilize_interval_days: int
        light_needs: str
        humidity: str

    @dataclass
    class CareEvent:
        type: str
        date: datetime.date
        note: str = ""

    @dataclass
    class BonsaiExtras:
        wire_applied: Optional[datetime.date] = None
        last_pruned: Optional[datetime.date] = None
        nebari_notes: str = ""

    @dataclass
    class DueAction:
        action_type: str
        due_date: datetime.date
        days_overdue: int
        priority: int

    @dataclass
    class HealthState:
        status: str
        flags: list
        notes: str

    @dataclass
    class Observations:
        yellowing: bool = False
        drooping: bool = False
        pests: bool = False
        dry_soil: bool = False
        leaf_drop: bool = False
        mold: bool = False
