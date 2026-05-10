# Observation Camera Modes

Habitat packets may include observation cameras only when the habitat remains
the primary design object and the camera system is isolated from the animal
cavity. Camera support extends the normal `geometry_params.json` contract; it
does not replace the species, material, welfare, cut-list, BOM, safety, or
agent-record requirements.

## Mode Enum

Declare exactly one top-level `camera_observation.mode` value:

| Enum | Meaning |
|---|---|
| `none` | No camera support is included. |
| `interior_view` | Primary camera sees the nest cavity through a sealed optical window from an exterior pod. |
| `exterior_approach` | Camera watches the entrance or approach zone only; no viewport into the cavity. |
| `interior_plus_exterior_approach` | Primary camera is `interior_view`; optional second camera is `exterior_approach`. |

For camera-enabled packets, prefer `interior_view` as the primary observation
mode when the user asks for a live nest view. Add a second exterior approach
camera only when the packet can preserve independent service access, cable
routing, and disturbance controls for both cameras.

## Required Shape

`geometry_params.json` should include this structure:

```json
{
  "camera_observation": {
    "mode": "interior_plus_exterior_approach",
    "primary": {
      "mode": "interior_view",
      "mount": "sealed_roof_pod",
      "electronics_inside_cavity": false,
      "cable_route_enters_cavity": false,
      "service_requires_opening_nest_cavity": false,
      "max_continuous_dissipation_w": 3.0,
      "visible_light_into_cavity": false,
      "status_led_visible_to_cavity": false,
      "moisture_barriers": ["sealed optical window", "gasketed pod lid"],
      "validation_tests": [
        "dark_room_light_leak",
        "30_min_heat",
        "spray_test",
        "service_independence"
      ]
    },
    "secondary": {
      "enabled": true,
      "mode": "exterior_approach",
      "mount": "exterior_rail_under_roof_overhang",
      "electronics_inside_cavity": false,
      "cable_route_enters_cavity": false,
      "service_requires_opening_nest_cavity": false
    }
  }
}
```

## Welfare Gates

Camera packets must add these gates to the normal habitat welfare gates:

- `electronics_isolation`: no electronics, batteries, LEDs, cable splices,
  heaters, or service openings inside the cavity.
- `interior_heat`: powered camera heat does not warm the interior cavity face.
- `interior_light`: no visible LED, white light, or status indicator leaks into
  the cavity.
- `moisture_control`: pod, viewport, cable gland, and drip loops keep water out
  of both the electronics and animal cavity.
- `cable_routing`: cable route remains external and has strain relief plus a
  downward drip loop.
- `service_independence`: camera service does not require opening the nest
  cavity, cleanout door, or habitat mount during active nesting.
- `non_disturbance`: commissioning and maintenance avoid active nests; the live
  feed must not drive repeated close-range visits.

## Geometry Manifest Expectations

When any camera geometry is generator-backed, ship a
`camera-geometry-manifest.json` next to the generated SVG/DXF. The manifest
should name the source parameter file, generator script, generated artifacts,
and welfare-critical features that must be present in the geometry.

Minimum manifest fields:

```json
{
  "schema_version": "1.0",
  "source_params": "geometry_params.json",
  "generator": "scripts/generate_camera_packet.py",
  "generated_artifacts": ["camera-habitat-panels.svg"],
  "required_features": [
    "entrance_hole",
    "side_ventilation",
    "floor_drainage",
    "cleanout_access",
    "interior_camera_pod",
    "sealed_viewport",
    "external_cable_gland",
    "exterior_approach_mount"
  ]
}
```

The exact generator may be packet-specific, but the manifest lets validators
confirm that camera-support geometry is traceable back to `geometry_params.json`
instead of being hand-edited into a vector file.
