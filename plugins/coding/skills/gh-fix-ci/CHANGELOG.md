# Changelog — gh-fix-ci

## v0.1.0 — 2026-06-15

- Initial Claude-usable port of the Codex-only `codex/skills/gh-fix-ci` into
  the `coding` plugin (consolidation: no loose skills).
- Added `scripts/inspect_pr_checks.py` — the script the original SKILL.md
  referenced but never shipped. Resolves failing GitHub Actions checks for a
  PR, pulls run logs, extracts a failure snippet, scopes out external providers
  (reports URL only), and exits non-zero when failures remain.
- Added `references/codex-variant.md` noting the Codex CLI copy and the single
  behavioral difference (plan-drafting step).
