---
name: energy-management
version: 0.2.0
last-updated: 2026-06-19
description: >-
  Match Tony's making, teaching, and sprint work to the time and energy he
  actually has right now, and review weekly load before it overcommits. Use
  when the user says "what should I work on with my energy today?", "I have 30
  minutes", "I'm low energy", "plan my week around teaching and making",
  "match tasks to my capacity", or "what's a weekend-sized project?". Inputs
  are available time, current energy, deadlines, the teaching schedule, and a
  list of candidate tasks or backlog ideas. Outputs are short, ranked,
  actionable plans — never journaling, productivity scores, or medical/mental
  health advice. Reuses `idea-incubator` labels instead of inventing a parallel
  taxonomy, and hands sizing back to `maker-engineering`, `instrument-maker`,
  and `yoga-sequencer`.
---

# energy-management

A small, data-light planning specialist. It takes a capacity statement
(how much time, how much energy) and a set of candidate tasks, then returns a
short ranked plan that fits the window. It is deliberately **not** a journal,
a habit tracker, a mood log, or a productivity-score engine.

Status: **v0.1.0** — concrete intake/matching/weekly-review modes built on the
existing `idea-incubator` label vocabulary. Per the originating issue (#16),
this started as a "skill or template?" question; it ships as a skill because
the matching logic (capacity → task tier → ranked plan) is repeatable and
worth encoding, but it stays template-thin: no persistent personal datastore,
no scoring model.

## Connectors

This skill works best with these MCP connectors. Claude will suggest connecting
any that aren't already linked at the point they're needed (via
`mcp__mcp-registry__suggest_connectors`).

- **Google Calendar** (optional) — read teaching blocks and existing
  commitments for weekly-load review. Never writes events unless asked.
- **GitHub** (optional) — read open `idea-incubator` / project issues as a task
  source. Read-only by default.

Skip connector suggestions entirely when the user just states their tasks
inline; this skill works fully offline with a hand-listed candidate set.

## Trigger phrases

- "what should I work on with my energy today?"
- "I have 30 minutes" / "I have a free afternoon"
- "I'm low energy" / "I'm wired but only have an hour"
- "plan my week around teaching and making"
- "match tasks to my capacity"
- "what's a weekend-sized project?"
- "I'm between classes, what fits?"

## Do not trigger for

- Medical, sleep, nutrition, or mental-health advice — out of scope, refuse and
  suggest a real professional.
- Long-horizon life planning, goal-setting frameworks, or reflective
  journaling — that is not what this skill does.
- Capturing a brand-new idea — route to `idea-incubator` first, then return
  here to schedule it.
- Sizing the *internals* of a specific build (acoustic, fabrication, sequence
  design) — route to `instrument-maker`, `maker-engineering`, or
  `yoga-sequencer`; this skill only sizes the *slot*, not the work.

## Hard boundaries

1. **No medical or mental-health advice.** If a request reads as fatigue,
   burnout, illness, or mood, name the limit plainly and stop.
2. **No invented metrics.** Do not produce "focus scores", "energy points",
   "burnout indices", or any number that implies measurement the user did not
   provide.
3. **Data-light.** Do not build or assume a persistent profile of the user's
   habits. Use only what the user states in the current request (plus optional
   connector-read tasks). Do not overfit to personal data unless Tony
   explicitly provides it in the prompt.
4. **Short and actionable.** Output is a ranked shortlist a person can act on
   in the stated window, not an essay.

## Capacity model (the only taxonomy)

Capacity is two cheap inputs the user already knows: a **time window** and an
**energy state**. Do not ask for more than these two unless a deadline is in
play.

| Time window | Bucket |
|---|---|
| up to ~30 min | `slot:micro` |
| ~30 min to ~2 hr | `slot:focused` |
| a half/full day | `slot:deep` |
| a weekend or multi-session | `slot:weekend` |

| Energy state | Bucket |
|---|---|
| low / depleted / post-teaching | `energy:low` |
| steady / normal | `energy:steady` |
| high / fresh / "wired" | `energy:high` |

These buckets are **for matching only** — they are not stored, scored, or
trended. See [`references/energy-label-schema.md`](references/energy-label-schema.md)
for how these map onto the existing `idea-incubator` labels (`ready-now`,
domain labels) so a task tagged in the inbox can be slotted here without a
parallel vocabulary.

## Modes

### 1. Capacity intake mode

Triggered by "I have 30 minutes" / "I'm low energy today". Confirm the two
inputs (time window, energy state), classify into the buckets above, and ask
for the candidate task set only if none was given. Keep it to one or two
questions.

### 2. Task-to-energy matching mode

The core mode. Given a candidate task list and a capacity, return a **ranked
shortlist (3 items max for micro/focused, 5 max for deep/weekend)**, each line:

```
[fits / stretch / skip today]  <task>  — why it fits this slot
```

Matching rules:

- A task fits a slot when its honest effort tier is at or below the slot, and
  its energy demand is at or below the user's energy state.
- `energy:low` → favor `ready-now` / mechanical / closeout tasks; never put a
  cold-start design task at the top.
- `energy:high` + `slot:deep`/`slot:weekend` → favor the hardest blocked or
  highest-leverage item.
- Deadlines override energy fit: a due-soon task surfaces as a `stretch` with
  the deadline named, even in a low-energy window.
- If nothing fits, say so and offer the smallest honest next action plus a
  rest recommendation — do not pad the list.

See [`references/task-energy-matching.md`](references/task-energy-matching.md)
for the full rubric and worked examples.

### 3. Weekly load review mode

Triggered by "plan my week around teaching and making". Lay the week against
the teaching schedule (calendar connector or stated blocks), mark recovery
windows after heated/teaching-heavy days, and place at most one `slot:deep`
or `slot:weekend` item per recovery-protected day. Output is a week grid, not
a backlog. Use [`references/weekly-planning-template.md`](references/weekly-planning-template.md).

### 4. Recovery-aware planning mode

A modifier on the other modes: after a heated yoga teaching block or a
back-to-back day, down-weight `energy:high` tasks the next slot and protect at
least one rest window. Pull teaching-day shape from `yoga-sequencer` output
when available. This is scheduling hygiene, not health advice.

### 5. Handoff mode

When the chosen task needs real scoping, hand off:

- new/raw idea → `idea-incubator`
- physical build sizing → `maker-engineering` or `instrument-maker`
- teaching-week sequencing → `yoga-sequencer`

Pass the slot and energy bucket along so the downstream skill knows the
constraint.

## Inputs and outputs

**Inputs:** available time, current energy state, deadlines, teaching schedule
(stated or calendar-read), active projects, candidate tasks/backlog.

**Outputs:** a short ranked plan (matching mode), a week grid (weekly mode), or
a one-line "rest / smallest next action" when nothing fits. Never reflective
prose, never invented scores.

## Bundled resources

- [`references/energy-label-schema.md`](references/energy-label-schema.md) —
  capacity buckets and the explicit mapping to `idea-incubator` labels.
- [`references/task-energy-matching.md`](references/task-energy-matching.md) —
  matching rubric, tie-breakers, and worked examples.
- [`references/weekly-planning-template.md`](references/weekly-planning-template.md)
  — fill-in week grid with recovery windows.
- [`references/task-source-registry.md`](references/task-source-registry.md) —
  optional list of where candidate tasks can be read from (GitHub inboxes,
  active repos), all read-only.

## Pairings

- `idea-incubator` — supplies feasible candidates and the shared label
  vocabulary.
- `yoga-sequencer` — supplies teaching-week shape and heated-class recovery
  cost.
- `maker-engineering`, `instrument-maker` — size the real work once a slot is
  chosen.

## Open work (v0.1.0 → v1.0)

- Optional calendar-read helper script for weekly mode (kept out of v0.1 to
  stay data-light until repeated use justifies it).
- A `--from-issues` reader that pulls `ready-now`-labelled idea-incubator
  issues as the candidate set.
- Validation that recovery windows are never overwritten by deadline pressure
  without an explicit user override.
