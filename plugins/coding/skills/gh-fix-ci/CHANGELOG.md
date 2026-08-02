# Changelog — gh-fix-ci

## v0.3.0 — 2026-08-02

- Consolidated the active implementation in the coding plugin and retired the
  standalone Codex variant.

## v0.2.0 — 2026-06-19 (structured evals)

Added `evals/evals.json` (4 evals):

- **eval 1** `inspect-and-fix-failing-pytest`: full auth→inspect→plan→approve→
  implement→recheck flow using inspect_pr_checks.py; drafts plan before editing.
- **eval 2** `external-ci-provider-scoping`: Buildkite check → label external,
  report detailsUrl only, do not drive non-GitHub-Actions providers.
- **eval 3** `no-logs-missing-run-id`: all fallbacks exhausted → report
  "Missing logs" explicitly rather than inventing content; no hallucination.
- **eval 4** `json-output-for-automation`: --json flag invocation, validates
  non-zero exit on remaining failures; no fixes or PRs opened.

## v0.1.0 — 2026-06-15

- Initial Claude-usable port of the Codex-only `codex/skills/gh-fix-ci` into
  the `coding` plugin (consolidation: no loose skills).
- Added `scripts/inspect_pr_checks.py` — the script the original SKILL.md
  referenced but never shipped. Resolves failing GitHub Actions checks for a
  PR, pulls run logs, extracts a failure snippet, scopes out external providers
  (reports URL only), and exits non-zero when failures remain.
- Added `references/codex-variant.md` noting the Codex CLI copy and the single
  behavioral difference (plan-drafting step).
