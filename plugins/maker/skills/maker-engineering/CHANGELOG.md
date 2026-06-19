# Changelog — maker-engineering

## 1.2.0 — 2026-06-19 (eval suite)

Adds the first machine-runnable eval suite (5 evals) and bumps SKILL.md to v1.2.0.

- `evals/evals.json` — 5 evals:
  1. `safety-gate-before-build-packet` — treehouse triggers all 8 gate
     sub-sections + verbatim "not a certification" clause before any packet.
  2. `routing-uses-canonical-specialist-name` — speaker cabinet routes to
     `instrument-maker` by exact canonical name; no acoustic work done here.
  3. `doe-mode-complete-matrix` — wood-glue experiment → full DoE matrix with
     factors, response, controls, trial design, logging, stop conditions.
  4. `intake-three-questions-max` — vague project → at most 3 clarifying
     questions; stated assumptions then project brief with route.
  5. `handoff-runtime-agnostic` — hybrid handoffs use canonical names only,
     no runtime-specific syntax.

## 1.1.0 — 2026-05-10 (human-carrying safety gate)

Added the human-carrying / floatable-object safety gate with the 8-section
packet template, the verbatim "not a certification" clause, and the Round 7
steam-bent kayak as the canonical worked example.

## 1.0.0 — initial

Initial umbrella routing skill for physical making projects. Intake,
routing, DoE, cross-project pattern search, and multi-specialist handoffs.
