---
name: tmux-boss
version: 0.1.0
last-updated: 2026-06-15
status: active
description: >-
  Supervise an already-running multi-pane tmux agent swarm while the operator
  is away. Polls a manager pane and worker panes on a fixed cadence,
  auto-approves routine permission prompts using a configurable rubric,
  escalates anything destructive or ambiguous, and produces a morning summary.
  Use when the operator says "watch the swarm", "supervise overnight", "keep an
  eye on the panes", or invokes the supervisor command. Scales by named scope:
  one instance watches one grid; multiple instances divide a larger topology,
  coordinating through a lockfile so peers do not double-approve. Project
  topology (grids, pane IDs, refusal classes, watchdog wiring) is
  configuration, supplied by a profile — not baked into this skill. Do not use
  to launch or define the swarm itself (that is the manager's job); do not use
  for single-agent sessions with no tmux grid.
---

# tmux-boss

Generic, project-neutral operational supervisor for a tmux-based agent swarm.
It keeps an already-running sprint unblocked while the operator is AFK: it does
not start the swarm, define personas, or own the grid topology — it watches and
unblocks.

> This is the public extraction of the portable supervision pattern described
> in `docs/release-readiness/sprint-supervisor-decision.md` (staged-extraction
> decision for #164). It ships in the `coding` plugin and is registered in
> `manifest.yaml`. Project-specific behavior (named grids, pane IDs, refusal
> classes, watchdog paths) is **not** baked in here — it lives in a separate
> private adapter/profile (e.g. `sprint-supervisor`) that supplies a config
> profile to this generic core.

## What it does

1. **Poll** the manager pane and the worker panes in its scope on a fixed
   cadence (default 240s — see `references/operation-model.md` for the
   rationale).
2. **Classify** any pane that is blocked on a permission prompt using a
   configurable approval rubric (`references/approval-rubric.example.md`).
3. **Act**: auto-approve prompts that match the safe-approval shape; **escalate**
   (notify, do not answer) anything destructive, ambiguous, rate-limit-related,
   or on the refusal list.
4. **Summarize**: emit a morning summary of what was approved, escalated, and
   what stalled.

## Split from the mechanical watchdog

This skill is deliberately the *judgment* half. A mechanical watchdog hook
absorbs the routine majority of approvals (plain edit prompts) with no model in
the loop; this skill handles the minority that needs judgment — command
approvals, rate-limit prompts, refusal-list calls, and the summary. The split
and the lockfile coordination are documented in `references/operation-model.md`.

## Configuration (profile, not code)

Everything project-specific is supplied by a profile so the skill stays
neutral:

- **scope**: a name + the set of tmux targets to watch (sessions or
  `session:window.pane` IDs). The manager pane is watched by every scope
  unless explicitly disabled.
- **cadence**: poll interval (default 240s).
- **approval rubric**: the prompt shapes that may be auto-approved.
- **refusal list**: command classes that must always escalate.
- **watchdog hook path / notify command**: supplied by the profile.

No profile values are committed in this package; see the `.example` reference
for shape only.

## Invocation modes

- **Single supervisor (default):** watch the manager + all panes in one grid.
- **Scoped supervisors (larger topologies):** run multiple instances, each
  scoped to a named slice, coordinating via a `/tmp` lockfile so two
  supervisors never approve the same prompt.

## Do not use for

- Launching, defining, or dispatching the swarm — that is the manager skill.
- Single-agent sessions with no tmux grid.
- Answering destructive prompts on the operator's behalf — those always
  escalate.

## Relationship to `sprint-supervisor`

`sprint-supervisor` (private, project-specific) becomes a thin adapter over
this generic core: it supplies the profile (its grids, pane IDs, refusal
classes, watchdog wiring). This package must not contain those specifics.
