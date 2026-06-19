# Stale Branch Audit — Instrument Repos

**Issue:** [claude-skills#192](https://github.com/tonykoop/claude-skills/issues/192)  
**Audited:** 2026-06-19  
**Scope:** All public instrument repos + `instrument-showcase`. Private repos
(`zephyr-zither`, `bell-stack-chord-horn`, `cryptex`) were not accessible via
the audit token and must be reviewed separately.

---

## Summary table

| Repo | Branch | Ahead | Behind | Status | Action |
|------|--------|------:|-------:|--------|--------|
| `siku-zampona` | `r26/explorer-html` | 2 | 14 | Unique work, no PR | **Review & file PR or delete** |
| `xiao` | `r26/explorer-html` | 1 | 10 | Unique work, no PR | **Review & file PR or delete** |
| `instrument-showcase` | `chore/publish-sh-wsl-22` | 1 | 0 | Open PR #34 | No action — PR in flight |
| `instrument-showcase` | `feat/explorer-template-v2-quality` | 1 | 0 | Open PR #35 | No action — PR in flight |
| `duduk` | `sprint/r4-songbook-wind-batch1` | 0 | 13 | Superseded | **Safe to delete** |
| `xiao` | `sprint/r4-songbook-wind-batch1` | 0 | 10 | Superseded | **Safe to delete** |
| `instrument-showcase` | `greta/r1-catalog-pilot` | 0 | 14 | Superseded | **Safe to delete** |
| `instrument-showcase` | `r35a/instrument-showcase-issue-3` | 0 | 54 | Superseded | **Safe to delete** |
| `xiao` | `gemshorn` | — | — | 404 (already gone) | No action |

---

## Superseded branches — safe to delete

These branches have **zero commits ahead of `main`**: every change they contained
is already merged. Deleting them carries no risk of data loss.

```bash
# duduk
gh api -X DELETE repos/tonykoop/duduk/git/refs/heads/sprint/r4-songbook-wind-batch1

# xiao
gh api -X DELETE repos/tonykoop/xiao/git/refs/heads/sprint/r4-songbook-wind-batch1

# instrument-showcase
gh api -X DELETE repos/tonykoop/instrument-showcase/git/refs/heads/greta/r1-catalog-pilot
gh api -X DELETE repos/tonykoop/instrument-showcase/git/refs/heads/r35a/instrument-showcase-issue-3
```

---

## Unique-work branches — need human review

### `siku-zampona/r26/explorer-html` (2 ahead, 14 behind main)

Two commits not in `main`:
1. `Add generated studio explorer`
2. `Tighten explorer overview scope`

Primary changed file: `explorer.html`

This branch diverged during the `r26` sprint wave. The work is not redundant
with anything in `main`; deleting it would discard `explorer.html` content
that was never merged. Options:

- Open a PR targeting `siku-zampona/main` to land the work, then delete the
  branch after merge.
- Cherry-pick the two commits onto a current branch if the explorer concept
  has moved to `instrument-showcase`.
- Delete after confirming the `explorer.html` content is superseded by a
  newer implementation (e.g. `feat/explorer-template-v2-quality` in
  `instrument-showcase` PR #35).

### `xiao/r26/explorer-html` (1 ahead, 10 behind main)

One unique commit. Likely related to the same `r26/explorer-html` wave as
the `siku-zampona` branch above. Same review guidance applies.

---

## In-flight branches — no action

`instrument-showcase` has two branches with open PRs:

| Branch | PR | Refs |
|--------|----|------|
| `chore/publish-sh-wsl-22` | [#34](https://github.com/tonykoop/instrument-showcase/pull/34) | Issue #22 |
| `feat/explorer-template-v2-quality` | [#35](https://github.com/tonykoop/instrument-showcase/pull/35) | Issue #31 |

These are 1 commit ahead and 0 behind — they sit cleanly on top of `main` and
will delete automatically on merge.

---

## Private repos — audit required separately

The following repos returned HTTP 404 for branch enumeration, likely because
the current `GITHUB_TOKEN` does not have `repo` scope for private repos:

- `tonykoop/zephyr-zither`
- `tonykoop/bell-stack-chord-horn`
- `tonykoop/cryptex`

Run the audit from a token with private repo read access:

```bash
for repo in zephyr-zither bell-stack-chord-horn cryptex; do
  echo "=== $repo ==="
  gh api "repos/tonykoop/$repo/branches" --jq \
    '.[] | select(.name != "main") | .name' 2>&1
done
```

---

## Quick-delete checklist

- [ ] Delete `duduk/sprint/r4-songbook-wind-batch1`
- [ ] Delete `xiao/sprint/r4-songbook-wind-batch1`
- [ ] Delete `instrument-showcase/greta/r1-catalog-pilot`
- [ ] Delete `instrument-showcase/r35a/instrument-showcase-issue-3`
- [ ] Review `siku-zampona/r26/explorer-html` (open PR or confirm superseded)
- [ ] Review `xiao/r26/explorer-html` (open PR or confirm superseded)
- [ ] Merge or close `instrument-showcase` PR #34 (`chore/publish-sh-wsl-22`)
- [ ] Merge or close `instrument-showcase` PR #35 (`feat/explorer-template-v2-quality`)
- [ ] Audit private repos (`zephyr-zither`, `bell-stack-chord-horn`, `cryptex`)
