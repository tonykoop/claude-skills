# Claude side

The Claude-tier skills, slash commands, and hooks that run the sprint orchestrator. Personas Alice, Bob, Cindy on the Claude tier (Opus / Sonnet) interleave with Codex personas Dan, Elsa, Frank in the same sprint grid.

For multi-vendor context, see the [top-level README](../README.md).

---

## Layout

```
claude/
├── skills/
│   ├── merge-review/       DAILY DRIVER — review PR against linked issue, codex-review-gated merge.
│   ├── sprint-update/      DAILY DRIVER — sprint-doc maintenance + auto-generated themed dispatch prompts.
│   ├── tmux-sprint/        Persona-grid driver (preflight, dispatch, restart).
│   └── disk-cleanup/       Weekly recovery: cargo, worktrees, npm/pnpm, optional Docker, WSL VHD shrink prompt.
├── commands/
│   ├── pull-all.md + .sh   Pull 20 repos + update 26 persona worktrees with state-aware safety.
│   └── deploy-node.md + .sh  Testnet node deploy to N5 Pro Proxmox CT + local desktop.
└── hooks/
    ├── sprint-doc-lock.sh    PreToolUse — claim advisory lock on sprint doc.
    └── sprint-doc-unlock.sh  PostToolUse — release lock if owned by current process.
```

`merge-review` and `sprint-update` are the highest-volume skills — together they're the loop that converts agent dispatches into merged commits and a current sprint-doc reflecting reality. See the top-level [README "How a typical day flows through this system"](../README.md#how-a-typical-day-flows-through-this-system) for the full picture.

---

## Installation

These files target [Claude Code](https://docs.claude.com/claude-code) at the project level. Drop them into a project's `.claude/` directory:

```bash
# In the root of your target project (e.g. ~/wrfcoin/):
cp -r path/to/agent-orchestration/claude/skills    .claude/skills
cp -r path/to/agent-orchestration/claude/commands  .claude/commands
cp -r path/to/agent-orchestration/claude/hooks     .claude/hooks
```

For the hooks to fire, register them in `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [{"type": "command", "command": ".claude/hooks/sprint-doc-lock.sh"}]
    }],
    "PostToolUse": [{
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [{"type": "command", "command": ".claude/hooks/sprint-doc-unlock.sh"}]
    }]
  }
}
```

---

## What's published vs. what's local

Some content stays local to the wrfcoin workspace and is **not** copied into this repo:

- `~/.claude/projects/*/tmux-v2/personas.json` (per-machine persona definitions)
- `~/.claude/projects/*/tmux-v2/rounds/*.json` (sprint round-state — runtime artifact)
- `auth.json`, `oauth_creds.json`, session caches, telemetry — already excluded by the repo's `.gitignore`

The skills and commands here read those local files but don't ship them. To use the skills, you'll need to populate your own `personas.json` (the `tmux-sprint` skill auto-creates a default on first run).
