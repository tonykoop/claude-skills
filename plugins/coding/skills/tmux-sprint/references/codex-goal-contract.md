# Codex /goal — sprint integration contract

> Design contract for incorporating Codex CLI `/goal` into tmux-sprint
> dispatch. Covers when to use it, startup sequence, goal shape, both sprint
> profiles, and recovery. See issue #117.

## What `/goal` does

`/goal` is an experimental Codex CLI feature for durable objectives that
persist across turns. The agent checks its goal state on each turn and keeps
working until the stopping condition is met.

Enable per-session with `/experimental` or globally in `~/.codex/config.toml`:

```toml
[features]
goals = true
```

Key commands:

| Command              | Effect                                       |
|----------------------|----------------------------------------------|
| `/goal <objective>`  | Set goal (replaces any existing goal)        |
| `/goal`              | Check current goal status and progress       |
| `/goal pause`        | Pause autonomous goal pursuit                |
| `/goal resume`       | Resume after pause or manager intervention   |
| `/goal clear`        | Remove goal entirely                         |

## When to use `/goal` vs not

**Use `/goal` when:**
- The lane has one well-scoped objective with a verifiable stopping condition.
- The task spans multiple turns (e.g. implement → test → PR → iterate).
- The manager will be AFK or asleep and cannot send turn-by-turn nudges.
- The task is a WRFCOIN dev sprint lane or a long-running personal-project
  implementation lane.

**Do NOT use `/goal` when:**
- The task is bounded and fits in one turn (e.g. "write a script", "run tests").
- The pane is a Claude pane — `/goal` is a Codex-specific command.
- The objective is ambiguous or spans unrelated backlog items.
- A round-by-round manager hand-off is already providing the rhythm.

## Startup sequence for a Codex goal lane

The correct order for each Codex pane before sending the full handoff:

```
1. /rename r<N>-<persona>-<slug>           # aligns pane label with assignment
2. /goal Complete <lane objective> without stopping until <verifiable end state>.
3. Round <N>: read <path> and execute. This file is a contract — do not edit it.
```

Steps 2 and 3 are both sent via `dispatch.sh`. Pass `--goal <text>` to inject
step 2 before the assignment one-liner for each Codex pane in the batch.
`/rename` remains a manual manager step (pre-dispatch) because it needs to
happen before the pane accepts the automated send.

The assignment file should still include a Plan-first gate (see SKILL.md
§ "Phase 0: Plan-first dispatch") so the goal does not bypass manager review
before implementation begins.

## Goal shape guidelines

A well-formed goal contains:

| Field                  | Example                                                       |
|------------------------|---------------------------------------------------------------|
| One objective          | "Implement the WRF-20 transfer fee burn in the validator crate" |
| Stopping condition     | "until tests pass and a PR is open"                           |
| Starting reads         | "read docs/plans/r12-dan.md and the linked issue first"       |
| Progress proof         | "each checkpoint: run `cargo test -p validator` and report"  |
| Scope boundary         | "do not touch the consensus module"                           |
| Pause point            | "pause before merging and wait for manager review"            |

Full template:

```
Complete <objective> without stopping until <stopping condition>. Read
<handoff path> and the linked issue first. Checkpoints: <what to run/report>.
Do not touch <out-of-scope areas>. Pause before <gate> and wait for manager
review.
```

## Sprint profile templates

### WRFCoin dev sprint (wrfcoin repo)

```
Complete <lane objective> without stopping until tests pass and a draft PR is
open. Read docs/plans/r<N>-<persona>-<slug>.md and the linked issue first.
At each checkpoint run `cargo test -p <crate>` and append a one-line note to
tmp/goal-progress-<persona>.md. Do not touch the consensus or governance
modules unless the issue explicitly requires it. Pause before opening a
non-draft PR or merging — wait for manager review.
```

### Personal GitHub project sprint (Documents/GitHub)

```
Complete <lane objective> without stopping until the implementation is done
and a PR is open. Read <handoff path> first. At each checkpoint run the
project's test suite and append a one-line note to /tmp/goal-progress-<persona>.md.
Do not modify files outside the assigned skill or plugin directory. Pause
before merge or any destructive file operation — wait for manager review.
```

## dispatch.sh --goal integration

`dispatch.sh` accepts an optional `--goal <text>` flag. When set, each Codex
pane in the batch receives `/goal <text>` + C-m before the assignment one-liner.
Claude panes are unaffected (the flag is silently skipped for non-codex
runtimes).

```bash
dispatch.sh --round 12 --goal "Complete the WRF-20 burn mechanic without stopping until tests pass and a draft PR is open" \
  --to dan  --assignment ws/docs/plans/r12-dan.md \
  --to elsa --assignment ws/docs/plans/r12-elsa.md
```

The goal text appears in the round JSON record under `goal` for traceability.

## Manager inspection and recovery

During a sprint or after waking up:

```bash
# Check current goal status in a pane
tmux send-keys -t sprint:sprint.3 -l "/goal" ; tmux send-keys -t sprint:sprint.3 C-m

# Pause if the pane is heading in the wrong direction
tmux send-keys -t sprint:sprint.3 -l "/goal pause" ; tmux send-keys -t sprint:sprint.3 C-m

# Resume after reviewing and sending corrective notes
tmux send-keys -t sprint:sprint.3 -l "/goal resume" ; tmux send-keys -t sprint:sprint.3 C-m

# Clear entirely before reassigning
tmux send-keys -t sprint:sprint.3 -l "/goal clear" ; tmux send-keys -t sprint:sprint.3 C-m
```

sprint-supervisor should include `/goal` status in morning summaries for
goal-enabled panes (detect the goal status line in pane captures).

## Interaction with Plan-first gating

`/goal` does not bypass Plan-first. The handoff file should still include the
"Plan first" instruction. The goal sets the long-horizon objective; the
Plan-first gate enforces manager review before implementation. The usual
sequence:

1. Codex reads the handoff file, produces a plan.
2. Manager approves (presses Enter or sends a nudge).
3. Codex proceeds — now working toward the durable goal.
4. Codex pauses at the gate defined in the goal text (e.g. "before merge").
5. Manager reviews and either approves or clears/resets the goal.
