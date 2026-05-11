# Prototype Validation-Loop Upgrade Template

Use this template when an instrument prototype repo already has a packet, but
the packet has not yet been upgraded into an empirical validation loop. The
goal is not to rewrite the project. The goal is to add the minimum auditable
loop that lets a future builder compare predicted dimensions, measured results,
and next-iteration decisions without losing the original design intent.

This applies to flutes, reeds, strings, drums, idiophones, hybrid
acoustic/electric builds, and family-aware packets. If the repo is still only a
concept with no packet artifacts, create the packet first instead of using this
upgrade path.

## When Not To Use

Do not use this path for a repo-first bare-bones starter packet. If the repo is
labeled `readiness:bare-bones`, asks for a "first packet," or has no packet
files yet, create the starter packet before adding this validation loop. This
template starts after the repo already has packet artifacts that can be checked
against measurements or explicit experiment plans.

Use this path when the current packet has enough structure to name:

- The artifact being validated.
- The predicted target or qualitative claim.
- The method that will prove or disprove that claim.
- The next action if the claim is not yet measured.

## Upgrade Flow

1. Inventory the existing packet.
   - Record the source repo, branch or commit, packet folder, and packet tier.
   - List authoritative fabrication artifacts: CAD, DXF, CAM, drawings,
     design tables, cut sheets, BOMs, tuning sheets, and build notes.
   - Mark generated images as concept/story support only. They must not replace
     CAD, DXF, measured drawings, or design tables as fabrication authority.

2. Assign a readiness label.
   - `L0_concept`: idea or sketch, no complete packet.
   - `L1_packet`: packet exists but has not been built or measured.
   - `L2_bench_validated`: critical dimensions or acoustic targets have bench
     measurements.
   - `L3_playable_prototype`: playable build exists with tuning/playability
     results logged.
   - `L4_repeatable_packet`: at least one successful iteration has been folded
     back into the packet and can be repeated by another builder.

3. Add `validation-loop.csv`.
   - Copy `examples/khaen/prototype-validation-loop.csv` or create an
     equivalent file in the target packet.
   - Every row must name the packet artifact being validated, the predicted
     target, tolerance, measurement method, result, status, and next action.
   - For family-aware wind/free-reed packets, keep running
     `scripts/validate_acoustic_law.py` on `family-spec.csv`; this template
     complements that validator and does not replace it.

4. Capture measurements before revising geometry.
   - Use measured values when they exist, including temperature/humidity for
     wind instruments and material state for wood, ceramic, metal, or skin.
   - If the prototype is not yet measured, set `status=measurement_required`
     and write the exact next measurement in `next_action`.
   - If a measurement contradicts the packet, keep the old prediction visible
     and add an iteration note instead of silently overwriting history.

5. Close the loop.
   - `pass`: prediction and measurement agree within tolerance.
   - `adjust_packet`: revise the packet, CAD, DXF, or design table from the
     measurement.
   - `rebuild_required`: the measurement exposes a build or fabrication issue.
   - `blocked`: a missing tool, unsafe process, unavailable source, or unknown
     acoustic model prevents the next iteration.

6. Update the packet record.
   - Record the new readiness label and the validation-loop file path in the
     packet README or build log.
   - For public repos, keep private family/media details out of issues and
     docs. Use neutral provenance such as "builder measurement" unless the
     user has explicitly approved a personal story detail for publication.
   - For supplier-driven rows, mark stale or unverified facts explicitly with
     `supplier_spec_unverified`, `needs_current_check`, or
     `substitution_candidate` rather than treating old listings as design data.

## Minimum `validation-loop.csv` Columns

| Column | Required | Meaning |
| --- | --- | --- |
| `check_id` | yes | Stable check id, for example `vl001`. |
| `packet_artifact` | yes | File or artifact under test, such as `family-spec.csv` or `mouthpiece.dxf`. |
| `readiness_before` | yes | One of `L0_concept`, `L1_packet`, `L2_bench_validated`, `L3_playable_prototype`, `L4_repeatable_packet`. |
| `prediction_source` | yes | Formula, CAD dimension, design table, prior build, supplier data, or user measurement. |
| `target` | yes | Predicted target value or qualitative gate. |
| `tolerance` | yes | Numeric tolerance, pass/fail rule, or `measurement_required`. |
| `method` | yes | How the check is measured or verified. |
| `measured_result` | yes | Actual result, or `TBD` before measurement. |
| `status` | yes | One of `pass`, `measurement_required`, `adjust_packet`, `rebuild_required`, `blocked`. |
| `next_action` | yes | Concrete follow-up that closes or advances the loop. |
| `evidence` | yes | Measurement log, photo set, tuner capture, caliper note, commit, or issue link. |

Optional rows may add `source_status` when the validation claim depends on a
supplier listing, donor part, catalog value, or purchased component. Use
`supplier_spec_unverified`, `needs_current_check`, or
`substitution_candidate` until the fact is verified for the current build.

## Packet Upgrade Prompt

Use this prompt shape when handing an existing repo to an agent:

```text
Upgrade the existing instrument packet in <repo/path> with an empirical
validation loop. Do not redesign the instrument. Inventory the existing packet,
assign a readiness label, add validation-loop.csv using the instrument-maker-v4
template, keep CAD/DXF/design tables as fabrication authority, and record the
next measurement or iteration decision for each critical acoustic and
manufacturing check. Do not publish private family/media details.
```

## Acceptance Gate

The upgrade is complete when:

- The packet has a readiness label and a `validation-loop.csv`.
- Every critical acoustic or fabrication claim has a target, method, status,
  and next action.
- CAD, DXF, design tables, or measured drawings remain the fabrication
  authority.
- Generated images, if present, are labeled as concept/story support only.
- The next builder can tell whether the repo needs measurement, packet edits,
  a rebuild, or no action before the next iteration.
