# Aerial-Root and Nebari Guidance Tracker

Read this reference when the user wants to develop, guide, or track aerial roots and root flare (nebari) — especially on *Ficus benjamina* and other ficus, where a braided aerial-root nebari is often the specimen's strongest design feature. This expands the brief note in [`bonsai-module.md`](bonsai-module.md). It uses [`../scripts/cut_marker.py`](../scripts/cut_marker.py) with `SEMANTIC="aerial_root"` (teal) to mark tips, and the new [`../scripts/aerial_root_trace.py`](../scripts/aerial_root_trace.py) to draw a guided root path from a branch down to substrate in the digital twin. Pairs with [`chrono-engine.md`](chrono-engine.md) for thickening-rate timing and [`collection-records-and-care.md`](collection-records-and-care.md) for the lifecycle event log.

## Why nebari matters

Nebari (surface root flare) and, on ficus, fused aerial roots create the impression of age and stability. On the maintainer's *Ficus benjamina* starter the braided aerial-root nebari is the headline feature and is actively being trained — see [`../assets/ficus-benjamina-starter.md`](../assets/ficus-benjamina-starter.md).

## Lifecycle states

Track each guided root through these states. Record the transition as a timeline event (see event-type additions below):

```
tip_promising  ->  guided  ->  reached_soil  ->  thickening  ->  fused
```

| State | Meaning | What to do |
|---|---|---|
| `tip_promising` | A new aerial root tip has emerged and is worth guiding | Mark teal in the twin; decide a target landing point on the substrate/trunk |
| `guided` | A guide (sphagnum, straw/tube, humidity tent) is directing it | Maintain humidity/contact; check the guide weekly; do not let it dry |
| `reached_soil` | Tip has entered substrate (or contacted target trunk for a fusing nebari) | Stop guiding the tip; protect the contact point; begin thickening watch |
| `thickening` | Root is gaining girth | Track girth over time; this is where the nebari "earns" its look |
| `fused` | Root has merged into structural trunk/nebari wood | Treat as permanent structure; record final girth and date |

## Intervention gate: only when healthy and warm

Suggest interventions (sphagnum wrapping, straw/tube guides, humidity tents, misting routines) **only when the plant is healthy and warm enough for active growth.** Aerial roots are produced and extended in warm, humid, actively growing conditions. Do **not** recommend new aerial-root work when:

- The plant is stressed, pest-flagged (see [`health-diagnostics.md`](health-diagnostics.md)), or recently hard-pruned/repotted.
- The room is cool or the plant is in dormancy/slow phase (the chrono engine will tell you).

In those cases, log the promising tip, keep humidity stable, and **wait** for active growth. State the gate explicitly in your recommendation.

## Guidance techniques (healthy, warm plants only)

- **Sphagnum contact / wrap** — keep a damp sphagnum collar against the root path so the tip stays moist and is encouraged to extend and thicken. Re-moisten on the chrono-engine cadence.
- **Straw / tube guide** — route the root through a translucent straw or tube to keep it straight and direct it to a chosen landing point; useful for building a deliberate braided nebari.
- **Humidity tent** — a loose clear cover raises local humidity to trigger/extend aerial roots; vent it to avoid rot, and remove once roots are established.
- **Routing for a braid** — when building a braided nebari, plan landing points so multiple roots converge and fuse at the flare; mark each target in the twin.

## Predicting thickening rate

Thickening tracks the species growth-speed class from [`chrono-engine.md`](chrono-engine.md): vigorous ficus thicken noticeably over a warm season; slow/woody species take far longer. Give ranges, not promises, and confirm by **measuring girth over time** (log it). A root only counts as `fused` when it visibly merges into trunk wood — confirm visually, do not assume from age.

## Digital-twin tracing

Use the marker for tips and the trace script for the guided path:

```python
# 1) Mark the promising tip (teal)
PLANT_ID = "ficus-benjamina-01"; BRANCH_ID = "aerialL01"; SUFFIX = "2026-06-15"
LOCATION = (0.03, 0.06, 0.30); SEMANTIC = "aerial_root"; RADIUS = 0.004
exec(open(r"<path>/scripts/cut_marker.py").read())

# 2) Trace a guided path from the branch tip down to the substrate landing point
PLANT_ID = "ficus-benjamina-01"; ROOT_ID = "aerialL01"
START = (0.03, 0.06, 0.30)        # current tip
END = (0.01, 0.02, 0.00)          # target landing point on substrate
STATE = "guided"
exec(open(r"<path>/scripts/aerial_root_trace.py").read())
```

`aerial_root_trace.py` builds a teal poly-curve from `START` to `END` with a gentle vertical droop (roots hang, not straight lines), drops it in `04_markers`, and stamps `root_id`, `state`, and `created` for cross-session recovery. Update its `STATE` custom property as the root advances through the lifecycle.

## Event-type additions for the record

Add these aerial-root lifecycle events to the timeline (extends the event list in `collection-records-and-care.md`):

- `aerial_root_observed` — tip first seen (`tip_promising`).
- `aerial_root_guided` — a guide applied (`guided`).
- `aerial_root_reached_soil` — tip entered substrate / contacted target (`reached_soil`).
- `aerial_root_thickening` — girth gain logged (`thickening`), include measured girth.
- `aerial_root_fused` — merged into structural wood (`fused`), include final girth + date.

Each event records date, the marker/trace object id, evidence (photo), measured girth where relevant, and the next check date.

## Output contract

```markdown
## Aerial-Root Plan — <plant_id> — <YYYY-MM-DD>
- Root id: <id>  | State: <lifecycle state>
- Health gate: <PASS healthy+warm | HOLD because ...>
- Recommended guidance: <sphagnum | straw/tube | humidity tent | route-for-braid | wait>
- Twin: teal marker + trace <object id>
- Thickening outlook: <range>, confirm by re-measuring girth
- Risk: <Low marker/trace only | Medium guiding on healthy plant | High root work on stressed plant>
- Next check: <date from chrono engine>
```
