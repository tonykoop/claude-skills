# Fabrication specialist charter (issue #15)

This note records that issue #15 ("Build makerspace fabrication specialist
skill", epic #211) is **satisfied by this existing `makerspace` skill**. No
sibling skill or new plugin was created — that would duplicate a mature skill
(v1.1.x). This charter maps #15's requirements to what already ships so the
decision is auditable in-skill.

## Why an extension, not a new sibling

Issue #15 was written as a skill-creator handoff to *build* `makerspace`. By the
time of epic #211 the skill already exists, is portable across Claude/Codex,
and carries the full fabrication-specialist surface the issue asked for. The
cleaner move (per the lane brief's #15 judgment call) is to confirm coverage and
record the mapping here, keeping everything inside the maker plugin.

## Requirement → existing deliverable

| #15 asks for | Where it lives now |
|---|---|
| Jig/fixture design planning mode | SKILL.md flow + `agents/specialists/shop-planner.md` |
| Machine setup & workholding review | `references/workholding-and-tolerance-checklist.md`, `references/manufacturing-and-tools.md` |
| Process plan generation | `references/repeatable-shop-packets.md`, `scripts/generate_build_packet.py` |
| Make/order/buy/borrow decision support | `references/make-order-buy-borrow.md`, `references/jig-decision-matrix.md` |
| Safety & tolerance checklist mode | `references/safety-checklist.md`, `references/workholding-and-tolerance-checklist.md` |
| Shop equipment profile template | `references/space-profile-schema.md`, `spaces/` |
| Jig decision matrix | `references/jig-decision-matrix.md` |
| Tolerance/workholding checklist | `references/workholding-and-tolerance-checklist.md` |
| Safety checklist reference | `references/safety-checklist.md` |

## Acceptance criteria (all met)

- [x] Produces shop-useful, constraint-aware plans — build-packet flow +
  structured-shop-artifacts schemas.
- [x] Separates design intent from machine-specific operations — explicit in
  SKILL.md scope and `repo-to-shop-packet-routing.md`.
- [x] Includes safety/tolerance/workholding checks — three dedicated references.
- [x] Handles hybrid instrument fabrication without taking over acoustic design
  — boundary documented; acoustics route to `instrument-maker`.

## Boundaries (unchanged, reaffirmed)

- No instrument acoustics — route to `instrument-maker` / `maker-engineering`.
- No blind full CAD/CAM without source geometry and machine constraints.
- Does not override machine safety practices.

## Pairings (unchanged)

- `maker-engineering` routes in; `instrument-maker` supplies instrument
  geometry; `reverse-engineer` supplies extracted dimensions.
