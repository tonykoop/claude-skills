# Changelog

## 2026-05-10

- Added native **TwinGrid + Partner Peek** round mode to `tmux-sprint` and
  `tmux-v2` (Refs #65). Contract lives at `docs/twingrid/` (README, blind
  and Partner Peek handoff templates, agent-record schema and example,
  partner-peek-record schema, lane-matrix row schema). Manager helpers live
  at `scripts/twingrid/`: `twingrid-lane-matrix.sh` builds the per-round
  A/B matrix; `twingrid-detect-blocked.sh` surfaces panes blocked on
  approval prompts, missing tools, or BLOCKED.txt markers. Agents are
  explicitly told **not** to self-report manager-owned telemetry
  (`elapsed_time`, `context_remaining`, `usage_remaining`,
  `blocked_state`); the lane-matrix script ignores those fields if they
  appear. Bumped `tmux-sprint` and `tmux-v2` to 2.1.0 and updated
  `manifest.yaml` `last_updated`.

## 2026-05-09

- Added `docs/pr-review-gate.md`: sprint-manager PR readiness and issue-closure
  checklists covering documentation-only, script, and skill-content PRs, with a
  portability quick-reference and instrument packet guidance.
- Reconciled release-hygiene docs: README, `docs/public-release-checklist.md`,
  and `docs/skill-versioning.md` now agree that canonical version metadata
  lives in `manifest.yaml`. Documented the `metadata`-nested migration path
  for `SKILL.md` frontmatter that already passes the bundled `skill-creator`
  validator without a validator update.
- Added `docs/release-hygiene-followups.md` as an index of deferred items;
  it defers to PR #32 (manifest drift automation) and PR #37 (packaging /
  release workflow / changelog format) instead of competing with their
  wording.
- Captured verbatim `quick_validate.py` evidence in the follow-ups doc so
  the manifest-as-canonical decision is auditable.
- Bumped `manifest.yaml` `last_updated` to 2026-05-09.
- Added strict manifest drift checks to `skills-meta`, including changelog-gap
  detection and fixture smoke coverage.
- Documented sprint-manager and CI commands for manifest/frontmatter drift
  checks.

## 2026-05-08

- Renamed the local repository from `agent-orchestration` toward
  `claude-skills`.
- Added canonical skill manifest and skill ecosystem docs.
- Began tracking skill versioning, controls, benchmarks, and public-release
  readiness as first-class GitHub issues.
