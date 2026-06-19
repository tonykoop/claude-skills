# Changelog

## 0.2.0 — 2026-06-19

- Add first machine-runnable eval suite (`evals/evals.json`): 4 evals covering
  auto-approve routine edit prompt, escalate destructive/ambiguous prompt,
  lockfile coordination for peer instances, and morning summary report.
- Add manifest.yaml entry (skill was missing from canonical manifest).

## 0.1.0 - 2026-06-15

- Initial public release of the portable tmux-swarm supervision pattern,
  extracted per `docs/release-readiness/sprint-supervisor-decision.md`
  (staged-extraction decision for #164).
- Generic `SKILL.md`, `references/operation-model.md` (watchdog-vs-skill split,
  lockfile coordination, 240s cadence rationale, escalation policy, morning
  summary), an example approval rubric / refusal-list shape
  (`references/approval-rubric.example.md`, ships an empty refusal list), and a
  fixture set (`fixtures/cases.md`) covering trigger, non-trigger, ambiguous
  scope, adjacent-skill conflict, safe approval, and escalation/refusal.
- Shipped in the `coding` plugin (v1.1.0), auto-discovered from `skills/`.
  `manifest.yaml` drift entry is a pending follow-up (see PR for the prepared
  block).
- Project-specific WRFCoin/topology behavior stays in the private
  `sprint-supervisor` adapter, which supplies this core a config profile.
