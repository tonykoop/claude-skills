# Changelog

## 0.1.0 - 2026-06-15 (draft, unshipped)

- Initial public extraction skeleton of the portable tmux-swarm supervision
  pattern, per `docs/release-readiness/sprint-supervisor-decision.md`
  (staged-extraction decision for #164).
- Adds generic `SKILL.md`, `references/operation-model.md` (watchdog-vs-skill
  split, lockfile coordination, 240s cadence rationale), an example approval
  rubric / refusal list (`references/approval-rubric.example.md`), and a
  fixture set (`fixtures/cases.md`) covering trigger, non-trigger, ambiguous
  scope, adjacent-skill conflict, safe approval, and escalation/refusal.
- **Not registered in `manifest.yaml`.** Ships nothing until it passes the
  agentic-skill gates (static, behavior, runtime, regression). Project-specific
  WRFCoin/topology behavior stays in the private `sprint-supervisor` adapter.
