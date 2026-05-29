# Design Brief: Flat Roof Rack for 2024 Toyota RAV4 Prime

## Authority

This packet is **provisional planning; not road-ready**. It is **design and CAD
planning** authority only. It is NOT fabrication authority and NOT a
certification that the rack is safe for highway use.

The sheet-metal skill cannot:

- Certify road safety, highway-speed use, or compliance with FMVSS, DOT, or
  insurance requirements.
- Approve loads on the OEM crossbars without a measured OEM spec sheet.
- Replace a qualified mechanical engineer, a licensed shop's review, or the
  vehicle manufacturer's roof load rating.

A `safety-gate` decision is included (see "Safety Gate" section below) and a
maker-engineering review is REQUIRED before any over-the-road use.

## Object And Use Case

- **Object:** flat (deck-style) roof rack platform that bolts to the factory
  curved crossbars of a 2024 Toyota RAV4 Prime.
- **User payload (stated):**
  - ShiftPod tent (stuff sack, soft-but-bulky cargo).
  - Lumber transport to a makerspace (sheet goods, dimensional lumber).
- **Trips:** low-speed surface streets and highway runs to the makerspace.
- **User context:** owner-fabricated at Maker Nexus-style shop (GoFab plasma,
  48 in brake, 48 in shear, slip rollers, TIG/MIG).

## Outside Envelope (provisional)

| Dimension | Value | Notes |
| --- | --- | --- |
| Platform length (fore-aft) | 52 in | Provisional. Must be confirmed against the actual measured crossbar spread plus any allowable overhang per OEM. |
| Platform width (lateral) | 48 in | Sized to plasma bed; nominal RAV4 roof width is approximately 44 to 47 in across crossbars (NEEDS MEASUREMENT). |
| Side rail height | 1.5 in return flange | Adds bending stiffness without big windage. |
| Deck thickness | 10 ga 5052-H32 (0.102 in) provisional | Could move to 1/8 in mild steel; trade-off addressed below. |
| Tie-down slots | 1.0 x 0.25 in, 4 in pitch perimeter | Allows ratchet hook and soft-shackle through-points. |

## Interfaces

- **OEM crossbars:** 2024 RAV4 Prime "XSE" trim factory roof rails are curved
  (rising fore-aft). Bar profile cross-section is NOT measured. Published roof
  load rating MUST be looked up by the user; do not invent. (Common Toyota
  spec for SUV crossbars is ~150 lb dynamic, but the user MUST verify in the
  owner's manual.)
- **Clamp interface:** provisional plan is to use a commercially produced
  rated clamp (e.g., Rhino-Rack, Yakima, Front Runner) that wraps the OEM bar
  and presents a flat M8 stud or T-slot. Do NOT design the clamp from
  scratch; it is the load path that has the most failure modes.
- **Tent / lumber tie-downs:** ratchet straps and soft shackles routed through
  perimeter slots; no straps over sharp deck edges.

## Constraints

- Owner-fabricated on Maker Nexus-style tooling. Max blank fits 48 x 96 in
  plasma bed, brake capacity 48 in.
- Aluminum 5052-H32 preferred for corrosion in PNW-style weather and weight;
  10 ga is at the upper end of a 48 in brake's capacity for aluminum and the
  user should verify with the instructor before committing.
- Galvanic isolation is mandatory if mixing aluminum deck with steel
  fasteners; use stainless hardware with nylon or HDPE washers between
  dissimilar metals.
- Whistle/wind noise: any open slot near the leading edge of the deck must be
  on the underside or have a fairing/cover.
- Visibility: deck plus tent stack must NOT block driver's rear-view per
  state regulations (user owns the legal check).

## Load Cases (must be filled by user before fabrication)

See `load-cases.csv`. Numbers shown there are STARTING GUESSES that the user
must replace with real values measured from the actual tent, lumber, and the
OEM roof rating.

## Stop-Work / Open Questions

1. What is the published Toyota dynamic roof load rating for this exact
   vehicle (Prime trim, model year, sunroof option)?
2. What is the measured OEM crossbar cross-section, length between feet, and
   spread between front and rear bars?
3. Which commercially rated clamp will be used, and what is its published
   working load?
4. What is the actual weight of a fully packed ShiftPod and a typical lumber
   load (with dynamic factor)?
5. What is the maximum highway speed and worst weather the rack will see?

The skill will NOT proceed past provisional planning until these are answered
and routed through `maker-engineering` and the `safety-gate` specialist.

## Safety Gate (preliminary)

```
SAFETY GATE: vehicle / roof rack

Decision: PROVISIONAL (planning only)

Why:
- OEM crossbar cross-section is not measured.
- OEM roof dynamic load rating is not confirmed.
- Clamp interface is not selected or rated.
- Load case worksheet is not filled with real numbers.
- No qualified review or test plan executed.

Required before next use:
- Measured OEM crossbar profile and roof load rating.
- Commercially rated clamp with published WLL.
- Filled load-cases.csv with real numbers and safety factors.
- Stop-work conditions: visible deck cracks, fastener back-out, clamp slip,
  wind whistle indicating motion, any audible thump on bumps.
- Static jack-stand load test at 1.5x designed payload for 30 minutes.
- Low-speed (parking lot, then 25 mph residential) drive with payload and
  torque re-check after 5 miles, 25 miles, 100 miles.

Stop-work conditions:
- Any sign of clamp slip or rotation on the crossbar.
- Cracking near bend reliefs or hole edges.
- Galvanic corrosion staining at fastener interfaces.
- Wind whistle at any normal driving speed.

Routed to:
- maker-engineering (required before highway-speed use).
- Maker Nexus instructor (for brake capacity and material confirmation).
- A qualified mechanical engineer or licensed shop (for highway certification).
```

## Authority Reminder

This file, the parameters table, and all CSV/markdown deliverables in this
packet are at design and CAD planning authority. They are explicitly NOT
fabrication-ready and NOT road-ready.
