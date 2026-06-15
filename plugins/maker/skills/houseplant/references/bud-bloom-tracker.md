# Bud and Bloom Chrono-Tracker

Read this reference when the user spots a flower bud, new leaf flush, or fruit set and wants it tracked, marked on the digital twin, and forecast to a bloom window. Pairs with [`chrono-engine.md`](chrono-engine.md) (timing), [`collection-records-and-care.md`](collection-records-and-care.md) (event log + reminders), and the existing [`../scripts/cut_marker.py`](../scripts/cut_marker.py) with `SEMANTIC="bud"` (pink). **No new script is required** — the marker workflow already exists.

## When this applies (and when it does not)

Track ephemeral botanical events on species where the event is **externally visible**:

- Flowering houseplants: orchids (*Phalaenopsis*), *Hoya*, jasmine, citrus, African violet, jade (*Crassula*), *Schlumbergera* (Christmas cactus), *Carmona* (Fukien tea bonsai), *Bougainvillea*.
- New leaf flushes / candle extension on any tracked specimen (useful even on non-flowering plants for vigor logging).
- Fruit set on citrus, *Carmona*, and similar.

**Skip *Ficus benjamina* (and figs generally): the flowers are enclosed inside the syconium (the fig body) and are not externally observable.** A ficus will not show a visible bud-to-bloom progression, so do not promise one. You *can* still track leaf flushes on a ficus as vigor events.

## Marker workflow (reuses `cut_marker.py`)

When the user points to a bud/flush location on the twin:

```python
PLANT_ID = "orchid-phalaenopsis-01"
BRANCH_ID = "spike01"        # or node/branch id
SUFFIX = "2026-06-15"        # first-observed date keeps markers distinct over time
LOCATION = (0.04, 0.11, 0.22)
SEMANTIC = "bud"             # pink — bud / bloom event
RADIUS = 0.004
exec(open(r"<path>/scripts/cut_marker.py").read())
```

The marker lands in `Plant_<plant_id>__04_markers` with `semantic="bud"` stamped. Use the first-observed date as the suffix so successive observations on the same spike form a dated trail rather than overwriting.

## Logging the observation

Record on the plant timeline with the existing event types:

- `bud_observed` — first sighting. Capture: location/object id, first-observed date, stage (tight bud / swelling / showing color), photo path, the forecast window + confidence.
- `bloom_observed` — open flower. Capture the open date so the user's own history sharpens future forecasts.
- If a bud **drops**, do not invent a new event type — record a `bud_observed` follow-up line noting `dropped` plus a hypothesized cause (see below).

## Forecasting the bloom window

Estimate conservatively and make confidence explicit. Order of evidence:

1. **The user's own historical logs first.** If this plant bloomed before, the interval from comparable bud stage to open flower is the best predictor. Use it and say so.
2. **Species baseline** as a fallback (rough ranges; vary widely by light/temperature):
   - *Phalaenopsis*: spike emergence to first open flower ~8-12 weeks; a visibly swelling bud to open ~1-3 weeks.
   - *Hoya*: peduncle/spur to open umbel ~3-6 weeks.
   - Jade (*Crassula*): buds to bloom ~2-4 weeks, late autumn/winter under cool-night + short-day conditions.
   - *Schlumbergera*: visible bud to open ~4-8 weeks; bud drop is common if light/temperature/watering shifts.
   - Citrus / *Carmona*: bud to open ~2-5 weeks in warm active growth.
3. **Modulate by current conditions** via the chrono engine — warmth and good light shorten the window; cool/dim lengthens it.

Output format:

```markdown
## Bloom Forecast — <plant_id> — <YYYY-MM-DD>
- Event: <bud / spike / flush> at <location/object id>
- Stage: <tight | swelling | showing color>
- Forecast window: <date range>
- Confidence: <low | medium | high> — based on <your-own-log | species-baseline-only>
- Marker: pink, <plant_id>_bud_marker_<branch_id>_<date>
- Care to protect it: <stable light/temp, avoid moving it, steady moisture>
- Calendar check: "Photograph <plant_id> <event> every <cadence> until open."
```

State confidence honestly. With no prior log for this plant, say the forecast is **species-baseline-only and provisional**, and give a range, not a single date.

## Bud drop: record, then hypothesize cause

Bud drop is information, not just loss. Log it and cross-reference recent stressors from the timeline and [`health-diagnostics.md`](health-diagnostics.md). Common culprits, in rough order:

- Moved/rotated plant or sudden light change (very common in *Phalaenopsis*, *Schlumbergera*).
- Temperature swing, draft, or proximity to heat/AC vent.
- Watering stress (let dry out, or waterlogged) during budding.
- Low humidity, or fertilizer change mid-bud.

Suggest stabilizing conditions and a follow-up photo check; do not over-diagnose from a single dropped bud.

## Calendar pairing

Hand the "photograph every N days until open" line and a "check at end of forecast window" line to the **Calendar-Ready Reminder Format** in `collection-records-and-care.md`. Live calendar events only on explicit user request with a connector available.
