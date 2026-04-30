---
name: wrfcoin-sprint-dispatch
description: Refresh a WRFCoin sprint from the current sprint doc and live GitHub issue or PR state, rewrite persona handoff markdown files, sync the sprint doc and persona-launch manifest, launch the tmux sprint window, and send kickoff nudges into the panes. Use when the user asks to pick up a sprint where the team left off, rewrite handoffs for Alice/Bob/Cindy/Dan, or restart the tmux sprint dashboard from current state.
---

# WRFCoin Sprint Dispatch

Use this skill when the user wants the "resume sprint" workflow, not just a raw persona launch.

This skill combines:
- sprint-doc review
- live GitHub issue and PR reconciliation
- handoff regeneration
- manifest refresh
- tmux sprint launch
- in-band pane nudges

## Worktree hygiene rule

Future tmux sprints must launch into clean, verified worktrees.

Important:
- `pull-all.sh` currently updates the top-level repos only
- it runs `git pull` on whatever branch each top-level repo is already on
- it does **not** update persona worktrees
- it does **not** reset worktrees to `origin/main`
- it does **not** detect rebases, detached HEADs, or dirty worktrees

So do not assume `pull-all.sh` made the persona worktrees safe.

## Launch config syntax

When the user wants a specific runtime or model mix, support a compact launch spec in the request.

Accepted patterns:
- `4 gpt-5.4`
- `4 sonnet`
- `2 sonnet, 2 gpt-5.3-codex`
- `2 opus, 2 gpt-5.4`
- `Alice and Bob on sonnet, Cindy and Dan on gpt-5.4`

Interpretation rules:
- Personas are assigned in fixed order: `Alice`, `Bob`, `Cindy`, `Dan`, `Elsa`, `Frank`, `Gina`
- A bare count plus model applies sequentially in that order
- Normalize common shorthand:
  - `opus` -> Claude runtime, model `opus`
  - `sonnet` or `sonnet 4.6` -> Claude runtime, model `sonnet`
  - `haiku` -> Claude runtime, model `haiku`
  - `gpt-5.4` -> Codex runtime, model `gpt-5.4`
  - `gpt-5.3-codex` or `5.3-codex` -> Codex runtime, model `gpt-5.3-codex`
- If the user names personas explicitly, prefer that mapping over sequential count parsing

If the user asks to launch personas and does not specify the model mix, do not guess unless they clearly asked for "the same as last time".
Ask one short clarifying question before launch, for example:
- `Which mix do you want for this launch: 4 opus, 4 gpt-5.4, or a split like 2 sonnet and 2 gpt-5.3-codex?`

Only skip that question when:
- the user explicitly says to reuse the current manifest, or
- the existing generated manifest is clearly the intended source of truth

Prefer this skill over a bare launcher when the user says things like:
- "pick up the sprint where we left off"
- "refresh the handoffs and launch tmux"
- "have Alice, Bob, Cindy, and Dan resume from the current state"

## Read first

Before doing anything substantial, read:
- `/home/tony/wrfcoin/.codex/skills/wrfcoin-persona-handoff/SKILL.md`
- `/home/tony/wrfcoin/.codex/skills/wrfcoin-launch-personas/SKILL.md`

If present, also mirror the operator behavior from:
- `/home/tony/.claude/skills/tmux-sprint/SKILL.md`

## Workflow

### 1. Establish the sprint source of truth

- Read the target sprint doc, usually `docs/plans/*Sprint*.md`
- Identify the personas the user wants to dispatch
- Read the current `docs/plans/sprint-<persona>.md` files if they already exist
- Read `docs/plans/persona-launch.generated.tsv` if it exists

### 2. Reconcile with live GitHub state

Use GitHub connector tools for all active issues and PRs mentioned in the sprint doc.

Check:
- active draft PRs
- whether PRs already merged
- requested changes / merge-conflict notes
- top queue issues that are still open

Do not trust the sprint doc blindly if GitHub says the state changed.

### 3. Rewrite persona handoffs

Write or refresh:
- `docs/plans/sprint-alice.md`
- `docs/plans/sprint-bob.md`
- `docs/plans/sprint-cindy.md`
- `docs/plans/sprint-dan.md`

Each handoff should:
- name the sprint doc path
- include a `## How to Work — You Are an Orchestrator` section
- state the live state being resumed
- prioritize rescuing still-open PRs before new queue items
- include exact worktree path, branch guidance, and focused validation commands
- tell the persona to update the sprint doc when claiming or blocking work
- end with "Start immediately"

Use the live repo that owns the active work, not the persona's historical default repo.

Examples:
- Cindy may need `backend-cindy` if her active PR is in `backend`
- Dan may need `backend-dan` if his active PR is in `backend`

### 4. Sync the sprint doc

Update the persona `Active` tables in the sprint doc so they match reality.

Typical fixes:
- mark merged PR rows as merged
- replace stale `next` rows with open draft PR rescue rows
- add `Handoff` links to `sprint-<persona>.md`
- keep queue order intact unless the user asked to reprioritize

Do not rewrite the entire sprint doc. Make the smallest accurate edit.

### 5. Refresh the manifest

Update `docs/plans/persona-launch.generated.tsv`.

Rules:
- use absolute prompt file paths
- set `team` to `sprint-ops`
- set `effort` to `high` unless the user asked otherwise
- choose `work_dir` based on the persona's current active repo, not just the persona default
- verify each worktree directory exists before keeping it in the manifest
- set `runtime` and `model` from the user's explicit launch config when provided
- if the user asked for a mixed launch, preserve the requested persona-to-model mapping exactly
- if reusing an existing manifest by user request, keep its runtime/model choices unless they asked to change them

### 5a. Verify or replace worktrees before launch

Before launching any persona, inspect each target worktree with:

```bash
git -C <worktree> status --short --branch
```

Treat any of the following as unsafe for launch:
- `HEAD (no branch)`
- rebase or merge in progress
- modified, deleted, or staged tracked files unrelated to the upcoming task
- wrong repo branch for the active PR rescue

If the worktree is safe and the next task is a fresh issue branch, normalize it with:

```bash
cd <worktree>
git fetch origin main
git checkout -B <branch-name> origin/main
git clean -fdx
```

If the worktree is unsafe, do **not** reuse it. Create a fresh rescue worktree from the owning repo instead.

Examples:

Fresh issue work:
```bash
git -C /home/tony/wrfcoin/<repo> worktree add /home/tony/wrfcoin/worktrees/<repo>-<persona>-dispatch -b <branch-name> origin/main
```

Existing PR rescue branch:
```bash
git -C /home/tony/wrfcoin/<repo> worktree add /home/tony/wrfcoin/worktrees/<repo>-<persona>-rescue <existing-branch>
```

Detached clean checkout from a remote PR tip when the local branch/worktree is compromised:
```bash
git -C /home/tony/wrfcoin/<repo> worktree add --detach /home/tony/wrfcoin/worktrees/<repo>-<persona>-rescue origin/<existing-branch>
```

If you create a rescue worktree, update:
- the persona handoff file
- the generated manifest
- any in-band kickoff nudge

The launch must always point at the clean worktree actually intended for the session.

### 6. Launch the tmux sprint window

If inside tmux, run:

```bash
scripts/launch-personas.sh --sprint-doc docs/plans/<SPRINT>.md --manifest docs/plans/persona-launch.generated.tsv --mode tmux --new-window
```

Expected result:
- new tmux window named `sprint`
- manager pane stays untouched
- `.sprint-target` updated

If tmux socket access is denied by the sandbox, rerun the command with escalation.

### 7. Verify pane state

Check:

```bash
tmux list-windows -F '#{window_index}:#{window_name}'
tmux list-panes -t sprint -F '#{pane_index}:#{pane_pid}:#{pane_current_command}:#{pane_title}'
cat /home/tony/wrfcoin/.sprint-target
```

If the panes show live Claude/Codex sessions, send a short kickoff nudge to each pane that points at the refreshed prompt file.

Preferred nudge shape:

```bash
tmux send-keys -t sprint.<N> "<Persona> kickoff: use /home/tony/wrfcoin/docs/plans/sprint-<persona>.md as the source of truth. <short priority summary>." Enter
```

If `send-keys` is blocked by sandbox permissions, rerun with escalation.

### 8. Fallback when a pane is waiting and send-keys text is not sufficient

If the session is live but needs the full prompt pasted in-band, use:

```bash
cat /home/tony/wrfcoin/docs/plans/sprint-<persona>.md | tmux load-buffer -
tmux paste-buffer -t sprint.<N>
tmux send-keys -t sprint.<N> Enter
```

Use this only when needed. Prefer the short nudge first.

## Reporting

In the final response:
- list the refreshed handoff files
- mention any key GitHub state corrections you made
- confirm the `sprint` tmux window was launched
- state the runtime/model assignment used for each persona
- include the pane map
- remind the user of `tmux select-window -t sprint` and `tmux send-keys -t sprint.<N> "message" Enter`

## Constraints

- Do not spawn subagents unless the user explicitly asks for subagent or team work
- Do not edit `scripts/launch-personas.sh` as part of normal dispatch
- Do not assume the old handoffs are still valid
- Keep the handoff files concise and operational, not essay-like
