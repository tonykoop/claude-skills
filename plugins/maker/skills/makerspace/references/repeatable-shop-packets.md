# Repeatable Shop Packets

This skill defaults to a compact fabrication packet rather than a full
portfolio bundle.

## Default packet

Required artifacts:

- `fabrication-plan.md`
- `jig-decision.md`
- `workholding-checklist.md`
- `safety-checklist.md`
- `make-order-buy-borrow.md`

## When to add optional artifacts

- Add `drawing-brief.md` when another person needs to draft CAD, CAM, or a
  print.
- Add `cad-index.csv` before the drawing brief when a repo contains recovered
  CAD/drawings/layout files and the current fabrication authority is unclear.
- Add `bom.csv` when the fixture or setup requires purchased stock or
  hardware.
- Add `sourcing.csv` when vendor choice or lead time affects the decision.
- Add `risks.md` when the setup is high-energy, user-facing, or failure
  sensitive.
- Add `response.md` when the user wants a chat-style answer instead of a
  file set.

## When to add structured (CSV) artifacts

When the packet has more than five distinct parts **or** more than five
distinct go/no-go gates, also produce:

- `cut-list.csv`
- `validation.csv`
- `cad-index.csv` when recovered CAD/drawing/archive authority is a blocker
- `process-schedule.csv` (rename to `bending-schedule.csv`,
  `welding-schedule.csv`, etc., as the work warrants)

For any packet whose primary feature is curved (rocker arc, kayak hull,
bent rim), also generate a parametric SVG side-elevation or top-view
that visually proves the dimensions in the narrative are mutually
consistent.

Schemas, validation snippets, and a steam-bending gate table live in
`references/structured-shop-artifacts.md`. Run the column check with
`scripts/validate_packet.py --schemas-only --packet <packet-dir>` before
declaring the packet ready.

## Packet design rules

- Keep design intent separate from machine operations.
- Every operation needs a tool, workholding method, tooling callout, and a
  go/no-go check.
- Every custom jig recommendation needs enough detail to make, source, or
  reject it without guessing at the purpose.
- Keep unknowns explicit with `TBD`, `assumption`, or `derived estimate`.

## Good packet smell

A strong packet answers:

- What matters dimensionally?
- How will the part be held?
- What machine path is primary?
- What is the fallback if the ideal path is blocked?
- Why is the chosen jig strategy better than the obvious alternatives?
