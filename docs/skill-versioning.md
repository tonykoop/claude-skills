# Skill Versioning

Every skill in this repo should be treated as a release artifact.

## Required Frontmatter

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

## Release Workflow

1. Edit the skill.
2. Bump `version` in `SKILL.md`.
3. Update `last-updated`.
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

The planned `skills-meta` skill should compare installed skill frontmatter
against `manifest.yaml` and report:

- missing version fields;
- installed version older than canonical;
- canonical skill missing locally;
- local skill not present in the manifest;
- stale `last-updated` dates.

