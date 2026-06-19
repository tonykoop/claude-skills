---
name: laser-art
version: 0.2.0
last-updated: 2026-06-19
description: >-
  Design laser-cut, laser-engraved, or laser-scored decorative artwork and
  art-adjacent fabrication packets such as layered wall art, edge-lit acrylic
  panels, engraved plaques, signage, ornaments, stencils, and vector-ready
  composition studies. Use when the user wants laser-friendly art direction,
  material/process constraints, SVG/DXF preparation guidance, image-to-vector
  planning, engraving tests, kerf/score/line-weight checklists, or a bridge
  from generated imagery into reviewed laser artwork. Do not use for general
  shop fixtures, CNC/plasma/mill work, structural assemblies, musical
  instruments, or wildlife habitat welfare design; route those to makerspace,
  instrument-maker, or habitat-maker as appropriate.
---

# Laser Art

## Connectors

This skill works best with these MCP connectors. Claude will suggest connecting any that aren't already linked at the point they're needed (via `mcp__mcp-registry__suggest_connectors`).

- **Adobe for Creativity** (`22854937-9510-4b57-9230-62c820102d8f`) — required for template-driven art design, vectorization, image-to-SVG bridges, batch editing, social variations. Suggest at first request for a designed laser-art file.
- **Figma** (`c758d038-d8eb-4421-b426-9dd68dc7f84a`) — optional for pulling design context, iterating posters/labels/cut-sheets that started on a tablet.
- **Canva** (`eb9240f2-e1c1-43c1-828f-0fda40c22e4c`) — optional alternative to Adobe for templated visuals, especially quick mood boards and social mockups.

## Trigger Phrases

- `laser art` / `laser-cut art` / `laser engraved art`
- `make this image laser-ready`
- `turn this into an SVG for engraving`
- `layered wall art` / `edge-lit acrylic art` / `engraved plaque`
- `vector-ready laser artwork`
- `kerf test for this art piece`

## Do Not Trigger For

- General jigs, fixtures, workholding, or CNC/plasma/mill process plans. Route
  to `makerspace`.
- Musical instruments or acoustic design. Route to `instrument-maker`.
- Birdhouses, bat houses, bee houses, feeders, or wildlife habitat. Route to
  `habitat-maker`.
- Pure image generation with no laser/fabrication intent. Use image generation
  directly instead of this skill.

Use `laser-art` when the center of gravity is artwork that must survive laser
translation: clean vector authority, material limits, line-weight choices,
engraving tests, layer order, and honest separation between concept images and
fabrication files.

## Core Boundaries

- Generated images may inspire or preview the composition, but they are not
  fabrication authority.
- Treat reviewed SVG, DXF, CAD, templates, measured drawings, and material test
  coupons as fabrication authority.
- Do not invent machine settings. Ask for the laser model, wattage, lens,
  material, thickness, air assist, bed size, and shop rules, then label any
  starting settings as test-coupon candidates.
- Keep materials safety explicit. Stop on unknown plastics, PVC/vinyl,
  polycarbonate, PTFE/Teflon, chlorinated or fluorinated materials, mirrored
  acrylic backings, coated metals, or mystery coatings until the shop policy or
  material SDS clears them.
- Keep privacy boundaries. Do not publish family photos, private names, private
  addresses, or personal media into public examples without explicit approval.

## Workflow

1. Classify the job:
   - concept art direction
   - image-to-vector planning
   - SVG/DXF readiness review
   - layered art packet
   - engraving test plan
   - edge-lit acrylic or signage packet
2. Gather inputs:
   - artwork source or prompt
   - material and thickness
   - machine/shop constraints
   - final size and display context
   - cut/score/engrave distinction
   - required privacy or licensing limits
3. Establish the authority ladder:
   - `concept`: sketches, prompts, generated images, mood references
   - `review`: vector trace, layer plan, dimensions, material callouts
   - `fabrication`: reviewed SVG/DXF/CAD plus shop-cleared material and test
     coupons
4. Produce the smallest useful artifact set:
   - `design-brief.md`
   - `layer-plan.md`
   - `material-safety.md`
   - `vector-readiness-checklist.md`
   - optional `test-coupon-plan.csv`
   - optional `handoff_checklist.json`
5. Validate before calling it ready:
   - file units are explicit
   - cut, score, and engrave layers are separate
   - dimensions fit the machine bed
   - minimum bridges, islands, tabs, and line weights are reviewed
   - kerf/char/edge finish are handled by test coupons
   - generated or raster previews are clearly marked non-authoritative

## Output Rules

- Mark readiness honestly: `concept`, `review-ready`, or `fabrication-ready`.
- If no vector file has been reviewed, do not say the packet is
  fabrication-ready.
- For SVG/DXF handoffs, name the authoritative file and its revision.
- For image-derived work, include a short trace plan instead of pretending the
  raster image is directly cuttable.
- For public repo artifacts, scrub private/person-identifying content unless
  the user explicitly says it is publishable.

## Version And Install Notes

This skill is versioned through top-level `SKILL.md` frontmatter and
`manifest.yaml`. There is no `laser-art` shell command or `laser-art --version`
shim in v0.1.0; version checks should use `skills-meta` until a real CLI shim
exists.
