# Changelog

## v0.3.0 — 2026-06-19

- Add first machine-runnable eval suite (`evals/evals.json`): 4 evals covering
  passing gate (auto-release-eligible), escalate-human-review on ambiguous
  confidence, distinct-model auditor assignment, and dirty-source noted
  (not hidden) in ticket.

## v0.2.0

- Added confidence scoring + circuit-breaker routing
  (`auto_release_eligible` / `escalate_human_review` / `blocked`) so reviewers
  only inspect the ambiguous minority.
- Added `publish-manifest.json` to the bundle: publishing metadata for the
  Studio Pipeline with deploy target and a `sha256`-checksummed artifact index.
- Wired adversarial-QA auditor assignment to the governance `review_router`
  (claude-skills#256): `--creator-agent`/`--creator-model` route the candidate
  to a distinct-model auditor, fail-closed to `blocked` when none exists, and
  skip cleanly when governance modules are absent (stays portable).
- `qa-decision.json` bumped to `schema_version: 2` (adds confidence, routing,
  auditor). Expanded the test suite to cover all new paths.

## v0.1.0

- Added the Studio Release skill for PR/end-of-block release QA handoff.
- Added a headless staging gate that writes `qa-decision.json` and a single
  approve/deploy ticket.
