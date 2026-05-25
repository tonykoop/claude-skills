# Agent Record: RAV4 Prime Roof Rack Planning

## Authority Statement

This entire packet is at **design and CAD planning** authority. It is
explicitly **not fabrication-ready** and **not road-ready**. The
sheet-metal skill cannot certify highway safety for vehicle-mounted
hardware. The packet is marked `provisional planning; not road-ready`.

## Skill And References Loaded

- Primary skill: `sheet-metal` (SKILL.md).
- References read:
  - `references/enclosures-bots-and-vehicles.md` (Automotive and roof
    racks section; RAV4 Prime-style planning; load case worksheet;
    stop-work requirements; provisional output guidance).
  - `references/shop-dfm-guardrails.md` (material starting points,
    SolidWorks Sheet Metal setup, bend math, DXF/plasma hygiene,
    sequencing, stop-work checks).
- Specialist briefs reviewed:
  - `agents/specialists/safety-gate.md` (vehicle / roof rack rules).

## Assumptions Made (all provisional)

| Assumption | Source | Confidence | What would change it |
| --- | --- | --- | --- |
| OEM RAV4 Prime dynamic roof rating ~150 lb | rule-of-thumb for Toyota SUVs | low | Owner's manual lookup |
| 5052-H32 10 ga (0.102 in) deck | corrosion + formability | medium | Brake capacity check; load case math |
| Platform 52 x 48 in | fits plasma bed and brake | medium | Measured OEM crossbar spread |
| 1.5 in side rail return flange | stiffness without windage | medium | FEA or test deflection |
| Inside bend radius 0.125 in, K-factor 0.44 | 5052 planning range | medium | Test coupon |
| Plasma kerf 0.07 in | Maker Nexus planning value | medium | Cut settings on this material |
| M8 stainless clamp studs | typical aftermarket | low | Actual clamp selection |
| Dynamic factor 3x for road impact | rack rule-of-thumb | medium | Qualified engineer review |
| ShiftPod weight 55 lb | nominal | low | User weighs actual unit |
| Lumber load up to 150 lb | example trip | low | User defines typical loads |
| Designed static payload 135 lb | below assumed OEM 150 lb | low | Confirm OEM rating |
| Safety factor target 2.0 | provisional | medium | Qualified review |

## Open Questions Routed To User

1. Toyota's published dynamic roof load rating for THIS exact vehicle.
2. Measured OEM crossbar cross-section, length, and spread.
3. Selected commercial clamp make/model and its published working load.
4. Real ShiftPod packed weight and typical lumber load weights.
5. Maximum highway speed expected and worst weather/corrosion environment.

## Routed To Other Skills / Specialists

- `maker-engineering`: REQUIRED before highway-speed use. This skill is the
  safety-routing layer for cross-discipline vehicle work; the sheet-metal
  skill cannot stand in for it.
- `safety-gate` specialist: invoked as PROVISIONAL planning only. Decision
  embedded in `design-brief.md`. Will need to be re-run with real numbers
  once Gate 0 inputs are in hand.
- Maker Nexus instructor: needed to confirm 48 in brake can form 10 ga
  aluminum at full width.
- Qualified mechanical engineer or licensed vehicle outfitter shop:
  required for any move to highway use.

## Generated Vs Reviewed Artifacts

- All deliverables in this packet are **generated planning**. No
  fabrication has occurred. No SolidWorks file has been built. No DXF has
  been cut. No vehicle measurement has been taken.
- Numbers in `parameters.csv` and `load-cases.csv` marked
  "planning_assumption" or "user_estimate_needs_verify" are NOT measured
  values and MUST be replaced with measured or vendor-published values
  before any fabrication.

## What This Skill Will And Will Not Do

The sheet-metal skill WILL:

- Shape the deck and side rail geometry.
- Specify SolidWorks Sheet Metal features and global variables.
- Specify a flat-pattern checklist and DXF layer template.
- Sequence shop operations.
- Define gates the user must clear before each level of use.

The sheet-metal skill WILL NOT:

- Certify any rack as safe at highway speed.
- Approve a clamp design from memory or from a photo.
- Replace the OEM manual, a qualified engineer, or the shop instructor.
- Assume OEM roof load ratings.
- Use the word "certified" or "road-ready" for this packet.

## Stop-Work Boundary

Fabrication of this rack is not approved by this skill. Fabrication is
approved only after:

- Gate 0 of `validation-checklist.md` is complete.
- The safety-gate decision has been re-run with real numbers and reads
  PROVISIONAL or better.
- `maker-engineering` has reviewed for cross-discipline safety.

## File Inventory

| File | Purpose | Authority |
| --- | --- | --- |
| `design-brief.md` | Object, use case, envelope, constraints, safety gate | planning |
| `parameters.csv` | Named variables with source and confidence | planning |
| `solidworks-plan.md` | Feature sequence, equations, configurations | planning |
| `flat-pattern-checklist.md` | DXF/CAM readiness, bend allowance | planning |
| `fabrication-plan.md` | Cut, deburr, bend, join, finish, inspect | planning |
| `validation-checklist.md` | Pass/fail gates and test plan | planning |
| `agent-record.md` | This file: assumptions, sources, authority | planning |
| `bom.csv` | Bill of materials (provisional) | planning |
| `cut-list.csv` | Cut blanks (provisional) | planning |
| `bend-table.csv` | Bend operations table (provisional) | planning |
| `hardware.csv` | Fastener and clamp hardware (provisional) | planning |
| `load-cases.csv` | Vehicle load case worksheet (user fills with real numbers) | planning |

End of agent record.
