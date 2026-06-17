# sprint-supervisor

> Babysit a running multi-pane tmux agent sprint while you're AFK or asleep.

`sprint-supervisor` is an operational skill that watches an already-running
tmux "sprint" — a manager agent dispatching work to a grid of persona agents —
and keeps it unblocked while you're away. It polls the panes on an adaptive
cadence, auto-approves the routine permission prompts you'd otherwise answer by
hand, escalates anything destructive, and hands you a structured summary when
you return.

It is **project-agnostic**: all project-specific behavior lives in a config
file, so you can point it at any tmux agent swarm. (A worked configuration for
one real project ships as a commented example.)

## What it does

- **Polls** the manager pane (`tmux 0:0`) and your grid persona panes every
  ~4 minutes via scheduled wakeups.
- **Auto-approves** routine agent prompts (edit confirmations, benign read-only
  commands, feature-branch pushes/PRs) using a configurable rubric matched by
  *prompt shape*, so it works across codex / claude / gemini / agy CLIs.
- **Refuses & escalates** destructive prompts (data wipes, force-push to
  protected branches, secret exfiltration, permission-policy broadening) —
  it pings you and pauses instead of guessing.
- **Coordinates** with peer supervisors via `/tmp` lockfiles so multiple
  instances can divide a large grid without double-approving.
- **Summarizes** the run (merges landed, issues closed, what it handled,
  caveats) when the sprint goes idle.

## The watchdog-vs-skill split

There are two layers, on purpose:

| Layer | What it is | Handles | Model in loop? |
|---|---|---|---|
| **`sprint-watchdog.sh`** | A shell hook running in the background | The mechanical ~70%: plain edit-confirmation prompts | No |
| **`sprint-supervisor` (this skill)** | A scheduled-wakeup skill | The judgment ~30%: command approvals, rate-limit prompts, refusal-list calls, escalation, the morning summary | Yes |

The watchdog clears the high-volume, low-judgment prompts without spending model
tokens. The skill wakes on a cadence to handle the prompts that actually need a
decision. The watchdog can also drop a `.pending` marker when it sees a
command-shape prompt it deliberately won't touch, so the skill acts on it
immediately instead of waiting a full cycle.

## Lockfile coordination

Each supervisor instance claims a **scope** (a name + a set of tmux targets) by
writing `/tmp/sprint-supervisor/<scope>.lock`. The lockfile is also where the
skill persists state across wakeups, so the wakeup prompt itself stays one line.

- Before approving any pane, a supervisor reads peer lockfiles and skips panes a
  peer already claims with a fresh (<15 min) heartbeat.
- On accidental overlap, the supervisor with the **earlier `started` timestamp**
  keeps the contested panes; the later one drops them. Deterministic, no
  negotiation.
- The manager pane (`0:0`) is watched by **every** scope — it's shared
  infrastructure and you want every supervisor to notice if it dies.

This lets one supervisor handle a "twingrid" (~18 panes) and several supervisors
divide a triplegrid/quadgrid by topic.

## Why ~240s cadence

Cadence is adaptive (`30s` / `240s` / `1800s`) and driven by a phase field in
the lockfile:

- **Cold-start (~30s, clamped to 60s):** prompts cluster at sprint kickoff
  (dispatch, first verification sweep). Front-loading attention reduces friction.
- **Active (240s):** the working default. The key constraint is the **prompt
  cache** — staying **under 300s keeps the cache warm**, so each wakeup is cheap.
  240s gives margin under that ceiling while still catching stalls quickly.
- **Idle (1800s):** once the sprint reports "Goal achieved" and goes quiet,
  sleep long. You eat one cache miss per cycle but earn it back by not waking
  through long silent stretches.

The deliberately-avoided value is ~300s: it's the "worst of both" — long enough
to drop the cache, short enough to wake too often.

## Configuration

Project-specific behavior lives in a YAML config. The skill looks for it in this
order and uses the first that exists:

1. `$SPRINT_SUPERVISOR_CONFIG`
2. `~/.claude/sprint-supervisor-config.yaml`
3. `references/supervisor-config.example.yaml` (bundled generic defaults)

To customize, copy the example and edit:

```bash
cp references/supervisor-config.example.yaml ~/.claude/sprint-supervisor-config.yaml
$EDITOR ~/.claude/sprint-supervisor-config.yaml
```

The config controls:

- `workspace_dir` / `worktrees_dir` — roots treated as safe to operate within.
- `protected_branches` — never force-push or push-to directly.
- `trusted_hosts` — hosts whose **read-only** diagnostics may be auto-approved
  (empty by default; nothing is trusted until you add it).
- `refusal_list.extra_patterns` — project additions to the built-in baseline.
- `approval_rubric.benign_readonly_extra` — extra read-only commands to allow.
- `labels` — morning-summary `repo_groups` and `pr_citation_format`.
- `notifications` — `PushNotification` toggle and Slack channel id.

If only the bundled example is found, the skill runs with conservative generic
defaults and prompts you once to create your own copy.

## Quickstart

1. **Start your sprint** (manager in tmux `0:0`, persona panes in target
   sessions). Make sure agents run in true auto mode, not `acceptEdits`.
2. **Configure** (first time only): copy the example config and set your
   `workspace_dir`, `protected_branches`, and any `trusted_hosts`.
3. **Supervise.** Invoke the skill:
   ```
   /sprint-supervisor
   ```
   (or with a scope: `/sprint-supervisor group-a --targets twingrid-a`). It
   claims a lockfile, optionally starts the watchdog, and begins the wakeup loop.
   Cold-start from your phone works too — if no manager is running, it confirms
   once and hands off to the sprint-manager skill to stand the topology up.
4. **Walk away.** It approves routine prompts, refuses destructive ones (pinging
   you via `PushNotification`), and runs a periodic post-merge prune sweep.
5. **Morning summary.** When the sprint goes idle it builds a summary (merges,
   issues closed, what it handled, caveats), posts it to Slack if configured,
   and renders it as its next reply. Dismiss the supervisor to clean up.

## What it does NOT do

It never dispatches work, never merges PRs, never `/clear`s or `/compact`s the
manager, and never touches a live production/testnet host directly — it only
approves or refuses what the manager asks. The one exception is a safe-by-default
post-merge worktree prune sweep (refuses unmerged/dirty branches).

## See also

- `references/supervisor-config.example.yaml` — config schema + worked example.
- `references/release-decision.md` — the ADR behind the generic/config split.
- `references/scaling-topology.md` — multi-supervisor topology patterns.
- `references/morning-summary.md` — summary template and worked example.
- `references/dispatch-patterns.md` — warm/cold-start and recurring-supervision.
- `CHANGELOG.md` — version history.
