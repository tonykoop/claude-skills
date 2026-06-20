"""Propagation log and specimen lineage tracker.

Records propagation attempts (cuttings, seeds, air-layers, divisions, grafts),
tracks success/failure, and resolves ancestor/descendant chains across a
``Collection``.

No real-clock calls — every method that needs a date accepts an explicit
``today`` parameter.

Usage::

    from plant_care.propagation import PropagationLog, PropagationMethod
    import datetime

    log = PropagationLog()
    log.add_attempt(
        attempt_id="prop-01",
        parent_id="jp-01",
        child_id=None,          # not yet potted up
        method=PropagationMethod.CUTTING,
        date=datetime.date(2024, 3, 1),
        notes="Tip cutting from primary trunk leader",
    )
    log.record_outcome("prop-01", success=True, child_id="jp-02")

    # Lineage queries
    log.ancestors_of("jp-02")     # → ["jp-01"]
    log.descendants_of("jp-01")   # → ["jp-02"]
    log.success_rate(PropagationMethod.CUTTING)  # → float in [0, 1]
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


# ── PropagationMethod ─────────────────────────────────────────────────────────


class PropagationMethod(str, Enum):
    """Recognised propagation techniques."""

    CUTTING = "cutting"          # stem or leaf cutting rooted in substrate
    SEED = "seed"                # grown from seed
    AIR_LAYER = "air-layer"      # aerial layering (marcotting)
    DIVISION = "division"        # root-ball division of a clumping plant
    GRAFT = "graft"              # scion grafted onto rootstock
    OFFSET = "offset"            # pup / sucker removed and potted separately


# ── PropagationAttempt ────────────────────────────────────────────────────────


@dataclass
class PropagationAttempt:
    """A single propagation attempt, which may or may not have succeeded.

    Attributes
    ----------
    attempt_id:
        Unique slug for this attempt (e.g. ``"prop-2024-01"``).
    parent_id:
        Specimen id of the source plant (must exist in the calling Collection,
        but the PropagationLog itself does not enforce FK — callers may cross-
        validate if needed).
    child_id:
        Specimen id of the newly potted plant once the attempt succeeded.
        ``None`` until the outcome is recorded.
    method:
        Propagation technique used.
    date:
        Date the attempt was started (cutting taken, seed sown, etc.).
    success:
        ``True`` if the propagation succeeded, ``False`` if it failed,
        ``None`` if the outcome is not yet known.
    notes:
        Free-text notes about the attempt.
    outcome_date:
        Date the outcome was recorded (potted up or declared failed).
    """

    attempt_id: str
    parent_id: str
    child_id: Optional[str]
    method: PropagationMethod
    date: datetime.date
    success: Optional[bool] = None
    notes: str = ""
    outcome_date: Optional[datetime.date] = None

    @property
    def is_pending(self) -> bool:
        """True if the outcome has not yet been recorded."""
        return self.success is None

    @property
    def days_since_attempt(self) -> Optional[int]:
        """Always None without an injected 'today' — use age_days(today) instead."""
        return None

    def age_days(self, today: datetime.date) -> int:
        """Return how many days have elapsed since the attempt was started."""
        return (today - self.date).days

    def to_dict(self) -> dict:
        return {
            "attempt_id": self.attempt_id,
            "parent_id": self.parent_id,
            "child_id": self.child_id,
            "method": self.method.value,
            "date": self.date.isoformat(),
            "success": self.success,
            "notes": self.notes,
            "outcome_date": (
                self.outcome_date.isoformat() if self.outcome_date else None
            ),
        }


# ── PropagationLog ────────────────────────────────────────────────────────────


class PropagationLog:
    """Registry of propagation attempts and the lineage graph they encode.

    The log maintains two internal indices:
    - ``_attempts``: ``attempt_id → PropagationAttempt``
    - ``_parent_of``: ``child_id → parent_id`` (for successful attempts only)

    These indices are updated atomically by ``add_attempt()`` and
    ``record_outcome()``.
    """

    def __init__(self) -> None:
        self._attempts: Dict[str, PropagationAttempt] = {}
        # child_id → parent_id for successful attempts
        self._parent_of: Dict[str, str] = {}

    # ── Mutation API ──────────────────────────────────────────────────────────

    def add_attempt(
        self,
        *,
        attempt_id: str,
        parent_id: str,
        method: PropagationMethod,
        date: datetime.date,
        child_id: Optional[str] = None,
        success: Optional[bool] = None,
        notes: str = "",
        outcome_date: Optional[datetime.date] = None,
    ) -> "PropagationLog":
        """Register a new propagation attempt.

        If *attempt_id* is already registered, a ``ValueError`` is raised.
        If *success* is ``True`` and *child_id* is provided, the lineage
        index is updated immediately.
        """
        if attempt_id in self._attempts:
            raise ValueError(
                f"Propagation attempt '{attempt_id}' already exists."
            )
        attempt = PropagationAttempt(
            attempt_id=attempt_id,
            parent_id=parent_id,
            child_id=child_id,
            method=method,
            date=date,
            success=success,
            notes=notes,
            outcome_date=outcome_date,
        )
        self._attempts[attempt_id] = attempt
        if success is True and child_id:
            self._parent_of[child_id] = parent_id
        return self

    def record_outcome(
        self,
        attempt_id: str,
        *,
        success: bool,
        child_id: Optional[str] = None,
        outcome_date: Optional[datetime.date] = None,
        notes: Optional[str] = None,
    ) -> "PropagationLog":
        """Record the outcome of a pending propagation attempt.

        Raises
        ------
        KeyError
            If *attempt_id* is not found.
        ValueError
            If the outcome was already recorded.
        ValueError
            If *success* is True but no *child_id* is provided.
        """
        attempt = self._get_attempt(attempt_id)
        if attempt.success is not None:
            raise ValueError(
                f"Outcome for attempt '{attempt_id}' already recorded "
                f"(success={attempt.success})."
            )
        if success and child_id is None:
            raise ValueError(
                "child_id is required when recording a successful propagation."
            )
        attempt.success = success
        attempt.outcome_date = outcome_date
        if notes is not None:
            attempt.notes = notes
        if success and child_id:
            attempt.child_id = child_id
            self._parent_of[child_id] = attempt.parent_id
        return self

    # ── Lookup API ────────────────────────────────────────────────────────────

    def get(self, attempt_id: str) -> PropagationAttempt:
        """Return the PropagationAttempt for *attempt_id*.

        Raises
        ------
        KeyError
            If not found.
        """
        return self._get_attempt(attempt_id)

    def all_attempts(self) -> List[PropagationAttempt]:
        """Return all attempts in insertion order."""
        return list(self._attempts.values())

    def attempts_from(self, parent_id: str) -> List[PropagationAttempt]:
        """Return all attempts whose source is *parent_id*."""
        return [a for a in self._attempts.values() if a.parent_id == parent_id]

    def successful(self) -> List[PropagationAttempt]:
        """Return all attempts that succeeded."""
        return [a for a in self._attempts.values() if a.success is True]

    def failed(self) -> List[PropagationAttempt]:
        """Return all attempts that failed."""
        return [a for a in self._attempts.values() if a.success is False]

    def pending(self) -> List[PropagationAttempt]:
        """Return all attempts whose outcome is not yet known."""
        return [a for a in self._attempts.values() if a.success is None]

    def by_method(self, method: PropagationMethod) -> List[PropagationAttempt]:
        """Return all attempts using the given propagation method."""
        return [a for a in self._attempts.values() if a.method == method]

    # ── Lineage API ───────────────────────────────────────────────────────────

    def parent_of(self, child_id: str) -> Optional[str]:
        """Return the direct parent specimen id of *child_id*, or None."""
        return self._parent_of.get(child_id)

    def ancestors_of(self, specimen_id: str) -> List[str]:
        """Return the ordered ancestor chain for *specimen_id*.

        The list is ordered from immediate parent to oldest known ancestor.
        Returns an empty list if *specimen_id* has no recorded parent.

        Cycles (impossible in well-formed data, but guarded against) are
        broken after visiting each node at most once.
        """
        chain: List[str] = []
        visited: Set[str] = {specimen_id}
        current = self._parent_of.get(specimen_id)
        while current is not None and current not in visited:
            chain.append(current)
            visited.add(current)
            current = self._parent_of.get(current)
        return chain

    def descendants_of(self, specimen_id: str) -> List[str]:
        """Return all descendant specimen ids of *specimen_id* (BFS order).

        A descendant is any specimen whose ancestor chain includes
        *specimen_id*.  Returns an empty list if no children exist.
        """
        # Build reverse index: parent → [children]
        children_of: Dict[str, List[str]] = {}
        for child, parent in self._parent_of.items():
            children_of.setdefault(parent, []).append(child)

        result: List[str] = []
        queue: List[str] = list(children_of.get(specimen_id, []))
        visited: Set[str] = {specimen_id}
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            result.append(node)
            queue.extend(children_of.get(node, []))
        return result

    def lineage_tree(self, specimen_id: str) -> dict:
        """Return the full lineage tree rooted at *specimen_id* as a dict.

        Format::

            {
              "id": "<specimen_id>",
              "children": [
                {"id": "<child_id>", "children": [...], "method": "<method>"},
                ...
              ]
            }
        """
        # Build reverse: parent → [(child_id, method)]
        children_of: Dict[str, List[tuple]] = {}
        for attempt in self.successful():
            if attempt.child_id:
                children_of.setdefault(attempt.parent_id, []).append(
                    (attempt.child_id, attempt.method.value)
                )

        def _build(sid: str, visited: Set[str]) -> dict:
            node: dict = {"id": sid, "children": []}
            for child_id, method in children_of.get(sid, []):
                if child_id not in visited:
                    visited.add(child_id)
                    child_node = _build(child_id, visited)
                    child_node["method"] = method
                    node["children"].append(child_node)
            return node

        return _build(specimen_id, {specimen_id})

    # ── Statistics ────────────────────────────────────────────────────────────

    def success_rate(self, method: Optional[PropagationMethod] = None) -> float:
        """Return the proportion of resolved attempts that succeeded.

        Parameters
        ----------
        method:
            If provided, limit the calculation to attempts using this method.
            If None, calculate across all attempts.

        Returns
        -------
        float
            A value in [0.0, 1.0].  Returns 0.0 if there are no resolved
            attempts (pending-only data or empty log).
        """
        pool = self.by_method(method) if method else self.all_attempts()
        resolved = [a for a in pool if a.success is not None]
        if not resolved:
            return 0.0
        successes = sum(1 for a in resolved if a.success is True)
        return successes / len(resolved)

    def attempt_count_by_method(self) -> Dict[str, int]:
        """Return a count of attempts per method value string."""
        result: Dict[str, int] = {}
        for a in self._attempts.values():
            result[a.method.value] = result.get(a.method.value, 0) + 1
        return result

    def pending_older_than(
        self, today: datetime.date, days: int
    ) -> List[PropagationAttempt]:
        """Return pending attempts that are older than *days* days.

        Useful for surfacing long-running propagation attempts that may need
        assessment (e.g. a cutting that hasn't rooted after 6 weeks).
        """
        return [
            a for a in self.pending()
            if a.age_days(today) > days
        ]

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_list(self) -> List[dict]:
        """Return a JSON-safe list of all attempt dicts."""
        return [a.to_dict() for a in self._attempts.values()]

    @classmethod
    def from_list(cls, data: List[dict]) -> "PropagationLog":
        """Reconstruct a PropagationLog from a ``to_list()`` payload."""
        log = cls()
        for entry in data:
            log.add_attempt(
                attempt_id=entry["attempt_id"],
                parent_id=entry["parent_id"],
                child_id=entry.get("child_id"),
                method=PropagationMethod(entry["method"]),
                date=datetime.date.fromisoformat(entry["date"]),
                success=entry.get("success"),
                notes=entry.get("notes", ""),
                outcome_date=(
                    datetime.date.fromisoformat(entry["outcome_date"])
                    if entry.get("outcome_date")
                    else None
                ),
            )
        return log

    # ── Internal ──────────────────────────────────────────────────────────────

    def _get_attempt(self, attempt_id: str) -> PropagationAttempt:
        try:
            return self._attempts[attempt_id]
        except KeyError:
            raise KeyError(
                f"Propagation attempt '{attempt_id}' not found."
            )

    def __len__(self) -> int:
        return len(self._attempts)
