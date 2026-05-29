---
name: sprint-supervisor
version: 1.1.0
last-updated: 2026-05-18
description: Babysit a running multi-pane WRFCoin tmux sprint while the user is AFK or asleep. Polls the manager pane and grid persona panes every ~4 min via ScheduleWakeup, auto-approves routine codex permission prompts using a fixed rubric, escalates destructive prompts, and produces a morning summary. Use this skill whenever the user says "watch the sprint", "supervise overnight", "I'm going to bed keep the sprint going", "babysit the panes", "keep an eye on twingrid", or invokes "/sprint-supervisor" — even without the word "supervisor". Scales by named scope — one instance handles a twingrid (18 panes), multiple instances divide-and-conquer a triplegrid or quadgrid by scoping each supervisor to a slice of grids (e.g. consensus, infra-backend, frontend) coordinated via /tmp lockfile so peers don't double-approve. Pairs with sprint-watchdog.sh which absorbs the mechanical ~70% of approvals; this skill handles the judgment ~30% — commands, rate-limit prompts, escalation.
---

# /sprint-supervisor

Watch an already-running tmux sprint and keep it unblocked while the user is away. The sprint manager (a codex agent in tmux window `0:0`) dispatches work to a persona grid; this skill steps in when either the manager or a grid pane stalls on a permission prompt the user would normally answer.

This skill is intentionally split from the mechanical watchdog hook. The hook absorbs the routine ~70% of approvals (plain edit prompts) without needing a model in the loop. This skill handles the judgment 30% — command approvals, rate-limit prompts, refusal-list calls, and the morning summary.

## Invocation modes

The skill scales by being invoked multiple times with different **scopes**. A scope is just a name + a set of tmux targets to watch.

**Single supervisor (default, twingrid):**
```
/sprint-supervisor
```
Scope = `default`. Watches the manager (`0:0`) and all panes in `twingrid-a` and `twingrid-b`. This is what the user almost always wants.

**Scoped supervisor (triplegrid+ or specialized):**
```
/sprint-supervisor consensus --targets twingrid-a
/sprint-supervisor infra-backend --targets twingrid-b,twingrid-c
/sprint-supervisor frontend --targets twingrid-d
```
The first token after the skill name is the scope name. `--targets` is a comma-separated list of tmux sessions (or `session:window.pane` IDs if the user wants finer granularity). The manager pane (`0:0`) is **always watched by every scope** unless the user passes `--no-manager` — the manager is the brain and you want every supervisor to notice if it dies.

**If the user invokes the skill without a clear scope and you're not sure**, ask:
> "What should I watch? Defaults: scope=`default`, targets=`twingrid-a` and `twingrid-b`. Say something like 'just the consensus grids on twingrid-a' if you want me scoped narrower."

## Dispatch modes — warm-start vs cold-start

The skill assumes a running sprint by default (warm-start). But Tony often dispatches it remotely (e.g. from the Claude mobile app while away from his desk), and in that case the sprint manager itself may not be running yet. The skill detects this on first iteration and bootstraps if needed.

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

See `references/dispatch-patterns.md` for worked patterns including the mobile cold-start handshake, the scheduled-task pattern for nightly recurring supervision, and the routines integration once that capability is generally available.

## Prerequisites (verify before starting)

1. **Auto mode is on.** Without it, you'll prompt the user on every tool call and the whole point is defeated. If auto mode is off, ask the user to enable it before continuing.
2. **Sprint manager is running** in tmux window `0:0`. Capture it once to confirm:
   ```bash
   tmux capture-pane -t 0:0 -p -S -20 | tail -20
   ```
3. **Target sessions exist.** Run `tmux list-sessions` and verify your scope's targets are present.
4. **Watchdog hook is running** (recommended, not required). The watchdog defaults to `twingrid-a twingrid-b`, so always pass your scope's actual targets via `SPRINT_SESSIONS`. Start it after writing the lockfile in step 5 so you can pull targets straight from it:
   ```bash
   SPRINT_SESSIONS="$(python3 -c "import json; print(' '.join(json.load(open('/tmp/sprint-supervisor/<scope>.lock'))['targets']))")" \
     nohup /home/tony/wrfcoin/scripts/sprint-watchdog.sh > /tmp/sprint-watchdog.log 2>&1 &
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
     "started": "$(date -Iseconds)",
     "heartbeat": "$(date -Iseconds)",
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

For each stuck pane that **isn't** claimed by a peer (from step 2), apply the rubric below. **Space approvals ~2s apart** to avoid codex-pane API overload.

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
relevant to your panes' lanes.)

The motivation is the 2026-05 WSL2 disk-bloat incident; see
`feedback_post_merge_prune.md` for the rule and rationale.

### 6. Schedule the next wakeup

Always re-schedule unless the user has returned or an escalation triggered. If escalation triggered, surface to the user and pause — don't auto-resume until the user acknowledges.

## Approval rubric

**Provider-agnostic note.** Grid panes may be running `codex` (gpt-X), `claude`, or `gemini` CLIs. The sprint-manager may also actively *migrate* a budget-exhausted pane from one provider to another (e.g. exit the codex CLI, launch `claude` in the same pane, brief availability test, resume dispatching that lane). Each CLI has its own prompt phrasing — codex says "Would you like to make the following edits?", claude says it differently, gemini differently again — but the *shapes* are the same: edit confirmation, command confirmation, rate-limit alert. Match the shape, judge the action, ignore which CLI is asking. If you see a prompt shape the rubric doesn't cover (a new CLI's UI, an unusual phrasing), fall through to the "anything else" row and lean conservative.

| Prompt pattern | Action |
|---|---|
| `Would you like to make the following edits?` with `1. Yes / 2. don't ask again for these files (a) / 3. No` | `a Enter` |
| `Would you like to make the following edits?` with `1. Yes / 2. No` (no `a` option) | `y Enter` |
| `Would you like to run the following command?` for benign read-only (`npm audit`, `cargo test`, `cargo check`, `gh pr view`, `gh pr list`, `gh issue view`, `git status`, `git diff`, `git log`, `ls`, `find` with `-maxdepth`) | `p Enter` (always-allow) |
| `Would you like to run the following command?` for `gh pr create/comment/ready/merge`, `gh issue close/comment`, `git push` to a feature/codex branch, `git rebase`, `git push --force-with-lease` to a feature branch | `y Enter` |
| `Would you like to run the following command?` for `ssh` read-only ops on the N5 host (`python3 node-dashboard.py`, `docker ps`, `find`, `ls`, `git status`) | `y Enter` |
| `Approaching rate limits — Switch to gpt-5.4-mini?` | `2 Enter` (Keep current model). The reason is **not** that downshifting is always wrong — it's that the sprint-manager may have a better plan (e.g. migrate the pane to a different provider entirely: codex → claude → gemini). Preserving model choice keeps that path open. The manager owns the pivot; the supervisor just doesn't shortcut it. |
| Provider availability test prompt (sprint-manager dispatching a brief "are you up?" probe to a freshly-launched `claude` or `gemini` in a previously-exhausted pane) | Same rules as the corresponding edit/command rubric row apply — judge by shape, not by which CLI is asking. |
| Anything else, or a command you can't immediately classify | Capture the last 40 lines first (`tmux capture-pane -p -t <pane> -S -40`), then judge. Lean conservative — when in doubt, escalate, don't approve. |

The reason this rubric is structured by prompt-pattern rather than by command-substring is that codex's prompt UI is the stable surface — its options change rarely. Command shapes are not. Match the prompt, then sanity-check the command, then act.

## Refusal list — do NOT auto-approve, escalate to user

If a prompt requests any of these, **do not approve and do not dismiss**. Capture context, fire a `PushNotification` to wake the user, append to `notable_events`, surface it in your next response, and pause the loop:

- `rm -rf` targeting paths outside `/home/tony/wrfcoin/worktrees/` or `/tmp/`
- `DROP TABLE`, `DROP DATABASE`, `redis-cli FLUSHALL`, or any other live-data wipe
- `git push --force` (without `--with-lease`) to `main` or `master`
- `git push` to `main` directly (not via PR merge)
- Anything that prints, exfiltrates, or writes secrets / env files / private keys
- `git branch -D` against more than 2 branches in one command
- Live service restart on the N5 testnet that isn't authorized by the active handoff contract
- Any command modifying `~/.ssh/`, system services, or sudo state

The reason these are hard-stop is that the cost of approving one wrong is catastrophic (data loss, leaked secrets, broken production) while the cost of waking the user is merely annoying. The asymmetry argues for caution.

## AFK notifications

The supervisor runs to keep the sprint going while Tony is AFK or asleep. Two outbound channels exist; use both when appropriate.

**Primary: `PushNotification` tool.** Always available, no auth dependency. Auto-suppresses when Tony is at the keyboard (last keystroke < 60s) so it doesn't distract him mid-work. Use it for the **urgent path** — anything that would otherwise sit until the next wakeup cycle and matters enough to interrupt him:

- Refusal-list trigger (see below). Send BEFORE pausing the loop so he sees it on his phone.
- Manager death / "Waiting for background terminal" >20 min.
- Pile-up of >8 stuck grid panes.
- Provider failover that needs his decision (manager exhausted weekly budget on all providers).

Keep messages under 200 chars, one line, no markdown. Lead with what he'd act on. Examples:

```
PushNotification(status="proactive", message="sprint-supervisor escalation: 10 grid panes stuck, manager may be dead. Pane tails in next reply.")
PushNotification(status="proactive", message="REFUSAL: manager tried git push --force to main. Paused. Open the CLI to review.")
```

Don't notify for routine progress, individual merge approvals, or anything you can handle inside the rubric without him.

**Secondary: Slack `slack_send_message`** (best-effort, may fail). Use for **morning summaries** and other non-urgent posts that benefit from markdown / threading / phone reply. Wrap in a try/except — if the call fails with `OAuth token does not meet scope requirement user:mcp_servers`, silently skip Slack and write the same summary to `/tmp/sprint-supervisor/<scope>.summary.md` for him to read in the terminal next time he invokes the supervisor.

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

**Configuring the Slack channel.** First-time setup: if `~/.claude/sprint-supervisor-slack.json` doesn't exist, ask the user once which channel/DM to use, save the channel_id to that file, and reuse it forever. Don't prompt every time.

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

When the user grows past twingrid (triplegrid = 27-36 agents, quadgrid = 36-45), they'll typically run multiple supervisors in separate Claude sessions, each scoped to a topic-coherent slice of grids. Examples:

- **`consensus`** scope watches the smart-contracts and core4 persona grids (where most cross-pane coordination happens).
- **`infra-backend`** scope watches the infra and backend persona grids.
- **`frontend`** scope watches the frontend and UX grids.

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
2. **Merges that landed** — grouped by repo (core4 / infra / backend / frontend / smart-contracts), with PR numbers.
3. **Issues closed** — grouped by repo.
4. **N5 Pro testnet** — starting state → ending state (height, peers, alerts, svc up). Only if your scope touches N5 diagnostics.
5. **What I handled directly** — count of stuck-pane approvals, ssh diagnostics approved, rate-limit prompts answered.
6. **Caveats / things to review** — panes that exhausted weekly budget, anything escalated, anything ambiguous.

Cite PR numbers as `wrfcoin/<repo>#NNNN` so the user can click. See `references/morning-summary.md` for a worked example with the exact phrasing patterns that have worked well.

**Delivery.** When the supervisor first detects `current_phase` flipping to `idle` (sprint complete), build the summary once and:
1. Save to `/tmp/sprint-supervisor/<scope>.summary.md` (always — this is the canonical copy).
2. Try `slack_send_message` to the configured channel; on scope failure, silently skip.
3. Render it as your next user-facing response.

Don't re-deliver the same summary on every subsequent idle cycle — track `summary_delivered_at` in the lockfile.

## What this skill does NOT do

- **Doesn't dispatch new work** to grid panes. The manager owns that.
- **Doesn't merge PRs.** The manager owns that.
- **Doesn't `/clear` or `/compact`** the manager. Let it self-compact.
- **Doesn't touch the live N5 testnet directly** — only approves the manager's read-only diagnostics.
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

Second full-sprint run (4 rounds, 32 PRs merged across 32 instrument repos, ~2h 12m manager runtime, 35 supervisor cycles). New findings:

- **Adaptive cadence beats fixed 240s.** Prompt density is front-loaded (dispatch, first verify sweep, first PR creation all within the first ~10 min) and tails to zero once "Goal achieved" appears. The 30/240/1800 schedule formalized above came from manually ramping cadence during this run and saved an estimated half-dozen unnecessary cycles in the idle phase.
- **Wakeup-prompt re-pasting was wasteful.** ~30 cycles each re-pasted the full rubric + per-iter status as the next wakeup's prompt. With cache warm this added measurable cost. Lockfile-resume + one-line wakeup prompts (see "Loop cadence") replace this entirely.
- **Watchdog session scoping is a footgun.** Watchdog hard-defaults to `twingrid-a twingrid-b`. The 2026-05-18 sprint used `8` and `r28-review-grid` and the watchdog silently watched the wrong sessions until manual kill+respawn. Prereq #4 now requires passing `SPRINT_SESSIONS` from the lockfile.
- **`.pending` short-circuit pattern was new.** Watchdog handles edit prompts; command-shape prompts that need supervisor judgment used to wait a full cycle. Writing a `.pending` marker on detection lets the next iteration know to act immediately instead of sleeping its scheduled cadence.
- **PushNotification is the right urgent channel.** Slack MCP write requires `user:mcp_servers` scope which sessions started before Slack-app install don't have. PushNotification works in every session and auto-suppresses when user is active — exactly what an AFK escalation channel should do. Slack-send is a nice-to-have for morning summaries from fresh sessions.
- **Codex sandbox DNS block created ~6 cycles of `gh` escalation friction.** See `[[codex_sandbox_dns_blocked]]`. Manager-side batching (one `gh search prs --owner` instead of looping `gh pr list --repo X`) would cut this to one approval per sprint.
- **Manager auto-compacted cleanly at 9% → 86%** mid-sprint without incident, matching the 2026-05-12 behavior.

## Tuning notes from the 2026-05-12 session

These came out of the first overnight run; update if subsequent runs change them:

- **240s wakeup cadence was correct** — caught every stall, kept cache warm.
- **The watchdog should run if available** — without it, the supervisor model spends most of its cycles on routine edit approvals instead of judgment work.
- **Manager averaged one auto-compact every ~1.5 hours.** Always recovered cleanly (7-9% → 78-91%).
- **Grid panes started hitting weekly budget exhaustion ~5 hours in.** Manager pivoted to running select lanes from its own context — this worked. Don't try to "fix" exhausted panes from the supervisor side; just preserve their model choice via the rate-limit rubric.
- **Forward improvement (not yet implemented): multi-provider failover before manager-absorption.** When a sprinter pane exhausts its weekly budget on provider A, the *better* pivot — before falling back to the manager absorbing the lane — is for the manager to exit that pane's codex session (keeping the pane open), launch a different CLI (`claude`, `gemini`), run a brief availability probe, and resume dispatching that lane via the new provider. This is **manager** work, not supervisor work — but the supervisor needs to recognize provider-availability-probe prompts and approve them the same way it approves regular dispatch. See `sprint-supervisor-issues-to-file.md` Issue 7 for the infrastructure work, and the provider-agnostic note at the top of the rubric.
- **One pile-up of 10 stuck grid panes** happened when the manager was deep in a multi-merge sequence and stopped polling its own grid. Watchdog would have caught most of these.
- **A second-level sprint manager** assisted successfully — same skill, same rubric, different scope. The lockfile coordination pattern in this skill formalizes that experience.
