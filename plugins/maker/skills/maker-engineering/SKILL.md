---
name: maker-engineering
metadata:
  version: 1.1.0
  last-updated: 2026-05-10
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

## Connectors

This skill works best with these MCP connectors. Claude will suggest connecting any that aren't already linked at the point they're needed (via `mcp__mcp-registry__suggest_connectors`).

- **Wolfram** (`de1d1dc7-ec10-459d-b511-797982834b43`) — required for DoE math, statistical sample sizing, mechanical feasibility checks, safety-gate computations on human-carrying/floatable objects.
- **GitHub** — optional for routing accepted projects into the right specialist repo and creating intake/handoff issues. No registry UUID; configure via the Claude Code GitHub connector if available.

## Trigger phrases

- `I want to make X` / `help me design this physical thing`
- `is this instrument-maker or makerspace?` / `which specialist?`
- `route this project` / `what should I build this with?`
- `set up an experiment` / `design of experiments`
- `hybrid project` / `this touches fabrication and acoustics`
- `multi-specialist handoff`
- Human-carrying or floatable objects: `kayak`, `canoe`, `boat`, `raft`,
  `paddleboard`, `bike frame`, `treehouse`, `climbing rig`, `ladder`,
  `play structure`, `child seat`, `swing`, `lift platform`, `dock float`

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
   - Specialist registry: [`references/specialist-registry.md`](references/specialist-registry.md)
   - Human-carrying / floatable safety gate: [`references/human-carrying-safety-gate.md`](references/human-carrying-safety-gate.md)
5. **If the project carries a person, floats with a person aboard, or could fail above a person — run the safety gate (see Safety Gate section below) before issuing any final build packet or specialist handoff.**
6. Produce the smallest useful output: a project brief, route decision, DoE matrix, pattern-search summary, or specialist handoff prompts.

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

### Safety Gate (human-carrying / floatable / overhead-of-person)

Required for any project where failure could injure or drown a person:
boats, paddleboards, bike frames, treehouses, climbing rigs, ladders,
swings, lift platforms, child seats, dock floats, suspended fixtures
above workstations, etc.

Run the gate **before** any final build packet or specialist handoff.
The gate is owned by this skill, not by `makerspace` or
`instrument-maker` — those specialists assume it has already been run.

The gate produces eight required sub-sections at the top of the build
packet: intended environment, excluded use cases, anthropometric
envelope, load cases and safety factor, prototype-vs-final boundary,
staged validation gates, assisted first-use protocol, re-validation
triggers, and the mandatory "not a certification" clause.

Use the template and worked example in
[`references/human-carrying-safety-gate.md`](references/human-carrying-safety-gate.md).
The Round 7 steam-bent kayak packet is the canonical example.

## Output Rules

- Name the chosen route and the reason in the first few lines.
- Keep boundaries explicit: what this umbrella skill decided versus what a specialist must produce.
- For hybrid work, create one handoff per specialist plus a short integration note.
- For DoE work, include factors, response metrics, controls, trial matrix, logging fields, and stop conditions.
- Keep handoff prompts runtime-agnostic: name the specialist by its canonical name and describe the work, but do not embed runtime-specific invocation syntax (such as `$skill` or slash-command markers). The user may carry the prompt to a different runtime where the specialist is installed.
- Do not generate full instrument packets, CNC toolpaths, BOMs, shop drawings, or acoustic calculations here.
- For any human-carrying / floatable / overhead-of-person object, the build packet **must** include the safety-gate sub-sections from [`references/human-carrying-safety-gate.md`](references/human-carrying-safety-gate.md), including the verbatim "not a certification" clause. Do not soften or omit that clause. The gate goes at the top of the packet, before any per-specialist handoff.
