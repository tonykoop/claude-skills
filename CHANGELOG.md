# Changelog

## 2026-05-09

- Added `docs/pr-review-gate.md`: sprint-manager PR readiness and issue-closure
  checklists covering documentation-only, script, and skill-content PRs, with a
  portability quick-reference and instrument packet guidance.
- Reconciled release-hygiene docs: README, `docs/public-release-checklist.md`,
  and `docs/skill-versioning.md` now agree that canonical version metadata
  lives in `manifest.yaml` until the bundled `skill-creator` validator
  accepts `version` / `last-updated` in `SKILL.md` frontmatter.
- Added `docs/release-hygiene-followups.md` to track deferred items
  (per-skill changelogs, tagging, packaging, sync workflow, frontmatter
  mirror).
- Bumped `manifest.yaml` `last_updated` to 2026-05-09.

## 2026-05-08

- Renamed the local repository from `agent-orchestration` toward
  `claude-skills`.
- Added canonical skill manifest and skill ecosystem docs.
- Began tracking skill versioning, controls, benchmarks, and public-release
  readiness as first-class GitHub issues.

