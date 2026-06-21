# Shared Sonic Blueprint + Per-Week Energy Progression

A 4-week series must feel recognizably the same series while growing in intensity across weeks. This reference defines the blueprint that stays constant and the per-week curve that evolves.

## The shared blueprint

Every week of the series shares:

| Element | Value |
|---|---|
| Phase arc | Grounding → Rising heat → Peak → Heart-opener → Descent → Savasana |
| Anchor artists | One Lane 8 + one Tinlicker per week (see anchor-injection.md) |
| Tonal center | Predominantly minor / modal (darker, inward) with major-key releases at peak |
| Texture signature | Builds feature long risers / filtered pads; drops land on the beat exactly |
| BPM floor | 88 BPM (warm-up / grounding) |
| BPM ceiling | 130 BPM (peak) |
| Teaching-friendly filter | On by default — no explicit content, voice headroom at peak |

## Per-week BPM and intensity curve

| Week | Theme | Peak BPM target | Intensity modifier | Notes |
|---|---|---|---:|---|
| 1 | Foundation | 124 BPM | baseline | Introduce the arc; don't overshoot |
| 2 | Build | 127 BPM | +2–3% above W1 intensity | Push grounding longer before rising |
| 3 | Peak | 129 BPM | +2–3% above W2 intensity | Highest heat; extend peak phase |
| 4 | Integration | 124 BPM | drop back to W1 range | Mirror W1 emotionally; close the arc |

Intensity modifier applies to average BPM across the peak phase (not the whole class). Savasana always ends in the 88–100 BPM range regardless of week.

## Phase arc with duration targets

| Phase | Duration | BPM range | Energy target |
|---|---|---|---|
| Grounding | 5–8 min | 88–100 | slow, open, breathable |
| Rising heat | 12–15 min | 100–118 | climbing, rhythmic |
| Peak (Sun A/B) | 18–22 min | 118–130 | sustained high intensity |
| Heart-opener | 5–8 min | 108–118 | melodic, emotional release |
| Descent | 8–10 min | 100–110 | gradual unwind |
| Savasana | 5–7 min | 88–98 | minimal, spacious |

Total: ~55–65 minutes (adjustable via the context profile).

## Week 4 "integration" guidance

Week 4 intentionally mirrors Week 1 to signal arc completion. Reuse the Week 1 phase arc, return peak BPM to baseline, and if possible reprise one non-anchor track from Week 1 as an intentional callback (flag it in the state file as `callback_from_week_1`).

## Blueprint file location

`contexts/series/sonic-blueprint.yaml` stores the shared blueprint. The 4-week progression spec lives in `contexts/series/4week-yoga-progression.json`. This reference documents their relationship; neither file overrides the other — the generator combines both.
