# Propagation Tracker

Read this reference when the user wants to take cuttings, air-layer, or track propagules from rooting through to independent specimens. Ficus roots readily from cuttings, and the user wants to expand the collection over time. This sub-module pairs with [`chrono-engine.md`](chrono-engine.md) (optimal cutting windows by species/season), [`collection-records-and-care.md`](collection-records-and-care.md) (event log + new specimen records), and [`blender-digital-twin.md`](blender-digital-twin.md) (scaffolding a twin once a propagule is independent).

## Two sub-flows: tip/stem cuttings vs. air-layering

Treat these separately — air-layering is more advanced.

### Tip / stem cuttings (the common case)

- **When**: warm, actively-growing season is best; use the chrono engine to pick the window. Avoid cool/dormant periods for difficult species.
- **What to take**: a healthy, non-flowering shoot. Target node length ~2-4 nodes; cut just below a node (the node is where roots form most readily). For ficus, semi-hardwood tip cuttings root well.
- **Prep**: remove lower leaves, optionally reduce large leaves to limit transpiration, optional rooting hormone, insert into a free-draining medium or water, keep warm and humid (a clear cover/bag), bright indirect light.
- **Rooting time**: ficus often 3-6 weeks in warm conditions; varies widely by species and warmth.

### Air-layering (advanced sub-flow)

- Use when you want a larger, already-thick propagule (e.g. to start a bonsai with instant trunk girth) or the shoot is hard to root as a cutting.
- Concept: girdle/ring a section of stem, wrap with damp sphagnum inside a moisture-retaining sleeve, keep moist until roots form **on the parent plant**, then sever below the new roots and pot up.
- Treat as its own tracked flow; it overlaps the aerial-root lifecycle in [`aerial-roots-nebari.md`](aerial-roots-nebari.md). Flag it as more advanced and higher-effort than tip cuttings.

## Lifecycle states and event types

Track each propagule through:

```
started  ->  rooted  ->  potted_up  ->  independent
                 \-> failed
```

Event types (extends `collection-records-and-care.md`):

- `propagation_started` — cutting taken / air-layer wrapped. Record method, parent `plant_id`, node count/length, date, conditions.
- `cutting_rooted` — roots confirmed. Record date and root extent.
- `cutting_potted_up` — moved to its own pot/substrate (**new event type added in v2**).
- `cutting_failed` — rotted/dried/no-take (**new event type added in v2**). Record hypothesized cause (too cold, too wet, too dry, no node, disease) so future attempts improve.

## Parent/child lineage

Track lineage so the collection's family tree is visible:

- Every propagule carries a `parent_plant_id` from the moment it is started.
- Use a child id derived from the parent: e.g. parent `ficus-benjamina-01` -> cuttings `ficus-benjamina-01-c01`, `-c02`, ... While dependent, the propagule lives as a sub-record / log lines under the parent.
- On `cutting_potted_up` and confirmed independence, **promote** it to its own full `plant_id` (you may keep the lineage id or assign a fresh collection id like `ficus-benjamina-04`) and record `parent_plant_id` in its frontmatter so lineage survives the rename.
- Once independent and worth modeling, scaffold its own digital twin with `scene_scaffold.py` (`blender-digital-twin.md`).

Suggested record frontmatter additions for propagules:

```markdown
parent_plant_id: ficus-benjamina-01
propagation_method: tip_cutting   # or air_layer
propagation_started:
propagation_state: started        # started | rooted | potted_up | independent | failed
```

## Optimal-window recommendation (via chrono engine)

When the user asks "should I take a cutting now?", route the timing through `chrono-engine.md`:

- Species growth-speed class + current phase -> is this an active-growth window?
- Recent stressors on the parent (don't take cuttings from a stressed/pest-flagged parent — check `health-diagnostics.md`).
- Emit a check, not a command: "Good cutting window opens as balcony nights stay above ~18 C; take 2-3 node semi-hardwood tips from vigorous, non-flowering shoots."

## Output contract

```markdown
## Propagation Plan — <plant_id parent> — <YYYY-MM-DD>
- Method: <tip cutting | stem cutting | air-layer>
- Window: <good now | wait until ...> (reason from chrono engine)
- Material: <node count/length, which shoots, leaf reduction, hormone?>
- Setup: <medium, humidity, light, warmth>
- Tracking: child id <parent-cNN>, state `started`
- Expected rooting: <range>, confidence <level>
- Parent health gate: <PASS | HOLD because ...>
- Follow-up checks: <cadence — e.g. mist/humidity weekly, check for roots at N weeks>
- On success: log `cutting_rooted` -> `cutting_potted_up` -> promote to own plant_id + scaffold twin
```

## Decision rules

- Don't take cuttings from a stressed, pest-flagged, or recently hard-worked parent.
- Air-layering is advanced — call it out and treat as a separate flow.
- Always set `parent_plant_id` from the start so lineage is never lost on promotion.
- Record `cutting_failed` with a cause hypothesis; failures are data that improve the next attempt.
