"""Seasonal care-plan generator.

Generates adjusted care profiles and advisory notes for each season,
accounting for hemisphere (northern/southern) and species growth habits.

Key concepts:
- ``Season`` — SPRING, SUMMER, AUTUMN, WINTER (astronomical quarter).
- ``Hemisphere`` — NORTHERN, SOUTHERN.  Southern seasons are the inverse
  of northern seasons for the same calendar month.
- ``SeasonalAdjustment`` — multipliers for watering and fertilising intervals,
  advisory notes, and an ``active_growth`` flag.
- ``seasonal_plan(profile, season)`` → adjusted ``CareProfile`` for that season.
- ``year_plan(profile, hemisphere)`` → dict of Season → SeasonalAdjustment.
- ``season_for(date, hemisphere)`` → which season the date falls in.
- ``months_in_season(season, hemisphere)`` → calendar months (1-12) for planning.

No real-clock calls — every function that needs a date takes an explicit
parameter.

Usage::

    from plant_care.seasonal import season_for, seasonal_plan, year_plan, Season
    from plant_care.seasonal import Hemisphere, SeasonalAdjustment
    from plant_care.models import CareProfile
    import datetime

    today = datetime.date(2024, 6, 15)
    s = season_for(today, Hemisphere.NORTHERN)   # Season.SUMMER

    profile = CareProfile(watering_interval_days=7, fertilize_interval_days=30,
                          light_needs="bright-indirect", humidity="moderate")
    adjusted = seasonal_plan(profile, Season.SUMMER)
    # adjusted.watering_interval_days is smaller (more frequent in summer)

    plan = year_plan(profile, Hemisphere.NORTHERN)
    # dict: {Season.SPRING: SeasonalAdjustment, Season.SUMMER: …, …}
"""

from __future__ import annotations

import datetime
import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from .models import CareProfile


# ── Enums ─────────────────────────────────────────────────────────────────────


class Season(str, Enum):
    """The four astronomical seasons."""

    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class Hemisphere(str, Enum):
    """Hemisphere of the grower; affects which calendar months map to which season."""

    NORTHERN = "northern"
    SOUTHERN = "southern"


# ── Season calendar map ───────────────────────────────────────────────────────
#
# Astronomical seasons by month (1-based).  Southern seasons are the inverse
# of Northern, offset by 6 months.

# Northern hemisphere: month → Season
_NORTHERN_MONTH_SEASON: Dict[int, Season] = {
    1: Season.WINTER,
    2: Season.WINTER,
    3: Season.SPRING,
    4: Season.SPRING,
    5: Season.SPRING,
    6: Season.SUMMER,
    7: Season.SUMMER,
    8: Season.SUMMER,
    9: Season.AUTUMN,
    10: Season.AUTUMN,
    11: Season.AUTUMN,
    12: Season.WINTER,
}

# Southern hemisphere is just the opposite
_SOUTHERN_MONTH_SEASON: Dict[int, Season] = {
    1: Season.SUMMER,
    2: Season.SUMMER,
    3: Season.AUTUMN,
    4: Season.AUTUMN,
    5: Season.AUTUMN,
    6: Season.WINTER,
    7: Season.WINTER,
    8: Season.WINTER,
    9: Season.SPRING,
    10: Season.SPRING,
    11: Season.SPRING,
    12: Season.SUMMER,
}


# ── SeasonalAdjustment ────────────────────────────────────────────────────────


@dataclass
class SeasonalAdjustment:
    """Care adjustments for a single season relative to a base CareProfile.

    Attributes
    ----------
    season:
        The season this adjustment applies to.
    watering_multiplier:
        Multiply the base watering interval by this factor.  Values < 1
        mean *more frequent* watering; values > 1 mean *less frequent*.
        e.g. 0.5 on a 7-day base → water every 3-4 days.
    fertilize_multiplier:
        Multiply the base fertilise interval by this factor.  Winter
        rest = higher multiplier (fertilise less often or not at all).
    active_growth:
        True during spring and summer when the plant is actively growing.
    notes:
        Human-readable advisory notes for this season.
    humidity_notes:
        Advisory on humidity adjustments (heating in winter dries air, etc.).
    light_notes:
        Advisory on light adjustments (fewer hours in winter, intense sun risk).
    """

    season: Season
    watering_multiplier: float
    fertilize_multiplier: float
    active_growth: bool
    notes: str
    humidity_notes: str = ""
    light_notes: str = ""

    def to_dict(self) -> dict:
        return {
            "season": self.season.value,
            "watering_multiplier": self.watering_multiplier,
            "fertilize_multiplier": self.fertilize_multiplier,
            "active_growth": self.active_growth,
            "notes": self.notes,
            "humidity_notes": self.humidity_notes,
            "light_notes": self.light_notes,
        }


# ── Default adjustment table ──────────────────────────────────────────────────
#
# Grounded in general houseplant and bonsai horticultural practice:
# - Spring: resuming growth; ramp up watering + feeding as temps rise.
# - Summer: peak growth; most frequent watering; fertilise actively.
# - Autumn: slow down; taper feeding; prepare for dormancy.
# - Winter: minimal growth or dormancy; minimal watering; no or rare feeding.

_DEFAULT_ADJUSTMENTS: Dict[Season, SeasonalAdjustment] = {
    Season.SPRING: SeasonalAdjustment(
        season=Season.SPRING,
        watering_multiplier=0.85,   # slightly more frequent than base
        fertilize_multiplier=0.8,   # start feeding again as growth resumes
        active_growth=True,
        notes=(
            "Spring is the main growth flush — resume regular watering as "
            "the soil dries faster. Begin fertilising as new buds appear. "
            "This is the best time for repotting and styling bonsai."
        ),
        humidity_notes="Humidity is usually adequate; open windows help circulation.",
        light_notes=(
            "Increasing day-length is an asset; rotate pots for even growth. "
            "Protect frost-sensitive species until night temps are reliably above 5 °C."
        ),
    ),
    Season.SUMMER: SeasonalAdjustment(
        season=Season.SUMMER,
        watering_multiplier=0.6,    # water more frequently — evaporation is high
        fertilize_multiplier=0.7,   # peak feeding period
        active_growth=True,
        notes=(
            "Summer heat increases evaporation significantly. "
            "Check soil moisture daily for small pots. "
            "Fertilise every 2-4 weeks with a balanced formula. "
            "Protect from direct midday sun to prevent scorch on shade-tolerant species."
        ),
        humidity_notes=(
            "Humid-loving species (ferns, orchids) benefit from pebble trays or misting. "
            "Air-conditioning dehumidifies rapidly — monitor closely."
        ),
        light_notes=(
            "Bright-indirect and full-sun species thrive. "
            "South/west-facing windows may need sheer curtains for delicate foliage."
        ),
    ),
    Season.AUTUMN: SeasonalAdjustment(
        season=Season.AUTUMN,
        watering_multiplier=1.3,    # less frequent as days shorten
        fertilize_multiplier=2.0,   # taper off; switch to low-nitrogen or stop
        active_growth=False,
        notes=(
            "Growth slows as temperatures drop and day length shortens. "
            "Reduce watering frequency as evaporation falls. "
            "Taper fertilising — switch to a low-nitrogen formula or stop by late autumn. "
            "Begin bringing frost-sensitive species indoors."
        ),
        humidity_notes=(
            "Indoor heating begins to dry air. "
            "Consider humidifiers or grouping plants together."
        ),
        light_notes=(
            "Move light-hungry species closer to windows as sun angle lowers. "
            "Clean dust off leaves to maximise photosynthesis."
        ),
    ),
    Season.WINTER: SeasonalAdjustment(
        season=Season.WINTER,
        watering_multiplier=2.0,    # half as frequent or less
        fertilize_multiplier=4.0,   # minimal or no feeding during dormancy
        active_growth=False,
        notes=(
            "Most houseplants enter a rest period. "
            "Water sparingly — allow soil to dry significantly between waterings. "
            "Suspend or greatly reduce fertilising until spring. "
            "Root rot is the primary winter risk for over-watered plants. "
            "Hardy outdoor bonsai may need frost protection but not heated interiors."
        ),
        humidity_notes=(
            "Central heating creates very dry air. "
            "Pebble trays, humidifiers, or bathroom placement help humidity-lovers."
        ),
        light_notes=(
            "Supplement with grow lights for light-hungry species if natural "
            "light drops below 4 hours of direct sun. "
            "South-facing windows are most valuable in winter."
        ),
    ),
}


# ── Public functions ──────────────────────────────────────────────────────────


def season_for(date: datetime.date, hemisphere: Hemisphere = Hemisphere.NORTHERN) -> Season:
    """Return the season for *date* in the given hemisphere.

    Uses a three-month astronomical grouping:
    - Dec/Jan/Feb → Winter (Northern) / Summer (Southern)
    - Mar/Apr/May → Spring / Autumn
    - Jun/Jul/Aug → Summer / Winter
    - Sep/Oct/Nov → Autumn / Spring

    Args:
        date:        Reference date (no real-clock calls).
        hemisphere:  Northern or southern hemisphere.

    Returns:
        The ``Season`` enum value for the given month and hemisphere.
    """
    if hemisphere == Hemisphere.NORTHERN:
        return _NORTHERN_MONTH_SEASON[date.month]
    return _SOUTHERN_MONTH_SEASON[date.month]


def months_in_season(
    season: Season,
    hemisphere: Hemisphere = Hemisphere.NORTHERN,
) -> List[int]:
    """Return the calendar months (1–12) that fall in *season* for *hemisphere*.

    Returns a sorted list of three month numbers.
    """
    mapping = (
        _NORTHERN_MONTH_SEASON
        if hemisphere == Hemisphere.NORTHERN
        else _SOUTHERN_MONTH_SEASON
    )
    return sorted(m for m, s in mapping.items() if s == season)


def adjustment_for(season: Season) -> SeasonalAdjustment:
    """Return the default ``SeasonalAdjustment`` for *season*.

    The returned object is a shared singleton — do not mutate it.
    To get a modified copy, use ``seasonal_plan()`` which returns new objects.
    """
    return _DEFAULT_ADJUSTMENTS[season]


def seasonal_plan(
    profile: CareProfile,
    season: Season,
) -> CareProfile:
    """Return a new ``CareProfile`` with intervals adjusted for *season*.

    The adjusted intervals are clamped to reasonable minimums:
    - ``watering_interval_days`` ≥ 1
    - ``fertilize_interval_days`` ≥ 7

    Args:
        profile:  Base care profile (unchanged; a new object is returned).
        season:   Target season.

    Returns:
        A new ``CareProfile`` with seasonally adjusted intervals.
        ``light_needs`` and ``humidity`` are carried through unchanged.
    """
    adj = _DEFAULT_ADJUSTMENTS[season]
    new_water = max(1, round(profile.watering_interval_days * adj.watering_multiplier))
    new_fert = max(7, round(profile.fertilize_interval_days * adj.fertilize_multiplier))
    return CareProfile(
        watering_interval_days=new_water,
        fertilize_interval_days=new_fert,
        light_needs=profile.light_needs,
        humidity=profile.humidity,
    )


def year_plan(
    profile: CareProfile,
    hemisphere: Hemisphere = Hemisphere.NORTHERN,
) -> Dict[Season, SeasonalAdjustment]:
    """Return a full year of seasonal adjustments for *profile*.

    Returns
    -------
    dict
        ``Season → SeasonalAdjustment`` for all four seasons.
        The adjustments are the default advisory objects; the *profile*
        parameter is used here for future per-species override hooks but
        is currently passed through unmodified.
    """
    return {season: _DEFAULT_ADJUSTMENTS[season] for season in Season}


def adjusted_profile_for_date(
    profile: CareProfile,
    date: datetime.date,
    hemisphere: Hemisphere = Hemisphere.NORTHERN,
) -> CareProfile:
    """Return a seasonally adjusted ``CareProfile`` for a specific date.

    Convenience wrapper that combines ``season_for()`` and ``seasonal_plan()``.
    """
    season = season_for(date, hemisphere)
    return seasonal_plan(profile, season)


def care_calendar(
    profile: CareProfile,
    hemisphere: Hemisphere = Hemisphere.NORTHERN,
) -> List[dict]:
    """Return a 12-month care-calendar as a list of dicts.

    Each entry covers one calendar month and includes the season, the
    adjusted care profile, and the human-readable advisory notes.

    Returns
    -------
    list[dict]
        One dict per month (month 1–12), each with keys:
        ``month``, ``season``, ``watering_interval_days``,
        ``fertilize_interval_days``, ``active_growth``, ``notes``.
    """
    mapping = (
        _NORTHERN_MONTH_SEASON
        if hemisphere == Hemisphere.NORTHERN
        else _SOUTHERN_MONTH_SEASON
    )
    calendar_entries = []
    for month in range(1, 13):
        season = mapping[month]
        adj = _DEFAULT_ADJUSTMENTS[season]
        adjusted = seasonal_plan(profile, season)
        calendar_entries.append({
            "month": month,
            "season": season.value,
            "watering_interval_days": adjusted.watering_interval_days,
            "fertilize_interval_days": adjusted.fertilize_interval_days,
            "active_growth": adj.active_growth,
            "notes": adj.notes,
        })
    return calendar_entries
