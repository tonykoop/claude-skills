# Changelog — disk-cleanup

## 1.2.0 — 2026-07-02

- Add opt-in **stale worktree removal** (`--prune-worktrees`, dry-run by default,
  `--apply` to act). Removes worktrees that are clean AND fully merged into
  `origin/main`; `git worktree remove` preserves branch refs, so no committed
  work is lost.
- **Persona-home protection** (`is_protected_worktree`): canonical persona
  worktrees (`<repo>-<persona>`) are never removed. The guard tests the worktree
  BASENAME — after a 2026-07-02 incident where an ad-hoc pass matched a
  `$`-anchored path regex against composite `repo|path|meta` lines (so the anchor
  never bound and ~25 persona homes were swept up). Documented inline.
- **Multi-root coverage**: worktrees are now enumerated via `git worktree list`
  per repo instead of a single `worktrees/*` glob, so secondary roots (e.g.
  `hwe-wt`) are covered by both the removal and inventory steps.
- **Fix CRLF line endings**: the script was committed with CRLF and would fail to
  run under bash on Linux/WSL (`case … in\r` syntax error). Normalized to LF.

## 1.1.0 — 2026-06-19

- Add first machine-runnable eval suite (`evals/evals.json`): 4 evals covering
  dry-run default, apply-requires-explicit-flag, docker-prune opt-in, and
  WSL VHD shrink prompt (print-only).

## 1.0.0 — 2026-05-08

- Initial release. Weekly-to-biweekly disk recovery for a multi-worktree
  development setup: `cargo clean` per worktree, merged-branch pruning, npm/pnpm
  cache cleaning, optional Docker prune, and WSL VHD shrink prompt.
