# Structural Polish Pass Reference

Run this pass after the table-read pass. Focus on structure and impact — not grammar or logistics.

## Hook audit (first 5 seconds)

Rate the opening 0–10:

| Score | Meaning |
|---|---|
| 8–10 | Viewer is immediately pulled forward — strong visual or question |
| 5–7 | Reasonable hook; could be sharper |
| < 5 | BLOCKER — hook is too slow, too on-the-nose, or buries the lead |

Rewrite rule: the first line must create a **gap** (an unanswered question the viewer needs to close).

## On-the-nose detector

Flag any line where the script *tells* the viewer what to feel or think when a visual could show it instead.

Patterns to catch:
- "This is incredible because..." → cut; let the image speak
- "As you can see..." → cut entirely
- "The point is..." → cut; restructure the surrounding section
- Emotional adjectives attached to inanimate subjects: "the beautiful way the reed vibrates" → show the reed, drop the adjective

For each flagged line, emit: `ON-THE-NOSE: [original line] → [visual treatment or rewrite]`

## Retention curve check

Walk through the script in 15–30 second segments. Mark each as:

- `↑ PEAK` — high information density or emotion; viewer is leaning forward
- `→ HOLD` — steady pacing; acceptable
- `↓ DIP` — low payoff; viewer at risk of dropping off

For each `↓ DIP`: recommend one of: cut entirely, add B-roll to maintain visual interest, compress to one sentence, or reorder with a hook.

## Transition audit

For every cut point:

| Cut type | When to use |
|---|---|
| Cold cut | Default; rhythmic impact |
| Dissolve | Temporal shift or emotional softening |
| Audio bridge | Voice carries over cut; scene changes under it |
| L-cut / J-cut | Audio pre-rolls or lingers; advanced; flag where useful |

Flag any transition that feels arbitrary (no rhythm, no purpose) with: `TRANSITION GAP: [location] — suggest cold cut / dissolve / audio bridge`

## Closing audit

Rate the ending 0–10 using the same scale as the hook. Check:

- Does the ending answer the opening question or pay off the gap?
- Is the CTA (call to action) direct — one clear ask, not three?
- Is the final image / line memorable?

## Output format

```
STRUCTURAL POLISH REPORT

Hook strength: [score]/10 — [one-line verdict]
Closing strength: [score]/10 — [one-line verdict]

ON-THE-NOSE
  [TC] [original → recommended]

RETENTION DIPS
  [TC-in]–[TC-out]: [DIP reason] → [recommendation]

TRANSITION GAPS
  [TC]: [issue] → [suggestion]

OVERALL: [summary sentence — what one rewrite would have the highest impact]
```
