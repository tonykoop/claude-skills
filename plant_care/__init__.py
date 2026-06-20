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

Photogrammetry / scan metadata::

    from plant_care.scan import (
        ScaleCalibration, ScanMeasurement, ScanSession, ScanLog,
        growth_delta, measurement_history, latest_measurement,
        growth_rate, measurement_summary,
    )
    # cal = ScaleCalibration("coin", reference_real_mm=23.0, reference_measured_units=230.0)
    # session = ScanSession(session_id="s1", specimen_id="ficus-01", date=today, calibration=cal)
    # session.measurements.append(ScanMeasurement.from_scan_units("trunk_girth", 85, cal))
    # log.add_session(session)
    # growth_rate(log, "trunk_girth", today) -> Optional[float]  # mm/day

Bloom / bud tracker::

    from plant_care.bloom import (
        BudStage, BudEvent, BloomRecord, BloomLog,
        time_in_stage, mean_days_to_stage,
        forecast_bloom_window, bloom_summary,
    )
    # record = BloomRecord(record_id="br-01", specimen_id="plum-01", species="Prunus mume")
    # record.add_event(BudEvent(stage=BudStage.OBSERVED, date=today))
    # window = forecast_bloom_window(log, today, baseline_days=14)
    # Note: not applicable for Ficus (syconium-enclosed flowers)

Aerial-root / nebari lifecycle::

    from plant_care.aerial_roots import (
        RootStage, RootEntry, AerialRoot, NebariLog, GuidanceNote,
        guidance_for, days_in_stage, days_in_current_stage,
        is_ready_to_guide, nebari_summary,
    )
    # root = AerialRoot(root_id="ar-01", specimen_id="ficus-01")
    # root.advance_stage(RootStage.TIP_PROMISING, today)
    # guidance_for(RootStage.GUIDED)  -> GuidanceNote (sphagnum/tube method)
    # is_ready_to_guide(root, today, min_days_observed=14) -> bool

Health diagnostics::

    from plant_care.diagnostics import (
        PestFlag, NutritionFlag, Confidence,
        DiagnosticFinding, DiagnosticReport,
        diagnose, root_rot_risk, probable_pests, nutrition_flags,
    )
    # report = diagnose(specimen, observations, history, today, profile)
    # report.overall_status   # "healthy" | "needs-attention" | "declining"
    # report.findings         # List[DiagnosticFinding], HIGH-confidence first
    # root_rot_risk(history, profile, today) -> float in [0, 1]
    # probable_pests(observations) -> List[DiagnosticFinding]
    # nutrition_flags(observations) -> List[DiagnosticFinding]

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
