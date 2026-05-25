# Sheet Metal Brainstorm Map

Use this file when onboarding the skill, summarizing scope, or deciding where a
new sheet metal request belongs. It distills the 2026-05-18 brainstorming
conversation into project families and runtime modules.

## Feature List

- SolidWorks Sheet Metal guidance: base flange, edge flange, miter flange, hem,
  closed corner, corner relief, lofted bend, design tables, global variables,
  flat patterns, bend allowance, K-factor, and DXF export checks.
- Maker Nexus-style fabrication routing: GoFab plasma cutting, stomp shear,
  48-inch box and pan brake, slip rollers, TIG/MIG welding, grinding,
  sanding, blasting, deburring, and test-coupon planning.
- Parametric project setup: named envelope variables, material thickness,
  inside bend radius, K-factor, clearances, hardware spacing, and stock limits.
- Fabrication authority discipline: generated images and mood references can
  inspire, but reviewed CAD/DXF, measured drawings, design tables, and shop
  test coupons govern fabrication.
- Progressive output: concept brief first, then SolidWorks plan, then flat
  pattern/DXF handoff, then shop sequencing and validation.
- Deterministic helper math: bend allowance, cylinder/cone blank estimates,
  weight estimates, and combat robot budget checks.
- Cross-specialist routing: pair with `makerspace`, `maker-engineering`,
  `instrument-maker`, `laser-art`, and `reverse-engineer` without taking over
  their domains.

## Project Types

- Modular toolboxes and cases:
  - standardized 20 x 10 x 8 tackle-box size
  - clamshell lids, piano hinges, latches, hems, dividers, removable trays
  - storage boxes for bicycle accessories, shoe-care gear, rimfire gadgets,
    and makerspace commute tools
- Storage and domestic structures:
  - shelves, houseplant stands, trays, drainage panels, anti-bow flanges
  - STAS gallery hanging brackets, mirrors, sconces, and rail accessories
  - cat furniture with no exposed raw edges and dynamic load checks
- Stackable and mobile systems:
  - clocking rims, corner cleats, draw latches, keyhole slide locks
  - bottom dolly chassis, caster plates, axle tabs, hand-truck spine, handle
    receivers, stack center-of-gravity checks
- Hybrid heritage cases:
  - wood-metal attache cases, old-world briefcase aesthetics, metal
    exoskeletons, hardwood inlay panels, recessed channels, custom corner caps,
    symmetrical visible fasteners, wood movement gaps
- Curved and acoustic forms:
  - cylinders, cones, tapered transitions, trumpet/bugle/horn bells
  - SolidWorks Lofted Bend, slip-roll sequencing, seam prep, annealing,
    brazing/TIG choices, planishing over mandrels
- Combat robotics:
  - antweight and beetleweight chassis, monocoque folded armor, tab-and-slot
    self-fixturing, service panels, sloped armor, dogbone reliefs, weight
    budgets, wheel guards, shock-mounted electronics
- Electronics and PC enclosures:
  - custom PC cases, cyberdecks, printer controller boxes, maker-bot
    electronics, ventilation grilles, EMI grounding, port and fan cutouts,
    safe service edges
- Automotive and off-road DIY:
  - roof racks, vehicle brackets, load-bearing side rails, return-flange
    stiffeners, cross-member slots, tie-down architecture, lumber and ShiftPod
    transport use cases
- Geometric folded and stacked art:
  - low-poly sculptures, folded faceted forms, mixed wood-metal stacked art,
    registration holes, layer offsets, Gabriel Schama-inspired depth studies
- Creative maker expansion:
  - lighting and shadow objects, lanterns, sconces, perforated shades, and
    projection panels
  - kinetic sculpture, automata, wind spinners, mechanical flowers, mobiles,
    cams, and linkage studies
  - shop infrastructure, cleat panels, tool organizers, machine guards, chip
    trays, welding-table accessories, and hardware bins
  - camping and outdoor gear such as folding fireboxes, wind screens, camp
    kitchen boxes, lantern hangers, solar brackets, and tent hardware
  - food and beverage tools such as pour-over stands, knock boxes, smoker
    baffles, grill accessories, and roasting trays
  - camera, audio, synth, and creator rigs such as monitor cages, cheese
    plates, mic brackets, rack panels, and effects enclosures
  - costume armor, masks, bracers, helmets, theatrical props, sci-fi panels,
    aged patina pieces, and decorative hardware
  - furniture accents, cabinet pulls, drawer fronts, table aprons, bent legs,
    corner guards, and brass/copper trim
  - garden and balcony systems, trellises, planter liners, seed trays, labels,
    privacy screens, drip trays, and rain-chain parts
  - repair panels, appliance panels, motorcycle side covers, vintage toolbox
    fixes, dashboard inserts, rust patch templates, and odd brackets
  - educational STEM kits, bend/fold geometry lessons, simple chassis kits,
    load-test coupons, and pre-deburred youth build kits
  - sound and percussion objects, tongue drums, gongs, rattles, resonator
    cones, kalimbas, speaker horns, and acoustic reflectors

## Sub-Module Registry

1. `shop-dfm-core`
   Owns material sync, K-factor, bend allowance, minimum flange length, bend
   relief, DXF hygiene, tool limits, and cut/bend/finish sequencing.
2. `boxes-storage`
   Owns modular box architecture, toolboxes, trays, storage archetypes,
   hardware, hinges, latches, and divider systems.
3. `domestic-decor`
   Owns shelves, houseplant stands, STAS/gallery items, safe cat-facing edges,
   drainage, stiffness, and wall-interface concerns.
4. `stacking-mobility`
   Owns stack alignment, latching between boxes, dolly chassis, caster/axle
   choices, handle spines, and center-of-gravity checks.
5. `hybrid-attache`
   Owns wood-metal exoskeleton design, inlay capture channels, expansion gaps,
   custom corner caps, handle mounts, flush latches, and visible fastener
   symmetry.
6. `curves-horns`
   Owns rolled cylinders/cones, lofted bends, horn blank segmentation,
   annealing, seam geometry, and forming notes while routing acoustic design to
   `instrument-maker`.
7. `combat-robotics`
   Owns micro-combat sheet metal chassis, weight budgets, armor material
   warnings, service access, wheel guards, sloped armor, and electronics shock
   mounting.
8. `electronics-enclosures`
   Owns ventilation, standard component interfaces, grounding points, EMI
   continuity, port cutouts, serviceability, and PC/cyberdeck enclosure DFM.
9. `vehicle-racks`
   Owns rack/bracket sheet metal geometry only after safety and vehicle
   interface assumptions are explicit; routes safety-sensitive scope to
   `maker-engineering`.
10. `geometric-art`
    Owns folded sheet metal art and wood-metal layer registration while routing
    laser-specific material and vector concerns to `laser-art`.
11. `lighting-shadow`
    Owns perforated, folded, and layered light/shadow objects while requiring
    electrical and heat boundaries before fixture-like use.
12. `kinetic-sculpture`
    Owns moving sheet metal art, linkages, cams, pivots, wind motion, balance,
    guards, and fatigue-friendly details.
13. `shop-camp-gear`
    Owns shop organizers, portable bins, camp gear, fire/wind screens, and
    rugged fold-flat utility objects, with heat and sharp-edge gates.
14. `food-beverage`
    Owns sheet metal food-adjacent tools only after material/contact safety,
    cleanability, heat, coatings, and corrosion are explicit.
15. `creator-prop-furniture`
    Owns camera/audio rigs, rack panels, cosplay armor, props, furniture
    accents, garden systems, repair panels, STEM kits, and sound objects where
    sheet metal DFM is the main challenge.

## Progressive Disclosure Shape

- `SKILL.md`: Triggering, scope boundaries, workflow, artifact contract,
  reference map, and final checks. Keep it lean enough for every runtime.
- `references/brainstorm-map.md`: This summary and module map. Use for scope
  review and future expansion.
- `references/shop-dfm-guardrails.md`: General sheet metal rules and shop tool
  constraints. Load for nearly every fabrication-facing task.
- `references/boxes-storage-and-decor.md`: Toolboxes, domestic builds, stacking,
  dolly systems, and hybrid cases.
- `references/curves-horns-and-art.md`: Curved forms, musical horns, and
  stacked art.
- `references/enclosures-bots-and-vehicles.md`: Electronics, combat robotics,
  and vehicle rack/bracket work.
- `references/creative-maker-expansion.md`: Lighting, kinetic, shop/camp,
  food/beverage, creator rig, costume/prop, furniture, garden, repair, STEM,
  and percussion directions.
- `references/benchmarks-and-versioning.md`: Maintenance, install, version, and
  eval strategy.
- `scripts/sheet_metal_math.py`: Deterministic calculations that do not need to
  be loaded into context unless being patched.

Keep references one level deep from `SKILL.md`. Add a new reference only when a
module grows large enough that loading it would waste context for unrelated
tasks.

## Shape Borrowed From Existing Skills

- `makerspace`: default artifact packets, machine-aware routing, safety and
  tolerance gates, optional scripts, and eval notes.
- `maker-engineering`: umbrella routing boundaries, safety gate posture, and
  runtime-agnostic handoff prompts.
- `instrument-maker`: authority discipline for CAD/DXF vs generated images,
  validator-backed packets, and versioned reference additions.
- `laser-art`: concept/review/fabrication authority ladder and art-to-vector
  boundary.
- `reverse-engineer`: provisional status when evidence is incomplete and clear
  separation between observed, measured, inferred, assumed, and unknown.
- `skills-meta`: manifest-based versioning, cross-runtime install awareness,
  deterministic helper scripts, tests, and benchmark tables.
