# Toolchain Handoffs

Keep handoffs runtime-agnostic. If a live connector is available, use it. If
not, produce exact file names, layer names, export settings, and manual steps.

## Adobe Illustrator / Creative Cloud

Use for `.ai`, `.pdf`, `.svg`, DXF cleanup, layer naming, artboard control,
swatches, and production-ready vector exports.

- Expand strokes before final cut exports.
- Remove hidden clipping masks and unused embedded images.
- Keep units explicit, preferably mm for fabrication unless the shop uses inches.
- Put registration geometry on a locked/shared layer copied to each output.
- Name layers by process: `CUT_L01_SHADOW`, `ENGRAVE_TEXTURE`,
  `REGISTRATION`, `JIG_BOUNDARY`, `DO_NOT_CUT_PREVIEW`.

Anthropic announced Claude creative connectors on Apr 28, 2026, including
Adobe Creative Cloud, Blender, Autodesk Fusion, and other creative tools. When
working in Claude with those connectors available, prefer direct tool actions
for layer cleanup, export, and batch production. Otherwise provide a manual
handoff.

Reference: https://www.anthropic.com/news/claude-for-creative-work?lang=us

## Photoshop / GIMP / Raster Prep

Use for photo cleanup, posterization, threshold masks, halftone/dither planning,
and separating values before vectorization.

- Preserve an untouched source copy.
- Make high-contrast value masks before vector trace.
- Avoid tiny isolated white/black specks unless they intentionally become dots.
- Use posterization for stencils; use dithering/halftone for engravings when
  the material can resolve it.

## LightBurn / RDWorks / Laser CAM

Use for laser layer assignment, power/speed placeholders, cut order, nesting,
kerf tests, and registration jigs.

- Map SVG/DXF layer colors to process operations.
- Cut internal details before outer boundaries.
- Keep jig and artwork files separate unless the job intentionally cuts both.
- Include an origin convention: lower-left, center, jig pin, or machine home.
- Do not invent final settings without the exact laser/material context.

## Blender

Use for dimensional previews, relief visualization, procedural patterns, and
animation of stack order or light/shadow behavior.

- Convert 2D layers into thin extrusions for preview, not production truth.
- Label objects by layer and material.
- Export manufacturing geometry through reliable 2D formats when the laser/CAD
  path requires it.

## Autodesk Fusion / SolidWorks

Use for CAD safe zones, fixtures, registration pins, rotary jigs, inlay pockets,
and parametric constraints.

- Create named sketches for `Art_Safe_Zone`, `Registration`, `Stencil_Master`,
  `Engrave_Layer`, and `Jig`.
- Preserve the original art file externally; imported curves are often painful
  to edit once embedded.
- Use configurations/components for layer variants rather than overwriting one
  sketch repeatedly.
- Export DXF/SVG per layer with a layer manifest.

## VCarve / CNC Inlay

Use for Broinwood-like pocket/insert workflows and carved inlay operations.

- Separate pocket and insert vectors.
- Track bit type, angle, flat depth, start depth, cut depth, and allowance.
- Include a test inlay before final work.
- Keep laser engraving/cutting notes separate from CNC toolpath notes.
