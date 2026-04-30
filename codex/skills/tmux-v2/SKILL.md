---
name: tmux-v2
description: Launch, probe, steer, and revive WRFCoin persona agents in a tmux grid from Codex. Use when the user wants a 2x3 persona dashboard, a mixed Claude and Codex pane layout, `tmux send-keys` steering, pane liveness checks, or recovery from a dead `codex resume` or idle bash pane.
---

# tmux-v2

Use this skill for two related jobs:

1. Launch an interactive tmux persona grid that leaves the agents idle and ready for live steering.
2. Drive an existing grid with preflight checks, assignment dispatch, and pane restart helpers.

## Default topology

For the WRFCoin six-persona layout, keep the grid in its own tmux session:

- session: `sprint`
- window: `sprint`
- panes: Alice, Bob, Cindy on the top row; Dan, Elsa, Frank on the bottom row

The launcher writes the active tmux target to `/home/tony/wrfcoin/.sprint-target`. Always use that breadcrumb instead of guessing the session or window name.

## Launch the interactive 2x3 grid

Run:

```bash
bash /home/tony/.codex/skills/tmux-v2/scripts/launch-interactive-grid.sh --replace
bash /home/tony/.codex/skills/tmux-v2/scripts/open-grid-window.sh
```

Default visible launch when the user wants to watch the session live:

```bash
bash /home/tony/.codex/skills/tmux-v2/scripts/launch-interactive-grid.sh --replace --open-window
```

What it does:

- creates a detached `sprint` tmux session
- builds the explicit 2x3 pane grid
- starts an interactive Claude or Codex CLI in each pane
- writes `/home/tony/wrfcoin/.sprint-target`

Implementation note:

- Even with `--open-window`, the launcher still starts tmux first and only opens the observer window after the tmux session exists.
- Use `open-grid-window.sh` when the user explicitly wants the two steps run separately.

The default persona mix lives in `~/.codex/memories/tmux-v2/personas.json`. The first run seeds that file from the bundled default asset. Edit it to change models, runtimes, work directories, or pane order.

## Probe pane state

Use:

```bash
bash /home/tony/.codex/skills/tmux-v2/scripts/preflight.sh
bash /home/tony/.codex/skills/tmux-v2/scripts/preflight.sh --json
bash /home/tony/.codex/skills/tmux-v2/scripts/preflight.sh --persona frank
bash /home/tony/.codex/skills/tmux-v2/scripts/capture-pane.sh --persona alice
```

Read `references/pane-state-machine.md` when you need the full classification details.

## Nudge and check in

Use these helpers for safe in-band steering:

```bash
bash /home/tony/.codex/skills/tmux-v2/scripts/nudge-pane.sh \
  --persona alice \
  --message "Manager check-in: reply with current task, current file/path, and blocker or none."

bash /home/tony/.codex/skills/tmux-v2/scripts/check-in-all.sh

bash /home/tony/.codex/skills/tmux-v2/scripts/advance-pane.sh --persona dan
```

Rules:

- Prefer `check-in-all.sh` or `nudge-pane.sh` over raw `tmux send-keys`.
- Keep nudges to one short line.
- Use `advance-pane.sh` only for local pane flow control such as submitting a staged prompt or moving past a non-destructive in-pane choice.
- Do not use `advance-pane.sh` to auto-approve high-impact actions that should still be surfaced to the user.

Recommended reusable approvals for future users:

- `["bash", "/home/tony/.codex/skills/tmux-v2/scripts/preflight.sh"]`
- `["bash", "/home/tony/.codex/skills/tmux-v2/scripts/capture-pane.sh"]`
- `["bash", "/home/tony/.codex/skills/tmux-v2/scripts/nudge-pane.sh"]`
- `["bash", "/home/tony/.codex/skills/tmux-v2/scripts/check-in-all.sh"]`
- `["bash", "/home/tony/.codex/skills/tmux-v2/scripts/advance-pane.sh"]`

## Dispatch assignment files

Use:

```bash
bash /home/tony/.codex/skills/tmux-v2/scripts/dispatch.sh \
  --round 53 \
  --manager codex \
  --to alice --assignment sprint-alice.md \
  --to dan --assignment sprint-dan.md
```

Rules:

- Dispatch only short one-line instructions through `send-keys`.
- Point each pane at a markdown assignment file under `/home/tony/wrfcoin/docs/plans/`.
- Let `dispatch.sh` perform preflight first unless the user explicitly wants `--force`.

## Revive a dead pane

Use:

```bash
bash /home/tony/.codex/skills/tmux-v2/scripts/restart.sh frank
bash /home/tony/.codex/skills/tmux-v2/scripts/restart.sh --persona bob
```

`restart.sh` uses the persona config to relaunch the correct runtime, model, effort, and working directory for either Claude or Codex panes.

## References

- Read `references/codex-handling.md` before troubleshooting Codex pane behavior.
- Read `references/persona-config.md` before editing the persona JSON.

## Implementation note (for this public repo)

The supporting `scripts/`, `agents/`, `assets/`, and `references/` folders referenced above live in the working WRFCoin workspace and are not yet included in this v0.2 publish. The SKILL.md (this file) is the contract; the implementation is shipped incrementally. The Claude-side counterpart at [`../../claude/skills/tmux-sprint/SKILL.md`](../../claude/skills/tmux-sprint/SKILL.md) describes the same protocol from the Claude perspective.
