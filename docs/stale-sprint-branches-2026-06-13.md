# Stale Sprint Branch Inventory - 2026-06-13

Issue: tonykoop/claude-skills#192

This is a list-only safety pass. No branches were deleted.

## Retrieval And Scope

- `qmd status` succeeded: 2821 indexed markdown files, 13904 embedded vectors,
  15 collections, last updated about 18 hours before this pass.
- `qmd search` in `sprint-docs` for this lane returned no direct hits.
- `qmd query` was attempted for the lane topic, but the Bun-backed local qmd
  runtime crashed after falling back from Vulkan/no-GPU. This inventory
  therefore uses live GitHub branch and compare API evidence.

The original issue named stale branch prefixes `r3/`, `r26/`, `r35b/`, and
`gpt55/`, with examples in `zephyr-zither`, `handpan`,
`bell-stack-chord-horn`, and `cryptex`. A live scan across `tonykoop` repos
found 14 remote branches matching those prefixes.

## Named Repos From Issue 192

| Repo | Live non-main branches | Status |
| --- | --- | --- |
| `handpan` | `gpt55/handpan-r2` | unmerged/diverged; see exact row below |
| `zephyr-zither` | no stale-prefix branch; adjacent `v5/zephyr-zither-l1-status` exists | unmerged/diverged, 1 ahead / 9 behind, outside the issue's stale-prefix filter |
| `bell-stack-chord-horn` | none | no branch action |
| `cryptex` | none | no branch action |

## Exact Stale-Prefix Branch List

All rows below are unmerged relative to `main` by GitHub compare API. Because
every row has `ahead_by > 0`, none is safe to delete solely from ancestry
status.

| Repo | Branch | Compare status | Ahead / behind | Ahead commits |
| --- | --- | --- | --- | --- |
| `handpan` | `gpt55/handpan-r2` | diverged | 2 / 10 | `69b197fd2973` `v5(handpan): honest packet surface (Refs #7)`; `1d9a2c1e1503` `v5(handpan): honest packet surface (Refs #4)` |
| `siku-zampona` | `r26/explorer-html` | diverged | 2 / 14 | `b7ab14c7018f` `Add generated studio explorer`; `a38dc5fa6fcd` `Tighten explorer overview scope` |
| `xiao` | `r26/explorer-html` | diverged | 1 / 10 | `2724b3df754e` `Add Round 26 explorer page` |
| `gemshorn` | `r26/explorer-html` | diverged | 1 / 12 | `ec470851591d` `Add generated gemshorn explorer` |
| `shakuhachi` | `r26/explorer-html` | diverged | 2 / 10 | `2956fc0f1d9c` `Add Round 26 explorer page`; `547d7ab19481` `Address partner overview wording` |
| `ocarina` | `r26/explorer-html` | diverged | 2 / 9 | `04624d63dfb8` `Add Round 26 explorer page`; `1dc0f27f2ca2` `Revise ocarina explorer release gates` |
| `irish-flute` | `r26/explorer-html` | diverged | 1 / 8 | `545b997af22c` `Add generated explorer page` |
| `drone-flutes` | `r26/explorer-html` | diverged | 2 / 10 | `1b6444336a1a` `Add Round 26 explorer page`; `4e46475c9598` `Clarify explorer release gate` |
| `andean-duct-flutes` | `r26/explorer-html` | diverged | 2 / 11 | `651268fce32b` `Add Round 26 explorer page`; `2f0bba77ebed` `Address explorer partner feedback` |
| `wooden-hang` | `r26/explorer-html` | diverged | 1 / 8 | `ddaedc73bc46` `Add Round 26 explorer page` |
| `steel-pan` | `r26/explorer-html` | diverged | 2 / 9 | `72370ccebf29` `Add generated explorer page`; `855ce5edd9cf` `Address explorer readiness copy` |
| `ceramic-hang` | `r26/explorer-html` | diverged | 1 / 9 | `6efa5cad47fb` `Add ceramic hang explorer page` |
| `vessel-flutes` | `r26/explorer-html` | diverged | 1 / 10 | `5cebb43e9adc` `Add Round 26 explorer page` |
| `transverse-flute` | `r26/explorer-html` | diverged | 1 / 7 | `73b6fa7bd00a` `Add Round 26 explorer page` |

## Adjacent Non-Prefix Finding

`zephyr-zither` has `v5/zephyr-zither-l1-status`, which is outside the
`r3/`, `r26/`, `r35b/`, `gpt55/` stale-prefix filter but was named in the
issue body as an affected repo. GitHub compare reports it as diverged, 1 ahead
/ 9 behind, with ahead commit `cbfa75c771b0`:
`docs: set V5-approved L1 status value (zephyr-zither#1)`.

Treat it as a separate V5 cleanup branch, not as part of this deletion queue.

## Safe Deletion Plan

1. Do not delete any branch in the exact stale-prefix list yet. All 14 have
   unique commits ahead of `main`.
2. For each `r26/explorer-html` branch, do a file-level review in its owning
   repo and decide whether the generated explorer page should be ported to the
   current public showcase flow, superseded by a newer manifest/showcase
   pipeline, or closed as intentionally abandoned.
3. For `handpan:gpt55/handpan-r2`, review the two V5 packet commits against
   current `main` and linked issues before deciding whether to cherry-pick,
   merge manually, or close as superseded.
4. Only after a branch's ahead commits are either merged, cherry-picked,
   intentionally replaced, or explicitly abandoned should the branch be
   deleted.
5. Any deletion command should be run repo-by-repo and recorded in the issue
   with the compare evidence that made it safe.

Suggested deletion command shape, after review only:

```bash
git push origin --delete <branch>
```

No row in this document currently qualifies for that command.
