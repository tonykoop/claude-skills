# Empirical learning loop

The skill gets smarter as you build. Every time you measure a finished
part against its `validation.csv` target, you're producing data the
skill can use to bias the next packet's predictions.

This is the read-write side of the catalog. The build packet is what
the skill *predicts*; the measurement record is what *actually
happened*; the corrections store is the bridge.

## What the loop captures

Three things, kept generic so the loop applies to *any* fabricated
project — wood sign, sewn bag, 3D-printed bracket, plasma-cut steel:

1. **Dimensional deltas** — target vs measured, per-dimension. Length,
   width, depth, hole position, angle.
2. **Time deltas** — predicted shop time vs actual shop time per op.
3. **Cost deltas** — BOM-predicted cost vs actual paid cost per item.

The skill never tries to learn acoustic physics or material-science
constants from these. It learns *your* shop's biases — your CNC tends
to undercut Y by 0.005 in, your laser tends to over-burn engrave
depth by 10%, your time estimates for finishing are consistently 2x
too low. That's enough to materially improve the next packet.

## Where the data lives

```
spaces/<slug>/
├── profile.yaml
└── corrections/
    ├── corrections.sqlite        # rolled-up corrections store
    └── raw-measurements.jsonl    # append-only log of every measurement
```

```
<project-slug>/
├── design.md
├── validation.csv               # the targets
└── measurements.csv             # the actuals (one row per validation row)
```

`measurements.csv` is parallel to `validation.csv` — same `check_id`
column, plus columns for the actual measured value, who measured,
when, and notes.

## Recording a measurement

```bash
python3 scripts/record_measurement.py \
    --packet ./projects/cnc-welcome-sign \
    --space maker-nexus \
    --check-id v002 \
    --measured 0.118 \
    --notes "depth gauge across deepest letter"
```

What this does:

1. Updates `<packet>/measurements.csv` with the new row (creates the
   file if missing, mirroring `validation.csv`'s schema).
2. Appends a normalized event to
   `spaces/<slug>/corrections/raw-measurements.jsonl`.
3. Recomputes the rolling correction for that op/tool/material trio
   and updates `corrections.sqlite`.

When the next packet generation references the same op/tool/material,
the skill reads the correction and surfaces it — *not* as a silent
override of dimensions, but as advice the orchestrator can apply or
ignore:

> Heads-up: across the last 5 measured V-carve jobs at Maker Nexus,
> actual depth ran 0.005 in shallower than nominal. If you want
> 0.125 in finished depth, set the toolpath to 0.130 in. (Or ignore
> this — recent 3 of 5 jobs are within ±0.002.)

## Correction granularity

A correction is keyed by `(space, tool_id, material_id, op_kind,
dimension_axis)`. So:

- `(maker-nexus, cnc-area, baltic-birch-quarter, v-carve, depth)`
- `(maker-nexus, cnc-area, hardwood-walnut, profile-cut, x)`
- `(home-shop-default, bandsaw, *, freehand-curve, length)`

Granular enough to be useful, coarse enough to accumulate sample
size. The schema is in `references/catalog-database.md`.

## When the skill applies a correction

The orchestrator reads corrections at packet generation time and
surfaces them in `design.md` and `op-sequence.md` — but never
silently. The maker should always see:

- The raw target (from the parametric design).
- The applied correction (if any) and its sample size.
- The corrected target as advisory.

If sample size is < 3, the correction is shown with a note that the
sample is too small to be reliable yet. If sample size is ≥ 5 and
stddev is tight, the skill recommends applying it. If the correction
disagrees with the design intent (e.g., a critical fit), the skill
flags the conflict instead of silently applying.

## Privacy

Measurements are tied to a `(space, project)` pair. They never leave
the local repo unless the user pushes them. If `spaces/<slug>` is
marked `visibility: private`, the corrections table is private too.

For aggregate insights across multiple shops (e.g., "do baltic birch
V-carve jobs run shallow at every shop, not just Maker Nexus?"), the
user can opt-in by running:

```bash
python3 scripts/build_catalog_db.py --include-corrections \
    --output ./catalog.sqlite
```

…and choose to share the resulting db. The default is local-only.

## Background consolidation — the "dreaming" job

If the host environment supports scheduled background tasks (Cowork's
`schedule` skill, cron locally, any task runner), the loop runs
nightly via `scripts/dream.py`. This is the makerspace skill's
analog of overnight memory consolidation: raw events accumulate
during the day; the dreaming job rolls them up into the form the
skill consults during the next session.

```bash
python3 scripts/dream.py
# or, more conservatively
python3 scripts/dream.py --space maker-nexus --no-top-level
```

What it does, every run:

1. Rebuilds the catalog SQLite database from current YAML profiles +
   project packets + raw measurement logs.
2. Recomputes rolling corrections (delta means, stddevs, sample
   sizes per (space, tool, material, op_kind, dimension_axis)).
3. Per shop, writes `spaces/<slug>/corrections/summary.md` with:
   - Top 20 biases by absolute mean delta
   - Newly-stable corrections that crossed 3/5/10/20-sample
     thresholds since the previous run
   - Recommendations of which biases are stable enough to apply
4. Writes `dream-log.md` at the skill root — a one-page morning
   briefing across all shops.

Idempotent and side-effect-free if there's no new data. A missed
run isn't a problem; running too often costs only the rebuild
time. Corrections never accumulate stale state because every run
re-derives from the raw measurement log.

Wire it up in Cowork:

> Schedule `scripts/dream.py` to run nightly at 3am. The job is
> idempotent and produces files the next session will read.

## What this isn't

- It isn't a replacement for shop calibration. If your tablesaw blade
  is wandering, fix the blade — don't compensate in the design.
- It isn't an excuse to skip drawings. The corrections feed back into
  the *prediction* side; drawings still need to specify the design
  intent, not the corrected target.
- It isn't a substitute for `validation.csv`. `validation.csv` is per
  project; corrections are per shop. Both stay.

## Walkthrough — a complete loop

1. Generate a Tier 2 packet for the welcome sign. Skill writes
   `validation.csv` with 7 acceptance checks. Predicted depth = 0.125.
2. You build it. After CNC, depth-gauge across the deepest letter
   reads 0.118.
3. Run `record_measurement.py --check-id v002 --measured 0.118`. The
   measurement gets logged; corrections table sees a -0.007 delta on
   `(maker-nexus, cnc-area, baltic-birch-quarter, v-carve, depth)`.
4. Months later you generate another V-carve packet. Skill notices
   the correction (now backed by 4 jobs, mean -0.006 ± 0.002) and
   the new packet's `op-sequence.md` includes a "shop-corrected"
   advice line: "Set the toolpath to 0.131 in to land at 0.125."
5. You build it; depth gauge reads 0.124. Record again. The
   correction stays useful or gets refined.

The maker isn't asking the skill to be a CAM software. They're asking
it to remember what their shop actually does, so they don't have to.
