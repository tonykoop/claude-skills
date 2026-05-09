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
- Add `sourcing.csv` when vendor choice or lead time affects the decision.
- Add `risks.md` when the setup is high-energy, user-facing, or failure
  sensitive.
- Add `response.md` when the user wants a chat-style answer instead of a
  file set.

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
