# Changelog

## 1.1.0 - 2026-05-10

- Added personal GitHub sprint Queue guidance with `Label`, `Model`, and
  `Batch` columns for generated queue rows.
- Updated dispatch prompt rules to carry label/model/batch context while still
  grouping by meaningful labels and themes instead of batch numbers alone.
- Added stale issue refresh guidance so sprint queues are reconciled with live
  GitHub issue and PR state before promotion or dispatch.
- Added archive follow-up guidance for promoting durable, public-safe actions
  from sprint artifacts without leaking private family or media details.
