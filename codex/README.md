# Codex side

Codex-tier skills for personas running on `gpt-5.4` and `gpt-5.3-codex`. In a typical sprint, personas Dan, Elsa, and Frank live on the Codex tier and interleave with Claude-tier personas Alice, Bob, Cindy in the same tmux grid.

The Codex side mirrors the Claude side at the protocol level: same persona names, same handoff format, same `sprint.md` source of truth, same review-gated merge. Skills here are written for the [Codex CLI](https://github.com/openai/codex) and live in `~/.codex/skills/` on the working machine.

For multi-vendor context, see the [top-level README](../README.md). For the Claude side, see [`../claude/`](../claude/).

---

## Layout

```
codex/
└── skills/
    └── gh-fix-ci/                Plan + fix failing GitHub Actions PR checks (vendor-portable; no wrfcoin assumptions).
```

> Retired 2026-06-15 (no-loose-skills consolidation): `tmux-v2`, `merge-manager`,
> and `wrfcoin-sprint-dispatch` were removed — they are superseded by the
> `coding` plugin's `tmux-sprint`, `merge-review`, and
> `sprint-supervisor`/`sprint-update`/`tmux-sprint`, which the coding plugin's
> `.codex-plugin` already serves to the Codex runtime.

---

## Skills published in v0.2

| Skill | Role |
|---|---|
| [`gh-fix-ci`](skills/gh-fix-ci/SKILL.md) | Inspect failing PR checks via `gh`, fetch GitHub Actions logs, summarize failures, propose a fix plan, and implement after approval. Vendor-portable. |

---

## Skills forthcoming in v0.3

The full Codex skill set on the working machine has 13 skills. The 4 above are the highest-leverage ones for understanding the system. The remaining 8 wrfcoin-specific skills (`wrfcoin-agent-teams`, `wrfcoin-heal`, `wrfcoin-launch-contract-review`, `wrfcoin-launch-personas`, `wrfcoin-merge-review`, `wrfcoin-persona-handoff`, `wrfcoin-sprint-planner`, `wrfcoin-sprint-update`, `wrfcoin-testnet-tdd`) and 1 generic skill (`pdf`) will land in subsequent commits.

The [Claude side](../claude/) has the parallel skill set — many capabilities exist in both vendor implementations.

---

## Codex configuration

The skills here run inside [Codex CLI](https://github.com/openai/codex). Codex reads:

- `~/.codex/skills/<skill-name>/SKILL.md` for skill definitions
- `~/.codex/rules/default.rules` for project-context rules (Codex's CLAUDE.md equivalent)
- `~/.codex/memories/<topic>/<file>.md` for persistent memory across sessions

A sanitized `default.rules.example` and a sample memory file will land in v0.3.

---

## Why a separate Codex skill set

Two reasons:

1. **Codex pane behavior is different.** A Codex pane that exits to "resume session" requires a specific revival sequence (`C-c C-c`, wait for bash, run `codex`); a Claude pane just needs a fresh `claude` invocation. Codex panes also share a backend that rate-limits at ~10s spacing, while Claude panes can interleave at 2s. The skill files codify these vendor-specific quirks so the manager doesn't have to remember them.
2. **Tier mixing is the point.** Most sprints run hybrid teams — Alice/Bob/Cindy on Claude, Dan/Elsa/Frank on Codex — and the manager dispatches to all of them through one common assignment-file contract. Maintaining parallel skill suites keeps the protocol vendor-neutral while honoring each vendor's specific quirks.
