# CADFit Feature Extractor Adapter

Use this reference for the mesh/scan branch of `maker:reverse-engineer` when a real watertight mesh or point cloud exists.

The public adapter is a structured boundary around CADFit-style feature extraction. It does not vendor CADFit code. When CADFit/native geometry tools are unavailable, it still returns a machine-readable degraded result so the agent can ask for the right artifact instead of hallucinating CAD features.

## Input Contract

Required:

- `mesh_path`: local path to a mesh or point-cloud artifact (`.stl`, `.obj`, `.ply`, `.off`, `.step`, `.stp`)

Optional metadata JSON:

```json
{
  "watertight": true,
  "bbox": {"x": 120, "y": 80, "z": 30},
  "units": "mm",
  "symmetry_axes": ["z"],
  "planar_sections": [
    {"axis": "z", "offset": 0, "profile": "rounded_rectangle"}
  ]
}
```

## Output Contract

The adapter returns:

- `status`: `ok`, `degraded`, or `error`
- `mesh`: path, extension, existence, watertight flag, units, and bounding box if known
- `candidate_sketch_profiles`: profile guesses with evidence labels
- `slicing_planes`: axis/offset candidates
- `revolution_axes`: axis-vector candidates
- `findings`: human-readable issues or next actions

## Degraded Behavior

If no usable mesh is supplied, return `status: degraded` and findings that ask for a watertight mesh or point cloud. Do not run CADFit for photo-only, sketch-only, named-object, or description-only intake.
