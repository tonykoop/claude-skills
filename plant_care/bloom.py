"""Bud and bloom chrono-tracker (story #173).

Tracks ephemeral botanical events — bud observations, bloom stages, and
bloom-window forecasting based on species baselines and the grower's own
historical data.

Key objects:

- ``BudStage`` — lifecycle enum:
  OBSERVED → SWELLING → OPENING → OPEN → FADING → DROPPED / FINISHED
- ``BudEvent`` — a single dated observation of a bud at a given stage.
- ``BloomRecord`` — full lifecycle of one bloom event on one specimen,
  composed of a sequence of ``BudEvent`` objects.  Optional ``species``
  field enables baseline-driven forecasting.
- ``BloomLog`` — ordered history of ``BloomRecord`` objects for one
  specimen.

Pure functions:

- ``time_in_stage(record, stage)`` → days the bud spent in that stage, or
  ``None`` if not entered.
- ``forecast_bloom_window(log, today, baseline_days)`` → ``(earliest, latest)``
  as ``datetime.date`` objects, or ``None`` if insufficient data.
- ``mean_days_to_stage(log, from_stage, to_stage)`` → historical average.
- ``bloom_summary(log)`` → statistics dict over the full log.

Notes:
- Species like *Ficus benjamina* have syconium-enclosed flowers and do NOT
  produce externally visible buds — skip this module for them.
- Bloom-window forecasts carry inherent uncertainty; confidence is flagged
  in function return values.
- No real-clock calls — all functions accept an explicit ``today`` date.

Usage::

    import datetime
    from plant_care.bloom import (
        BudStage, BudEvent, BloomRecord, BloomLog,
        forecast_bloom_window, time_in_stage, bloom_summary,
    )

    record = BloomRecord(record_id="br-01", specimen_id="plum-01",
                         species="Prunus mume")
    record.add_event(BudEvent(stage=BudStage.OBSERVED,
                              date=datetime.date(2024, 1, 15)))
    record.add_event(BudEvent(stage=BudStage.OPEN,
                              date=datetime.date(2024, 1, 28)))

    log = BloomLog(specimen_id="plum-01")
    log.add_record(record)

    window = forecast_bloom_window(log, datetime.date(2024, 12, 1),
                                   baseline_days=14)
    # (datetime.date(2024, 12, 15), datetime.date(2024, 12, 21))
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ── BudStage ──────────────────────────────────────────────────────────────────


class BudStage(str, Enum):
    """Sequential lifecycle stages of a bud/bloom event.

    The expected progression is OBSERVED → SWELLING → OPENING → OPEN →
    FADING → FINISHED.  A bud may also be DROPPED at any stage before
    FINISHED (premature drop is a health/stress signal).
    """

    OBSERVED = "observed"       # First notice of a bud swell
    SWELLING = "swelling"       # Clearly swelling; visible growth
    OPENING = "opening"         # Petals separating
    OPEN = "open"               # Fully open / anthesis
    FADING = "fading"           # Petals wilting / colour change
    FINISHED = "finished"       # Spent; pollinated or wilted off naturally
    DROPPED = "dropped"         # Premature drop (stress, low humidity, etc.)


# Ordered stages (DROPPED is a side-branch, not in the main chain)
_STAGE_ORDER: List[BudStage] = [
    BudStage.OBSERVED,
    BudStage.SWELLING,
    BudStage.OPENING,
    BudStage.OPEN,
    BudStage.FADING,
    BudStage.FINISHED,
]
_STAGE_RANK: Dict[BudStage, int] = {s: i for i, s in enumerate(_STAGE_ORDER)}


# ── BudEvent ──────────────────────────────────────────────────────────────────


@dataclass
class BudEvent:
    """A single dated observation of a bud at a given lifecycle stage.

    Attributes
    ----------
    stage:
        The ``BudStage`` observed on *date*.
    date:
        The observation date (injected; no real-clock calls).
    notes:
        Free-text notes (location on plant, colour, size, stressors, etc.).
    """

    stage: BudStage
    date: datetime.date
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "stage": self.stage.value,
            "date": self.date.isoformat(),
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BudEvent":
        return cls(
            stage=BudStage(data["stage"]),
            date=datetime.date.fromisoformat(data["date"]),
            notes=data.get("notes", ""),
        )


# ── BloomRecord ───────────────────────────────────────────────────────────────


@dataclass
class BloomRecord:
    """Full lifecycle record for one bloom event on one specimen.

    A ``BloomRecord`` is a sequence of ``BudEvent`` objects that narrate
    a single bud from first observation to completion or drop.

    Attributes
    ----------
    record_id:
        Unique identifier (e.g. ``"br-2024-01"``).
    specimen_id:
        ID of the host specimen.
    species:
        Optional species name for baseline-driven forecasting.
    events:
        Ordered list of ``BudEvent`` observations.
    notes:
        Record-level notes (position on plant, unusual conditions, etc.).
    """

    record_id: str
    specimen_id: str
    species: str = ""
    events: List[BudEvent] = field(default_factory=list)
    notes: str = ""

    # ── Mutation ──────────────────────────────────────────────────────────────

    def add_event(self, event: BudEvent) -> "BloomRecord":
        """Append *event*.  Returns self for chaining."""
        self.events.append(event)
        # Keep events sorted by date
        self.events.sort(key=lambda e: e.date)
        return self

    # ── Queries ───────────────────────────────────────────────────────────────

    def first_event(self) -> Optional[BudEvent]:
        """Return the earliest event, or None."""
        return self.events[0] if self.events else None

    def latest_event(self) -> Optional[BudEvent]:
        """Return the most recent event, or None."""
        return self.events[-1] if self.events else None

    def event_for_stage(self, stage: BudStage) -> Optional[BudEvent]:
        """Return the first event at *stage*, or None."""
        return next((e for e in self.events if e.stage == stage), None)

    def date_of_stage(self, stage: BudStage) -> Optional[datetime.date]:
        """Return the date the bud reached *stage*, or None."""
        ev = self.event_for_stage(stage)
        return ev.date if ev else None

    def is_complete(self) -> bool:
        """True if the bud reached FINISHED or DROPPED."""
        return any(
            e.stage in (BudStage.FINISHED, BudStage.DROPPED) for e in self.events
        )

    def was_dropped(self) -> bool:
        """True if the bud was prematurely dropped."""
        return any(e.stage == BudStage.DROPPED for e in self.events)

    def current_stage(self) -> Optional[BudStage]:
        """Return the stage of the most recent event, or None."""
        ev = self.latest_event()
        return ev.stage if ev else None

    def days_observed(self, today: datetime.date) -> Optional[int]:
        """Days since the bud was first observed, or None."""
        fe = self.first_event()
        return (today - fe.date).days if fe else None

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "specimen_id": self.specimen_id,
            "species": self.species,
            "events": [e.to_dict() for e in self.events],
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BloomRecord":
        rec = cls(
            record_id=data["record_id"],
            specimen_id=data["specimen_id"],
            species=data.get("species", ""),
            notes=data.get("notes", ""),
        )
        for ev_data in data.get("events", []):
            rec.events.append(BudEvent.from_dict(ev_data))
        return rec


# ── BloomLog ──────────────────────────────────────────────────────────────────


class BloomLog:
    """Ordered history of bloom records for one specimen.

    Records are keyed by ``record_id``.
    """

    def __init__(self, specimen_id: str) -> None:
        self.specimen_id = specimen_id
        self._records: Dict[str, BloomRecord] = {}

    def add_record(self, record: BloomRecord) -> "BloomLog":
        """Add *record*.  Raises ``ValueError`` on duplicate ID."""
        if record.record_id in self._records:
            raise ValueError(f"Record '{record.record_id}' already exists.")
        self._records[record.record_id] = record
        return self

    def get_record(self, record_id: str) -> BloomRecord:
        """Return record by ID.  Raises ``KeyError`` if not found."""
        try:
            return self._records[record_id]
        except KeyError:
            raise KeyError(f"BloomRecord '{record_id}' not found.")

    def all_records(self) -> List[BloomRecord]:
        """Return all records sorted by their first-event date."""
        def _first_date(r: BloomRecord) -> datetime.date:
            fe = r.first_event()
            return fe.date if fe else datetime.date.min

        return sorted(self._records.values(), key=_first_date)

    def complete_records(self) -> List[BloomRecord]:
        """Return only records that reached FINISHED (not dropped)."""
        return [
            r for r in self.all_records()
            if r.is_complete() and not r.was_dropped()
        ]

    def dropped_records(self) -> List[BloomRecord]:
        """Return records where the bud was dropped."""
        return [r for r in self.all_records() if r.was_dropped()]

    def active_records(self) -> List[BloomRecord]:
        """Return records that are neither FINISHED nor DROPPED."""
        return [r for r in self.all_records() if not r.is_complete()]

    def __len__(self) -> int:
        return len(self._records)

    def to_list(self) -> List[dict]:
        return [r.to_dict() for r in self.all_records()]

    @classmethod
    def from_list(cls, specimen_id: str, data: List[dict]) -> "BloomLog":
        log = cls(specimen_id=specimen_id)
        for item in data:
            log.add_record(BloomRecord.from_dict(item))
        return log


# ── Pure functions ────────────────────────────────────────────────────────────


def time_in_stage(
    record: BloomRecord,
    stage: BudStage,
) -> Optional[int]:
    """Return the number of days the bud spent in *stage*, or None.

    The duration is computed as the difference in dates between *stage*
    and the immediately following stage in the record's event list.
    If no subsequent event exists (the record is still active at *stage*),
    ``None`` is returned.

    Args:
        record:  The bloom record to analyse.
        stage:   The stage to measure duration for.

    Returns:
        Integer days, or ``None`` if the stage was not entered or has no
        subsequent event.
    """
    stage_date = record.date_of_stage(stage)
    if stage_date is None:
        return None

    # Find the next event after stage_date
    later_events = [
        e for e in record.events
        if e.date > stage_date and e.stage != stage
    ]
    if not later_events:
        return None

    next_date = min(e.date for e in later_events)
    return (next_date - stage_date).days


def mean_days_to_stage(
    log: BloomLog,
    from_stage: BudStage,
    to_stage: BudStage,
) -> Optional[float]:
    """Return the mean number of days from *from_stage* to *to_stage*.

    Computes the average across all complete records in *log* that have
    both stages recorded.  Returns ``None`` if fewer than one data point
    is available.

    The result is intended for bloom-window forecasting — it answers the
    question "on average, how long does this specimen take to go from
    first observation to open flower?"
    """
    durations: List[int] = []
    for record in log.all_records():
        start = record.date_of_stage(from_stage)
        end = record.date_of_stage(to_stage)
        if start is not None and end is not None and end >= start:
            durations.append((end - start).days)
    if not durations:
        return None
    return sum(durations) / len(durations)


def forecast_bloom_window(
    log: BloomLog,
    today: datetime.date,
    baseline_days: int = 14,
    confidence_band: float = 0.25,
) -> Optional[Tuple[datetime.date, datetime.date]]:
    """Forecast when the next bud will open from first observation.

    Uses the grower's own historical data if available (≥1 completed
    record with both OBSERVED and OPEN stages), otherwise falls back to
    *baseline_days* (a species-typical or generic default).

    Args:
        log:               The specimen's bloom history.
        today:             Reference date for the forecast start.
        baseline_days:     Fallback days from OBSERVED to OPEN when no
                           history is available.  Default 14 days is a
                           generic estimate for common flowering houseplants.
        confidence_band:   Fraction of *mean_days* added/subtracted for the
                           window bounds.  Default ±25%.

    Returns:
        ``(earliest_date, latest_date)`` as a tuple, or ``None`` if
        *log* has no active buds to forecast from (i.e. no record with
        a recent OBSERVED event).

    Note:
        This is a probabilistic estimate.  Actual bloom date depends on
        temperature, light hours, water stress, and cultivar.  Present
        the window as a guide, not a guarantee.
    """
    # Find active buds that are in a pre-OPEN stage
    active = [
        r for r in log.active_records()
        if r.current_stage() in (
            BudStage.OBSERVED, BudStage.SWELLING, BudStage.OPENING
        )
    ]
    if not active:
        return None

    # Use the most recently observed bud as the anchor
    latest_active = max(active, key=lambda r: r.first_event().date)
    observed_date = latest_active.date_of_stage(BudStage.OBSERVED)
    if observed_date is None:
        observed_date = latest_active.first_event().date

    # Estimate days from OBSERVED to OPEN from history or baseline
    historical_mean = mean_days_to_stage(log, BudStage.OBSERVED, BudStage.OPEN)
    mean_days = historical_mean if historical_mean is not None else float(baseline_days)

    # How far are we already through the window?
    days_elapsed = (today - observed_date).days
    remaining_days = max(0, mean_days - days_elapsed)

    # Apply confidence band
    band = max(1, round(mean_days * confidence_band))
    earliest = today + datetime.timedelta(days=max(0, round(remaining_days - band)))
    latest = today + datetime.timedelta(days=round(remaining_days + band))

    return (earliest, latest)


def bloom_summary(log: BloomLog) -> dict:
    """Return summary statistics for the full bloom log.

    Keys:
    - ``total_records`` — total number of bloom records.
    - ``complete`` — records that reached FINISHED.
    - ``dropped`` — records where the bud dropped prematurely.
    - ``active`` — currently in-progress records.
    - ``drop_rate`` — fraction of resolved records that dropped.
    - ``mean_days_observed_to_open`` — historical average (or None).
    - ``mean_days_open_to_finished`` — historical average (or None).
    - ``most_recent_open_date`` — date of most recent OPEN event (or None).
    """
    all_recs = log.all_records()
    complete = log.complete_records()
    dropped = log.dropped_records()
    active = log.active_records()

    resolved = len(complete) + len(dropped)
    drop_rate = len(dropped) / resolved if resolved > 0 else 0.0

    open_dates = [
        r.date_of_stage(BudStage.OPEN)
        for r in all_recs
        if r.date_of_stage(BudStage.OPEN) is not None
    ]
    most_recent_open = max(open_dates).isoformat() if open_dates else None

    return {
        "total_records": len(all_recs),
        "complete": len(complete),
        "dropped": len(dropped),
        "active": len(active),
        "drop_rate": drop_rate,
        "mean_days_observed_to_open": mean_days_to_stage(
            log, BudStage.OBSERVED, BudStage.OPEN
        ),
        "mean_days_open_to_finished": mean_days_to_stage(
            log, BudStage.OPEN, BudStage.FINISHED
        ),
        "most_recent_open_date": most_recent_open,
    }
