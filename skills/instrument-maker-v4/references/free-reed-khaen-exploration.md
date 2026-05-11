# Free-Reed / Khaen Exploration Template

Use this reference when a prompt asks for a khaen, khen, sheng, sho, bawu,
hulusi, harmonica, melodica, accordion, chalumeau-style reed pipe, or other
mouth-organ / reed-coupled pipe experiment. This is an exploration template,
not a finished instrument packet.

## First Build Rule

Start with a **P0 reed coupon**, not full CAD.

Do not commit to a full pipe set, ceramic body, or decorative windchest until
one reed has been measured in a controlled coupon and one single-pipe control
has been validated. Free-reed pitch, onset pressure, pull-down, and blow/draw
behavior are too sensitive to reed stock, tongue gap, gasket leakage, windchest
volume, and socket geometry to treat supplier dimensions as final acoustic
data.

## Branch Decision

Every packet must pick one branch before layout:

| Branch | Use When | First Gate |
| --- | --- | --- |
| `control-build` | You are proving reed behavior, pipe law, socket seal, or windchest geometry. | P0 reed coupon, then one measured pipe. |
| `family-true` | You already have measured reed/coupon data and are scaling a known architecture into a family. | `family-spec.csv` validates with `scripts/validate_acoustic_law.py`. |

If the branch is unclear, choose `control-build`.

### `control-build` packet minimum

- `design.md` with branch, target note, candidate reed source, and explicit
  unknowns.
- `p0-reed-coupon-log.csv` copied from `examples/khaen/`.
- `family-spec.csv` row with `acoustic_law=unknown_requires_measurement` until
  the reed and pipe coupling are measured.
- One single-pipe control layout before any mouth-organ windchest.
- Leak, onset-pressure, blow/draw, and pull-down validation rows.

### `family-true` packet minimum

- `family-spec.csv` with `acoustic_law`, `end_condition`, and
  `dimension_provenance` filled for every pipe.
- `scripts/validate_acoustic_law.py family-spec.csv` passes.
- Reed source/provenance and coupon data named in the packet.
- Pipe socket pitch map and windchest section drawing.
- Notes explaining whether this is traditional side-branch khaen/sheng logic
  or a compact closed-open/stopped-pipe control variant.

## P0 Reed Coupon Worksheet

Copy `examples/khaen/p0-reed-coupon-log.csv` into the packet and fill one row
per reed. Required fields:

| Field | Meaning |
| --- | --- |
| `coupon_id` | Stable ID for this reed coupon. |
| `reed_source` | Donor instrument, bought reed, handmade blank, or supplier. |
| `source_status` | One of the sourcing status values below. |
| `source_provenance` | Where the reed data came from: measured, supplier note, photo, prior build, etc. |
| `reed_material` | Brass, phosphor bronze, stainless, cane, polymer, unknown. |
| `reed_alone_pitch_hz` | Reed pitch outside the pipe, measured with the coupon. |
| `reed_alone_note` | Nearest note name for the reed-alone pitch. |
| `target_pipe_note` | Intended coupled note. |
| `pull_down_cents` | `1200 * log2(coupled_freq / reed_alone_freq)`. |
| `onset_pressure_pa` | Measured start pressure; leave blank if not measured yet. |
| `blow_behavior` | `speaks`, `stalls`, `squeals`, `silent`, `unstable`, etc. |
| `draw_behavior` | Same vocabulary for draw direction. |
| `gap_setting_mm` | Reed tongue gap after setup. |
| `window_size_mm` | Reed window width x length. |
| `gasket_leak_status` | `none_seen`, `minor`, `major`, `unknown`. |
| `measurement_environment` | Temperature, humidity, and rig notes. |
| `next_action` | What to change before the next coupon. |

Treat `reed_alone_pitch_hz`, `pull_down_cents`, `onset_pressure_pa`, and
blow/draw behavior as required before moving from `control-build` to
`family-true`.

## Acoustic-Law Validator Path

Before claiming a pipe length:

1. Read `references/acoustic-models.md` section
   **"Reed boundary-condition decision tree"**.
2. Fill `acoustic_law`, `end_condition`, and `dimension_provenance` in
   `family-spec.csv`.
3. Run:

```bash
python3 skills/instrument-maker-v4/scripts/validate_acoustic_law.py \
  path/to/family-spec.csv
```

Use these values deliberately:

| Acoustic law | Use For | Validation Expectation |
| --- | --- | --- |
| `side_branch_reed` | Traditional khaen/sheng-style pipe with reed in side wall and both pipe ends open. | Requires `end_condition=both_ends_open`; length checks as half-wave. |
| `closed_open` | Compact control build with reed acting as the closed end and one open pipe end. | Requires one-end-closed condition; length checks as quarter-wave. |
| `stopped_pipe` | Chalumeau-style beating-reed or reed-pipe layout where the reed/stopped end defines the closed boundary. | Requires one-end-closed condition; length checks as quarter-wave. |
| `unknown_requires_measurement` | Donor reed, uncertain coupling, or no measured coupon yet. | Emits warning; do not produce final CAD claims. |

Unsupported pipe-law names such as `quarter_wave_closed_open`,
`khaen_halfwave_guess`, or prose-only model claims are not valid. The validator
catches unsupported values in `family-spec.csv`; this checklist catches prose
claims before they become CAD.

## Mouth-Organ DXF Checklist

Copy `examples/khaen/mouth-organ-dxf-checklist.csv` into the packet or convert
it into a drawing checklist. A first mouth-organ DXF must identify:

- Reed window geometry: reed tongue outline, frame/window, rivet or clamp line,
  clearance around the vibrating tongue, and tongue travel direction.
- Socket pitch map: pipe ID, target note, reed ID, acoustic law, pipe length,
  socket center, and row/column.
- Gasket layer: gasket outline, screw/dowel holes, leak land, compression stop,
  and service direction.
- Windchest section: air inlet, chamber volume assumption, reed plate seat,
  pressure path, and removable cover.
- Side-branch/stopped-end note: a no-cut note naming whether each pipe is
  `side_branch_reed`, `closed_open`, `stopped_pipe`, or
  `unknown_requires_measurement`.

The DXF may be a coupon or one-pipe test article. It should not imply a
complete khaen/sheng family until the P0 coupon and single-pipe control pass.

## Visual Authority Checkpoint

If the packet includes concept images, visual BOM plates, build-log renders, or
image-gen-2 prompts, add a lightweight visual-output register with each
artifact's ID, role, authority, and source. The governing reed window, pipe
length, socket map, stopped-end note, and side-branch layout must trace back to
DXF, CAD, a design table, or a measured template. Generated images are
`concept_only` or `reference_only`; they must not claim cut-ready geometry,
dimensioned reed windows, hole locations, pipe lengths, or toolpaths.

## Ceramic Shell Versus Removable Acoustic Core

Ceramic shells are attractive for final objects, but early free-reed work
should keep the acoustic core removable.

| Option | Use When | Guidance |
| --- | --- | --- |
| Removable acoustic core in non-ceramic test shell | P0/P1 exploration. | Preferred. Lets reed plate, gasket, and pipe socket change without remaking the body. |
| Ceramic shell with removable core | Aesthetic prototype after coupon data exists. | Design a dry mechanical seat, gasket land, drain/cleaning path, and service access. |
| Monolithic ceramic acoustic path | Late family-true build only. | Use only after shrinkage, glaze thickness, and reed service access are validated. |

For ceramics, keep fired shrinkage out of the acoustic-law math until measured.
Mark shell dimensions as `empirically_seeded` or `measurement_required` unless
post-fire dimensions have been measured.

## Sourcing `source_status`

Use these values in free-reed sourcing tables so live stock is not mistaken for
stable design data:

| `source_status` | Meaning |
| --- | --- |
| `measured_in_shop` | Physically measured by the builder. Stable for this packet. |
| `donor_part_on_hand` | Salvaged or bought part is in hand but not fully characterized. |
| `supplier_spec_unverified` | Supplier dimensions or pitch claim; not yet measured. |
| `live_stock_transient` | Availability/price/current listing may change; verify before purchasing. |
| `historical_reference` | Museum, article, photo, or old catalog data; useful context, not procurement. |
| `needs_supplier_quote` | Requires RFQ or current vendor confirmation. |
| `substitution_candidate` | Possible replacement; must be coupon-tested before family use. |

If current purchasing is requested, verify price, availability, lead time, and
shipping before recommending a supplier. Otherwise record search terms and
status, not confident purchase instructions.

## Promotion Gates

Move from `control-build` to `family-true` only when:

- At least one reed coupon has measured reed-alone pitch, onset behavior, and
  blow/draw behavior.
- One single-pipe control validates the declared `acoustic_law`.
- Leaks are controlled well enough that pitch and onset measurements are
  meaningful.
- The pipe-law validator passes or intentionally warns with
  `unknown_requires_measurement`.
- The packet documents source provenance and `source_status` for every reed or
  donor part.

Do not use a full mouth-organ CAD model as the first validation artifact.
