# Enclosures, Combat Bots, And Vehicles

Use this file for electronics and PC enclosures, combat robot chassis, and
automotive or off-road sheet metal work such as roof racks and brackets.

## Contents

- Electronics and PC enclosures
- Combat robotics
- Micro-combat budgets
- Automotive and roof racks
- Output checklist

## Electronics And PC Enclosures

Use for PC cases, cyberdecks, controller boxes, maker-bot electronics, printer
control enclosures, fan shrouds, and custom device chassis.

Core concerns:

- component mounting patterns
- ventilation and fan clearance
- port and cable clearance
- service access
- EMI continuity and chassis grounding
- safe internal and external edges
- separation between high-voltage and low-voltage zones

Standard form factors:

- Treat ATX, Micro-ATX, Mini-ITX, SFX, ATX PSU, PCIe, fan, and radiator patterns
  as lookup-and-verify data, not memory-only facts.
- Ask for the exact component models or datasheets before fabrication-ready
  hole patterns.
- When browsing is available and current specs matter, use primary sources or
  manufacturer drawings.

Ventilation:

- Prefer staggered hex, slot, or round-hole arrays where they do not weaken the
  case.
- Keep web width at least `1.5 x T` as a first-pass minimum, larger near bends
  or high-stress areas.
- Do not place dense plasma perforations so close together that heat warps the
  panel.
- Add fan grills, filters, or finger-safe guards for exposed fans.

Grounding and finish:

- Add a dedicated ground screw location near the PSU or power entry when
  appropriate.
- Mark any paint or powder coat removal needed for electrical continuity.
- Deburr cable pass-throughs and add grommets where insulation can rub.

## Combat Robotics

Use for sheet metal antweight, beetleweight, hobbyweight, and similar combat
robot chassis or armor.

Core tactics:

- Monocoque folded chassis spreads impacts through the shell.
- Tab-and-slot self-fixturing improves alignment and impact resistance.
- Sloped front and side armor, often 30 to 45 degrees from the floor, deflects
  weapon hits better than vertical walls.
- Dogbone or circular reliefs at internal corners reduce crack initiation.
- Service panels need fast access between matches.
- Electronics trays should be isolated from shock with rubber, silicone, foam,
  or floating mounts.
- Wheels should be guarded with side flanges, loops, or replaceable armor.

Material warnings:

| Material | Use | Bending warning |
| --- | --- | --- |
| Grade 2 titanium | light armor/brackets | bendable with generous radius |
| Grade 5 titanium | premium armor | high cold-bend fracture risk |
| AR400/AR500 | spinner-resistant armor | do not cold bend on normal brake |
| 7075-T6 aluminum | stiff flat plates | crack-prone in bends |
| 6061-T6 aluminum | common chassis | use `R >= T`, test coupon |
| 5052 aluminum | formable chassis | generally better for bends |

Default to mechanical interlocks and screws/rivets for very thin micro-bot
work unless the builder has proven welding settings and fixtures.

## Micro-Combat Budgets

Planning classes from the brainstorm:

| Class | Limit | Target chassis budget | Starting material |
| --- | ---: | ---: | --- |
| Antweight | 1 lb / 454 g | 100 to 130 g | 0.031 in 6061-T6 or 0.020 in Grade 2 Ti |
| Beetleweight | 3 lb / 1360 g | 300 to 400 g | 0.062 in 6061-T6 or 0.040 in Grade 2 Ti |

Guardrails:

- For 1 to 3 lb bots, every gram matters. Estimate sheet area and weight before
  committing to a layout.
- Reject steel thicker than 20 ga as a default for micro-bot chassis unless the
  user explicitly budgets for it.
- Ask whether motors, battery, ESC, receiver, weapon, wheels, fasteners, and
  armor spares are already included in the weight budget.
- Use M3 or #4-40 as common fastener starting points, then match the team's
  actual hardware.
- Use pocketing only where it does not invite weapon bite or crack paths.

Run:

```bash
python3 scripts/sheet_metal_math.py combat-budget --class antweight
python3 scripts/sheet_metal_math.py weight --material aluminum --area 36 --thickness 0.031
```

## Automotive And Roof Racks

Vehicle and roof-rack work is safety-sensitive. This skill can help shape sheet
metal rails, brackets, cross-member plates, and flat patterns, but it cannot
certify road safety.

Route to `maker-engineering` for the safety gate before finalizing anything
that carries loads at speed, attaches to a vehicle, or could fail above people.

Spawn the `safety-gate` specialist (`agents/specialists/safety-gate.md`) for
the explicit pass/fail review before any vehicle part is treated as
fabrication-ready.

### RAV4 Prime-Style Roof Rack Planning

- The user interest is a flat rack for a 2024 Toyota RAV4 Prime with curved
  factory crossbars, meant for a ShiftPod tent and lumber transport.
- Start from measured roof rail/crossbar geometry, OEM roof load ratings, and
  attachment point limits.
- A flat platform must account for wind lift, braking, cornering, vibration,
  fatigue, corrosion, and tie-down load paths.
- Side rails may use 10 ga 5052-H32 aluminum or 1/8 inch mild steel as a
  planning start, but final material depends on load cases and attachment.
- Return flanges around 1.0 to 1.5 inches can greatly improve side-rail
  stiffness.
- Slot side rails for commercial aluminum extrusion or square tube
  cross-members when adjustability matters.
- Add generous radii, drainage, anti-whistle features, tie-down slots, and
  finish plans.

### Vehicle Load Case Worksheet

Before quoting any rack geometry or material, fill the load case worksheet:

| Load | Source | Magnitude | Notes |
| --- | --- | --- | --- |
| Static payload | designed | _ lb | What is being carried |
| Dynamic factor | road | x2 to x4 | Driving over potholes, bumps |
| Wind lift | aerodynamic | _ lb at _ mph | Estimated from frontal area |
| Cornering side load | _ g lateral | _ lb side | Tied to payload and CoG |
| Braking longitudinal | _ g forward | _ lb forward | Tied to payload |
| Tie-down preload | strap tension | _ lb | Per strap, can exceed payload weight |
| Fatigue cycles | road | _ million miles | Highway vibration |
| Temperature range | ambient | _ to _ °F | Garaged vs unsheltered |
| Corrosion exposure | environment | salt / rain / wash | Affects finish and fastener choice |

The user owns the actual numbers in this worksheet. The skill provides the
shape; do not invent loads from memory.

### Stop-Work Requirements For Vehicle Work

- Do not state "road ready" or "safe for highway use" without qualified review
  and testing.
- Do not assume factory crossbars can carry the intended load.
- Do not design clamping interfaces from memory or photos alone; require a
  measured interface or a manufactured part with a published spec.
- Require torque specs, locking hardware, anti-loosening strategy, inspection
  intervals, and low-speed/private-road validation before public-road use.
- Treat any roof-mounted item that could come loose at highway speed as
  "could hurt people downstream" — not just the owner.

### Attachment Patterns That Tend To Fail

- Self-tapping screws into factory crossbar rubber/foam. They feel solid and
  let go after a winter.
- Single-shear plates trying to handle dynamic loads. Use double-shear or
  through-bolts.
- Galvanized fasteners against aluminum rails without isolation. Galvanic
  corrosion eats one of the metals over time.
- Plastic or thin extruded clamps re-purposed beyond their rated load.
- Aftermarket "rated" hardware where the rating turns out to be the
  manufacturer's marketing rather than a tested capacity.

### Provisional Output

Even when the safety gate is open, the skill can still produce:

- A provisional rail profile (cross-section sketch with return flanges).
- A provisional cross-member spacing recommendation.
- A provisional bolt pattern based on the user's stated attachment points.
- A list of every measurement and OEM spec needed before fabrication.
- A test plan: static load test on jack stands, low-speed parking-lot drive
  with payload, highway speed only after qualified review.

Mark the output as `provisional planning; not road-ready` in every file.

## Output Checklist

For enclosures:

- exact component models or provisional hole-pattern status
- service access
- ventilation and fan clearances
- grounding and finish continuity
- cable edge protection
- cutout and bend clearances

For combat bots:

- weight class and full weight budget
- material/thickness and bend radius
- armor angles and reliefs
- service access time goal
- wheel and electronics protection
- hardware standard

For vehicle work:

- measured vehicle interface
- load cases and safety factor
- attachment and anti-loosening strategy
- corrosion and finish plan
- validation and inspection plan
- explicit non-certification boundary

