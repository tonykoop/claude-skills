# Dispatch patterns

Concrete patterns for how the supervisor gets invoked and how it bootstraps. The skill body covers the basic invocation modes; this reference covers the more involved cases — mobile cold-starts, scheduled recurring supervision, and the forward-looking routines integration.

## 1. Warm-start (default, in-person)

User is at the desk. Sprint manager is already running. They type `/sprint-supervisor` either to hand off before leaving or to recover an interrupted supervisor session.

Steps:
1. Verify manager alive (`tmux capture-pane -t 0:0` shows codex/claude UI).
2. Verify targets exist (`tmux has-session -t twingrid-a` etc.).
3. Claim lockfile, schedule the first wakeup.
4. Done.

No bootstrap needed. This is the path the skill body describes step-by-step.

## 2. Mobile cold-start (remote dispatch)

User is on their phone, PC is at home. They open Claude mobile and type `/sprint-supervisor cold-start` or just `/sprint-supervisor` (with the explanation that nothing is running yet).

The handshake:

```
User → "Start an overnight sprint, scope default, work the wrfcoin sprint queue."
Skill → "Confirming cold-start: no manager pane in 0:0, no twingrid-* sessions
         exist. I'll dispatch the sprint-manager skill to set up twingrid and
         start the sprint. Confirm?"
User → "yes"
Skill → [invokes sprint-manager skill with the queue context]
        [polls 0:0 every 30s until manager UI appears]
        [claims its own lockfile, begins normal loop]
        "Sprint manager is up at 22:14. First grid panes spawning now.
         I'll resume in 240s. Sleep well."
```

**Wiring caveat — this depends on Tony's specific PC/mobile setup.** The mechanism for "mobile Claude reaches the PC's tmux" is one of:

- **Cowork session is left running on the PC**, mobile app talks to the same Claude account, the cowork session receives the prompt and uses its own computer-use access to operate the local tmux. (Most likely path today.)
- **Scheduled task on the PC** that polls for a "dispatch" signal (e.g. a magic file at `/tmp/sprint-supervisor.dispatch`) and runs locally when it sees one. Mobile writes that file via a connected file-write tool.
- **SSH from a relay machine** that has access to the home network.

If the wiring isn't obvious from context, ask the user before assuming a path. Don't invent a remote-execution mechanism that isn't actually in place.

## 3. Scheduled / recurring nightly supervision

For predictable overnight sprints (e.g. "supervise every weeknight 11pm–7am"), use the **scheduled-tasks MCP** to create a recurring task rather than relying on the user remembering to dispatch.

Task setup pattern:

```
Name: sprint-supervisor-nightly
Trigger: recurring, weeknights at 22:55 local
Prompt: Run /sprint-supervisor scope=default. If the sprint manager is
        not running in tmux 0:0, perform cold-start handoff to the
        sprint-manager skill. Loop until 07:00 local or until user wakes
        the session. Then deliver the morning summary and exit.
```

Notes:
- Schedule the kickoff a few minutes *before* the expected sprint-start time, so the manager has time to bootstrap before there's work to dispatch.
- Set a hard stop time in the task prompt — without it the supervisor keeps re-scheduling itself indefinitely.
- The scheduled task is the *kickoff*. Once it fires, the supervisor's own `ScheduleWakeup` calls keep it alive through the night. They're cheaper than re-firing the scheduled task every 4 minutes.
- If `routines` (see below) is available, prefer that — scheduled-tasks is the bridge until routines lands.

## 4. Routines integration (forward-looking)

Anthropic's "routines" capability (announced, not yet GA) generalizes scheduled tasks into multi-step, state-aware workflows. Once it's stable, the supervisor's nightly pattern fits cleanly:

```
Routine: nightly-sprint
Steps:
  1. At 22:50 local → dispatch sprint-manager (cold-start the twingrid)
  2. At 22:55 local → dispatch sprint-supervisor (loop until 07:00)
  3. At 07:00 local → trigger morning summary, exit both
  4. Conditional: if escalation fires mid-routine, page user and pause
```

This is a forward reference — don't try to *use* routines syntax that doesn't exist. When routines ships, update this section with the actual invocation.

Until then, the scheduled-tasks pattern in section 3 is the closest equivalent.

## 5. Manual mid-sprint addition of a peer supervisor

User is asleep. The sprint has grown to 4 grids. The default supervisor is keeping up but barely. Tony's phone vibrates with an escalation: ">8 panes stuck simultaneously, suspect manager fell behind."

Tony's response from the phone: `/sprint-supervisor consensus --targets twingrid-c,twingrid-d`.

What should happen:
1. New supervisor starts on its own scope. Writes its lockfile.
2. **First iteration** — it reads peer lockfiles. Sees the `default` supervisor already claims `twingrid-c` and `twingrid-d` too (overlap).
3. **Conflict resolution** — its own `started` timestamp is later. It drops the conflicting targets and notes it: "Detected overlap with peer `default`. Dropping twingrid-c and twingrid-d from my scope — they're still owned by the earlier peer."
4. This isn't what Tony wanted (he intended the new supervisor to *take over* those targets).
5. To actually transfer ownership, Tony needs to issue: `/sprint-supervisor default --release twingrid-c,twingrid-d` to the existing default-scope session first. The release updates the default's lockfile to exclude those targets, then the new supervisor can claim them.

The release pattern isn't in the skill body because it adds a moving part. If Tony hits this case in practice, lift it into SKILL.md.

## 6. The dispatch decision tree

For quick triage when a user invokes the skill:

```
User invokes /sprint-supervisor
├── No args? → scope=default, targets=twingrid-a,twingrid-b. Continue.
├── Has scope name + --targets? → use them.
└── Has scope name only? → ask "what targets?"

Capture 0:0 and target sessions
├── Manager UI visible + sessions exist? → warm-start, normal loop.
├── No manager UI but sessions exist? → ask user; manager may have crashed.
├── No sessions (cold)? → confirm cold-start intent, then hand off to
│                          sprint-manager skill before claiming lockfile.
└── Mixed (some sessions exist, manager dead)? → ask user. Don't auto-recover.
```
