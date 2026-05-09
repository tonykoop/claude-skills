# 04 - Cut Path Strategy

This is the section you flagged. You haven't run plasma at this scale before, so the plan below is conservative and explicit. Follow in order.

---

## Guiding principles (read first)

1. **Internal cuts before external.** If you cut the outer profile first, the part can shift, drop, or twist before the inner features are pierced. Always do every internal pierce while the part is still locked into the parent sheet.
2. **Pierce in scrap, lead in to the cut line.** A pierce blows a tapered, splattered hole. You never want that hole to BE part of the finished edge. Lead-in is a short ramp from a pierce point in scrap into the kerf.
3. **Lead-out into scrap as well**, especially on closed loops, to avoid a divot at the closing point.
4. **Sequence small features first, large last.** Heat doesn't accumulate as much, less warping, and the small features still have rigid surrounding metal to anchor them.
5. **Use micro-tabs on the outer profile only.** Internal voids fall away into the slat bed - that's fine. The outer trellis itself is a 28 lb part - it cannot fall away mid-cut. Tab it.

---

## Cut order

### Stage 1 - Reference
- **Cut 1**: Mark the sheet origin (top-left corner of usable material). Operator software will set this as the table zero. Confirm zero with a dry run (rapid trace at Z+0.5", torch off) before any pierce.

### Stage 2 - Internal features (in order of size, smallest first)
- **Cuts 2-9**: 8 small leaf vein slots (interior to 2.5" leaves). Each is a closed slot: pierce in the center of the slot, lead in 0.10" to the cut line, traverse the loop, lead out 0.10" back into the dropped slug.
- **Cuts 10-15**: 6 medium leaf vein slots.
- **Cuts 16-19**: 4 large leaf vein slots.
- **Cuts 20-21**: 2 tendril through-holes (the closed loops in the spiral curls). These are larger pierces (~0.4" diameter scrap) - watch for blowback.

Pause checkpoint after Stage 2: visually confirm all interior cuts cleared. Any uncut slug still hanging means the pierce didn't go through - mark and re-pierce manually.

### Stage 3 - Outer profile (the big one)
- **Cut 22**: The full silhouette outline. ONE continuous path with micro-tabs.

#### Lead-in for outer profile
- Start point: bottom of the spine, on the stake portion (the 6" buried part). This means the lead-in scar is below ground after install - invisible.
- Lead-in geometry: **arc lead-in**, 0.25" radius, tangent to the cut line. Better than a straight lead-in for organic curves because there's no kink where the lead meets the path.
- Pierce delay: per machine card, typically 0.5-0.7s for 1/4" mild steel.

#### Micro-tabs (CRITICAL)
Place 4 tabs on the outer profile:
1. Bottom of stake (where lead-in starts) - 0.10" tab
2. Mid-spine, ~24" up, in a flat region - 0.10" tab
3. Top of trellis, on the topmost leaf tip - 0.08" tab
4. Mid-spine, ~50" up, on the opposite side from #2 - 0.10" tab

Tab logic:
- Without tabs, the freed silhouette torques and droops into the kerf as cuts complete, ruining the cut and risking torch crash.
- 4 tabs distribute load. 2 are on the spine (stiff), 2 are on protrusions to keep the perimeter from rolling.
- Tab width 0.10" = ~1.6x kerf. Snaps off cleanly with a tap; grinds flush in <30 seconds.

#### Lead-out
- Same arc geometry, into scrap, 0.25" radius.
- The lead-out point should NOT coincide with the lead-in - offset by at least 0.5" along the path so the start/end pierce craters aren't stacked.

### Stage 4 - Bracket plates (if cutting from offcut)
- Two small 2" x 4" rectangles with bolt holes. Cut holes first as internal features, then perimeter. Tabs not needed - parts are small and won't shift.

---

## Tab break-out and finishing

After cut completes:
1. Let the part sit on the table 60-90 seconds before lifting. 1/4" plate retains heat.
2. Wear leather gloves to lift. The cut edge can still scorch nitrile gloves.
3. Tap each tab with a 16 oz hammer; it should fracture cleanly. If it bends instead, the tab is too wide - score with a cutoff wheel and snap.
4. Grind tab stubs flush with a 60-grit flap disc.

---

## Cut-path failure modes specific to this job

| Symptom | Cause | Mitigation |
|---|---|---|
| Tendril spirals come out blobby / curves not smooth | Cut speed too high for tight radii | CAM should auto-slow on small radii; verify in preview |
| Inner vein slugs don't drop | Pierce didn't fully penetrate (cold pierce) | Increase pierce delay 0.1s; check consumable wear |
| Spine warps / banana-shaped | Asymmetric heat input | The mirrored design helps; if still warping, alternate left-side and right-side cuts in Stage 2 |
| Edge dross stripe along bottom | Speed too low | Bump feedrate 5%; check air pressure |
| Top edge bevel obvious | Standard plasma artifact | Orient the bevel-out side toward viewer (consult shop on which side of cut is which) |

---

## Pre-flight: do this BEFORE the real cut

**Do a 6" x 6" test square** in the corner of your sheet:
- Same material, same consumables, same machine settings as the real run.
- Cut a 4" outer square with two 1" interior circles (to test pierce + small-radius behavior).
- Inspect: bevel angle, dross, slag, kerf width.
- Adjust feedrate / pierce delay as needed BEFORE starting Stage 1.

This costs 15 minutes and ~10 cents of consumables. It will save the ~$80 plate if a setting is off.
