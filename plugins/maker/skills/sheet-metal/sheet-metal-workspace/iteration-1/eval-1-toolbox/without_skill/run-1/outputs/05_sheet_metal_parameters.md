# Sheet Metal Parameters & DFM Rules

## Material Specification
| Property | Value | Notes |
|---|---|---|
| Material | Cold Rolled Steel, ASTM A1008 CS Type B | Powder-coated finish |
| Gauge (Small/Medium) | 18 ga | Nominal 0.048 in / 1.214 mm |
| Gauge (Large) | 16 ga | Nominal 0.060 in / 1.519 mm |
| Tensile strength | ~50 ksi | |
| Yield strength | ~30 ksi | |
| Surface | Mill finish before powder coat | |

## Bend Parameters
| Parameter | Value | Source |
|---|---|---|
| Inner bend radius | 1 x thickness (1T) | Standard air-bend, mild steel |
| K-factor | 0.44 | SolidWorks default for steel, 1T radius |
| Bend deduction | Calculated by SW from K-factor | Use SW formula, not manual |
| Minimum flange length | 4T (~0.19 in for 18 ga) | Avoid press-brake collision |
| Minimum bend-to-bend | 6T | Punch clearance |

## Bend Relief
- **Style:** Rectangular (slot) relief, NOT round (laser doesn't slow on round)
- **Width:** 1.5T
- **Length past tangent line:** 2T
- Apply at every torn corner (where two perpendicular flanges meet).

## Hole / Slot Rules
| Feature | Min Distance | Reason |
|---|---|---|
| Hole edge to bend tangent | 2.5T | Avoid bend-zone distortion |
| Hole edge to part edge | 2T | Tear-out risk |
| Hole diameter | >= 1.0T | Punch tooling minimum |
| Slot width | >= 1.2T | |
| Hole-to-hole pitch | >= 3T (edge-to-edge) | |

## Corner Treatments
- **Outside corners (after forming):** R = 0.125 in (3 mm) min for safety
- **Inside corners (flat pattern):** Add small radius equal to 0.5T to avoid stress concentrators
- **Mitered corners** at lid-to-skirt joints: 45 deg with 0.020 in gap for weld bead

## Joining Methods
| Joint | Method | Spacing |
|---|---|---|
| Body side-to-bottom | Continuous bend (no joint) | n/a |
| Body corner (4 places) | Stitch weld OR rivet | 2 in centers |
| Lid corner | Resistance-spot weld OR Tox clinch | Corners only |
| Hinge to lid | 4x 1/8 in pop rivet per hinge | |
| Latch keeper to body | M4 self-clinching nut + powder coat | |
| Caster to dolly | 1/4-20 x 0.75 button head + nylock | 4 per caster |

## Forming Sequence (per part)
1. Laser cut flat pattern (incl. all holes, reliefs, etch lines for bend locations)
2. Deburr edges (vibratory tumble or hand)
3. Form smallest flanges first, largest last (avoid press-brake collision)
4. Form interlock embosses on rotary or stamping die BEFORE main bends
5. Weld/rivet corner joints
6. Wash, phosphate, powder coat (matte black exterior, optional liner color)

## Flat Pattern Validation Checklist
- [ ] All bends are 90 deg (or 45 for miters)
- [ ] No flange < 4T
- [ ] All hole-to-bend distances >= 2.5T
- [ ] All bend reliefs present at torn corners
- [ ] Flat pattern fits in 48 x 96 in stock (with 0.25 in border for nesting)
- [ ] K-factor consistent across all features
- [ ] No collinear bends (would be a single bend instead)
