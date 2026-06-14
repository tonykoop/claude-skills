# Changelog — sprint-supervisor

## v1.2.0 — 2026-06-13

Closes #163 (cross-platform tmux compatibility audit).

### Added

- **Platform compatibility section** in `SKILL.md` — documents verified platforms (WSL2/Ubuntu 22.04, macOS Homebrew tmux 3.4+), minimum tmux version (2.0), macOS BSD `date` portability caveat, and WSL2 `/tmp` boundary notes.
- **Provider-prompt compatibility notes** — folds in evidence from tmux-sprint v2.4.1 (`#191`, `#163`): agy idle/working sentinels are correctly excluded from `PROMPT_REGEX` (not confirmation prompts); agy's approval prompt phrasing is TBD and documented as an open gap; gpt-5.5 confirmation prompts use standard `Would you like to` phrasing (no change needed).

### Fixed

- **`grid-scan.sh` bash 3.2 compatibility** — replaced `mapfile -t` (bash 4+ only) with a `while IFS= read -r` loop. The script now works on the macOS system shell (bash 3.2.57) without requiring Homebrew bash.

### Follow-up (out of scope for this PR)

- #160 Mobile cold-start wiring — requires live test with Tony's mobile/PC setup; blocked on availability.
- #161 Routines integration — blocked on routines GA.

## v1.1.0 — 2026-05-18

Second full-sprint run (4 rounds, 32 PRs, ~2h 12m, 35 supervisor cycles). Adaptive cadence and one-line wakeup prompts implemented.

### Added

- **Adaptive cadence** (30s/240s/1800s) replacing fixed 240s — phase-driven by `current_phase` in the lockfile. Saves unnecessary cycles during idle phases.
- **Lockfile-resume pattern** — all per-cycle state persisted to `<scope>.lock`; wakeup prompt reduced to one line. Eliminates ~3KB of re-pasted rubric per cycle.
- **`.pending` short-circuit** — watchdog writes `/tmp/sprint-supervisor/<scope>.pending` on command-shape prompts it won't auto-handle; supervisor reads and clears it at iteration start, forcing tightest cadence without polling.
- **Phase tracking fields** (`current_phase`, `last_goal_achieved_seen_at`, `last_status_summary`) in the lockfile schema.
- **Watchdog `SPRINT_SESSIONS` export requirement** in Prerequisites step 4 — prevents watchdog from silently watching the wrong sessions.

### Fixed

- **Watchdog session scoping footgun** — documented and required the `SPRINT_SESSIONS` export. Previously the watchdog defaulted to `twingrid-a twingrid-b` regardless of the supervisor's actual scope.

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
