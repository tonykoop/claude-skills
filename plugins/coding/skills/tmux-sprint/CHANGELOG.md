# Changelog - tmux-sprint

## v2.6.0 - 2026-06-15

- Added Codex `/goal` integration (resolves #117): `dispatch.sh` accepts an
  optional `--goal <text>` flag that injects `/goal <text>` before the
  assignment one-liner for each Codex pane; Claude and agy panes are
  unaffected. Goal text is recorded in the round JSON under `goal` at both
  the top level and per-codex dispatch entry (null for non-codex).
- Added `references/codex-goal-contract.md`: full design contract covering
  when to use `/goal`, startup sequence, goal shape guidelines, WRFCoin dev
  and personal-project sprint profile templates, Plan-first gate interaction,
  and manager inspection/pause/resume/clear patterns.
- Added `tests/test_goal_dispatch.sh`: four fake-tmux test cases verifying
  goal injection for codex panes, no injection for claude panes, mixed
  dispatch behavior, and no-goal baseline.
- Updated `SKILL.md` with a "Codex /goal lanes" section documenting the
  startup sequence, `--goal` flag usage, and pane inspection/recovery commands.

## v2.5.0 - 2026-06-15

- **agy / Antigravity (Gemini) as a first-class pane type (#191).**
  `ts_classify` now recognizes agy panes — IDLE on the `? for shortcuts`
  prompt footer, WORKING on the `Generating…` / `esc to cancel` spinner —
  instead of mis-classifying them as DEAD and blocking `dispatch`. Also added
  the newer-codex (`gpt-5.5+`) middot-footer idle branch.
- `restart.sh` is runtime-aware: an agy pane is revived once its prompt-box
  footer appears (not the codex banner).
- `launch-grid.sh` staggers agy cold-starts by the `agy` rate limit (8s
  default) and warns via `ts_agy_grid_warn` when more than `TMUX_SPRINT_AGY_MAX`
  (default 3) interactive agy panes are launched — Gemini quota drains fast on
  the individual plan; prefer headless `agy -p` for fan-out.
- SKILL.md: new "agy (Antigravity / Gemini) panes" section (submission,
  `~/.gemini/policies/auto-saved.toml` permission routing, `agy -p` print vs
  interactive, quota awareness) and a new **Compatibility** section covering
  tmux 3.2+ on Linux/WSL2/macOS + bash 3.2 / BSD `date` portability rules
  (#163).
- `tests/test_preflight.sh` covers the agy idle/working and codex-5.5 idle
  branches.

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
