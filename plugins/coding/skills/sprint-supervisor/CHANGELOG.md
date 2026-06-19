# Changelog — sprint-supervisor

## v1.8.0 — 2026-06-19 (morning-summary generic worked example — Refs #164)

Genericized `references/morning-summary.md` for public release (Refs #164):

- **Template** — replaced hardcoded project-specific group names, repo
  citation strings, and N5-testnet section with generic placeholders
  (`<owner>/<repo>#<n>`, `<group>`, `<host>`). Added note that section 4
  (named host / service) is only emitted when `trusted_hosts` is configured.
- **Worked example** — replaced the project-coupled worked example with a
  fictional-project equivalent (`acme/core`, `acme/infra`, etc.) and swapped
  the private workspace path (`rm -rf /home/tony/wrfcoin/cache-old/`) for the
  generic placeholder `rm -rf <workspace>/cache-old/`. Added a preamble
  directing users to populate group names from `labels.repo_groups` in their
  config.
- Removed the private "N5 Pro testnet" section from the template; a generic
  "Named host / service" section replaces it with a conditional note.

This is the last sprint-supervisor reference doc that contained project-coupled
content; combined with prior PRs #229, #251, and the config/README work, the
skill is now fully public-release-ready for the `coding` plugin.

## v1.7.0 — 2026-06-19 (structured evals + duplicate version key fix)

Added `evals/evals.json` — the skill's first machine-runnable eval suite
(five cases covering the core supervisor loop behaviors):

- **eval 1** `warm-start-routine-edit-approval`: prerequisites check, lockfile
  write, loop start, auto-approval of 'Would you like to make the following
  edits?' via 'a Enter', cold-start cadence (60s) → active (240s).
- **eval 2** `refusal-list-escalation-force-push`: detects 'git push --force'
  to main, refuses to approve, fires PushNotification, appends notable_event,
  pauses the loop.
- **eval 3** `morning-summary`: reads lockfile notable_events, loads
  morning-summary.md format, produces mobile-friendly counts-first report.
- **eval 4** `cold-start-detection-and-handoff`: no manager pane found,
  confirms with user, hands off to sprint-manager skill, polls until alive.
- **eval 5** `idle-cadence-transition`: tracks two consecutive 'Goal achieved'
  cycles, transitions current_phase to idle, picks delaySeconds=1800 (avoids
  the 300s worst-of-both trap).

Also collapses the duplicate `version: 1.5.0 / version: 1.6.0` key in
SKILL.md (YAML last-key-wins; this makes the effective version explicit).

## v1.5.0 — 2026-06-19

Cross-platform tmux compatibility gate (#163).

### Added

- `scripts/tmux-preflight.sh` — probes `tmux -V`, normalizes the version, and
  compares against `MIN_TMUX_VERSION` (3.2). Soft-gates instead of failing loud:
  exit 0 supported, 4 present-but-old (warn + continue), 3 absent (install
  guidance). Sourceable for unit tests (`parse_tmux_version`, `version_ge`,
  `run_preflight`; test seams `TMUX_VERSION_OVERRIDE` / `TMUX_BIN`).
- `tests/test-tmux-preflight.sh` — covers version parsing, comparison, and all
  three exit codes.

### Changed

- `scripts/grid-scan.sh` now sources the preflight and gates before scanning, so
  a missing/old tmux yields one actionable message instead of confusing empty
  output.
- `SKILL.md` Compatibility section documents the preflight, adds verified-version
  rows for old/absent tmux, and makes the "gate behind a version check" rule
  mechanical rather than advisory.
## v1.6.0 — 2026-06-19

Mobile cold-start: ship the dispatch watcher (#160). (Stacks above the #163
tmux-preflight work at v1.5.0.)

### Added

- **`scripts/sprint-dispatch-watcher.sh`** — the PC-side half of mobile
  cold-start that `dispatch-patterns.md` §2 committed to but had only deferred
  as "a small follow-up." Polls a dispatch folder, **atomically claims** a fresh
  dispatch (`mv` into `claimed/`, so a double-fire launches one manager, never
  two), gates **stale** dispatches (`requested_at` older than
  `SPRINT_SUPERVISOR_MAX_AGE_SECONDS`, default 3600), validates `action:
  cold-start`, writes a `status/<scope>.status.json` the phone polls, and hands
  the actual launch to a pluggable `--exec` wrapper (prints the bootstrap line
  with no `--exec`). Portable (bash 3.2 / BSD+GNU date), fail-soft, sourceable
  for tests.
- **`tests/test-sprint-dispatch-watcher.sh`** — JSON field extraction, staleness
  gating, atomic claim, status write-back, invalid-action rejection, and the
  no-double-launch guard.

### Changed

- **`references/dispatch-patterns.md`** §2 — documents the shipped watcher
  (usage, guarantees, test seams) and updates the #160 status: the watcher is
  now implemented + tested; what remains is Tony's signal-transport choice and a
  single live phone→PC run (depends on his home setup, not the repo).

## v1.4.0 — 2026-06-16

Public release readiness — genericization + configurable rubric (epic #164).

Decision: **abstract-and-release via a split** — a project-agnostic
`tmux-agent-supervisor` core plus a configurable extension, rather than keeping
the skill private. See `references/release-decision.md` for the full ADR.

### Added

- **`references/supervisor-config.example.yaml`** — externalizes the refusal
  list, approval-rubric extensions, and project labels (repo groups, PR citation
  format, protected branches, trusted hosts) into a config file. Ships
  conservative generic defaults plus a commented, illustrative wrfcoin-flavored
  example block. Config lookup order:
  `$SPRINT_SUPERVISOR_CONFIG` → `~/.claude/sprint-supervisor-config.yaml` →
  bundled example.
- **`README.md`** — public-facing README: what the skill does, the
  watchdog-vs-skill split, lockfile coordination, the ~240s cadence reasoning
  (sub-300s keeps the prompt cache warm), how to configure, and a
  cold-start → supervise → morning-summary quickstart.
- **`references/release-decision.md`** — ADR recording the keep-private vs
  abstract vs split options, the chosen split, consequences, the migration
  checklist, and remaining optional work (demo recording, final public-name
  decision, reference-doc genericization, watchdog packaging).
- **`## Configuration`** section in `SKILL.md` — documents the config lookup
  order, what the config controls, and the safe-defaults fallback.

### Changed

- **Version bump 1.3.1 → 1.4.0.**
- **`SKILL.md` genericized (surgical edits only):** description frontmatter and
  prose no longer say "WRFCoin"; triggers preserved verbatim so invocation is
  unchanged. Hardcoded project paths/hosts/labels replaced with placeholders
  (`<repo>`, `~/work/<project>`, `<host>`) and config references. The refusal
  list and approval rubric keep a built-in conservative baseline and now read
  project-specific extensions from config. Morning-summary repo groups and PR
  citation format are config-driven. Scope examples use neutral names
  (`group-a/b/c`).

### Known remaining work (not blocking release; tracked on the PR / epic #164)

- Demo recording (cold-start → supervise → morning summary) — epic #164 stays open.
- Final public-name decision (`sprint-supervisor` vs `tmux-agent-supervisor`).
- Genericize prose in `references/*.md` worked examples (still
  project-flavored; illustrative only).
- Package `sprint-watchdog.sh` and source its sessions/paths from the same config.

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
