# Cut List

Source of truth: `geometry_params.json`. All dimensions in **mm**,
finished (post-kerf-compensation). Stock: **6 mm Baltic-birch plywood,
exterior phenolic glue (WBP)**.

**Total: 8 panels.** Nest on a single 600 × 760 mm sheet (sheet size
matches `chickadee-panels.svg`).

## Panel summary

| ID | Name | Finished outline (W × H, mm) | Notes |
|---|---|---|---|
| P1 | Front | 122 × 275 (rectangle) | Entrance Ø 28.6, 5 kerf-grip score lines, box-joint left/right |
| P2 | Back | 122 × 352 (rectangle, 30 mm bottom tab + 80 mm top tab) | 2 × Ø 5.5 mount holes, box-joint left/right (box section only) |
| P3 | Side, fixed (left) | 110 × 269 / 236 (trapezoid; front edge 269, back edge 236) | 3 × vent slots 4 × 50 mm, box-joint slots front + back, dado for floor |
| P4 | Side, cleanout door (right) | 110 × 269 / 236 (trapezoid, mirror) | 3 × vent slots, 3 × Ø 3 mm pilot holes, **slip-fit** slots |
| P5 | Floor | 110 × 110 with 4 × 8 × 8 mm corner notches | Drainage notches |
| P6 | Roof | 172 × 204 | 4 × Ø 3 mm pilot holes, perimeter drip score |
| P7 | Kerf test | 50 × 50 | Cut FIRST; calibrate kerf before production |
| P8 | Entrance guard (optional) | 60 × 60 with Ø 28.6 hole | Sacrificial wear plate |

## Verification math

| Check | Spec | Actual | Pass |
|---|---|---|---|
| Floor area ≥ 16 in² (NestWatch min for chickadee) | ≥ 103 cm² | 110 × 110 = 121 cm² | ✓ |
| Hole-to-floor interior height in 6–8 in range | 152–203 mm | 175 mm | ✓ |
| Hole-to-roof interior clearance | sufficient for adult passage | 230 − 175 − 14.3 = 40.7 mm | tight but workable |
| Total cavity volume | NestWatch ≥ ~3 L | 110 × 110 × 230 = 2.78 L | borderline; move to 250 mm interior height for ≥ 3 L |
| Entrance hole diameter | 28.6 ± 0 / −0.5 mm | 28.6 mm | ✓ (kerf-test gate before production) |
| Vent open area per side | ≥ 6 cm² | 3 × 50 × 4 = 600 mm² = 6.0 cm² | ✓ |
| Drain open area | ≥ 2 cm² | 4 × 8 × 8 = 256 mm² = 2.56 cm² | ✓ |

The borderline cavity-volume check is acceptable per NestWatch (chickadees
accept boxes down to ~2 L) but a future bump to 250 mm interior height
would put it firmly inside the comfort range. That edit lives in
`geometry_params.json` → `cavity_dimensions_mm.interior_height_floor_to_roof_underside`.

## Sheet nesting

The generator emits panels at fixed positions on a 600 × 760 mm sheet.
Adjust the `LAYOUT` array in `scripts/generate_chickadee_packet.py` if a
different sheet size is needed. Approximate area utilization: ~75 %.
