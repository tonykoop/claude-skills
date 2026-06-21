# Table-Read Pass — Reference

The table-read pass simulates speaking the script aloud to catch problems the eye misses. In Hollywood pre-production, a table read is done with the full cast before principal photography; this pass applies the same logic to video scripts, voiceovers, and narrations.

## Goals

1. Confirm every line is speakable at natural conversational pace.
2. Mark where the speaker needs to breathe without breaking rhythm.
3. Score pacing per section so the editor can plan B-roll length.
4. Catch jargon or phrasing that reads clever but sounds robotic when spoken.

## Procedure

### 1. Spoken-rhythm scan

Read each sentence aloud (or mentally simulate it at speaking pace). Flag:

- Lines longer than ~12 words between commas/periods — these exhaust a speaker's breath
- Back-to-back sentences that start with the same word or structure (monotony trap)
- Technical strings read as abbreviations (e.g. "API" → "A-P-I" or "ay-pee-eye" — note which pronunciation is intended)
- Phrasing that requires unnatural emphasis to make sense (e.g. "the **only** way" when "only" isn't bolded in the script)

### 2. Breath-break insertion

Insert `[BREATH]` annotations at every natural pause point:

- After every period or question mark in fast-paced passages
- Mid-sentence after a comma when the segment exceeds 8–10 words
- Before a scene-shift or tonal pivot

Example:
```
Before: "Whether you're a complete beginner or a seasoned practitioner you'll find a practice here that meets you exactly where you are."
After:  "Whether you're a complete beginner [BREATH] or a seasoned practitioner, [BREATH] you'll find a practice here [BREATH] that meets you exactly where you are."
```

### 3. Pacing score per section

Divide the script into labelled sections (intro / body / CTA or by scene). For each, estimate pace:

| Pacing | Tokens per second | Indication |
|--------|-------------------|------------|
| **SLOW** | < 2.5 | Meditative, instructional hold, savasana |
| **MEDIUM** | 2.5–3.5 | Conversational narration, demonstration |
| **FAST** | > 3.5 | Hook, teaser, excitement-building montage |

Flag mismatches: e.g. a FAST-paced paragraph placed over a B-roll shot requiring 8 seconds of visual hold.

### 4. Archetype rhythm check

Cross-reference with the channel archetype (from `references/channel-profiles.yaml`):

| Archetype | Target spoken pace | Typical hold beats |
|-----------|-------------------|--------------------|
| yoga | SLOW–MEDIUM | 4-count, 8-count breath cycles; no rushed cues |
| instrument-maker | MEDIUM | Demonstration rhythm; 2–4 sec step pauses |
| AI/agentic | FAST–MEDIUM | Punchy; no held silence beyond 1 sec |
| consciousness / reflective | SLOW | Poetic cadence; deliberate pauses valued |
| WRFcoin | MEDIUM–FAST | Data-forward; crisp transitions |

Flag any segment where the script pace conflicts with the archetype.

## Output format

Produce a `## Table-Read Pass` section in the review document with:

1. **Speakability issues** — numbered list, each with the offending line and a suggested rewrite
2. **Breath-break annotated script** — the full script with `[BREATH]` markers inserted inline
3. **Pacing table** — one row per section (TC-in, TC-out, pacing score, notes)
4. **Archetype verdict** — MATCH / MISMATCH with one-sentence rationale

If there are no speakability issues, write: `No speakability issues found.`
