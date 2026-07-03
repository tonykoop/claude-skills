# Stage 1 — Brainstorm → design brief

The goal is a brief strong enough to drive both an image prompt and a CAD
prompt, produced from conversation a dictating user can actually sustain.
You are structuring their thinking, not interrogating them.

## Pacing

Open by mirroring the idea back in one sentence and asking the single most
load-bearing unknown first — usually function ("what does it need to *do*?")
if the idea arrived as a shape, or form ("what does it look like in your
head?") if it arrived as a purpose. Then rotate lenses. 6–10 total questions
is the normal budget; stop early when the brief writes itself. If an answer
covers two lenses, don't re-ask the second one — acknowledge and move on.

## Question banks (pick, don't recite)

**Form** — silhouette from across the room? hand-scale, lap-scale,
furniture-scale? one vivid object it rhymes with? symmetric or asymmetric?
what should someone *feel* when they first see it?

**Function** — the one job it must do well? who uses it, how often, where
does it live between uses? what does it interface with (hands, walls, other
parts, instruments, plants...)? what would make the user abandon it?

**First principles** — what loads or forces does it carry (gravity, string
tension, impact, moisture, heat)? what physics makes it work (resonance,
leverage, capillary action, stiffness-to-weight)? where will it fail first?
what's the one dimension everything else derives from?

**Materials** — what's it made of in the dream version? what can the user
actually fabricate (their shop, their processes)? printed, cut, bent, turned,
cast, carved? finish and feel? any material honesty rule ("if it looks like
walnut it IS walnut")?

Ask about **envelope** explicitly before leaving the stage — max bounding box
in mm — and about **part count**: what are the distinct pieces? Those two
answers become the objective gate's floors later, so they can't stay vague.

## The brief template

Write `design-brief.md`:

```markdown
# <object name> — design brief (voice-to-cad)

**Vision** — one paragraph in the user's own words/phrases.

## Constraints
| item | value | label |
|---|---|---|
| envelope_mm | [W, D, H] | stated / inferred / assumed |
| <driving dimension> | ... | ... |
| material | ... | ... |
| process | ... | ... |
| min_wall_mm floor | ... (from process: FDM ~1.6, resin ~1.0, CNC wood ~3, sheet ~t) | assumed |

## Parts (distinct bodies)
1. <part> — <role>        → min_bodies = N

## First principles
- <load/physics note that must survive into CAD>

## Unknowns (explicitly NOT decided)
- <thing> — decide at <stage>
```

Label every constraint `stated` (user said it), `inferred` (you derived it,
say from what), or `assumed` (placeholder to keep moving — these get read
back at the gate). The labels are what stop a dictated ramble from
hardening into false spec three stages later.

## The gate

Read back: object + the 2–3 constraints that drive everything + the part
list, in ≤ 4 sentences. Ask "build the brief on that? or change something."
Amend and re-read until assent. Then write the file and move to Stage 2.
