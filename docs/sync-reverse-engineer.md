# Sync: `reverse-engineer` portable ↔ standalone repo

The same skill ships in two places:

| Location | Path | Role |
| --- | --- | --- |
| Portable (this repo) | `skills/reverse-engineer/` | **Canonical source.** Where edits land first. |
| Standalone | `tonykoop/reverse-engineering` → `skills/v1/reverse-engineer/` | Mirror, plus a `CHANGELOG.md` that doesn't exist in the portable copy. |

## Why two copies

The standalone repo predates the portable monorepo. Keeping a mirror in the standalone repo means people who only know about `tonykoop/reverse-engineering` still get a current skill, and the standalone repo can publish its own release notes (`CHANGELOG.md`).

## The rule

**Edit `skills/reverse-engineer/` here first.** Treat the standalone copy as read-only output of a sync.

The only file the standalone copy is allowed to maintain on its own is `CHANGELOG.md`. Everything else — `SKILL.md`, `references/*`, `agents/*`, `evals/*` — gets overwritten on each sync.

## Sync script

Run from the standalone repo:

```bash
# inside tonykoop/reverse-engineering
./scripts/sync-from-claude-skills.sh /path/to/claude-skills
```

The script (committed in the standalone repo, not here) does:

```bash
SRC="$1/skills/reverse-engineer"
DST="skills/v1/reverse-engineer"
rsync -a --delete --exclude=CHANGELOG.md "$SRC/" "$DST/"
```

After running it, review the diff, add a `CHANGELOG.md` entry describing the sync, and commit on a branch named `sync/reverse-engineer-YYYY-MM-DD`.

## Verifying the two copies are in sync

From either repo:

```bash
diff -r \
  /path/to/claude-skills/skills/reverse-engineer \
  /path/to/reverse-engineering/skills/v1/reverse-engineer
```

The only expected difference is `Only in .../v1/reverse-engineer: CHANGELOG.md`.

## When to sync

- Any time `skills/reverse-engineer/` changes here.
- Before tagging a release in either repo.
- After a cross-platform review handoff (this PR is the first such handoff).
