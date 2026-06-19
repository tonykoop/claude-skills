# Changelog

## 1.2.0 — 2026-06-19

- Add first machine-runnable eval suite (`evals/evals.json`): 4 evals covering
  read-only refresh (no edits), personal GitHub queue with Label/Model/Batch
  columns, WRFCoin persona queue update, and archive follow-up before
  regenerating dispatch prompts.

## 1.1.1 - 2026-05-11

- Added read-only refresh mode guidance for reporting stale sprint counts,
  open issue/PR pressure, ready/draft/overlap PR clusters, and candidate queue
  changes without editing the sprint document.
- Added queue-gating language so `risk:*`, welfare/safety review, privacy/IP,
  and clarification labels remain manager/Tony decisions even when an item also
  carries `sprint:implementation-pass`.

## 1.1.0 - 2026-05-10

- Added personal GitHub sprint Queue guidance with `Label`, `Model`, and
  `Batch` columns for generated queue rows.
- Updated dispatch prompt rules to carry label/model/batch context while still
  grouping by meaningful labels and themes instead of batch numbers alone.
- Added stale issue refresh guidance so sprint queues are reconciled with live
  GitHub issue and PR state before promotion or dispatch.
- Added archive follow-up guidance for promoting durable, public-safe actions
  from sprint artifacts without leaking private family or media details.
