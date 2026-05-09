# Manifest Drift Checks

`skills-meta` audits the checked-out skill tree against `manifest.yaml`.

## Sprint manager command

Run this from the repo root before packaging, tagging, or merging a skill
change:

```bash
python3 skills/skills-meta/scripts/skills-meta.py --mode drift --strict
```

The command exits with status `1` when it finds any tracked skill with missing
`version` or `last-updated` frontmatter, missing per-skill changelog coverage,
local skills absent from `manifest.skills`, or manifest entries whose
`repo_path` does not exist locally.

Use inventory mode when you want a readable full list without failing the
calling shell:

```bash
python3 skills/skills-meta/scripts/skills-meta.py --mode inventory
```

## CI smoke commands

The fixtures demonstrate both expected outcomes:

```bash
cd tests/fixtures/manifest-drift/pass
python3 ../../../../skills/skills-meta/scripts/skills-meta.py --mode drift --strict
```

```bash
cd tests/fixtures/manifest-drift/fail
python3 ../../../../skills/skills-meta/scripts/skills-meta.py --mode drift --strict
```

The first command should pass. The second should fail and print missing
frontmatter, a missing changelog, stale changelog coverage, an untracked local
skill, and a manifest skill missing locally.

## Limits

The helper treats `manifest.yaml` as canonical and only reports drift. It does
not rewrite skill files, create changelogs, delete unknown local skills, or infer
metadata from release tags.
