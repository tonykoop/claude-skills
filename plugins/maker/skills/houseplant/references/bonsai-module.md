# Bonsai Module

Read this reference when the user asks for bonsai pruning, branch selection, wiring, bending, cut placement, aerial-root guidance, nebari development, grafting concepts, or bonsai-specific follow-up schedules.

## Bonsai Intake

Before making a decisive plan, gather or infer:

- Species or likely species.
- Current date, location, indoor/outdoor placement, and active growth status.
- Last repot, root work, structural prune, maintenance prune, defoliation, fertilizer, and wiring dates.
- Health state: pests, leaf yellowing, recent leaf drop, weak growth, drought stress, root rot risk, or recent relocation.
- Intended style if known: informal upright, broom, cascade, windswept, clump, forest, root-over-rock, fusion, or "still discovering."
- Visual inputs: front/back/left/right/top, trunk/root flare, branch close-ups, canopy silhouette, and scale reference.
- Current physical constraints: wire gauges on hand, pot size, substrate, tools, and whether the user is willing to make irreversible cuts now.

## Styling Priorities

Evaluate in this order:

1. Health and recovery capacity.
2. Best front: trunk movement, nebari/root flare, branch depth, and visible flaws.
3. Trunk line and apex: avoid competing leaders unless the design intentionally uses them.
4. Primary branch structure: first branch, second branch, back branch, visual depth, and taper.
5. Problem growth: crossing branches, bar branches, inward growth, strong upward shoots, downward weak growth, reverse taper, and congested crotches.
6. Light and airflow: protect interior buds and leave enough foliage for recovery.
7. Future design: what to encourage, not only what to remove.

For ficus and other tropical indoor bonsai, account for faster warm-season growth and strong back-budding potential, but still avoid heavy work on weak or recently stressed plants.

For *Ficus benjamina* specifically, a starter plant profile lives at [`../assets/ficus-benjamina-starter.md`](../assets/ficus-benjamina-starter.md) with care preferences, fast-cambium wire-window notes, and aerial-root-as-feature guidance. Use it as a baseline when the user hasn't created their own record yet.

## Risk Levels

- `Low`: tip pruning, removing small dead twigs, shortening vigorous extensions, leaf cleanup, photo annotations, or Blender-only simulations.
- `Medium`: removing a healthy secondary branch, moderate apex reduction, wiring flexible branches, or pruning during active growth on a healthy plant.
- `High`: removing a primary branch, heavy trunk chop, major root work, hard bend on lignified wood, out-of-season structural work, work on a weak plant, or recommendations based on incomplete media.

When the user wants decisive guidance, still include a pre-action verification step. Example: "Before cutting, confirm this is branch `L02` by matching the red marker to the lower-left branch that crosses in front of the trunk."

## Pruning Plan Format

Use this structure:

```markdown
## Pruning Plan

| Id | Action | Why | Risk | Verify Before Cutting | Aftercare | Follow-up |
|---|---|---|---|---|---|---|
| L02-A | Cut back to the first outward-facing node | Opens trunk line and reduces crossing growth | Medium | Confirm the branch crosses in front of the trunk from the chosen front | Bright indirect light, normal moisture checks, no heavy fertilizer for 7 days | Check back-budding in 3-4 weeks |
```

Add a short "do not cut" list for branches that should be preserved or encouraged.

## Wiring and Bending

Use wiring only when it serves a clear design goal. Estimate wire gauge from branch diameter when possible; a common starting heuristic is wire about one-third the branch diameter, adjusted for species flexibility and wire material. Ask what wire sizes the user has if the plan depends on exact gauge.

Plan wire work with:

- Target branch id and bend goal.
- Wire material and gauge estimate.
- Anchor point.
- Coil direction and approximate angle.
- Bend amount and whether it should be staged.
- Risk of cracking, bite-in, or scarring.
- Inspection cadence and removal window.

During active growth, schedule bite-in checks every 1-2 weeks. For vigorous ficus, wire can mark quickly; use shorter inspection intervals and remove or reapply before the bark swells around the wire.

## Aerial Roots and Nebari

For ficus-like species, track aerial roots and root flare as design features:

- Mark promising aerial root tips in photos or Blender with teal markers.
- Suggest humidity tents, damp sphagnum contact, straw/tube guides, and careful routing only when the plant is healthy and warm enough for active growth.
- Track whether a guided root has reached soil, thickened, fused, or become a structural element.
- Avoid root manipulation immediately after major pruning or stress unless the user accepts high risk.

## Bud, Bloom, and Growth Event Tracking

Use pink markers for buds, bloom sites, new flushes, fruit, or other events the user wants to anticipate. Record:

- Event type and stage.
- Location on the plant or Blender object id.
- First observed date.
- Photo path if available.
- Expected window and confidence.
- Care adjustments to avoid bud drop or stress.

When species-specific bloom timing is uncertain, use the user's historical logs first, then state that the forecast is provisional.

## Aftercare Defaults

After structural pruning or wiring:

- Keep light stable and avoid additional major stressors.
- Monitor soil moisture more closely instead of automatically increasing watering.
- Pause or reduce fertilizer briefly after hard pruning if root uptake or stress is uncertain.
- Watch for dieback, latex/sap bleeding, pest exposure, wire bite, and branch cracking.
- Schedule a follow-up photo review rather than assuming the design response.
