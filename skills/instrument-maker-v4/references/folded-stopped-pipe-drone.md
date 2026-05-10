# Folded Stopped-Pipe Drone Packet Template

Use this template when a prompt asks for a folded didgeridoo-like drone,
laser-laminated labyrinth drone, compact stopped-pipe proof mule, or other
breath-driven folded bore. It is intentionally prototype-grade: the output
should be DXF-first, leak-testable, cleanable, and honest about bend losses.

## Naming and public-language guardrail

Default public language:

- "folded stopped-pipe drone"
- "didgeridoo-inspired compact drone"
- "lip-buzz stopped-pipe proof mule"
- "folded bore acoustic experiment"

Do not call a packet a traditional didgeridoo build unless the user supplies
the cultural/source frame, provenance, and intent. For default maker packets,
say the design borrows the stopped-pipe/lip-buzz acoustic principle while
remaining a modern CNC/laser-laminated experiment.

## Required design fields

| Field | Required guidance |
| --- | --- |
| `target_note` / `target_hz` | Primary drone fundamental |
| `playing_temperature_C` | Use breath-warmed value, usually 30-35 C unless measured |
| `room_temperature_C` | Include comparison, usually 20-22 C |
| `acoustic_law` | `stopped_pipe` or `closed_open` |
| `end_condition` | `one_end_closed_stopped` |
| `bore_shape` | `rectangular_folded_duct`, `round_reference_tube`, or explicit alternate |
| `duct_width_mm` | Width schedule may vary by station |
| `duct_height_mm` | Lamination stack/duct spacer height |
| `equivalent_diameter_mm` | `2 * sqrt((width_mm * height_mm) / pi)` |
| `centerline_length_mm` | Sum along folded centerline before trim |
| `tuning_tail_mm` | Removable/trim allowance, preferably 100-200 mm for bass drones |
| `bend_count` | Count direction changes that can add loss/turbulence |
| `min_bend_radius_mm` | Avoid sharp inside corners; document if laser-laminated square turns are used |
| `straight_reference_length_mm` | Required control tube |

## First-order acoustic model

Use:

```text
c = 331.3 * sqrt(1 + T_C / 273.15)
L_eff = c / (4 * f)
area_rect = width * height
d_eq = 2 * sqrt(area_rect / pi)
L_geom_first_pass = L_eff - 0.82 * d_eq
```

Notes:

- `d_eq` is an area-equivalent diameter for end-correction and sanity checks.
- It does not make a rectangular labyrinth behave like a smooth round tube.
- Bend losses, wall friction, seam leakage, and mouthpiece geometry can shift
  speaking behavior; keep a removable tuning tail and validate against the
  straight reference tube.
- Compute at warm playing temperature and include a cooler-room comparison.

## Centerline station CSV

The folded-bore DXF helper expects at least:

```csv
station_id,x_mm,y_mm,width_mm
S0,0,0,52
S1,360,0,52
S2,360,160,54
S3,20,160,54
S4,20,320,56
S5,200,320,56
```

Optional columns:

- `height_mm`
- `bend_radius_mm`
- `role` (`mouthpiece`, `fold`, `straight`, `tuning_tail`, `closed_end`)
- `note`

The centerline is the acoustic path datum. The generated DXF is a starter
layout, not CAM-ready geometry.

## DXF output contract

Required starter layers:

- `DUCT_CENTERLINE`
- `DUCT_LEFT_WALL`
- `DUCT_RIGHT_WALL`
- `FOLD_BEND_ZONE`
- `TUNING_TAIL`
- `LEAK_TEST_NOTES`
- `BREATH_SAFETY_NOTES`
- `NOTES_NO_CUT`

The DXF should include:

- centerline segments in millimeters
- wall offsets from the width schedule
- bend markers at internal stations
- tuning-tail witness marks
- equivalent-diameter and straight-reference notes
- leak-test and breath-contact safety notes on no-cut layers

## Build packet checklist

- `design.md`: acoustic assumptions, public-language note, bend-loss limits
- `data/centerline-stations.csv`: folded path and width schedule
- `drawings/folded-drone-layout.dxf`: generated starter DXF
- `cnc/` or `laser/` setup notes: lamination stack, kerf, registration pins
- `bom.csv`: breath-safe mouthpiece, cured finish, adhesive, gasket/sealant
- `validation.csv`: straight reference tube and folded body tests
- `risks.md`: leaks, moisture, cleanability, bend turbulence, tuning drift

## Validation minimum

The template requires validation against a straight reference tube:

1. Build or source a straight stopped tube with the same equivalent diameter.
2. Tune/measure it at room temperature.
3. Warm it with breath or warm air and measure again.
4. Compare against the folded drone before final tail trim.
5. Trim or slide the removable tail only after leak tests pass.

Breath-contact gates:

- finish fully cured before playing
- mouthpiece removable and washable
- duct drains moisture when held in normal playing/storage orientations
- no uncured epoxy, solvent finish, or raw porous adhesive in the breath path
- internal seams survive a low-pressure leak test after finish
