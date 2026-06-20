"""Collection / digital-twin model for a multi-specimen plant collection.

A ``Collection`` is the top-level container that owns every specimen and its
associated care state (profile + history).  All scheduling and health queries
can be run across the whole collection from a single call, returning a unified
view ordered by urgency.

No real-clock calls — every public method accepts an explicit ``today`` date
so tests remain fully deterministic.

Usage::

    from plant_care.collection import Collection
    from plant_care.models import Specimen, CareProfile, CareEvent
    import datetime

    col = Collection()
    spec = Specimen(id="jp-01", species="Juniperus procumbens",
                    acquired=datetime.date(2023,1,1), location="balcony",
                    light_level="full-sun", pot_size="5in", is_bonsai=True)
    profile = CareProfile(watering_interval_days=3,
                          fertilize_interval_days=14,
                          light_needs="full-sun", humidity="low")
    col.add(spec, profile)
    col.record(spec.id, CareEvent(type="water", date=datetime.date(2024,1,1)))

    today = datetime.date(2024, 1, 5)
    due = col.due_for_collection(today)   # list[(Specimen, DueAction)]
    summary = col.summary(today)          # CollectionSummary
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

from .health import assess_health
from .models import (
    CareEvent,
    CareProfile,
    DueAction,
    HealthState,
    Observations,
    Specimen,
)
from .schedule import next_actions


# ── SpecimenRecord ─────────────────────────────────────────────────────────────


@dataclass
class SpecimenRecord:
    """All persistent state for one specimen in the collection.

    Attributes
    ----------
    specimen:
        Immutable identity data for the plant.
    profile:
        Current care profile (intervals, light needs, humidity).
    history:
        Ordered list of care events; newer events should be appended.
    tags:
        Free-form labels (e.g. "featured", "gift", "show-ready").
    """

    specimen: Specimen
    profile: CareProfile
    history: List[CareEvent] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # ── Convenience accessors ─────────────────────────────────────────────────

    def events_of_type(self, action_type: str) -> List[CareEvent]:
        """Return all history events matching the given action type."""
        return [e for e in self.history if e.type == action_type]

    def last_event(self, action_type: str) -> Optional[CareEvent]:
        """Return the most-recent event of the given type, or None."""
        matches = self.events_of_type(action_type)
        return max(matches, key=lambda e: e.date) if matches else None

    def to_dict(self) -> dict:
        d: dict = {
            "specimen": {
                "id": self.specimen.id,
                "species": self.specimen.species,
                "acquired": self.specimen.acquired.isoformat(),
                "location": self.specimen.location,
                "light_level": self.specimen.light_level,
                "pot_size": self.specimen.pot_size,
                "is_bonsai": self.specimen.is_bonsai,
            },
            "profile": {
                "watering_interval_days": self.profile.watering_interval_days,
                "fertilize_interval_days": self.profile.fertilize_interval_days,
                "light_needs": self.profile.light_needs,
                "humidity": self.profile.humidity,
            },
            "history": [
                {"type": e.type, "date": e.date.isoformat(), "note": e.note}
                for e in self.history
            ],
            "tags": list(self.tags),
        }
        return d


# ── CollectionSummary ─────────────────────────────────────────────────────────


@dataclass
class CollectionSummary:
    """Aggregate health snapshot of the whole collection on a given date.

    Attributes
    ----------
    total:
        Number of specimens in the collection.
    due_count:
        Specimens with at least one due/overdue action.
    overdue_count:
        Specimens with at least one overdue action (days_overdue > 0).
    healthy_count:
        Specimens assessed as healthy (requires observations to be provided).
    attention_count:
        Specimens needing attention or declining.
    bonsai_count:
        Specimens flagged as bonsai.
    locations:
        Distinct location strings present.
    most_urgent:
        The specimen with the highest-priority outstanding action, or None.
    """

    total: int
    due_count: int
    overdue_count: int
    healthy_count: int
    attention_count: int
    bonsai_count: int
    locations: List[str]
    most_urgent: Optional[str]  # specimen id

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "due_count": self.due_count,
            "overdue_count": self.overdue_count,
            "healthy_count": self.healthy_count,
            "attention_count": self.attention_count,
            "bonsai_count": self.bonsai_count,
            "locations": self.locations,
            "most_urgent": self.most_urgent,
        }


# ── Collection ────────────────────────────────────────────────────────────────


class Collection:
    """A named, keyed container for a multi-specimen plant collection.

    All reads return new lists/dicts; the internal ``_records`` dict is the
    single source of truth.  There are no in-place mutations of individual
    ``SpecimenRecord`` objects from the outside — callers must use the
    ``record()`` / ``update_profile()`` / ``tag()`` methods.

    Parameters
    ----------
    name:
        Optional display name for the collection (e.g. "Studio collection").
    """

    def __init__(self, name: str = "My Collection") -> None:
        self.name = name
        self._records: Dict[str, SpecimenRecord] = {}

    # ── Mutation API ──────────────────────────────────────────────────────────

    def add(
        self,
        specimen: Specimen,
        profile: CareProfile,
        *,
        history: Optional[List[CareEvent]] = None,
        tags: Optional[List[str]] = None,
    ) -> "Collection":
        """Add a specimen to the collection.

        Raises
        ------
        ValueError
            If a specimen with the same id is already present.  Use
            ``update_profile()`` to change an existing specimen's profile.
        """
        if specimen.id in self._records:
            raise ValueError(
                f"Specimen '{specimen.id}' already exists in collection "
                f"'{self.name}'. Use update_profile() to change care settings."
            )
        self._records[specimen.id] = SpecimenRecord(
            specimen=specimen,
            profile=profile,
            history=list(history or []),
            tags=list(tags or []),
        )
        return self

    def remove(self, specimen_id: str) -> bool:
        """Remove a specimen by id.  Returns True if found and removed."""
        if specimen_id in self._records:
            del self._records[specimen_id]
            return True
        return False

    def record(self, specimen_id: str, event: CareEvent) -> "Collection":
        """Append a care event to a specimen's history.

        Raises
        ------
        KeyError
            If no specimen with *specimen_id* exists.
        """
        rec = self._get(specimen_id)
        rec.history.append(event)
        return self

    def update_profile(self, specimen_id: str, profile: CareProfile) -> "Collection":
        """Replace the care profile for a specimen.

        Raises
        ------
        KeyError
            If no specimen with *specimen_id* exists.
        """
        rec = self._get(specimen_id)
        self._records[specimen_id] = SpecimenRecord(
            specimen=rec.specimen,
            profile=profile,
            history=rec.history,
            tags=rec.tags,
        )
        return self

    def tag(self, specimen_id: str, *tags: str) -> "Collection":
        """Add one or more tags to a specimen.  Duplicate tags are ignored."""
        rec = self._get(specimen_id)
        for t in tags:
            if t not in rec.tags:
                rec.tags.append(t)
        return self

    def untag(self, specimen_id: str, tag: str) -> "Collection":
        """Remove a tag from a specimen if present."""
        rec = self._get(specimen_id)
        rec.tags = [t for t in rec.tags if t != tag]
        return self

    # ── Query API — single specimen ───────────────────────────────────────────

    def get(self, specimen_id: str) -> SpecimenRecord:
        """Return the SpecimenRecord for *specimen_id*.

        Raises
        ------
        KeyError
            If no specimen with *specimen_id* exists.
        """
        return self._get(specimen_id)

    def due(
        self, specimen_id: str, today: datetime.date
    ) -> List[DueAction]:
        """Return due/overdue actions for a single specimen."""
        rec = self._get(specimen_id)
        return next_actions(rec.specimen, rec.profile, rec.history, today)

    def health(
        self, specimen_id: str, observations: Observations
    ) -> HealthState:
        """Assess health for a single specimen from observations."""
        rec = self._get(specimen_id)
        return assess_health(rec.specimen, observations)

    # ── Query API — whole collection ──────────────────────────────────────────

    def all_records(self) -> List[SpecimenRecord]:
        """Return all SpecimenRecords, in insertion order."""
        return list(self._records.values())

    def specimens(self) -> List[Specimen]:
        """Return all Specimen objects, in insertion order."""
        return [r.specimen for r in self._records.values()]

    def __len__(self) -> int:
        return len(self._records)

    def __contains__(self, specimen_id: str) -> bool:
        return specimen_id in self._records

    def by_location(self, location: str) -> List[SpecimenRecord]:
        """Return all records whose specimen.location matches *location*."""
        return [r for r in self._records.values()
                if r.specimen.location == location]

    def bonsai(self) -> List[SpecimenRecord]:
        """Return all records whose specimen.is_bonsai is True."""
        return [r for r in self._records.values() if r.specimen.is_bonsai]

    def tagged(self, tag: str) -> List[SpecimenRecord]:
        """Return all records that carry the given tag."""
        return [r for r in self._records.values() if tag in r.tags]

    def locations(self) -> List[str]:
        """Return the sorted list of distinct location strings."""
        return sorted({r.specimen.location for r in self._records.values()})

    def due_for_collection(
        self, today: datetime.date
    ) -> List[Tuple[Specimen, DueAction]]:
        """Return all due/overdue actions across the whole collection.

        Returns a flat list of (Specimen, DueAction) pairs, sorted by
        DueAction.days_overdue descending (most urgent first).
        """
        pairs: List[Tuple[Specimen, DueAction]] = []
        for rec in self._records.values():
            actions = next_actions(rec.specimen, rec.profile, rec.history, today)
            for action in actions:
                pairs.append((rec.specimen, action))
        pairs.sort(key=lambda p: p[1].days_overdue, reverse=True)
        return pairs

    def health_for_collection(
        self, observations_map: Dict[str, Observations]
    ) -> Dict[str, HealthState]:
        """Assess health for every specimen that has an entry in *observations_map*.

        Returns a dict mapping specimen_id → HealthState.  Specimens without
        an observations entry are omitted (not defaulted to healthy).
        """
        result: Dict[str, HealthState] = {}
        for sid, obs in observations_map.items():
            if sid in self._records:
                rec = self._records[sid]
                result[sid] = assess_health(rec.specimen, obs)
        return result

    def summary(
        self,
        today: datetime.date,
        observations_map: Optional[Dict[str, Observations]] = None,
    ) -> CollectionSummary:
        """Return an aggregate snapshot of the collection on *today*.

        Parameters
        ----------
        today:
            Reference date for scheduling queries.
        observations_map:
            Optional mapping of specimen_id → Observations for health
            assessment.  If not provided, healthy_count and attention_count
            are both 0.
        """
        total = len(self._records)
        bonsai_count = sum(1 for r in self._records.values() if r.specimen.is_bonsai)
        locs = self.locations()

        due_count = 0
        overdue_count = 0
        most_urgent_id: Optional[str] = None
        max_overdue = -1

        for rec in self._records.values():
            actions = next_actions(rec.specimen, rec.profile, rec.history, today)
            if actions:
                due_count += 1
                worst = max(actions, key=lambda a: a.days_overdue)
                if any(a.days_overdue > 0 for a in actions):
                    overdue_count += 1
                if worst.days_overdue > max_overdue:
                    max_overdue = worst.days_overdue
                    most_urgent_id = rec.specimen.id

        healthy_count = 0
        attention_count = 0
        if observations_map:
            for sid, obs in observations_map.items():
                if sid in self._records:
                    state = assess_health(self._records[sid].specimen, obs)
                    if state.status == "healthy":
                        healthy_count += 1
                    else:
                        attention_count += 1

        return CollectionSummary(
            total=total,
            due_count=due_count,
            overdue_count=overdue_count,
            healthy_count=healthy_count,
            attention_count=attention_count,
            bonsai_count=bonsai_count,
            locations=locs,
            most_urgent=most_urgent_id,
        )

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a JSON-safe dict representing the full collection."""
        return {
            "name": self.name,
            "specimens": [r.to_dict() for r in self._records.values()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Collection":
        """Reconstruct a Collection from a ``to_dict()`` payload.

        Raises
        ------
        KeyError / ValueError
            If required fields are missing or malformed.
        """
        col = cls(name=data.get("name", "My Collection"))
        for entry in data.get("specimens", []):
            sp_d = entry["specimen"]
            pr_d = entry["profile"]
            specimen = Specimen(
                id=sp_d["id"],
                species=sp_d["species"],
                acquired=datetime.date.fromisoformat(sp_d["acquired"]),
                location=sp_d["location"],
                light_level=sp_d["light_level"],
                pot_size=sp_d["pot_size"],
                is_bonsai=sp_d.get("is_bonsai", False),
            )
            profile = CareProfile(
                watering_interval_days=pr_d["watering_interval_days"],
                fertilize_interval_days=pr_d["fertilize_interval_days"],
                light_needs=pr_d["light_needs"],
                humidity=pr_d["humidity"],
            )
            history = [
                CareEvent(
                    type=ev["type"],
                    date=datetime.date.fromisoformat(ev["date"]),
                    note=ev.get("note", ""),
                )
                for ev in entry.get("history", [])
            ]
            tags = entry.get("tags", [])
            col.add(specimen, profile, history=history, tags=tags)
        return col

    # ── Internal ──────────────────────────────────────────────────────────────

    def _get(self, specimen_id: str) -> SpecimenRecord:
        try:
            return self._records[specimen_id]
        except KeyError:
            raise KeyError(
                f"Specimen '{specimen_id}' not found in collection '{self.name}'."
            )
