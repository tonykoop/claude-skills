# Changelog

## 0.1.0 - 2026-06-15

- Created `energy-management` in the Maker plugin (issue #16, epic #211).
- Resolved the "skill or template?" question: ships as a thin, data-light
  skill because capacity → task-tier → ranked-plan matching is repeatable.
- Capacity model is two inputs only (time window + energy state); no persistent
  profile, no invented productivity/energy scores.
- Reuses `idea-incubator` labels (`ready-now`, domain labels) via
  `references/energy-label-schema.md` instead of inventing a parallel taxonomy.
- Five modes: capacity intake, task-to-energy matching, weekly load review,
  recovery-aware planning, and handoff to idea-incubator / maker-engineering /
  instrument-maker / yoga-sequencer.
- Hard boundaries: no medical or mental-health advice, no made-up metrics,
  data-light, short and actionable.
- Bundled references: energy-label-schema, task-energy-matching,
  weekly-planning-template, task-source-registry.
