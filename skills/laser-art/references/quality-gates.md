# Quality Gates

Run the relevant checks before calling work fabrication-ready.

## Vector Hygiene

- Units are explicit.
- Artboard matches physical size or declared scale.
- Strokes intended for cutting are expanded or otherwise CAM-safe.
- Duplicate paths, hidden layers, clipping masks, and tiny artifacts are removed.
- Closed shapes are closed; open engrave paths are intentionally open.
- Cut order is internal detail before outer boundary.

## Registration

- Every layer shares the same origin.
- Registration holes/marks are present on every stencil/cut layer.
- The jig/substrate has matching pins or marks.
- Pin diameter includes practical clearance.
- The registration geometry is outside visible art or designed into the piece.

## Bridge and Island Check

- Floating islands in stencil layers are bridged.
- Bridges are wide enough for the material and handling.
- Delicate paper/wood lace is supported by frame geometry or neighboring forms.
- Small dots or islands are either intentionally retained, converted to
  engraving, or removed.

## Material and Safety

- Material is laser-safe or routed to a non-laser process.
- Unknown plastic, PVC, vinyl, coated mystery materials, and unsafe fumes are
  flagged before cutting.
- A test coupon is included when settings, finish, paint, or material are new.
- Adhesive, paint, clear coat, and ventilation needs are noted.

## Spray Stencil

- Layer order is clear.
- Paint colors are assigned.
- Overspray, underspray, and dry-time control are addressed.
- Repositionable adhesive, magnets, weights, or fixture strategy is specified.
- The output includes a one-layer proof before full multi-layer application.

## Relief and Inlay

- Stack order is clear.
- Glue-up order and alignment method are clear.
- Sanding/finish access is considered.
- Inlay pockets and inserts are separated.
- Cutter/kerf assumptions are noted rather than hidden.

## Rotary

- Circumference and usable height are recorded.
- Seam location is marked.
- Text and critical motifs avoid the seam unless intentional.
- Taper or handle obstruction is addressed.
- Focus and rotation-axis checks are included.

## CAD Safe Zone

- Art stays inside `Art_Safe_Zone` or equivalent.
- Screw holes, bracing, ports, tongues, joints, and fixtures are excluded.
- Instrument acoustics are not assumed; route acoustic impact to an instrument
  specialist when needed.
- CAD sketch names and export names match the layer manifest.
