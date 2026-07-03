# Stages 2–3 — Image prompt refinement + A/B tournament

## Why images before CAD

The concept image is cheap taste-alignment: a few dollars and two minutes
buys a visual authority that keeps the (more expensive, slower) CAD stage
from wandering. Two arena rounds of evidence say image conditioning buys
visual fidelity essentially free — same geometric hygiene, much better
"looks like the vision".

## Base prompt (Stage 2)

Build ONE base prompt from the brief:

- photorealistic product/hero render language; single object; neutral studio
  or contextually-honest background (workshop bench, garden bed — wherever
  the brief says it lives);
- material honesty from the brief ("oiled walnut", "nitrided steel", "matte
  PLA") — never let the image promise a material the process can't deliver;
- scale cue when size matters (hands, coin, bench);
- the user's vivid phrases verbatim — they're the vision;
- camera: three-quarter view default (shows form + depth for later CAD
  reading).

**Gate: show the base prompt, get approval before spending.** The user edits
words here, not pixels later.

## Variants: one axis each

Derive 4 variants that each change exactly ONE axis from the base — form
factor, proportion, material/finish, or detail density. Single-axis variants
make votes interpretable: when B beats A, you learn which *trait* won, not
just which picture. Name each variant by its axis ("A: base | B: elongated
| C: brass hardware | D: minimal ornament").

## Rendering (proven recipe)

Local headless render via agy:

```bash
agy -p "<variant prompt>" # one call per variant; no bypass flag
```

JPEG output → normalize to PNG. Save as
`concepts/<slug>-{a,b,c,d}.png` next to the brief. If agy is unavailable,
any image generator the runtime has works — the tournament format is the
point, not the renderer. Record per-image cost if the backend reports it.

## The tournament (Stage 3)

2-round single-elimination bracket, 3 votes:

```
semifinal 1: A vs B  → user says "A" or "B"
semifinal 2: C vs D
final:       winner1 vs winner2
```

Present each pair as the two images side by side (or sequential links when
the runtime can't render inline) with their axis names. One vote per turn —
this is a voice flow. Accept "A", "left", "the angular one". Offer "both
lose — regenerate" as a standing option; a bad pair shouldn't win by
default.

Log to `concepts/vote-log.json`:

```json
{"round": "semifinal-1", "pair": ["a", "b"], "axis": "proportion",
 "winner": "b", "note": "user: 'the taller one, more presence'"}
```

After the final, write one sentence of synthesis into the brief's Vision
section: what the votes revealed ("angular > round, restrained ornament").
The winner image + that sentence are the CAD stage's visual authority.
