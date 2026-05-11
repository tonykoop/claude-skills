# Manifest Schema

Use the manifest as the canonical drift source, not as a rewrite target.

## Installed skill frontmatter

Required fields:

- `name`
- `version`
- `last-updated`
- `description`

## `manifest.yaml`

Active skill entries use:

- `canonical_version`
- `runtime`
- `repo_path`
- `last_updated`
- `status`
- `notes`

`planned_skills` is supporting context, not canonical inventory. Treat it as a
hint, not as an up-to-date install record.

## Comparison rules

- Missing `version` is drift.
- Missing `last-updated` is drift.
- A local `version` older than `canonical_version` is drift.
- A local `last-updated` older than the manifest `last_updated` is stale.
- A local skill missing from `manifest.skills` is unknown/untracked.
- A manifest skill missing locally is missing from the current install set.
- A manifest skill with `status: deprecated`, `status: obsolete`, or
  `status: retired` is a cleanup candidate when installed. If it is already
  absent, do not count it as missing-local drift.

## Frontmatter fix output

When suggesting a fix, print only the replacement frontmatter block.

```yaml
---
name: example-skill
version: 1.0.0
last-updated: 2026-05-08
description: Short description.
---
```

## Version comparison

Use semver ordering when both sides are parseable.
If a version string is not semver-shaped, report it as unparseable instead of
guessing.
