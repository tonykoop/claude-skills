# agent-orchestration

> *Multi-vendor agentic infrastructure for a 7-repo blockchain project.*
> *Sprint manager + persona dispatch + automated PR review across Claude, Codex, and Gemini.*

![Sprint mid-flight — two monitors deep into an 8-hour sprint, with a candy assist](images/20260323_004011.jpg)

This repository is the actual agentic infrastructure that runs day-to-day development for the [WRFCoin](https://github.com/wrfcoin) project — skills, slash commands, hooks, and config files used to coordinate parallel AI agents across 7 repositories of Rust + TypeScript code.

It is not a hypothetical framework or a redacted portfolio piece. The skills below have shipped 206 commits, +100K / −5K lines across 1,107 files in a 23-day measurement window, with a 96% outcome-success rate validated by [Anthropic's Claude Code Insights](https://www.anthropic.com/news/claude-code) auto-generated usage report.

---

## What this is, in one paragraph

A sprint manager (the human, plus a Claude or Codex agent in a manager pane) coordinates up to seven named persona agents — Alice, Bob, Cindy, Dan, Elsa, Frank, Gina — running in a tmux grid. Personas can be Claude (Opus, Sonnet) or Codex (gpt-5.4, gpt-5.3) or a hybrid mix in the same sprint. Each persona owns a semi-permanent git worktree, opens draft PRs first with attached decision history, dispatches sub-agents in parallel for sub-tasks, and submits work for an automated `merge-review` step that gates on Codex auto-review for codex-enabled repos. State lives on disk: a `sprint.md` file as the source of truth, GitHub issues + PRs as the merge ledger, structured JSON per round under `~/.claude/projects/`. Concurrency on the sprint doc is enforced by a pair of PreToolUse / PostToolUse hooks. Skills, commands, and hooks are version-controlled in this repo.

---

## Validated metrics

From [Anthropic's Claude Code Insights](https://www.anthropic.com/news/claude-code) report covering **2026-03-17 through 2026-04-17** (23 days):

| Metric | Value |
|---|---|
| Messages | 1,393 across 204 sessions |
| Cumulative session time | 830 hours |
| Lines changed | +100,812 / −5,630 |
| Files touched | 1,107 |
| Commits | 206 |
| Outcome-success rate | 96% (58 fully + 24 mostly achieved out of 85) |
| Multi-claude (overlapping parallel sessions) | 56% of all messages |
| PRs merged in a single session (peak) | 18 in one 8-hour session |
| Languages | Rust 1670 edits, Markdown 1559, TypeScript 636 |
| Tool calls | 8,674 Bash, 2,425 Read, 1,906 Edit, 491 Agent (sub-agent) |

The report's "At a Glance" opens with this assessment, generated automatically from session telemetry:

> *"Your sprint manager pattern is genuinely impressive — orchestrating multi-lane, multi-repo sprints with tmux persona agents (Alice, Bob, Frank) across 8+ hour sessions, merging 18 PRs in a single push, and closing all P0 consensus bugs in one coordinated sweep. The plan-then-execute handoff rhythm you've built (explore codebase → write plan doc → hand off for implementation) is paying off, especially on gnarly Rust work like nonce enforcement where you landed 803 passing tests after fixing 33 broken ones."*

See [`docs/metrics.md`](docs/metrics.md) for the full report breakdown.

---

## Three-vendor scope

This repo treats the AI tool stack as a coordination protocol, not a single-vendor lock-in. The same persona names, handoff format, merge-review semantics, and on-disk sprint state are mirrored across three agent vendors:

| Vendor | Role | Skills published here |
|---|---|---|
| **Claude** (Opus, Sonnet, Haiku) | Manager pane + persona agents on Claude-tier lanes; primary skill suite | [`claude/`](claude/) |
| **Codex** (gpt-5.4, gpt-5.3) | Persona agents on Codex-tier lanes (typically Dan, Elsa, Frank); parallel skill suite | [`codex/`](codex/) |
| **Gemini** | Specialized roles (currently `merge-manager`); third-vendor parity check on the protocol | *(in flight — landing in v0.3)* |

A single sprint can have ~30 agents working in parallel (7 personas × 3-5 sub-agents each) across the 7 wrfcoin repositories.

---

## Repository layout

```
agent-orchestration/
├── README.md                         (this file)
├── LICENSE                           (MIT)
├── docs/
│   ├── architecture.md               (system view: manager / personas / worktrees / state / hooks)
│   └── metrics.md                    (full Claude Code Insights breakdown)
├── claude/
│   ├── skills/
│   │   ├── merge-review/             (DAILY DRIVER — Codex-review-gated PR review, 7-point checklist, structured comment)
│   │   ├── sprint-update/            (DAILY DRIVER — per-persona queue mgmt + auto-generated themed dispatch prompts)
│   │   ├── tmux-sprint/              (persona dispatch, preflight probing, codex revival)
│   │   └── disk-cleanup/             (weekly cargo + worktree + Docker cleanup with --dry-run by default)
│   ├── commands/
│   │   ├── pull-all.md + .sh         (pull 20 repos + update 26 persona worktrees with state-aware safety)
│   │   └── deploy-node.md + .sh      (testnet node deploy to N5 Pro Proxmox CT + local desktop)
│   └── hooks/
│       ├── sprint-doc-lock.sh        (PreToolUse — claim advisory lock on sprint doc)
│       └── sprint-doc-unlock.sh      (PostToolUse — release lock)
├── codex/                            (4 of 13 codex-side skills published in v0.2)
│   ├── skills/tmux-v2/                Codex-side persona-grid driver
│   ├── skills/merge-manager/          Vendor-portable PR review + sprint coordination
│   ├── skills/wrfcoin-sprint-dispatch/ "Resume sprint" workflow tying everything together
│   └── skills/gh-fix-ci/              Vendor-portable CI failure triage
├── gemini/                           (in flight — landing in v0.3)
└── images/
    └── 00-hero-trolli.jpg            (sprint mid-flight)
```

This is **v0.2**. The Claude side is the most mature. The Codex side now ships 4 skills (the flagship `tmux-v2`, the vendor-portable `merge-manager` and `gh-fix-ci`, and the integrative `wrfcoin-sprint-dispatch`); 9 more are forthcoming. The Gemini directory is in active development and lands in v0.3.

---

## Personas

Personas are terminal-level orchestrators, not workers. Each persona spawns 3-5 sub-agents in parallel via the Agent tool to do the actual code editing. The persona's role is to coordinate, review sub-agent output, and commit.

| Persona | Default lane | Worktree |
|---|---|---|
| Alice | core4 (consensus / blockchain) | `worktrees/core4-alice/` |
| Bob | backend | `worktrees/backend-bob/` |
| Cindy | frontend | `worktrees/frontend-cindy/` |
| Dan | infra | `worktrees/infra-dan/` |
| Elsa | backend (second lane) | `worktrees/backend-elsa/` |
| Frank | core4 (second lane) | `worktrees/core4-frank/` |
| Gina | frontend (second lane) | `worktrees/frontend-gina/` |

Personas are stable across sprints. Their worktrees are semi-permanent — they don't get created or destroyed each sprint. This eliminates `git worktree add` churn, lets each persona keep build artifacts warm, and means a persona's branch state at the end of one sprint is the starting state for the next.

---

## How a typical day flows through this system

Most working days run through a tight loop that hits two skills more often than anything else:

```
   tmux-sprint dispatch   →   personas open draft PRs   →   merge-review on each PR
                                                                        ↓
                                              sprint-update reflects merges in the doc
                                                                        ↓
                                                        next dispatch (top of loop)
```

`merge-review` and `sprint-update` are the daily drivers. Everything else (`tmux-sprint`, `pull-all`, `deploy-node`, `disk-cleanup`) supports the periodic moments — sprint kickoff, weekly maintenance, deploys. The loop above is what makes a single 8-hour session ship 18 PRs in one push: every PR goes through the same review checklist, every merge updates the sprint doc the same way, and the next round of work falls out of the doc automatically.

## Skills, commands, and hooks

### Skills (Claude) — daily drivers

| Skill | Purpose |
|---|---|
| [`merge-review`](claude/skills/merge-review/SKILL.md) | **The PR-review-and-merge loop.** Reads the linked GitHub issue, gates on Codex auto-review (mandatory for codex-enabled repos: `core4`, `infra`, `frontend`, `backend`), runs a 7-point checklist (scope match, test coverage, CI status, code quality, implementation correctness, merge safety, codex-review verdict), posts a structured PR-review comment with explicit blockers / warnings / positives, and either merges (with closing comments on PR + issue) or requests changes. Knows the dependency-first merge order across the 7 wrfcoin repos. |
| [`sprint-update`](claude/skills/sprint-update/SKILL.md) | **Sprint-doc maintenance after every merge batch.** Moves merged items from `Active` to `Completed` per persona, promotes the next Queue item to Active, updates header counts and velocity table, and **auto-generates themed dispatch-prompt patterns** for every persona with queued work — sized at 2-3 issues per agent, grouped by repo + theme (not batch number), with revision rounds prepended for any changes-requested PRs. The dispatch prompts get regenerated each run so they always reflect current queue state. |

### Skills (Claude) — periodic / maintenance

| Skill | Purpose |
|---|---|
| [`tmux-sprint`](claude/skills/tmux-sprint/SKILL.md) | Persona-grid driver: `preflight` (structured pane state probe), `dispatch` (transactional fan-out with assignment-file-as-contract), `restart` (codex-aware session revival). Replaces fragile `tmux send-keys \| sleep 5 \| capture-pane` patterns with verified primitives. |
| [`disk-cleanup`](claude/skills/disk-cleanup/SKILL.md) | Weekly recovery: `cargo clean` per worktree, merged-branch cleanup, npm/pnpm cache prune, optional Docker prune, generates the WSL `Optimize-VHD` PowerShell command (does not run it — WSL can't shrink its own backing VHD while running). Default mode is `--dry-run`. |

More skills (`handoff`, `auto-manage`, `run-swarm`, `ci-triage`, `launch-lanes`, `launch-audit`, `heal`, `scaffold-hygiene`, `sprint-archive`, `sprint-planner`) are forthcoming.

### Slash commands (Claude project-level)

| Command | Purpose |
|---|---|
| [`/pull-all`](claude/commands/pull-all.md) | Pulls all 20 repos in the org, clones any missing, then updates 26 semi-permanent persona worktrees with a state-aware safety machine (detached HEAD → `origin/main`, on `main` → pull, on a feature branch → skip, dirty → skip). |
| [`/deploy-node`](claude/commands/deploy-node.md) | Deploys latest code to the WRFCoin testnet — N5 Pro Proxmox CT and the local desktop node. Supports `--target n5\|desktop\|both`, `--pull-only`, `--skip-build`, `--restart`, `--status`. |

More commands (`commit`, `prime`, `next`, `five`, `dump`, `rust-check`, `security-scan`, `start-microservices`, `start-mobile`, `start-testnet`, `startdev`, `status`, `check-services`) are forthcoming.

### Hooks

| Hook | Event | Purpose |
|---|---|---|
| [`sprint-doc-lock.sh`](claude/hooks/sprint-doc-lock.sh) | PreToolUse on Edit / Write / MultiEdit | Claims an advisory lock on the active sprint doc. Blocks concurrent agent updates from racing on the same file. Stale-holder detection (looks at `/proc/$pid`) reclaims the lock if a holder process died without releasing. |
| [`sprint-doc-unlock.sh`](claude/hooks/sprint-doc-unlock.sh) | PostToolUse on Edit / Write / MultiEdit | Releases the lock if and only if the current process owns it. Always exits 0 — unlock is best-effort and must not block tool-call completion. |

These two hooks are small (~80 lines combined) but represent something important: real concurrency awareness. When you're running 7 personas in parallel and one of them updates the sprint doc while another is also editing it, the lock prevents lost writes. Stale locks are reclaimed automatically. This is the kind of detail that distinguishes "I use AI" from "I built infrastructure for AI."

---

## Provenance

This system was designed and operated by Tony Koop ([@tonykoop](https://github.com/tonykoop)) during development of the [WRFCoin](https://github.com/wrfcoin) testnet — a 7-repo Rust + TypeScript blockchain project building toward a mid-2026 public testnet launch. The skills published here are the working production versions used to ship that codebase.

References to specific persona worktree paths, the N5 Pro Proxmox CT, the codex-enabled-repo list, and individual sprint round / PR numbers are kept intact rather than redacted to placeholders. The wrfcoin context is the proof these workflows are real.

---

## License + status

MIT — see [LICENSE](LICENSE).

This is a **v0.1** snapshot of an actively-evolving system. Skills and commands are updated as the wrfcoin project ships new sprints; the skill files in this repo are periodic exports rather than a live mirror.

For the Claude Code platform features used here (skills, commands, hooks, MCP), see [Anthropic's Claude Code documentation](https://docs.claude.com/claude-code).
