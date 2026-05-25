# Drawing Package List

All drawings: ANSI standard, B-size (11x17) unless noted. Title block to include configuration name and revision.

## Part Drawings (Sheet Metal)
| DWG # | Part | Sheets | Views Required | Notes |
|---|---|---|---|---|
| DWG-1001 | 10.1_Body | 2 | Iso, Front, Right, Top, Bottom, Section A-A, FLAT PATTERN (1:1) | Bend table; etch lines for bend locations |
| DWG-1002 | 10.2_Lid | 2 | Iso, Front, Right, Top, Bottom, FLAT PATTERN | Show interlock detail |
| DWG-2001 | 20.1_DollyDeck | 2 | Iso, Top, Bottom, Front, Section, FLAT PATTERN | Caster mount detail callout |
| DWG-2002 | 20.1.1_CasterPlate | 1 | Top, Side, FLAT PATTERN | 4x identical |

## Part Drawings (Other)
| DWG # | Part | Sheets | Views | Notes |
|---|---|---|---|---|
| DWG-2003 | 20.2_DollyHandle | 1 | Iso, Front, Side, weld symbols | Tube weldment cut list |
| DWG-2004 | 20.2.1_HandlePost | 1 | Top, Side | 2x identical |
| DWG-1003 | 10.4_HingePin | 1 | Top, Side | Turned rod; OD/length |

## Assembly Drawings
| DWG # | Assembly | Sheets | Views | Notes |
|---|---|---|---|---|
| DWG-3001 | 10_Box | 1 | Iso, exploded, BOM table | Show fastener callouts |
| DWG-3002 | 20_Dolly | 1 | Iso, exploded, BOM table | Caster part number |
| DWG-4001 | 99_StackDemo | 1 | Iso, 3-box config, 4-box config | Marketing/instruction reference |

## Drawing Standards
- **Title block:** project name, drawing number, revision, scale, material, finish, designer, date, units.
- **Tolerances:**
  - Linear: +/- 0.005 in unless noted
  - Angular: +/- 0.5 deg
  - Hole positions: +/- 0.010 in
  - Bends: +/- 0.5 deg, length +/- 0.020 in
- **Notes block on every flat pattern drawing:**
  - "FLAT PATTERN SHOWN. SCALE 1:1. K-FACTOR 0.44. BEND RADIUS 1T (0.048 in). REMOVE ALL BURRS. BREAK SHARP EDGES R0.010 MAX."
- **Bend tables:** Auto-generated from SW sheet metal feature; include direction, angle, radius, position.
- **DXF export:** Each flat pattern exported to DXF for laser cutter; layer naming follows shop convention (Cut = layer 0, Etch = layer 1).

## Drawing Revision Control
- Initial release: Rev A.
- Engineering change order (ECO) required for any post-release change.
- Drawing files named `DWG-1001_Body_RevA.SLDDRW`.

## Bend Table Format (example)
| Bend ID | Direction | Angle | Radius (in) | Position from datum (in) | Note |
|---|---|---|---|---|---|
| B1 | Up | 90 deg | 0.048 | 0.500 | Body left wall |
| B2 | Up | 90 deg | 0.048 | 19.500 | Body right wall |
| B3 | Up | 90 deg | 0.048 | 0.500 | Body back wall |
| B4 | Up | 90 deg | 0.048 | 9.500 | Body front wall |
