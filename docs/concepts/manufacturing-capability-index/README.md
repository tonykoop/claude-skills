# Manufacturing Capability Index + Planetary Element Inventory

First concrete artifact for [claude-skills#205](https://github.com/tonykoop/claude-skills/issues/205)
(capture, epic-adjacent to Koop's Law, [#204](https://github.com/tonykoop/claude-skills/issues/204)).

The issue's `Next step` is: *"Sketch the index schema (per-process capability row
+ per-element abundance/run-rate row) and identify which fields a MakerBench seed
could actually gate on today."* This directory is that sketch, made executable:
two JSON Schemas, sample rows, and a stdlib validator that also runs the
scarcity triage the index exists to enable.

## Why this index exists

An AI hardware-design agent, left alone, picks the *best material in a vacuum*.
This index makes it pick **resource-aware**: it queries the index before
committing geometry, so "coat it in gold for EMI shielding" is rejected and an
abundant-atom substitute (copper, aluminium) is forced *before* the design ever
reaches the physical grader. It is also the empirical substrate Koop's Law
(`C = k·S_e^α`, #204) fits its curve against — the index is the moving capability
boundary; Koop's Law is the rate at which that boundary moves.

## The two row types

### 1. Process capability row — what we can build

One row per manufacturing process, time-stamped (`as_of`) because capability is a
moving boundary. Schema: [`schema/process_capability_row.schema.json`](schema/process_capability_row.schema.json).

| Field | Meaning | Example (CNC wood milling, 2026-Q3) |
|---|---|---|
| `min_feature_mm` | spatial floor — smallest reliable feature | 1.5 |
| `max_envelope_mm` | spatial ceiling — work volume `{x,y,z}` | 1200×1200×150 |
| `kinematic_cadence` | speed before deflection/warp | feed 3000 mm/min |
| `energetic_threshold_j_per_cm3` | energy to alter/remove a unit volume | 30 |
| `tolerance_floor_mm` | σ-capability — tightest held tolerance | ±0.05 |
| `states_of_matter` | states the process manipulates | `["solid"]` |

This is exactly the lookup the issue describes: *"Give me Q3-2026 limits for CNC
wood milling" → "min bit radius 1.5 mm, feed 3000 mm/min, ±0.05 mm"*.

### 2. Element inventory row — what the planet has

One row per element. Schema: [`schema/element_inventory_row.schema.json`](schema/element_inventory_row.schema.json).

| Field | Meaning |
|---|---|
| `crustal_abundance_ppm` | A_c — average crustal abundance |
| `annual_run_rate_tonnes` | global production/run-rate |
| `scarcity_penalty` | 0..1 triage weight (derived from abundance if omitted) |
| `abundant_substitutes` | abundant-atom alternatives for the common use |

## The scarcity gate

`scarcity_penalty` is a log-scale map of crustal abundance to `0..1` (abundant →
0, vanishingly scarce → 1). A penalty at or above the gate (default `0.70`)
rejects the material and surfaces substitutes. On the sample data:

```
Au penalty 0.925 >= gate 0.7: reject, prefer Cu, Al
Al penalty 0.011 < gate 0.7: allowed
Fe penalty 0.031 < gate 0.7: allowed
Nd penalty 0.423 < gate 0.7: allowed
```

## Which fields a MakerBench seed can gate on TODAY

This is the second half of the acceptance — the honest scoping of what is
enforceable now versus aspirational:

**Gateable today** (static, vendor-published or measurable, so a seed challenge
can enforce them against a real grader immediately):

- process: `min_feature_mm`, `max_envelope_mm`, `tolerance_floor_mm`, `states_of_matter`
- element: `crustal_abundance_ppm`, `scarcity_penalty`, `abundant_substitutes`

**Aspirational** (need live telemetry or under-load measurement we do not yet
have — keep in the schema, do not gate on them yet):

- process: `kinematic_cadence` (speed *before deflection* is load-dependent),
  `energetic_threshold_j_per_cm3`
- element: `annual_run_rate_tonnes` (needs a live data feed; the WRFCoin
  extraction-siting source is forthcoming)

So a MakerBench seed today can reject a design for (a) a feature below a
process's `min_feature_mm`, (b) a part exceeding `max_envelope_mm`, (c) a
tolerance tighter than `tolerance_floor_mm`, or (d) a scarce material above the
scarcity gate — all four are enforceable now.

## Run it

```bash
python3 validate.py            # validate bundled rows + print the triage + gate report
python3 -m pytest test_mci.py -q
```

The validator is stdlib-only (a small draft-07 subset), so it adds no
dependency. `validate.py` exits non-zero if any row violates its schema.

## Status & scope

This is a `capture`/exploratory first artifact, intentionally lightweight per the
issue. The numbers in `data/` are order-of-magnitude (USGS-class) seeds to make
the gate runnable, not a curated dataset. The natural long-term home is
`makerbench-hwe`; it lives here now as the schema sketch + working gate so the
idea is concrete and testable before it is promoted.
