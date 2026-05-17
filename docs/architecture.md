# Architecture

How the pieces fit together.

---

## The two-session topology

The manager pane (where the human + steering agent live) and the persona grid (where the worker agents live) **must** run in two separate tmux sessions, not two windows of the same session.

```
session "manager"   — 1 window, 1 pane: the sprint manager (Claude or Codex)
                      attached from terminal #1

session "sprint"    — 1 window, 6 panes: Alice/Bob/Cindy on top row,
                                          Dan/Elsa/Frank on bottom row
                      attached from terminal #2
```

**Why two sessions, not two windows?** If both terminals attach to the same session, every connected client locks onto the same active window. Click between two terminal windows on the desktop and they fight for which window is shown — both terminals jump to whatever the other selected. Two sessions fix this cleanly because each terminal owns its own session state.

`send-keys -t sprint:0.<N>` from inside the manager session reaches persona pane N regardless of which session is "active" in either terminal.

---

## Personas dispatch sub-agents; they do not edit files directly

A persona is an orchestrator. When dispatched a task, the persona:

1. Reads its assignment markdown file (a read-only contract from the manager — the persona must not edit this file)
2. Sets up its semi-permanent worktree (`git checkout -B <branch> origin/main; git clean -fdx`)
3. Opens a draft PR **before** writing any code, attaching the assignment file and a session plan as PR comments — this creates a decision-history record on every PR
4. Spawns 3-5 sub-agents in parallel via the Agent tool to do the actual code editing
5. Reviews sub-agent output, commits, runs tests, marks the PR ready
6. Hands off to `merge-review` for review-gated merge

The 3-5 sub-agents per persona × 7 personas = ~30 agents running in parallel during peak sprints.

---

## State lives on disk

| Path | Purpose |
|---|---|
| `<workspace>/docs/plans/<date>-Sprint.md` | The sprint's source of truth — backlog, lane assignments, status |
| `<workspace>/docs/plans/<date>-<persona>-<slug>.md` | Per-persona assignment file (read-only contract from manager) |
| `<workspace>/docs/plans/persona-launch.generated.tsv` | Manifest the launch-script reads to populate the persona grid |
| `~/.claude/projects/<project-slug>/tmux-v2/personas.json` | Persona definitions (pane index, model, worktree, allowlist) |
| `~/.claude/projects/<project-slug>/tmux-v2/rounds/round-<N>.json` | Per-round dispatch record (survives `/compact`) |
| `~/.claude/projects/<project-slug>/tmux-v2/dispatches/<ts>.json` | Raw transaction log per dispatch |
| GitHub issues + PRs | Merge ledger; the canonical "what's done" |
| `/tmp/sprint-doc-locks/<basename>.holder` | Advisory-lock holder file managed by the sprint-doc-lock hook |

Round-state JSON survives manager-pane `/compact` and is readable by a second sprint manager (codex or claude). This is what makes manager handoffs across compaction boundaries work.

---

## The dispatch transaction

`tmux-sprint dispatch` is the kernel of the system. Every dispatch:

1. **Preflights** every target pane. Refuses to send to `BUSY` or `DEAD` panes unless `--force`.
2. **Validates the assignment file**. Must exist, must be under `<workspace>/docs/plans/`, must contain the read-only-contract preamble.
3. **Cancels copy-mode** on each target pane (`send-keys -X cancel`). No-op if the pane isn't in copy-mode; cheap to run unconditionally.
4. **Builds the dispatch one-liner** for each pane: `Round N: read <path> and execute. This file is a contract — do not edit it.`
5. **Sends text, then `C-m`** in separate `send-keys` calls. Never passes the literal string `"Enter"`.
6. **Rate-limits by pane type.** Claude panes fire 2s apart and can interleave in parallel. Codex panes are strictly sequential with 10s spacing — they share a backend and 5s sometimes hits `overloaded_error`; 10s observed stable as of 2026-04-17.
7. **Verifies submission** with three-tier retry:
   - 3s after send, recapture pane. If prompt text appears OR a `Working` / `Processing` / tool-call indicator shows → success.
   - If nothing → retry with fresh `C-m`.
   - Still nothing → full re-send (cancel copy-mode, re-send text, `C-m`, wait 2× verify) — catches the post-`/clear` race observed 2026-04-17 where a pane silently absorbed the initial send.
   - Only after all three tiers fail is the dispatch marked `SILENT_FAIL` and logged with a ⚠️ marker.
8. **Persists round state** to `rounds/round-<N>.json`.

The whole thing is ~15 seconds of overhead per round, and it eliminates the class of silent failures that make autonomous multi-agent dispatch unreliable.

---

## Codex-aware revival

Codex panes have their own failure modes that don't apply to Claude:

- Pane exits to a "resume session" prompt — dispatched text lands in a dead buffer
- The `npm install -g @openai/codex` update prompt blocks input
- Auth re-prompts

`tmux-sprint restart <persona>` walks a state machine:

1. Cancel any stuck copy-mode
2. Detect current state via preflight:
   - `CODEX_EXITED` (at codex-resume prompt) → `C-c C-c`, wait for bash, run `codex`
   - `CODEX_UPDATE_PROMPT` → send `2` + `C-m` to skip
   - `DEAD` (at bash prompt) → run `codex`
   - `IDLE` → no-op, report
   - `WORKING` → refuse unless `--force`
3. Wait for `OpenAI Codex (vX.Y)` banner up to 15s
4. Report the new state

No user interaction needed unless codex itself prompts for auth.

---

## Concurrency: the sprint-doc lock

When two persona managers (e.g., a codex-side manager and a claude-side manager) are both active, they can race on the sprint markdown file. The lock prevents lost writes:

```
PreToolUse hook (sprint-doc-lock.sh):
  • Triggers on Edit / Write / MultiEdit
  • Filter: only files matching <workspace>/docs/plans/.*[Ss]print.*\.md$
  • If holder file exists AND holder PID is alive (/proc/$pid present) → exit 2 (block)
  • Stale holder (process dead) → reclaim
  • Otherwise → claim the lock, exit 0 (allow)

PostToolUse hook (sprint-doc-unlock.sh):
  • Triggers on the same operations
  • Releases the lock IF AND ONLY IF the current process owns it
  • Always exits 0 — unlock must not block tool-call completion
```

The lock is per-file (one holder per `<basename>.holder`), advisory (relies on agents respecting it via the hook), and self-healing (stale holders get reclaimed automatically). It's not a substitute for proper distributed locking, but for the actual workflow — humans + agents writing to a single sprint doc — it's exactly enough.

---

## What this design is not

- **Not a multi-machine cluster.** Personas run on one workstation, in one tmux server. A second machine running its own manager + grid would race on shared state (sprint doc, round-state JSON, GitHub PRs). Future work could add `flock`-based shared-state locking or a small relay service; for now, single-host is the assumption.
- **Not a replacement for human review.** `merge-review` gates on Codex auto-review for codex-enabled repos and posts structured findings before any merge decision, but the human (or manager agent) still sees every PR. Speed comes from parallel dispatch and reduced ceremony, not from removing review.
- **Not vendor-portable code.** The skill files target Claude Code, Codex, and Gemini specifically. Concepts (persona grid, dispatch contract, decision-history-on-PR, review-gating) are portable; the implementation is not.
