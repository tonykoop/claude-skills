# Chickadee Camera Observation Contract

This is a short contract example for habitat-maker camera modes. It is not a
full build packet; it exists to show the machine-readable shape that validators
expect before a packet adds generated interior-view and optional exterior
approach camera geometry.

The example declares:

- primary `interior_view` mode through a sealed roof pod and optical window
- optional second `exterior_approach` camera on an outside rail
- welfare gates for electronics isolation, heat, light, moisture, cable route,
  service independence, and non-disturbance
- a `camera-geometry-manifest.json` that names the generated artifacts and
  welfare-critical geometry features

Validate from the repo root:

```bash
python3 skills/habitat-maker/scripts/validate_camera_modes.py \
  --packet skills/habitat-maker/examples/chickadee-camera-observation-contract
```
