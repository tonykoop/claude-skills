# Morning summary — template and worked example

When the user returns, lead with this summary. Don't bury it under banter — they want to know what happened while they slept.

## Template

```markdown
# Sprint supervisor — overnight summary
**Scope:** `<scope>` | **Run time:** <hours>h | **Awakenings:** <count>

## 1. Sprint manager
- Hours running: <N>
- Auto-compacts: <N> (last at <time>, <context%> → <context%>)
- Current task: <one-liner>
- Context remaining: <%>
- Budget remaining: <%>

## 2. Merges that landed
**<group>** — <owner>/<repo>#<n>, <owner>/<repo>#<n>
**<group>** — <owner>/<repo>#<n>
**<group>** — (none)

## 3. Issues closed
**<group>** — <owner>/<repo>#<n> (<short description>), <owner>/<repo>#<n>

## 4. Named host / service  ← omit this section if no trusted_hosts are configured
Start: <stat>=<value> | <stat>=<value> | alerts=0 | svc=up
End:   <stat>=<value> | <stat>=<value> | alerts=0 | svc=up
Δ: <delta summary>

## 5. What I handled directly
- Stuck-pane approvals: <N> (<M> via watchdog hook, <K> via this skill)
- SSH read-only diagnostics approved: <N>
- Rate-limit prompts answered (kept current model): <N>
- Refusal-list hits: <N>

## 6. Caveats / things to review
- <pane> exhausted its weekly budget at <time> — manager re-routed lane work to its own context, succeeded
- One escalation: <time> — codex on <target> asked to `<command>`. I waited. It timed out and the manager retried with a more scoped command. I approved the retry.
- Two PRs are ready to merge but blocked on CI: <owner>/<repo>#<n>, <owner>/<repo>#<n>
```

**Group names** come from `labels.repo_groups` in the config. If the config has no repo groups, flatten merges and issues into a single `## 2. Merges that landed` list without group headings.

**Section 4** is only present when at least one `trusted_hosts` entry is configured; leave it out entirely otherwise. What to report for each host depends on the read-only diagnostics allowed in the config.

## What good summaries do

**Lead with the numbers.** "47 approvals, 6 PRs merged, 0 escalations" is more useful as a first read than prose.

**Cite everything.** PR numbers as `<owner>/<repo>#<n>`. Times in 24h local. Counts not adjectives ("47" not "lots of").

**Be honest about ambiguity.** If you weren't sure about something but approved it, say so in section 6. The user can decide retroactively whether they agree.

**Note non-events.** "Refusal-list hits: 0" is information. "No host alerts" is information. Silence about things the user might be worried about is worse than confirming they're fine.

## What good summaries do NOT do

- **Apologize for routine.** Don't say "I'm sorry I had to wake you" or "I hope this was useful." Just deliver the report.
- **Speculate.** If a pane stalled and you don't know why, say "stalled, last output was X" — don't invent a cause.
- **Bury escalations.** Anything from the refusal list, or anything you weren't sure about, goes in section 6 — clearly. Don't soften it.
- **Pad the merges list.** If nothing merged, say "no merges landed". Don't list PRs that *almost* merged.

## Scope-aware reporting (multi-supervisor)

When multiple supervisors are running, **only the first one to report covers section 1 (manager state).** The others should write:

> Section 1 — manager state — already covered by peer supervisor `<scope>` above.

This avoids three supervisors all independently reporting the same context% and auto-compact count.

Sections 2-6 are always scope-specific: each supervisor reports merges/issues/handled-approvals for **its own targets only**.

## Worked example

This example uses a fictional project (`acme`) with four repo groups (core, infra, backend, frontend). Adapt group names and PR citation format via `labels` in your config.

```
# Sprint supervisor — overnight summary
**Scope:** `default` | **Run time:** 8.1h | **Awakenings:** 121

## 1. Sprint manager
- Hours running: 8.1
- Auto-compacts: 5 (last at 04:53, 8% → 84%)
- Current task: merging acme/core#1238 (deadline patch)
- Context remaining: 67%
- Budget remaining: 52%

## 2. Merges that landed
**core** — acme/core#1234, acme/core#1235, acme/core#1237
**infra** — acme/infra#456, acme/infra#458
**backend** — acme/backend#789, acme/backend#791, acme/backend#792
**frontend** — (none — frontend lanes pivoted to design review pass)

## 3. Issues closed
**core** — acme/core#1100, acme/core#1102, acme/core#1108
**infra** — acme/infra#400
**backend** — acme/backend#502, acme/backend#504

## 5. What I handled directly
- Stuck-pane approvals: 47 (38 via watchdog, 9 via skill)
- SSH read-only diagnostics: 12
- Rate-limit prompts (kept current model): 4
- Refusal-list hits: 0

## 6. Caveats / things to review
- twingrid-b:0.5 exhausted weekly budget at 03:17. Manager re-routed.
- 04:42 escalation: codex asked to `rm -rf <workspace>/cache-old/`. I held. Manager retried with scoped path; I approved.
- PRs ready, blocked on CI: acme/backend#793, acme/frontend#211
- One pile-up at 02:31 (10 panes stuck simultaneously) — watchdog cleared 8, I handled 2. Root cause: manager was deep in a multi-merge sequence and stopped polling its own grid for ~4 min.
```
