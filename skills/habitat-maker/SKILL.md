---
name: habitat-maker
metadata:
  version: 0.3.0
  last-updated: 2026-05-10
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

Status: **v0.3** — adds balcony bird-bath support on top of the first
working canonical example (chickadee laser birdhouse). Some habitat types are
still scaffolded; see "Open work" below.

## Trigger phrases

- "design a chickadee birdhouse" / "bluebird box plans" / "bat house build"
- "design a balcony bird bath" / "bird bath for a hot balcony"
- "renter-safe bird bath" / "no-drill balcony habitat"
- "build packet for a [species] birdhouse / bee house / bird feeder"
- "laser-cut [habitat] for [species]" / "CNC [habitat]"
- "parametric birdhouse design" / "regenerate the SVG for the birdhouse"
- "what wall thickness does a chickadee box need?"
- "habitat design for [species]"

## Do not trigger for

- Beekeeping welfare decisions for the `observation-hive` project — that's a
  separate personal/family project with its own design path.
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

## Build packet contract (v0.2)

Every habitat build packet **must** ship:

1. **A single source-of-truth parameter file** — `geometry_params.json` —
   that lists species assumptions, material profile(s), cavity dimensions,
   and panel dimensions in a machine-readable schema.
2. **Generator-backed geometry artifacts** — when the build method involves
   laser, CNC, or other digitally-driven fabrication, the SVG/DXF must be
   produced by a script that reads `geometry_params.json` and emits the
   geometry deterministically. Hand-edited SVGs drift from the prose and
   are forbidden in v0.2 packets.
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
4. **Cut list and BOM** — derived from the parameter file, dimensioned in
   the file's declared units, including kerf-test coupon.
5. **Safety notes** — laser/CNC operation, glue/finish, child-build
   supervision, and animal-welfare cautions.
6. **Agent record** — provenance: which species data fed the packet, which
   material profile was selected, which artifacts were generated vs hand
   authored, what validation was run.

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

- Does not own beekeeping welfare decisions for the `observation-hive`
  project — separate path.
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

## Open work (v0.3 → v1.0)

- Second canonical example: bluebird box (different cavity size, same
  laser method, different species data) to demonstrate the parameter-driven
  re-generation pattern.
- Third canonical example: tube bee house (different habitat type entirely;
  exercises the schema for non-cavity habitats).
- First canonical bird-bath example packet using the balcony/renter reference
  gates and a bill of materials for a low ballasted removable basin.
- Species reference loader (pulls from `habitat-reference` repo when that
  repo is seeded with NestWatch-derived data).
- Method-specific reference docs under `references/` for CNC entrance-hole
  jigs, slip-cast mold prep, and lathe profiles for bird baths.
- Validation generator: emit the validation-checklist.md programmatically
  from `geometry_params.json` so adding a species automatically updates
  the gate set.
