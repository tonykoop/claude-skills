"""Command-line interface for the plant-care engine.

Entry-point::

    python -m plant_care <subcommand> [args...]

Subcommands
-----------
due         Compute due/overdue care actions from intervals and last-event dates.
health      Assess plant health from visual-observation flags.
seasonal    Show a seasonally adjusted care profile (by date or explicit season).
calendar    Print a 12-month care calendar with per-month adjusted intervals.
zones       Rank environment zones for a care profile.
propagation Show method statistics for a serialised propagation log (JSON file/stdin).

All subcommands write JSON to stdout and exit 0 on success.
Errors print a message to stderr and exit 1.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from typing import List, Optional

from .health import assess_health
from .models import CareEvent, CareProfile, Observations, Specimen
from .propagation import PropagationLog
from .schedule import next_actions
from .seasonal import (
    Hemisphere,
    Season,
    adjusted_profile_for_date,
    care_calendar,
    season_for,
    seasonal_plan,
)
from .zones import LightLevel, Zone, ZoneCollection, best_zone, match_zone, rank_zones


# ── Helpers ────────────────────────────────────────────────────────────────────


def _parse_date(s: str, field: str = "date") -> datetime.date:
    """Parse an ISO date string (YYYY-MM-DD).  Exits on error."""
    try:
        return datetime.date.fromisoformat(s)
    except ValueError:
        _die(f"Invalid {field} '{s}' — expected YYYY-MM-DD")


def _die(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def _out(data) -> None:
    """Serialise *data* to JSON and print to stdout."""
    print(json.dumps(data, indent=2, default=str))


def _make_profile(args) -> CareProfile:
    """Build a CareProfile from parsed CLI args."""
    return CareProfile(
        watering_interval_days=args.water_interval,
        fertilize_interval_days=args.fert_interval,
        light_needs=getattr(args, "light", "bright-indirect") or "bright-indirect",
        humidity=getattr(args, "humidity", "moderate") or "moderate",
    )


# ── Subcommand handlers ────────────────────────────────────────────────────────


def cmd_due(args) -> None:
    """Print due/overdue care actions as a JSON array."""
    today = _parse_date(args.today, "today")

    # Build a minimal specimen
    specimen = Specimen(
        id="cli-specimen",
        species=args.species or "Unknown",
        acquired=today,
        location="CLI",
        light_level="bright-indirect",
        pot_size="unknown",
    )

    profile = CareProfile(
        watering_interval_days=args.water_interval,
        fertilize_interval_days=args.fert_interval,
        light_needs="bright-indirect",
        humidity="moderate",
    )

    history: List[CareEvent] = []
    if args.last_watered:
        d = _parse_date(args.last_watered, "last-watered")
        history.append(CareEvent(type="water", date=d))
    if args.last_fertilized:
        d = _parse_date(args.last_fertilized, "last-fertilized")
        history.append(CareEvent(type="fertilize", date=d))

    actions = next_actions(specimen, profile, history, today)
    _out(
        [
            {
                "action_type": a.action_type,
                "due_date": a.due_date.isoformat(),
                "days_overdue": a.days_overdue,
                "priority": a.priority,
            }
            for a in actions
        ]
    )


def cmd_health(args) -> None:
    """Print health assessment as JSON."""
    specimen = Specimen(
        id="cli-specimen",
        species=args.species or "Unknown",
        acquired=datetime.date(2020, 1, 1),
        location="CLI",
        light_level="bright-indirect",
        pot_size="unknown",
    )
    observations = Observations(
        yellowing=args.yellowing,
        drooping=args.drooping,
        pests=args.pests,
        dry_soil=args.dry_soil,
        leaf_drop=args.leaf_drop,
        mold=args.mold,
    )
    health = assess_health(specimen, observations)
    _out(
        {
            "status": health.status,
            "flags": health.flags,
            "notes": health.notes,
        }
    )


def cmd_seasonal(args) -> None:
    """Print a seasonally adjusted care profile as JSON."""
    profile = _make_profile(args)
    hemisphere = Hemisphere(args.hemisphere)

    if args.season:
        try:
            season = Season(args.season.lower())
        except ValueError:
            valid = [s.value for s in Season]
            _die(f"Unknown season '{args.season}' — choose from {valid}")
    elif args.today:
        today = _parse_date(args.today, "today")
        season = season_for(today, hemisphere)
    else:
        _die("Provide either --season SEASON or --today YYYY-MM-DD")

    adjusted = seasonal_plan(profile, season)
    from .seasonal import adjustment_for
    adj = adjustment_for(season)

    _out(
        {
            "season": season.value,
            "hemisphere": hemisphere.value,
            "watering_interval_days": adjusted.watering_interval_days,
            "fertilize_interval_days": adjusted.fertilize_interval_days,
            "light_needs": adjusted.light_needs,
            "humidity": adjusted.humidity,
            "active_growth": adj.active_growth,
            "notes": adj.notes,
            "humidity_notes": adj.humidity_notes,
            "light_notes": adj.light_notes,
        }
    )


def cmd_calendar(args) -> None:
    """Print a 12-month care calendar as a JSON array."""
    profile = _make_profile(args)
    hemisphere = Hemisphere(args.hemisphere)
    cal = care_calendar(profile, hemisphere)
    _out(cal)


def cmd_zones(args) -> None:
    """Rank zones for a care profile; output JSON array of zone matches."""
    profile = CareProfile(
        watering_interval_days=7,
        fertilize_interval_days=30,
        light_needs=args.light_needs,
        humidity=args.humidity,
    )

    col = ZoneCollection(name="CLI zones")

    for zone_spec in (args.zones or []):
        # Format: "Name:light-level:humidity_percent"
        parts = zone_spec.split(":")
        if len(parts) != 3:
            _die(
                f"Invalid zone spec '{zone_spec}' — "
                "expected 'Name:light-level:humidity_pct' e.g. 'Kitchen:medium:55'"
            )
        name, light_str, hum_str = parts
        try:
            light = LightLevel(light_str)
        except ValueError:
            valid = [ll.value for ll in LightLevel]
            _die(f"Unknown light level '{light_str}' — choose from {valid}")
        try:
            hum = float(hum_str)
        except ValueError:
            _die(f"Humidity must be a number, got '{hum_str}'")
        col.add(Zone(name=name, light_level=light, humidity_percent=hum))

    if not col.all_zones():
        _out({"ranked": [], "best": None})
        return

    ranked = rank_zones(profile, col)
    best = best_zone(profile, col)

    _out(
        {
            "ranked": [
                {
                    "zone": z.to_dict(),
                    "match": m.to_dict(),
                }
                for z, m in ranked
            ],
            "best": best.name if best else None,
        }
    )


def cmd_propagation(args) -> None:
    """Print propagation statistics from a JSON file or stdin."""
    if args.file == "-":
        raw = sys.stdin.read()
    else:
        try:
            with open(args.file) as fh:
                raw = fh.read()
        except OSError as e:
            _die(f"Cannot read '{args.file}': {e}")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        _die(f"Invalid JSON: {e}")

    if not isinstance(data, list):
        _die("Expected a JSON array of propagation attempt objects")

    log = PropagationLog.from_list(data)
    counts = log.attempt_count_by_method()

    by_method = {}
    from .propagation import PropagationMethod
    for method in PropagationMethod:
        resolved = log.by_method(method)
        successful = [a for a in resolved if a.success is True]
        failed = [a for a in resolved if a.success is False]
        pending = [a for a in resolved if a.is_pending]
        by_method[method.value] = {
            "total": len(resolved),
            "successful": len(successful),
            "failed": len(failed),
            "pending": len(pending),
            "success_rate": log.success_rate(method),
        }

    _out(
        {
            "total_attempts": len(log),
            "successful": len(log.successful()),
            "failed": len(log.failed()),
            "pending": len(log.pending()),
            "success_rate_overall": log.success_rate(),
            "by_method": by_method,
        }
    )


# ── Argument parser ────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="plant_care",
        description="Plant-care engine CLI — compute schedules, health, and zone matches.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── due ──────────────────────────────────────────────────────────────────
    p_due = sub.add_parser("due", help="Show due/overdue care actions.")
    p_due.add_argument("--today", required=True, metavar="YYYY-MM-DD",
                       help="Reference date for due calculation.")
    p_due.add_argument("--water-interval", type=int, required=True, metavar="N",
                       help="Watering interval in days.")
    p_due.add_argument("--fert-interval", type=int, required=True, metavar="N",
                       help="Fertilising interval in days.")
    p_due.add_argument("--last-watered", metavar="YYYY-MM-DD",
                       help="Date of last watering event.")
    p_due.add_argument("--last-fertilized", metavar="YYYY-MM-DD",
                       help="Date of last fertilising event.")
    p_due.add_argument("--species", default="Unknown",
                       help="Species name (cosmetic, for output label).")

    # ── health ───────────────────────────────────────────────────────────────
    p_health = sub.add_parser("health", help="Assess plant health from observations.")
    p_health.add_argument("--species", default="Unknown")
    p_health.add_argument("--yellowing", action="store_true")
    p_health.add_argument("--drooping", action="store_true")
    p_health.add_argument("--pests", action="store_true")
    p_health.add_argument("--dry-soil", action="store_true", dest="dry_soil")
    p_health.add_argument("--leaf-drop", action="store_true", dest="leaf_drop")
    p_health.add_argument("--mold", action="store_true")

    # ── seasonal ─────────────────────────────────────────────────────────────
    p_seasonal = sub.add_parser(
        "seasonal",
        help="Show a seasonally adjusted care profile.",
    )
    p_seasonal.add_argument("--water-interval", type=int, required=True, metavar="N")
    p_seasonal.add_argument("--fert-interval", type=int, required=True, metavar="N")
    p_seasonal.add_argument("--light", default="bright-indirect",
                            help="Light needs string (e.g. bright-indirect).")
    p_seasonal.add_argument("--humidity", default="moderate",
                            choices=["low", "moderate", "high"])
    _add_hemisphere(p_seasonal)
    group = p_seasonal.add_mutually_exclusive_group(required=True)
    group.add_argument("--season", choices=[s.value for s in Season],
                       help="Explicit season name.")
    group.add_argument("--today", metavar="YYYY-MM-DD",
                       help="Derive season from this date.")

    # ── calendar ─────────────────────────────────────────────────────────────
    p_cal = sub.add_parser("calendar", help="Print a 12-month care calendar.")
    p_cal.add_argument("--water-interval", type=int, required=True, metavar="N")
    p_cal.add_argument("--fert-interval", type=int, required=True, metavar="N")
    p_cal.add_argument("--light", default="bright-indirect")
    p_cal.add_argument("--humidity", default="moderate", choices=["low", "moderate", "high"])
    _add_hemisphere(p_cal)

    # ── zones ────────────────────────────────────────────────────────────────
    p_zones = sub.add_parser("zones", help="Rank environment zones for a care profile.")
    p_zones.add_argument("--light-needs", required=True,
                         choices=[ll.value for ll in LightLevel],
                         help="Plant's light requirement.")
    p_zones.add_argument("--humidity", required=True,
                         choices=["low", "moderate", "high"],
                         help="Plant's humidity requirement.")
    p_zones.add_argument("--zone", dest="zones", action="append",
                         metavar="NAME:LIGHT:HUMIDITY",
                         help=(
                             "Zone spec in the form 'Name:light-level:humidity_pct'. "
                             "Repeat for multiple zones. "
                             "Example: 'Kitchen:medium:55'"
                         ))

    # ── propagation ──────────────────────────────────────────────────────────
    p_prop = sub.add_parser(
        "propagation",
        help="Show propagation statistics from a JSON log file.",
    )
    p_prop.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Path to a JSON propagation log file, or '-' for stdin (default).",
    )

    return parser


def _add_hemisphere(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--hemisphere",
        default="northern",
        choices=["northern", "southern"],
        help="Hemisphere (affects season–month mapping). Default: northern.",
    )


# ── Main ──────────────────────────────────────────────────────────────────────


def main(argv: Optional[List[str]] = None) -> None:
    """Parse *argv* (defaults to sys.argv[1:]) and run the matching subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "due": cmd_due,
        "health": cmd_health,
        "seasonal": cmd_seasonal,
        "calendar": cmd_calendar,
        "zones": cmd_zones,
        "propagation": cmd_propagation,
    }
    handlers[args.command](args)
