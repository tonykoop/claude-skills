# SolidWorks Sheet Metal Reference

Use this file when the project leans heavily on SolidWorks Sheet Metal
features, Master Layout Parts, design tables, equations, or configuration
management. It is the dedicated SolidWorks companion to
`shop-dfm-guardrails.md`.

## Contents

- Master Layout Part (MLP)
- Equations and global variables
- Design tables and configurations
- Sheet Metal feature recipes
- DXF/flat pattern export discipline
- Drawing package
- Common SolidWorks traps
- File naming and assembly hygiene

## Master Layout Part (MLP)

Use a Master Layout Part as the single source of size and interface truth for
any family of sizes, any nested assembly with stacking interfaces, or any
project where multiple sheet metal parts must agree on dimensions.

Recommended MLP contents:

- All global variables (see `parameters.csv` for the project).
- Origin placed deliberately (e.g., bottom center of the controlling envelope
  for a box family).
- Named reference planes for every interface, e.g.,
  `PL_Box_Front`, `PL_Box_Bottom`, `PL_Box_Tub_Rim`, `PL_Box_Lid_Top`,
  `PL_Dolly_Deck_Top`.
- Named layout sketches for every controlled outline, e.g.,
  `SK_Box_Envelope`, `SK_Tub_Profile`, `SK_Lid_Profile`, `SK_Stack_Rim`,
  `SK_Stack_Feet`, `SK_Latch_Zones`, `SK_Hinge_Line`.
- No production sheet metal bodies. Keep the MLP as planes, axes, sketches,
  and simple envelope surfaces only.

Why no production bodies: a production body in the MLP becomes a circular
dependency the first time someone derives a child part from it. Keep skeleton
geometry abstract.

## Equations and Global Variables

SolidWorks Equations accepts named global variables. Quote variable names in
the equations file exactly as SolidWorks expects:

```
"Box_Length"        = 20.000in
"Box_Depth"         = 10.000in
"Box_Height"        =  8.000in
"Material_T_Box"    =  0.060in
"Inside_Bend_R_Box" =  "Material_T_Box"
"Clearance_Gap"     =  0.030in
"Lid_Drop"          =  1.500in
"Hardware_Pitch"    =  2.000in
"Stack_Rim_Height"  =  0.500in
```

Rules:

- Quote variable names; don't omit the quotes inside the Equations dialog.
- Include units explicitly when SolidWorks expects them (in or mm).
- Sort dependent equations after the variables they depend on.
- Comment with intent and units when the equation isn't self-evident.
- Avoid silent rounding; if you round, comment the un-rounded value.
- Never set a dependent value that can be derived from variables. If two
  parameters must agree, derive one from the other.

Derived equations (preferred when possible) keep the family consistent:

```
"Dolly_Deck_Length"     = "Box_Length" + 2.000in
"Dolly_Deck_Depth"      = "Box_Depth" + 2.000in
"Stack_Envelope_3_High" = ("Box_Height" * 3) + 3.000in
"Min_Flange"            = 4 * "Material_T_Box"
"Min_Hole_To_Bend"      = 3 * "Material_T_Box"
"Relief_Size"           = 2 * "Material_T_Box"
```

## Design Tables and Configurations

Use a SolidWorks Design Table when there are 3+ size variants of the same
part, or when one assembly must support multiple top-level configurations.

Design table CSV shape:

```
Configuration,Box_Length_in,Box_Depth_in,Box_Height_in,Material_Thickness_Box_in,...
BOX-20x10x8-SEED,20.000,10.000,8.000,0.060,...
BOX-16x8x6-COMPACT,16.000,8.000,6.000,0.060,...
BOX-24x12x10-LARGE,24.000,12.000,10.000,0.060,...
BOX-20x10x8-ALUMINUM-ALT,20.000,10.000,8.000,0.063,...
```

Rules:

- Column names match the global variable names exactly (without the quotes
  SolidWorks uses in Equations).
- The first row is the seed/default. Downstream configurations should differ
  in meaningful ways (size or material), not just renamed copies.
- Configuration names should encode the differentiator
  (`BOX-{L}x{W}x{H}-{TAG}`).
- Suppress purchased hardware (hinges, latches, casters) by configuration only
  after the seed configuration is stable.

## Sheet Metal Feature Recipes

These features flatten cleanly. Prefer them over arbitrary extrusions.

### Base Flange / Tab

The seed sheet metal feature. Sets material thickness, inside radius, and
K-factor for the whole part. Always start a sheet metal part with this.

### Edge Flange

Adds a straight bend off an existing edge. Common uses:

- Box walls bent up from a flat bottom.
- Lid skirts bent down from a flat top.
- Return flanges on shelves and trays.

Always check that the edge flange direction and angle reference are correct
in the property manager.

### Miter Flange

Bends a continuous frame along a sketch path. Common uses:

- Continuous picture-frame style perimeter flanges.
- Trim flanges around irregular shapes.

Miter flange handles corners automatically. Check the flat pattern unfolds
without overlap.

### Hem

Folds a small return on itself to create a safe edge or stiffener. Hem styles:

- Closed hem (zero gap): strongest stiffener, hardest to form on light brakes.
- Open hem (defined gap): easier on tooling, slightly less stiffening.
- Tear-drop hem: good for hand-safe edges with some clearance.
- Rolled hem: full radius, decorative.

Always verify the chosen hem can be made on the available brake before
specifying it in design.

### Closed Corner

Makes box corners visually closed (the two adjacent walls meet flush). Three
options:

- Butt (no overlap)
- Overlap
- Underlap

Closed corners drive how the flat pattern unfolds at the corner; choose
before generating the DXF.

### Corner Relief

Required where two folds meet at a corner. Without relief, the material bunches
up and either tears or distorts the bend. Default starting size: circular or
tear relief about `2 * T` diameter for 90 degree corners.

### Forming Tool

Used for embossed/punched features: louvers, dimples, drawn flanges, beads.
Forming tools require a punch and a die; do not specify them unless the shop
actually has the tool. They do not unfold cleanly in flat patterns.

### Lofted Bend

The only sheet metal feature that handles tapered, conical, or transitional
shapes that must unfold. Two manufacturing methods:

- `Formed` (smooth rolled or hand-formed). Use for slip-rolled cones, horns,
  bells, and curved transitions.
- `Bent` (faceted brake-bend segments). Use for low-poly faceted forms cut and
  bent on a brake.

Lofted Bend requires sketches at both ends of the loft. The sketches must
produce a valid sheet metal loft (same number of segments, compatible
tangency). If you cannot get a clean flat pattern, the geometry is wrong, not
the feature.

## DXF / Flat Pattern Export Discipline

When exporting a flat pattern as a DXF or DWG:

1. Export 1:1 scale. Always.
2. Set units in the export options and document them in the filename and
   drawing note.
3. Separate layers:
   - `cut`: the actual cut profile.
   - `mark` / `etch`: low-power marking for layout, station lines, or
     alignment witness marks.
   - `bend-centerline`: bend lines from SolidWorks.
   - `construction`: ignored by CAM.
   - `registration`: holes used to align layers or for hardware location, if
     used.
   - `drill-later`: holes too small to plasma cleanly; pierce only.
4. Close all loops. Open loops will confuse plasma CAM and create stuttering.
5. Convert splines to arcs/lines if the CAM workflow demands it.
6. Filename pattern:
   `{PART}_{MATERIAL}_{THICKNESS}_{REV}.dxf` e.g.,
   `SWTB_Tub_U_Shell_MS_060_A.dxf`.

## Drawing Package

For a fabrication-bound design, ship at least:

- Overall assembly drawing with envelope, weight, and stack height.
- One flat pattern drawing per sheet metal part, including:
  - Material callout
  - Stock thickness
  - Bend table (angle, radius, direction, allowance)
  - Inside-radius and K-factor used
  - Grain direction if relevant
  - Critical dimensions tagged
  - Note: 1:1 DXF available separately
- Assembly drawings with hardware callouts and torque/anti-loosening notes
  where applicable.

## Common SolidWorks Traps

1. **Generic extrusion → Convert To Sheet Metal**: technically possible, but
   the flat pattern is usually wrong unless the geometry happens to be valid
   sheet metal. Start with Base Flange instead.
2. **External references to other production parts**: child parts derived
   from each other create dependency loops. Always derive from the MLP, not
   from siblings.
3. **Hidden bend radius mismatch**: per-feature radius overrides can drift
   from the part-level default. Use one radius unless you have a reason.
4. **Hem after closed corner**: a closed corner can prevent a later hem on
   the same edge. Order: hem first if possible.
5. **Tab and slot tolerance**: SolidWorks Tab and Slot feature uses
   nominal-to-nominal. Add `Kerf` and clearance manually unless you've
   confirmed the CAM compensates.
6. **Configuration suppression vs design table override**: design tables can
   override features that aren't actually controlled by the table. Verify the
   table column names match what you expect to drive.
7. **Forming Tool without a real punch**: a SolidWorks forming tool with no
   physical equivalent will look great in CAD and fail at the shop. Verify
   the tool exists before designing around it.

## File Naming and Assembly Hygiene

Use a project prefix and numbered hierarchy:

```
00_<PREFIX>_MasterLayout.SLDPRT
10_<PREFIX>_SubAssembly1.SLDASM
20_<PREFIX>_SubAssembly2.SLDASM
90_<PREFIX>_FamilyLayout.SLDASM
```

Use feature names that map back to `parameters.csv` variable names. The MLP's
named planes and sketches should match the named entities production parts
will derive from.

Save and Pack-and-Go the whole project at every meaningful milestone. Treat
the MLP and design table as the authoritative versioned files; production
parts are derived and can be rebuilt.
