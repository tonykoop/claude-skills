# script-doctor changelog

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
