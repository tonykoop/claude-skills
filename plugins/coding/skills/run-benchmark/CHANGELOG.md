# Changelog — run-benchmark

## 0.2.0 — 2026-06-19 (eval suite)

Adds the first machine-runnable eval suite (5 evals) covering the skill's
verify-don't-trust behavioral contracts.

### Added

- `evals/evals.json` — 5 evals:
  1. `orient-before-run` — Phase 0 orientation executes before the harness is
     touched; concrete map written from the benchmark's own docs.
  2. `canary-preserved-verbatim` — contamination canary preserved as-is in the
     bundle; missing canary flagged before submission.
  3. `no-answer-key-leak` — oracle/gold files refused; failure described from
     public metadata only.
  4. `infra-error-honest-reporting` — timed-out rows marked errored using the
     benchmark's own error sentinel; not laundered into zeros or dropped.
  5. `no-self-verification` — submission PR opens at default unverified state;
     maintainer attestation is the only path to verified status.

### Changed

- `SKILL.md` — bumped to v0.2.0 (`last-updated: 2026-06-19`).
- Root `manifest.yaml` — updated `canonical_version` to 0.2.0 and appended
  eval suite note.

## 0.1.0 — 2026-06-13

Initial release.

### Added

- **Five-phase workflow** (`SKILL.md`) for contributing to an AI-agent benchmark
  end-to-end: run the harness, scrutinize/aggregate results, file issues, open
  PRs, and submit/verify leaderboard rows.
- **Phase 0 — Orient**, the portability mechanism: discover the target
  benchmark's contract from its own `AGENTS.md`/`CONTRIBUTING.md`/submission docs
  and detect its harness, instead of hardcoding one benchmark.
- **Verify-don't-trust spine** baked into every phase: no contamination, never
  expose the answer key, reproduce before claiming, honest infra-failure
  reporting, clean public surfaces, no self-verification, no grader patching.
- **`references/makerbench.md`** — worked reference with exact MakerBench-HWE
  commands, paths, public/private boundary, and submission + attestation flow.
- **`references/orienting.md`** — how to fill the Phase-0 map for an unfamiliar
  benchmark from its repo.
- **`references/integrity.md`** — the spine in depth, with the reasoning and the
  failure each rule prevents.
- **`scripts/bundle_preflight.py`** — stdlib-only result-bundle sanity gate
  (canary present, no answer-key/source/absolute/traversal paths, required
  metadata populated, not self-verified). Does not recompute scores. ASCII output
  for cp1252 consoles.
