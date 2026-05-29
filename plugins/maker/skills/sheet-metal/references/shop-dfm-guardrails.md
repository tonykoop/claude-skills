# Shop And DFM Guardrails

Use this file for general sheet metal feasibility, SolidWorks Sheet Metal
setup, Maker Nexus-style machine routing, and DXF/flat-pattern review.

## Contents

- Authority and assumptions
- Maker Nexus-style tool profile
- Material starting points
- SolidWorks Sheet Metal setup
- Bend math and design rules
- DXF and plasma hygiene
- Bend, roll, weld, and finish sequencing
- Stop-work checks

## Authority And Assumptions

Treat all shop numbers as planning assumptions until verified against the
current posted machine rules, instructor guidance, and actual tooling.

Default authority order:

1. Current shop policy, machine labels, instructor guidance, and measured tools
2. User-measured stock and hardware
3. Reviewed SolidWorks part/assembly and exported flat pattern
4. This skill's planning assumptions
5. Generated images, mood boards, and verbal concepts

Generated images are never fabrication authority.

## Maker Nexus-Style Tool Profile

The brainstorming source described this shop profile:

- GoFab CNC plasma table: 48 x 96 inch bed
- Stomp shear: 48 inch
- Box and pan brake / finger brake: 48 inch
- Floor slip roller: 48 inch, planning minimum radius about 1 inch
- Tabletop slip roller: 12 inch, planning minimum radius about 0.75 inch
- TIG/MIG welding, grinders, sanders, and blasting cabinet

Use these as a starting profile only. Ask the user to verify tool limits before
final DXF or bend plans, especially for thick stock, stainless, titanium, AR
plate, brass, copper, or long parts near the 48 inch capacity.

## Material Starting Points

Use measured thickness when possible. Gauge tables vary by material.

| Material | Planning thickness | Notes |
| --- | ---: | --- |
| Mild steel, 16 ga | 0.060 in | Rugged boxes, shelves, brackets |
| Aluminum, 14 ga | 0.064 in | Lightweight boxes and panels |
| Stainless, 18 ga | 0.048 in | Durable and corrosion resistant, harder to form |
| Aluminum 5052-H32 | 0.063 to 0.125 in | Good sheet metal alloy for bending |
| Aluminum 6061-T6 | 0.031 to 0.125 in | Usable but crack-prone at tight bends |
| Brass/copper | 0.020 to 0.040 in | Horns and decorative work, anneal as needed |
| Grade 2 titanium | 0.020 to 0.040 in | Formable relative to Grade 5, expensive |
| Grade 5 titanium | varies | High risk to bend cold; use large radii or avoid |
| AR400/AR500 | varies | Treat as flat armor plate; do not cold bend on a normal brake |

For load-bearing or vehicle work, material choice is not a style decision. It
must be tied to load cases, attachment design, fatigue, corrosion, and a test
plan.

## SolidWorks Sheet Metal Setup

Start with named parameters:

| Variable | Purpose |
| --- | --- |
| `Part_Length`, `Part_Width`, `Part_Height` | Outside or controlling envelope |
| `Material_Thickness` | Measured stock thickness |
| `Inside_Bend_Radius` | Actual tooling or conservative default |
| `K_Factor` | Bend allowance estimate |
| `Clearance_Gap` | Moving part, lid, tray, or insert clearance |
| `Kerf` | CAM/plasma cutting allowance |
| `Hardware_Pitch` | Repeat fastener spacing |
| `Relief_Size` | Bend and corner relief dimensions |

Prefer Sheet Metal features that flatten cleanly:

- Base Flange/Tab for the seed sheet
- Edge Flange for straight bends
- Miter Flange for continuous frames
- Hem for safe/stiffened edges
- Closed Corner for tubs and boxes
- Corner Relief for intersecting bends
- Lofted Bend for cones, horns, and tapered transitions

Avoid modeling sheet metal as arbitrary thin extrusions and then trying to
recover a flat pattern later.

## Bend Math And Design Rules

Bend allowance:

```text
BA = pi * angle_deg / 180 * (inside_radius + K_factor * thickness)
```

Conservative first-pass rules:

- Set inside bend radius `R >= T` unless measured tooling and a test coupon
  justify tighter.
- Use K-factor 0.40 to 0.45 for mild steel, 0.42 to 0.48 for common aluminum,
  and 0.35 to 0.40 for stainless as planning ranges only.
- Keep straight flange length at least `4 x T`, plus any tool-specific grip
  requirement.
- Keep holes, slots, and emboss-like cutouts at least `3 x T` from bend lines
  unless distortion is acceptable or tested.
- Use bend reliefs where folds terminate at edges. Start with relief width at
  least `T` and depth at least `R + T`.
- Use corner reliefs for box corners. Start with circular or tear relief around
  `2 x T` diameter for 90 degree box corners.
- For hems, confirm the chosen hem can be made on available tools and will not
  trap the part before later bends.
- For cat-facing, hand-facing, or carry objects, raw accessible sheet edges
  require deburring plus a hem, guard, radius, or protected finish.

When numbers matter, run:

```bash
python3 scripts/sheet_metal_math.py bend-allowance --angle-deg 90 --radius 0.06 --thickness 0.06 --k-factor 0.44
```

## DXF And Plasma Hygiene

Before plasma, laser, or outside-shop handoff:

- Export 1:1 scale flat patterns.
- Confirm file units in the drawing and filename or handoff note.
- Keep cut, etch/mark, drill-later, bend-centerline, and construction layers
  separate.
- Close all loops.
- Convert splines to arcs/lines when the CAM workflow needs them.
- Add stock boundary and nesting margins; use 0.5 inch as a plasma planning
  margin unless the shop uses another rule.
- Treat plasma kerf around 0.060 to 0.080 inch as a planning assumption until
  cut settings and material are known.
- For holes smaller than about `2 x T`, consider center-pierce/marking and
  drilling/reaming afterward.
- Add test coupons for new material, tight bend radius, critical hole fit,
  visible finish, or any novel tab/slot joint.

## Bend, Roll, Weld, And Finish Sequencing

Output an explicit operation sequence:

1. Cut oversize stock if needed.
2. Plasma/laser/shear the blank and coupons.
3. Deburr while the part is flat.
4. Drill/ream critical holes if plasma quality is insufficient.
5. Bend internal flanges, hems, or trapped features first.
6. Bend outer walls and larger enclosing forms later.
7. Roll cylinders or cones before seam closure when needed.
8. Fit, clamp, tack, rivet, screw, braze, or TIG/MIG weld.
9. Grind, sand, blast, patina, powder coat, paint, oil, or seal.
10. Inspect fit, dimensions, edges, stability, and load gates.

For boxes on a finger brake, check that later bends do not trap the part under
the upper beam. For multi-flange trays, name the bend order.

For slip-rolled parts, plan for unbent flats at the leading and trailing edges.
Add sacrificial trim margin or a manual pre-bend step when a continuous curve
matters.

## Stop-Work Checks

Stop and ask for confirmation or route to a safety specialist when:

- The project supports people, pets, heavy overhead loads, moving vehicles, or
  highway-speed loads.
- The user requests vehicle roof racks, suspension brackets, climbing or
  lifting hardware, child-carrying hardware, or anything above a person.
- Material is exotic, hardened, unknown, plated, painted, galvanized, or
  coated in a way that affects cutting, welding, fumes, or bending.
- A requested bend exceeds machine capacity or risks damaging the brake.
- The design depends on an unmeasured vehicle roof, proprietary rail profile,
  or unknown fastener interface.
- Acoustic or musical instrument claims require tuning, bore profile, or
  voicing decisions. Route those to `instrument-maker`.

