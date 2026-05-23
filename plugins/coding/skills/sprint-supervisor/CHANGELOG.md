# Changelog — sprint-supervisor

## v1.0.0 — 2026-05-12

Initial release. Captures the supervisor pattern that emerged from the 2026-05-12 overnight WRFCoin sprint (8.1h, 47 approvals, 0 escalations).

### Added

- `SKILL.md` — main skill body: prerequisites, dispatch modes (warm-start vs cold-start), 240s wakeup cadence, five-step iteration loop, full approval rubric, refusal list, escalation triggers, coordination with peer supervisors, morning summary outline, and tuning notes from the inaugural overnight run.
- `references/scaling-topology.md` — twingrid/triplegrid/quadgrid topology examples, lockfile coordination schema, conflict resolution rules, topic specialization patterns, when (and when not) to add another supervisor.
- `references/morning-summary.md` — six-section summary template, scope-aware reporting rules for multi-supervisor setups, worked example from the 2026-05-12 run.
- `references/dispatch-patterns.md` — warm-start, mobile cold-start, scheduled-tasks recurring supervision, forward-looking routines integration, mid-sprint peer addition with release-pattern note, dispatch decision tree.
- `scripts/grid-scan.sh` — bundled pane-scanning script that takes scope targets as args, used each cycle.

### Design notes

- Lockfile-based multi-supervisor coordination (under `/tmp/sprint-supervisor/<scope>.lock`) chosen over a central coordinator because it's deterministic and requires no negotiation. Earlier `started` timestamp wins on overlap conflicts.
- Rubric is structured by **prompt pattern shape**, not by command substring, because codex's prompt UI is stable while command shapes are not. Provider-agnostic: same rubric applies to claude/gemini CLIs once sprint-manager multi-provider failover lands (see repo issue #166).
- Splits intentionally with `sprint-watchdog.sh` (mechanical 70% of edit-prompt approvals — no model in loop) so the model time is spent on judgment work, not mechanical clicks.

### Known forward work (tracked in repo issues)

- #160 Mobile cold-start wiring
- #161 Routines integration when GA
- #162 Benchmarking pattern for operational skills
- #163 Cross-platform tmux audit
- #164 Public release readiness
- #165 skills-meta dependency manifest
- #166 Multi-provider failover (sprint-manager)
