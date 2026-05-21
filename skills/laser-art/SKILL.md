---
name: laser-art
version: 1.0.0
last-updated: 2026-05-10
description: >-
  Cross-platform workflow for turning Adobe Illustrator/vector files, photos,
  hand sketches, written or spoken descriptions, dreams, memories, and stories
  into layered laser art, spray-paint stencils, laser etching/cutting/engraving
  plans, rotary laser wraps, and CNC/laser inlay-ready design packets. Use when
  designing parametric wall art, layered relief, multi-layer stencil posters or
  canvas, safe-zone instrument art, LightBurn/RDWorks/Illustrator/Fusion/Blender/
  SolidWorks handoffs, registration fixtures, layer manifests, bridge checks,
  material/process validation, or artist-inspired fabrication studies based on
  Gabriel Schama, Martin Tomsky, Broinwood/Nik, Eric Standley, or related
  layered cut-paper and wood techniques.
---

# Laser Art

Turn fuzzy human inputs into laser-ready layered art without losing the story.
Support flat art, wall relief, stencil painting, engraving, inlay, rotary wraps,
and CAD-constrained objects.

Use artist references as process inspiration, not exact imitation. Translate
materials, layering logic, registration, rhythm, density, and negative-space
strategies into an original design language.

## Core Workflow

1. Capture the source: image, `.ai`, `.svg`, `.dxf`, sketch, photo, object,
   spoken/written description, dream, memory, or story.
2. Identify the output family:
   - spray-paint stencil set;
   - stacked laser-cut relief;
   - laser etch, raster engrave, or vector engrave panel;
   - CNC or laser inlay/veneer packet;
   - rotary laser wrap;
   - CAD safe-zone art for instruments, furniture, signage, or fixtures.
3. Build a design brief: subject, emotional tone, target size, material,
   machine/process, number of layers, color/material palette, deadline, and
   tolerance needs.
4. Decompose the art into layers: silhouette, shadow, midtone, highlight,
   detail, texture, registration, jig, and optional test coupon.
5. Apply fabrication constraints before aesthetics harden: kerf, minimum bridge
   width, island retention, material grain, paint bleed, engraving contrast,
   tool diameter, rotary seam, fixture pins, and safe zones.
6. Produce the smallest useful output for the user's current stage: concept
   directions, layer plan, file checklist, toolchain handoff, CAD sketch plan,
   SVG/DXF naming scheme, or full fabrication packet.
7. Close the loop with a prototype step: test coupon, one-layer proof, bridge
   check, registration check, then revise.

Ask at most three blocking questions. If the user provided enough context,
state assumptions and proceed.

## Load References

Read only the reference needed for the current task:

- Style translation: [`references/style-profiles.md`](references/style-profiles.md)
- Process choices: [`references/fabrication-modes.md`](references/fabrication-modes.md)
- Creative/CAD software handoffs: [`references/toolchain-handoffs.md`](references/toolchain-handoffs.md)
- Intake and output templates: [`references/intake-output-templates.md`](references/intake-output-templates.md)
- Validation checks: [`references/quality-gates.md`](references/quality-gates.md)

## Intake Heuristics

- If the input is an Illustrator, SVG, PDF, or DXF file, inspect layer names,
  artboard size, units, stroke expansion, clipping masks, embedded rasters, and
  whether registration geometry already exists.
- If the input is a photo or sketch, extract subject, silhouette, value range,
  edge complexity, likely layer count, and areas that will need bridging or
  simplification.
- If the input is a dream, memory, or story, convert it into motifs, motion,
  contrast, symbols, texture, and a layerable visual grammar before proposing
  fabrication.
- If the user wants "parametric" art, define named dimensions, safe zones,
  layer count, material thickness, registration pin diameter, and variable
  pattern rules rather than a single static composition.
- If the user mentions an instrument, route acoustic calculations to
  `instrument-maker` when available; keep this skill focused on art, safe zones,
  paint/engrave/inlay decisions, and registration with the instrument CAD.

## Required Output Fields

For fabrication-ready work, include:

- intent and subject;
- selected fabrication mode;
- material assumptions and safety notes;
- layer manifest with names, colors/materials, purpose, and order;
- registration plan with origin, pins/marks, jig notes, and tolerance target;
- bridge/island strategy;
- file export plan with units, formats, and naming;
- prototype and validation steps.

For early ideation, keep the output lighter: give 2-4 concept directions and a
recommended first prototype.

## Fabrication Safety

Never recommend cutting or engraving unknown plastic, PVC, vinyl, or materials
with unsafe fumes. Ask for material identity or SDS when uncertain. Separate
visual settings from machine settings unless machine, lens, material, thickness,
air assist, and ventilation are known. Prefer a test coupon over confident
speed/power claims.
