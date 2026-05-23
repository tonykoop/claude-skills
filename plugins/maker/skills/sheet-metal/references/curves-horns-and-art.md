# Curves, Horns, And Stacked Art

Use this file for slip-rolled cylinders and cones, SolidWorks Lofted Bend,
musical horn sheet metal, and geometric stacked wood-metal art.

## Contents

- Slip-rolled cylinders
- Slip-rolled cones
- SolidWorks Lofted Bend deep dive
- Musical horns and bells
- Annealing and material work-hardening
- Seam strategies for acoustic and decorative work
- Planishing and finishing
- Stacked geometric art
- Output checklist

## Slip-Rolled Cylinders

Cylinder blank planning:

```
flat_width  = pi * finished_diameter + seam_allowance + 2 * trim_margin
flat_height = finished_height
```

Use `scripts/sheet_metal_math.py cylinder-blank` for first-pass estimates.

Planning rules:

- Large floor slip roller minimum radius: about 1 inch (Maker Nexus profile).
- Tabletop slip roller minimum radius: about 0.75 inch.
- Slip rollers leave flat unbent regions at leading and trailing edges of the
  plate. Plan for sacrificial trim: 1.5 to 2 inches at each end if a
  continuous curve is required, OR pre-bend the ends by hand or with a brake
  before feeding the roller.
- Add alignment marks and seam witness lines on the flat blank, etched at low
  power so they survive rolling but don't compromise the finish.
- Choose the seam style at the design stage, not at the bench: butt seam,
  lap seam, riveted seam, folded lock seam, soldered seam, brazed seam, or
  TIG seam.

Feed orientation matters: feed the blank so the grain (or rolling direction
of the stock) runs across the bend axis, not along it. This produces a more
uniform curve.

## Slip-Rolled Cones

A cone is a tapered cylinder. Rolling one on straight rollers requires
angling the feed so the narrow end stays put while the wide end travels
faster. This is a hand technique; even with the same flat pattern, two
operators may produce different results.

Developed cone blank math:

```
slant_length L = sqrt((R_large - R_small)^2 + height^2)
arc_radius_large = L * R_large / (R_large - R_small)   # outer arc radius
arc_radius_small = L * R_small / (R_large - R_small)   # inner arc radius
arc_angle (radians) = (R_large - R_small) / L * 2*pi   # subtended angle, no
                                                       # this is the
                                                       # half-angle factor;
                                                       # see below
```

The exact developed-blank arc geometry is:

- The developed blank is the annular sector between two concentric arcs.
- Inner arc radius:  `r1 = L * R_small / (R_large - R_small)`
- Outer arc radius:  `r2 = L * R_large / (R_large - R_small)`
- Subtended angle:   `theta = 2 * pi * (R_large - R_small) / L` radians
- Where `R_small` and `R_large` are the cone end radii, `height` is the
  axial height, and `L` is the slant length.

For dramatic flares (large `R_large / R_small` ratio), the developed sector
gets close to a full circle. At that point, segmenting the cone into 2-3
sections produces a better result than rolling one giant sector.

Segmentation rules of thumb:

- If `R_large / R_small > 3`, consider 2 segments.
- If `R_large / R_small > 6`, consider 3 segments (throat / mid / bell).
- Each segment should have a slip-roll-friendly entry diameter (>= minimum
  roller radius).

## SolidWorks Lofted Bend Deep Dive

Lofted Bend is the only sheet metal feature that handles tapered or
transitional geometry while still producing a flat pattern.

Two manufacturing methods:

- **Formed**: the flat pattern represents the developed surface of a smooth
  rolled or hand-formed part. Use for slip-rolled cones, horns, bells, and
  curved transitions.
- **Bent**: the flat pattern is broken into faceted brake-bend segments. Use
  for low-poly faceted forms cut and bent on a brake.

Requirements:

- Two profile sketches at opposite ends of the loft. Both must be valid for
  sheet metal lofting (same number of segments, compatible tangency,
  consistent winding).
- Material thickness and K-factor set on the part (Base Flange convention).
- The two profiles should sit on parallel planes (most common case) or on
  planes whose intersection lies outside the lofted body.

If Lofted Bend errors:

- Check that the two profiles have the same number of geometric entities.
- Check that the entities are in the same order around each profile.
- Check that the planes are positioned correctly (no impossible geometry).
- For dramatic tapers, try splitting into two or more lofts rather than one.

For non-circular cross-sections (oval, elliptical, polygonal), Lofted Bend
still works but produces a more complex developed shape. Always paper-pattern
test before committing to metal.

## Musical Horns And Bells

This skill owns sheet metal forming, seams, annealing reminders, and flat
blank planning. Route acoustic bore profile, tuning, tone-hole or valve
acoustics, embouchure feel, and instrument validation to `instrument-maker`.

Materials:

| Material | Character | Workability | Joining notes |
| --- | --- | --- | --- |
| Yellow brass | bright traditional response | work-hardens fast | silver braze or solder; seamless ideal |
| Red brass / gilding metal | slightly darker, warmer | similar to yellow brass, slightly softer | silver braze or solder |
| Copper | warm, dark | very malleable, easy to form by hand | solder, braze, or careful TIG |
| Aluminum | light, modern, sterile | crack-prone in tight bends; TIG-only joining at horn thicknesses | TIG, test first |
| Mild steel | experimental, heavy, rusts | easy to cut and bend | MIG/TIG; corrosion concerns |
| Bronze | rich, complex tone | harder to work; specialty | silver braze typically |

Common horn thicknesses: 20-gauge to 24-gauge (0.020" to 0.040" or so).

Fabrication workflow for a single horn segment:

1. **Define ownership**: acoustic intent (bore profile, target pitch, voicing)
   to `instrument-maker`; forming geometry (slant length, blank shape) here.
2. **Segment the horn**: throat, middle, bell flare. Each segment is a
   single Lofted Bend in SolidWorks (Formed method).
3. **Generate flat blanks**: export each segment's flat pattern as a DXF
   with seam witness marks and station lines on a separate `mark` layer.
4. **Cut the blanks**: thin material favors a fine plasma setting, laser
   (where the shop has it), or shear with hand finishing. Test the kerf and
   edge quality on a coupon before cutting the real blank.
5. **Pre-bend the seam edges**: a gentle pre-bend on each long edge of the
   blank helps the slip roller catch the material and reduces flat-spot
   problems at the seam.
6. **Roll partially**: bring the segment to roughly its target curvature.
   When resistance rises sharply or small surface cracks appear, stop.
7. **Anneal**: heat the segment to a dull red, hold briefly, and quench in
   water (copper/brass tolerate water quench; aluminum does not). This resets
   the work-hardened crystalline structure.
8. **Finish rolling**: complete the curvature, holding the seam in alignment.
9. **Join the seam**: butt seam preferred for acoustic interior smoothness;
   align with witness marks; tack at a few points; solder or braze along the
   seam.
10. **Planish over a mandrel**: place the segment over a polished steel cone
    or stake and gently tap with a planishing hammer to smooth out facets and
    work-harden the surface uniformly.
11. **Join segments**: butt or lap-join consecutive segments, with the same
    interior-smoothness considerations.
12. **Validate diameters**: measure at each design station against the design
    table; route any acoustic-impacting deviation to `instrument-maker`.

## Annealing And Material Work-Hardening

Why anneal: brass, copper, and bronze work-harden as they are bent, rolled,
hammered, or planished. The metal becomes progressively stiffer and more
brittle until it cracks. Annealing restores ductility.

Annealing procedure (general; specifics vary by alloy):

- Heat the part with a propane or MAPP torch to the alloy's annealing
  temperature. For yellow brass, that's a dull red glow in a dim room (about
  700-1100 °F depending on alloy).
- Hold briefly (a few seconds at temperature is usually enough for thin
  sheet).
- Quench in water for copper and brass; air-cool for some alloys; never water
  quench aluminum (it does not respond and may warp).
- Clean the part with a pickle (citric acid or vinegar will work for hobby
  scale; the shop may have a proper pickle).
- Resume forming.

When to anneal:

- When resistance to forming rises noticeably.
- When small surface cracks appear at bend lines.
- Routinely between major forming steps for thin brass and copper.
- Before final shaping if the part has already been worked.

Annealing is shop-instructor territory if the user has never done it before:
torch work, flux, fumes, and hot metal all carry risk.

## Seam Strategies For Acoustic And Decorative Work

For acoustic interior smoothness:

- **Butt seam** (zero-clearance): two edges meet without overlap. Best for
  acoustic interior because there is no internal ridge to disturb air flow.
  Requires careful blank prep and skilled joining.
- **Lap seam** with interior smoothing: one edge overlaps the other; the
  interior step is ground or scraped smooth after joining. Acceptable for
  loud or aggressive sounds where minor interior ridges don't matter.
- **Folded lock seam**: traditional sheet metal joint; not appropriate for
  acoustic interior.

For decorative work (lanterns, sconces, plant liners, art):

- Folded lock seams, riveted lap seams, and TIG/MIG welded butt seams are all
  fine.
- The seam can be a design feature (visible rivets) or hidden (interior
  weld).

For load-bearing rolled cylinders:

- TIG or MIG weld a butt seam with full penetration if the cylinder will be
  loaded (pressure, hanging weight).
- Inspect the weld; route load-bearing welds to `maker-engineering` if the
  failure mode could hurt someone.

## Planishing And Finishing

Planishing smooths out facets and surface irregularities by lightly tapping
the metal between a planishing hammer and a polished stake or mandrel.

Tools:

- Planishing hammer with a polished face.
- Polished steel stake or mandrel matching the interior curvature.
- Sandbag for shaping organic curves.

Technique:

- Light, overlapping blows.
- Don't drive the metal hard; the goal is to compress the surface, not to
  stretch or distort.
- Rotate the work frequently to keep the stake/mandrel mark moving.

After planishing, the part is ready for polishing:

- 240 grit → 400 → 600 → polishing compound for brass and copper.
- Brass-brushed finishes hide minor facets; mirror polish reveals every
  defect.

## Stacked Geometric Art

Use this mode for folded low-poly forms, layered reliefs, and Gabriel
Schama-inspired stacked wood-metal studies.

Layering offset math:

The "depth illusion" depends on consistent offsets between layers. Three
common patterns:

- **Concentric uniform offset**: every layer steps inward by a fixed amount
  (e.g., 0.060" or 0.125"). Produces a regular tunnel effect.
- **Concentric geometric offset**: offsets follow a geometric series
  (e.g., 0.060", 0.120", 0.240", ...). Produces an accelerating
  perspective.
- **Free composition**: each layer has its own shape; alignment is by
  registration pin only. Best for Schama-style intricate mandalas.

For uniform offset:

```
layer_n_radius = layer_0_radius - n * offset
```

For geometric offset:

```
layer_n_radius = layer_0_radius - sum(initial_step * ratio^k for k in 0..n)
```

Registration discipline:

- Three registration holes (3-2-1 layout, not collinear) in a scrap border or
  hidden backplate. Two holes are theoretically enough; three eliminates
  rotational drift.
- Hole diameter `1/8 inch` (3.175 mm) is a common standard; brass dowel pins
  or wooden dowels are easy to source.
- Plot the holes on a separate `registration` DXF layer so they don't get
  included in production cuts.

Material stack ideas:

- Mahogany, walnut, or birch for warm wooden top layers.
- Brass or copper thin accent layers for shimmer.
- Dark-stained or ebonized oak/birch base layers for shadow depth.
- Patinated steel or blued steel backplates for industrial contrast.

Authority:

- Generated images can propose mood, composition, and depth.
- Fabrication authority is the reviewed SVG/DXF/CAD layer stack plus material
  and test-coupon notes. The pattern that the laser cuts is the
  authoritative artifact.

Route laser-specific material safety (which lasers can cut which metals,
fume extraction) to `laser-art`.

## Output Checklist

For curved or art work, include:

- developed blank dimensions or method (cone math, lofted bend, etc.)
- material, thickness, alloy/temper, and forming process
- seam type and joining plan
- alignment marks, station lines, and registration holes
- trim margin or flat-spot mitigation
- annealing schedule (when, how often, with which torch)
- planishing or finishing plan
- vector layer authority and registration plan (for stacked art)
- test coupon or paper pattern requirement
- which decisions go to `instrument-maker` (acoustics) or `laser-art`
  (vector/material safety)
