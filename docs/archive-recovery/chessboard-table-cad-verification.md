# Chessboard Table CAD Recovery Verification

Issue: https://github.com/tonykoop/claude-skills/issues/43

## Result

The requested promotion target already contains the recovered CAD.

- Target repo: `tonykoop/chessboard-table`
- Local checkout: `/mnt/c/Users/Tony/Documents/GitHub/fabrication/chessboard-table`
- Default branch: `main`
- Current head checked: `580b335`
- Relevant recovery commit: `4fbafd0 Add fabrication handoff scaffold for chessboard table CAD archive (#2)`
- Follow-up restore commit: `580b335 Recover from 2026-05-18 hygiene-bot stash; restore 21 DSLR photos of the coffee table`

## Evidence

`cad/` is populated on `main`:

| Extension | Count |
|---|---:|
| `SLDPRT` / `sldprt` | 17 |
| `SLDDRW` | 9 |
| `ai` / `AI` | 6 |
| `SLDASM` | 3 |
| `pdf` | 2 |

Representative CAD files present:

- `cad/Checkerboard.SLDASM`
- `cad/Checkerboard Tile.SLDPRT`
- `cad/Chessboard Layout.ai`
- `cad/Chessboard Layout V2.pdf`
- `cad/Coffee Table Edge Band.SLDPRT`
- `cad/Wedges Laser Assembly.SLDASM`
- `cad/Wedge.SLDPRT`
- `cad/Long Panel.sldprt`
- `cad/Short Panel Bubinga.sldprt`

The repo also has a recovery-oriented handoff:

- `build-notes/fabrication-handoff.md`

And a README warning that the CAD archive is historical reference, not
shop-ready until the handoff gates are reviewed.

## Branch / Issue Implication

The original issue next step was:

> Copy `D:\...\to organize\Coffee Table\` -> `GitHub\chessboard-table\cad\`.

That action appears already complete in the target repository. Do not duplicate
the CAD tree or re-copy archive assets unless a later audit identifies missing
files against the original `Coffee Table` archive.

## Remaining Review

- Compare the current `cad/` tree against the original archive if that exact
  `Coffee Table` source folder is found again.
- Keep `cad/` treated as historical reference until
  `build-notes/fabrication-handoff.md` is signed off.
- Close or supersede #43 once the host confirms the external repo state is
  sufficient.
