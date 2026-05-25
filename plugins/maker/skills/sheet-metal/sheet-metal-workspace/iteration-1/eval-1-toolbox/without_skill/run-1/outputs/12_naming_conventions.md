# Naming Conventions

## File Names
- **Parts:** `<level>.<seq>_<Name>.sldprt` -> `10.1_Body.sldprt`, `20.1_DollyDeck.sldprt`
- **Assemblies:** `<level>_<Name>.sldasm` -> `10_Box.sldasm`, `20_Dolly.sldasm`, `99_StackDemo.sldasm`
- **Drawings:** `DWG-<4digit>_<Name>_<Rev>.slddrw` -> `DWG-1001_Body_RevA.slddrw`
- **Flat patterns (DXF):** `FLAT_<part_number>_Rev<X>.dxf` -> `FLAT_10.1_Body_RevA.dxf`

## Number Blocks
- 00xx: Master layout / library
- 10xx: Box parts and assembly
- 20xx: Dolly parts and assembly
- 30xx: Box-related drawings (assy)
- 40xx: Multi-assembly drawings (stack demo)
- 90xx: Fixtures / shop aids

## Configurations
- Box configurations: `Small-Half`, `Small-Full`, `Medium-Half`, `Medium-Full` (default), `Medium-Deep`, `Large-Half`, `Large-Full`, `Large-Deep`
- Dolly configurations: `Default`, `Heavy` (for Large boxes)
- Stack demo configurations: `3_boxes`, `4_boxes`

## Feature Names (in FeatureManager)
- Sketches: `Sk_<Purpose>` -> `Sk_BoxFootprint`, `Sk_InterlockGrid`
- Sheet metal features: `SM_<Purpose>` -> `SM_BaseFlange`, `SM_LeftEdgeFlange`
- Cuts: `Cut_<Purpose>` -> `Cut_HandleSlot`, `Cut_LatchHoles`
- Patterns: `Ptn_<Purpose>` -> `Ptn_InterlockCorners`

## Global Variable Names (already in 02_global_variables.txt)
- CamelCase, no spaces, no underscores in the variable itself.
- Prefix groups: `Box*`, `Lid*`, `Dolly*`, `Caster*`, `Interlock*`, `Sheet*`, `Bend*`.

## Mate Names
- Always rename mates: `Mate_<part1>_to_<part2>_<type>` -> `Mate_Body_to_Layout_Coincident`.
- Distance / angle mates include value: `Mate_Lid_to_Body_Distance_0.500`.

## Revision Letters
- Drawing rev: A, B, C, D, ...
- Skip I, O, Q (per ANSI Y14.35M).
- Major change (form/fit/function) = rev letter bump.
- Minor change (note/dimension fix not affecting fab) = same letter with revision note in title block.
