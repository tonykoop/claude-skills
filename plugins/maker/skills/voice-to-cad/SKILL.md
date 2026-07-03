---
name: voice-to-cad
version: 0.2.0
last-updated: 2026-07-02
description: >-
  Idea-to-prototype express highway: a voice-first, multi-turn pipeline that
  takes a spoken or dictated idea through structured brainstorm (form,
  function, first principles, materials) → approved design brief → refined AI
  image prompt → a generated concept-image tournament voted A/B arena-style →
  image-conditioned codeCAD production (parametric OpenSCAD via CADAM + Claude,
  objective mesh gate) → artifacts committed to an existing or new GitHub repo
  with GENERATED provenance. Use whenever the user wants to go from a rough
  idea, voice note, or dictated ramble toward a physical prototype — "I have an
  idea for a thing", "let's design something new", "take this idea to CAD",
  "idea to prototype", "voice to CAD", "let's brainstorm then build it" — even
  if they don't name a pipeline. Also use when the user wants concept images
  A/B-voted before CAD, or wants a brainstormed object pushed to a repo. Do not
  use for recreating an existing object from photos (use reverse-engineer) or
  when the user already has a finished spec and just wants CAD generated (use
  maker-engineering's modality routing directly).
---

# Voice to CAD — the idea-to-prototype express highway

Drive one idea from spoken thought to a gated, committed CAD prototype in a
single conversation. The user talks; you structure. Five stages, each ending
in an explicit human gate — never run two gates together, and never skip a
gate because the answer seems obvious. The gates ARE the product: this skill
exists so a half-formed idea survives contact with production tooling.

```
voice brainstorm ──► design brief ──► image prompt ──► image tournament ──► codeCAD ──► repo push
     (talk)          [GATE: readback]  [GATE: approve]   [GATE: A/B votes]   [GATE: mesh]  [GATE: confirm]
```

## Voice etiquette (applies to every stage)

The user may be dictating — walking around a shop, driving, cooking. Respect
that in how you converse:

- **One question per turn** during brainstorm. Never a numbered list of five
  questions a speaking user can't hold in their head.
- **Short turns.** Two to four sentences while brainstorming. Save prose for
  the written artifacts.
- **Number or letter every choice** so the user can answer "two" or "B"
  instead of describing. Keep option sets ≤ 4.
- **Readback before every gate**: compress the state into 2–4 spoken-style
  sentences and ask for "yes / change X". A gate passes only on explicit
  assent.
- Capture the user's own phrases verbatim into the brief when they're vivid
  ("thigh-cradle", "looks like a seed pod") — those words carry the vision
  and later feed the image prompt.

## Stage 1 — Brainstorm → design brief

Run a structured but conversational intake across four lenses, one at a time:
**form** (silhouette, scale, presence), **function** (what it does, who uses
it, where it lives), **first principles** (loads, acoustics, ergonomics,
physics of why it works), **materials** (what it's made of, how it's made,
what the user can actually fabricate). Question banks and the brief template
are in `references/brainstorm-to-brief.md` — read it when entering this stage.

Produce `design-brief.md`: object, one-paragraph vision (user's words),
constraints table with confidence labels (borrow reverse-engineer's
observed/inferred/assumed discipline), envelope estimate, part list with
min-body count, material + process, open unknowns. **Gate: read the brief
back in 3 sentences; user approves or amends.**

## Stage 2 — Image prompt refinement

Co-write ONE image prompt from the brief (style, material honesty, camera,
background, the vivid user phrases). Then derive 4 variants that differ on a
single axis each (form factor, proportion, material finish, or detail
density) so the tournament teaches you something. Conventions and the proven
`agy -p` headless render recipe are in `references/image-tournament.md`.
**Gate: user approves the base prompt before any generation spend.**

## Stage 3 — Concept-image tournament (A/B arena format)

Generate the 4 concepts, then run a 2-round single-elimination bracket:
present pairs ("A or B?"), semifinals then final, 3 votes total. Log every
vote with the differing axis, because the *losing* traits are design
information ("rounder lost twice → user wants angular"). The winning image
becomes the visual authority for CAD. **Gate: the bracket's final vote.**

## Stage 4 — codeCAD production

Feed the winning image + the brief into the image-conditioned codeCAD lane
(default), or — when the deliverable wants a native feature tree — the
live-CAD bridge lane driven by any agent model (see the alternate-backend
section of `references/codecad-handoff.md`):
CADAM (local) + Claude → one self-contained parametric OpenSCAD program,
module per part, distinct bodies, editable parameters, BOSL2 allowed.
Prompt recipe, extraction (Supabase, not DOM), compile, and the objective
mesh gate (renders / watertight / sorted-extents envelope / min-wall /
body-count) are in `references/codecad-handoff.md`. State fabrication floors
in the prompt — thin display geometry is the universal failure mode. Iterate
with the user until the gate passes or the user accepts documented misses.
**Gate: mesh gate score + user acceptance.**

## Stage 5 — Repo push

Ask: existing repo or new one? Conventions for both — directory layout,
provenance JSON (pipeline, model, costs, vote log, gate scores, source
image), GENERATED-not-a-master labeling, commit message shape — are in
`references/repo-push.md`. **Gate: confirm repo + path before pushing;
pushing is outward-facing.** Never push without the confirm, never label
generated CAD as measured/reviewed.

## Telemetry

Track cost from Stage 2 onward (image renders + codeCAD API spend; OpenRouter
usage delta before/after). Report the running total at each gate — "we're at
$1.40" keeps the express highway honest — and write it into provenance.

## Express mode (one-shot)

If the user explicitly asks for the one-shot version ("just run the whole
highway on this idea"), collapse Stages 1–2 into your best single pass,
generate 4 images, still stop for the tournament votes (they're 30 seconds
of the user's time and the only human taste in the loop), then run CAD +
push with a single combined confirm at the end. Express mode still writes
every artifact and provenance record.

## Handoffs

- Existing object from photos → `reverse-engineer` (Parametric Recreation
  Branch) instead of this skill.
- Finished spec, no brainstorm needed → `maker-engineering` CAD-generation
  modality routing.
- Instrument-specific acoustics beyond first principles → `instrument-maker`
  after the brief exists; sheet-metal fabrication → `sheet-metal`.
- Idea isn't ready to build at all → `idea-incubator` (file it, don't force
  the highway).

## Reference map

- `references/brainstorm-to-brief.md` — four-lens question banks, voice
  pacing, design-brief template with confidence labels.
- `references/image-tournament.md` — base-prompt conventions, single-axis
  variant derivation, agy headless render recipe, bracket + vote-log format.
- `references/codecad-handoff.md` — CADAM prompt recipe from brief + image,
  source extraction, compile, objective mesh gate, iteration loop.
- `references/repo-push.md` — existing-repo layout, new-repo scaffold,
  provenance schema, GENERATED labeling, commit conventions.
