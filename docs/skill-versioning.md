# Skill Versioning

Every skill in this repo should be treated as a release artifact.

## Target Metadata

```yaml
---
name: skill-name
version: 1.0.0
last-updated: 2026-05-08
description: ...
---
```

`name` and `description` remain the trigger-critical fields. `version` and
`last-updated` make drift detectable across desktop, mobile, Claude, Codex, and
other runtimes.

Compatibility note: the current bundled `skill-creator` validator accepts only
`name` and `description` in `SKILL.md` frontmatter. Until that validator is
updated, portable reviewed skills may keep only validator-compatible frontmatter
and store canonical `version` / `last_updated` in `manifest.yaml`.

Portable skills under `skills/` may use `runtime: portable` in
`manifest.yaml` so one canonical entry can cover Claude, Codex, Gemini, and
desktop installs.

## Release Workflow

1. Edit the skill.
2. Bump `version` in `SKILL.md` or `manifest.yaml`, depending on the active
   validator convention.
3. Update `last-updated` / `last_updated`.
4. Add a per-skill changelog entry.
5. Update `manifest.yaml`.
6. Commit.
7. Tag with `<skill-name>/v<X.Y.Z>`.
8. Build the zip from the tagged commit.
9. Upload or install the tagged artifact.

## Semver Defaults

- Patch: trigger wording, clarifications, small bug fixes.
- Minor: additive modes, new bundled resources, new runtime support.
- Major: breaking schema, output, installation, or workflow changes.

## Drift Checks

The `skills-meta` helper compares installed skill frontmatter against
`manifest.yaml` and reports:

- missing version fields;
- installed version older than canonical;
- canonical skill missing locally;
- local skill not present in the manifest;
- stale `last-updated` dates;
- missing per-skill changelog coverage.

Use strict mode when a sprint manager or CI job should fail on drift:

```bash
python3 skills/skills-meta/scripts/skills-meta.py --mode drift --strict
```

See [Manifest Drift Checks](manifest-drift-checks.md) for fixture smoke tests
and limitations.
