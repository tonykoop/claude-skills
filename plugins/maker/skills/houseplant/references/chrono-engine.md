# Chrono-Horticultural Engine

Read this reference when the user wants dynamic watering, fertilizing, or **wire-removal-inspection** scheduling — i.e. any care timing question. This is the scheduling brain that turns species + season + recent stressors into calendar-ready **checks** rather than fixed timers. It pairs with [`collection-records-and-care.md`](collection-records-and-care.md) (record/reminder formats) and feeds [`propagation.md`](propagation.md) (optimal cutting windows) and [`bonsai-module.md`](bonsai-module.md) (wire bite-in).

## Core principle: schedule checks, not actions

A fixed "water every 3 days" rule fails the moment the balcony gets hot or the plant is repotted. Emit **observation loops** instead:

> Check soil moisture at root depth every 2 days while balcony highs stay above ~26 C; water only when the top 2-3 cm is dry and the pot feels light.

Convert the user's situation into a **cadence** (how often to check) plus a **trigger** (the observation that fires the action) plus a **done condition**.

## Inputs the engine ingests

- **Species profile** — growth speed class (see table), drought tolerance, dormancy behavior, indoor flowering relevance.
- **Current date / season / hemisphere** — derive the growth phase (active growth, hardening, dormancy, repot window).
- **Indoor vs. outdoor** and microclimate signals — balcony heat, indoor heating/AC, humidity, light level.
- **Recent stressors** — repot, hard prune, defoliation, relocation, pest event. Each compresses or suspends normal cadence.
- **Local climate signal** if available — a forecast of a hot spell tightens the watering-check cadence; a cold snap loosens it. Only use a live weather connector when one is connected; otherwise ask the user for the rough forecast.

## Growth-speed classes (drives every cadence)

| Class | Examples | Growing-season check cadence (watering) | Wire bite-in inspection cadence |
|---|---|---|---|
| Fast / vigorous tropical | *Ficus benjamina*, *F. microcarpa*, *Schefflera* | every 1-2 days in heat, 3-4 days mild | every **5-10 days** in active growth |
| Moderate | *Carmona*, *Ulmus parvifolia* (Chinese elm), most foliage houseplants | every 2-3 days in heat, 4-6 days mild | every **2-3 weeks** |
| Slow / woody | pines, junipers, maples, succulents/jade | every 4-7 days, weekly+ when cool | every **3-6 weeks**, watch lignified bark closely |

These are starting heuristics. Always widen the interval for cool/dim conditions and tighten it for heat, wind, small pots, free-draining substrate, or recent root reduction.

## Phase modifiers

Apply these on top of the base cadence:

- **Just repotted / root-reduced** — reduce fertilizer to zero for ~3-4 weeks; keep in bright shade; tighten moisture *checks* but resist overwatering a reduced root system.
- **Just hard-pruned / defoliated** — pause fertilizer ~1-2 weeks; monitor for back-budding; do not increase watering by default (less foliage = less uptake).
- **Active growth (warm, lengthening days)** — fertilizer cadence opens up (species-appropriate dilute feeding); wire bite-in risk is highest → use the *short* end of the inspection range.
- **Dormancy / cool season** — stretch watering checks, suspend or minimize fertilizer, and lengthen wire-inspection cadence (cambium thickens slowly).
- **Stressed / pest-flagged** (from [`health-diagnostics.md`](health-diagnostics.md)) — suspend fertilizer, no structural work, watering checks driven purely by the plant not the calendar.

## Computing the watering/fertilizing cadence

The watering-check and fertilizing cadences above are implemented in
[`../scripts/care_cadence.py`](../scripts/care_cadence.py) (pure Python, no bpy):
it turns a growth-speed class + phase + heat signal + recent stressors into a
calendar-ready watering **check** (cadence + trigger + done-condition, phrased as
an observation loop, not a fixed timer) and a fertilizing cadence that suspends
in dormancy and for ~6 weeks after a repot. Import `care_schedule(...)` or run it
with the documented overridable globals. (Wire-removal windows stay in
`wire_window.py`, below.)

## Wire-removal inspection windows

This is the engine's headline feature: **wire bites in as the branch thickens, and thickening rate is species- and season-dependent.** From the `wired` event date, compute an inspection window rather than a fixed removal date, because the branch — not the calendar — decides when the wire must come off.

Logic (implemented in [`../scripts/wire_window.py`](../scripts/wire_window.py)):

1. Take the `wired` date, the species growth-speed class, and whether the plant is in active growth.
2. Emit a **first-inspection date** at the short end of the class window and a **recheck cadence** until removal.
3. Phrase every entry as a check: "Inspect branch R02 wire for bite-in starting `<date>`, then every `<cadence>`; remove or reapply the moment the bark starts to swell around the wire."
4. Escalate: on a vigorous ficus in summer, the first inspection can be as early as 5-7 days. Never let a fast grower's wire go unchecked for a month.

Record `wire_checked` on each inspection and `wire_removed` when it comes off (event types already in `collection-records-and-care.md`).

## Output: a chrono care plan

```markdown
## Chrono Care Plan — <plant_id> — <YYYY-MM-DD>

Phase: <active growth | hardening | dormancy | post-repot | post-prune>
Drivers: <species growth class>, <indoor/outdoor + microclimate>, <recent stressors>

### Watering
- Check: <cadence + trigger observation>
- Done condition: <what "watered correctly" looks like>

### Fertilizing
- Status: <feed | reduced | paused> because <reason>
- Check: <cadence + what to confirm before feeding>

### Wire-removal inspections (if wired)
- Branch <id>: first inspect <date>, then every <cadence>; remove when <bite-in sign>.

### Notes / uncertainty
- <climate assumption, missing data, provisional species id>
```

Then hand the watering/fertilizer/wire lines to the **Calendar-Ready Reminder Format** in `collection-records-and-care.md`. Create live calendar events only when the user asks and a calendar connector is connected.

## Decision rules

- Never emit a bare "every N days" action unless the user explicitly wants a fixed cadence and accepts it overrides observation.
- State the climate/forecast assumption you used; if you guessed the season or hemisphere, say so.
- Do not give pesticide/treatment schedules here — route pest/health concerns to [`health-diagnostics.md`](health-diagnostics.md) and keep any chemical guidance label-compliant.
- When species is uncertain, pick the slower growth class (safer: more conservative feeding, longer intervals) and flag the assumption.
