# Routing Decision Tree

Use this reference when `maker-engineering` must choose a route or split a
hybrid project into specialist handoffs.

## 1. Activation Gate

Proceed only if the request is about a physical thing or experiment. Examples:
instrument, enclosure, jig, fixture, tool, material test, mechanism, prototype,
repair, measurement rig, acoustic object, or manufactured artifact.

Do not activate for generic software, UI, branding, writing, or product strategy
unless the user connects it to a buildable object or making workflow.

## 2. Primary Axis

Choose the primary axis by the user's next needed deliverable.

| Primary need | Route |
| --- | --- |
| Acoustic behavior, playable instrument, tuning, bore/string/membrane/body design, instrument shop packet | `instrument-maker` |
| Jig, fixture, machine setup, toolpath, cut plan, workholding, shop operation, fabrication workflow | `makerspace` |
| Existing-object teardown, measurement, clone, fit check, unknown geometry/material inference | `reverse-engineer` |
| Early concept shaping, idea promotion, feasibility framing before build planning | `idea-incubator` |
| Parameter sweep, tuning study, prototype comparison, validation plan | Stay in `maker-engineering` DoE mode unless a specialist calculation dominates |
| Mixed or unclear route | Stay in `maker-engineering` intake/routing mode |

## 3. Hybrid Split Rules

Split into separate handoffs when two or more specialist outputs would be
different artifacts.

Examples:

- Ceramic ocarina with slip-cast mold and tuning validation:
  - `instrument-maker`: acoustic geometry and tuning intent.
  - `makerspace`: mold, casting, firing, and shop workflow.
  - `maker-engineering`: DoE matrix tying shrinkage, wall thickness, and pitch error.
- Copy a vintage instrument from photos and calipers:
  - `reverse-engineer`: measurement plan and geometry reconstruction.
  - `instrument-maker`: acoustic interpretation and playable redesign.
- Build a router jig for repeated tone-hole drilling:
  - `instrument-maker`: tone-hole datum requirements.
  - `makerspace`: jig/workholding/toolpath implementation.

Do not ask one specialist to absorb another specialist's deliverable. Cross-link
the handoffs instead.

## 4. Intake Questions

Ask only questions that block routing or experiment setup. Prefer these:

- What is the object, and what must it do physically?
- Is the next deliverable a design, a shop process, a measurement plan, or an experiment?
- What tools, materials, and measurements are already available?
- Is there an existing object to copy/analyze?
- What outcome defines success: sound, fit, strength, repeatability, cost, time, or yield?

## 5. Route Decision Output

Use this compact schema:

```text
Route: <primary skill or maker-engineering mode>
Secondary: <none or specialist list>
Why: <one to three concrete reasons>
Boundary: <what maker-engineering will not produce>
Next output: <brief, DoE scaffold, pattern search, or handoff prompts>
Assumptions: <only if needed>
```

For multi-specialist work, add:

```text
Integration checkpoint: <where outputs must meet>
Shared constraints: <materials/tools/dimensions/targets all specialists must honor>
```
