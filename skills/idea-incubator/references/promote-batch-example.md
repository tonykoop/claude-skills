# Promote-batch worked example: legacy-import / Weather Balloon Camera Vessel

This worked example walks through Promote-batch on the cluster that
prompted the mode (Round 7 TwinGrid, Lane Bob, 2026-05-10). It is here so
that future runs have a concrete pattern to mirror, not so the cluster
itself is repeated.

## Cluster signal

- Burst: 21 `capture`-labeled issues opened in `tonykoop/claude-skills`
  inside a 28-hour window (2026-05-09 → 2026-05-10).
- Shared template: every issue used `Capture / What this is / Why it
  matters / Next step / Promotion target`.
- Shared root: each capture pointed at a path under
  `D:\...\Document Archive 3-3-18\`.
- Shared blocker: a single inventory pass (`archive-inventory-2026-05-09.csv`)
  was the prerequisite for confirming source paths and sizes.

Two of the four heuristics in `SKILL.md` fire — burst plus shared root —
which is enough to move from Promote to Promote-batch.

## Promotion-readiness matrix

| Issue | State | Evidence | Blockers | Best next route | Decision |
|---|---|---|---|---|---|
| #43 chessboard-table CAD | ready-now, maker | source folder confirmed in inventory CSV; `chessboard-table` repo exists | none | inline (copy + commit) | promote (small) |
| #53 full inventory pass | ready-now, skills | `archive-inventory-2026-05-09.csv` already in working dir | already satisfied | n/a | **close, do not promote** |
| #55 Weather Balloon Camera Vessel | promote, maker | 46 SolidWorks files, 816.81 MB, no target repo | LFS rules + provenance review | new repo via `maker-engineering` | **promote first** (sets cluster conventions) |
| #57 Kickstarter aerial print | promote, maker | folder size + sibling CAD; ambiguous repo target | own repo vs sub-folder of `aerial-photography` | needs decision before promote | defer |
| #44 aerial drone portfolio | promote, maker | wide-scope portfolio capture | curation pass needed | maker-engineering after #57 decision | defer |
| #58 additional aerial folders | capture, maker | folder names only | inventory cross-ref needed | promote into #44 once that lands | defer |

## One-promote-first recommendation

Promote **#55** first. Its scaffold establishes:

- LFS extension list (`*.sldprt *.sldasm *.eprt *.stl *.step *.stp`)
- `legacy-import` label set (`legacy-import`, `cad-recovery`, `documentation`,
  `needs-provenance`, `maker`)
- `legacy-import-0.1` milestone naming
- `docs/evidence-ledger.md` structure with observed-vs-inferred columns
- Private-first visibility with provenance gating

Sibling promotions (#57, #44, #58) mirror those conventions, which is
cheaper than retrofitting them after the fact.

## Binary-asset / LFS pass

Applied to #55 (the only cluster member with a binary-asset payload large
enough to matter):

1. Target repo `tonykoop/weather-balloon-camera-vessel` does **not** exist
   (verified via `gh repo view`).
2. Files are still on `D:\...\CAD\Weather Balloon Camera Vessel\`; not yet
   copied into any working tree.
3. Yes — LFS must be configured before first import. 46 files at 817 MB
   (~17.7 MB average) means several individual files will exceed GitHub's
   100 MB per-file hard limit.
4. Provenance source-of-truth: `archive-inventory-2026-05-09.csv`
   (line: `CAD\Weather Balloon Camera Vessel,2,46,816.81,2023-01-23,
   .eprt,.jpg,.sldprt,.stl`).
5. Use `Refs #55`, not `Closes #55`. Source capture stays open as a
   provenance anchor until the evidence ledger lands.

## Provenance discipline

The capture body says "designed (and possibly built) to mount a camera on
a weather balloon." That "possibly" is load-bearing. The evidence ledger
in the new repo separates:

- **Observed:** `<filename>` present in archive at `<path>` on `<date>`.
- **Inferred:** project purpose, altitude target, flight history, build
  status — all marked PROVISIONAL until reviewed.

Public-facing README copy may repeat the Observed column verbatim. It must
not promote Inferred-column wording without review.

## What this example does NOT prescribe

- Specific repo names beyond the one used here.
- LFS extension lists for non-CAD clusters (audio/video/PDF clusters need
  their own extension lists).
- Whether sibling captures (#57, #44, #58) eventually merge or stay
  separate. Promote-batch defers that decision; it does not pre-empt it.
