"""plant_care — houseplant/bonsai care-engine module.

A pure-function, date-injected engine for scheduling, health assessment,
propagation tracking, seasonal planning, and environment-zone matching
for houseplant and bonsai collections.

Public API surface (import selectively):

Core models::

    from plant_care.models import (
        Specimen, CareProfile, CareEvent, BonsaiExtras,
        DueAction, HealthState, Observations,
    )

Scheduling::

    from plant_care.schedule import next_actions
    # next_actions(specimen, profile, history, today) -> List[DueAction]

Health assessment::

    from plant_care.health import assess_health
    # assess_health(specimen, observations) -> HealthState

Bonsai extras::

    from plant_care.bonsai import wire_reminders, prune_recovery_status

Collection / digital-twin::

    from plant_care.collection import Collection, SpecimenRecord, CollectionSummary
    # col = Collection()
    # col.add(specimen, profile, tags=["indoor", "tropical"])
    # col.due(specimen_id, today)          -> List[DueAction]
    # col.health(specimen_id, obs)         -> HealthState
    # col.summary(today, obs_map)          -> CollectionSummary

Propagation log and lineage::

    from plant_care.propagation import PropagationLog, PropagationAttempt, PropagationMethod
    # log = PropagationLog()
    # log.add_attempt(attempt_id, parent_id, method, date, ...)
    # log.ancestors_of(specimen_id)        -> List[str]   (ordered, cycle-safe)
    # log.descendants_of(specimen_id)      -> List[str]   (BFS)
    # log.lineage_tree(specimen_id)        -> dict

Seasonal care-plan generator::

    from plant_care.seasonal import (
        Season, Hemisphere, SeasonalAdjustment,
        season_for, seasonal_plan, year_plan,
        adjusted_profile_for_date, care_calendar,
    )
    # adjusted = seasonal_plan(profile, Season.SUMMER)
    # cal = care_calendar(profile, Hemisphere.NORTHERN)  # 12-entry list

Environment-zone matching::

    from plant_care.zones import (
        LightLevel, Zone, ZoneCollection,
        MatchQuality, ZoneMatch,
        match_zone, best_zone, rank_zones,
    )
    # match_zone(profile, zone)            -> ZoneMatch
    # best_zone(profile, zone_collection)  -> Optional[Zone]
    # rank_zones(profile, zone_collection) -> List[Tuple[Zone, ZoneMatch]]

CLI (python -m plant_care)::

    # python -m plant_care due --today 2024-06-15 --water-interval 7 --fert-interval 30
    # python -m plant_care health --yellowing --pests
    # python -m plant_care seasonal --season summer --water-interval 7 --fert-interval 30
    # python -m plant_care calendar --water-interval 7 --fert-interval 30
    # python -m plant_care zones --light-needs bright-indirect --humidity moderate \\
    #         --zone "South window:bright-indirect:55" --zone "Bathroom:medium:70"
    # python -m plant_care propagation log.json

    from plant_care.cli import main as cli_main

All functions accept an explicit ``today`` date; no real-clock calls anywhere.
"""
