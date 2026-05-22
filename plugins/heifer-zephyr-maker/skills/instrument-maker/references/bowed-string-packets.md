# Bowed-String Packet Support — v4.5

> Added for issue #106 after Round 9 TwinGrid lanes Cindy and Dan:
> bass tagelharpa with inlay and yayli tambur segmented-bowl packet seeds.

Use this reference when the instrument is a bowed lyre, tagelharpa,
rebab, kemenche-adjacent form, yayli tambur, or other bowed-string
instrument where bridge crown, bow clearance, string schedule, top/head
load path, and setup validation decide whether the packet is buildable.

Do not average incompatible source choices. If two packets disagree on
scale length, string count, top mode, or bowl construction, preserve
them as named variants until a source frame or prototype objective
selects one.

## Packet posture

Every bowed-string packet must label claims with one of:

| Posture | Use when | Packet behavior |
| --- | --- | --- |
| `sourced` | A selected reference instrument, measurement, drawing, or cited source supports the claim. | Safe to repeat as design context. |
| `prototype_assumption` | The choice is made for shop learning or setup isolation. | Keep it editable and validate it physically. |
| `TBD` | The source frame or measured value is missing. | Do not lock CAD, BOM, or cut files from this value. |

Use `assets/templates/bowed-source-posture.csv` as the claim ledger. A
traditional instrument seed must not present `prototype_assumption` rows
as historical facts.

## Required packet files or sections

For a build packet, include:

- `design.md` with source posture, variant decisions, and setup target.
- `string-schedule.csv` using the template fields below.
- `validation.csv` or `validation-notes.md` with bowability and load
  gates.
- `risks.md` with structural, setup, and source-posture risks.
- `drawing-brief.md` or `cad-dxf-starter-plan.md` listing bridge crown,
  string path, top/head, and fixture drawings.
- `solidworks-skeleton-plan.md` when SolidWorks is part of the packet.
- `decorative-no-carve-zone.csv` when the packet includes inlay,
  engraving, carving, rosettes, or soundboard decoration.

For a seed-only packet, include the same headings even when the values
are `TBD`. A missing field is harder to review than an honest unknown.

## String schedule helper

Use `assets/templates/bowed-string-schedule.csv`.

Minimum fields:

| Field | Purpose |
| --- | --- |
| `string_id` | Stable row id: `S1`, `M1`, `Q4`, etc. |
| `variant_id` | Named configuration such as `V2A_bass` or `P0_geometry_mule`. |
| `role` | `active_bowed`, `drone`, `sympathetic`, `cad_placeholder`. |
| `target_pitch` | Pitch name or `TBD`. |
| `target_hz` | Numeric target when known. |
| `scale_length_mm` | Speaking length. Do not average variants. |
| `material_family` | Plain steel, wound steel, gut, nylon, fluorocarbon, etc. |
| `gauge_or_diameter` | Gauge, diameter, or `TBD`. |
| `estimated_tension_lbf` | Calculated or measured tension; blank until known. |
| `retuning_factor` | Ratio or cents/semitones from a source string. |
| `percent_breaking` | Required for plain synthetic/gut/steel when data exists. |
| `risk_flags` | `too_high_tension`, `too_low_response`, `unknown_gauge`, etc. |
| `status` | `sourced`, `prototype_assumption`, `TBD`, `measured`. |

Use Mersenne-Taylor as the governing string model:

```text
f = (1 / (2L)) * sqrt(T / mu)
cents_error = 1200 * log2(measured_freq / target_freq)
```

For planning from an existing source string:

```text
retuning_factor = target_frequency / source_frequency
tension_ratio_same_string = retuning_factor^2
scale_ratio_tension_same_pitch = (target_scale / source_scale)^2
```

Warnings:

- Do not choose final bridge height from an incomplete string schedule.
- Do not add sympathetic strings to a first article until active bowed
  string setup is stable.
- Wound strings need effective density or source-string data; do not
  pretend plain-string percent-breaking math applies cleanly.

## Bowed lyre / tagelharpa guidance

Use this branch for tagelharpa, jouhikko, bowed lyres, and carved-tray
bowed instruments.

### Geometry gates

- Keep each scale/string choice as a named variant. Example:
  - `V2A_bass`: 720 mm, three strings, C2-G2-D3.
  - `V2B_compact`: 620 mm, four strings, D2-A2-D3-A3.
- Define bridge crown before finalizing string spacing.
- Define nut, bridge, and tailpiece spacing from the bow path, not from
  decoration or body outline.
- Record afterlength from bridge witness point to tailpiece witness
  point.
- Document the tailpiece load path from strings into the body, rim, or
  end block before drilling any anchor holes.
- Document whether the bridge is fixed, floating, or partially captured.

### Bridge and top load path

Required fields:

- `bridge_crown_radius_mm`
- `bridge_height_center_mm`
- `bridge_foot_width_mm`
- `bridge_foot_spacing_mm`
- `bridge_patch_length_mm`
- `bridge_patch_width_mm`
- `soundboard_thickness_mm`
- `top_deflection_limit_mm`
- `tailpiece_anchor_type`
- `tailpiece_load_path`

Validation gates:

1. Measure top flatness before strings.
2. Tune to half tension and record bridge lean plus top deflection.
3. Tune to full tension and record top deflection.
4. Recheck after 24 hours.
5. Record any bridge rocking, buzzing, soundboard compression, or
   afterlength noise.

### CNC tray / carved body notes

For carved-tray bodies, the CAD datum chain is:

```text
centerline -> outer body -> cavity -> glue ledge -> top plane ->
bridge patch -> tailpiece anchor -> nut/bridge/tail string path
```

Do not route decorative pockets or inlay before declaring no-carve
zones for:

- bridge patch and bridge feet,
- tailpiece anchor and fine-tuner clearance,
- soundpost or internal brace locations,
- glue ledges,
- rib/body walls,
- pickup or sensor channels,
- clamp access.

## Long-neck bowl guidance

Use this branch for yayli tambur, rebab-like, kemenche-adjacent, and
long-neck bowl-backed studies.

### Source frame first

Before choosing dimensions, record:

- chosen reference instrument or source set,
- whether the packet is tradition-seeking or a shop prototype,
- body construction mode,
- top/head mode,
- active string count,
- sympathetic or drone staging,
- neck reinforcement strategy: plain wood, laminate, spline, carbon
  fiber, truss rod, or `TBD`,
- player support posture: lap, stand, strap, endpin, or table fixture.

### Bowl construction branch

Do not collapse these branches into one averaged bowl:

| Mode | Use when | Validation coupon |
| --- | --- | --- |
| `faceted_stave` | Oval/lute-like source frame or quick geometry mule. | Three to five rib dry-fit section over a mold. |
| `segmented_ring` | Circular head/membrane resonator or segmented-drum shop path. | One complete scrap ring and rim/head rabbet sample. |
| `bent_rib` | Source frame favors thin ribs over a mold. | One bent rib and mold strip. |
| `carved_bowl` | Source frame or visual goal requires carved shell. | Wall-thickness coupon. |
| `metal_or_bought_resonator` | Cumbus-like source or fast acoustic mule. | Head/rim/bridge load coupon. |

Required variables:

- `bowl_construction_mode`
- `rim_oval_major_mm`
- `rim_oval_minor_mm`
- `head_clear_dia_mm`
- `bowl_depth_mm`
- `rib_count`
- `segments_per_ring`
- `ring_count`
- `neck_block_len_mm`
- `tail_block_len_mm`
- `top_mode`

### Top/head mode

Top mode is source-dependent:

- `wood_soundboard`: easier plate/rib CAD, clearer bridge patch, familiar
  deflection checks.
- `membrane_head`: closer to head/tensioned-skin descriptions, needs
  head tension, bridge foot, and humidity validation.
- `synthetic_head`: repeatable first prototype branch when a head/rim
  system is acceptable.
- `TBD`: source frame unresolved; do not cut final rim/top geometry.

### Active and sympathetic staging

Recommended staging:

1. `2_active_setup_isolation`: two active bowed melody strings to test
   bridge/head/fingerboard response.
2. `4_active_stress_test`: four active strings to test bridge crown,
   string spacing, and neck load.
3. `sympathetic_cad_placeholder`: sympathetic strings as CAD lanes only.
4. `sympathetic_active`: add only after active setup is stable.

## SolidWorks skeleton checklist

Use the canonical master sketch + global equations + design table
workflow. For bowed-string packets, the master skeleton must own:

- `Sketch_Master_Centerline`
- `Plane_Nut`
- `Plane_Bridge`
- `Plane_Tail_Anchor`
- `Plane_Top_Surface` or `Plane_Head_Surface`
- `Plane_Rim`
- `Sketch_String_Paths_3D`
- `Sketch_Bow_Sweep`
- `Sketch_Fingerboard_Taper`
- `Sketch_Bridge_Crown_Gauge`
- `Sketch_Top_or_Head_Load_Patch`
- bowl, tray, or rib station sketches when relevant.

Global variables to include when applicable:

- `scale_length_mm`
- `neck_projection_mm`
- `neck_angle_deg`
- `nut_width_mm`
- `fingerboard_end_width_mm`
- `fingerboard_radius_mm`
- `string_spacing_nut_mm`
- `string_spacing_bridge_mm`
- `bridge_crown_radius_mm`
- `bridge_height_center_mm`
- `bridge_foot_spacing_mm`
- `afterlength_mm`
- `top_mode`
- `soundboard_thickness_mm`
- `head_clear_dia_mm`
- `rim_oval_major_mm`
- `rim_oval_minor_mm`
- `bowl_depth_mm`
- `tailpiece_anchor_offset_mm`
- `no_carve_zone_margin_mm`

Quality gates:

- Every critical dimension is driven by a global or global equation.
- No feature hand-dimensions drive scale length, neck projection, bridge
  height, string spacing, or top/head plane.
- Bow sweep clears adjacent strings and fingerboard in the active
  configuration.
- Bridge crown gauge exports as DXF before the bridge is cut.
- `Extract_Dimensions.swp` output matches the design table before the
  packet claims verified SolidWorks.

## Decorative no-carve zones and inlay coupons

Decorative work is allowed only after exclusion zones are named. Use
`assets/templates/decorative-no-carve-zone.csv`.

Declare no-carve zones for:

- bridge patch and expected bridge-foot travel,
- soundboard patch or brace areas,
- tailpiece/fine-tuner clearance,
- nut and pegbox drilling,
- neck heel and body/rim joint,
- clamp paths and glue ledges,
- pickup, sensor, or wire routes,
- future setup adjustment zones.

For inlay:

- Cut a coupon in the same top/body material before cutting the real
  instrument.
- Measure V-bit width, pocket depth, filler shrinkage, and finish
  visibility.
- Keep inlay out of the first-article bridge patch unless the test
  coupon proves no structural or acoustic penalty.

## Bowed-string validation checklist

Minimum validation rows:

| Stage | Measurement |
| --- | --- |
| before strings | centerline, top/head flatness, neck projection, bridge fit |
| half tension | bridge lean, top/head deflection, neck relief |
| full tension | action, bow clearance, bridge movement, tailpiece load |
| 24-hour drift | tuning drift, deflection drift, buzzes, afterlength noise |
| recording pass | open strings, stopped notes, attack, sustain, noise |

Keep photos or sketches of bridge foot contact, bow sweep, and any
deformation. The first article should teach the next design table row.
