# Anchor Artist Phase Placement Rules

Anchor artists (Lane 8, Tinlicker) each have a preferred phase slot in each
episode. The placement system resolves priorities in order: the per-episode
`anchor_rules` from the series context take precedence, then these defaults.

---

## Lane 8 — default phase order

Lane 8 tracks are uplifting, melodic, and vocally warm. They work best during
moments of energy build or emotional peak.

| Priority | Phase | Rationale |
|---|---|---|
| 1 | Sun A (Rising) | Builds energy with the opening salutation series |
| 2 | Sun B (Peak) | Sustains intensity through standing and balance work |
| 3 | Heart Opener | Lyrical vocals land well during chest/backbend sequences |
| 4 | Balance Series | Clean rhythmic phrasing supports held balance postures |
| 5 | Cool Down (Descent) | Lower energy Lane 8 tracks transition out of the peak |

## Tinlicker — default phase order

Tinlicker tracks are deeper, more atmospheric, and emotionally spacious.
They resonate during descent and rest phases.

| Priority | Phase | Rationale |
|---|---|---|
| 1 | Cool Down (Descent) | Progressive-house texture carries floor-work momentum |
| 2 | Savasana | Slower, ambient Tinlicker tracks fill the closing window |
| 3 | Savasana (Extended) | Week 4 longer savasana; second preference for atmospheric cuts |
| 4 | Sun B (Peak) | High-BPM Tinlicker works for a mid-peak shift when needed |

---

## Resolution order

1. Check `episode["anchor_rules"][artist_key]` — explicit per-week list wins.
2. Fall back to the table above.
3. If none of the preferred phases exist in the playlist, use the first phase.

## Series-global uniqueness

Each anchor track URI must be unique across all four episodes. The series
`used_track_ids` set accumulates as episodes are built; a track already in
the set is skipped even if it is the highest-priority candidate.

## One anchor per artist per episode

Each of Lane 8 and Tinlicker appears exactly once per episode. No episode
has two Lane 8 tracks or two Tinlicker tracks.

---

## Per-week placement summary (4-week yoga progression)

| Week | Theme | Lane 8 preferred phase | Tinlicker preferred phase |
|---|---|---|---|
| 1 | Rooting | Sun A (Rising) | Cool Down (Descent) |
| 2 | Expanding | Sun B (Peak) | Sun B (Peak) or Cool Down |
| 3 | Refining | Sun B (Peak) | Cool Down (Descent) |
| 4 | Integrating | Sun A (Rising) | Savasana (Extended) |

These are defaults from `anchor_rules` in the series context. The placement
engine respects them if those phases exist; otherwise it falls back to the
general priority list above.
