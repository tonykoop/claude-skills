# DoE integration

## Table of contents

- When to run a DoE
- Anatomy of a DoE study
- File layout
- Protocol YAML
- Data CSV
- Recording responses
- Summarizing findings
- Feeding findings back into the catalog and correction loop

A *Design of Experiments* (DoE) is a structured way to figure out
how a process responds to its inputs without burning a giant pile
of stock. The skill ships a small DoE harness that fits inside a
build packet — define the study, run the cells, record the
responses, and the catalog DB rolls up the results.

## When to run a DoE

- You're dialing in feeds and speeds for a new bit + material combo
  on the CNC.
- You're calibrating laser power × speed × passes for a tricky
  acrylic.
- You're testing 3 dye concentrations × 2 fabric weights × 3 wash
  cycles to see what survives.
- You're varying glaze formulations across a kiln load.

If you're tweaking one knob at a time, DoE is overkill. If you're
varying two or more knobs and care about the interaction, DoE is
worth the structure.

## Anatomy of a DoE study

A study has:

- **Factors** — the knobs you're turning. Usually 2 or 3.
- **Levels** — the values each factor takes. Typically 2 or 3 levels
  per factor.
- **Replicates** — how many times each cell runs. ≥ 2 lets you
  estimate within-cell variance.
- **Response variable** — the thing you're measuring. Cut quality,
  finish smoothness, dimensional accuracy, time, cost, etc. Pick
  one main response; track secondary ones in `notes`.
- **Run order** — randomized to avoid drift confounding factors.

For most maker projects, a **2-factor 3-level full factorial** with
2 replicates is plenty: 3 × 3 × 2 = 18 runs.

## File layout

A DoE study lives inside the build packet that motivated it:

```
<project-slug>/
├── doe/
│   ├── study-01-protocol.yaml      # plan
│   ├── study-01-data.csv           # observations (one row per run)
│   ├── study-01-analysis.md        # write-up + plots
│   └── study-01-images/            # photos of each cell's output
```

A project can have multiple studies (`study-02-*`, etc.) if you're
running them sequentially.

## Protocol — `study-01-protocol.yaml`

```yaml
study_id: 1
project_slug: cnc-welcome-sign
title: V-carve depth calibration on baltic birch
date_planned: 2026-05-15
hypothesis: |
  V-carve depth is sensitive to feed rate and bit RPM. We expect
  measured depth to be within ±0.005 in of nominal across the
  factor space, but want to verify before committing to a
  customer order.
factors:
  - name: feed_rate_ipm
    levels: [60, 80, 100]
    unit: ipm
  - name: spindle_rpm
    levels: [16000, 20000, 24000]
    unit: rpm
replicates: 2
randomize: true
response_variable:
  name: measured_depth_delta
  unit: in
  measurement_method: depth gauge across deepest point of cell
secondary_responses:
  - name: edge_finish_score
    scale: 1-5 (5 = best)
  - name: cycle_time
    unit: seconds
materials:
  - id: baltic-birch-quarter
    qty: 1
    notes: 12 × 12 test panel divided into 18 cells
tools:
  - id: cnc-area
    space: maker-nexus
total_estimated_runtime_min: 90
analysis_plan: |
  Compute mean delta per cell. Flag cells whose mean delta is
  outside ±0.005. Look for monotone trends in feed_rate or
  spindle_rpm. ANOVA optional; visual inspection is usually
  enough at this scale.
```

## Data — `study-01-data.csv`

```
run_id,run_order,feed_rate_ipm,spindle_rpm,replicate,measured_depth_delta_in,edge_finish_score,cycle_time_s,notes
1,7,60,16000,1,-0.003,4,42,
2,2,60,16000,2,-0.004,4,42,
3,12,60,20000,1,-0.001,5,32,
...
```

`run_order` is the order you actually performed the runs (post
randomization). `run_id` is the canonical identifier for the
factor combination.

## Recording the data

The script `scripts/record_doe_results.py` has two modes:

```bash
# Initialize the data CSV from the protocol (writes the header
# and one row per planned run with response columns blank)
python3 scripts/record_doe_results.py \
    --packet ./projects/cnc-welcome-sign \
    --study 1 \
    --init

# Append/update a run as you complete it
python3 scripts/record_doe_results.py \
    --packet ./projects/cnc-welcome-sign \
    --study 1 \
    --run-id 1 \
    --response measured_depth_delta_in=-0.003,edge_finish_score=4,cycle_time_s=42 \
    --notes "first cell, slight fuzzing on grain"
```

The script writes to the data CSV and emits a normalized event
into the space's `corrections/raw-measurements.jsonl` so that
DoE responses feed into the same correction store as ad-hoc
measurements.

## Analysis — `study-01-analysis.md`

Free-form. Common sections:

- Headline finding ("100 IPM at 24k RPM produced uniform depth
  within ±0.001 across replicates; lower RPMs introduced bias").
- Per-cell mean and stddev table.
- Plot placeholder (drop a screenshot into
  `study-01-images/results.png`).
- Recommended setting for the project this study served.
- Open questions for follow-up.

## Catalog integration

The catalog DB has `doe_studies` and `doe_runs` tables. Running
`scripts/build_catalog_db.py` (with the data CSV present) populates
both. The skill can then query:

```sql
-- Across all studies, which feed/RPM combinations gave the
-- tightest depth control on baltic birch?
SELECT s.title, r.factor_a_value, r.factor_b_value,
       AVG(r.response_value) AS mean_response
FROM doe_runs r JOIN doe_studies s ON r.study_id = s.id
WHERE s.title LIKE '%baltic birch%'
GROUP BY r.factor_a_value, r.factor_b_value
ORDER BY ABS(mean_response) ASC;
```

## When *not* to run a DoE

- For a one-off project where you don't care about repeatability.
- When you can't measure the response objectively. ("Looks pretty"
  isn't a response variable.)
- When the factor levels would damage equipment or violate shop
  safety policy.
- When you don't have the stock to spend on calibration. Run a
  smaller pilot first.

## Limits

- The harness is light by design — no built-in ANOVA, no factorial
  optimization. Real DoE software exists (Minitab, JMP, R's
  `DoE.base`); use it if you need it. The harness here keeps the
  protocol and data structured enough that exporting to those
  tools is one CSV away.
- The protocol assumes ≤ 3 factors. For higher-order designs,
  hand-author the protocol and adapt the data CSV — the analysis
  script doesn't care about column count.
