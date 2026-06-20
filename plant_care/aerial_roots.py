"""Aerial-root and nebari guidance tracker (story #174).

Tracks the development lifecycle of aerial roots on species such as
*Ficus benjamina*, *Ficus microcarpa*, *Ficus religiosa*, and other
Moraceae / Araceae that produce above-ground structural roots.  Especially
useful for nebari (root spread at soil level) development in bonsai
practice.

Key objects:

- ``RootStage`` — lifecycle enum:
  TIP_PROMISING → GUIDED → REACHED_SOIL → THICKENING → FUSED.
  A root may also be ABANDONED (guide removed, root withered).
- ``RootEntry`` — a dated log entry recording a stage transition.
- ``AerialRoot`` — a single tracked root on one specimen, with a full
  stage history.
- ``GuidanceNote`` — care advice for a given stage (sphagnum wrapping,
  humidity tent, etc.).
- ``NebariLog`` — collection of aerial roots for one specimen.

Pure functions:

- ``guidance_for(stage)`` → ``GuidanceNote`` with intervention advice.
- ``days_in_stage(root, stage)`` → days spent in that stage, or None.
- ``is_ready_to_guide(root, today, min_days_observed)`` → bool.
- ``nebari_summary(log)`` → aggregate stats dict.

Notes:
- Only intervene when the plant is actively growing and healthy — the
  ``guidance_for()`` notes reflect this.
- All functions accept an explicit ``today`` date; no real-clock calls.

Usage::

    import datetime
    from plant_care.aerial_roots import (
        RootStage, RootEntry, AerialRoot, NebariLog,
        guidance_for, days_in_stage, is_ready_to_guide, nebari_summary,
    )

    root = AerialRoot(root_id="ar-01", specimen_id="ficus-01",
                      origin_description="right fork, 3 cm up")
    root.add_entry(RootEntry(stage=RootStage.TIP_PROMISING,
                             date=datetime.date(2024, 3, 1)))

    advice = guidance_for(RootStage.TIP_PROMISING)
    print(advice.action)   # "Observe and protect"
    print(advice.notes)    # Detailed guidance text
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ── RootStage ─────────────────────────────────────────────────────────────────


class RootStage(str, Enum):
    """Lifecycle stages of a guided aerial root.

    The expected progression is:
    TIP_PROMISING → GUIDED → REACHED_SOIL → THICKENING → FUSED.

    ABANDONED is a terminal state for a root that failed to develop or
    was deliberately removed (e.g. the guide broke, rot set in, or the
    design direction changed).
    """

    TIP_PROMISING = "tip_promising"   # Emerging aerial root spotted; viable tip
    GUIDED = "guided"                 # Guide attached (sphagnum/tube/wire)
    REACHED_SOIL = "reached_soil"     # Root tip has made contact with substrate
    THICKENING = "thickening"         # Root is visibly adding girth
    FUSED = "fused"                   # Root has fused to trunk or substrate
    ABANDONED = "abandoned"           # Guide removed; root not developed further


# Ordered progression (ABANDONED is a terminal side-branch)
_STAGE_ORDER = [
    RootStage.TIP_PROMISING,
    RootStage.GUIDED,
    RootStage.REACHED_SOIL,
    RootStage.THICKENING,
    RootStage.FUSED,
]
_STAGE_RANK: Dict[RootStage, int] = {s: i for i, s in enumerate(_STAGE_ORDER)}


# ── RootEntry ─────────────────────────────────────────────────────────────────


@dataclass
class RootEntry:
    """A dated lifecycle entry for one aerial root.

    Attributes
    ----------
    stage:
        The ``RootStage`` reached on *date*.
    date:
        Observation/intervention date (injected; no real-clock calls).
    notes:
        Free-text notes (guide type, humidity measurements, photos, etc.).
    """

    stage: RootStage
    date: datetime.date
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "stage": self.stage.value,
            "date": self.date.isoformat(),
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RootEntry":
        return cls(
            stage=RootStage(data["stage"]),
            date=datetime.date.fromisoformat(data["date"]),
            notes=data.get("notes", ""),
        )


# ── GuidanceNote ─────────────────────────────────────────────────────────────


@dataclass
class GuidanceNote:
    """Care advice for a given aerial-root lifecycle stage.

    Attributes
    ----------
    stage:
        The stage this guidance applies to.
    action:
        Short label for the primary action (e.g. ``"Wrap with sphagnum"``).
    notes:
        Detailed advisory text drawn from Ficus / bonsai horticultural
        practice.
    conditions:
        Prerequisite conditions before taking action (e.g. "plant must
        be actively growing").
    """

    stage: RootStage
    action: str
    notes: str
    conditions: str = ""

    def to_dict(self) -> dict:
        return {
            "stage": self.stage.value,
            "action": self.action,
            "notes": self.notes,
            "conditions": self.conditions,
        }


# ── Guidance table ────────────────────────────────────────────────────────────
#
# Grounded in Ficus bonsai practice and general aerial-root development
# guidance (humidity, substrate contact, avoidance of mechanical damage).

_GUIDANCE_TABLE: Dict[RootStage, GuidanceNote] = {
    RootStage.TIP_PROMISING: GuidanceNote(
        stage=RootStage.TIP_PROMISING,
        action="Observe and protect",
        notes=(
            "A promising aerial root tip has appeared.  Do not disturb or "
            "bend it yet — the root cap is fragile.  Photograph it to track "
            "length gain.  Maintain humidity above 60% in the local "
            "micro-climate (pebble tray or occasional misting near the root). "
            "Avoid repotting while the root is establishing."
        ),
        conditions="No action required; monitor weekly.",
    ),
    RootStage.GUIDED: GuidanceNote(
        stage=RootStage.GUIDED,
        action="Attach a guide toward the substrate",
        notes=(
            "Once the root is at least 2–3 cm long and visibly flexible, "
            "wrap the tip lightly with moist sphagnum moss to maintain "
            "humidity around the growing tip.  A thin bamboo tube, straw, "
            "or plastic sleeve can gently direct the root toward the "
            "substrate without creasing it.  Do not force — the root "
            "follows humidity gradients naturally.  Check monthly and "
            "re-moisten the sphagnum if it dries."
        ),
        conditions=(
            "Plant must be actively growing (spring or summer, northern "
            "hemisphere).  Health status must be 'healthy' — do not guide "
            "on a stressed or declining plant."
        ),
    ),
    RootStage.REACHED_SOIL: GuidanceNote(
        stage=RootStage.REACHED_SOIL,
        action="Allow contact with substrate; remove guide gently",
        notes=(
            "The root tip has reached the substrate.  Carefully remove the "
            "guide sleeve so as not to snap the root, but leave the sphagnum "
            "in place until the root has anchored (2–4 weeks).  The root "
            "will now begin to thicken as it starts to function as a "
            "conductor.  Keep the soil evenly moist to encourage the tip "
            "to penetrate."
        ),
        conditions="Soil contact must be confirmed visually before removing guide.",
    ),
    RootStage.THICKENING: GuidanceNote(
        stage=RootStage.THICKENING,
        action="Measure girth monthly; fertilise regularly",
        notes=(
            "The root is now conducting water and nutrients and will "
            "gradually add girth.  Measure diameter monthly at a fixed "
            "point (e.g. 5 cm above substrate) and log it in the scan "
            "record.  A balanced fertiliser at half strength every two "
            "weeks during active growth accelerates thickening.  Avoid "
            "disturbing or repositioning the root — movement breaks the "
            "cambial contact that drives girth gain."
        ),
        conditions="Continue normal growing-season care.",
    ),
    RootStage.FUSED: GuidanceNote(
        stage=RootStage.FUSED,
        action="Document for design record; no further intervention",
        notes=(
            "The root has fused with the trunk or substrate and is now "
            "structural.  Photograph the nebari spread and update the "
            "scan log with the final root diameter.  This root can now "
            "be considered part of the permanent trunk base.  Future "
            "styling decisions should treat it as a structural element. "
            "Nebari spread can still be encouraged by placing a flat stone "
            "or tile beneath the root to guide future surface growth."
        ),
        conditions="No further intervention required.",
    ),
    RootStage.ABANDONED: GuidanceNote(
        stage=RootStage.ABANDONED,
        action="Log abandonment; remove any guide material",
        notes=(
            "The root was not developed further.  Remove any guide material "
            "to prevent rot or mechanical damage.  Record the reason for "
            "abandonment (design change, root broke, plant health, etc.) "
            "in the notes.  Other roots on the plant are unaffected."
        ),
        conditions="None.",
    ),
}


# ── AerialRoot ────────────────────────────────────────────────────────────────


@dataclass
class AerialRoot:
    """A single tracked aerial root on one specimen.

    Attributes
    ----------
    root_id:
        Unique identifier for this root (e.g. ``"ar-01"``).
    specimen_id:
        ID of the host specimen.
    origin_description:
        Human-readable description of where on the plant this root originates
        (e.g. ``"right fork, 3 cm above first branch"``).
    entries:
        Ordered list of ``RootEntry`` lifecycle observations.
    notes:
        Root-level notes (target position, design intent, photos, etc.).
    """

    root_id: str
    specimen_id: str
    origin_description: str = ""
    entries: List[RootEntry] = field(default_factory=list)
    notes: str = ""

    # ── Mutation ──────────────────────────────────────────────────────────────

    def add_entry(self, entry: RootEntry) -> "AerialRoot":
        """Append *entry*.  Returns self for chaining."""
        self.entries.append(entry)
        self.entries.sort(key=lambda e: e.date)
        return self

    def advance_stage(
        self,
        stage: RootStage,
        date: datetime.date,
        notes: str = "",
    ) -> "AerialRoot":
        """Record a stage transition.  Convenience wrapper for add_entry."""
        return self.add_entry(RootEntry(stage=stage, date=date, notes=notes))

    # ── Queries ───────────────────────────────────────────────────────────────

    def current_stage(self) -> Optional[RootStage]:
        """Return the stage of the most recent entry, or None."""
        return self.entries[-1].stage if self.entries else None

    def first_entry(self) -> Optional[RootEntry]:
        return self.entries[0] if self.entries else None

    def latest_entry(self) -> Optional[RootEntry]:
        return self.entries[-1] if self.entries else None

    def entry_for_stage(self, stage: RootStage) -> Optional[RootEntry]:
        """Return the first entry at *stage*, or None."""
        return next((e for e in self.entries if e.stage == stage), None)

    def date_of_stage(self, stage: RootStage) -> Optional[datetime.date]:
        """Return the date *stage* was reached, or None."""
        e = self.entry_for_stage(stage)
        return e.date if e else None

    def is_active(self) -> bool:
        """True if the root is still being developed (not FUSED or ABANDONED)."""
        cs = self.current_stage()
        return cs not in (RootStage.FUSED, RootStage.ABANDONED, None)

    def is_fused(self) -> bool:
        return self.current_stage() == RootStage.FUSED

    def is_abandoned(self) -> bool:
        return self.current_stage() == RootStage.ABANDONED

    def age_days(self, today: datetime.date) -> Optional[int]:
        """Days since this root was first observed, or None."""
        fe = self.first_entry()
        return (today - fe.date).days if fe else None

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "root_id": self.root_id,
            "specimen_id": self.specimen_id,
            "origin_description": self.origin_description,
            "entries": [e.to_dict() for e in self.entries],
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AerialRoot":
        root = cls(
            root_id=data["root_id"],
            specimen_id=data["specimen_id"],
            origin_description=data.get("origin_description", ""),
            notes=data.get("notes", ""),
        )
        for e_data in data.get("entries", []):
            root.entries.append(RootEntry.from_dict(e_data))
        return root


# ── NebariLog ────────────────────────────────────────────────────────────────


class NebariLog:
    """Collection of all tracked aerial roots for one specimen.

    The log provides aggregate views (total roots, active, fused, abandoned)
    and is the entry-point for nebari spread analysis.
    """

    def __init__(self, specimen_id: str) -> None:
        self.specimen_id = specimen_id
        self._roots: Dict[str, AerialRoot] = {}

    def add_root(self, root: AerialRoot) -> "NebariLog":
        """Register *root*.  Raises ``ValueError`` on duplicate root_id."""
        if root.root_id in self._roots:
            raise ValueError(f"Root '{root.root_id}' already exists.")
        self._roots[root.root_id] = root
        return self

    def remove_root(self, root_id: str) -> bool:
        """Remove by root_id.  Returns True if found."""
        if root_id in self._roots:
            del self._roots[root_id]
            return True
        return False

    def get_root(self, root_id: str) -> AerialRoot:
        """Return root by ID.  Raises ``KeyError`` if not found."""
        try:
            return self._roots[root_id]
        except KeyError:
            raise KeyError(f"AerialRoot '{root_id}' not found.")

    def all_roots(self) -> List[AerialRoot]:
        return list(self._roots.values())

    def active_roots(self) -> List[AerialRoot]:
        return [r for r in self._roots.values() if r.is_active()]

    def fused_roots(self) -> List[AerialRoot]:
        return [r for r in self._roots.values() if r.is_fused()]

    def abandoned_roots(self) -> List[AerialRoot]:
        return [r for r in self._roots.values() if r.is_abandoned()]

    def roots_at_stage(self, stage: RootStage) -> List[AerialRoot]:
        return [r for r in self._roots.values() if r.current_stage() == stage]

    def __len__(self) -> int:
        return len(self._roots)

    def to_list(self) -> List[dict]:
        return [r.to_dict() for r in self.all_roots()]

    @classmethod
    def from_list(cls, specimen_id: str, data: List[dict]) -> "NebariLog":
        log = cls(specimen_id=specimen_id)
        for item in data:
            log.add_root(AerialRoot.from_dict(item))
        return log


# ── Pure functions ────────────────────────────────────────────────────────────


def guidance_for(stage: RootStage) -> GuidanceNote:
    """Return care guidance for the given ``RootStage``.

    The returned object is a shared singleton — do not mutate it.
    """
    return _GUIDANCE_TABLE[stage]


def days_in_stage(root: AerialRoot, stage: RootStage) -> Optional[int]:
    """Return the number of days the root has been (or was) in *stage*.

    For the current stage, returns days elapsed since that stage was
    entered (requires *today* to be meaningful — use
    ``days_in_current_stage()`` with an explicit date).

    For completed stages, returns the number of days before the next
    entry, or None if no subsequent entry exists.
    """
    stage_date = root.date_of_stage(stage)
    if stage_date is None:
        return None
    # Find the next entry after this stage date
    later = [
        e for e in root.entries
        if e.date > stage_date and e.stage != stage
    ]
    if not later:
        return None
    return (min(e.date for e in later) - stage_date).days


def days_in_current_stage(root: AerialRoot, today: datetime.date) -> Optional[int]:
    """Return days since the root's current stage was entered.

    Returns None if the root has no entries.
    """
    latest = root.latest_entry()
    if latest is None:
        return None
    return (today - latest.date).days


def is_ready_to_guide(
    root: AerialRoot,
    today: datetime.date,
    min_days_observed: int = 14,
) -> bool:
    """Return True if the root is ready to have a guide attached.

    A root is ready when:
    1. Its current stage is TIP_PROMISING.
    2. It has been observed for at least *min_days_observed* days
       (giving the root cap time to harden slightly and confirm viability).

    Args:
        root:               The aerial root to evaluate.
        today:              Reference date (injected).
        min_days_observed:  Minimum days at TIP_PROMISING before guiding.
                            Default 14 days follows common practice of
                            waiting 2 weeks for the tip to confirm growth.

    Returns:
        True if both conditions are met.
    """
    if root.current_stage() != RootStage.TIP_PROMISING:
        return False
    first_observed = root.date_of_stage(RootStage.TIP_PROMISING)
    if first_observed is None:
        return False
    return (today - first_observed).days >= min_days_observed


def nebari_summary(log: NebariLog) -> dict:
    """Return aggregate statistics for all roots in *log*.

    Keys:
    - ``total_roots`` — total number of tracked roots.
    - ``active`` — roots not yet FUSED or ABANDONED.
    - ``fused`` — roots that have reached FUSED.
    - ``abandoned`` — roots that were ABANDONED.
    - ``by_stage`` — dict of stage → count.
    - ``success_rate`` — fraction of resolved roots that fused.
    """
    all_r = log.all_roots()
    fused = log.fused_roots()
    abandoned = log.abandoned_roots()

    resolved = len(fused) + len(abandoned)
    success_rate = len(fused) / resolved if resolved > 0 else 0.0

    by_stage: Dict[str, int] = {s.value: 0 for s in RootStage}
    for root in all_r:
        cs = root.current_stage()
        if cs:
            by_stage[cs.value] += 1

    return {
        "total_roots": len(all_r),
        "active": len(log.active_roots()),
        "fused": len(fused),
        "abandoned": len(abandoned),
        "by_stage": by_stage,
        "success_rate": success_rate,
    }
