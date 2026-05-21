# Parametric Design Tables

Use this file when the project needs a family of sizes (toolboxes, horn
segments, shelves, robot chassis variants) driven from one master. It is the
dedicated companion to `solidworks-sheetmetal.md` for the design-table
discipline.

## When To Use A Design Table

Use a design table when:

- The user asked for "a family of sizes" or "the next size up."
- You will fabricate the same shape in more than one material.
- Multiple downstream parts (lid, tub, dolly, trays) must agree on a few
  driving dimensions.
- The MLP would otherwise need a separate copy per size.

Avoid a design table when:

- There is exactly one part with no plans to scale it.
- The dimensions of interest are continuous, not discrete (use equations
  alone).

## Family Patterns

Two patterns cover most cases.

### Pattern A: Linear Family From One Master Envelope

The seed configuration sets the envelope; other configurations scale length,
width, and height while keeping material thickness, inside radius, K-factor,
and hardware pitch constant.

```
Configuration,Box_Length,Box_Width,Box_Height,Material_T,Inside_R,K,Hardware_Pitch
BOX-S,12,6,5,0.060,0.060,0.44,1.5
BOX-M,16,8,6,0.060,0.060,0.44,2.0
BOX-L,20,10,8,0.060,0.060,0.44,2.0
BOX-XL,24,12,10,0.060,0.060,0.44,2.0
```

Watch for:

- Stiffness suffers at large sizes if material thickness stays constant. At
  some size, you need a return flange, a hem, an internal rib, or thicker
  stock. Add a "stiffener strategy" column or split the family.
- Hardware pitch may need to vary if the smallest size is too small for the
  default pitch.
- Stack interface dimensions (rim height, foot inset) might need to scale
  too; check whether the seed value still locates the upper box correctly.

### Pattern B: Material Variants Of One Size

The seed configuration sets the dimensions; other configurations vary
material, thickness, inside radius, K-factor, and finish.

```
Configuration,Material,Material_T,Inside_R,K,Finish
BOX-MS-SEED,Mild Steel 16ga,0.060,0.060,0.44,Powder
BOX-AL-ALT,Aluminum 5052 14ga,0.063,0.063,0.46,Brush
BOX-SS-ALT,Stainless 18ga,0.048,0.048,0.38,Brush
```

Watch for:

- Bend allowance changes per material; the same flat pattern won't unfold
  the same way. Generate a per-configuration flat pattern review.
- Joining method may need to change (rivets vs welds vs screws) per material.
- Finish appearance: stainless brush direction matters; aluminum anodizes
  differently than mild steel powder-coats.

## Configuration Naming

Encode the differentiator in the configuration name. Three patterns:

```
BOX-{L}x{W}x{H}-{TAG}         # size family
BOX-{SIZE}-{MATERIAL}-{REV}   # material family
BOX-{L}x{W}x{H}-{MATERIAL}    # combined
```

Avoid `CONFIG-1`, `CONFIG-2`. They tell you nothing six months later.

## CSV Conventions

When writing a design table CSV that will be consumed by SolidWorks:

- Column names match global variable names exactly. SolidWorks variable names
  cannot contain spaces; use underscores.
- Use SI or imperial consistently within a project. Mark units in column
  headers if a column could be misread (e.g., `Box_Length_in`).
- One configuration per row.
- The seed row goes first.
- Avoid blank cells; if a parameter is not used for a configuration, set it
  to its default rather than leaving it blank.

When writing a design table CSV that will be consumed by humans
(`parameters.csv` shape), include source, confidence, and notes columns:

```
name,value,units,scope,source,confidence,notes
Box_Length,20.000,in,case,user seed,high,Outside width across front face
Material_T_Box,0.060,in,case,16 ga planning,medium,Measure actual sheet before flat pattern release
```

`source` values: `user seed`, `user measured`, `assumption`, `derived`,
`skill reference`, `script estimate`, `vendor datasheet`, `shop tooling`,
`planning rule`.

`confidence` values: `high` (measured or specified), `medium` (well-grounded
planning assumption), `low` (rough placeholder).

## Cross-Part Consistency

When a family includes multiple parts (case + dolly + tray), share a master
parameters file rather than duplicating the variable list. Either:

1. One `parameters.csv` covering every part, with a `scope` column
   identifying which part each variable belongs to.
2. Multiple part-scoped files (`parameters_case.csv`, `parameters_dolly.csv`)
   plus a `parameters_shared.csv` for variables both parts depend on.

Pattern 1 is simpler for small projects; pattern 2 scales better when the
family grows past ~50 variables.

## Validation

Run the design table through these checks before declaring it usable:

- Every column has a sensible name (no anonymous indices).
- Every configuration name encodes the differentiator.
- No two rows have the same name.
- For each configuration, every dimension is positive and unitful.
- Derived columns match their equation across all rows (e.g.,
  `Dolly_Deck_Length` should equal `Box_Length + 2`).
- The seed row produces a SolidWorks part that flat-patterns without errors;
  the others should at least pass `rebuild` without flags.

The `scripts/validate_packet.py` script can help check the column shape and
CSV hygiene; it doesn't replace opening the part in SolidWorks.
