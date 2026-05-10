---
name: makerspace
metadata:
  version: 0.1.0
  last-updated: 2026-05-09
description: >-
  Plan shop-floor fabrication for jigs, fixtures, workholding, molds, machine
  setups, and make/order/buy/borrow decisions. Use when the user asks to
  design a jig or fixture, review a CNC/laser/mill/router/plasma setup, choose
  workholding, build a repeatable shop packet, or separate design intent from
  machine-specific operations. Inputs are part geometry, materials, tolerances,
  batch size, deadline, and shop constraints. Outputs are fabrication plans,
  jig packets, workholding and safety checklists, and make/order/buy/borrow
  recommendations. Do not use for instrument acoustics — route to
  `instrument-maker` or `maker-engineering`. Do not use when the project is
  still conceptual — route to `idea-incubator` or `maker-engineering` first.
---

# Makerspace

## Trigger phrases

- `design a jig` / `I need a fixture for this`
- `help me set up the CNC` / `plan this on the router / laser / mill`
- `make or buy?` / `should I build this or source it?`
- `repeatable shop packet` / `setup sheet`
- `workholding for this part`
- `tolerance check` / `go/no-go`

## Do not trigger for

- Instrument acoustics or voicing — route to `instrument-maker`.
- Projects that are not yet scoped — route to `maker-engineering` or `idea-incubator`.
- Reverse engineering of an existing object — route to `reverse-engineer` first, then return here when builder-ready.

Treat `makerspace` as a fabrication specialist. Use it after the concept
exists and the next question is practical: hold the part safely, choose a
machine route, decide whether to make or source a fixture, and define the
tolerance and safety checks that keep the setup repeatable.

Keep the scope narrow. Favor fabrication operations over portfolio
packaging, broad project management, or acoustic design.

## Own these tasks

- Plan jigs, fixtures, molds, and workholding
- Plan machine-aware routes tied to a real shop profile
- Produce repeatable setup packets for one-off and small-batch work
- Decide whether to make, order, buy, borrow, or adapt tooling
- Call out safety, tolerance, and go/no-go checks

## Respect these boundaries

- Do not calculate instrument acoustics or take over voicing. Route that
  work to `instrument-maker`.
- Do not invent CAD/CAM blindly. Mark missing geometry, machine limits, or
  stock constraints as `TBD` when they affect safety, fit, or feasibility.
- Do not override posted shop safety practices.
- Do not blur design intent and machine operations together. Write the
  required outcome first, then choose the shop-specific route.

## Produce these default artifacts

Produce a compact repeatable shop packet unless the user asks for a
different shape. Mirror the same sections in chat when file output is not
needed.

- `fabrication-plan.md`
  Include feasibility, machine route, operation sequence, go/no-go checks,
  and prep actions.
- `jig-decision.md`
  Compare candidate fixture approaches and record the chosen path plus the
  rejected options.
- `workholding-checklist.md`
  Record datums, clamping, tool access, tolerance checkpoints, and failure
  watch items.
- `safety-checklist.md`
  Record machine, material, PPE, retention, and stop-work hazards.
- `make-order-buy-borrow.md`
  Record the sourcing decision and the tradeoffs that drove it.

Add optional artifacts only when the prompt calls for them:

- `drawing-brief.md`
- `bom.csv`
- `cut-list.csv`
- `validation.csv`
- `process-schedule.csv` or `bending-schedule.csv`
- `sourcing.csv`
- `risks.md`
- `response.md`

Read `references/repeatable-shop-packets.md` before choosing the output
shape.

When the setup has repeated parts, timed processes, steam bending,
laminations, human-load objects, or safety-critical gates, also read
`references/structured-shop-artifacts.md` and include the relevant CSV
schemas and go/no-go gates.

## Gather the minimum inputs

Capture these inputs before locking a plan:

- part or feature geometry
- material and stock form
- critical tolerances or fit class
- batch size and repeatability needs
- shop, machine, and tooling constraints
- deadline or build cadence

Load `spaces/home-shop-default/profile.yaml` when the user omits shop
context. Use `assets/templates/shop-equipment-profile.yaml` when the user
needs a temporary profile instead of a canonical `spaces/<slug>/` entry.

## Follow this workflow

1. Identify the shop context.
   Load `spaces/<slug>/profile.yaml` when it exists. Otherwise use the
   temporary equipment template and mark assumptions.
2. Write the design intent.
   State the must-hit geometry, tolerance, finish, and throughput goals
   before choosing machines.
3. Choose the task mode.
   Pick the best fit:
   - jig or fixture design
   - workholding review
   - machine-aware process planning
   - make/order/buy/borrow decision support
   - safety and tolerance readiness check
4. Build the route.
   Produce a primary path and at least one fallback when the ideal machine,
   certification, or purchased component is unavailable.
5. Validate the packet.
   Run the verifier checklist before declaring the plan ready.

## Load references on demand

- `references/repeatable-shop-packets.md`
  Read first when choosing artifacts.
- `references/structured-shop-artifacts.md`
  Read when a packet needs structured CSV artifacts, timed process
  schedules, SVG/PNG sanity checks, steam-bending gates, or human-load
  object validation.
- `references/jig-decision-matrix.md`
  Read when comparing fixture strategies or deciding whether to custom-make,
  adapt, purchase, or borrow.
- `references/workholding-and-tolerance-checklist.md`
  Read when defining datums, clamping, tool access, and inspection points.
- `references/safety-checklist.md`
  Read when sweeping machine, material, retention, and operator hazards.
- `references/make-order-buy-borrow.md`
  Read when cost, lead time, reuse, or rigidity drive the tooling choice.
- `references/manufacturing-and-tools.md`
  Read when machine-family-specific guidance is needed.
- `references/sourcing-and-production.md`
  Read only when the user asks for procurement guidance or vendor options.
- `references/space-profile-schema.md`
  Read when creating or editing a canonical shop profile.
- `references/doe-integration.md`
  Read when the user is tuning feeds, speeds, cure times, or other process
  variables experimentally.

## Dispatch to specialists deliberately

- `agents/specialists/shop-planner.md`
  Use for feasibility, machine routing, prep sequencing, and make/order/
  buy/borrow recommendations tied to a specific shop.
- `agents/specialists/manufacturing-planner.md`
  Use for jig concepts, workholding, tooling, drawing briefs, and tolerance
  checkpoints.
- `agents/specialists/verifier.md`
  Use for completeness and contradiction checks before shipping.
- `agents/specialists/red-team.md`
  Use for unusual hazards, awkward ergonomics, high-energy processes, or
  failure-sensitive fixtures.

## Accept paired inputs without scope creep

- Accept source geometry, design intent, and tolerances from
  `maker-engineering`.
- Accept instrument geometry or tooling needs from `instrument-maker`
  without taking over acoustic decisions.
- Accept measured dimensions from `reverse-engineer`.

## Treat legacy material as optional context

Use `examples/` only for historical comparison or legacy packet behavior.
The v0.2 benchmark workspace lives outside the skill package at
`docs/benchmarks/makerspace/` in the host repo (or
`tonykoop/makerspace/evals/workspace/` in the standalone repo); load it on
demand for benchmark inspection only. Do not let the broader v0.2
build-packet material take over the default runtime behavior of this
skill.
