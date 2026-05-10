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

The launcher writes the active tmux target to `<workspace>/.sprint-target`. Always use that breadcrumb instead of guessing the session or window name.

## Launch the interactive 2x3 grid

Run:

```bash
bash ~/.codex/skills/tmux-v2/scripts/launch-interactive-grid.sh --replace
bash ~/.codex/skills/tmux-v2/scripts/open-grid-window.sh
```

Default visible launch as the user always wants to watch the session live:

```bash
bash ~/.codex/skills/tmux-v2/scripts/launch-interactive-grid.sh --replace --open-window
```

What it does:

- creates a detached `sprint` tmux session
- builds the explicit 2x3 pane grid
- starts an interactive Claude or Codex CLI in each pane
- writes `<workspace>/.sprint-target`

Implementation note:

- Even with `--open-window`, the launcher still starts tmux first and only opens the observer window after the tmux session exists.
- Use `open-grid-window.sh` when the user explicitly wants the two steps run separately.

The default persona mix lives in `~/.codex/memories/tmux-v2/personas.json`. The first run seeds that file from the bundled default asset. Edit it to change models, runtimes, work directories, or pane order.

## Probe pane state

Use:

```bash
bash ~/.codex/skills/tmux-v2/scripts/preflight.sh
bash ~/.codex/skills/tmux-v2/scripts/preflight.sh --json
bash ~/.codex/skills/tmux-v2/scripts/preflight.sh --persona frank
bash ~/.codex/skills/tmux-v2/scripts/capture-pane.sh --persona alice
```

Read `references/pane-state-machine.md` when you need the full classification details.

## Nudge and check in

Use these helpers for safe in-band steering:

```bash
bash ~/.codex/skills/tmux-v2/scripts/nudge-pane.sh \
  --persona alice \
  --message "Manager check-in: reply with current task, current file/path, and blocker or none."

bash ~/.codex/skills/tmux-v2/scripts/check-in-all.sh

bash ~/.codex/skills/tmux-v2/scripts/advance-pane.sh --persona dan
```

Rules:

- Prefer `check-in-all.sh` or `nudge-pane.sh` over raw `tmux send-keys`.
- Keep nudges to one short line.
- Use `advance-pane.sh` only for local pane flow control such as submitting a staged prompt or moving past a non-destructive in-pane choice.
- Do not use `advance-pane.sh` to auto-approve high-impact actions that should still be surfaced to the user.

Recommended reusable approvals for future users:

- `["bash", "~/.codex/skills/tmux-v2/scripts/preflight.sh"]`
- `["bash", "~/.codex/skills/tmux-v2/scripts/capture-pane.sh"]`
- `["bash", "~/.codex/skills/tmux-v2/scripts/nudge-pane.sh"]`
- `["bash", "~/.codex/skills/tmux-v2/scripts/check-in-all.sh"]`
- `["bash", "~/.codex/skills/tmux-v2/scripts/advance-pane.sh"]`

## Dispatch assignment files

Use:

```bash
bash ~/.codex/skills/tmux-v2/scripts/dispatch.sh \
  --round 53 \
  --manager codex \
  --to alice --assignment sprint-alice.md \
  --to dan --assignment sprint-dan.md
```

Rules:

- Dispatch only short one-line instructions through `send-keys`.
- Point each pane at a markdown assignment file under `<workspace>/docs/plans/`.
- Let `dispatch.sh` perform preflight first unless the user explicitly wants `--force`.
- For any agent that will edit files, create a per-agent git worktree before
  dispatch. Never send two agents into the same mutable checkout. Use a naming
  pattern like `/tmp/<repo>-alice-r1-idea-incubator` and a branch pattern like
  `sprint/alice-r1-idea-incubator`.
- Send `/rename <agent>_r<round>_<topic>` to each pane so `/resume` and later
  reviews show who did what. Examples: `alice_r1_idea-incubator`,
  `bob_r4_sheet-music`.
- If the runtime is Claude and the API/login state is touchy, wait about five
  seconds between `/rename`, `/new`, and handoff sends.

## Worktree isolation

The sprint manager owns worktree setup. Agents should receive an explicit
working directory and should be told not to run branch-changing, index-writing,
commit, or PR commands from the shared repo checkout.

For portable tmux-sprint work, use the public helper when available:

```bash
bash /mnt/c/Users/Tony/Documents/GitHub/tmux-sprint/scripts/prepare-agent-worktree.sh \
  --repo /mnt/c/Users/Tony/Documents/GitHub/claude-skills \
  --agent alice \
  --round 1 \
  --topic idea-incubator \
  --base main \
  --root /tmp
```

The helper prints `worktree=`, `branch=`, and `conversation=` values that belong
in the handoff.

## Revive a dead pane

Use:

```bash
bash ~/.codex/skills/tmux-v2/scripts/restart.sh frank
bash ~/.codex/skills/tmux-v2/scripts/restart.sh --persona bob
```

`restart.sh` uses the persona config to relaunch the correct runtime, model, effort, and working directory for either Claude or Codex panes.

## TwinGrid + Partner Peek round mode

A reusable round mode that pairs every lane with a twin runtime (Claude **A**
vs Codex **B**), runs a blind A/B pass, then a structured Partner Peek pass.
Use whenever the user says "TwinGrid", "blind A/B round", "partner peek
round", "twin run", or "A/B-then-peek".

Phases (Codex-side view):

1. Blind dispatch via `dispatch.sh` using the per-pane handoff from
   `docs/twingrid/blind-handoff-template.md` (in the repo root, not under
   the skill folder).
2. Each pane writes to `/tmp/twingrid-r<N>-<runtime>-<lane>-<slug>/` and
   finishes with an agent record matching
   `docs/twingrid/agent-record.schema.yaml`.
3. Manager writes the shared `/tmp/twingrid-r<N>-partner-peek.md` reveal
   brief, then dispatches `docs/twingrid/partner-peek-handoff-template.md`.
4. Manager runs `scripts/twingrid/twingrid-lane-matrix.sh --round N` for
   the matrix and `scripts/twingrid/twingrid-detect-blocked.sh` for block
   detection.

Manager-owned vs agent-owned data: the manager scrapes elapsed time,
context remaining, usage remaining, and blocked state from tmux/the
statusline. Agents must not self-report those fields. Agents own artifacts,
validations, partner-idea adoption, and skill-improvement recommendations.

Supports both content-generation rounds and skill-development rounds. See
`docs/twingrid/README.md` for the contract, schemas, and Round 7 provenance.

## References

- Read `references/codex-handling.md` before troubleshooting Codex pane behavior.
- Read `references/persona-config.md` before editing the persona JSON.
- Read `docs/twingrid/README.md` for the TwinGrid + Partner Peek round mode.

## Implementation note (for this public repo)

The supporting `scripts/`, `agents/`, `assets/`, and `references/` folders referenced above live in the working WRFCoin workspace and are not yet included in this v0.2 publish. The SKILL.md (this file) is the contract; the implementation is shipped incrementally. The Claude-side counterpart at [`../../claude/skills/tmux-sprint/SKILL.md`](../../claude/skills/tmux-sprint/SKILL.md) describes the same protocol from the Claude perspective.
