"""Photogrammetry and scan-metadata model.

Tracks geometric measurements derived from photogrammetry scans or manual
measurement sessions.  Particularly useful for bonsai development tracking
(trunk thickening, nebari spread, canopy dimensions, height) and general
growth monitoring over time.

Key objects:

- ``ScaleCalibration`` — maps a reference-object measurement (in scan units)
  to real-world millimetres.  E.g. you placed a 10 mm hex nut in the frame
  and measured it as 47.3 px → 10 / 47.3 mm/px.
- ``ScanMeasurement`` — a named measurement (e.g. ``"trunk_diameter_mm"``)
  with a real-world value in mm and a confidence rating.
- ``ScanSession`` — a dated set of measurements taken in one pass, optionally
  with a ``ScaleCalibration``.
- ``ScanLog`` — ordered history of ``ScanSession`` objects for one specimen.

Pure functions:

- ``growth_delta(session_a, session_b)`` → dict of name → delta in mm for
  all measurements shared by both sessions.
- ``growth_rate(log, name, today)`` → average mm/day growth over the full log
  for the named measurement (None if fewer than 2 data points).
- ``latest_measurement(log, name)`` → the most recent value in mm, or None.
- ``measurement_history(log, name)`` → ordered ``(date, value_mm)`` pairs.

No I/O, no real-clock calls.

Usage::

    import datetime
    from plant_care.scan import (
        ScaleCalibration, ScanMeasurement, ScanSession, ScanLog,
        growth_delta, growth_rate, latest_measurement, measurement_history,
    )

    cal = ScaleCalibration(
        reference_name="10mm hex nut",
        reference_real_mm=10.0,
        reference_measured_units=47.3,   # pixels
    )
    # cal.mm_per_unit → 0.2114...

    session_1 = ScanSession(
        session_id="s01",
        specimen_id="jp-01",
        date=datetime.date(2024, 3, 1),
        calibration=cal,
        measurements=[
            ScanMeasurement(name="trunk_diameter_mm", value_mm=18.5),
            ScanMeasurement(name="height_mm", value_mm=310.0),
        ],
    )
    session_2 = ScanSession(
        session_id="s02",
        specimen_id="jp-01",
        date=datetime.date(2024, 6, 1),
        measurements=[
            ScanMeasurement(name="trunk_diameter_mm", value_mm=19.2),
            ScanMeasurement(name="height_mm", value_mm=315.0),
        ],
    )
    log = ScanLog(specimen_id="jp-01")
    log.add_session(session_1)
    log.add_session(session_2)

    delta = growth_delta(session_1, session_2)
    # {"trunk_diameter_mm": 0.7, "height_mm": 5.0}

    rate = growth_rate(log, "trunk_diameter_mm", datetime.date(2024, 6, 1))
    # ≈ 0.0076 mm/day  (0.7 mm over 92 days)
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── ScaleCalibration ──────────────────────────────────────────────────────────


@dataclass
class ScaleCalibration:
    """Maps a scan-unit measurement of a reference object to real-world mm.

    Attributes
    ----------
    reference_name:
        Human-readable label for the reference object
        (e.g. ``"10mm hex nut"``, ``"ruler at 10mm mark"``).
    reference_real_mm:
        The known real-world size of the reference object in millimetres.
    reference_measured_units:
        The measured size of the reference object in the scan's native units
        (pixels, point-cloud units, etc.).
    notes:
        Free-text notes (scanner model, distance, lighting, etc.).
    """

    reference_name: str
    reference_real_mm: float        # known size in mm
    reference_measured_units: float  # size as measured in the scan
    notes: str = ""

    def __post_init__(self) -> None:
        if self.reference_real_mm <= 0:
            raise ValueError(
                f"reference_real_mm must be positive; got {self.reference_real_mm}"
            )
        if self.reference_measured_units <= 0:
            raise ValueError(
                f"reference_measured_units must be positive; "
                f"got {self.reference_measured_units}"
            )

    @property
    def mm_per_unit(self) -> float:
        """Conversion factor: real-world mm per one scan unit."""
        return self.reference_real_mm / self.reference_measured_units

    def to_real_mm(self, scan_units: float) -> float:
        """Convert a scan-unit measurement to real-world mm."""
        return scan_units * self.mm_per_unit

    def to_dict(self) -> dict:
        return {
            "reference_name": self.reference_name,
            "reference_real_mm": self.reference_real_mm,
            "reference_measured_units": self.reference_measured_units,
            "mm_per_unit": self.mm_per_unit,
            "notes": self.notes,
        }


# ── ScanMeasurement ───────────────────────────────────────────────────────────


CONFIDENCE_LEVELS = {"high", "medium", "low"}


@dataclass
class ScanMeasurement:
    """A single named measurement from a scan or manual measurement session.

    Values are always stored in millimetres; convert beforehand if needed.

    Attributes
    ----------
    name:
        Identifier for this measurement
        (e.g. ``"trunk_diameter_mm"``, ``"height_mm"``, ``"nebari_spread_mm"``).
    value_mm:
        Measured value in millimetres.
    confidence:
        Subjective quality rating: ``"high"``, ``"medium"``, or ``"low"``.
        Default is ``"medium"``.
    notes:
        Free-text notes about this measurement (method, location, etc.).
    """

    name: str
    value_mm: float
    confidence: str = "medium"
    notes: str = ""

    def __post_init__(self) -> None:
        if self.confidence not in CONFIDENCE_LEVELS:
            raise ValueError(
                f"confidence must be one of {sorted(CONFIDENCE_LEVELS)}; "
                f"got '{self.confidence}'"
            )
        if self.value_mm < 0:
            raise ValueError(
                f"value_mm must be non-negative; got {self.value_mm}"
            )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value_mm": self.value_mm,
            "confidence": self.confidence,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScanMeasurement":
        return cls(
            name=data["name"],
            value_mm=data["value_mm"],
            confidence=data.get("confidence", "medium"),
            notes=data.get("notes", ""),
        )

    @classmethod
    def from_scan_units(
        cls,
        name: str,
        scan_units: float,
        calibration: ScaleCalibration,
        *,
        confidence: str = "medium",
        notes: str = "",
    ) -> "ScanMeasurement":
        """Construct from a raw scan-unit measurement and a calibration.

        The conversion ``scan_units × calibration.mm_per_unit → mm`` is
        applied automatically.
        """
        return cls(
            name=name,
            value_mm=calibration.to_real_mm(scan_units),
            confidence=confidence,
            notes=notes,
        )


# ── ScanSession ───────────────────────────────────────────────────────────────


@dataclass
class ScanSession:
    """A dated set of measurements taken in one scan or measurement pass.

    Attributes
    ----------
    session_id:
        Unique identifier for this session.
    specimen_id:
        ID of the specimen this session belongs to.
    date:
        Date the scan/measurement was taken (injected; no real-clock calls).
    measurements:
        List of ``ScanMeasurement`` objects captured in this session.
    calibration:
        Optional ``ScaleCalibration`` used for this session.  Stored for
        provenance; measurements are already converted to mm before storage.
    notes:
        Free-text session notes (equipment, conditions, observer, etc.).
    """

    session_id: str
    specimen_id: str
    date: datetime.date
    measurements: List[ScanMeasurement] = field(default_factory=list)
    calibration: Optional[ScaleCalibration] = None
    notes: str = ""

    def add_measurement(self, measurement: ScanMeasurement) -> "ScanSession":
        """Append a measurement.  Returns self for chaining."""
        self.measurements.append(measurement)
        return self

    def get_measurement(self, name: str) -> Optional[ScanMeasurement]:
        """Return the first measurement with *name*, or None."""
        return next((m for m in self.measurements if m.name == name), None)

    def value_mm(self, name: str) -> Optional[float]:
        """Return the ``value_mm`` for the named measurement, or None."""
        m = self.get_measurement(name)
        return m.value_mm if m else None

    def measurement_names(self) -> List[str]:
        """Return deduplicated list of measurement names in this session."""
        seen = set()
        out = []
        for m in self.measurements:
            if m.name not in seen:
                seen.add(m.name)
                out.append(m.name)
        return out

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "specimen_id": self.specimen_id,
            "date": self.date.isoformat(),
            "measurements": [m.to_dict() for m in self.measurements],
            "calibration": self.calibration.to_dict() if self.calibration else None,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScanSession":
        cal_data = data.get("calibration")
        calibration = None
        if cal_data:
            calibration = ScaleCalibration(
                reference_name=cal_data["reference_name"],
                reference_real_mm=cal_data["reference_real_mm"],
                reference_measured_units=cal_data["reference_measured_units"],
                notes=cal_data.get("notes", ""),
            )
        return cls(
            session_id=data["session_id"],
            specimen_id=data["specimen_id"],
            date=datetime.date.fromisoformat(data["date"]),
            measurements=[ScanMeasurement.from_dict(m) for m in data.get("measurements", [])],
            calibration=calibration,
            notes=data.get("notes", ""),
        )


# ── ScanLog ───────────────────────────────────────────────────────────────────


class ScanLog:
    """Ordered history of scan sessions for one specimen.

    Sessions are stored in chronological order by date.  Adding a session
    out of order triggers a sort so the log stays consistently ordered.

    Raises
    ------
    ValueError
        If a session with the same ``session_id`` is added twice.
    """

    def __init__(self, specimen_id: str) -> None:
        self.specimen_id = specimen_id
        self._sessions: List[ScanSession] = []
        self._ids: set = set()

    def add_session(self, session: ScanSession) -> "ScanLog":
        """Add *session* to the log.  Returns self for chaining."""
        if session.session_id in self._ids:
            raise ValueError(
                f"Session '{session.session_id}' already exists in the log."
            )
        self._sessions.append(session)
        self._ids.add(session.session_id)
        # Keep sorted by date (stable sort preserves insertion order for ties)
        self._sessions.sort(key=lambda s: s.date)
        return self

    def get_session(self, session_id: str) -> ScanSession:
        """Return a session by ID.

        Raises
        ------
        KeyError
            If *session_id* is not found.
        """
        for s in self._sessions:
            if s.session_id == session_id:
                return s
        raise KeyError(f"Session '{session_id}' not found.")

    def all_sessions(self) -> List[ScanSession]:
        """Return all sessions in chronological order."""
        return list(self._sessions)

    def latest_session(self) -> Optional[ScanSession]:
        """Return the most recent session, or None if the log is empty."""
        return self._sessions[-1] if self._sessions else None

    def earliest_session(self) -> Optional[ScanSession]:
        """Return the earliest session, or None if the log is empty."""
        return self._sessions[0] if self._sessions else None

    def __len__(self) -> int:
        return len(self._sessions)

    def to_list(self) -> List[dict]:
        return [s.to_dict() for s in self._sessions]

    @classmethod
    def from_list(cls, specimen_id: str, data: List[dict]) -> "ScanLog":
        log = cls(specimen_id=specimen_id)
        for item in data:
            log.add_session(ScanSession.from_dict(item))
        return log


# ── Pure functions ────────────────────────────────────────────────────────────


def growth_delta(
    session_a: ScanSession,
    session_b: ScanSession,
) -> Dict[str, float]:
    """Return per-measurement deltas (``session_b − session_a``) in mm.

    Only measurements present in **both** sessions are included.
    Positive values indicate growth; negative values indicate shrinkage
    (which can happen legitimately, e.g. trunk diameter fluctuates with
    hydration, height may be reduced by pruning).

    Args:
        session_a:  Earlier session.
        session_b:  Later session (order is not enforced; the sign of the
                    delta follows ``b - a`` regardless of date ordering).

    Returns:
        ``dict[measurement_name, delta_mm]`` for each shared measurement.
    """
    shared_names = set(session_a.measurement_names()) & set(session_b.measurement_names())
    return {
        name: session_b.value_mm(name) - session_a.value_mm(name)
        for name in shared_names
        if session_a.value_mm(name) is not None and session_b.value_mm(name) is not None
    }


def measurement_history(
    log: ScanLog,
    name: str,
) -> List[Tuple[datetime.date, float]]:
    """Return all (date, value_mm) pairs for *name* across the log.

    Sessions where *name* is absent are silently skipped.
    Returned in chronological order.
    """
    pairs: List[Tuple[datetime.date, float]] = []
    for session in log.all_sessions():
        v = session.value_mm(name)
        if v is not None:
            pairs.append((session.date, v))
    return pairs


def latest_measurement(log: ScanLog, name: str) -> Optional[float]:
    """Return the most recent value_mm for *name*, or None if not recorded."""
    history = measurement_history(log, name)
    return history[-1][1] if history else None


def growth_rate(
    log: ScanLog,
    name: str,
    today: datetime.date,
) -> Optional[float]:
    """Return the average growth rate in mm/day for *name* over the log.

    Uses a simple linear regression: total delta divided by total days.
    Returns ``None`` if fewer than two data points are available, or if
    the time span is zero.

    Args:
        log:    The scan log to analyse.
        name:   The measurement name to compute the rate for.
        today:  Reference date (used only when the log has one entry — not
                applicable in the linear case; provided for API consistency
                and future per-period weighting).

    Returns:
        Average mm/day, or ``None`` if insufficient data.
    """
    history = measurement_history(log, name)
    if len(history) < 2:
        return None
    first_date, first_val = history[0]
    last_date, last_val = history[-1]
    total_days = (last_date - first_date).days
    if total_days == 0:
        return None
    return (last_val - first_val) / total_days


def measurement_summary(log: ScanLog, name: str) -> dict:
    """Return a summary dict for *name* across the full log.

    Keys:
    - ``name`` — the measurement name.
    - ``count`` — number of data points.
    - ``latest_mm`` — most recent value, or None.
    - ``earliest_mm`` — oldest value, or None.
    - ``total_delta_mm`` — latest minus earliest, or None if < 2 points.
    - ``growth_rate_mm_per_day`` — average growth rate, or None.
    - ``min_mm`` — minimum recorded value.
    - ``max_mm`` — maximum recorded value.
    - ``history`` — list of ``{"date": str, "value_mm": float}`` dicts.
    """
    history = measurement_history(log, name)
    if not history:
        return {
            "name": name,
            "count": 0,
            "latest_mm": None,
            "earliest_mm": None,
            "total_delta_mm": None,
            "growth_rate_mm_per_day": None,
            "min_mm": None,
            "max_mm": None,
            "history": [],
        }

    values = [v for _, v in history]
    latest_d, latest_v = history[-1]
    earliest_d, earliest_v = history[0]

    return {
        "name": name,
        "count": len(history),
        "latest_mm": latest_v,
        "earliest_mm": earliest_v,
        "total_delta_mm": (latest_v - earliest_v) if len(history) >= 2 else None,
        "growth_rate_mm_per_day": growth_rate(log, name, latest_d),
        "min_mm": min(values),
        "max_mm": max(values),
        "history": [
            {"date": d.isoformat(), "value_mm": v}
            for d, v in history
        ],
    }
