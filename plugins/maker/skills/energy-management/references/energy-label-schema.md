# Energy & capacity label schema

This skill does **not** invent a parallel taxonomy. It defines two cheap
matching buckets and maps them onto labels that already exist in
`idea-incubator` (see `idea-incubator/references/label-schema.md`).

## Capacity buckets (matching-only, never stored)

### Time window → `slot:*`

| Window | Bucket |
|---|---|
| up to ~30 min | `slot:micro` |
| ~30 min – ~2 hr | `slot:focused` |
| half / full day | `slot:deep` |
| weekend / multi-session | `slot:weekend` |

### Energy state → `energy:*`

| State | Bucket |
|---|---|
| low / depleted / post-teaching | `energy:low` |
| steady / normal | `energy:steady` |
| high / fresh | `energy:high` |

These buckets live only inside a single planning reply. Do not persist, trend,
or score them.

## Mapping to existing idea-incubator labels

| idea-incubator label | Meaning there | How energy-management reads it |
|---|---|---|
| `ready-now` | low-friction, executable without setup | strong fit for `slot:micro`/`slot:focused` and `energy:low` |
| `needs-clarification` | missing a key detail | not schedulable yet — route back to `idea-incubator`, do not slot |
| `stale` | sat long enough to review | surface in weekly review, not in a micro slot |
| domain labels (`maker`, `instrument`, `yoga`, `skills`, `general`) | topic | used to balance a week across domains, and to pick the right handoff target |

A task that carries `ready-now` in the inbox is already energy-cheap; this
skill trusts that label rather than re-rating the task. If a task has no
idea-incubator label, ask the user for its rough effort once and treat the
answer as ephemeral.

## Effort tier (derived, not a new persistent label)

For inline (non-inbox) tasks, infer a one-shot effort tier so it can be matched
to a slot. This is a derivation, not a stored label:

| Effort tier | Fits slot |
|---|---|
| trivial / closeout | `slot:micro`+ |
| single-session | `slot:focused`+ |
| multi-step, one sitting | `slot:deep`+ |
| spans sessions / needs setup | `slot:weekend` |

Never write these tiers back to a datastore. They exist for the duration of the
reply only.
