---
name: habitat-maker
version: 0.4.0
last-updated: 2026-05-11
description: >-
  Design wildlife habitat and garden infrastructure — birdhouses, bat houses,
  bee houses, bird baths, bird feeders, planters, pollinator habitat, garden
  signage, and plant supports. Use when designing a species-specific habitat
  or garden support, generating parametric build packets across
  CNC/woodturning/laser/slip-cast/joinery methods, or pairing a habitat design
  with the makerspace skill for parent/grandparent + child builds. Pairs with
  `makerspace` for shop-floor planning and follows `instrument-maker-v4`
  patterns for parametric documentation.
---

# habitat-maker

Generates parametric build packets for wildlife habitat and garden
infrastructure. Companion skill to `instrument-maker-v4` (instruments) and
`makerspace` (shop-floor fabrication).

Status: **v0.4** — adds bat, native bee, observation-hive preflight, and
camera/electronics welfare gates on top of the first working canonical example
(chickadee laser birdhouse). Some habitat types are still scaffolded; see
"Open work" below.

## Trigger phrases

- "design a chickadee birdhouse" / "bluebird box plans" / "bat house build"
- "design a balcony bird bath" / "bird bath for a hot balcony"
- "renter-safe bird bath" / "no-drill balcony habitat"
- "review bat house welfare gates" / "bat box with camera"
- "native bee house" / "solitary bee hotel" / "tube bee house"
- "observation hive design review" / "camera in an observation hive"
- "observation hive design preflight" / "camera in a habitat"
- "build packet for a [species] birdhouse / bee house / bird feeder"
- "laser-cut [habitat] for [species]" / "CNC [habitat]"
- "parametric birdhouse design" / "regenerate the SVG for the birdhouse"
- "what wall thickness does a chickadee box need?"
- "habitat design for [species]"

## Do not trigger for

- Beekeeping welfare decisions, colony management, legal compliance, or live
  bee handling instructions for the `observation-hive` project — that's a
  separate personal/family project with its own design path. `habitat-maker`
  may provide only preflight design caveats for public-facing packets.
- Jig and fixture design — route to `makerspace`.
- Instrument acoustics — route to `instrument-maker-v4`.
- Reverse-engineering an existing habitat object from photos — start with
  `reverse-engineer`, then route here for the parametric packet.

## Owns

- Species/method/material design across these repos:
  - `birdhouses`, `bat-houses`, `bee-houses`
  - `bird-baths`, `bird-feeders`
  - `planters`, `plant-supports`
  - `pollinator-habitat`
  - `garden-signage`
  - `found-cavities` (minimal-intervention repurposing of paused instrument
    blanks as documented habitat)
- Cross-references species/material/method data from the `habitat-reference`
  repo when populated.
- Build packet output that mirrors instrument-maker-v4 conventions (BOM, cut
  list, dimensioned drawings, validation, agent record).

## Build packet contract (v0.4)

Cavity-habitat and generator-backed packets **must** ship:

1. **A single source-of-truth parameter file** — `geometry_params.json` —
   that lists species assumptions, material profile(s), cavity dimensions,
   and panel dimensions in a machine-readable schema.
2. **Generator-backed geometry artifacts** — when the build method involves
   laser, CNC, or other digitally-driven fabrication, the SVG/DXF must be
   produced by a script that reads `geometry_params.json` and emits the
   geometry deterministically. Hand-edited SVGs drift from the prose and are
   forbidden in v0.3 packets.
3. **A welfare-integrated validation checklist** — each acceptance item is a
   pass/fail gate, not a suggestion. The required species-agnostic checks
   are:
   - **No perch.** Perches benefit predators, not the bird.
   - **No interior finish.** Bare wood inside; no paint, stain, oil, or
     sealer. Fledgling claw grip and nestling health depend on this.
   - **Drainage.** ≥ 4 drains in the floor, total ≥ 2 cm² open area.
   - **Ventilation.** Cross-ventilation under the roof line, ≥ 6 cm² per
     side for songbird boxes.
   - **Fledgling grip.** Score lines, kerf grooves, or roughened texture on
     the inside of the front wall below the entrance.
   - **Predator baffle.** Required on pole mounts; documented as
     recommended on tree mounts.
   - **Cleanout access.** Hand-tool removable side, floor, or roof for
     annual cleaning.
   Use [`references/welfare-gate-schema.md`](references/welfare-gate-schema.md)
   as the shared record shape when copying these checks into
   `geometry_params.json`, generated checklists, or future
   `habitat-reference` sourced packets.
4. **Cut list and BOM** — derived from the parameter file, dimensioned in
   the file's declared units, including kerf-test coupon.
5. **Safety notes** — laser/CNC operation, glue/finish, child-build
   supervision, and animal-welfare cautions.
6. **Agent record** — provenance: which species data fed the packet, which
   material profile was selected, which artifacts were generated vs hand
   authored, what validation was run.

Bird-bath and other non-cavity, non-generator-backed water-habitat packets do
not need `geometry_params.json` unless the output includes machine-driven
geometry. For those packets, the maintenance-first reference contract below is
the source of truth.

Bat house, native bee house, observation-hive preflight, and
camera/electronics prompts use the same welfare-gate schema. Start from the
concrete gate families in
[`references/welfare-gate-schema.md`](references/welfare-gate-schema.md) and
turn the relevant ids into pass/fail records before issuing a public packet.
Generated images may support concept/story work, but CAD/DXF/JSON or
dimensioned drawings remain the fabrication authority.

## Bird-bath and balcony packet contract

Bird-bath packets are maintenance-first water-habitat designs, not decorative
objects. Any bird-bath prompt — especially a balcony or renter prompt — must
consult [`references/bird-bath-balcony.md`](references/bird-bath-balcony.md)
and include:

1. **Bird-bath welfare gates** — shallow water depth, textured footing,
   escape path, dump/scrub cadence, mosquito prevention, water-contact
   material safety, heat/evaporation plan, and stability.
2. **Balcony/renter deployment gates** — no-drill anchoring, wind/tip
   resistance, drip control, window-strike posture, railing and neighbor
   constraints, and travel-dry behavior.
3. **Material safety matrix** — known-safe, conditional, and reject guidance
   for ceramic/glaze, concrete, stone, plastic, stainless steel, copper
   alloys, galvanized metal, treated wood, paint/sealer, and unknown glaze.
4. **Compact pass/fail checklist** — enough for a balcony owner to reject an
   unsafe setup before filling it.
5. **Optional fill-depth gauge** — a printable or hand-drawn gauge that marks
   the entry-depth, maximum-depth, and no-overflow fill line.

For hot-climate balcony packets, default to a low, ballasted, removable basin:
morning sun or bright shade; no railing clamp for v1; no pump/bubbler unless
the prompt explicitly accepts wiring, splash, cleaning, and evaporation burden.

## Bat, bee, observation-hive, and electronics welfare contract

Bat house, native bee house, observation-hive preflight, and camera/electronics
prompts must consult
[`references/bat-bee-observation-hive-welfare.md`](references/bat-bee-observation-hive-welfare.md)
and include the relevant pass/fail gates:

1. **Bat house gates** — rough landing and roost surfaces, chamber spacing,
   heat and sun posture, predator exclusion, untreated interior, exterior-only
   weatherproofing, mounting stability, and no disturbance during maternity or
   hibernation-sensitive windows.
2. **Native bee house gates** — solitary native bee scope, dry overhang,
   cleanable or replaceable tubes/blocks, correct tunnel sizing for the target
   group, smooth tunnel interiors, parasite/mold management, and no honeybee
   colony-management claims.
3. **Observation-hive preflight gates** — explicit route-out for beekeeping
   decisions, qualified keeper review, secure containment, ventilation and
   thermal management, escape-proof service access, and public/privacy safety.
4. **Camera/electronics gates** — no animal-contact protrusions, no exposed
   wires in occupant paths, low heat load, weatherproof external routing,
   service access without disturbing occupants, and no lights/IR/audio unless
   species-safe evidence is documented.

When copying these checks into packet JSON, generated checklists, or future
`habitat-reference` records, preserve the reference's reusable gate record
shape: stable gate id, scope, pass condition, fail remedy, evidence, and
provenance.

For camera-enabled habitat packets, generated concept images may communicate
placement ideas, but CAD/DXF/JSON or dimensioned packet artifacts remain the
fabrication authority.

## Generator-backed artifacts: when to require them

When a build packet's method is **laser**, **CNC**, **plotter-cut vinyl**,
or any other digitally-driven fabrication, the agent **must** prefer a
generator script over hand-drawn vector files. Concretely:

- The agent generates `geometry_params.json` first (or updates it if it
  exists), then regenerates the SVG/DXF by invoking the generator script.
- Hand-edits to the SVG/DXF that do not flow back to `geometry_params.json`
  are not accepted; the next regeneration would silently overwrite them.
- The generator script lives next to the example packet under `scripts/`
  in the example folder, **or** under `skills/habitat-maker/scripts/` for
  shared generators usable across packets.

For methods that are not digitally-driven (woodturning a bird bath bowl,
slip-casting a ceramic feeder, hand-joining cedar planks), prose drawings
and dimensioned sketches remain the artifact of record. Generator-backed
artifacts are required only where the geometry actually drives a machine.

## Boundaries

- Does not own beekeeping welfare decisions, colony management, legal
  compliance, or live bee handling for the `observation-hive` project —
  separate path. Keep public packets free of private family/media details.
- Does not duplicate `makerspace` (jigs / fixtures / workholding) or
  `instrument-maker-v4` (instrument acoustics) — route accordingly.
- Public-facing designs intended for makerspace family builds (parent or
  grandparent + child) should be friendly to that audience: chamfered
  edges, no exposed fasteners on the inside, removable cleanout, no specialty
  tools.

## Canonical examples

- [`examples/chickadee-laser-baltic-birch/`](examples/chickadee-laser-baltic-birch/)
  — generator-backed laser-cut chickadee birdhouse. Use as a fixture for
  any new species/method packet in this skill: the file layout, the
  parameter schema, the validation gate set, and the agent record format
  are normative.
- [`references/bird-bath-balcony.md`](references/bird-bath-balcony.md)
  — normative reference for bird-bath welfare gates, balcony/renter
  deployment constraints, material safety matrix, and compact fill/deployment
  checks.
- [`references/bat-bee-observation-hive-welfare.md`](references/bat-bee-observation-hive-welfare.md)
  — normative reference for bat house, native bee house, observation-hive
  preflight, and camera/electronics welfare gates.
- [`references/welfare-gate-schema.md`](references/welfare-gate-schema.md)
  — shared pass/fail welfare-gate schema for packet-local records and the
  future `habitat-reference` import workflow.

## Open work (v0.4 → v1.0)

- Second canonical example: bluebird box (different cavity size, same
  laser method, different species data) to demonstrate the parameter-driven
  re-generation pattern.
- Third canonical example: tube bee house (different habitat type entirely;
  exercises the schema for non-cavity habitats).
- First canonical bat-house example packet using the bat/electronics welfare
  gates without an internal camera by default.
- First canonical bird-bath example packet using the balcony/renter reference
  gates and a bill of materials for a low ballasted removable basin.
- Species reference loader (pulls gate records and species data from the
  `habitat-reference` repo when that repo is seeded, preserving packet-local
  welfare gates if the shared reference is incomplete and preserving the shared
  welfare-gate schema for imported records).
- Method-specific reference docs under `references/` for CNC entrance-hole
  jigs, slip-cast mold prep, and lathe profiles for bird baths.
- Validation generator: emit the validation-checklist.md programmatically
  from `geometry_params.json` so adding a species automatically updates
  the gate set.
