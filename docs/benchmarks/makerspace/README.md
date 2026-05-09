# Makerspace v0.2 benchmark workspace

Legacy benchmark artifacts moved out of the runtime skill package on
2026-05-08 to keep `skills/makerspace/` lean for mobile zip-upload and
cross-platform installs.

## Contents

- `iteration-1/`, `iteration-2/` — per-eval `with_skill/` and
  `without_skill/` outputs, `eval_metadata.json`, `grading.json`,
  `timing.json`, plus the `benchmark.json` and rendered `eval-viewer.html`
  for each iteration.
- `aggregate_benchmark.py`, `grade_iteration.py` — helper scripts captured
  alongside the workspace for reproducibility.

## Provenance

- Source: `skills/makerspace/evals/workspace/` in this repo prior to the
  2026-05-08 cross-platform-review handoff.
- Mirror: `tonykoop/makerspace/evals/workspace/` in the standalone repo
  (kept in sync until the next release cut).

## Why it lives here

The runtime skill never reads this directory. Bundling it would have made
the portable skill package ~10× larger than its actual runtime footprint
and pushed mobile zip-upload installs over comfortable limits.

To rerun a benchmark, point `aggregate_benchmark.py` at a fresh
`iteration-N/` directory created next to these.
