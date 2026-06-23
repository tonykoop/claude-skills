# script-doctor changelog

## v0.2.0 — 2026-06-22
- Add mrbeast and coding channel profiles to references/channel-profiles.yaml. Channel count: 7. VALID_CHANNELS in run_review.py updated to include mrbeast and coding.
- Refs tonykoop/claude-skills#430

## v0.1.5 — 2026-06-22
- Add scripts/logistical_breakdown.py: segment parser (stage direction regex → type/TC/assets/props/location/risk classification). Wire into run_review.py; last stub removed.
- Refs tonykoop/claude-skills#429

## v0.1.4 — 2026-06-22
- Update run_greenlight(): full BLOCKER/POLISH/OPTIONAL tier collection from all passes; closing_score < 4 auto-added as POLISH flag. Update _render_review() to emit tiered fix list + phone-friendly READY line.
- Refs tonykoop/claude-skills#431

## v0.1.3 — 2026-06-22
- Add scripts/structural_polish.py: real heuristic structural polish pass (hook/closing scoring, on-the-nose detection, retention dips, transition audit). Wire into run_review.py.
- Refs tonykoop/claude-skills#428

## v0.1.2 — 2026-06-22
- Add scripts/table_read.py: real heuristic table-read pass (hard-to-speak, breath breaks, pacing, archetype alignment). Wire into run_review.py.
- Refs tonykoop/claude-skills#427

## v0.1.1 — 2026-06-22
- Add evals/evals.json: 5 trigger-routing + end-to-end behavior evals.
- Refs tonykoop/claude-skills#426

## v0.1.0 — 2026-06-21
- Initial scaffold: 6-step workflow (table-read, structural-polish, logistical breakdown, channel-profile alignment, greenlight verdict), frontmatter, output contract.
- Refs tonykoop/claude-skills#426
