# Changelog — yoga-sequencer

## v1.2.1 — 2026-06-13

- `references/sequencing-principles.md`: mirrored the staple-pose safety boundary into mixed-level room defaults so reference-only loading still routes pigeon, lizard, deep twists, deep backbends, arm balances, inversions, and other constraint-sensitive shapes through `poses.yaml`.
- SKILL.md: bumped version and `last-updated` for the safety-boundary hardening.
- Source: Round 2 Henry implementation for issue #26.

## v1.2.0 — 2026-05-10

- Added `references/heated-room-safety.md` with a reusable teacher-facing hot-room checklist covering hydration, breath-quality gates, heat-distress signs, pregnancy / non-heated substitutions, and compression or inversion caution.
- SKILL.md now directs heated, hot power, sculpt, and C3-style requests to load the heated-room safety reference and include the checklist in full-class outputs.
- `references/sequencing-principles.md`: added heated-room cue-volume guidance so teacher voice gets quieter as repetition and heat rise.
- Source: Round 8 Bob hot-power vinyasa follow-on (issue #95).

## v1.1.0 — 2026-05-10

- Added cue-density arc as a required field on every phase of a full-class plan. Controlled vocabulary: `sparse`, `moderate`, `rhythmic`, `focused`, `minimal`.
- `references/sequencing-principles.md`: new "Cue density across the arc" section with default arcs for vinyasa (60/75/90), yin, restorative, and heated power vinyasa.
- `references/sequencing-principles.md`: new "Alternate-peak guidance" section with the regression-vs-alternate distinction, a constraint trigger list, and worked examples (Bound Side Angle, Bird of Paradise, Camel, Crow, Revolved Triangle).
- `references/playlist-builder-handoff.md`: formalized `cue_density` controlled vocabulary, clarified its independence from `energy`, and added a worked yin-class example so the schema is shown across non-vinyasa styles.
- SKILL.md: peak-pose-first mode now requires a teacher-discretion alternate peak when the default peak is constraint-heavy; sequencing rules and final check updated.
- Source: Round 7 TwinGrid Lane Dan blind run + Partner Peek (issue #69).

## v1.0.0 — 2026-05-09

- Initial skill: yoga session sequencing with pose safety boundaries.
- Lazy-load poses.yaml; inline playlist YAML for cross-platform portability.
- Staple-pose cheat-sheet safety boundaries tightened.
- Shorter-class playlist handoff worked examples added.
- Public-scrub pass: private names removed.
