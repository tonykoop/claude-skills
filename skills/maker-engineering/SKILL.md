---
name: maker-engineering
metadata:
  version: 0.1.0
  last-updated: 2026-05-09
description: >-
  Route physical making projects when the right specialist is unclear, the user
  asks "I want to make X", "help me design this physical thing", "is this
  instrument-maker or makerspace?", "set up an experiment", or "design a jig or
  fixture", or the work spans fabrication, acoustics, reverse engineering,
  experiment design, or idea-to-build routing. Use for project intake,
  specialist routing, DoE scaffolding, cross-project pattern search, and
  multi-specialist handoffs. Do not use for generic design requests or when one
  specialist skill clearly owns the whole task.
---

# Maker Engineering

## Trigger phrases

- `I want to make X` / `help me design this physical thing`
- `is this instrument-maker or makerspace?` / `which specialist?`
- `route this project` / `what should I build this with?`
- `set up an experiment` / `design of experiments`
- `hybrid project` / `this touches fabrication and acoustics`
- `multi-specialist handoff`
- human-carrying, body-load, climbable, floatable, or on-water prototype

## Do not trigger for

- Work clearly owned by one specialist — go directly to `instrument-maker`, `makerspace`, `reverse-engineer`, or `idea-incubator`.
- Generic CAD/design questions with no physical build goal.
- Idea capture for unscoped concepts — route to `idea-incubator` first.

Route and orchestrate physical making work without taking over specialist jobs.

Treat this skill as an umbrella for buildable objects, materials, tools,
measurements, shop constraints, acoustic behavior, fixtures, reverse
engineering, and experiments. Clarify the work, choose the right specialist
path, and produce crisp handoffs.

## Scope Check

- Stay in this skill when the project is unclear, hybrid, experimental, or needs multiple specialist owners.
- Switch to `instrument-maker` for full instrument packets, acoustic design, tuning tables, or shop packets. Always use the canonical name `instrument-maker` in handoffs so routing stays portable across runtimes regardless of which version is installed.
- Switch to `makerspace` when available for jig, fixture, toolpath, machine setup, or shop-process-only work.
- Switch to `reverse-engineer` when available for existing-object measurement, cloning, teardown, or documentation-only work.
- Switch to `idea-incubator` when available for early concepts that are not ready for build planning.

## Core Workflow

1. Identify the project object, goal, and current maturity: idea, sketch, prototype, build, debug, or validation.
2. Capture hard constraints: materials, tools, budget, deadline, safety limits, target environment, and available measurements.
3. Decide the mode: intake, routing, DoE, cross-project pattern search, or multi-specialist orchestration.
4. Read the relevant reference only when needed:
   - Routing rules: [`references/routing-decision-tree.md`](references/routing-decision-tree.md)
   - DoE scaffold: [`references/doe-template.md`](references/doe-template.md)
   - Human-carrying or floatable-object gate:
     [`references/human-carrying-floatable-gate.md`](references/human-carrying-floatable-gate.md)
   - Specialist registry: [`references/specialist-registry.md`](references/specialist-registry.md)
5. Produce the smallest useful output: a project brief, route decision, DoE matrix, pattern-search summary, or specialist handoff prompts.

Ask at most three blocking questions. If reasonable assumptions are available,
state them and proceed.

## Modes

### Intake

Use for vague physical project descriptions. Output a project brief with:

- object and intended use;
- current state and evidence available;
- constraints and unknowns;
- likely specialist route;
- next action.

### Routing

Use the routing decision tree to select a primary owner and any secondary
specialists. Explain why the umbrella skill is staying in routing mode or why
the next response should switch to a specialist.

### DoE

DoE mode can stand alone. Use it when the user wants an experiment, parameter
sweep, prototype comparison, tuning plan, or validation matrix. Do not perform
specialist calculations unless another triggered skill owns them.

### Cross-Project Pattern Search

Use when the user asks whether a similar build, failure, material choice, or
design pattern exists in provided repos, notes, or logs. Prefer local search
with `rg`, summarize matches, and convert useful patterns into routing or DoE
inputs.

### Multi-Specialist Orchestration

Use when a hybrid project needs multiple owners. Create separate, cross-linked
handoffs with shared assumptions and integration checkpoints. Do not merge
acoustic, fabrication, reverse-engineering, and experiment outputs into one
muddled packet.

### Human-Carrying / Floatable Gate

Use this gate before final build packets, shop handoffs, or first-use advice
for kayaks, canoes, rafts, chairs, stools, ladders, climbing/play structures,
wearable supports, and other objects whose failure can injure a person or put
someone in water. Read
[`references/human-carrying-floatable-gate.md`](references/human-carrying-floatable-gate.md)
and include the gate output before routing fixture, toolpath, or shop execution
details to `makerspace`.

This gate does not certify the object. It records assumptions, excluded uses,
load cases, staged validation, assisted first-use protocol, re-validation
triggers, and specialist boundaries.

## Output Rules

- Name the chosen route and the reason in the first few lines.
- Keep boundaries explicit: what this umbrella skill decided versus what a specialist must produce.
- For hybrid work, create one handoff per specialist plus a short integration note.
- For DoE work, include factors, response metrics, controls, trial matrix, logging fields, and stop conditions.
- For human-carrying, body-load, or floatable objects, include explicit
  "not a certification" language and run the human-carrying / floatable gate
  before final build or first-use guidance.
- Keep handoff prompts runtime-agnostic: name the specialist by its canonical name and describe the work, but do not embed runtime-specific invocation syntax (such as `$skill` or slash-command markers). The user may carry the prompt to a different runtime where the specialist is installed.
- Do not generate full instrument packets, CNC toolpaths, BOMs, shop drawings, or acoustic calculations here.
