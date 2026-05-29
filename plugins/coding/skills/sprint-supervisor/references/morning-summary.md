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
**core4** — wrfcoin/core4#1234, wrfcoin/core4#1238
**infra** — wrfcoin/infra#456
**backend** — wrfcoin/backend#789, wrfcoin/backend#791
**frontend** — (none)
**smart-contracts** — wrfcoin/smart-contracts#321

## 3. Issues closed
**core4** — wrfcoin/core4#1100 (consensus race fix), wrfcoin/core4#1102
**infra** — wrfcoin/infra#400 (alert noise reduction)

## 4. N5 Pro testnet
Start: height=482,103 | peers=14 | alerts=0 | svc=up
End:   height=485,917 | peers=14 | alerts=0 | svc=up
Δ: +3,814 blocks in 8.2h ≈ 7.7 blocks/min (healthy)

## 5. What I handled directly
- Stuck-pane approvals: 47 (38 via watchdog hook, 9 via this skill)
- SSH read-only diagnostics approved: 12
- Rate-limit prompts answered (kept current model): 4
- Refusal-list hits: 0

## 6. Caveats / things to review
- twingrid-b pane 5 exhausted its weekly budget at 03:17 — manager re-routed lane work to its own context, succeeded
- One escalation: 04:42 — codex on twingrid-a:0.2 asked to `rm -rf /home/tony/wrfcoin/cache-old/`. I waited. It timed out and the manager retried with a more scoped command (`rm -rf /home/tony/wrfcoin/cache-old/build-2026-04/`). I approved the retry.
- Two PRs are ready to merge but blocked on CI: wrfcoin/backend#793, wrfcoin/frontend#211
```

## What good summaries do

**Lead with the numbers.** "47 approvals, 6 PRs merged, 0 escalations" is more useful as a first read than prose.

**Cite everything.** PR numbers as `repo#NNNN`. Times in 24h local. Counts not adjectives ("47" not "lots of").

**Be honest about ambiguity.** If you weren't sure about something but approved it, say so in section 6. The user can decide retroactively whether they agree.

**Note non-events.** "Refusal-list hits: 0" is information. "No N5 alerts" is information. Silence about things the user might be worried about is worse than confirming they're fine.

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

## Worked example (real, from 2026-05-12)

```
# Sprint supervisor — overnight summary
**Scope:** `default` | **Run time:** 8.1h | **Awakenings:** 121

## 1. Sprint manager
- Hours running: 8.1
- Auto-compacts: 5 (last at 04:53, 8% → 84%)
- Current task: merging wrfcoin/core4#1238 (consensus deadline patch)
- Context remaining: 67%
- Budget remaining: 52%

## 2. Merges that landed
**core4** — wrfcoin/core4#1234, wrfcoin/core4#1235, wrfcoin/core4#1237
**infra** — wrfcoin/infra#456, wrfcoin/infra#458
**backend** — wrfcoin/backend#789, wrfcoin/backend#791, wrfcoin/backend#792
**smart-contracts** — wrfcoin/smart-contracts#321

(no frontend merges — frontend lanes pivoted to design review pass)

## 3. Issues closed
**core4** — wrfcoin/core4#1100, wrfcoin/core4#1102, wrfcoin/core4#1108
**infra** — wrfcoin/infra#400
**backend** — wrfcoin/backend#502, wrfcoin/backend#504

## 4. N5 Pro testnet
Start: height=482,103 | peers=14 | alerts=0 | svc=up
End:   height=485,917 | peers=14 | alerts=0 | svc=up
Healthy throughout. One peer flapped at 02:14 (rejoined in 38s, no alert).

## 5. What I handled directly
- Stuck-pane approvals: 47 (38 via watchdog, 9 via skill)
- SSH read-only diagnostics: 12
- Rate-limit prompts (kept gpt-5.4 not gpt-5.4-mini): 4
- Refusal-list hits: 0

## 6. Caveats / things to review
- twingrid-b:0.5 exhausted weekly budget at 03:17. Manager re-routed.
- 04:42 escalation: codex asked to `rm -rf /home/tony/wrfcoin/cache-old/`. I held. Manager retried with scoped path; I approved.
- PRs ready, blocked on CI: wrfcoin/backend#793, wrfcoin/frontend#211
- One pile-up at 02:31 (10 panes stuck simultaneously) — watchdog cleared 8, I handled 2. Root cause: manager was deep in a multi-merge sequence and stopped polling its own grid for ~4 min.
```
