# Welfare Gate Schema

Use this reference whenever a habitat-maker packet turns animal welfare
guidance into build acceptance criteria. Welfare gates are pass/fail checks,
not suggestions or "best effort" notes.

The schema is intentionally small so future `habitat-reference` records can
feed packet generation without becoming a second packet format.

## Required fields

Every welfare gate record must include:

| Field | Required | Meaning |
|---|---:|---|
| `gate_id` | yes | Stable lowercase identifier, for example `no_perch` or `drainage`. |
| `label` | yes | Human-readable checklist label. |
| `applies_to` | yes | Habitat or taxon scope, for example `songbird_cavity_box` or `bird_bath`. |
| `severity` | yes | `required`, `conditional`, or `recommended`. |
| `pass_condition` | yes | Observable condition that lets a builder mark the gate passed. |
| `fail_remedy` | yes | Concrete action before the packet can proceed. |
| `evidence` | yes | Measurement, inspection, or deployment artifact to record. |
| `source_ref` | yes | Packet-local or habitat-reference citation key used for provenance. |

Optional fields:

| Field | Meaning |
|---|---|
| `numeric_threshold` | Dimension, count, volume, timing, or tolerance for machine checks. |
| `method_constraints` | Fabrication methods that change the acceptance evidence. |
| `conditional_trigger` | Rule that promotes a conditional gate to required, such as pole mounting. |
| `habitat_reference_key` | Future key in the external `habitat-reference` repo. |

## Controlled values

`severity` has these meanings:

- `required`: packet cannot ship or deploy until this gate passes.
- `conditional`: packet must state the trigger and whether the trigger is
  active. If active, treat as `required`.
- `recommended`: useful welfare guidance that does not block packet release.

`evidence` should be one of:

- `inspection`: builder confirms visible construction state.
- `measurement`: builder records a dimension, count, or tolerance.
- `functional_test`: builder performs a test such as drainage or smoke flow.
- `deployment_record`: builder records siting, mounting, or maintenance state.
- `maintenance_log`: builder records recurring cleaning or refill cadence.

## Cavity habitat baseline

Songbird cavity boxes must include these seven gate ids before the packet can
be treated as habitat-maker compliant:

| Gate id | Severity | Evidence | Minimum pass condition |
|---|---|---|---|
| `no_perch` | required | inspection | No exterior perch is fitted. |
| `no_interior_finish` | required | inspection | Interior surfaces are bare wood or otherwise species-safe bare substrate. |
| `drainage` | required | functional_test | Floor drains are open; songbird boxes provide at least four drains and at least 2 cm2 total open area. |
| `ventilation` | required | functional_test | Cross-ventilation is present under the roof line; songbird boxes provide at least 6 cm2 per side. |
| `fledgling_grip` | required | inspection | Interior front wall below the entrance has score lines, kerf grooves, or rough texture. |
| `predator_baffle` | conditional | deployment_record | Required on pole mounts and any deployment where predator access is not otherwise mitigated. |
| `cleanout_access` | required | inspection | A side, floor, or roof opens with hand tools for annual cleaning. |

## Concrete gate families

Use the same record shape for non-cavity habitats and electronics-enabled
habitats. These starter ids are intentionally compact; packet authors should
expand them into full records with `pass_condition`, `fail_remedy`, `evidence`,
and `source_ref`.

| Applies to | Starter gate ids | Routing note |
|---|---|---|
| `bat_house` | `rough_roost_surfaces`, `chamber_spacing`, `heat_sun_posture`, `predator_exclusion`, `untreated_roost_interior`, `mounting_stability`, `clear_drop_space`, `venting_moisture`, `no_mesh`, `tree_mount_discouraged`, `seasonal_disturbance` | Prefer no internal camera for v1 unless heat, wiring, sealing, service, and disturbance burdens are accepted and gated. Keep `habitat-maker` as the first owner for welfare, site/climate, mount type, and service-calendar decisions; route downstream DXF/CNC, fastener, and workholding details to `makerspace` only after the welfare scaffold is stable. |
| `native_bee_house` | `solitary_bee_scope`, `tunnel_size_match`, `smooth_tunnel_interior`, `dry_overhang`, `replaceable_media`, `parasite_mold_management`, `chemical_avoidance` | Route honeybee colony-management claims away from habitat-maker; keep this scope to solitary native nesting habitat. |
| `observation_hive_preflight` | `qualified_keeper_review`, `secure_containment`, `ventilation_thermal_management`, `escape_proof_service_access`, `public_privacy_safety`, `route_out_colony_decisions` | habitat-maker may document preflight design caveats only; colony welfare, live handling, legal compliance, feeding, disease, and seasonal management route elsewhere. |
| `camera_electronics` | `no_contact_protrusions`, `no_exposed_wires`, `low_heat_load`, `weatherproof_external_routing`, `service_without_disturbance`, `species_safe_sensing`, `fabrication_authority` | Electronics are welfare gates, not gadget notes. Generated images are concept-only; CAD/DXF/JSON or dimensioned drawings remain fabrication authority. |

Do not publish private family/media details in public observation-hive or
camera-enabled habitat packets.

## Habitat-reference workflow

When the external `habitat-reference` repo has species or habitat records,
use it as the source of values and provenance, then copy only the packet-ready
gate records into the local packet's `geometry_params.json` or checklist.

Workflow:

1. Select habitat type, target species, deployment context, and fabrication
   method.
2. Load candidate welfare gates from habitat-maker's baseline plus any
   matching `habitat-reference` records.
3. Resolve conditional gates against the packet context.
4. Record every active `required` or triggered `conditional` gate in the
   packet's single source of truth.
5. Generate or update the checklist from those records.
6. Record `source_ref` values in the agent record so later reviewers can
   trace which species/material references were consumed.

If `habitat-reference` is unavailable or missing a species record, keep using
the habitat-maker baseline gates and cite packet-local references. Do not
drop a gate merely because the shared reference repo is incomplete.

For bat-house packets, preserve unknowns instead of inventing dimensions.
The first welfare scaffold should record target bat group, climate/site
preset, mount type, service calendar, seasonal disturbance window, roughening
method, and whether camera/electronics gates are active before any
machine-authoritative CAD/DXF or shop packet claim.

## Minimal JSON shape

```json
{
  "gate_id": "drainage",
  "label": "Drainage",
  "applies_to": ["songbird_cavity_box"],
  "severity": "required",
  "pass_condition": "At least four floor drains are open with at least 2 cm2 total open area.",
  "fail_remedy": "Clear obstructions or re-cut the floor before deployment.",
  "evidence": "functional_test",
  "numeric_threshold": {
    "drain_count_min": 4,
    "total_open_area_cm2_min": 2
  },
  "source_ref": ["nestwatch_features_good_birdhouse"],
  "habitat_reference_key": "songbird_cavity_box.welfare.drainage"
}
```

The JSON shape above is illustrative, not a replacement for a packet's own
single source of truth. Generator-backed packets still use
`geometry_params.json`; this schema defines the welfare-gate record shape that
file should preserve.
