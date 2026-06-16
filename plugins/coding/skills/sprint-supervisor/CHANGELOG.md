# Changelog — sprint-supervisor

## v1.3.1 — 2026-06-15

Forward-looking routines design (repo issue #161 — **still blocked on Anthropic routines GA**; no runtime added).

### Added

- **`references/routines-integration.md`** (#161) — design-only doc, prominently banner-marked BLOCKED on routines GA. Fleshes out the `nightly-sprint` routine sketch (Step 1 cold-start dispatch sprint-manager at 22:50; Step 2 dispatch sprint-supervisor loop-until-07:00 at 22:55; Step 3 morning summary + exit both at 07:00; Step 4 conditional escalation→pause→page→await-ack). Documents the scheduled-task→routine **migration path** (overlap dry-run on a throwaway/attended night, cutover only after one clean unattended night, disable-not-delete the old scheduled task, rollback to the bridge, and the "exactly one live nightly trigger per scope — never zero, never two" invariant). All routine syntax is clearly labeled illustrative-only pending the real (unknown) API. Cross-references `dispatch-patterns.md` §2/§3/§4 and SKILL.md behaviors rather than duplicating them.
- **Pointer in `references/dispatch-patterns.md` §4** to the new routines-integration doc (append-only, minimal).
- **SKILL.md** cold-start references sentence now mentions `references/routines-integration.md`.

### Note

This is honest forward-looking work — issue #161 stays **open**, blocked on routines GA. Nothing here is implemented as runtime; the live nightly mechanism remains the scheduled-tasks MCP bridge (`dispatch-patterns.md` §3).

## v1.3.0 — 2026-06-15

Sprint-infra hardening (repo issues #163, #160, #166, #191).

### Added

- **Compatibility section** (#163) — tmux 3.2+ matrix for Linux/WSL2/macOS, plus the bash-3.2 / BSD-`date` portability rules and a note that `sprint-watchdog.sh` (install-only) needs the same fixes when packaged.
- **agy / Antigravity permission caveat** in the approval rubric (#191) — agy is Gemini-backed with a `~/.gemini/policies/auto-saved.toml` allowlist; broadening that policy (auto-allow `run_shell_command`, `--dangerously-skip-permissions`, `skipPermissions`) is now an explicit refusal-list item. Headless `agy -p` raises no prompts.
- **Mobile cold-start chosen path** (#160) — `references/dispatch-patterns.md` §2 now commits to the magic-file / dispatch-watcher mechanism (over always-on Cowork or SSH relay), with the dispatch-file shape, a prerequisites list (persistent PC-side watcher, a phone-writable / PC-readable transport, atomic claim), and a clear "live phone→PC test still pending Tony's transport confirmation" status.

### Changed / fixed (portability — #163)

- `scripts/grid-scan.sh` — `mapfile` → portable `while read` loop; `capture-pane | tail -12` → `capture-pane -p -S -40` so prompts above trailing blank rows aren't missed; `PROMPT_REGEX` widened with a generic confirmation catch-all and agy/gemini phrasings.
- `scripts/notify-supervisor.sh` — GNU-only `date -Iseconds` and `%3N` now fall back to portable `date -u +%Y-%m-%dT%H:%M:%SZ` / epoch seconds on BSD/macOS.
- Lockfile snippet in Prerequisites uses portable `date -u +%Y-%m-%dT%H:%M:%SZ`.
- Provider-agnostic rubric note now names `agy` and points at `tmux-sprint/references/provider-failover.md` (#166).

## v1.2.0 — 2026-06-14

Hardening from the AI-HWE sprint (~14 rounds, 60+ PRs merged across 5 repos). Dispatch/parallelism was strong; every painful failure was at the merge/integration boundary or in permission ergonomics.

### Added

- **Pre-merge checklist** section in `SKILL.md` — `mergeStateStatus == CLEAN` is necessary-not-sufficient. Covers: verify a CI-adding PR's new job is actually green; run tests locally for no-CI repos; new-task-family → completeness-validator cascade; duplicate/superseded detection for self-extending agents; foundation-first + rebase-the-rest dependency order; the coincidental-shared-context merge trap (mis-joined function bodies from naive marker-stripping).
- **Manager-acting-on-an-agent's-behalf safety** section — committed-vs-staged check before a manager-push; don't race a live agent on a shared `.git` (scratch worktree + lock-retry); open codex PRs from host with `Refs`.
- **Pre-dispatch verification** section (combined manager+supervisor role) — assert each worktree's `git remote get-url origin` matches the intended repo; launch agents in true `auto` mode (claude `--permission-mode auto`, codex `-a on-failure`) not `acceptEdits`; clear the first-run trust-folder prompt.

### Why

`acceptEdits` stalled an Opus grid on every bash command (~30min lost hand-clearing). Merged a red CI-adding foundation PR → poisoned main. Manager-pushed a staged-but-uncommitted fix → CI stayed red. A worktree pointed at the wrong clone routed an agent's work to the wrong repo. Each is now a checklist item.

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
