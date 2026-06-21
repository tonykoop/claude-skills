# Playlist Series Sonic Blueprint

A "sonic blueprint" is the shared energy and BPM contract that ties all four
episodes of a progression series together. Each episode applies a week-specific
BPM scale factor and energy ceiling against this common baseline.

---

## 4-Week Yoga Progression Blueprint

### Baseline BPM range

| Phase | Min BPM | Max BPM | Notes |
|---|---|---|---|
| Opening / Centering | 60 | 80 | Ambient or slow groove; breath-sync |
| Sun A (Rising) | 100 | 118 | Steady escalation; teacher counts on beat |
| Sun B (Peak) | 118 | 132 | Maximum intensity; sustain 20–24 min |
| Heart Opener | 100 | 115 | Lyrical or melodic; emotional arc |
| Balance Series | 108 | 120 | Clean structure; predictable phrasing |
| Cool Down (Descent) | 85 | 105 | Step-down momentum |
| Savasana / Extended | 55 | 72 | No percussion; wide dynamic range |

### Per-week BPM scale factors

These multipliers shift the whole baseline range up or down for the week,
encoding the arc Rooting → Expanding → Refining → Integrating.

| Week | Theme | BPM Scale | Effect |
|---|---|---|---|
| 1 | Rooting | ×1.00 | Baseline — establish ground |
| 2 | Expanding | ×1.02 | Slight lift — open and energize |
| 3 | Refining | ×1.03 | Peak pace — precision at speed |
| 4 | Integrating | ×0.98 | Pull back — depth over intensity |

**Example:** Week 3, Sun B (Peak) — baseline 118–132 → after ×1.03: 122–136.

### Energy ceiling per week

The energy ceiling caps how high the `energy` tag on any phase can go,
softening or heightening the arc without changing the phase structure.

| Week | Energy ceiling | Arc intention |
|---|---|---|
| 1 | 7/10 | Grounded; manageable first week |
| 2 | 9/10 | Full expansion |
| 3 | 9/10 | Peak refinement |
| 4 | 8/10 | Integration — slightly softer peak |

---

## How `BlueprintConfig` uses these values

`scripts/blueprint.py` exposes a `BlueprintConfig` dataclass. Callers pass
a week number; `apply()` returns a modified copy of the phase list with
BPM bounds scaled and energy values clamped to the week's ceiling.

```python
from blueprint import BlueprintConfig, SERIES_BLUEPRINT

cfg = BlueprintConfig.for_week(week=2, blueprint=SERIES_BLUEPRINT)
phases_w2 = cfg.apply(episode["phases"])
# phases_w2[i]["bpm_min"] and ["bpm_max"] reflect the ×1.02 scale
# phases_w2[i]["energy"] is clamped to ≤ 9
```

### Schema additions to phase objects

`apply()` adds these keys to each phase dict (does not mutate the original):

| Key | Type | Description |
|---|---|---|
| `bpm_min` | float | Scaled lower bound for BPM selection |
| `bpm_max` | float | Scaled upper bound for BPM selection |
| `energy_effective` | int | min(phase["energy"], week_ceiling) |
| `bpm_scale` | float | The scale factor applied (for traceability) |
| `energy_ceiling` | int | The week's ceiling (for traceability) |

---

## Anchor-artist BPM note

Anchor tracks (Lane 8, Tinlicker) are injected AFTER BPM scaling. Their
actual BPM is not modified; instead, the scaled BPM range should be used as
a _preference signal_ when selecting from the catalog. See `anchor.py`.
