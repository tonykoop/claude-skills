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
- Add `bom.csv` when the fixture or setup requires purchased stock or
  hardware.
- Add `cut-list.csv` when stock layout, paired parts, or repeated parts need
  auditable dimensions.
- Add `validation.csv` when the maker needs measurable acceptance checks or
  a human-load/static-load test record.
- Add `process-schedule.csv` when heat, glue, cure, soak, casting, or
  pressing times affect success.
- Add `bending-schedule.csv` when steam bending or bent laminations are
  central to the packet.
- Add `sourcing.csv` when vendor choice or lead time affects the decision.
- Add `risks.md` when the setup is high-energy, user-facing, or failure
  sensitive.
- Add `response.md` when the user wants a chat-style answer instead of a
  file set.

Read `structured-shop-artifacts.md` before emitting those CSV files; it
defines minimum column schemas and validation commands.

## Packet design rules

- Keep design intent separate from machine operations.
- Every operation needs a tool, workholding method, tooling callout, and a
  go/no-go check.
- Every structured CSV uses the documented minimum columns so it can be
  parsed and checked later.
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
