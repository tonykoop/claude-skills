#!/usr/bin/env python3
"""Collection-wide care dashboard: aggregate care tasks across the whole houseplant collection.

Glues the individual chrono scripts (care_cadence, wire_window, bloom_forecast,
propagation_tracker, health_triage) into a single prioritised care list.
Each plant in the input contributes zero or more tasks; tasks are bucketed by
urgency (overdue, today, this week, this month, later) and rendered as a
Markdown dashboard.

Pure stdlib + imports from sibling scripts — no Blender, no network.

Input (JSON via --input FILE or stdin):
    {
      "today": "2026-06-19",
      "plants": [
        {
          "plant_id": "ficus-01",
          "display_name": "Ficus benjamina",
          "species": "ficus",
          "growth_class": "fast",
          "phase": "active_growth",
          "heat": true,
          "stressors": [],
          "care_events": [
            {"type": "watered", "date": "2026-06-17"},
            {"type": "wired", "date": "2026-06-10", "branch": "R02"},
            {"type": "fertilized", "date": "2026-06-05"}
          ],
          "buds": [
            {
              "species": "phalaenopsis",
              "stage": "swelling",
              "anchor_date": "2026-06-16",
              "condition": "warm",
              "history_intervals_days": [16, 19]
            }
          ],
          "propagules": [
            {
              "method": "tip-cutting",
              "species": "ficus",
              "condition": "warm",
              "started_date": "2026-06-01"
            }
          ],
          "health_observations": [
            {"symptom": "chlorosis-lower-leaves", "region": "lower interior"}
          ]
        }
      ]
    }

CLI:
    collection_dashboard.py --input collection.json
    cat collection.json | collection_dashboard.py
Exit 0 = dashboard produced, 2 = bad input.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

# --- sibling script imports ---------------------------------------------------
# Allow running from any directory by inserting the scripts/ dir on sys.path.
_SCRIPTS_DIR = str(Path(__file__).parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from care_cadence import watering_check, fertilizing_plan  # noqa: E402
from wire_window import wire_inspection_window  # noqa: E402
from bloom_forecast import forecast as bloom_forecast  # noqa: E402
from propagation_tracker import rooting_forecast  # noqa: E402
from health_triage import triage, structural_risk  # noqa: E402


# --- task dataclass ----------------------------------------------------------

class Task:
    __slots__ = ("due", "plant_id", "label", "detail", "priority_boost")

    def __init__(self, due: _dt.date | None, plant_id: str, label: str, detail: str,
                 priority_boost: int = 0):
        self.due = due
        self.plant_id = plant_id
        self.label = label
        self.detail = detail
        self.priority_boost = priority_boost  # flags bump to top of bucket

    def sort_key(self):
        # None means unknown/open-ended -> sort last; boost flips within bucket
        return (_dt.date.max if self.due is None else self.due, -self.priority_boost)


# --- per-plant task builders --------------------------------------------------

def _last_event_date(care_events: list, kind: str) -> _dt.date | None:
    """Most recent date for a given care-event type."""
    dates = []
    for ev in care_events or []:
        if ev.get("type") == kind:
            try:
                dates.append(_dt.date.fromisoformat(str(ev["date"])))
            except (KeyError, ValueError):
                pass
    return max(dates) if dates else None


def _watering_tasks(plant: dict, today: _dt.date) -> list[Task]:
    pid = plant["plant_id"]
    gc = plant.get("growth_class", "moderate")
    phase = plant.get("phase", "active_growth")
    heat = bool(plant.get("heat", False))
    stressors = plant.get("stressors", [])

    try:
        plan = watering_check(gc, phase, heat, stressors)
    except ValueError:
        return []

    cadence = plan["cadence_days"]
    last_watered = _last_event_date(plant.get("care_events", []), "watered")
    if last_watered:
        due = last_watered + _dt.timedelta(days=cadence)
    else:
        due = today  # unknown -> treat as due today

    label = "Watering check"
    cond_note = " (heat)" if heat else ""
    detail = (
        f"Check soil moisture every {cadence} day(s){cond_note}; "
        f"water only when top 2–3 cm dry & pot feels light."
        + (f" Last watered: {last_watered}." if last_watered else "")
    )
    return [Task(due=due, plant_id=pid, label=label, detail=detail)]


def _fertilizing_tasks(plant: dict, today: _dt.date) -> list[Task]:
    pid = plant["plant_id"]
    gc = plant.get("growth_class", "moderate")
    phase = plant.get("phase", "active_growth")
    stressors = plant.get("stressors", [])

    try:
        plan = fertilizing_plan(gc, phase, stressors)
    except ValueError:
        return []

    if plan["suspended"]:
        resume_after = plan.get("resume_after_days")
        if resume_after:
            # Find repot/root_reduction date to compute resume date
            base_date = (
                _last_event_date(plant.get("care_events", []), "repotted")
                or _last_event_date(plant.get("care_events", []), "root_reduction")
                or today
            )
            resume_due = base_date + _dt.timedelta(days=resume_after)
            return [Task(
                due=resume_due, plant_id=pid,
                label="Fertilizing: resume",
                detail=f"Hold fertilizer until {resume_due} (~{resume_after}d after last repot/root work); "
                       "resume dilute feed when new growth appears.",
            )]
        return []

    cadence = plan["cadence_days"]
    last_fed = _last_event_date(plant.get("care_events", []), "fertilized")
    if last_fed:
        due = last_fed + _dt.timedelta(days=cadence)
    else:
        due = today + _dt.timedelta(days=cadence)

    detail = (
        f"Dilute balanced fertilizer every {cadence} day(s) during active growth; "
        f"skip if stressed or soil is dry."
        + (f" Last fed: {last_fed}." if last_fed else "")
    )
    return [Task(due=due, plant_id=pid, label="Fertilizing", detail=detail)]


def _wire_tasks(plant: dict, today: _dt.date) -> list[Task]:
    pid = plant["plant_id"]
    gc = plant.get("growth_class", "moderate")
    active = plant.get("phase", "active_growth") == "active_growth"
    tasks = []
    for ev in plant.get("care_events", []):
        if ev.get("type") != "wired":
            continue
        try:
            wired_date = str(ev["date"])
            _dt.date.fromisoformat(wired_date)
        except (KeyError, ValueError):
            continue
        branch = ev.get("branch", "branch")
        try:
            win = wire_inspection_window(wired_date, gc, active)
        except ValueError:
            continue
        due = _dt.date.fromisoformat(str(win["first_inspection"]))
        detail = (
            f"Check {branch} for wire bite-in; recheck every {win['recheck_cadence_days']}d. "
            f"Wired: {wired_date}."
        )
        tasks.append(Task(due=due, plant_id=pid, label=f"Wire inspection ({branch})", detail=detail))
    return tasks


def _bloom_tasks(plant: dict, today: _dt.date) -> list[Task]:
    pid = plant["plant_id"]
    tasks = []
    for bud in plant.get("buds", []):
        anchor = bud.get("anchor_date")
        if not anchor:
            continue
        try:
            fc = bloom_forecast(
                history=bud.get("history_intervals_days", []),
                species=bud.get("species", ""),
                condition=bud.get("condition", "neutral"),
                anchor_date=anchor,
            )
        except (ValueError, KeyError):
            continue
        watch_start = _dt.date.fromisoformat(fc["window_start"])
        watch_end = _dt.date.fromisoformat(fc["window_end"])
        detail = (
            f"Bloom window: {watch_start} … {watch_end} "
            f"({fc['low_days']}–{fc['high_days']} days from bud, confidence {fc['confidence']}). "
            f"Check every {fc['cadence_days']}d. {fc.get('caveat', '')}"
        )
        tasks.append(Task(due=watch_start, plant_id=pid, label="Bloom watch", detail=detail))
    return tasks


def _propagation_tasks(plant: dict, today: _dt.date) -> list[Task]:
    pid = plant["plant_id"]
    tasks = []
    for prop in plant.get("propagules", []):
        started = prop.get("started_date")
        if not started:
            continue
        try:
            fc = rooting_forecast(
                method=prop.get("method", ""),
                species=prop.get("species", ""),
                condition=prop.get("condition", "neutral"),
                started_date=started,
            )
        except (ValueError, KeyError):
            continue
        window_start = _dt.date.fromisoformat(fc["window_start"])
        window_end = _dt.date.fromisoformat(fc["window_end"])
        detail = (
            f"Rooting window: {window_start} … {window_end} "
            f"(confidence {fc['confidence']}); check every {fc['check_cadence_days']}d. "
            f"{fc['note']}"
        )
        tasks.append(Task(due=window_start, plant_id=pid, label="Propagule root check", detail=detail))
    return tasks


def _health_tasks(plant: dict, today: _dt.date) -> list[Task]:
    pid = plant["plant_id"]
    observations = plant.get("health_observations", [])
    if not observations:
        return []
    try:
        flags = triage(observations, plant.get("care_events", []), today.isoformat())
    except Exception:
        return []
    tasks = []
    risk = structural_risk(flags)
    for flag in flags:
        detail = (
            f"[{flag.confidence} confidence] {flag.inspection}"
            + (f" — {flag.cross_ref_note}" if flag.cross_ref_note else "")
        )
        boost = 2 if flag.category in ("pest", "rot") else 1
        tasks.append(Task(
            due=today, plant_id=pid,
            label=f"Health flag: {flag.flag}",
            detail=detail,
            priority_boost=boost,
        ))
    if risk["risk"] == "High" and tasks:
        # Add a structural-risk blocker note
        tasks.append(Task(
            due=today, plant_id=pid,
            label="Structural work BLOCKED",
            detail=risk["reason"],
            priority_boost=3,
        ))
    return tasks


def _plant_tasks(plant: dict, today: _dt.date) -> list[Task]:
    builders = [
        _health_tasks,   # health flags first so they surface urgent items
        _watering_tasks,
        _fertilizing_tasks,
        _wire_tasks,
        _bloom_tasks,
        _propagation_tasks,
    ]
    tasks: list[Task] = []
    for builder in builders:
        tasks.extend(builder(plant, today))
    return tasks


# --- bucketing + rendering ---------------------------------------------------

def _bucket(task: Task, today: _dt.date) -> str:
    if task.due is None:
        return "later"
    delta = (task.due - today).days
    if delta < 0:
        return "overdue"
    if delta == 0:
        return "today"
    if delta <= 7:
        return "this_week"
    if delta <= 30:
        return "this_month"
    return "later"


_BUCKET_ORDER = ["overdue", "today", "this_week", "this_month", "later"]
_BUCKET_HEADERS = {
    "overdue":    "### Overdue",
    "today":      "### Today",
    "this_week":  "### This week",
    "this_month": "### This month",
    "later":      "### Later (> 30 days)",
}


def render_dashboard(tasks: list[Task], today: _dt.date, display_names: dict) -> str:
    buckets: dict[str, list[Task]] = {k: [] for k in _BUCKET_ORDER}
    for task in tasks:
        b = _bucket(task, today)
        buckets[b].append(task)
    for b in buckets.values():
        b.sort(key=lambda t: t.sort_key())

    lines = [f"## Collection Care Dashboard — {today}"]
    total = sum(len(v) for v in buckets.values())
    lines.append(f"_{total} task(s) across {len(display_names)} plant(s)_\n")

    any_content = False
    for bucket_key in _BUCKET_ORDER:
        group = buckets[bucket_key]
        if not group:
            continue
        any_content = True
        lines.append(_BUCKET_HEADERS[bucket_key])
        for task in group:
            name = display_names.get(task.plant_id, task.plant_id)
            due_str = f" (due {task.due})" if task.due and bucket_key not in ("overdue", "today") else ""
            lines.append(f"- **{name}** — {task.label}{due_str}")
            lines.append(f"  {task.detail}")
        lines.append("")

    if not any_content:
        lines.append("_No tasks scheduled — collection is up to date._\n")

    return "\n".join(lines)


# --- main --------------------------------------------------------------------

def build_dashboard(data: dict) -> str:
    today_str = data.get("today")
    if not today_str:
        raise ValueError("'today' field required in input")
    today = _dt.date.fromisoformat(str(today_str))

    plants = data.get("plants", [])
    if not isinstance(plants, list):
        raise ValueError("'plants' must be a list")

    display_names = {}
    all_tasks: list[Task] = []
    for plant in plants:
        pid = plant.get("plant_id")
        if not pid:
            continue
        display_names[pid] = plant.get("display_name", pid)
        all_tasks.extend(_plant_tasks(plant, today))

    return render_dashboard(all_tasks, today, display_names)


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate care tasks across a houseplant collection into a prioritised dashboard."
    )
    parser.add_argument("--input", help="JSON file (else stdin).")
    args = parser.parse_args(argv)

    try:
        raw = sys.stdin.read() if not args.input else open(args.input, encoding="utf-8").read()
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        output = build_dashboard(data)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(output + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
