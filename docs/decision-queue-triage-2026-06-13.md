# Decision Queue Triage - 2026-06-13

Issue: tonykoop/claude-skills#188

This document turns the human-decision queue into a decision surface plus a
safe default for each item. It does not perform repository edits outside this
`claude-skills` worktree.

## Retrieval And Source

- `qmd status` succeeded: 2821 indexed markdown files, 13904 embedded vectors,
  15 collections, last updated about 18 hours before this pass.
- `qmd search` in `sprint-docs` for this lane returned no direct hits.
- `qmd query` was attempted for the lane topic, but the Bun-backed local qmd
  runtime crashed after falling back from Vulkan/no-GPU.
- Source queue: GitHub issue
  [tonykoop/claude-skills#188](https://github.com/tonykoop/claude-skills/issues/188).

## Triage Table

| Queue item | Human decision needed | Safe default until decided | Suggested next action |
| --- | --- | --- | --- |
| `tongue-drum` copyrighted WOOD magazine scans | Decide whether any public redistribution is acceptable and where private reference scans may live. | Treat public full-page scans as not redistributable. Remove public copies in the repo, replace them with a citation block, and keep any scans only in ignored local/private storage. | Open a `tongue-drum` PR that deletes scans from the public tree, adds `SOURCES.md`/`NOTICE.md` citation text, and adds ignore rules for local reference scans. |
| `cryptex` John Giem third-party plan and derived CAD | Decide whether the plan can be redistributed and what license/attribution applies to derived files. | Keep repo private. Do not publish PDFs, photos, or derived CAD as a public kit. Add attribution and a public-release blocker note instead of trying to infer license rights. | Add a private-safe `NOTICE.md` and `PUBLIC_RELEASE_BLOCKERS.md`; only broaden distribution after permission/license evidence exists. |
| `tumbler-oven` diagnostic and repair narratives | Tony must write or approve the first-person engineering narratives. | Do not fabricate first-person experience. Keep placeholders or add an outline prompt that makes authorship explicit. | Prepare a short authoring scaffold with section prompts and photo references, but leave narrative text marked `forthcoming`. |
| `suction-cup-mount` reflections | Tony must decide and author the hinge-geometry and gel-interface reflections. | Do not publish AI-written first-person reflections. Keep the repo factual and patent-adjacent until Tony supplies the reflections. | Add outline stubs for the two reflections and link US Patent 11,137,017 B2 as context. |
| `_meta/yoga` portfolio tile | Decide whether the 12-class tarot-anchored curriculum should be represented publicly and how it fits the current portfolio layout. | Do not expose local-only curriculum content by default. Keep portfolio unchanged unless Tony chooses a public framing. | Draft two low-risk options: add a third practice tile, or keep "Two Practices" and link the curriculum only after public copy review. |
| `cryptex` binary blobs and LFS/history | Decide whether to rewrite history with `git-filter-repo` or accept existing history size. | Do not rewrite history without explicit approval. Add forward-looking LFS tracking and a blob-size CI guard first. | Create a `cryptex` PR adding `.gitattributes` for CAD/binary extensions and a CI size check; file a separate explicit history-rewrite decision. |
| stale sprint branches | Decide which unique branch commits should be merged, cherry-picked, abandoned, or deleted. | Delete nothing. All live stale-prefix branches found in the 2026-06-13 scan are unmerged/diverged with ahead commits. | Use [stale-sprint-branches-2026-06-13.md](stale-sprint-branches-2026-06-13.md) as the review list; clear branches only after the ahead commits are accounted for. |
| `instrument-showcase` manifest drift | Decide whether regeneration is automatic after every sprint wave or manually gated. | Do not fabricate missing entries. Regenerate from repo truth in a controlled PR and add a repeatable drift check before making it automatic. | Add a CI or scheduled check that reports manifest count drift and documents the qmd/update/embed trigger path. |
| `marimba` readiness label | Assign an explicit V5/L-level status. | Use the most conservative public label until reviewed: `Status: L1 concept packet`, if current repo evidence supports only scaffold-level readiness. | Open a focused `marimba` docs PR that changes only the status line and cites the repo evidence used. |
| `chessboard-table` scaffold | Decide whether to complete the shop packet or keep it as a review scaffold. | Keep as `review-scaffold` / `pending_measurement`; do not invent dimensions, BOM rows, cut lists, or visual-output-register entries. | Add an explicit status block listing missing measurements and the minimum evidence needed to promote it. |

## Decision Order

1. Legal/IP items first: `tongue-drum` and `cryptex` redistribution.
2. Public portfolio authorship next: `tumbler-oven`, `suction-cup-mount`, and
   `_meta/yoga`.
3. Infrastructure hygiene: `cryptex` LFS/history, stale branches, and
   `instrument-showcase` drift.
4. Readiness/scaffold labels: `marimba` and `chessboard-table`.

## Safe-Default Principle

When the repo evidence is incomplete or the decision requires Tony's judgment,
prefer a reversible, non-public, provenance-preserving default:

- remove or quarantine risky public artifacts instead of rationalizing them;
- block public release instead of inferring licenses;
- preserve private/local evidence without publishing it;
- use `pending_measurement`, `review-scaffold`, or `L1 concept packet` rather
  than inventing maturity;
- avoid branch deletion until unique commits are merged, superseded, or
  explicitly abandoned.
