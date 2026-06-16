# Routines integration (forward-looking)

> **Status: BLOCKED on Anthropic routines GA. Forward-looking design only — do NOT
> implement runtime until the capability ships. Last reviewed 2026-06-15.**

This doc is the design home for issue #161. It fleshes out the `nightly-sprint`
routine sketch and documents how a user migrates from today's scheduled-tasks
bridge to a routine *once routines is generally available* — without losing a
night of supervision in the cutover.

It deliberately does **not** add runtime to the skill. There is nothing to wire
up here today. When routines ships, the migration path below becomes actionable;
until then, the live mechanism remains the scheduled-tasks MCP bridge documented
in `dispatch-patterns.md` §3, and the mobile cold-start watcher in
`dispatch-patterns.md` §2.

## Why routines (vs. today's scheduled task)

`dispatch-patterns.md` §3 ("Scheduled / recurring nightly supervision") fires a
single recurring *kickoff* — the supervisor's own `ScheduleWakeup` calls carry
it through the night. That works, but the kickoff is a one-shot prompt: it can't
express *steps*, *ordering between the manager and the supervisor*, a hard stop
that's a first-class concept rather than prose in the prompt, or a *conditional
branch* (escalation → pause → page → await ack). All of that lives inside the
single Claude session today, recreated from the prompt text each night.

Routines (announced, not yet GA) generalize scheduled tasks into multi-step,
state-aware workflows. The nightly sprint maps onto that shape cleanly: it is
genuinely a small ordered workflow with one conditional. See the forward-looking
pointer in `dispatch-patterns.md` §4, which this doc expands.

## The `nightly-sprint` routine design

Fleshing out the four-step sketch from §4 of `dispatch-patterns.md` and issue
#161. This is a *design*, not a runnable artifact.

**Step 1 — 22:50 local: cold-start dispatch (sprint-manager).**
Stand up the tmux topology (twingrid by default) and start the sprint manager,
exactly as the mobile cold-start handshake in `dispatch-patterns.md` §2 does it.
The routine plays the role the magic-file watcher plays today: it *is* the
always-on trigger, so the phone→PC transport in §2 is no longer the only way to
kick a cold-start. Scheduling the manager 5 min ahead of the supervisor gives it
time to bootstrap before there's anything to supervise (same rationale as the
"schedule the kickoff a few minutes before" note in §3).

**Step 2 — 22:55 local: dispatch sprint-supervisor (loop until 07:00).**
Run `/sprint-supervisor scope=default` and let it enter its normal adaptive loop
(the 30s/240s/1800s cadence in SKILL.md "Loop cadence"). The routine does *not*
re-implement the loop — once the supervisor is running, its own `ScheduleWakeup`
calls carry it through the night, which is cheaper than re-firing a routine step
every 4 minutes. The routine's job is to *start* the supervisor and to own the
hard-stop and the conditional, not to babysit each cycle. The `07:00` hard stop
is passed to the supervisor as its terminal condition (mirrors the `hard_stop`
field in the dispatch-file shape in §2).

**Step 3 — 07:00 local: morning summary, exit both.**
Trigger the supervisor's "Morning summary" path (SKILL.md "Morning summary" —
build once, save to `/tmp/sprint-supervisor/<scope>.summary.md`, attempt Slack,
render), then run the supervisor's "On exit" cleanup (remove the lockfile and
`.pending`, stop the watchdog if the routine started one, stop rescheduling).
Then exit the manager. The routine is responsible for the *deterministic* 07:00
exit that prose-in-a-prompt makes unreliable today.

**Step 4 — Conditional: escalation mid-routine → pause → page → await ack.**
If any refusal-list trigger or escalation trigger fires while the routine is
running (SKILL.md "Refusal list" and "Escalation triggers"):

1. **Pause** the routine — do not advance to the 07:00 exit, do not let the
   supervisor auto-resume its loop. The night's supervision is frozen in place,
   not abandoned.
2. **Page** the user via `PushNotification` (the urgent channel — SKILL.md "AFK
   notifications"), with the one-line summary already specified there.
3. **Await ack.** The routine stays paused until the user acknowledges. On ack,
   the user chooses: resume the loop, or exit early with a partial morning
   summary. The routine must not silently self-resume — that's the whole point
   of the refusal-list asymmetry (waking the user is cheap; approving one wrong
   destructive command is catastrophic).

This conditional is the piece scheduled-tasks cannot express today: a recurring
task can fire a kickoff, but it has no notion of "pause this run and wait for a
human" as a first-class state.

### Illustrative pseudo-syntax (NOT real — pending actual routine syntax)

> **The block below is illustrative only.** The real routines API/syntax is not
> yet known. Do not copy this into a config file and expect it to run, and do not
> cite it anywhere as the concrete API. When routines ships, replace this block
> with the real syntax and drop this warning.

```yaml
# ILLUSTRATIVE — pending real routine syntax. Do not implement.
routine: nightly-sprint
timezone: America/Los_Angeles
schedule: weeknights            # real recurrence syntax TBD
steps:
  - at: "22:50"
    do: dispatch
    skill: sprint-manager
    args: { topology: twingrid, queue: wrfcoin, mode: cold-start }
  - at: "22:55"
    do: dispatch
    skill: sprint-supervisor
    args: { scope: default, hard_stop: "07:00" }
  - at: "07:00"
    do: finalize
    actions: [morning_summary, supervisor_exit, manager_exit]
on_event:                        # real conditional/event syntax TBD
  escalation:                    # refusal-list OR escalation trigger fires
    - pause
    - page: { channel: push, message: "nightly-sprint paused: escalation. Open the CLI to review." }
    - await_ack                  # do NOT auto-resume
```

Everything about field names, the recurrence grammar, and how `on_event` binds
to the supervisor's existing `PushNotification` escalations is a guess. Treat the
*shape* (ordered timed steps + one conditional) as the stable design intent; the
*syntax* is a placeholder.

## Migration path: scheduled-task → routine (post-GA)

The goal of the migration is a clean cutover with **zero lost nights of
supervision**. The risk is the obvious one: disable the old scheduled task, the
new routine misfires on its first real night, and the sprint runs unsupervised
(or doesn't run at all). The strategy is overlap-then-cutover, never
flip-and-pray.

### Phase 0 — preconditions

- Routines is actually GA (this whole doc is unblocked).
- The pseudo-syntax above has been replaced with the real syntax and the routine
  authored but **disabled** (or scheduled for a night you'll be awake to watch).
- The existing `sprint-supervisor-nightly` scheduled task (dispatch-patterns.md
  §3) is still **enabled and untouched**. Do not delete it yet.

### Phase 1 — overlap dry-run (one night, attended)

Run the new routine on a night the user is around, with the old scheduled task
still enabled. To avoid two managers fighting over `tmux 0:0`:

- **Either** point the routine at a throwaway scope/topology (e.g. a
  `migration-test` scope on a separate tmux session) so it doesn't collide with
  the production scheduled task, **or**
- temporarily disable the old scheduled task for that one night *only because the
  user is awake to manually fall back to warm-start (§1) if the routine fails*.

The first option is safer — it tests the routine end-to-end without ever putting
a real night's supervision at risk. Use it unless you specifically need to test
the routine against the production scope.

Success criteria for the dry-run:
- Step 1 cold-starts the manager (manager UI in `0:0` within ~5 min).
- Step 2 brings the supervisor up and it enters its adaptive loop (lockfile
  written, heartbeat refreshing).
- Step 4 conditional verified at least once — deliberately trip an escalation
  (e.g. a benign refusal-list-shaped prompt in a scratch pane) and confirm the
  routine pauses, pages, and waits for ack rather than barrelling to 07:00.
- Step 3 fires at the hard stop: morning summary written to
  `/tmp/sprint-supervisor/<scope>.summary.md`, lockfile + `.pending` cleaned up,
  watchdog stopped, both manager and supervisor exited.

### Phase 2 — cutover (only after one clean night)

**Disable the old scheduled task only after the routine has run one clean,
unattended night** against the real production scope. Sequence:

1. Enable the routine on the production scope. **Leave the old scheduled task
   enabled too** for this first production night.
2. To prevent both firing the same night, give the routine a kickoff time that
   precedes the scheduled task and have it claim the production lockfile first —
   the existing peer-coordination rule (SKILL.md "Coordination with peer
   supervisors": earlier `started` timestamp wins overlap) means the
   scheduled-task supervisor, firing 5 min later, will read the routine's fresh
   lockfile, find its scope already claimed, and stand down. This is the same
   deterministic conflict resolution already in the skill — the migration reuses
   it instead of inventing a new lock. (Confirm this is actually what happens on
   the dry-run; if the scheduled-task supervisor does *not* cleanly stand down on
   a fully-claimed scope, fall back to the throwaway-scope approach and don't run
   both against production simultaneously.)
3. After **one clean unattended night** where the routine owned the whole night
   end-to-end (manager up, supervisor looped, morning summary delivered, clean
   exit, no double-dispatch), disable the old `sprint-supervisor-nightly`
   scheduled task.
4. Do not delete the scheduled task — disable it. Keep it as the rollback target.

### Rollback

If the routine misbehaves on any production night (fails to cold-start, double-
dispatches, skips the conditional, doesn't exit at the hard stop):

1. Re-enable the old `sprint-supervisor-nightly` scheduled task immediately —
   it's still present (Phase 2 step 4 disabled, never deleted it). The next
   night is covered by the known-good bridge.
2. Disable the routine.
3. Capture what the routine did wrong (the routine's own run log + the
   supervisor lockfile's `notable_events` + the `<scope>.summary.md` if one was
   written) before re-attempting Phase 1.

The invariant across the whole migration: **at every moment, exactly one of {old
scheduled task, new routine} is the live nightly trigger for the production
scope — never zero (a lost night), never two against the same scope (a double-
dispatch).** Overlap is only ever allowed against a throwaway scope or on an
attended night.

## Cross-references (do not duplicate)

- `dispatch-patterns.md` §3 — the scheduled-tasks MCP bridge this routine
  replaces. The migration's "old" side.
- `dispatch-patterns.md` §4 — the forward-looking routines pointer this doc
  expands; §4 links here.
- `dispatch-patterns.md` §2 — mobile cold-start handshake + dispatch-file shape
  (`hard_stop`, atomic claim) the routine's Step 1 reuses.
- `SKILL.md` "Loop cadence", "Refusal list", "Escalation triggers", "AFK
  notifications", "Morning summary", "On exit", "Coordination with peer
  supervisors" — the existing behaviors the routine *orchestrates* rather than
  reimplements.
