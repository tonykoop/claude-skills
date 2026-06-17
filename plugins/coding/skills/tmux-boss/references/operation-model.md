# Operation Model

How the supervisor runs, and why. All values here are defaults a profile may
override; none are project-specific.

## Watchdog vs. skill split

Approvals fall into two buckets:

- **Mechanical (~majority):** plain, low-risk prompts (e.g. routine file
  edits). A shell **watchdog hook** approves these with no model in the loop.
  It is fast, cheap, and deterministic.
- **Judgment (~minority):** command execution, rate-limit prompts, anything on
  the refusal list, ambiguous scope. **This skill** handles these, plus the
  morning summary.

Keeping the mechanical majority in a hook means the model is only invoked when
judgment is actually required. The watchdog's path and the notify command are
profile-supplied, not committed here.

## Cadence (default 240s)

The default poll interval is **240 seconds**. Rationale:

- Long enough that the supervisor is not spamming captures or burning tokens on
  a quiet grid.
- Short enough that a pane blocked on a prompt is unblocked within a few
  minutes, which is well inside the time a worker would otherwise sit idle.
- A profile may shorten it for high-throughput grids or lengthen it overnight.

## Lockfile coordination

When a topology is large enough to need multiple supervisors, each is invoked
with a distinct **scope** (a name + a set of tmux targets). To prevent two
supervisors from approving the same prompt:

- Each supervisor takes a per-prompt lock in a shared `/tmp` lockfile keyed by
  the pane identity before acting.
- If the lock is already held, the peer skips that prompt.
- The manager pane is watched by every scope (so a manager death is always
  noticed) but its prompts are also lock-guarded.

This lets a triple/quad-grid be divided across supervisors without double
approvals, and degrades cleanly to a single supervisor when only one scope is
running.

## Escalation policy

Escalate (notify the operator, take no approving action) when a prompt is:

- destructive (delete, force-push, drop, reset --hard, prod mutation),
- on the profile's refusal list,
- a rate-limit / quota prompt,
- ambiguous about scope or target.

Everything else that matches the safe-approval rubric may be auto-approved.

## Morning summary

On operator return (or end of window), emit: counts of auto-approved vs.
escalated prompts, any panes still stalled, any panes that died and whether
they recovered, and the open escalations awaiting a decision.
