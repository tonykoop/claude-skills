# CADFit `test_cad_program()` Adapter

Use this reference when evaluating an agent-written CadQuery hypothesis against a target mesh/scan.

The adapter returns CADFit-shaped feedback:

- `invalid_ratio`: `0.0` for a valid candidate, `1.0` for compile/kernel/runtime failure in the current public adapter
- `volumetric_iou`: overlap score from `0.0` to `1.0`
- `status`: `ok`, `invalid_program`, `kernel_unavailable`, or `kernel_failure`
- `findings`: feedback for the next correction loop

## Runtime Requirements

Real kernel scoring requires a local CADFit/CadQuery/OpenCascade environment. The public skill does not vendor CADFit or CadQuery. In Codex CLI sandboxes, mobile hosts, or zip-uploaded skill hosts, expect `kernel_unavailable` unless the user has installed native dependencies locally.

## Safe Public Behavior

The public adapter:

- compiles the candidate Python source to catch syntax errors
- detects whether `cadquery` is importable
- accepts deterministic mock score assignments for tests and offline review
- returns failures as data, not thrown exceptions

For full kernel execution, run only in a user-controlled CADFit environment and treat OpenCascade crashes, non-manifold solids, and self-intersections as normal invalid-ratio signals.

## Offline Score Fixture

A candidate script may include:

```python
CADFIT_MOCK_RESULT = {
    "candidate_volume": 80,
    "target_volume": 100,
    "intersection_volume": 70
}
```

The adapter computes:

```text
IoU = intersection / (candidate + target - intersection)
```

This is not a substitute for real kernel scoring; it is a deterministic review fixture for CI and agent-loop tests.
