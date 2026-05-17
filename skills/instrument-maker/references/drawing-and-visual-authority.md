# Drawing and Visual Authority

Use this reference when an instrument packet includes DXF/CAD drawings,
derived previews, visual BOM plates, concept art, or image-gen-2 prompts.
It exists to keep fabrication authority traceable: generated images can help
the maker understand a design, but they must not replace the drawing, CAD, or
design table that controls dimensions.

## Authority Rule

DXF, CAD, design tables, measured templates, and explicitly reviewed drawings
are the only fabrication authority.

Generated images, including image-gen-2 outputs, are never fabrication
authority. They may support concept direction, visual storytelling,
ergonomics, finish studies, visual BOM communication, or build-log context.
They must not be treated as cut-ready layouts, dimensional evidence, or a
source of hole locations, wall thicknesses, socket centers, reed windows,
string scale lengths, bridge placement, or CNC/laser toolpaths.

## Visual Output Register

When a packet includes more than one visual artifact, add a
`visual-output-register.csv` or equivalent JSON record. Use these fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `artifact_id` | yes | Stable ID such as `DXF-001`, `IMG-002`, or `SVG-003`. |
| `path` | yes | Packet-relative file path or prompt file path. |
| `artifact_kind` | yes | One of the kinds below. |
| `role` | yes | What the artifact is for. |
| `authority` | yes | `fabrication`, `derived_preview`, `concept_only`, or `reference_only`. |
| `derived_from` | conditional | Required for `derived_preview` artifacts. |
| `dimension_claim` | yes | `none`, `derived_from_authority`, or `image_inferred`. |
| `notes` | no | Short provenance or review note. |

### `artifact_kind` vocabulary

- `dxf`
- `cad`
- `drawing_pdf`
- `svg_preview`
- `render_preview`
- `design_table`
- `measurement_template`
- `image_gen_2_prompt`
- `image_gen_2_output`
- `photo_reference`

### `role` vocabulary

Fabrication roles:

- `fabrication_geometry`
- `cut_layout`
- `cnc_reference`
- `laser_reference`
- `dimensioned_drawing`
- `design_table`
- `measurement_template`

Non-fabrication visual roles:

- `derived_preview`
- `concept`
- `story`
- `visual_bom`
- `ergonomics`
- `finish_study`
- `build_log`
- `photo_reference`

### `authority` values

- `fabrication` - controls dimensions, machining, cutting, or inspection.
- `derived_preview` - preview generated from a fabrication-authority source.
- `concept_only` - helpful imagery with no dimensional authority.
- `reference_only` - photo or contextual reference that does not control the build.

### `dimension_claim` values

- `none` - no dimensional claim.
- `derived_from_authority` - dimensions shown only because they come from
  the named authoritative drawing/CAD/design table.
- `image_inferred` - invalid for image-gen-2; flags a generated image being
  used as dimensional evidence.

## Required Checks

Before sending an instrument packet to a shop, run:

```bash
python3 skills/instrument-maker/scripts/validate_visual_authority.py \
  path/to/visual-output-register.csv
```

The validator fails when:

- no fabrication-authority DXF/CAD/design-table/measurement-template record is
  present for a visual packet;
- an image-gen-2 prompt or output is marked as fabrication authority;
- an image-gen-2 prompt or output uses a fabrication role such as
  `cut_layout`, `dimensioned_drawing`, or `cnc_reference`;
- an image-gen-2 prompt or output claims `dimension_claim=image_inferred`;
- a derived preview does not name its source in `derived_from`.

## Reed and Free-Reed Packets

For khaen, sheng, hulusi, bawu, chalumeau-style reed pipes, or other
reed-coupled packets, visual authority also depends on acoustic-law authority.
Run `scripts/validate_acoustic_law.py` on the packet's `family-spec.csv`
before treating a reed window, pipe length, socket map, stopped-end note, or
side-branch layout as build geometry.

Generated images must not promote a visually plausible reed layout into a
fabrication claim. A concept image may show the mood, finish, ergonomics, or
story of a sheng/hulusi/chalumeau-inspired build, but the build dimensions
must come from the acoustic-law record, measured reed/coupon data, and the
governing DXF/CAD/design table.

## Image-Gen-2 Prompt Guard

Any image-gen-2 prompt emitted by the skill should include these constraints in
plain language:

- "Concept image only; not fabrication authority."
- "Do not include cut-ready dimensions, hole locations, or toolpaths."
- "Fabrication dimensions are controlled by `<DXF/CAD/design-table id>`."

The prompt may describe silhouette, context, finish, lighting, scale cues, and
story intent. It must not ask the model to infer missing instrument dimensions
or generate a usable DXF-like layout.

## Packet Closeout

In the packet README or design notes, name the artifact that controls the build
before showing concept images. A concise pattern is:

```text
Fabrication authority: drawings/body-layout.dxf and design-table.csv.
Generated images in images/concepts/ are concept-only and do not control
dimensions, tone-hole placement, reed windows, or toolpaths.
```
