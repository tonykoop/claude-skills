# Routing Decision Tree

Use this reference when `maker-engineering` must choose a route or split a
hybrid project into specialist handoffs.

## 1. Activation Gate

Proceed only if the request is about a physical thing or experiment. Examples:
instrument, enclosure, jig, fixture, tool, material test, mechanism, prototype,
repair, measurement rig, acoustic object, or manufactured artifact.

Do not activate for generic software, UI, branding, writing, or product strategy
unless the user connects it to a buildable object or making workflow.

## 1a. Safety-Critical Object Check

Before choosing a route, ask: does this object carry a person, float with a
person aboard, or sit above a person? If yes, the project is safety-critical.
Run `references/human-carrying-safety-gate.md` and produce its eight required
sub-sections (intended environment, exclusions, anthropometric envelope, load
cases, prototype-vs-final boundary, staged validation, assisted first use,
re-validation triggers, plus the verbatim "not a certification" clause)
**before** issuing any final build packet or specialist handoff.

The gate is owned by `maker-engineering`. `makerspace`,
`instrument-maker`, and `reverse-engineer` all assume the gate has already
been run and will rely on its outputs.

Triggers for the gate include but are not limited to: kayak, canoe, boat,
raft, paddleboard, dock float, life-buoy, bike frame, treehouse, climbing
rig, ladder, scaffold, swing, hammock stand, child seat, lift platform,
suspended overhead fixture above a workstation.

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
- Steam-bent skin-on-frame kayak (safety-critical, human-carrying, floatable):
  - `maker-engineering`: safety-gate sub-sections, parametric schema,
    DoE matrix for steam-bend trials and float trials.
  - `makerspace`: steam plant, bending forms, strongback, station molds.
  - The gate runs first; specialist handoffs reference its outputs.

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
