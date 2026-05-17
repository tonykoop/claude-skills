# Changelog - tmux-sprint

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
