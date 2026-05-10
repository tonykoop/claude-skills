# Design Table

Values in this table come from `design_params.json`. Regenerate
`geometry_params.json` and `panels.svg` after changing any parameter.

## Species Constraints

| Parameter | Value | Reason |
| --- | ---: | --- |
| Entrance diameter | 1.125 in | Hard upper limit for chickadees; larger holes admit larger competitors. |
| Interior floor | 5.5 x 5.5 in | Small cavity floor suited to chickadee clutch size. |
| Interior depth at front | 8.0 in | Gives nest cup and fledgling headroom. |
| Entrance center above floor | 6.0 in | Keeps nestlings away from the entrance while still reachable at fledge. |
| Perch | none | Perches help predators and competitors more than chickadees. |
| Interior finish | none | Avoids exposure and preserves climbable texture. |

## Material Profiles

| Profile | Stock | Wall Strategy | Use When |
| --- | --- | --- | --- |
| `cedar_laminate` | untreated solid cedar, 1/4 in plies | three plies per finished panel | wildlife-first default when the shop can safely laser cedar |
| `exterior_plywood` | known laser-safe exterior plywood, 1/4 in plies | three plies per finished panel | fallback when adhesive is verified safe and shorter lifespan is acceptable |

## Derived Geometry

| Feature | Value |
| --- | ---: |
| Finished wall thickness | 0.75 in |
| Front panel | 7.0 x 9.5 in |
| Back panel | 7.0 x 11.5 in |
| Side panel | 5.5 in deep, 9.5 in front, 10.25 in rear |
| Floor | 5.5 x 5.5 in |
| Roof | 10.0 x 10.25 in |
| Vent slots | 3 per side, 1.8 x 0.18 in |
| Vent free area | 0.972 sq in per side |
| Floor drainage | four 0.375 x 0.375 in corner notches |

## Generator Contract

The generator must keep these values synchronized:

- `design_params.json` species constraints and panel dimensions.
- `geometry_params.json` material, derived vent/drainage area, and validation checks.
- `panels.svg` panel outlines, entrance, vent slots, drainage notches, and score lines.
