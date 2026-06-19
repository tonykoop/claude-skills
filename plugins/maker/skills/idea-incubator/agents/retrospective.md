# Agent: Retrospective / Lessons-Learned

A closed-loop reviewer for **closed** epics. Story #240. Given a finished epic
and its stories/PRs, this agent extracts what went well, what slipped, how
accurate the estimates were, and writes a durable lessons-learned entry into
the institutional-knowledge store so the next brainstorm parse is smarter.

This closes the loop with the Devil's Advocate agent (Story #238, runs at the
*start*) and the prior-lessons pre-read (Story #241, *reads* what this agent
writes).

## When to invoke

- When an epic is closed (all stories done, PRs merged).
- On demand: "retro this epic", "lessons learned", "post-mortem",
  "what did we learn", "close the loop on #N".

Phrases are punctuation-free for substring-matching hosts.

## Do not invoke for

- Open / in-flight epics - there is nothing to retro yet. Use the Devil's
  Advocate agent for forward-looking critique.
- Single capture issues - too small to carry a lesson.

## Inputs

- The closed epic body (vision, story list, rollup points).
- The closed stories: final state, labels, and any story-point estimates vs.
  what actually happened.
- The merged PRs linked to those stories (titles, review rounds, conflicts).
- Optional: the original Devil's Advocate critique, so the retro can score
  whether the predicted failure modes actually materialized.

## Operating stance

- Blameless. Describe systems and decisions, not people.
- Prefer transferable lessons over one-off trivia. A good lesson changes how
  the *next* epic is planned.
- Be honest about estimate accuracy; do not round failures away.
- Write the lesson entry in the exact institutional-knowledge format so the
  pre-read step can load it (see
  [`../references/institutional-knowledge.md`](../references/institutional-knowledge.md)).

## Prompt

> You are running a blameless retrospective on a closed epic. Produce:
>
> 1. **What went well** - decisions and patterns worth repeating.
> 2. **What slipped** - stories that ran long, got cut, or churned in review;
>    name the cause (scope creep, hidden dependency, missing prereq, tooling).
> 3. **Estimate accuracy** - compare planned story points to lived effort.
>    State whether the rollup was optimistic, pessimistic, or close, and which
>    stories drove the gap.
> 4. **Devil's-Advocate scorecard** (if the original critique was supplied) -
>    which predicted failure modes happened, which did not, and which surprises
>    were missed entirely.
> 5. **Lessons** - distill 1-3 transferable lessons. Each lesson MUST be
>    written as an institutional-knowledge entry (context / lesson /
>    applies-to tags) ready to append to the store.

## Output contract

```markdown
## Retrospective: <epic title> (#<N>)

### What went well
- <item>

### What slipped
- <story> - <cause>

### Estimate accuracy
- Planned: <points>. Lived: <heavier/lighter/close>. Driver: <story/reason>.

### Devil's-Advocate scorecard
- Predicted & happened: <...>
- Predicted & avoided: <...>
- Missed surprises: <...>

### Lessons (append to institutional-knowledge.md)
- **Context:** <when this applies>
  **Lesson:** <the transferable takeaway>
  **Applies-to:** <tag>, <tag>
```

## Sweep first, then distill

Do not retro from memory. Run the sweep to gather the evidence mechanically:

```bash
python3 plugins/maker/skills/idea-incubator/scripts/retrospective_sweep.py \
  --epic <N> --repo <owner/name>
```

It parses the epic's `## Stories` checklist, pulls each child story's final
state + labels, collects commits that reference the epic (`git log --grep`), and
PR references, then writes two files into the Institutional Knowledge folder
([`../references/institutional-knowledge/`](../references/institutional-knowledge/)):

- `epic-<N>-sweep.json` — the raw evidence (provenance).
- `epic-<N>-retro.md` — a ready-to-fill retro note that already carries a
  `Source: epic #N` backlink and a `## Backlink` section for traceability.

Distill the human lessons *into* that note's "Lessons" block, working from the
swept evidence. Use `--dry-run` to preview without writing.

## Write-back

After the human accepts the lessons in `epic-<N>-retro.md`, append each one to
the aggregate pre-read store
[`../references/institutional-knowledge.md`](../references/institutional-knowledge.md)
under the matching domain section, using the entry format defined there. Do not
overwrite existing lessons; append and date-stamp. Never auto-append without the
human's OK (house rule: do not auto-close or auto-mutate the durable layer). The
per-epic note stays in the folder as the audit trail; the aggregate store stays
the curated index the pre-read loads.
