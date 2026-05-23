# SolidWorks Plan - Stackable Sheet Metal Toolbox Family + Dolly

Top-down assembly driven by a Master Layout Part (MLP). Every size variant
is selected from a Design Table on the MLP; every child part inherits its
controlling sketches and planes from the MLP through derived sketches. The
dolly is part of the same family layout assembly so its deck rim always
matches the current box base.

## File Tree (Planning Names)

```
00_SWTB_MasterLayout.SLDPRT            # MLP - the single source of truth
10_SWTB_Tub.SLDPRT                     # Sheet metal tub body (U-fold + ends)
11_SWTB_Lid.SLDPRT                     # Sheet metal lid body (clamshell)
12_SWTB_Tray_Stepped_Hanger.SLDPRT     # Drop-in tray (optional)
20_SWTB_Box_Assy.SLDASM                # Tub + lid + hinge + latches + feet
30_SWTB_Dolly_Deck.SLDPRT              # Sheet metal dolly deck
31_SWTB_Dolly_Caster_Doubler.SLDPRT    # Doubler plate at caster bolt pattern
32_SWTB_Dolly_Handle_Bracket.SLDPRT    # Handle spine receiver bracket
40_SWTB_Dolly_Assy.SLDASM              # Dolly deck + doublers + casters + handle
90_SWTB_FamilyLayout.SLDASM            # MLP + Box Assy + Dolly Assy + stack rep
```

## Master Layout Part Contents

The MLP holds only planes, axes, sketches, and simple envelope surfaces.
No production sheet metal bodies live here.

Named reference planes:

- `PL_Box_Bottom` - origin (bottom center of seed envelope)
- `PL_Box_Top` - top of tub before lid; height = `Tub_Height`
- `PL_Box_Lid_Top` - top of lid; height = `Box_Height`
- `PL_Box_Front`, `PL_Box_Back`, `PL_Box_Left`, `PL_Box_Right` - vertical
  face planes at +/- `Box_Length/2` and +/- `Box_Depth/2`
- `PL_Tub_Rim` - tub rim plane; height = `Tub_Height`
- `PL_Stack_Rim_Top` - rim plane top; height = `Box_Height + Stack_Rim_Height`
- `PL_Dolly_Deck_Top` - dolly deck plane
- `PL_Hinge_Line` - axis-defining plane at back face

Named layout sketches:

- `SK_Box_Envelope` - rectangle `Box_Length x Box_Depth` at `PL_Box_Bottom`
- `SK_Tub_Profile` - outline of tub body for derived sketch reference
- `SK_Lid_Profile` - outline of lid skirt
- `SK_Stack_Rim` - perimeter rim outline at lid top
- `SK_Stack_Shoulder` - perimeter inset on next box's base
- `SK_Latch_Zones` - rectangles where latch bases attach
- `SK_Hinge_Line` - line along back face where piano hinge mounts
- `SK_Dolly_Deck_Envelope` - dolly outline `Dolly_Deck_Length x Dolly_Deck_Depth`
- `SK_Dolly_Rim` - upward rim outline matching `SK_Stack_Rim`
- `SK_Caster_Pattern` - four caster bolt patterns at deck corners

## Equations And Global Variables

Quote variable names exactly as written. Units in inches.

```
"Box_Length"             = 20.000in
"Box_Depth"              = 10.000in
"Box_Height"             =  8.000in
"Material_T_Box"         =  0.060in
"Inside_Bend_R_Box"      =  "Material_T_Box"
"K_Factor_Box"           =  0.44
"Clearance_Gap"          =  0.030in
"Lid_Drop"               =  1.500in
"Hardware_Pitch"         =  2.000in
"Stack_Rim_Height"       =  0.500in
"Tub_Height"             =  "Box_Height" - "Lid_Drop"
"Lid_Height"             =  "Lid_Drop"
"Stack_Shoulder_Inset"   =  "Stack_Rim_Height" + "Clearance_Gap"
"Min_Flange"             = 4 * "Material_T_Box"
"Min_Hole_To_Bend"       = 3 * "Material_T_Box"
"Relief_Size"            = 2 * "Material_T_Box"
"Dolly_Deck_Length"      = "Box_Length" + 2.000in
"Dolly_Deck_Depth"       = "Box_Depth"  + 2.000in
"Material_T_Dolly"       =  0.105in
"Inside_Bend_R_Dolly"    =  "Material_T_Dolly"
"K_Factor_Dolly"         =  0.44
"Dolly_Skirt_Height"     =  2.000in
"Stack_Envelope_3_High"  = ("Box_Height" * 3) + ("Stack_Rim_Height" * 6)
"Stack_Envelope_4_High"  = ("Box_Height" * 4) + ("Stack_Rim_Height" * 8)
```

Notes:

- `Inside_Bend_R_Box` and `Inside_Bend_R_Dolly` are driven equal to thickness
  by default (`R >= T` rule). Override only if a measured punch radius is
  larger.
- `Tub_Height` and `Lid_Height` are derived so the lid skirt always overlaps
  the tub by exactly `Lid_Drop`.
- Stack envelopes assume each interface (rim + shoulder) adds `Stack_Rim_Height`
  twice per box. Adjust if rim and shoulder overlap nests instead of stacking.

## Design Table (Configurations On The MLP)

Driven by `family-design-table.csv`. The first row is the seed; the rest are
the immediate family.

| Configuration | Box_Length | Box_Depth | Box_Height | Material | Material_Thickness | Notes |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| `BOX-20x10x8-SEED` | 20.000 | 10.000 | 8.000 | Mild Steel 16 ga | 0.060 | seed |
| `BOX-16x8x6-COMPACT` | 16.000 | 8.000 | 6.000 | Mild Steel 16 ga | 0.060 | smaller hand-carry |
| `BOX-24x12x10-LARGE` | 24.000 | 12.000 | 10.000 | Mild Steel 16 ga | 0.060 | verify stiffness; may need return flanges |
| `BOX-20x10x8-AL-ALT` | 20.000 | 10.000 | 8.000 | Aluminum 5052 14 ga | 0.063 | material variant; flat pattern re-export |

Configuration name pattern: `BOX-{L}x{D}x{H}-{TAG}` for size variants;
`BOX-{L}x{D}x{H}-{MATERIAL}-{TAG}` when material differs.

## Feature Sequence Per Part

### 10_SWTB_Tub (Tub Body)

Strategy: single U-fold front-to-back, with relieved corner end-cap closure
(TIG seam or rivet line at the two vertical end corners). This avoids
trapping the part in the brake on a four-sided pull.

1. Insert Base Flange from a derived sketch of `SK_Tub_Profile` (bottom
   rectangle `Box_Length x Box_Depth`). Set thickness `Material_T_Box`,
   inside radius `Inside_Bend_R_Box`, K-factor `K_Factor_Box`.
2. Edge Flange on front long edge: height `Tub_Height`, direction up,
   inside-side reference. Add corner reliefs at both ends; relief diameter
   `Relief_Size`.
3. Edge Flange on back long edge: same parameters as step 2.
4. Edge Flange on left short edge: height `Tub_Height`, direction up. Set
   Closed Corner option to Butt against the front flange; leave the back as
   open (will weld or rivet to back flange later).
5. Edge Flange on right short edge: same as step 4.
6. Closed Corner feature between front-and-left and front-and-right edges
   (Butt option). Reliefs at intersections.
7. Tear-drop Hem on the entire tub rim (top edges of all four walls).
   Inside radius equal to `Material_T_Box`. Verify hem is reachable on
   available brake before fabrication release.
8. Cut Sketch on back face for piano hinge knuckle slots (driven from
   `SK_Hinge_Line`), and on front face for latch base mounting holes
   (driven from `SK_Latch_Zones`). Holes at `Min_Hole_To_Bend` minimum from
   bend centerline.
9. Flat Pattern feature - verify clean unfold, no overlapping reliefs.

### 11_SWTB_Lid (Lid Body)

Strategy: lid top + four-sided skirt with closed-corner butt joins, with
an outward perimeter rim that becomes the stack-clocking feature.

1. Base Flange from derived sketch of `SK_Lid_Profile` (top rectangle
   `Box_Length x Box_Depth`). Same material setup as tub.
2. Edge Flange (skirt) on all four edges: height `Lid_Drop`, direction
   down, inside-side reference. Closed Corner Butt on all four corners.
3. Edge Flange (rim): on the four outside top edges of the skirt - no wait
   - the rim is a separate feature. Instead, add an outward Edge Flange off
   the *top* of the lid: height `Stack_Rim_Height`, direction up, inside-set
   to outside (so the rim sits proud of the lid top). Path defined by
   `SK_Stack_Rim`.
4. Tear-drop Hem on the bottom skirt edge for hand-safe edges. Inside
   radius `Material_T_Box`.
5. Cut Sketch on back skirt for piano hinge knuckle slots, on front skirt
   for latch keepers.
6. Flat Pattern feature - verify.

### 12_SWTB_Tray_Stepped_Hanger (Optional)

A drop-in tray sized to hook over the tub rim.

1. Base Flange from a derived sketch sized `Box_Length - 2*Clearance_Gap`
   by `(Box_Depth - 2*Clearance_Gap)/2`.
2. Edge Flange on the four sides: height 2.0 in (use tray depth variable
   if added). Closed Corner Butt.
3. Tear-drop Hem on rim.
4. Stepped hanger lip on the two long edges - a downward edge flange to
   hook over the tub rim.

### 30_SWTB_Dolly_Deck (Dolly Deck)

Strategy: flat deck with four downward structural skirts, upward locating
rim sized to match `SK_Stack_Shoulder` on the bottom of any box.

1. Base Flange from `SK_Dolly_Deck_Envelope`. Thickness `Material_T_Dolly`,
   radius `Inside_Bend_R_Dolly`, K-factor `K_Factor_Dolly`.
2. Edge Flange (skirt) on all four edges, downward, height
   `Dolly_Skirt_Height`. Closed Corner Butt on all four corners. Corner
   reliefs at `2 * Material_T_Dolly` diameter.
3. Edge Flange (rim) - upward, height `Stack_Rim_Height`, path from
   `SK_Dolly_Rim`. Matches the lid rim so any box bottom drops in and
   self-locates.
4. Cut Sketch for caster bolt patterns at four corners and for handle
   bracket attachment at the rear.
5. Tear-drop Hem on the bottom skirt edge.
6. Flat Pattern feature - verify.

### 31_SWTB_Dolly_Caster_Doubler

Simple flat plate driven from `SK_Caster_Pattern`. Thickness
`Material_T_Dolly`. Holes match deck pattern. Two doublers stacked under
each caster mount as planning baseline (subject to caster manufacturer
recommendation).

### 32_SWTB_Dolly_Handle_Bracket

Two formed brackets at the rear that receive a square-tube handle spine
(handle is purchased stock, out of scope as a sheet-metal part).

## Assembly Mates (20_SWTB_Box_Assy)

- Concentric: hinge knuckle slot on tub back to hinge knuckle slot on lid
  back, driven by `SK_Hinge_Line`.
- Coincident: tub back face + lid back skirt face when lid is closed (with
  `Clearance_Gap` mate offset).
- Distance / Limit mate: lid swing 0 to ~110 deg.
- Concentric: latch base bolt holes on tub front to latch keeper on lid.
- Fasten/Lock: foot pads to underside of tub at four corners.

## Assembly Mates (40_SWTB_Dolly_Assy)

- Concentric: each caster bolt pattern to its doubler plate hole pattern,
  to the deck hole pattern.
- Coincident: caster top plate to underside of deck (with doubler in
  between).
- Concentric: handle bracket bolts to deck hole pattern.

## Family Layout Assembly (90_SWTB_FamilyLayout)

- Insert MLP at origin.
- Insert Box Assy (`20_SWTB_Box_Assy`) at MLP origin, mated to MLP envelope.
- Insert Dolly Assy (`40_SWTB_Dolly_Assy`) below the box, deck rim mated to
  base of the bottom box with `Clearance_Gap`.
- Use Configurations to show: single box on dolly; 3-high stack on dolly;
  4-high stack on dolly. Verify center-of-gravity height stays inside the
  caster footprint at full load.

## Top-Down Discipline Checklist

- All controlling sketches live on the MLP and are derived (not copied)
  into child parts.
- Production sheet metal parts contain no external references to other
  production parts. Only MLP -> child, never sibling -> sibling.
- Each child part has its own configuration table linked to the MLP's
  configuration so size changes propagate.
- File Pack-and-Go is the supported transport mechanism for the whole
  family.

## Known SolidWorks Traps For This Project

- Forming Tool for the stack rim is tempting but unfolds poorly. Use an
  Edge Flange off the lid top instead.
- Closed Corner before Hem on the tub rim will not unfold cleanly. Sequence
  is corners first, hem last for the tub. Lid rim is an Edge Flange so the
  order doesn't trap.
- Design table column names must match the global variable names exactly
  (without quotes). Watch underscores.
- If the tub U-fold approach is replaced with a four-sided pull, re-check
  that the part fits the brake fingers without trapping at the last bend.
