# Public Release Readiness Sweep - 2026-06-13

This sweep records the release-readiness checks added for issues #8 and #10.
It does not flip the repo public; it keeps the repo private-first until the
remaining public-path findings are either generalized or documented as
intentional provenance.

## Scope Reviewed

- README and repo docs policy surfaces.
- `manifest.yaml` skill entries and manifest-owned `SKILL.md` frontmatter.
- `plugins/coding/skills/skills-meta/` docs, references, helper, tests, and
  agent metadata.
- Commands, hooks, scripts, and packaged skill trees by regex scan for obvious
  secret/private-path terms.

## Evidence

- `qmd status` succeeded; `qmd query` crashed in Bun after loading the local
  reranker path, so local file and GitHub issue evidence were used after the
  qmd gate attempt.
- Manifest-owned skill frontmatter check: 24 `manifest.skills[*].repo_path`
  entries have top-level `version` and `last-updated`.
- `python3 plugins/coding/skills/skills-meta/tests/test_skills_meta.py`: 24
  tests passed.
- `skills-meta --mode controls --skill skills-meta --strict`: 0 controls
  issues for `skills-meta`.
- Secret-pattern scan found references to environment variable names and
  policy text, not literal checked-in credential values.

## Remaining Public Gates

- Full-repo `skills-meta --mode controls` currently reports personal path
  findings in several project-specific skill bodies and installed duplicate
  roots. Those must be generalized or explicitly documented as private
  provenance before a public release.
- Existing manifest install roots intentionally contain Tony-specific local
  paths. They are useful for private sync, but public distribution should move
  them to examples or local config.
- A broad all-`SKILL.md` scan still sees intentional non-shipped exceptions:
  failing test fixtures and a duplicate `houseplant-workspace` snapshot outside
  the manifest-owned release surface.
