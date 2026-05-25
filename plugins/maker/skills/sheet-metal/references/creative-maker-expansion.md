# Creative Maker Expansion

Use this file when a project is creative, theatrical, domestic, educational, or
utility-oriented and does not fit cleanly into toolboxes, horns, bots,
electronics, or vehicles. Load `shop-dfm-guardrails.md` alongside it whenever
the answer needs bend, DXF, material, or shop sequencing details.

## Contents

- Talent pattern for new project modes
- Lighting and shadow objects
- Kinetic sculpture and automata
- Shop infrastructure
- Camping and outdoor gear
- Food and beverage tools
- Camera, audio, synth, and creator rigs
- Costume armor and props
- Furniture accents
- Garden and balcony systems
- Repair panels and restoration
- Educational STEM kits
- Sound and percussion objects
- Output checklist

## Talent Pattern For New Project Modes

To make the skill good at a new category, define the module in this compact
shape:

1. **Trigger objects**: concrete things the user might ask for.
2. **Primary geometry**: sheet metal forms that usually solve it.
3. **Hard constraints**: safety, heat, food contact, moving parts, body
   contact, fatigue, load, corrosion, service access, or finish.
4. **CAD/flat pattern tactics**: features, bend order, tabs, slots, hems,
   perforations, reliefs, nesting, and alignment marks.
5. **Companion skill route**: when to involve `makerspace`, `laser-art`,
   `maker-engineering`, `reverse-engineer`, or `instrument-maker`.
6. **Benchmark prompt**: one realistic user request and pass criteria.

This pattern lets future maintainers add talent without turning `SKILL.md` into
a giant prompt.

## Lighting And Shadow Objects

Trigger objects:

- sconces, lanterns, lampshades, candle shields, LED strip channels,
  projection panels, perforated diffusers, art deco light boxes

Sheet metal tactics:

- Use perforated patterns, folded shades, removable backplates, hidden
  brackets, hemmed front lips, and offset standoffs.
- Keep perforation web width at least `1.5 x T` as a starting point; increase
  it near bends, mounting holes, and heat zones.
- Separate shade, reflector, mounting plate, and service cover in CAD.
- Add ventilation slots and air gaps around LEDs, bulbs, or candles.
- Put cut, score/etch, bend, and registration layers on separate DXF layers.

Guardrails:

- Do not certify electrical fixtures. Treat wiring, mains voltage, UL/ETL, and
  building-code compliance as external review.
- For candles or hot bulbs, require noncombustible spacing, soot/heat testing,
  and a stop-work warning.
- For mirror-polished or reflective interiors, consider glare and hot spots.

Route:

- Use `laser-art` for ornamental vector design and material safety.
- Use `maker-engineering` for overhead or permanent wall-mounted load concerns.

## Kinetic Sculpture And Automata

Trigger objects:

- wind spinners, whirligigs, balanced mobiles, cams, crank toys, linkage
  studies, mechanical flowers, folding wings, moving display pieces

Sheet metal tactics:

- Use folded ribs for stiffness, tabbed pivots, replaceable bushings, spacer
  washers, balanced hubs, and removable service panels.
- Round internal corners and avoid crack-starting notches near moving joints.
- Use slots for adjustment where balance or phase timing must be tuned.
- Design hard stops so links cannot over-center and jam.
- Use test coupons for pivot wear and fatigue-prone bends.

Guardrails:

- Name pinch points and sweep envelopes.
- Check wind load, overspeed, fatigue, and sharp moving edges.
- Use retainers or locknuts so outdoor vibration cannot shed parts.

Route:

- Use `makerspace` for fixture or jig planning.
- Use `maker-engineering` when the sculpture is large, overhead, public, or
  wind-loaded enough to harm people.

## Shop Infrastructure

Trigger objects:

- French-cleat panels, wall tool organizers, drill indexes, grinder guards,
  chip trays, machine splash shields, welding-table accessories, hardware bins

Sheet metal tactics:

- Use return flanges, hems, ribs, folded trays, modular slots, labels, and
  replaceable wear strips.
- Bias toward robust edges and easy cleaning over visual delicacy.
- Make hole patterns parametric and match actual fastener bins or tool shanks.
- Add drain/cleanout corners for trays that collect chips, coolant, or dust.

Guardrails:

- Guards and shields near machines are safety devices. Do not call them
  adequate without shop review.
- Avoid reflective glare and snag edges near rotating machinery.

Route:

- Use `makerspace` for machine-specific setup, workholding, and safety review.

## Camping And Outdoor Gear

Trigger objects:

- folding fireboxes, camp stove wind screens, pot stands, camp kitchen boxes,
  lantern hangers, tent stakes, solar panel brackets, compact camp sinks

Sheet metal tactics:

- Use fold-flat panels, hinge tabs, keyed slots, captive pins, stiffening beads
  or flanges, and pack-safe edge guards.
- For hot gear, prefer stainless or plain steel over aluminum near flames.
- Add airflow and ash/soot cleanout paths.
- Make stability visible: foot width, pot centerline, wind-screen footprint,
  and stake angles.

Guardrails:

- Fire gear needs burn, tip, ventilation, and local fire-rule warnings.
- Galvanized, coated, painted, or unknown metal near flame is a fume risk.
- Packable gear needs edge protection so it does not cut bags or hands.

Route:

- Use `maker-engineering` for load-bearing, human-shelter, vehicle-mounted, or
  high-wind outdoor systems.

## Food And Beverage Tools

Trigger objects:

- pour-over stands, espresso knock boxes, drip trays, roasting trays, smoker
  baffles, grill accessories, pizza-oven tools

Sheet metal tactics:

- Prefer stainless for food-contact or wet-contact parts.
- Design for cleanability: open corners, removable trays, no inaccessible
  crevices, no mystery coatings, no trapped oils.
- Isolate hot surfaces from handles and counters.
- Use folded rims for stiffness and hand-safe edges.

Guardrails:

- Do not declare food-safe certification. State material/contact assumptions.
- Avoid galvanized, painted, unknown-plated, oily, leaded brass, or mystery
  scrap for food-contact surfaces.
- Consider dishwasher, acids, salts, coffee oils, heat cycling, and corrosion.

Route:

- Use `maker-engineering` for pressure, steam, combustion, or appliance-like
  devices.

## Camera, Audio, Synth, And Creator Rigs

Trigger objects:

- monitor cages, camera cheese plates, mic brackets, boom-arm mounts, rack
  panels, pedal/effects enclosures, synth panels, field-recording cases

Sheet metal tactics:

- Use standardized hole grids only after verifying exact thread and spacing.
- Add slots for adjustment, captive nuts, PEM hardware, rubber isolation, and
  cable grommets.
- For rack panels, verify rack unit height, hole spacing, and rail standard
  from the actual system.
- Isolate vibration for audio recorders and microphones.

Guardrails:

- Protect cables from sharp panel edges.
- Keep conductive panels away from exposed electronics unless grounding and
  insulation are designed.
- Consider noise, resonance, and handling comfort for audio gear.

Route:

- Use `electronics-enclosures` guidance from `enclosures-bots-and-vehicles.md`
  when the project contains powered electronics.

## Costume Armor And Props

Trigger objects:

- cosplay armor plates, helmets, bracers, masks, sci-fi panels, faux-medieval
  hardware, theatrical lanterns, aged patina props

Sheet metal tactics:

- Use segmented plates, hems, rolled edges, riveted straps, slots for elastic,
  spacer standoffs, and replaceable decorative panels.
- Include motion envelope: shoulder raise, elbow bend, neck turn, sitting,
  walking, kneeling, and quick removal.
- Use light gauges and non-structural finishes where the object is visual.
- Add patina test coupons before treating the hero parts.

Guardrails:

- Body-contact edges need hems, trim, leather/fabric backing, or rubber guards.
- Avoid sharp spikes, exposed burrs, and pinch points for public events.
- Helmets and armor are costume pieces unless properly certified; do not imply
  impact protection.

Route:

- Use `reverse-engineer` first when the user wants to recreate a specific prop
  from photos or a named artifact.

## Furniture Accents

Trigger objects:

- metal drawer fronts, cabinet pulls, table aprons, chair brackets, bent legs,
  decorative corner guards, inlay strips, brass/copper trim

Sheet metal tactics:

- Use bend returns, hidden tabs, countersunk holes, standoffs, and backer
  plates.
- Consider wood movement when metal is fastened across grain.
- Put visible fasteners on intentional spacing and symmetry.
- Use protective finishes to prevent staining wood or hands.

Guardrails:

- Chairs, tables, shelves, and child-facing furniture need load and tip checks.
- Do not bridge wood movement with rigid metal in a way that splits the wood.

Route:

- Use `makerspace` for joinery, jigs, and installation fixtures.
- Use `maker-engineering` for seating, overhead, or child-use safety gates.

## Garden And Balcony Systems

Trigger objects:

- trellises, planter liners, seed trays, plant labels, privacy screens, hose
  guides, rain-chain parts, decorative drip trays

Sheet metal tactics:

- Account for water, soil chemistry, fertilizer salts, UV, wind, and corrosion.
- Use drainage, standoffs, removable liners, rounded corners, and cleanable
  seams.
- For balcony screens or hanging planters, require measured railing/anchor
  interfaces and wind/tip checks.

Guardrails:

- Avoid copper or zinc runoff where plant or animal toxicity matters.
- Balcony objects can fall on people. Route overhead/outboard loads through
  `maker-engineering`.

Route:

- Pair with `houseplant` when the object is designed around a specific plant
  collection, watering workflow, or plant-care database.

## Repair Panels And Restoration

Trigger objects:

- appliance panels, vintage toolbox repairs, motorcycle side covers, dashboard
  inserts, rust patch templates, odd brackets, replacement covers

Sheet metal tactics:

- Preserve observed/measured vs inferred dimensions.
- Use paper/card templates, transfer punches, scribe lines, and first-article
  coupons.
- Match bend radii, hems, beads, hole positions, and fastener clearances from
  the original part.
- Add corrosion isolation between dissimilar metals.

Guardrails:

- Do not guess vehicle, appliance, or structural interfaces from memory.
- For proprietary or safety-related parts, keep outputs repair-focused and
  provisional until measured.

Route:

- Use `reverse-engineer` first for photo/object-derived geometry.
- Use `maker-engineering` for safety-critical vehicle or appliance parts.

## Educational STEM Kits

Trigger objects:

- bend-and-fold geometry kits, simple robot chassis kits, paper-to-metal
  origami lessons, load-test coupons, pre-deburred youth makerspace projects

Sheet metal tactics:

- Use oversized features, generous radii, pre-deburred edges, low-risk
  materials, and visible labels.
- Build in comparison coupons: bend radius A/B, flange length A/B, perforation
  stiffness, tab-slot fit, and load-deflection tests.
- Prefer hand tools, safe fixtures, and adult-operated cutting/forming for
  youth projects.

Guardrails:

- No sharp raw edges in student-handled kits.
- Keep small choking parts, flying chips, pinch points, and hot work out of
  child-facing steps unless supervised and age-appropriate.

Route:

- Use `makerspace` for class/shop setup and facilitator packets.

## Sound And Percussion Objects

Trigger objects:

- tongue drums, gongs, rattles, resonator cones, metal kalimbas, cymbal
  experiments, speaker horns, acoustic reflectors

Sheet metal tactics:

- Separate acoustic intent from sheet metal geometry.
- Use test coupons for tone, sustain, slot width, tongue length, and material
  hardness.
- Avoid over-constraining vibrating surfaces with stiff brackets or weld beads.
- Include damping/isolation choices where the object mounts to a frame.

Guardrails:

- Route tuned instrument design, pitch prediction, bore profiles, and voicing
  to `instrument-maker`.
- Hearing safety matters for loud gongs, horns, or resonant metal experiments.

Route:

- Pair with `instrument-maker` for musical validity and validation logs.

## Output Checklist

For creative maker modules, include:

- object category and intended environment
- material/thickness and finish
- body/contact/heat/water/electrical/motion/load constraints
- CAD feature strategy
- flat pattern and DXF layer plan
- edge treatment
- joining and serviceability
- test coupon or prototype step
- companion skill route
- reason the output is concept, review-ready, or fabrication-ready
