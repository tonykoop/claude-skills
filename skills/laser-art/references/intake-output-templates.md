# Intake and Output Templates

Use these templates when the user wants a reusable packet or when the project
is too fuzzy to fabricate safely without structure.

## Fast Intake

Ask only what blocks progress:

1. What is the final object and approximate size?
2. Which process should lead: spray stencil, layered cut relief, engraving,
   inlay, rotary wrap, or CAD safe-zone art?
3. What materials and machine/toolchain are available?

If the user supplied a story or memory, ask what feeling must survive the
translation, not only what object should appear.

## Design Brief

```text
Project:
Source input:
Final object:
Target size:
Fabrication mode:
Material/substrate:
Machine/toolchain:
Layer count target:
Palette or material contrast:
Style/process inspirations:
Registration method:
Known constraints:
Unknowns:
First prototype:
```

## Layer Manifest

```text
L00_BACKER_OR_SUBSTRATE
  Purpose:
  Material/color:
  Operation:
  Notes:

L01_SHADOW_OR_BASE
  Purpose:
  Material/color:
  Operation:
  Bridges/islands:
  Registration:

L02_MIDTONE
  Purpose:
  Material/color:
  Operation:
  Bridges/islands:
  Registration:

L03_HIGHLIGHT
  Purpose:
  Material/color:
  Operation:
  Bridges/islands:
  Registration:

L04_DETAIL
  Purpose:
  Material/color:
  Operation:
  Bridges/islands:
  Registration:

JIG_OR_REGISTRATION
  Pin diameter:
  Origin:
  Tolerance target:
```

## File Naming

```text
projectname_00_reference-not-cut.svg
projectname_01_shadow-cut.svg
projectname_02_midtone-cut.svg
projectname_03_highlight-cut.svg
projectname_04_detail-cut.svg
projectname_registration-jig.svg
projectname_layer-manifest.md
projectname_test-coupon.svg
```

## Concept Directions

For early ideation, produce:

- 2-4 named directions;
- one sentence of emotional intent per direction;
- target fabrication mode;
- likely layer count;
- primary risk;
- recommended first prototype.

## Handoff Prompt

```text
Use laser-art to convert this source into a fabrication packet.
Input:
Desired object/process:
Material and machine:
Target size:
Must preserve:
Avoid:
Output needed now:
```
