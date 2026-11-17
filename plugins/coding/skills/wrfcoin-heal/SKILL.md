---
name: wrfcoin-heal
description: Run a focused WRFCoin fix-check-test loop for Rust, TypeScript, Flutter, or Solidity changes. Use when a persona branch is failing checks or needs a tight iterate-until-green workflow.
---

# WRFCoin Heal

Use a scoped compile and test loop after implementation work.

For a generic Rust or TypeScript repair loop outside WRFCoin, use `heal`.

## Process

1. Detect the smallest reasonable scope.
2. Run compile or type checks first.
3. Fix root-cause errors before broader tests.
4. Run targeted tests next.
5. Repeat until green or a real design decision blocks progress.

## Scope examples

- Rust crate: `cargo check -p <crate>`
- Rust targeted tests: `cargo test -p <crate> <test_name>`
- TypeScript: `npx tsc --noEmit`
- Jest (backend): `DATABASE_URL=postgres://127.0.0.1:1/x REDIS_URL=redis://127.0.0.1:1 npx jest --no-coverage`
  (unset, backend tests hit the LIVE local Postgres/Redis)
- Flutter: `flutter test <explicit test files>` (the full suite hangs on ws on two files; CI runs them)
- Solidity: `npx hardhat test`

## Rules

- Work in a worktree of `/home/tony/wrfcoin-public/<repo>`, never in `/home/tony/wrfcoin/<repo>`
  (read-only archive clones).
- Rust: stop if `df -h /` shows under 20 GB free; never point a cargo target dir at /tmp.
- Build and test on the workstation or CT102 only, never on a host running a live node.

- Fix one logical problem per round.
- Do not refactor unrelated code during a heal loop.
- When a struct or API changes, search all usages before re-running checks.
- Treat known pre-existing failures as non-goals unless the task is explicitly to fix them.
- Stop and surface blockers when the failure requires a product or architecture decision.
