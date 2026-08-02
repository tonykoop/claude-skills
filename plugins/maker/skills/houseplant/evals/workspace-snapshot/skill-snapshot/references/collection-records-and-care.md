# Collection Records and Care

Read this reference when the user wants Obsidian or Markdown plant records, spreadsheet-backed collection data, care checklists, reminders, bud/bloom calendar entries, propagation logs, or updates after Blender or pruning work.

## Source of Truth

Use the user's stated collection database as the authority. If both Obsidian and a spreadsheet exist, do not silently fork the record; ask which one should receive canonical updates or write a concise sync note for both.

Prefer stable ids over plant nicknames:

```text
ficus-benjamina-01
jade-plant-02
orchid-phalaenopsis-01
```

## Minimal Plant Record

A Markdown/Obsidian record can use this shape:

```markdown
---
plant_id: ficus-benjamina-01
common_name: Weeping fig
scientific_name: Ficus benjamina
nickname:
acquired:
source:
location:
indoor_outdoor:
pot:
substrate:
light:
watering_method:
digital_twin:
media_folder:
last_watered:
last_fertilized:
last_repotted:
last_pruned:
last_wired:
health_flags: []
---

# Ficus benjamina 01

## Current State

## Care Preferences

## Timeline

### YYYY-MM-DD
- Event:
- Evidence:
- Follow-up:
```

For spreadsheets, use equivalent columns and one row per specimen. Put repeat events in a linked log sheet when possible instead of packing history into one cell.

## Event Log Types

Use consistent event names:

- `watered`
- `fertilized`
- `repotted`
- `pruned`
- `wired`
- `wire_checked`
- `wire_removed`
- `photographed`
- `scanned`
- `digital_twin_synced`
- `bud_observed`
- `bloom_observed`
- `propagation_started`
- `cutting_rooted`
- `health_flag_added`
- `health_flag_resolved`

Each event should include date, evidence, action, result, and follow-up.

## Care Scheduling Principles

Prefer observation loops over fixed timers:

- Watering: soil moisture, pot weight, leaf turgor, season, indoor heat, outdoor heat, substrate, pot size, and recent pruning/repotting.
- Fertilizer: active growth, recent repotting, stress status, species, and product strength.
- Repotting/root work: species, rootbound evidence, substrate breakdown, season, and recent stress.
- Pruning: active growth, health, design goal, and recovery capacity.
- Wiring: branch growth rate, wire material, gauge, species, and bite-in risk.
- Propagation: season, cutting maturity, humidity, temperature, and user setup.

If the user asks for a recurring reminder, phrase it as a check unless a fixed action is genuinely appropriate. Example: "Check soil moisture every 2 days during hot balcony weather" is safer than "Water every 2 days."

## Calendar-Ready Reminder Format

Use this format when drafting reminders:

```markdown
### Reminder
- Title:
- Plant:
- Date/time:
- Recurrence:
- Priority:
- Trigger/evidence:
- Checklist:
- Done condition:
```

Create live calendar events only when the user explicitly asks and the relevant calendar connector/tool is available. Otherwise provide entries ready to paste into a calendar or task app.

## Care Checklist Format

```markdown
## Care Checklist - <plant_id> - YYYY-MM-DD

- Inspect newest leaves and branch tips.
- Check soil moisture at root depth.
- Compare pot weight to recently watered baseline.
- Inspect undersides of leaves and branch crotches for pests.
- Review any active markers: wire, bud, aerial root, cutting, or health flag.
- Record action taken and next check date.
```

Tailor the checklist to the plant and current goal. For a bonsai under wire, include wire bite checks. For a bud tracker, include hydration stability and photo update. For a digital twin, include "capture updated photos from the same angles."

## Sync Note Format

After any meaningful care or digital twin session, append:

```markdown
### YYYY-MM-DD - <event type>
- Goal:
- Inputs:
- Actions:
- Outputs:
- Decisions:
- Risk:
- Follow-up:
- Open questions:
```
