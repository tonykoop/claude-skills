# plant_care — Houseplant/Bonsai Care Engine

This module is the deterministic engine layer backing the `houseplant` skill
(`plugins/maker/skills/houseplant/`). It does **not** touch the skill markdown;
it provides pure-Python, testable logic that the skill and agents can call at
runtime.

## Overview

```
plant_care/
├── models.py      — Pydantic data models (Specimen, CareProfile, CareEvent …)
├── schedule.py    — next_actions(): due/overdue care action scheduler
├── health.py      — assess_health(): rule-based health status from observations
├── bonsai.py      — wire_reminders() + prune_recovery_status()
└── tests/
    ├── test_schedule.py
    ├── test_health.py
    ├── test_bonsai.py
    └── test_models.py
```

## Scheduling Logic (`schedule.py`)

`next_actions(specimen, profile, history, today)` computes which care actions
are due or overdue relative to an injected `today` date (no real-clock calls).

- For each scheduled action type (`water`, `fertilize`), the most recent event
  in `history` of that type is located.
- If no prior event exists, the action is due today.
- If `last_event_date + interval_days <= today`, the action is included with
  `days_overdue = today - due_date`.
- Actions not yet due are excluded.
- The returned list is sorted by `days_overdue` descending (most overdue first).

## Health States and Rules (`health.py`)

`assess_health(specimen, observations)` evaluates a set of boolean `Observations`
flags and returns a `HealthState` with one of three statuses:

| Status            | Trigger rule                                          |
|-------------------|-------------------------------------------------------|
| `declining`       | `pests`, OR (`yellowing` AND `drooping`), OR `leaf_drop` |
| `needs-attention` | `yellowing`, OR `drooping`, OR `dry_soil`, OR `mold`  |
| `healthy`         | none of the above                                     |

Rules are evaluated most-severe-first; the first matching rule sets the status.
All triggered flags are collected into `HealthState.flags` regardless of status.

## Bonsai Training Tracker (`bonsai.py`)

### Wire reminders

`wire_reminders(extras, today)` checks whether the applied wire coil has
reached the 90-day inspection threshold (configurable via `WIRE_CHECK_THRESHOLD_DAYS`).
If `wire_applied` is set and `today >= wire_applied + 90 days`, a reminder
string is returned describing the risk of bark bite-in.

### Prune recovery window

`prune_recovery_status(extras, today)` returns one of:

- `"In recovery window (N days remaining)"` — if `today < last_pruned + 14 days`
- `"Recovery complete"` — if the window has elapsed or no prune is recorded
  (safe default when `last_pruned` is `None`)

The recovery threshold is configurable via `PRUNE_RECOVERY_DAYS`.

## Data Models (`models.py`)

All models are Pydantic `BaseModel` subclasses (with a stdlib `dataclass`
fallback for environments without Pydantic installed).

| Model          | Key fields                                                              |
|----------------|-------------------------------------------------------------------------|
| `Specimen`     | `id`, `species`, `acquired`, `location`, `light_level`, `pot_size`, `is_bonsai` |
| `CareProfile`  | `watering_interval_days`, `fertilize_interval_days`, `light_needs`, `humidity` |
| `CareEvent`    | `type` (water/fertilize/prune/repot/wire), `date`, `note`              |
| `BonsaiExtras` | `wire_applied`, `last_pruned`, `nebari_notes`                          |
| `DueAction`    | `action_type`, `due_date`, `days_overdue`, `priority`                  |
| `HealthState`  | `status`, `flags`, `notes`                                              |
| `Observations` | `yellowing`, `drooping`, `pests`, `dry_soil`, `leaf_drop`, `mold`      |

## Running Tests

```bash
cd /tmp/w2-plantcare   # or wherever the repo is cloned
python -m pytest plant_care/tests/ -v
```

All tests are offline and deterministic — `today` is always injected, never
read from the system clock.

## Relationship to the Houseplant Skill

The skill markdown at `plugins/maker/skills/houseplant/SKILL.md` is unchanged.
This engine module is an additive layer that provides a clean Python API for
the scheduling and health-assessment logic described in the skill's reference
documents (`chrono-engine.md`, `health-diagnostics.md`, `bonsai-module.md`).
Agents and scripts can import from `plant_care` directly without going through
the skill markdown at runtime.
