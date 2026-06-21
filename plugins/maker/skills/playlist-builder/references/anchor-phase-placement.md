# Per-Week Anchor Phase Placement

Anchor tracks must land in phase-appropriate slots each week. This reference defines the placement rotation so anchors don't always appear in the same position, keeping the arc fresh across the series.

## Default placement rotation

| Week | Anchor A (Lane 8) slot | Anchor B (Tinlicker) slot |
|---|---|---|
| 1 | warm-up (Rising heat, early) | heart-opener |
| 2 | peak (Sun A/B high point) | cool-down (Descent, early) |
| 3 | heart-opener | peak (Sun A/B high point) |
| 4 | grounding (final track before Rising heat) | savasana |

The rotation ensures each anchor appears at least once in a high-energy slot and at least once in a low-energy slot across the series. It also means the listener never anticipates "oh, Lane 8 is always the peak track."

## Phase slot definitions

| Slot name | Maps to phase | Position within phase |
|---|---|---|
| grounding | Grounding | any track in the grounding phase |
| warm-up | Rising heat | first 2–3 tracks of rising heat |
| peak | Peak (Sun A/B) | highest-BPM track of the peak phase |
| heart-opener | Heart-opener | first or second track of heart-opener |
| cool-down | Descent | first 1–2 tracks of descent |
| savasana | Savasana | any track in savasana |

## Overriding the rotation

The user may override any slot assignment per-week. Override in the series state file:

```json
"anchor_placement_overrides": {
  "week_2": {
    "anchor_A": "heart-opener",
    "anchor_B": "peak"
  }
}
```

When an override is present, skip the rotation table for that week and use the override values.

## BPM compatibility check

Before placing an anchor track in a slot, verify its BPM is within the slot's expected range (see sonic-blueprint.md phase arc table). If the track BPM is outside ±4 BPM of the slot range, flag a warning and suggest an alternate slot from the artist's catalog.

## Teach-friendliness check

Anchors placed in peak or warm-up slots must pass the teach-friendly filter (voice headroom, beat clarity). Anchors placed in savasana or grounding slots may prioritize texture over beat clarity.
