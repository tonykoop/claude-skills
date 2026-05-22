# Specialist Registry

Use this reference when producing handoff prompts or explaining route ownership.

## Naming Convention

Use the canonical, unversioned specialist name in routing decisions and handoff
prompts (`instrument-maker`, `makerspace`, `reverse-engineer`,
`idea-incubator`). A user may have a different version installed in a different
runtime (Claude Code, Claude Desktop, Codex CLI, Codex Desktop, Gemini CLI,
mobile zip upload), and the canonical name keeps the route correct as long as
any compatible version is present. When you know a feature requires a specific
minimum version, add a parenthetical hint like "prefer v4+" rather than baking
the version into the name.

## Current Specialists

### `instrument-maker` (current canonical version: v4)

Owns musical instrument design and documentation: acoustic physics, parametric
tables, CAD/OpenSCAD/SolidWorks starters, dimensioned drawings, BOMs, sourcing,
cut/validation packets, slip-cast workflows, capstone decks, printable shop
packets, empirical tuning loops, and build-log support.

Route here for acoustic artifacts, playable instruments, tuning behavior,
instrument geometry, and instrument-specific shop packets.

### `idea-incubator`

Owns early idea capture, promotion, triage, and concept shaping before a project
has enough build intent for engineering routing.

Route here when the user is still choosing what to make, comparing concepts, or
turning a loose idea into a candidate project brief.

## Planned Specialists

### `makerspace`

Will own fabrication execution: jigs, fixtures, toolpaths, workholding,
materials/process planning, shop setup, cut lists, machine constraints, safety
steps, and build process documentation.

Route here when the main deliverable is how to make the thing in a shop.

### `reverse-engineer`

Will own existing-object analysis: measurement strategy, teardown plans,
geometry reconstruction, material inference, fit checks, tolerances, reference
photo/caliper workflows, and clone/redesign evidence packets.

Route here when the work starts from an object that already exists.

## Future Specialist Slots

Reserve future routing slots for:

- electronics and embedded systems;
- materials testing;
- ceramics and kiln process specialization;
- mechanical simulation;
- public release packaging for build kits.

Until a future specialist exists, `maker-engineering` may produce an intake
brief and DoE scaffold, then clearly mark the missing specialist capability.

## Handoff Prompt Shape

```text
Specialist: <skill name>
Project:
User goal:
Owned deliverable:
Inputs available:
Constraints:
Shared assumptions:
Do not handle:
Integration checkpoint:
Validation expected:
```

For hybrid projects, produce one prompt per specialist and keep shared
assumptions identical across prompts.

Keep these prompts runtime-agnostic: use the canonical specialist name and plain
prose. Do not embed `$skill`, slash-command markers, or runtime-specific
invocation syntax — the user may paste the prompt into whichever runtime has the
specialist installed (Claude Code, Claude Desktop, Codex CLI, Codex Desktop,
Gemini CLI, or a mobile zip upload).
