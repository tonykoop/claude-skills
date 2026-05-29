# Tools — example-space

Long-form descriptions of each tool listed in `profile.yaml::tools`.
Anchor each section to the YAML `id` so the schema can deep-link.

## Conventions

- One H2 per tool. The H2's anchor matches the YAML `id`.
- Include any quirks ("the X-axis backlash on this CNC is ~0.005",
  "the laser fume extractor is loud — bring earplugs").
- Prefer short, factual descriptions. Members want "what's the bed
  size and is the vacuum table working" more than "this CNC was
  generously donated by..."

## Example sections (delete or replace)

### `#example-cnc-1`

Bed size: 48" × 96". Max Z: 8". Spindle: 5 HP, 24000 RPM, ER32.
Vacuum table works. Shop owns ¼" compression and ⅛" ball-end bits;
bring your own for anything else.

Common failure modes:
- Compression bits dive into the spoilboard if Z-zero is set wrong.
  Always re-zero between jobs.
- The vacuum pump cycles every ~60 seconds. Plan cuts under that
  window or use clamps for backup.

### `#example-laser-1`

Bed size: 32" × 18". 80W CO₂. Air assist. Fume extractor exhausts
to roof.

Permitted materials: see `materials-policy.md`. Acrylic, plywood up
to ¼", MDF, leather, paper. **Never** PVC, vinyl, ABS,
polycarbonate, or anything fluoride-bearing.
