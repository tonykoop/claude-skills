# script-doctor changelog

## v1.0.0 — 2026-06-21
- Greenlight gate: PASS/FAIL verdict with BLOCKER / POLISH / OPTIONAL tiered fix list and human-override note. Hard-constraint violations and BLOCK-level missing assets auto-escalate to FAIL.
- `evals/evals.json`: 5 machine-runnable evals (step order, on-the-nose detection, BLOCK propagation, yoga hard constraint, human-override disclosure).
- SKILL.md promoted to v1.0.0 — feature-complete.
- Refs tonykoop/claude-skills#431

## v0.5.0 — 2026-06-21
- Channel profiles YAML: yoga, instrument_maker, ai_agentic, consciousness, wrfcoin, unknown archetypes with hard constraints, pace targets, CTA language.
- `scripts/channel_profiles.py`: load profiles, resolve aliases, check hard constraints.
- `tests/test_channel_profiles.py`: 9 tests.
- Refs tonykoop/claude-skills#430

## v0.4.0 — 2026-06-21
- Logistical breakdown pass reference doc: segment-type taxonomy, breakdown table format, missing-asset escalation, archetype patterns.
- `scripts/breakdown_parser.py`: parse Markdown scripts with `[TC]` annotations into segment breakdown tables.
- `tests/test_breakdown_parser.py`: 10 tests (parse TC, segment count/types, TC-out chaining, WARN/BLOCK flags, table format).
- Refs tonykoop/claude-skills#429

## v0.3.0 — 2026-06-21
- Structural polish pass reference doc: hook strength rating, on-the-nose detection, retention-curve drag, transition audit, closing strength + CTA check.
- Refs tonykoop/claude-skills#428

## v0.2.0 — 2026-06-21
- Table-read pass reference doc: spoken-rhythm scan, breath-break insertion, pacing scoring, and archetype rhythm check.
- Refs tonykoop/claude-skills#427

## v0.1.0 — 2026-06-21
- Initial scaffold: 6-step workflow (table-read, structural-polish, logistical breakdown, channel-profile alignment, greenlight verdict), frontmatter, output contract.
- Refs tonykoop/claude-skills#426
