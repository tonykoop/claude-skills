"""Environment-zone (light/humidity) model.

Models named zones within a growing space (rooms, window sills, greenhouse
benches, etc.) and matches specimens/profiles against them to identify good
placements and expose mismatches.

Key objects:
- ``LightLevel`` — descriptive light-level enum (dark to full-sun).
- ``Zone`` — a named growing area with light level, humidity range, and
  temperature range.
- ``ZoneCollection`` — registry of all zones in a space.
- ``ZoneMatch`` / ``MatchQuality`` — the result of evaluating whether a
  specimen's care profile is compatible with a zone.
- ``match_zone(profile, zone)`` → ``ZoneMatch``.
- ``best_zone(profile, zones)`` → the best-fit ``Zone`` from a collection.

No I/O, no real-clock calls.

Usage::

    from plant_care.zones import Zone, ZoneCollection, LightLevel, match_zone
    from plant_care.models import CareProfile

    balcony = Zone(
        name="South balcony",
        light_level=LightLevel.FULL_SUN,
        humidity_percent=45,
        temp_min_c=10,
        temp_max_c=35,
    )
    profile = CareProfile(
        watering_interval_days=3, fertilize_interval_days=14,
        light_needs="full-sun", humidity="low",
    )
    result = match_zone(profile, balcony)
    print(result.quality)   # MatchQuality.GOOD
    print(result.reasons)   # []
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ── LightLevel ─────────────────────────────────────────────────────────────────


class LightLevel(str, Enum):
    """Ordered descriptive light levels, from darkest to brightest."""

    DARK = "dark"                    # < 50 lux; windowless interior
    LOW = "low"                      # 50–200 lux; north-facing, deep interior
    MEDIUM = "medium"                # 200–800 lux; bright interior, no direct sun
    BRIGHT_INDIRECT = "bright-indirect"  # 800–2000 lux; near window, diffused
    BRIGHT_DIRECT = "bright-direct"  # 2000–10000 lux; direct sun part of the day
    FULL_SUN = "full-sun"            # > 10000 lux; unobstructed outdoor sun


# Numeric rank for comparison (higher = more light)
_LIGHT_RANK: Dict[LightLevel, int] = {
    LightLevel.DARK: 0,
    LightLevel.LOW: 1,
    LightLevel.MEDIUM: 2,
    LightLevel.BRIGHT_INDIRECT: 3,
    LightLevel.BRIGHT_DIRECT: 4,
    LightLevel.FULL_SUN: 5,
}


# ── Humidity strings to numeric range ────────────────────────────────────────

# Maps the CareProfile.humidity strings to an acceptable % range
_HUMIDITY_RANGES: Dict[str, Tuple[int, int]] = {
    "high": (60, 100),
    "moderate": (40, 70),
    "low": (20, 50),
}

# Maps the CareProfile.light_needs string to a LightLevel
_LIGHT_NEEDS_MAP: Dict[str, LightLevel] = {
    "dark": LightLevel.DARK,
    "low": LightLevel.LOW,
    "medium": LightLevel.MEDIUM,
    "bright-indirect": LightLevel.BRIGHT_INDIRECT,
    "bright-direct": LightLevel.BRIGHT_DIRECT,
    "full-sun": LightLevel.FULL_SUN,
}


# ── MatchQuality ──────────────────────────────────────────────────────────────


class MatchQuality(str, Enum):
    """Qualitative result of a zone-match evaluation."""

    GOOD = "good"              # All key requirements met
    ACCEPTABLE = "acceptable"  # Minor mismatches that can be mitigated
    POOR = "poor"              # Significant mismatch; plant would struggle


# ── Zone ──────────────────────────────────────────────────────────────────────


@dataclass
class Zone:
    """A named growing area with environmental parameters.

    Attributes
    ----------
    name:
        Human-readable identifier (e.g. "South windowsill", "Greenhouse bench A").
    light_level:
        Dominant ambient light level in this zone.
    humidity_percent:
        Typical relative humidity in percent (0–100).
    temp_min_c:
        Typical minimum temperature in °C (winter night minimum).
    temp_max_c:
        Typical maximum temperature in °C (summer day maximum).
    notes:
        Free-text notes about the zone (orientation, obstructions, etc.).
    """

    name: str
    light_level: LightLevel
    humidity_percent: float  # 0–100
    temp_min_c: float = 5.0
    temp_max_c: float = 30.0
    notes: str = ""

    def __post_init__(self) -> None:
        if not (0 <= self.humidity_percent <= 100):
            raise ValueError(
                f"humidity_percent must be in [0, 100]; got {self.humidity_percent}"
            )
        if self.temp_min_c >= self.temp_max_c:
            raise ValueError(
                f"temp_min_c ({self.temp_min_c}) must be less than "
                f"temp_max_c ({self.temp_max_c})"
            )

    @property
    def light_rank(self) -> int:
        return _LIGHT_RANK[self.light_level]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "light_level": self.light_level.value,
            "humidity_percent": self.humidity_percent,
            "temp_min_c": self.temp_min_c,
            "temp_max_c": self.temp_max_c,
            "notes": self.notes,
        }


# ── ZoneMatch ─────────────────────────────────────────────────────────────────


@dataclass
class ZoneMatch:
    """Result of evaluating a CareProfile against a Zone.

    Attributes
    ----------
    zone:
        The zone that was evaluated.
    quality:
        Overall match quality.
    reasons:
        List of mismatch reasons (empty if ``quality == GOOD``).
    mitigations:
        Suggested mitigations for ``ACCEPTABLE`` mismatches.
    light_ok:
        Whether light is adequate.
    humidity_ok:
        Whether humidity is within the acceptable range.
    """

    zone: Zone
    quality: MatchQuality
    reasons: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    light_ok: bool = True
    humidity_ok: bool = True

    def to_dict(self) -> dict:
        return {
            "zone_name": self.zone.name,
            "quality": self.quality.value,
            "reasons": self.reasons,
            "mitigations": self.mitigations,
            "light_ok": self.light_ok,
            "humidity_ok": self.humidity_ok,
        }


# ── ZoneCollection ────────────────────────────────────────────────────────────


class ZoneCollection:
    """Registry of all named zones in a growing space.

    Zones are keyed by name.  Names are case-sensitive.
    """

    def __init__(self, name: str = "My Space") -> None:
        self.name = name
        self._zones: Dict[str, Zone] = {}

    def add(self, zone: Zone) -> "ZoneCollection":
        """Register a zone.

        Raises
        ------
        ValueError
            If a zone with the same name already exists.
        """
        if zone.name in self._zones:
            raise ValueError(
                f"Zone '{zone.name}' already exists in '{self.name}'."
            )
        self._zones[zone.name] = zone
        return self

    def remove(self, name: str) -> bool:
        """Remove a zone by name.  Returns True if found."""
        if name in self._zones:
            del self._zones[name]
            return True
        return False

    def get(self, name: str) -> Zone:
        """Return a zone by name.

        Raises
        ------
        KeyError
            If not found.
        """
        try:
            return self._zones[name]
        except KeyError:
            raise KeyError(f"Zone '{name}' not found in '{self.name}'.")

    def all_zones(self) -> List[Zone]:
        return list(self._zones.values())

    def __len__(self) -> int:
        return len(self._zones)

    def __contains__(self, name: str) -> bool:
        return name in self._zones

    def zones_by_light(self, level: LightLevel) -> List[Zone]:
        """Return all zones with the given light level."""
        return [z for z in self._zones.values() if z.light_level == level]

    def brightest(self) -> Optional[Zone]:
        """Return the zone with the highest light rank, or None if empty."""
        if not self._zones:
            return None
        return max(self._zones.values(), key=lambda z: z.light_rank)

    def darkest(self) -> Optional[Zone]:
        """Return the zone with the lowest light rank, or None if empty."""
        if not self._zones:
            return None
        return min(self._zones.values(), key=lambda z: z.light_rank)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "zones": [z.to_dict() for z in self._zones.values()],
        }


# ── match_zone ────────────────────────────────────────────────────────────────


def match_zone(
    profile,   # CareProfile — avoid circular import by not type-annotating here
    zone: Zone,
) -> ZoneMatch:
    """Evaluate whether a CareProfile is compatible with a Zone.

    Rules:
    1. **Light**: The zone's light level must be >= the plant's light needs.
       If the zone is exactly one rank below needs → ACCEPTABLE + mitigation.
       If two+ ranks below → POOR.
    2. **Humidity**: The zone's humidity must fall within the humidity range
       for the profile's ``humidity`` string (high/moderate/low).
       If within 10 pp of the range → ACCEPTABLE.
       Outside by more → POOR (if also light mismatch) or ACCEPTABLE alone.

    The worst failing dimension determines the overall quality.
    """
    reasons: List[str] = []
    mitigations: List[str] = []
    light_ok = True
    humidity_ok = True
    quality = MatchQuality.GOOD

    # ── Light check ───────────────────────────────────────────────────────────
    plant_light_str = (profile.light_needs or "bright-indirect").lower()
    needed_level = _LIGHT_NEEDS_MAP.get(plant_light_str, LightLevel.BRIGHT_INDIRECT)
    needed_rank = _LIGHT_RANK[needed_level]
    zone_rank = zone.light_rank
    light_gap = needed_rank - zone_rank  # positive = zone too dark

    if light_gap == 1:
        light_ok = False
        quality = MatchQuality.ACCEPTABLE
        reasons.append(
            f"Light is one level below needs ({zone.light_level.value} vs "
            f"required {needed_level.value})."
        )
        mitigations.append(
            "Supplement with a grow light or move closer to the window."
        )
    elif light_gap >= 2:
        light_ok = False
        quality = MatchQuality.POOR
        reasons.append(
            f"Light is significantly below needs ({zone.light_level.value} vs "
            f"required {needed_level.value})."
        )
    elif light_gap < -1:
        # Zone is much brighter than needed — some species will burn
        quality = _worst(quality, MatchQuality.ACCEPTABLE)
        reasons.append(
            f"Zone is brighter than needed ({zone.light_level.value} vs "
            f"optimal {needed_level.value}); risk of scorch for delicate species."
        )
        mitigations.append("Use sheer curtains or move back from the direct pane.")

    # ── Humidity check ────────────────────────────────────────────────────────
    humidity_str = (profile.humidity or "moderate").lower()
    lo, hi = _HUMIDITY_RANGES.get(humidity_str, (40, 70))
    zone_hum = zone.humidity_percent

    if lo <= zone_hum <= hi:
        humidity_ok = True
    else:
        humidity_ok = False
        gap = min(abs(zone_hum - lo), abs(zone_hum - hi))
        if gap <= 10:
            quality = _worst(quality, MatchQuality.ACCEPTABLE)
            reasons.append(
                f"Humidity ({zone_hum:.0f}%) is close to but outside the "
                f"target range ({lo}–{hi}%) for '{humidity_str}' plants."
            )
            if zone_hum < lo:
                mitigations.append(
                    "Use a pebble tray or humidifier to raise humidity."
                )
            else:
                mitigations.append(
                    "Improve air circulation to reduce humidity and prevent mold."
                )
        else:
            quality = _worst(quality, MatchQuality.POOR)
            reasons.append(
                f"Humidity ({zone_hum:.0f}%) is well outside the target range "
                f"({lo}–{hi}%) for '{humidity_str}' plants."
            )

    return ZoneMatch(
        zone=zone,
        quality=quality,
        reasons=reasons,
        mitigations=mitigations,
        light_ok=light_ok,
        humidity_ok=humidity_ok,
    )


def best_zone(
    profile,  # CareProfile
    zones: ZoneCollection,
) -> Optional[Zone]:
    """Return the best-fit Zone from *zones* for *profile*.

    Scoring: GOOD = 2 pts, ACCEPTABLE = 1 pt, POOR = 0 pts.
    Ties are broken by light-rank proximity to the plant's light needs.
    Returns None if *zones* is empty.
    """
    if not zones.all_zones():
        return None

    plant_light_str = (profile.light_needs or "bright-indirect").lower()
    needed_level = _LIGHT_NEEDS_MAP.get(plant_light_str, LightLevel.BRIGHT_INDIRECT)
    needed_rank = _LIGHT_RANK[needed_level]

    _QUALITY_SCORE = {
        MatchQuality.GOOD: 2,
        MatchQuality.ACCEPTABLE: 1,
        MatchQuality.POOR: 0,
    }

    scored: List[Tuple[Zone, int, int]] = []  # (zone, quality_score, -light_distance)
    for zone in zones.all_zones():
        match = match_zone(profile, zone)
        q_score = _QUALITY_SCORE[match.quality]
        light_dist = abs(zone.light_rank - needed_rank)
        scored.append((zone, q_score, light_dist))

    # Sort: highest quality score first, then lowest light distance
    scored.sort(key=lambda t: (-t[1], t[2]))
    return scored[0][0]


def rank_zones(
    profile,  # CareProfile
    zones: ZoneCollection,
) -> List[Tuple[Zone, ZoneMatch]]:
    """Return all zones ranked best-to-worst for *profile*.

    Returns a list of (Zone, ZoneMatch) pairs in descending quality order.
    """
    _QUALITY_SCORE = {
        MatchQuality.GOOD: 2,
        MatchQuality.ACCEPTABLE: 1,
        MatchQuality.POOR: 0,
    }
    plant_light_str = (profile.light_needs or "bright-indirect").lower()
    needed_level = _LIGHT_NEEDS_MAP.get(plant_light_str, LightLevel.BRIGHT_INDIRECT)
    needed_rank = _LIGHT_RANK[needed_level]

    pairs: List[Tuple[Zone, ZoneMatch, int, int]] = []
    for zone in zones.all_zones():
        match = match_zone(profile, zone)
        q_score = _QUALITY_SCORE[match.quality]
        light_dist = abs(zone.light_rank - needed_rank)
        pairs.append((zone, match, q_score, light_dist))

    pairs.sort(key=lambda t: (-t[2], t[3]))
    return [(z, m) for z, m, _, _ in pairs]


# ── Internal helpers ──────────────────────────────────────────────────────────


def _worst(a: MatchQuality, b: MatchQuality) -> MatchQuality:
    """Return the worse of two MatchQuality values."""
    order = {MatchQuality.GOOD: 0, MatchQuality.ACCEPTABLE: 1, MatchQuality.POOR: 2}
    return a if order[a] >= order[b] else b
