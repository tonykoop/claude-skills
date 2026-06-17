# Hulusi / Bawu Stopped-Pipe Free-Reed Validation

Use this reference when a prompt asks for a hulusi, bawu, or similar
stopped-pipe free-reed instrument: a free reed mounted at the pipe head, a
pipe or tube that pulls the reed toward a played pitch, and often a gourd or
small wind chamber that acts mainly as a pressure reservoir.

This is a readiness-gated validation note, not a build-ready packet template.
Do not infer reed windows, socket locations, pipe lengths, or DXF/CAD authority
from concept images, supplier listings, or an unmeasured workbook.

## Routing Decision

Hulusi and bawu work usually belongs in `control-build` until measured data
exists.

| Situation | Route | Boundary-condition claim |
| --- | --- | --- |
| Existing repo has packet artifacts but no reed coupon or single-pipe measurements | Prototype validation-loop upgrade | `unknown_requires_measurement` |
| README-only or first public repo | Repo-first bare-bones packet | `unknown_requires_measurement` |
| One measured reed coupon and one measured pipe control exist | Continue validation loop | declare the measured law only for the tested row |
| Multiple measured rows support family scaling | `family-true` packet | declared law per row with evidence |

Do not route hulusi/bawu as `side_branch_reed` unless the physical layout truly
uses a traditional side-wall reed with both pipe ends open. Most hulusi/bawu
control builds are closer to a stopped-pipe/free-reed test article, but the
safe first declaration is still `unknown_requires_measurement` until HUL-P0
and HUL-P1 data exists.

## HUL-P0 Before HUL-P1

HUL-P0 is a reed coupon. It proves that the reed stock, tongue gap, window,
and mounting method can speak in a controlled fixture before any pipe family
claims are made.

Required HUL-P0 fields:

- `coupon_id`
- `reed_source`
- `source_status`
- `source_provenance`
- `reed_material`
- `reed_alone_pitch_hz`
- `reed_alone_note`
- `target_pipe_note`
- `pull_down_cents`
- `onset_pressure_pa`
- `blow_behavior`
- `draw_behavior`
- `gap_setting_mm`
- `window_size_mm`
- `gasket_leak_status`
- `measurement_environment`
- `next_action`

If these values are not measured, keep the packet at
`L1_packet -> measurement_required` and do not promote it to
`L2_bench_validated`.

## HUL-P1 Single-Pipe Control

HUL-P1 is one measured pipe control, not a full hulusi/bawu family. It tests
whether one measured reed and one measured pipe behave together.

Required HUL-P1 fields:

- pipe ID, target note, bore, and measured pipe length
- reed coupon ID tied back to HUL-P0
- declared `acoustic_law`, `end_condition`, and `dimension_provenance`
- all-closed measured frequency
- selected finger-hole measured frequencies if the control pipe has holes
- cents error before and after wax, gap, or reed adjustment
- leak status at reed frame, pipe socket, and wind supply interface
- pressure range or onset-pressure measurement when the rig supports it
- exact next packet action if the result is outside tolerance

Only after HUL-P1 gives meaningful measured pitch, pull-down, onset, and leak
evidence should the row move from `unknown_requires_measurement` to a specific
stopped-pipe/free-reed law.

## Validation-Loop Shape

If the repo already has `validation.csv`, preserve it as the tuning log.
Extend it with missing fields or add a sidecar `validation-loop.csv` that
cross-references the existing rows. Do not duplicate rows in a disconnected
table.

Minimum validation-loop columns:

```text
check_id,packet_artifact,readiness_before,prediction_source,target,tolerance,method,measured_result,status,next_action,evidence,source_status
```

Recommended starter checks:

- HUL-P0 reed-alone pitch and behavior.
- HUL-P0 pull-down setup: measured reed-alone frequency versus coupled pitch.
- HUL-P1 all-closed single-pipe pitch.
- HUL-P1 selected finger-hole notes if applicable.
- Reed window, tongue clearance, frame seal, and socket leak check.

Allowed statuses are the prototype validation-loop statuses:
`pass`, `measurement_required`, `adjust_packet`, `rebuild_required`, and
`blocked`.

## Acoustic-Law Register

For hulusi/bawu rows, `family-spec.csv` or a sidecar acoustic-law register
must include:

- `member_id`
- `target_hz`
- `target_note`
- `acoustic_law`
- `end_condition`
- `dimension_provenance`
- `predicted_L_geom_mm` when a physics-derived length is claimed
- notes linking the row to the HUL-P0/HUL-P1 evidence

Use `unknown_requires_measurement` with
`dimension_provenance=measurement_required` before the control data exists.
Run `scripts/validate_acoustic_law.py` and treat `rows_checked=0` as a
readiness gap for any reed/free-reed issue.

## Visual And DXF Authority

Hulusi/bawu packets often contain attractive concept renders, SVG previews,
or visual BOM plates before shop geometry is ready. These are not fabrication
authority.

Before any shop-facing handoff, add a `visual-output-register.csv` or JSON
equivalent:

- design tables, CAD, DXF, or measured templates may be `fabrication`
  authority;
- SVG/PDF previews are `derived_preview` only when they name their source;
- generated or concept images are `concept_only` or `reference_only`;
- generated images must not claim reed windows, hole locations, pipe lengths,
  socket centers, or toolpaths.

Production DXF/CAD should remain deferred until HUL-P0 and HUL-P1 validate the
reed, pipe, leak, and pull-down assumptions.

## Copyable Handoff

```text
Upgrade the hulusi/bawu packet as a readiness-gated stopped-pipe free-reed
validation loop. Do not redesign the instrument and do not claim build-ready
DXF/CAD. Preserve the existing validation.csv when present, add or cross-link
HUL-P0 reed coupon and HUL-P1 single-pipe checks, keep acoustic_law as
unknown_requires_measurement until measured data exists, and keep concept
images out of fabrication authority.
```
