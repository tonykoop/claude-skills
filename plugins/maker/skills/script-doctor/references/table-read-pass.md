# Table-Read Pass Reference

Simulate a director reading the script aloud for the first time. Catch anything that would cause a stumble, a confused pause, or a forced ad-lib on camera.

## What to scan for

### Ear-vs-eye gap
Lines that look fine on paper but are hard to speak naturally. Flag these patterns:
- Multiple nested clauses in one sentence (hard to breathe through)
- Abbreviations or acronyms that have no obvious pronunciation (CSV, BOM, WL)
- Numbers that are ambiguous when spoken ("8" = "eight" or "ate"?)
- Passive constructions that bury the verb at the end

### Breath-break markers
Insert `[BREATH]` at every natural pause point (end of a beat, topic transition, dramatic hold). Recommend one `[BREATH]` every 20–30 seconds minimum. A script with no natural breath points will sound rushed and is a POLISH flag.

### Hard-to-speak lines
Flag any line where a fluent speaker would likely stumble on a cold read. For each, emit:
```
HARD-TO-SPEAK: [original line]
→ EASIER: [suggested rewrite or structure note]
```

### Pacing score per section
Walk through the script in chunks of ~30 seconds (or natural sections). Score each:
- `FAST` — dense information, lots of names/numbers, viewer must concentrate
- `MEDIUM` — comfortable, viewer follows without strain
- `SLOW` — deliberate; fine for emotional holds or complex setups, POLISH flag if overused outside those contexts

### Archetype check
Does the spoken rhythm match the channel archetype? Load the matching profile from `references/channel-profiles.yaml` and check:
- Yoga: breath-based rhythm, long holds, slow cadence — is the script speaking too fast?
- AI/coding: punchy, short sentences, demo-anchored — is the script over-explaining?
- WRFcoin: data-dense but clear — does every number have a label?

## Output format

```
TABLE-READ REPORT

Archetype: [yoga | ai_agentic | instrument_maker | consciousness | wrfcoin | generic]
Readability score: [1–10]

HARD-TO-SPEAK
  [TC] [original → easier]

BREATH-BREAK MAP
  [TC] [BREATH] — recommended insertion point
  [TC] [BREATH] ...

PACING BY SECTION
  [label] [FAST / MEDIUM / SLOW] — [one-line note]

ARCHETYPE ALIGNMENT: [MATCH / MISMATCH] — [one-line verdict]
```

## Scoring rubric

| Score | Meaning |
|---|---|
| 9–10 | Reads naturally; minimal flags; voice-ready |
| 7–8 | Minor rewrites needed; filmable with light prep |
| 5–6 | Notable stumble points; prep required |
| < 5 | BLOCKER — script needs a significant table-read rewrite before camera rolls |
