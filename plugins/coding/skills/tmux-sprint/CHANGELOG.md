# Changelog - tmux-sprint

## v2.4.1 - 2026-06-13

- `preflight`/`ts_classify` now recognize **Antigravity (`agy`)** panes
  (resolves #191): idle is detected from the `? for shortcuts` footer and
  working from the `esc to cancel` / `Generating...` spinner. Previously agy
  panes were misclassified `DEAD`, which blocked `dispatch` from sending to
  them.
- Fixed codex idle detection for newer codex (e.g. `gpt-5.5`), which shows a
  `model · cwd` footer without a `5h NN%` meter at idle (relates to #163/#7).
  The codex idle rule now also accepts the middot footer.
- Added `tests/test_preflight.sh` cases for agy idle/working and the codex
  middot-footer idle.

## v2.4.0 - 2026-06-09

- Shipped the core driver implementation, resolving #193 (the SKILL.md
  documented `preflight`/`dispatch`/`restart` plus a launch step, but the
  scripts and assets were missing from the publish).
- Added `scripts/launch-grid.sh` — builds the two-session persona grid from
  `personas.json` and starts each runtime (`--with-manager`, `--no-start`,
  `--kill`).
- Added `scripts/preflight.sh` — structured pane probe with `--pane`,
  `--panes`, and `--json`; classifies IDLE/WORKING/DEAD and codex
  exited/update states with ctx and usage meters.
- Added `scripts/dispatch.sh` — transactional, assignment-file-only fan-out:
  preflight gate, `docs/plans/` path + preamble validation, runtime-aware
  rate limiting, three-tier submission verify, and per-round state JSON.
- Added `scripts/restart.sh` — codex-aware revival state machine.
- Added `scripts/lib/common.sh` shared helpers, `assets/assignment-preamble.txt`,
  and `assets/personas.default.json` (the persona seed).
- Added `tests/test_preflight.sh` and `tests/test_dispatch.sh`, which run
  without a live tmux via a fake `tmux` on `PATH`.
- Fixed a stale `scripts/dispatch.py` reference in SKILL.md (the validator is
  `dispatch.sh`) and pointed the launch step at the shipped `launch-grid.sh`.

## v2.3.1 - 2026-05-17

- Added `references/provider-failover.md`, a manager-owned contract for
  migrating budget-exhausted panes across Codex, Claude, Gemini, and final
  manager absorption.
- Documented provider failover in `SKILL.md`, including fallback order,
  provider state fields, same-pane swap boundaries, and summary requirements.

## v2.3.0 - 2026-05-11

- Added label-aware sprint batching and smart model-picker routing guidance.
- Added `references/label-aware-routing.md` with source-label preservation,
  assignment header shape, model conflict handling, and sprint-update output
  expectations.
- Added `scripts/plan-label-batches.sh` plus a focused smoke test for turning
  GitHub issue JSON into Markdown/JSON batch plans.

## v2.2.0 - 2026-05-10

- Added `twingrid_contracts.py` helpers for `ready_for_peek.json` freeze
  records and Partner Peek record stubs.
- Documented Plan-first implementation dispatch, short file-based prompt
  dispatch, pane recovery from frozen artifacts, and canonical
  `skill_findings.md` naming.
- Documented pane `/rename`, smart batching, and model-picker notes for
  TwinGrid dispatch hygiene.
- Extended the manager matrix to read freeze state, SHA256 manifests,
  canonical/alias skill findings files, `partner-feedback.md`, and
  `combine_recommendation.md`.

## v2.1.0 - 2026-05-10

- Added TwinGrid blind A/B and Partner Peek workflow guidance.
- Added reusable blind-pass and Partner Peek handoff templates.
- Added a filesystem matrix script for lane artifacts, validations, skill
  recommendations, and pane-block findings.

## v2.0.0 - 2026-05-08

- Initial public tmux sprint driver contract.
