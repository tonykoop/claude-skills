# Drawing And Visualization

The drawing quality bar is the attached Fender Stratocaster blueprint: a one-page, 22 × 34 inch, AutoCAD R14-style technical drawing with a full-body outline, cavities, contours, centerlines, dimension callouts, and manufacturing intent. Use that level of clarity for instrument drawings even when the visual style changes.

## Blueprint Reference

```text
C:\Users\Tony\Documents\GitHub\laser-cut\docs\Fender62stratocaster-blueprint.pdf
```

Observed metadata:

- PDF 1.3, one page.
- MediaBox: `1584 × 2448 pt`, which is `22 × 34 in`.
- Title: `C:\Program Files\AutoCAD R14\Drawings\StratBody.dwg`.
- Creator: `PSCRIPT.DRV Version 4.0`.

Use it as a style and completeness reference, not as permission to invent guitar dimensions.

## Manufacturing Drawing Checklist

Every serious shop drawing should include:

- **Title block**: instrument, part, scale, units, date, revision, source workbook/CAD ID.
- **Orthographic views**: plan, front/side, section, detail views as needed.
- **Datums**: centerline, bridge line, nut/scale reference, bore axis, head diameter, ring plane, or other primary geometry.
- **Dimensions**: all critical lengths, diameters, radii, hole positions, slot widths, depths, wall thicknesses, clearances, trim allowances.
- **Tolerances**: tuning-critical, fit-critical, and noncritical shop tolerances separated.
- **Materials and finish**: species, thickness, grain direction, metal/ceramic/plastic spec, finish constraints.
- **Operation notes**: CNC side, bit diameter, tabs, fixture pins, laser kerf, lathe centers, steam bend form, drilling sequence.
- **Revision notes and assumptions**.

## Drawing Outputs

Prefer vector or CAD-like artifacts for build-critical drawings:

- **SVG** for lightweight dimensioned diagrams and web review.
- **PDF** for print/shop packets.
- **DXF/SVG** for laser/router templates when geometry is 2D and exact.
- **OpenSCAD/STL/STEP/SolidWorks/Wolfram `Graphics3D`** for 3D geometry when available.
- **PNG/JPEG** only for communication images, previews, BOM plates, renderings.

## AI Image Use

Use image generation for:

- Concept renderings of new instrument families.
- Technical-leaning product sketches that communicate scale, resources, size, material choices, character, concept direction before CAD is complete.
- Blueprint-style explanatory plates when precise dimensions are also provided elsewhere.
- BOM sheets with part illustrations.
- 3D perspective views that help a builder understand form.
- Player/ergonomic views showing scale, hand reach, posture, strap angle, embouchure, lap/standing position, balance.
- Information boards: engineering-poster layouts, editorial explainer pages, reference-sheet layouts, storyboard/process boards, material palettes, callout-heavy comparison plates.

Do NOT rely on image generation for:

- Exact hole spacing, CNC contours, neck pockets, fret locations, bridge placement, fit-critical mating features.
- Supplier-specific hardware geometry unless a measured drawing or CAD model is available.
- Hidden internal geometry not present in the design data.

## Technical Product Sketches

Use these when the team needs a shared mental model before committing to CAD or drawings. Good sketches include:

- One clear hero view with real scale cues.
- Small orthographic or section insets.
- Material swatches and finish labels.
- Resource/BOM badges: stock size, tool class, primary processes, cost band, build difficulty.
- A simplified player/hand/body scale reference for ergonomics.
- Callouts for design characteristics: bore path, head, resonator, strings, tone fields, hardware, handles, fixtures, service access.

Treat these as communication artifacts. Every number must come from a design table/CAD/source measurement or be marked `TBD`; never back-solve dimensions from generated pixels.

## BOM With Images

A strong BOM plate combines a table and visual callouts:

- Thumbnail/photo/render for each part or subassembly.
- Item number matching exploded-view callouts.
- Part name, qty, material/spec, dimensions, source/supplier, estimated cost, operation.
- Group rows by subsystem: body/shell, soundboard/head, neck/bore, strings/reeds/tone fields, hardware, jigs/fixtures, finish/consumables.
- Include make/buy status and drawing references.

For image plates, use actual repo photos where available before generating imaginary parts. Useful local visual references include `ashiko-drum-workshop/images/figure-bom-v2.png`, stave dimension figures, drum build photos, flute photos, CAD/drawing exports.

Tony's Ashiko BOM reference is especially useful:

```text
C:\Users\Tony\Documents\GitHub\ashiko-drum-workshop\images\figure-bom-v2.png
```

Pattern notes:

- Top header names the assembly, quote date, estimated cost.
- A large hero/reference image shows the finished assembly.
- The table reads like a spreadsheet: part number, part name, description, quantity, units, picture, cost each, total.
- Each row has a concrete part image, not just a generic icon.
- Bottom notes record sourcing assumptions, wood species choices, bulk-pricing caveats.

When creating a visual BOM brief, include which images are real photos, which are generated placeholders, and which need replacement with supplier images or shop photos.

## Ergonomic And Player Views

For an ergonomic rendering or critique:

- Establish real scale: overall length, body diameter, weight estimate, strap/support point, player height/hand span assumption.
- Show likely playing posture: seated/standing, left/right hand orientation, embouchure angle, shoulder/neck angle, reach to holes/strings/fields, clearance against torso/lap.
- Mark risk zones: wrist extension, excessive reach, heavy cantilevered neck, sharp edges, blocked controls, poor balance, breath angle, awkward tuning access.
- Suggest geometry changes with dimensions or ranges, not just visual commentary.

## Technical-Drawing Prompt Pattern

When an image prompt is appropriate, include:

- Instrument and view set: plan, side, cross-section, exploded, ergonomic/player.
- Style: technical blueprint, white lines on dark navy, or clean engineering drawing.
- Known dimensions and named datums.
- Labels/callouts to include.
- Explicit instruction that dimension values must match provided data and unknowns should be omitted or marked `TBD`.

Pair the image with a dimension table or vector drawing when the user needs to build from it.
