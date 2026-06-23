# Issue reconciliation

Closes open GitHub issues whose deliverable **already merged** — the backlog created by
the `Refs #N` (instead of `Closes #N`) build-packet convention. Without this, a finished
story's issue stays open forever, and the next sprint round re-dispatches already-done work.

## The real fix is the convention

This sweep is a **backstop**, not the primary fix. The root cause is closing-keyword
discipline (encoded in the `sprint-supervisor` skill):

- **Software story a PR completes → `Closes #<story>`** (GitHub auto-closes on merge,
  squash included).
- **Epic / umbrella / partial slice → `Refs #N`** (never auto-close an epic from a child PR).
- **instrument-maker readiness-ladder packets → keep `Refs #N`** — an L2 shop-packet
  legitimately stays open until L3/L4 build evidence. **Never run this sweep on those repos.**

## What the sweep does (safely)

- Closes an issue only on **strong signal**: a *merged* PR whose **title** matches
  `feat|fix|chore|...(#N)` or whose **body** matches `Refs|Closes|Resolves|Fixes #N`.
  A loose `#N` mention is ignored (it catches cross-references).
- **Skips epic issues** unless fully drained (no remaining open story references them).
- **Protects actively-building epics** via the optional second field in `repos.txt`.
- Closes **without a comment** (halves writes, dodges the ~500/hr secondary write cap).
- **Idempotent** — re-fetches open issues each run, so transient GraphQL failures are
  fixed by simply re-running.

## Usage

```bash
# local, manual
scripts/issue-reconciliation/reconcile.sh dry    # report only (default)
scripts/issue-reconciliation/reconcile.sh exec   # actually close

# single repo
PROTECT_EPICS="142,123" scripts/issue-reconciliation/issue-sweep.sh tonykoop/Advanced-HWE dry
```

## Weekly automation

`.github/workflows/issue-reconciliation.yml` runs `exec` weekly (Mondays) and supports
manual `workflow_dispatch` (defaults to `dry`). It needs a **`RECON_TOKEN`** secret — a PAT
that can close issues in every repo in `repos.txt` (the default `GITHUB_TOKEN` only reaches
this repo). Edit `repos.txt` to add/remove targets — **software-epic repos only**.

History: first run 2026-06-22 closed ~295 open-but-merged issues across 13 repos.
