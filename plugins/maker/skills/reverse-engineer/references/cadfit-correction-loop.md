# CADFit Error-Guided Correction Loop

Use this reference after `test_cad_program()` returns score and residual feedback.

## Correction Rules

- `over_reconstruction`: the candidate contains extra material. Recommend `cut()` for the affected region.
- `under_reconstruction`: the candidate is missing material. Recommend `union()` with a new or refined primitive.
- `kernel_failure`: simplify the last risky operation, reduce fillet/chamfer complexity, or split the candidate into smaller primitives.
- `low_iou_without_residuals`: return to feature extraction; the current sketch tree is likely wrong.

## Termination

Stop the correction loop when any is true:

- `volumetric_iou >= target_iou`
- `iteration >= max_iterations`
- score status is `kernel_unavailable`
- a manufacturing review flag is unresolved

Default public thresholds:

- `target_iou = 0.92`
- `max_iterations = 8`
- `prune_tolerance = 0.01`

## Backward Pruning

After IoU is high, walk operations from newest to oldest:

- Drop an operation if removing it lowers IoU by at most `prune_tolerance`.
- Never drop operations marked `manufacturing_critical`.
- Re-score after each drop in a real kernel environment.

## IoU Is Not Correctness

High IoU can still hide a manufacturing-wrong CAD tree. Keep these guardrails:

- preserve functional interfaces, symmetry axes, fastening features, and datum-defining planes
- flag operations that create non-manufacturable slivers or impossible tooling access
- require a human manufacturing review before presenting the tree as builder-ready
