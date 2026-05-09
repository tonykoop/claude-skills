# Maker Nexus — DoE: Feeds & Speeds for 1/8" Single-Flute Upcut on 1/2" HDPE

A Design-of-Experiments study to dial in feed rate and depth-per-pass
for a new bit + material combo on the Maker Nexus CNC router
(`cnc-area`). HDPE is on `cnc-area`'s `allowed_materials` list, so the
material policy is satisfied — see `spaces/maker-nexus/profile.yaml` in
the makerspace skill.

## What's in this packet

```
maker-nexus-doe-feeds-speeds/
├── README.md                       # this file
└── doe/
    ├── study-01-protocol.yaml      # plan: factors, levels, replicates, hypothesis
    └── study-01-data.csv           # 18 planned runs, blank response columns
```

When you finish the study, drop these alongside:

```
    ├── study-01-analysis.md        # write-up: per-cell means, recommendation
    └── study-01-images/            # photos of each cell's cut edge
```

## Study at a glance

- **Factors:** `feed_rate_ipm` ∈ {40, 60, 80}, `depth_per_pass_in` ∈ {0.05, 0.10, 0.15}
- **Design:** 3 × 3 full factorial, 2 replicates → **18 runs**
- **Run order:** randomized (column `run_order` in the data CSV)
- **Primary response:** `edge_finish_score` (1–5 visual/tactile scale; see protocol for rubric)
- **Secondary response:** `cycle_time_seconds`
- **Tool:** 1/8" single-flute upcut endmill (member-supplied)
- **Material:** ~12 × 12 panel of 1/2" HDPE, divided into 18 test pockets
- **Estimated runtime:** ~75 min

## How to record results as you run

The makerspace skill ships `scripts/record_doe_results.py`. Run it
from the skill folder (`C:\Users\Tony\Documents\GitHub\makerspace\`)
and point `--packet` at this folder.

### One-time setup (already done if `doe/study-01-data.csv` exists)

If you'd rather have the script regenerate the data CSV (with its
own randomization seed), copy the protocol into your packet folder
and re-init:

```bash
python3 scripts/record_doe_results.py \
    --packet <path-to-this-packet> \
    --study 1 \
    --init \
    --seed 42
```

The hand-authored CSV in `doe/study-01-data.csv` is already
populated with 18 planned runs and a randomized run order — you
can skip `--init` and start recording directly.

### Record a run

Sort the CSV by `run_order`, then walk top-to-bottom. After each cut:

```bash
python3 scripts/record_doe_results.py \
    --packet <path-to-this-packet> \
    --study 1 \
    --run-id 9 \
    --space maker-nexus \
    --response edge_finish_score=4,cycle_time_seconds=38 \
    --notes "60 IPM / 0.10 dop — clean edge, faint tool marks, no melt"
```

`--run-id` is the canonical run identifier (the `run_id` column),
not the order you ran it in. The script also appends a normalized
event to `spaces/maker-nexus/corrections/raw-measurements.jsonl` so
this study's measurements feed the makerspace skill's
empirical-learning loop and show up in the catalog DB
(`doe_studies` / `doe_runs` tables) on the next
`build_catalog_db.py` run.

### When all 18 runs are recorded

Write `doe/study-01-analysis.md`:

- Per-cell mean and stddev of `edge_finish_score`
- Plot of `edge_finish_score` vs `feed_rate_ipm` (one series per `depth_per_pass_in`)
- Headline recommendation (best feed/dop combination for this bit + material)
- Cycle-time tradeoff note
- Open questions / follow-up studies (e.g., add spindle RPM as a third factor)

## Methodology reference

Full schema, file layout, and analysis guidance:
`references/doe-integration.md` in the makerspace skill.

Related references:

- `references/empirical-learning-loop.md` — how DoE responses feed
  back into future packets
- `references/catalog-database.md` — the SQLite tables
  (`doe_studies`, `doe_runs`) that get populated when you run
  `build_catalog_db.py`
- `spaces/maker-nexus/profile.yaml` — confirms HDPE is allowed on
  `cnc-area` and CNC certification is required (`cnc-cert`)

## Safety / shop notes

- HDPE is allowed on Maker Nexus's `cnc-area` (verified in
  `profile.yaml`). Aluminum, ferrous, and brass are banned on this
  CNC — don't substitute test stock.
- HDPE chips are stringy. Run dust collection and clear the bit
  between cells if you see swarf wrapping.
- HDPE creeps under vacuum hold-down; use mechanical clamps or
  hold-downs, not just the vacuum table.
- 1/8" upcut at 0.15" depth-per-pass is at the upper end of what a
  single-flute can comfortably evacuate in 1/2" HDPE. If the bit
  starts squealing or you smell hot plastic, abort that cell and
  record `edge_finish_score=1` with a note.
