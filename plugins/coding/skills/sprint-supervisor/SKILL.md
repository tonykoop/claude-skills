---
name: sprint-supervisor
version: 1.7.0
last-updated: 2026-06-19
description: Babysit a running multi-pane tmux agent sprint while the user is AFK or asleep. Polls the manager pane and grid persona panes every ~4 min via ScheduleWakeup, auto-approves routine agent permission prompts using a configurable rubric, escalates destructive prompts, and produces a morning summary. Use this skill whenever the user says "watch the sprint", "supervise overnight", "I'm going to bed keep the sprint going", "babysit the panes", "keep an eye on twingrid", or invokes "/sprint-supervisor" — even without the word "supervisor". Scales by named scope — one instance handles a twingrid (18 panes), multiple instances divide-and-conquer a triplegrid or quadgrid by scoping each supervisor to a slice of grids coordinated via /tmp lockfile so peers don't double-approve. Pairs with sprint-watchdog.sh which absorbs the mechanical ~70% of approvals; this skill handles the judgment ~30% — commands, rate-limit prompts, escalation.
---

# /sprint-supervisor

Watch an already-running tmux sprint and keep it unblocked while the user is away. The sprint manager (an agent in tmux window `0:0`) dispatches work to a persona grid; this skill steps in when either the manager or a grid pane stalls on a permission prompt the user would normally answer.

This skill is intentionally split from the mechanical watchdog hook. The hook absorbs the routine ~70% of approvals (plain edit prompts) without needing a model in the loop. This skill handles the judgment 30% — command approvals, rate-limit prompts, refusal-list calls, and the morning summary.

> **Project-agnostic core.** This skill is the generic `tmux-agent-supervisor`. All project-specific behavior (refusal-list paths, approval-rubric entries, repo groupings, host names, citation format) lives in a config file — see the **Configuration** section. A worked configuration for one real project ("wrfcoin") ships as the commented example block in `references/supervisor-config.example.yaml`; treat it as illustrative, not as a default.

## Configuration

The refusal list, the approval rubric, and the project-specific labels (repo groupings, host names, workspace paths, PR citation format) are **externalized into a config file** so the skill core stays generic and you can release or share it without leaking project internals.

**Where to look.** On first run, look for a supervisor config in this order and use the first one that exists:

1. `$SPRINT_SUPERVISOR_CONFIG` (explicit path, if the user set it)
2. `~/.claude/sprint-supervisor-config.yaml` (per-user install)
3. `<skill-dir>/references/supervisor-config.example.yaml` (bundled generic defaults — safe fallback)

If only the example is found, run with the **generic defaults** from it (conservative refusal list, provider-agnostic rubric, placeholder labels) and mention once that the user can copy the example to `~/.claude/sprint-supervisor-config.yaml` and customize it.

**What the config controls** (see `references/supervisor-config.example.yaml` for the full schema and a commented wrfcoin-flavored example):

- `workspace_dir` / `worktrees_dir` — the roots the refusal list treats as "safe to operate within". Anything destructive *outside* these escalates.
- `refusal_list` — patterns that must never be auto-approved (data wipes, force-push to protected branches, secret exfiltration, permission-policy broadening, etc.). Generic defaults are provided; projects extend with their own protected hosts/paths.
- `approval_rubric` — the allow/confirm/escalate rows by prompt shape. The defaults are provider-agnostic (codex/claude/gemini/agy); projects add their own benign-command allowlist (e.g. read-only ops on a specific host).
- `labels` — `repo_groups` for the morning summary, `pr_citation_format` (e.g. `<owner>/<repo>#<n>`), `protected_branches`, and any named host aliases.
- `notifications` — Slack channel id (or none), and whether to use `PushNotification`.

When this SKILL.md gives a concrete example (a path, a host, a repo group), read it as a **placeholder** that the config supplies for real. The illustrative strings below use `<repo>`, `~/work/<project>`, `<host>` etc. on purpose.

## Invocation modes

The skill scales by being invoked multiple times with different **scopes**. A scope is just a name + a set of tmux targets to watch.

**Single supervisor (default, twingrid):**
```
/sprint-supervisor
```
Scope = `default`. Watches the manager (`0:0`) and all panes in `twingrid-a` and `twingrid-b`. This is what the user almost always wants.

**Scoped supervisor (triplegrid+ or specialized):**
```
/sprint-supervisor group-a --targets twingrid-a
/sprint-supervisor group-b --targets twingrid-b,twingrid-c
/sprint-supervisor group-c --targets twingrid-d
```
The first token after the skill name is the scope name. `--targets` is a comma-separated list of tmux sessions (or `session:window.pane` IDs if the user wants finer granularity). The manager pane (`0:0`) is **always watched by every scope** unless the user passes `--no-manager` — the manager is the brain and you want every supervisor to notice if it dies.

**If the user invokes the skill without a clear scope and you're not sure**, ask:
> "What should I watch? Defaults: scope=`default`, targets=`twingrid-a` and `twingrid-b`. Say something like 'just group-a on twingrid-a' if you want me scoped narrower."

## Dispatch modes — warm-start vs cold-start

The skill assumes a running sprint by default (warm-start). But it is often dispatched remotely (e.g. from the Claude mobile app while away from the desk), and in that case the sprint manager itself may not be running yet. The skill detects this on first iteration and bootstraps if needed.

**Warm-start (default).** A sprint manager is already running in `0:0` and panes already exist in the target sessions. Skip straight to the loop.

**Cold-start (remote-dispatch).** No manager pane, no target sessions. The skill must:

1. Confirm with the user (one round-trip) that a cold-start is intended — don't auto-bootstrap on a misfire.
2. Hand off to the **sprint-manager skill** to set up the tmux topology (twingrid by default) and start the manager. Don't reimplement that here — it's a separate skill with its own contract.
3. Wait until the manager pane is producing output (poll `0:0` every 30s for up to 5 min).
4. Once the manager is healthy, begin the normal supervisor loop.

The cold-start detection itself is simple — capture `0:0` and the configured target sessions, and decide based on what you see:

```bash
manager_alive=$(tmux capture-pane -t 0:0 -p 2>/dev/null | grep -cE 'codex|claude|>' || echo 0)
targets_exist=$(tmux has-session -t twingrid-a 2>/dev/null && echo 1 || echo 0)
```

See `references/dispatch-patterns.md` for worked patterns including the mobile cold-start handshake, the scheduled-task pattern for nightly recurring supervision, and the routines integration once that capability is generally available. The forward-looking `nightly-sprint` routine design and the scheduled-task→routine migration path live in `references/routines-integration.md` (blocked on Anthropic routines GA — design-only, issue #161).

## Prerequisites (verify before starting)

1. **Auto mode is on.** Without it, you'll prompt the user on every tool call and the whole point is defeated. If auto mode is off, ask the user to enable it before continuing.
2. **Sprint manager is running** in tmux window `0:0`. Capture it once to confirm:
   ```bash
   tmux capture-pane -t 0:0 -p -S -20 | tail -20
   ```
3. **Target sessions exist.** Run `tmux list-sessions` and verify your scope's targets are present.
4. **Watchdog hook is running** (recommended, not required). The watchdog defaults to `twingrid-a twingrid-b`, so always pass your scope's actual targets via `SPRINT_SESSIONS`. Start it after writing the lockfile in step 5 so you can pull targets straight from it. The watchdog script path is configurable (`watchdog_script` in the config; defaults to `~/.claude/skills/sprint-supervisor/scripts/sprint-watchdog.sh` or wherever the install placed it):
   ```bash
   SPRINT_SESSIONS="$(python3 -c "import json; print(' '.join(json.load(open('/tmp/sprint-supervisor/<scope>.lock'))['targets']))")" \
     nohup "$WATCHDOG_SCRIPT" > /tmp/sprint-watchdog.log 2>&1 &
   disown
   ```
   Check the log at `/tmp/sprint-watchdog.log` to confirm it logged `sessions='<your targets>'` rather than the default. Without the watchdog, you'll spend most of your cycles on routine edit prompts instead of judgment work. **Don't skip the `SPRINT_SESSIONS` export** — the watchdog will silently watch the wrong sessions and you'll wonder why no edit prompts ever get auto-approved (2026-05-18 lesson).
5. **Claim the scope.** Write a lockfile so peer supervisors can see your slice and avoid stepping on it. The lockfile is also where you persist state across wakeups so the wakeup prompt itself can stay tiny (see "Loop cadence" below):
   ```bash
   mkdir -p /tmp/sprint-supervisor
   cat > /tmp/sprint-supervisor/<scope>.lock <<EOF
   {
     "scope": "<scope>",
     "manager_pane": "0:0",
     "targets": ["twingrid-a", "twingrid-b"],
     "started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
     "heartbeat": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
     "iter": 0,
     "current_phase": "cold-start",
     "last_goal_achieved_seen_at": null,
     "last_status_summary": null,
     "notable_events": []
   }
   EOF
   ```
   Field semantics:
   - **`current_phase`** ∈ {`cold-start`, `active`, `idle`, `re-engaged`} — drives cadence (see "Loop cadence").
   - **`last_goal_achieved_seen_at`** — ISO timestamp of the most recent cycle that saw the manager's "Goal achieved" pill; used to decide when to ramp to idle cadence.
   - **`last_status_summary`** — one-line summary of the most recent action ("approved Round 32 merge loop (14 PRs)", "manager idle on Goal achieved", etc.) so the wakeup prompt can resume statefully without re-pasting context.
   - **`notable_events`** — append-only list of dicts `{iter, time, event}` for anything you'll want in the morning summary (escalations, refusals, pile-ups, provider failovers, etc.). Keep it bounded (~50 entries; drop oldest).

   Refresh `heartbeat` each cycle. Read peer lockfiles before approving any pane — if a peer's `targets` claims the pane and its heartbeat is fresh (<15 min), skip it.

## Loop cadence — adaptive (30s / 240s / 1800s)

Cadence is driven by `current_phase` in the lockfile. Pick the next-wakeup delay from this table at the end of each iteration:

| Phase | Trigger | `delaySeconds` |
|---|---|---|
| `cold-start` | `iter` < 3, or `.pending` marker non-empty | **60** (clamped from desired 30) |
| `active` | Any manager prompt seen in the last 2 cycles, OR any grid pane stuck in the last 2 cycles | **240** |
| `idle` | No prompts seen for 2 consecutive cycles AND `last_goal_achieved_seen_at` is within the last 30 min | **1800** |
| `re-engaged` | Manager was `idle` last cycle but is now producing output / has a prompt again | **240** (revert to active next cycle) |

**Cache cost reasoning:**
- 30s ideal for cold-start (but the runtime clamps to 60) — manager-side prompts cluster at sprint kickoff (dispatch escalation, first verification sweep). Front-loading attention saves user friction.
- 240s during active work — under 300s = prompt cache stays warm.
- 1800s when idle — one cache miss per cycle, but earns it back by sleeping past long quiet periods. Avoid the 300s "worst-of-both" trap.

**Phase transitions:**
- Set `current_phase` = `cold-start` on first iteration. Bump to `active` once `iter ≥ 3` OR you've handled at least one prompt.
- Set `current_phase` = `idle` when both: (a) the last 2 captures of the manager pane showed "Goal achieved" or no `Would you like to` prompts, AND (b) `last_goal_achieved_seen_at` is set within the last 30 min.
- Reset to `active` (or `re-engaged`) as soon as the manager emits a fresh prompt or a grid pane gets stuck.

**Wakeup prompt is now ONE LINE.** Persist all state in the lockfile and let the wakeup prompt be:
```
Resume /sprint-supervisor for scope <scope>. State in /tmp/sprint-supervisor/<scope>.lock.
```
This survives compact boundaries (the SKILL is re-loaded by the harness) and saves ~3KB of re-pasted rubric per cycle. Do NOT re-paste the rubric, target list, or per-iter status into the wakeup prompt — that drove ~30 wasted cycles' worth of cache bloat in the 2026-05-18 run.

### Pending-judgment short-circuit

The watchdog can leave a marker at `/tmp/sprint-supervisor/<scope>.pending` when it sees a command-shape prompt it deliberately won't handle (commands need supervisor judgment, not blind approval). At the top of each iteration, check this file first:

```bash
PENDING=/tmp/sprint-supervisor/<scope>.pending
if [ -s "$PENDING" ]; then
  current_phase=cold-start  # force tightest cadence
  cat "$PENDING"            # read which panes are flagged
  : > "$PENDING"            # clear the marker
fi
```

A non-empty `.pending` file always means "act now, then drop back to your scheduled cadence on the next iteration." This halves the average latency on command-shape prompts without needing event-driven plumbing.

## Each iteration — five steps

### 1. Refresh your lockfile heartbeat + status

Update heartbeat, bump iter, and write back the previous iteration's `last_status_summary` and `current_phase`. At the end of the iteration (after step 6) you'll overwrite these again with the new values:

```bash
LOCK=/tmp/sprint-supervisor/<scope>.lock
python3 - <<PY
import json, datetime
p = "$LOCK"
d = json.load(open(p))
d["heartbeat"] = datetime.datetime.now().isoformat()
d["iter"] = d.get("iter", 0) + 1
json.dump(d, open(p, "w"))
PY
ITER=$(python3 -c "import json; print(json.load(open('$LOCK')).get('iter', 0))")
PHASE=$(python3 -c "import json; print(json.load(open('$LOCK')).get('current_phase', 'cold-start'))")
```

At the end of the iteration, write back `last_status_summary` (one line) and `current_phase` (per the cadence table) and append to `notable_events` if anything noteworthy happened.

### 2. Read peer lockfiles

```bash
ls /tmp/sprint-supervisor/*.lock 2>/dev/null | while read f; do
  scope=$(basename "$f" .lock)
  [ "$scope" = "<your-scope>" ] && continue
  cat "$f"
  echo "---"
done
```

Build a set of "panes owned by peers" from any peer lockfile whose heartbeat is within the last 15 minutes. You'll filter these out in step 4.

### 3. Check the sprint manager

```bash
tmux capture-pane -t 0:0 -p -S -60 | tail -60
```

If a prompt is open, apply the rubric below. The manager pane is the most load-bearing single pane — never skip it, even if a peer also claims it.

### 4. Scan your grid panes

Use the bundled script:
```bash
bash <skill-dir>/scripts/grid-scan.sh <target1> <target2> ...
```

Or inline (functionally equivalent):
```bash
for sess in <target1> <target2>; do
  for id in $(tmux list-panes -t "$sess" -F '#{pane_id}'); do
    out=$(tmux capture-pane -p -t "$id" 2>/dev/null | tail -12)
    if echo "$out" | grep -qE 'Press enter to confirm|Yes, proceed|Approaching rate limits|Would you like to'; then
      echo "=== $id ==="; echo "$out" | tail -10; echo ""
    fi
  done
done
```

For each stuck pane that **isn't** claimed by a peer (from step 2), apply the rubric below. **Space approvals ~2s apart** to avoid agent-pane API overload.

### 5. Periodic post-merge prune sweep (every 4th wakeup ≈ 16 min)

Safety net for merges that happened outside the sprint manager (manual gh merges,
GitHub UI, merge-review called standalone). The merge-time skill already prunes
its own merges; this catches anything it missed.

Track an `iter` counter in your lockfile (initialize to 0, increment each cycle).
Every 4th iteration, run:

```bash
~/.claude/skills/disk-cleanup/scripts/prune-after-merge.sh --sweep --apply --json \
  >> /tmp/sprint-supervisor/<scope>.prune.log
```

The script is safe-by-default (refuses unmerged, dirty, or live-pattern
branches; resets persona worktrees rather than removing them). One sweep is
capped at 20 branches — if more remain, the next sweep will pick them up.

If a peer supervisor's lockfile claims any repo you'd touch, skip those repos
this cycle and let the peer's own sweep handle them. (Sweep mode currently
walks all repos under `WORKSPACE_DIR`; if peers exist, scope yourself by
running the script repo-by-repo with `--repo <name>` for only the repos
relevant to your panes' lanes.) `WORKSPACE_DIR` comes from `workspace_dir` in
the config (see Configuration).

The motivation is the 2026-05 WSL2 disk-bloat incident; see
`feedback_post_merge_prune.md` for the rule and rationale.

### 6. Schedule the next wakeup

Always re-schedule unless the user has returned or an escalation triggered. If escalation triggered, surface to the user and pause — don't auto-resume until the user acknowledges.

## Approval rubric

> The rows below are the **generic defaults**. Project-specific additions (e.g. a benign read-only command allowlist on a named host) come from `approval_rubric` in the config — see `references/supervisor-config.example.yaml`.

**Provider-agnostic note.** Grid panes may be running `codex` (gpt-X), `claude`, `gemini`, or `agy` (Antigravity, Gemini-backed) CLIs. The sprint-manager may also actively *migrate* a budget-exhausted pane from one provider to another (e.g. exit the codex CLI, launch `claude` in the same pane, brief availability test, resume dispatching that lane — see `tmux-sprint/references/provider-failover.md`, repo issue #166). Each CLI has its own prompt phrasing — codex says "Would you like to make the following edits?", claude says it differently, gemini/agy differently again — but the *shapes* are the same: edit confirmation, command confirmation, rate-limit alert. Match the shape, judge the action, ignore which CLI is asking. If you see a prompt shape the rubric doesn't cover (a new CLI's UI, an unusual phrasing), fall through to the "anything else" row and lean conservative.

**agy / Antigravity permission caveat (#191).** agy uses a codex-style allowlist at `~/.gemini/policies/auto-saved.toml`. Treat any prompt asking to broaden that policy — auto-allow `run_shell_command`, add `--dangerously-skip-permissions` / `skipPermissions`, or persistently allow shell — as a **refusal-list** item (escalate, do not approve). One-shot agy edit/command prompts follow the normal shape rows below. Headless `agy -p` panes are non-interactive and raise no permission prompts.

| Prompt pattern | Action |
|---|---|
| `Would you like to make the following edits?` with `1. Yes / 2. don't ask again for these files (a) / 3. No` | `a Enter` |
| `Would you like to make the following edits?` with `1. Yes / 2. No` (no `a` option) | `y Enter` |
| `Would you like to run the following command?` for benign read-only (`npm audit`, `cargo test`, `cargo check`, `gh pr view`, `gh pr list`, `gh issue view`, `git status`, `git diff`, `git log`, `ls`, `find` with `-maxdepth`) | `p Enter` (always-allow) |
| `Would you like to run the following command?` for `gh pr create/comment/ready/merge`, `gh issue close/comment`, `git push` to a feature/codex branch, `git rebase`, `git push --force-with-lease` to a feature branch | `y Enter` |
| `Would you like to run the following command?` for `ssh` read-only ops on a config-listed host (e.g. `<host>`: dashboard scripts, `docker ps`, `find`, `ls`, `git status`) — only if the host appears in the config's allowlist | `y Enter` |
| `Approaching rate limits — Switch to gpt-5.4-mini?` | `2 Enter` (Keep current model). The reason is **not** that downshifting is always wrong — it's that the sprint-manager may have a better plan (e.g. migrate the pane to a different provider entirely: codex → claude → gemini). Preserving model choice keeps that path open. The manager owns the pivot; the supervisor just doesn't shortcut it. |
| Provider availability test prompt (sprint-manager dispatching a brief "are you up?" probe to a freshly-launched `claude` or `gemini` in a previously-exhausted pane) | Same rules as the corresponding edit/command rubric row apply — judge by shape, not by which CLI is asking. |
| Anything else, or a command you can't immediately classify | Capture the last 40 lines first (`tmux capture-pane -p -t <pane> -S -40`), then judge. Lean conservative — when in doubt, escalate, don't approve. |

The reason this rubric is structured by prompt-pattern rather than by command-substring is that the agent CLI prompt UI is the stable surface — its options change rarely. Command shapes are not. Match the prompt, then sanity-check the command, then act.

## Refusal list — do NOT auto-approve, escalate to user

> The patterns below are the **generic defaults**. Projects add their own protected paths/hosts/branches via `refusal_list` in the config — see `references/supervisor-config.example.yaml`. Path/host placeholders (`<worktrees_dir>`, `<host>`, protected branches) are resolved from the config.

If a prompt requests any of these, **do not approve and do not dismiss**. Capture context, fire a `PushNotification` to wake the user, append to `notable_events`, surface it in your next response, and pause the loop:

- `rm -rf` targeting paths outside the configured `worktrees_dir` (default placeholder `~/work/<project>/worktrees/`) or `/tmp/`
- `DROP TABLE`, `DROP DATABASE`, `redis-cli FLUSHALL`, or any other live-data wipe
- `git push --force` (without `--with-lease`) to a protected branch (default: `main` / `master`)
- `git push` to a protected branch directly (not via PR merge)
- Anything that prints, exfiltrates, or writes secrets / env files / private keys
- `git branch -D` against more than 2 branches in one command
- Live service restart on a production/testnet host that isn't authorized by the active handoff contract
- Any command modifying `~/.ssh/`, system services, or sudo state
- Broadening an agent's permission policy: `--dangerously-skip-permissions`, `skipPermissions`, persistently auto-allowing `run_shell_command`, or editing `~/.gemini/policies/auto-saved.toml` to add shell access (agy / Antigravity — #191)

The reason these are hard-stop is that the cost of approving one wrong is catastrophic (data loss, leaked secrets, broken production) while the cost of waking the user is merely annoying. The asymmetry argues for caution.

## Pre-merge checklist (run before every PR merge)

`mergeStateStatus == CLEAN` is necessary but **not sufficient**. Before squash-merging any agent PR, walk this list — each item is a real failure that bit a real sprint (2026-06-14):

1. **A PR that ADDS or changes CI must have its NEW job green.** If the repo had no pre-existing *required* checks, `CLEAN`/`UNSTABLE` can hide a red brand-new job (e.g. an added `ci.yml` whose `validate` step fails). Explicitly read `gh pr checks <n>` and confirm the conclusion of the job the PR introduced — don't trust the rollup. Merging a red foundation poisons `main` for every downstream PR.
2. **No-CI / light-CI repos: run the tests locally first.** For repos without enforced CI (fresh repos, some plugin repos), `git -C <worktree> pull` then `python3 -m pytest -q` (+ `ruff check` on touched files) before merging. CLEAN there just means "no required checks", not "tests pass".
3. **New task family / catalog entry → completeness-validator cascade.** If the PR adds a task family (or anything a "every X is registered/mapped" validator enumerates), confirm it also updated the map (e.g. `REASONING_BUCKETS.md`, `registry.json`). After it merges, re-check sibling PRs — they may flip `BLOCKED` because the validator now sees the new entry as unmapped in *their* branch.
4. **Duplicate / superseded detection.** When agents self-extend into adjacent issues they create overlapping branches. Before merging, list the PR's files and check whether main already has that deliverable (a prior round/rework merged it). Close duplicates as superseded rather than merging a second copy.
5. **Dependency order for a new foundation repo.** Merge the schema/CI story first, then rebase each dependent branch onto the new `main` (they carry stale shared files — `pyproject.toml`, `__init__.py` — resolve those to main's version). Re-check mergeability after each merge; expect rebase cascades on shared trees.
6. **Conflict resolution on overlapping inserts — beware the coincidental-context trap.** When two branches both insert new code at the same location and share trailing lines (`}`, `</section>`, dict/registry boilerplate), do NOT just strip the 3 conflict markers — that mis-joins one block's header to another's body. Reconstruct from main + the branch's *named* additions, or duplicate the shared closing per side. Validate (`python -c "import ast; ast.parse(...)"` / balanced-tag count) and run tests before continuing the rebase.

## Manager-acting-on-an-agent's-behalf safety

The supervisor sometimes finishes an agent's work for it (push a stalled-but-done agent's commit, fix a trivial lint, open a codex PR). Guardrails:

- **Committed vs staged before a manager-push.** If you push an idle agent's HEAD to unblock it, first confirm the intended change is *committed*, not merely staged/working-tree. Check `git show HEAD:<file> | grep <fix>` or `git diff --cached --quiet`. Pushing a pre-fix HEAD looks like progress but leaves CI red and wastes a cycle.
- **Don't race a live agent on a shared `.git`.** Worktrees share one `.git`; operating in/near a worktree whose agent is still active causes `index.lock` collisions. Use a dedicated scratch worktree for manager rebases and wrap git in a short lock-retry loop (sleep 8s, retry ~5×).
- **Open codex PRs from the host** (codex panes can't reach `api.github.com`); use `Refs #N`, never `Closes`.

## Pre-dispatch verification (when the supervisor also dispatches)

If this supervisor instance also stands up worktrees and launches panes (warm hand-off, or a combined manager+supervisor role), verify before sending any task:

1. **Worktree↔repo match.** For each worktree, assert `git -C <worktree> remote get-url origin` is the *intended* repo. A copy-paste slip (running `git worktree add` from the wrong clone dir after a `cd`) silently routes an agent's work to the wrong repo — caught too late, at PR time, in the wrong place. One cheap loop after setup prevents it.
2. **Launch agents in true auto mode, not acceptEdits.** claude: `--permission-mode auto` (footer must read `⏵⏵ auto mode on`, not `accept edits on`). codex: `-a on-failure`. `acceptEdits` still prompts on every bash command and turns the supervisor into a full-time prompt-clearer.
3. **Clear the one-time "trust this folder" prompt** that fresh worktrees trigger on first agent launch (`1 Enter` for claude; codex usually auto-trusts).

## AFK notifications

The supervisor runs to keep the sprint going while the user is AFK or asleep. Two outbound channels exist; use both when appropriate.

**Primary: `PushNotification` tool.** Always available, no auth dependency. Auto-suppresses when the user is at the keyboard (last keystroke < 60s) so it doesn't distract them mid-work. Use it for the **urgent path** — anything that would otherwise sit until the next wakeup cycle and matters enough to interrupt them:

- Refusal-list trigger (see below). Send BEFORE pausing the loop so they see it on their phone.
- Manager death / "Waiting for background terminal" >20 min.
- Pile-up of >8 stuck grid panes.
- Provider failover that needs a decision (manager exhausted weekly budget on all providers).

Keep messages under 200 chars, one line, no markdown. Lead with what they'd act on. Examples:

```
PushNotification(status="proactive", message="sprint-supervisor escalation: 10 grid panes stuck, manager may be dead. Pane tails in next reply.")
PushNotification(status="proactive", message="REFUSAL: manager tried git push --force to main. Paused. Open the CLI to review.")
```

Don't notify for routine progress, individual merge approvals, or anything you can handle inside the rubric without the user.

**Secondary: Slack `slack_send_message`** (best-effort, may fail). Use for **morning summaries** and other non-urgent posts that benefit from markdown / threading / phone reply. Wrap in a try/except — if the call fails with `OAuth token does not meet scope requirement user:mcp_servers`, silently skip Slack and write the same summary to `/tmp/sprint-supervisor/<scope>.summary.md` for the user to read in the terminal next time they invoke the supervisor.

```python
try:
    # via the MCP tool
    slack_send_message(channel_id=SLACK_CHANNEL_ID, message=summary_markdown)
except Exception as e:
    if "user:mcp_servers" in str(e):
        # session was started before Slack scope was granted; fall back to filesystem
        Path(f"/tmp/sprint-supervisor/{scope}.summary.md").write_text(summary_markdown)
    else:
        raise
```

The Slack scope dependency: Slack write requires the CLI session's OAuth token to include `user:mcp_servers`. If the user installed the Slack app AFTER starting this CLI session, this session won't have it; the next fresh session will. Don't ask the user to log out mid-supervision.

**Configuring the Slack channel.** First-time setup: if no Slack channel is set in the config (`notifications.slack_channel_id`), ask the user once which channel/DM to use, save the channel_id to the config, and reuse it forever. Don't prompt every time.

## Escalation triggers — surface proactively

Even without a destructive prompt, surface to the user (in the next wakeup response) if:

- **More than 8 grid panes** in your scope are stuck on prompts simultaneously — signals the manager has fallen behind or died.
- The **manager pane has been "Waiting for background terminal"** for >20 min with no new output.
- Manager **context is <5% AND has not auto-compacted** within one cycle (it should auto-compact around 7-10%).
- A persona pane shows a **shell prompt or process death** instead of the expected codex/claude UI.
- The watchdog log shows a tight loop on the same pane (>5 approvals per minute on one pane).
- **A peer supervisor's lockfile heartbeat has gone stale** (>15 min) — its scope is now unowned. Note this in your response and ask whether to expand your scope or wake the peer.

When escalating: write a one-paragraph summary at the top of your next response, then list the affected panes/commands with their last 10 lines of context.

## Coordination with peer supervisors

When the user grows past twingrid (triplegrid = 27-36 agents, quadgrid = 36-45), they'll typically run multiple supervisors in separate Claude sessions, each scoped to a topic-coherent slice of grids. Scope names are arbitrary and project-defined (the config's `labels.repo_groups` is a good source); for example:

- A **`group-a`** scope watches the grids where most cross-pane coordination happens.
- A **`group-b`** scope watches the infra/backend grids.
- A **`group-c`** scope watches the frontend / UX grids.

Each supervisor:
1. Owns its declared targets (lockfile claims them).
2. Watches the manager pane regardless (the manager is shared infrastructure).
3. Skips panes claimed by a peer with a fresh heartbeat.
4. Reports on its scope only in the morning summary.

If two supervisors accidentally claim overlapping panes (config drift, user typo), the supervisor with the **earlier `started` timestamp** keeps the overlap; the later one drops the conflicting panes and notes it in the next response. This is deterministic and doesn't require negotiation.

See `references/scaling-topology.md` for worked triplegrid/quadgrid examples and topic-specialization patterns.

## Morning summary

When the user returns, lead with a structured summary scoped to **your** slice. Sections in order:

1. **Sprint manager** — hours running, auto-compact count, current task, context/budget remaining. (Only the first supervisor to report should cover this; subsequent supervisors can skip if a peer already did.)
2. **Merges that landed** — grouped by repo (use the config's `labels.repo_groups`), with PR numbers.
3. **Issues closed** — grouped by repo.
4. **Production / testnet diagnostics** — starting state → ending state (only if your scope touches diagnostics for a host listed in the config).
5. **What I handled directly** — count of stuck-pane approvals, ssh diagnostics approved, rate-limit prompts answered.
6. **Caveats / things to review** — panes that exhausted weekly budget, anything escalated, anything ambiguous.

Cite PR numbers using the config's `labels.pr_citation_format` (default `<owner>/<repo>#<n>`) so the user can click. See `references/morning-summary.md` for a worked example with the exact phrasing patterns that have worked well.

**Delivery.** When the supervisor first detects `current_phase` flipping to `idle` (sprint complete), build the summary once and:
1. Save to `/tmp/sprint-supervisor/<scope>.summary.md` (always — this is the canonical copy).
2. Try `slack_send_message` to the configured channel; on scope failure, silently skip.
3. Render it as your next user-facing response.

Don't re-deliver the same summary on every subsequent idle cycle — track `summary_delivered_at` in the lockfile.

## Compatibility (tmux versions / platforms)

Audited for #163. The supervisor's bundled scripts target tmux 3.2+ and run on
Linux, WSL2, and macOS, but the default shell and `date` differ across them.

| Platform / shell | Status | Notes |
|---|---|---|
| WSL2 Ubuntu 24.04 + tmux 3.4 | Verified | `list-panes -F '#{pane_id}'`, `capture-pane -p`, `capture-pane -p -S -N`, `has-session` all work. `/tmp/sprint-supervisor/` lockfiles live on the WSL filesystem and need no special handling across the WSL boundary. |
| WSL2 Ubuntu 22.04 + tmux 3.2/3.3 | Expected OK | Same flags. |
| macOS Homebrew tmux 3.4+ | Expected OK (portability fixes applied) | The tmux flags used are stable since 2.x; the gotchas are shell/`date`, not tmux. |
| macOS default `/bin/bash` 3.2 | Gated | `grid-scan.sh` reads panes with a portable `while read` loop, not `mapfile` (bash 4+ only). |
| tmux < 3.2 (e.g. macOS default 2.x) | Soft-gated | `tmux-preflight.sh` detects it and warns (exit 4); scanning continues but may miss prompts — upgrade via Homebrew. |
| tmux not installed | Guarded | `tmux-preflight.sh` exits 3 with install guidance; `grid-scan.sh` exits cleanly instead of emitting confusing empty output. |

Portability fixes applied this round (#163):

- **`tmux-preflight.sh`** (new) — the concrete version gate. It probes `tmux -V`,
  normalizes the version (`tmux 3.2a` → `3.2`, `tmux next-3.5` → `3.5`), and
  compares against `MIN_TMUX_VERSION` (3.2). Exit `0` = supported, `4` = present
  but old (soft warning, scanning continues), `3` = tmux absent (clear install
  guidance). `grid-scan.sh` sources it and runs `run_preflight --quiet` before
  scanning, so a missing/old tmux yields **one actionable message** instead of
  confusing empty output. Source it to unit-test `parse_tmux_version` /
  `version_ge` / `run_preflight` (test seam: `TMUX_VERSION_OVERRIDE`, `TMUX_BIN`).
- **`grid-scan.sh`** — replaced `mapfile -t` with a `while IFS= read -r` loop
  (bash 3.2 safe), and switched from `capture-pane | tail -12` to
  `capture-pane -p -S -40` so a prompt sitting above trailing blank pane rows
  isn't pushed out of a short tail window (observed on tmux 3.4). Widened
  `PROMPT_REGEX` with a generic confirmation catch-all so a new CLI's phrasing
  surfaces to the supervisor instead of being silently missed. Now preflights
  tmux before scanning.
- **`notify-supervisor.sh`** — `date -Iseconds` (GNU-only) and `%3N`
  millisecond format (GNU-only) now fall back to portable
  `date -u +%Y-%m-%dT%H:%M:%SZ` and epoch seconds on BSD/macOS.
- **Lockfile snippet** in Prerequisites uses portable
  `date -u +%Y-%m-%dT%H:%M:%SZ` instead of `date -Iseconds`.

The gating rule is now mechanical, not just advice: an incompatible/old/missing
tmux is detected by `tmux-preflight.sh` and surfaced as a soft warning with
install guidance rather than a loud failure or silent empty scan — never assume
a single tmux build.

> **Note:** `sprint-watchdog.sh` is an install-time companion (it ships into the
> live `~/.claude` install, not this repo package). The same two portability
> rules apply to it — `date -u +%Y-%m-%dT%H:%M:%SZ` over `date -Iseconds`, and
> a portable pane-read loop. Apply them when that script is next packaged.

## Marathon mode (long-haul ~5h runs)

A **marathon** is a grid run meant to stay productive through a full ~5-hour usage block *without* (a) the scarce budget exhausting early or (b) the Opus supervisor hitting its own usage limit and killing the run. When the user says "marathon" (or wants an overnight that lasts), supervise with these in mind. Full rationale in `feedback_marathon_grid_pattern.md`.

**Budget ordering (lean on cheap/resettable, protect scarce):**
- **codex-spark = workhorse** — if the user has a reset button it's ~unlimited; lean on it hardest.
- **gpt-5.5 = second-heaviest** — synthesizer / merge-queue / reviewer roles.
- **Sonnet = the scarce worker budget** — this is what caps a marathon; pace it (fewer lanes, hard sub-fanout caps).
- **Opus 4.8 = scarcest → supervisor/manager ONLY, never a churning worker.** The supervisor's own Opus quota is the thing most likely to kill the marathon.

**Approved 9-agent topologies:**
- **4 Sonnet + 4 codex-spark + 1 gpt-5.5**, two-phase: all 8 produce PRs, then **cross-peer-review** (Sonnet review the codex PRs, codex review the Sonnet PRs); gpt-5.5 = synthesizer / merge-queue. Cross-review is free useful burn + adversarial verify.
- **3 Sonnet + 3 codex-spark + 3 gpt-5.5** — heavier on resettable/codex-side budgets, for huge backlogs.

**The pacing levers matter more than the model mix** (this is what actually kills marathons):
1. **Cap per-agent sub-fanout** — no 40-agent sub-swarms. On 2026-06-19 a single lane's 40-agent audit burned ~2.4M tokens and helped cap Sonnet in ~90 min. Bake "Task sub-swarms ≤3; go serial for breadth" into the dispatch contract; if you see a lane fan out massively, flag it (it's a budget bomb, not progress).
2. **Lean Opus supervisor** — long cadence (20–30 min once past cold-start), minimal cycles, never worker-grade work. (The 2026-06-19 supervisor ran 56 cycles, many redundant.)
3. **Useful burn, not raw burn** — cross-review rounds + loop-until-dry-with-caps + staggered waves beat one giant sub-swarm.

## What this skill does NOT do

- **Doesn't dispatch new work** to grid panes. The manager owns that.
- **Doesn't merge PRs.** The manager owns that.
- **Doesn't `/clear` or `/compact`** the manager. Let it self-compact.
- **Doesn't touch a live production/testnet host directly** — only approves the manager's read-only diagnostics.
- **Doesn't dispatch the manager's own commands** — only approves or refuses what the manager asks for.
- **Doesn't reorganize the grid topology.** If a peer supervisor dies, surface it to the user; don't unilaterally absorb its scope.

**One exception** — post-merge worktree pruning. The supervisor runs a
periodic `prune-after-merge.sh --sweep` (step 5 above) as a safety net for
merges that happen outside the manager. The sweep is read-mostly: it refuses
unmerged branches, refuses dirty worktrees, and only resets persona worktrees
rather than removing them. See `feedback_post_merge_prune.md`.

## On exit

When the user returns and dismisses the supervisor:
1. Deliver the morning summary (if not already delivered — see "Morning summary").
2. Clean up scope files:
   ```bash
   rm -f /tmp/sprint-supervisor/<scope>.lock
   rm -f /tmp/sprint-supervisor/<scope>.pending
   # Keep <scope>.summary.md and <scope>.prune.log — user may want to grep them later.
   ```
3. Stop the watchdog if you started it (check via `pgrep -f sprint-watchdog.sh`).
4. Don't reschedule another wakeup.

## Tuning notes from the 2026-05-18 session

Second full-sprint run (4 rounds, 32 PRs merged across 32 repos, ~2h 12m manager runtime, 35 supervisor cycles). New findings:

- **Adaptive cadence beats fixed 240s.** Prompt density is front-loaded (dispatch, first verify sweep, first PR creation all within the first ~10 min) and tails to zero once "Goal achieved" appears. The 30/240/1800 schedule formalized above came from manually ramping cadence during this run and saved an estimated half-dozen unnecessary cycles in the idle phase.
- **Wakeup-prompt re-pasting was wasteful.** ~30 cycles each re-pasted the full rubric + per-iter status as the next wakeup's prompt. With cache warm this added measurable cost. Lockfile-resume + one-line wakeup prompts (see "Loop cadence") replace this entirely.
- **Watchdog session scoping is a footgun.** Watchdog hard-defaults to `twingrid-a twingrid-b`. The 2026-05-18 sprint used `8` and `r28-review-grid` and the watchdog silently watched the wrong sessions until manual kill+respawn. Prereq #4 now requires passing `SPRINT_SESSIONS` from the lockfile.
- **`.pending` short-circuit pattern was new.** Watchdog handles edit prompts; command-shape prompts that need supervisor judgment used to wait a full cycle. Writing a `.pending` marker on detection lets the next iteration know to act immediately instead of sleeping its scheduled cadence.
- **PushNotification is the right urgent channel.** Slack MCP write requires `user:mcp_servers` scope which sessions started before Slack-app install don't have. PushNotification works in every session and auto-suppresses when user is active — exactly what an AFK escalation channel should do. Slack-send is a nice-to-have for morning summaries from fresh sessions.
- **Sandbox DNS block created ~6 cycles of `gh` escalation friction.** Some agent CLIs sandbox network access; `gh` calls then need host-side approval. Manager-side batching (one `gh search prs --owner` instead of looping `gh pr list --repo X`) would cut this to one approval per sprint.
- **Manager auto-compacted cleanly at 9% → 86%** mid-sprint without incident, matching the 2026-05-12 behavior.

## Tuning notes from the 2026-05-12 session

These came out of the first overnight run; update if subsequent runs change them:

- **240s wakeup cadence was correct** — caught every stall, kept cache warm.
- **The watchdog should run if available** — without it, the supervisor model spends most of its cycles on routine edit approvals instead of judgment work.
- **Manager averaged one auto-compact every ~1.5 hours.** Always recovered cleanly (7-9% → 78-91%).
- **Grid panes started hitting weekly budget exhaustion ~5 hours in.** Manager pivoted to running select lanes from its own context — this worked. Don't try to "fix" exhausted panes from the supervisor side; just preserve their model choice via the rate-limit rubric.
- **Forward improvement (not yet implemented): multi-provider failover before manager-absorption.** When a sprinter pane exhausts its weekly budget on provider A, the *better* pivot — before falling back to the manager absorbing the lane — is for the manager to exit that pane's codex session (keeping the pane open), launch a different CLI (`claude`, `gemini`), run a brief availability probe, and resume dispatching that lane via the new provider. This is **manager** work, not supervisor work — but the supervisor needs to recognize provider-availability-probe prompts and approve them the same way it approves regular dispatch. See repo issue #166 for the infrastructure work, and the provider-agnostic note at the top of the rubric.
- **One pile-up of 10 stuck grid panes** happened when the manager was deep in a multi-merge sequence and stopped polling its own grid. Watchdog would have caught most of these.
- **A second-level sprint manager** assisted successfully — same skill, same rubric, different scope. The lockfile coordination pattern in this skill formalizes that experience.

## Tuning notes from the 2026-06-19 run (marathon-that-wasn't)

Overnight launch-hardening run that burned out at **~90 min** (real output: 5 PRs + 28 issues, all created 06:35–08:00 UTC, then the grid was dead while the supervisor kept ticking for hours). Hard lessons:

- **Detect working-vs-idle by the SPINNER/TIMER line, not a verb list.** Claude's spinner verb is whimsical and unbounded (Bootstrapping, Transfiguring, Bloviating, Garnishing, Topsy-turvying, Philosophising, Sautéed, Ebbing, Percolating, …). A regex of verbs will mislabel busy lanes as idle — this wasted ~15 cycles on 2026-06-19. Instead treat a pane as **working** iff it shows an activity marker: `\(\d+m ?\d+s ·`, `esc to interrupt`, `↓ \d`/`↑ \d` tokens, `% until auto-compact`, `\d+/\d+ agents`, or `queued`. Treat as **idle** only when the bare input prompt (`❯` / `›`) shows with no such marker AND no compose text.
- **Verify progress against SCM ground truth, never pane scrollback.** Pane spinners can outrun reality — a stalled/looping lane *looks* active. When reporting "what got done" (esp. the morning summary), pull it from the SCM: `gh pr view <n> --json additions,deletions,commits,createdAt` (real diff size + commit times) and `gh issue list --json createdAt` (when work actually stopped). On 2026-06-19 the commit timestamps proved all real output ended at ~08:00 UTC even though panes "looked busy" for hours afterward. **Build the morning summary from PR diffs/commit-times + issue-create-times, then spot-check claims (e.g. a PR with 0 additions, or whose last commit predates the run, was not actually worked).**
- **A budget that vanishes fast = runaway sub-fanout, not productivity.** When a lane reports `N/40 agents` or burns >1M tokens on one task, that's a budget bomb — surface it; it's the most likely cause of an early burnout. See Marathon mode + `feedback_marathon_grid_pattern.md`.
- **"Ran out of usage" is a distinct end state from "Goal achieved."** When grid panes show session/weekly-limit messages (`You've used N% of your session limit`) and stop producing, the marathon is *capped*, not done — say so plainly rather than narrating continued progress. Once SCM shows no new commits/issues for 2+ cycles, flip to a quiet health-watch hold and stop re-reporting "still working."
