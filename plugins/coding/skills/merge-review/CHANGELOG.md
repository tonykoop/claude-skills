# Changelog — merge-review

## v0.2.0 — 2026-06-19 (structured evals)

Added `evals/evals.json` — the skill's first machine-runnable eval suite
(five cases covering the full 8-step review workflow):

- **eval 1** `single-pr-approve-and-merge`: full happy-path review — gather,
  notify, Codex wait-gate, 6-check checklist, structured review comment,
  APPROVE, merge, closing comments, prune-after-merge.sh cleanup.
- **eval 2** `single-pr-changes-requested`: PR blocked by red CI — ends at
  CHANGES REQUESTED with a blocker citing the failing step; no merge, no
  prune-after-merge call.
- **eval 3** `codex-wait-gate-timeout`: Codex enabled but no review lands in
  120s — records `codex-timed-out` in the review comment and allows merge if
  remaining checks pass.
- **eval 4** `parallel-fan-out-three-prs`: 3-PR queue triggers parallel
  sub-agent fan-out (general-purpose, sonnet); sequential merge in
  dependency order after all verdicts land.
- **eval 5** `quick-fix-then-merge`: trivially fixable PR (missing brace) —
  worktree cherry-pick, fix, force-push, re-review, merge, cleanup.

## v0.1.0 — 2026-05-20 (initial release)

First stable release: 8-step PR review workflow with Codex wait-gate,
structured review comment template, parallel fan-out for 3+ PRs, quick-fix
path, and post-merge prune-after-merge.sh cleanup.
