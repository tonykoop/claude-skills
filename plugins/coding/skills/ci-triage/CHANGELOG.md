# Changelog — ci-triage

## v0.2.0 — 2026-06-19 (eval suite)

Adds the first machine-runnable eval suite (5 evals) covering the skill's
core behavioral contracts: parallel data gathering, minimal trigger phrase
recognition, billing-blocked failure categorization, read-only constraint
enforcement, and report format compliance.

### Added

- `evals/evals.json` — 5 evals:
  1. `parallel-data-gather` — all 5 Step 1 gh commands fire simultaneously in
     one message, not sequentially.
  2. `minimal-trigger-phrase` — "are workflows passing?" resolves to the full
     ci-triage sweep, not a guessed one-liner.
  3. `billing-blocked-detection` — spending-limit annotation → category
     "billing", log fetch skipped, BLOCKED recorded in Summary table.
  4. `read-only-constraint` — mid-triage fix request refused; failure logged
     as P0/P1 action item instead.
  5. `report-format-compliance` — report lands at the prescribed path with all
     8 required sections present; only the path + executive summary go to stdout.

### Changed

- `SKILL.md` — bumped to v0.2.0 (`last-updated: 2026-06-19`).
- Root `manifest.yaml` — added `ci-triage` entry (`canonical_version: 0.2.0`,
  `status: active`).

## v0.1.0 — 2026-05-20 (initial skill)

First version of the read-only CI and Dependabot health-check skill across
all 7 WRFCoin repos. Fires 5 parallel gh commands, categorizes failures as
billing / real / config, and writes a structured markdown report.
