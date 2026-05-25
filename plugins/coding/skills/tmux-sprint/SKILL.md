---
name: tmux-sprint
version: 2.3.1
last-updated: 2026-05-17
description: >-
  Transactional sprint-round dispatch, liveness probing, and codex-session
  revival for persona agents running in a tmux grid. Use whenever the user
  mentions tmux-sprint, round dispatch, preflight sprint panes, persona dispatch,
  restart a dead codex pane, frank pane is stuck at codex resume, dispatch a
  sprint round, TwinGrid blind A/B, Partner Peek reveal, send an assignment to
  alice/bob/cindy/dan/elsa/frank, or wants to reliably hand out per-persona
  assignment markdown files across a mixed claude+codex tmux sprint session.
  Includes label-aware sprint batching and smart model-picker routing for
  GitHub issue queues.
  Replaces fragile `tmux send-keys` patterns with structured primitives that
  verify submission, rate-limit by pane type, and persist round state across
  `/compact`.
---

# tmux-sprint — Sprint Driver

This skill drives an active tmux persona grid. A separate launch step
(typically a `launch-personas.sh` script) creates the grid; this skill
**dispatches work to it, probes pane state, and revives dead codex panes**.
Use these primitives instead of raw `tmux send-keys` whenever dispatching
persona work, especially when codex panes are involved or a previous
dispatch silently failed.

> **Provenance.** This SKILL.md was developed in the wrfcoin project as
> `tmux-v2` — the second-generation driver after an earlier `tmux-sprint`
> launch-side skill. The published name in this public repo collapses both
> back into a single skill called `tmux-sprint`, since outside the wrfcoin
> workspace the launch/drive split is an implementation detail.

## Clean two-session topology (REQUIRED — set up before launching personas)

**The flicker problem:** if the manager terminal and the personas grid live in
the **same tmux session**, every connected client locks onto the same active
window. Click between two terminal windows and they fight for which window is
shown — both terminals jump to whatever the other selected. Two sessions
(not two windows) fix this cleanly.

### Recommended layout

```
session "manager"   — 1 window, 1 pane: the sprint manager (Claude or codex)
                      attach from terminal #1
session "sprint"    — 1 window, 6 panes: Alice/Bob/Cindy on top row,
                                          Dan/Elsa/Frank on bottom row
                      attach from terminal #2
```

Each terminal has its own session, so clicking between them never re-orders
the other's window state. `send-keys -t sprint:0.<N> "..."` from the manager
session reaches persona pane N regardless of which session is "active" in
either terminal.

### One-time setup (do this BEFORE invoking the launch script)

From outside any tmux:

```bash
# Kill any stale sessions left from prior runs
tmux kill-server 2>/dev/null || true

# Create the manager session (this is where Claude Code runs)
tmux new-session -d -s manager -n manager
tmux send-keys -t manager:manager "claude" C-m   # or just leave it bash

# Create the personas session (empty for now — launch script populates it)
tmux new-session -d -s sprint -n sprint

# Pin remain-on-exit so a crashed agent doesn't vanish silently
tmux set-option -t sprint:sprint remain-on-exit on
```

Then in **terminal #1**:
```bash
tmux attach -t manager
```

And in **terminal #2** (separate window):
```bash
tmux attach -t sprint
```

Each terminal owns its own session. Clicking between the two windows is now
visually independent — the manager window doesn't follow the personas window
(or vice versa).

### Verifying the topology after launch

```bash
tmux list-sessions
# Expected:
#   manager: 1 windows (created ...)
#   sprint:  1 windows (created ...) [+ "sprint" window with 6 panes]

tmux list-clients
# Expected: each client attached to a DIFFERENT session
#   /dev/pts/0: manager  (terminal 1)
#   /dev/pts/2: sprint   (terminal 2)
```

If both clients show the same session, the flicker bug is back — kill one
and re-attach to the correct session.

### Cleanup at end of sprint

```bash
tmux kill-session -t sprint    # close personas
tmux kill-session -t manager   # close manager (or leave for next sprint)
```

Don't accumulate multiple `sprint`/`manager` sessions across days — stale
sessions show up in `tmux ls` output and cause confusion.

## Why this exists

A sprint manager dispatching to 6–8 personas in a tmux grid hits the same
failure modes repeatedly:

1. A codex pane exits to "resume session" — dispatched text lands in a dead
   buffer and the pane silently ignores it.
2. `tmux send-keys ... Enter` doesn't submit reliably on codex panes; `C-m`
   works but bash scripts often use the string `"Enter"`.
3. Rate-limiting is a convention ("20s between codex dispatches") that lives
   in human memory and gets violated under time pressure.
4. Persona A accidentally touches persona B's worktree because the dispatch
   didn't constrain scope.
5. A compacted manager pane loses in-flight round state and has to
   reconstruct "who did I dispatch what to" by eye.
6. Personas sometimes read the assignment file and then *edit* it instead of
   *executing* it — the file looks like a working doc, not a contract.

The three subcommands below are designed around these failures. Every one of
them writes structured state to disk so you can recover across `/compact`,
cross-session handoffs, and dual-manager setups.

## Subcommands

### `preflight` — structured pane probe

```
tmux-sprint preflight                 # probe all 6 panes
tmux-sprint preflight --pane 3        # probe one
tmux-sprint preflight --json          # JSON output for piping
```

Captures each pane and parses its output into a structured state record:

```
pane 0 alice claude-opus-4-6   IDLE     ctx=42%  worktree=core4-alice      [OK]
pane 1 bob   claude-haiku-4-5  WORKING  ctx=75%  worktree=backend-bob-651  [BUSY]
pane 2 cindy claude-sonnet-4-6 IDLE     ctx=63%  worktree=frontend-cindy   [OK]
pane 3 dan   codex-gpt-5.4     WORKING  5h=42%   weekly=24%                [BUSY]
pane 4 elsa  codex-gpt-5.4-m   IDLE     5h=21%   weekly=20%                [OK]
pane 5 frank codex-exited                                                   [DEAD]
```

Detection logic recognizes:

- **Claude live**: `Ctx:NN%`, model line (`[Opus 4.6 ...]`, `[Haiku 4.5]`,
  `[Sonnet 4.6]`), `❯` prompt, `✻`/`✢`/`●`/`·` tool indicators
- **Claude working**: `Cooked`/`Leavening`/`Galloping`/`thinking`/`Processing`
  sentinels plus elapsed time
- **Codex live**: `gpt-5.4` model line, `5h NN%`, `weekly NN%`
- **Codex working**: `• Working` / `◦ Booting` / `Spawned <name> [worker]`
- **Codex exited**: `To continue this session, run codex resume`
- **Codex update prompt**: `Update now (runs 'npm install -g @openai/codex')`
- **Dead bash**: no model line, just `<user>@<host>:~$` prompt
- **Blank**: compacted claude pane (empty tail with worktree footer still present)

Any state other than `IDLE` returns a `BUSY` or `DEAD` verdict. `dispatch`
refuses to send to non-`OK` targets unless `--force`.

### `dispatch` — transactional fan-out, assignment-file-only

```
tmux-sprint dispatch --round 53 --manager claude-opus-4-6 \
  --to alice --assignment <workspace>/docs/plans/2026-04-11-alice-round53.md \
  --to bob   --assignment <workspace>/docs/plans/2026-04-11-bob-round53.md \
  --to cindy --assignment <workspace>/docs/plans/2026-04-11-cindy-round53.md
```

**Every dispatch requires `--assignment <md-path>`.** There is no `--items`
inline option. This is deliberate: it forces traceable decision history and
kills the "persona thought the task was to update the handoff file"
pathology. The assignment is the contract; the dispatch prompt only points
at it.

#### What dispatch does, step by step

1. **Preflight first.** Internally calls `preflight`. If any target is `BUSY`
   or `DEAD`, abort and print who and why. User can override with `--force`.
2. **Validate each assignment file.** Must exist, must be under
   `<workspace>/docs/plans/`, must contain the preamble block from
   `assets/assignment-preamble.txt`. A missing preamble blocks dispatch —
   fix the file, rerun. This prevents dispatching to a handoff file that
   doesn't declare itself a read-only contract.
3. **Cancel copy-mode** on each target pane. `send-keys -X cancel` is a
   no-op if the pane isn't in copy-mode, so it's cheap to run
   unconditionally.
4. **Build the one-liner** for each pane, e.g.
   `Round 53: read <path> and execute. This file is a contract — do not
   edit it.`
5. **Send text, then `C-m`** — separate send-keys calls. Never pass the
   literal string `"Enter"`.
6. **Rate-limit by pane type.** Claude panes fire 2s apart and can
   interleave in parallel (different processes); codex panes are strictly
   sequential with 10s spacing (shared backend — 5s occasionally hit
   `overloaded_error`; 10s observed stable 2026-04-17).
7. **Verify submission — three-tier retry.** 3s after send, recapture the
   pane. If the prompt text appears OR a `Working`/`Processing`/tool-call
   indicator shows, mark success. If nothing: (a) retry with fresh `C-m`;
   (b) still nothing → full re-send (cancel copy-mode, re-send text,
   `C-m`, wait 2×verify) — this catches the post-`/clear` race observed
   2026-04-17 where Elsa's pane silently absorbed the initial send. Only
   after all three tiers fail is the dispatch marked `SILENT_FAIL` and
   logged with a ⚠️ marker so the manager sees it immediately.
8. **Persist round state.** Append the complete record to
   `~/.claude/projects/<project-slug>/tmux-v2/rounds/round-<N>.json`.
   The record survives manager-pane `/compact` and is readable by a second
   sprint manager (codex or claude).

#### Assignment file preamble (enforced)

Every `.md` file passed to `--assignment` must contain this block verbatim:

```
> EXECUTE the assignment. Do NOT edit this file — it is a read-only contract
> from the sprint manager. Report results in your tmux output and PR
> descriptions. If the assignment looks wrong, post a comment in this pane and
> STOP; do not silently redefine the task.
```

`scripts/dispatch.py` validates this with a literal substring match. The
block is in `assets/assignment-preamble.txt` — copy from there when writing
new assignment files.

### `restart` — codex-aware session revival

```
tmux-sprint restart frank
tmux-sprint restart --pane 5
```

Walks the state machine:

1. **Cancel any stuck copy-mode** on the target pane.
2. **Detect current state** via `preflight`:
   - `CODEX_EXITED` (at `codex resume` prompt): send `C-c` twice, wait for
     bash prompt, run `codex`
   - `CODEX_UPDATE_PROMPT`: send `2` + `C-m` to skip
   - `DEAD` (at bash prompt): run `codex`
   - `IDLE` (already live): no-op, report
   - `WORKING`: refuse unless `--force`
3. **Wait for the `OpenAI Codex (vX.Y)` banner** up to 15s
4. **Report** the new state

No user interaction needed unless the codex binary itself prompts for auth.

### Provider failover - budget-exhausted pane recovery

When a live pane is blocked by a provider-specific budget or rate-limit
condition, the manager should prefer a same-pane provider migration before
absorbing the lane into the manager context. The first implementation contract
lives in `references/provider-failover.md` and defines:

- the default fallback order: `codex -> claude -> gemini -> manager-absorb`
- the per-pane provider state fields that round records should persist
- the same-pane swap flow: interrupt, exit to shell, launch, probe, resume
- the prompt families that count as retryable exhaustion signals
- the morning-summary fields for migrated panes

The failover path deliberately reuses the existing `preflight`, `dispatch`,
and `restart` boundaries. Provider migration is a manager-owned recovery
operation; sprint-supervisor should only approve safe prompts by prompt shape
and escalate anything outside its rubric.

## TwinGrid mode - blind A/B plus Partner Peek

Use TwinGrid mode when the manager wants paired Claude/Codex lanes to solve
the same task independently, reveal partner outputs only after the blind pass,
and turn the combined result into a skill-improvement recommendation or PR.

TwinGrid is a manager-owned protocol layered on top of normal `preflight` and
`dispatch`; it can run content-generation rounds, skill-development rounds, or
mixed rounds. The manager owns metrics and orchestration. Agents must not
self-report elapsed time, context remaining, usage remaining, or pane status;
capture those from tmux/statusline telemetry instead.

### Phase 0: Plan-first dispatch

Use Plan-first dispatch for implementation rounds or any task that may create
repo changes. The assignment should say "Plan first" and the persona must
summarize intended files, tests, and PR scope before editing. The manager then
presses Enter or sends a short approval nudge. Only after that gate should the
persona create worktrees, edit files, commit, push, or open a PR.

For long instructions, write the full prompt to a file and dispatch a short
one-liner such as:

```text
Read /tmp/r9i-dan.md and execute. Plan first.
```

This avoids `tmux send-keys -l` hangs on large prompts while preserving a
readable contract file for recovery after `/compact`.

Rename each pane/session before dispatch when the runtime supports it:

```text
/rename <agent>_r<round>_<topic>
```

Examples: `dan_r9_twingrid-contracts`, `elsa_r9_yaybahar-rig`. This makes
`/resume`, pane recovery, PR review, and archive inspection line up with the
assignment. For Claude panes with touchy login/API state, wait a few seconds
between `/rename`, `/new`, and the handoff send.

### Smart batching and model picker notes

Batch dispatch by runtime and risk:

- Send short file-based prompts to all Claude panes in small groups when the
  panes are idle and the work is artifact-only.
- Send Codex panes sequentially with the existing rate limit, especially when
  the task involves edits, tests, network tools, or repo state.
- Give implementation, merge, review-gate, and ambiguous architecture work to
  the stronger available model; use lighter models for bounded artifact
  generation, transcription, simple matrix reads, and no-code validation.
- Keep blind A/B independence by recording the actual runtime/model in the
  handoff and agent record rather than changing expectations mid-round.
- If a pane is blocked on approval, auth, missing tools, or a long-running
  command, skip it in the next batch and let the manager recover it explicitly.

For GitHub-backed sprint queues, preserve issue labels as first-class routing
inputs. Read `references/label-aware-routing.md` before generating assignment
headers from issue labels, and use `scripts/plan-label-batches.sh` when you
have `gh issue list --json number,title,url,labels` output to convert labels
into batch groups, suggested models, and manager-review notes.

### Phase 1: blind dispatch

Use `references/twingrid-blind-handoff-template.md` to generate one assignment
per side/lane. The template requires:

- lane, side, runtime, task, and output folder
- named skill(s) to load
- isolated worktree/output-path guardrails
- no partner-output visibility
- a required agent record without self-reported runtime metrics

For content-generation rounds, the output folder can be under `/tmp`. For
skill-development rounds, each side must receive an assigned branch/worktree
and should open a draft PR only after concrete repo changes.

Before Partner Peek, each side must freeze the blind pass by writing
`ready_for_peek.json` in its own output folder. Use
`scripts/twingrid_contracts.py freeze` where possible:

```bash
python3 claude/skills/tmux-sprint/scripts/twingrid_contracts.py freeze \
  --round 9 \
  --lane elsa \
  --side A \
  --runtime gpt55-window-13 \
  --task "Yaybahar resonance test rig" \
  --output-folder /tmp/twingrid-r9-gpt55-elsa-yaybahar-test-rig
```

The freeze record state is `BLIND_FROZEN` and includes the output folder,
artifact summary/validation/skill findings paths when present, a blind
artifact manifest, and SHA256 receipts. Do not read partner output or modify
existing blind artifacts before writing it.

Canonical skill findings filename: `skill_findings.md`. Existing aliases
`skill-improvement-findings.md` and `skill-improvement-recommendation.md` are
accepted for backwards compatibility, but new handoffs should ask for
`skill_findings.md`.

### Phase 2: Partner Peek reveal

After both sides finish the blind pass, the manager writes a compact reveal
brief and uses `references/twingrid-partner-peek-template.md`. The reveal must
include the partner output path, a manager comparison, any newly available
tools, and the instruction to preserve the original blind artifact while adding
v2 supplements such as `partner-peek-improvements.md`, `v2-*`, validation logs,
`combine_recommendation.md`, and a Partner Peek record.

For structured Partner Peek records, use
`scripts/twingrid_contracts.py peek-record` as a starter and then fill in the
adopted ideas, validation, PR/issues, and manager notes:

```bash
python3 claude/skills/tmux-sprint/scripts/twingrid_contracts.py peek-record \
  --round 9 \
  --lane elsa \
  --side A \
  --runtime gpt55-window-13 \
  --task "Yaybahar resonance test rig" \
  --output-folder /tmp/twingrid-r9-gpt55-elsa-yaybahar-test-rig \
  --partner-folder /tmp/twingrid-r9-gpt54-elsa-yaybahar-test-rig
```

If a pane disappears or is restarted after producing artifacts, first inspect
its existing output folder. A valid `ready_for_peek.json` with `BLIND_FROZEN`
and matching SHA256 receipts is enough to recover from the folder rather than
rerunning the blind pass. Launch a fresh pane only for the missing Partner Peek
or implementation continuation, and point it at the frozen folder.

### Manager matrix

Use `scripts/twingrid_matrix.py` after the blind pass or Partner Peek pass to
scan output folders and optional pane captures:

```bash
python3 claude/skills/tmux-sprint/scripts/twingrid_matrix.py \
  --outputs-glob '/tmp/twingrid-r7-*' \
  --pane-captures-dir /tmp/twingrid-r7-pane-captures \
  --format markdown
```

The matrix reports lane, side, runtime, output folder, blind artifacts, v2
artifacts, validations run, PR/issue status, skill-improvement
recommendations, freeze state, canonical/alias skill findings filenames, and
pane-block findings. It detects common blockers in pane capture text,
including local command approval prompts, missing tool requests, and
command-not-found/install hints. See
`references/twingrid-manager-matrix.md` for the JSON shape and manager
workflow.

## Persona config

Persona metadata is read from
`~/.claude/projects/<project-slug>/tmux-v2/personas.json`. On first
invocation the skill copies `assets/personas.default.json` into place if
none exists. Edit it to change pane-to-persona mapping, worktree allowlists,
or add new personas (Gina, Henry, ...).

## Config + output locations

| Path | Purpose |
|------|---------|
| `~/.claude/projects/<project-slug>/tmux-v2/personas.json` | Persona definitions |
| `~/.claude/projects/<project-slug>/tmux-v2/rounds/round-<N>.json` | Per-round dispatch record |
| `~/.claude/projects/<project-slug>/tmux-v2/dispatches/<ts>.json` | Raw transaction log |
| `~/.claude/projects/<project-slug>/tmux-v2/logs/preflight.log` | Preflight raw captures |

All paths are created automatically on first run.

## How to invoke from Claude Code

The skill's scripts are meant to be called via Bash from within a Claude
Code session:

```bash
bash <workspace>/.claude/skills/tmux-sprint/scripts/preflight.sh
bash <workspace>/.claude/skills/tmux-sprint/scripts/dispatch.sh \
  --round 53 --manager claude-opus-4-6 \
  --to alice --assignment <workspace>/docs/plans/2026-04-11-alice-round53.md \
  --to bob   --assignment <workspace>/docs/plans/2026-04-11-bob-round53.md
bash <workspace>/.claude/skills/tmux-sprint/scripts/restart.sh frank
```

Prefer these over raw `tmux send-keys` whenever you're dispatching a sprint
round. The extra ~10 seconds of validation + rate-limit + verification
eliminates the class of silent failures that bit us during early development.

## Trigger phrases

Invoke this skill when the user says any of:

- "tmux-sprint preflight" / "preflight the sprint panes" / "probe all panes"
- "dispatch round N" / "send round N to personas" / "dispatch the assignments"
- "restart frank" / "frank is at codex resume" / "revive the codex pane"
- "check which personas are idle" / "who is free for more work"
- "send alice this assignment" / "hand bob this md file"
- "label-aware sprint batching" / "smart model picker" / "plan label batches"

## Related skills

- **`handoff`** *(forthcoming in this repo)* — generates the per-persona
  assignment markdown files. The preamble required by `dispatch` is part of
  the handoff template.
- **`sprint-update`** *(forthcoming)* — updates the sprint doc after dispatches.
  The round state JSON this skill writes feeds that update.

## Known limitations (as of v0.1)

- Worktree fence is NOT enforced yet — `preflight` reports the allowlist
  but `dispatch` does not reject mismatched worktrees. Future work.
- No multi-manager coordination — if a codex manager and claude manager
  both dispatch to the same round, they will race on the round-state JSON.
  Future work adds `flock`-based shared-state locking.
- 7/8-persona layouts (2x4, 4x2) are not auto-detected by `preflight` —
  it iterates panes 0..5 by default. Override with `--panes 0,1,2,3,4,5,6,7`.
- Assignment file preamble enforcement is a literal substring match, not a
  structural parse. A persona can still reinterpret the file if it's
  determined to, but the preamble block makes the contract explicit and
  sharply reduces the incidence.

## Implementation note (for this public repo)

The supporting `scripts/preflight.sh`, `scripts/dispatch.sh`, `scripts/restart.sh`,
`assets/assignment-preamble.txt`, and `assets/personas.default.json` files
referenced above live in the working wrfcoin workspace and are not yet
included in this v0.1 publish. The SKILL.md (this file) is the contract;
the implementation is shipped incrementally. The provider failover contract in
`references/provider-failover.md` is likewise a design packet until those
reference scripts are present in this public package. Open an issue in this
repo if you want to request the reference script implementations.
