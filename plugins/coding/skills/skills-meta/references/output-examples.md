# Output Examples

Keep outputs short enough to read on a phone.

## Inventory

```text
skills-meta inventory
roots scanned: 3
skills found: 9

ok      tmux-v2           v2.0.0  2026-05-08  codex/skills/tmux-v2/SKILL.md
drift   skills-meta       v1.0.0  2026-05-07  skills/skills-meta/SKILL.md
planned makerspace        v0.1.0  2026-05-08  skills/makerspace/SKILL.md

missing makerspace        canonical 1.0.0 not found locally
```

## Single skill

```text
skills-meta --skill tmux-v2
installed: v2.0.0
canonical:  v2.0.0
last-updated: 2026-05-08
status: ok
```

## Drift

```text
drift check
3 issues

- tmux-v2: version ok, last-updated stale
- skills-meta: manifest says active, local file missing version
- reverse-engineer: local install not in manifest.skills
```

## Frontmatter fix

```text
Suggested frontmatter
---
name: skills-meta
version: 1.0.0
last-updated: 2026-05-08
description: Audit installed skills, compare frontmatter to manifest.yaml, and report version drift or missing metadata.
---
```
