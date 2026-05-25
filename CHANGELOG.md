# Changelog

## 2026-05-25

- Added `file-a-patent` (v0.1.0) to the Maker plugin at
  `plugins/maker/skills/file-a-patent/`. The import keeps the attorney-review
  packet workflow, USPTO/source-reference guardrails, packet templates, and
  scaffold script while excluding the standalone repo internals and generated
  zip artifact.
- Bumped the Maker plugin metadata to `1.1.1` and registered
  `file-a-patent` in the marketplace listing and canonical skill manifest.

## 2026-05-22

- Added `source-citations` skill (v0.1.0) at `skills/source-citations/`.
  Installs the keyed bibliography registry (201 entries from the Drive source
  library) and the companion techniques catalog (maker demonstrations with a
  `confirmed`/`unconfirmed` status that hard-gates citation). Per-repo
  `SOURCES.md` / `TECHNIQUES.md` are generated from `.citations.yaml` /
  `.techniques.yaml`; both generators refuse to ship without a maker-written
  `why` for every cited key. Registered in `manifest.yaml`. The pilot
  rollout across the public "done-bar" instrument repos and promotion of
  unconfirmed technique seeds happen on the desktop where those repos live;
  this commit only ships the skill.

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
