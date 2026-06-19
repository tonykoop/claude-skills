# Changelog — disk-cleanup

## 1.1.0 — 2026-06-19

- Add first machine-runnable eval suite (`evals/evals.json`): 4 evals covering
  dry-run default, apply-requires-explicit-flag, docker-prune opt-in, and
  WSL VHD shrink prompt (print-only).

## 1.0.0 — 2026-05-08

- Initial release. Weekly-to-biweekly disk recovery for a multi-worktree
  development setup: `cargo clean` per worktree, merged-branch pruning, npm/pnpm
  cache cleaning, optional Docker prune, and WSL VHD shrink prompt.
