# Bat, Bee, Observation-Hive, And Electronics Welfare Reference

Use this reference when a `habitat-maker` prompt asks for a bat house, native
bee house, solitary bee hotel, observation-hive design preflight, or habitat
camera/electronics integration. The output should be a welfare review packet
with pass/fail gates, not a gadget-first concept.

## Default Routing Pattern

Default to the least intrusive design that can still be inspected and
maintained:

- Bat houses: no internal camera for v1 unless the prompt explicitly accepts
  heat, wiring, sealing, service, and disturbance burdens.
- Bat-house example scope: a four-chamber packet is appropriate for the first
  canonical skill-package example, but chamber count is not a default
  requirement for all `bat-houses` scaffolds. Choose chamber count from the
  target bat group, site/climate, mounting posture, welfare gates, and
  deployment assumptions before claiming build-ready geometry.
- Native bee houses: removable or replaceable nesting media under a dry
  overhang; avoid permanent sealed blocks that cannot be cleaned or retired.
- Observation-hive prompts: provide only design preflight caveats and route
  colony welfare, legal, and live bee handling decisions to a qualified keeper
  or project-specific path.
- Camera/electronics: place components outside animal-contact paths and make
  all service operations possible without opening occupied chambers.

Generated images may support concept/story work, but must never replace
CAD/DXF/JSON or dimensioned packet artifacts as fabrication authority.

## Reusable Gate Record Shape

When a packet copies these gates into `geometry_params.json`, a generated
checklist, or future `habitat-reference` records, preserve a small reusable
record shape:

| Field | Required | Meaning |
| --- | --- | --- |
| `gate_id` | yes | Stable lowercase identifier, for example `bat_heat_sun_posture`. |
| `label` | yes | Human-readable checklist label. |
| `applies_to` | yes | Habitat or taxon scope, for example `bat_house` or `native_bee_house`. |
| `severity` | yes | `required`, `conditional`, or `recommended`. |
| `pass_condition` | yes | Observable condition that lets a builder mark the gate passed. |
| `fail_remedy` | yes | Concrete action before the packet can proceed. |
| `evidence` | yes | Measurement, inspection, service plan, or deployment artifact to record. |
| `source_ref` | yes | Packet-local or habitat-reference citation key used for provenance. |

Do not drop a welfare gate because `habitat-reference` is missing, sparse, or
not yet populated. Use this reference as the packet-local baseline until a
reviewed external record is available.

## Bat House Welfare Gates

Every bat-house packet must include these pass/fail gates.
If a packet uses a four-chamber layout, record it as the selected example or
design scope and still document why that chamber count fits the target bat
group and site. Do not let the canonical example layout substitute for target
group, climate/site, mount type, or deployment evidence.

| Gate | Pass condition | Fail remedy |
| --- | --- | --- |
| Rough landing and roost surfaces | Landing pad and internal roost surfaces are roughened, grooved, or otherwise bare-textured for secure climbing without mesh or snag-prone liners. | Add shallow kerfs/grooves or roughen the wood; reject slick plastic, slick finishes, loose fibers, or mesh that can snag claws or wings. |
| Chamber spacing | Chamber gap is sized for the target bat group and does not create a loose deep cavity. | Adjust spacers before fabrication; do not rely on vague "bat box" proportions. |
| Heat and sun posture | Packet names climate/site preset, sun exposure, exterior color/finish, venting and moisture posture, and overheating mitigation. | Re-site, change exterior color, add ventilation/moisture-shedding detail, or reject the mounting location. |
| Predator exclusion | Entry geometry and mounting avoid perches, ledges, and easy predator reach. | Remove ledges/perches, raise mount height, or redesign the entry zone. |
| Untreated interior | No paint, stain, oil, adhesive squeeze-out, or loose fibers contact roosting bats. | Keep interior bare and mechanically clean; move coatings to exterior-only surfaces. |
| Exterior-only weatherproofing | Weather protection is outside the roost path and fully cured before deployment. | Seal exterior seams only; reject uncured, odorous, or interior coatings. |
| Mounting stability | Mount type is named and resists wind, vibration, and seasonal movement without opening gaps; tree mounts are discouraged unless a qualified review documents the added predator, sway, and maintenance risks. | Improve backing, fasteners, or site; prefer building, pole, or post mounting; do not deploy a wobbly or unreviewed tree-mounted box. |
| Clear drop space | Deployment record documents a clear entry/drop zone for the target site without immediate obstructions, ledges, or clutter below the entrance. | Re-site, raise, clear the approach zone, or reject the deployment until the entry/drop path is documented. |
| Venting and moisture | Vent and weather-shedding details are dimensioned or otherwise inspectable, with no water-wicking path into roost chambers. | Add vent/moisture details to the drawing or parameter file before treating the packet as fabrication-ready. |
| Seasonal disturbance | Packet names seasonal disturbance windows and includes a service calendar; inspection, camera service, or relocation during maternity or hibernation-sensitive windows is forbidden unless handled by qualified wildlife support. | Delay service, remove electronics, or keep the packet concept-only until the box is confirmed unoccupied and service timing is documented. |

## Native Bee House Welfare Gates

Use these gates for native solitary bee houses and tube/block bee hotels. This
skill does not provide honeybee colony-management instructions.

| Gate | Pass condition | Fail remedy |
| --- | --- | --- |
| Native solitary bee scope | Packet names target solitary bee group and avoids honeybee hive claims. | Route honeybee colony questions elsewhere; rewrite scope around solitary nesting habitat. |
| Tunnel diameter and depth | Tunnel dimensions match the target group range and are documented in the packet. | Change tube/block dimensions before build; do not mix unknown random holes. |
| Smooth tunnel interiors | Tubes or drilled holes are smooth, splinter-free, and closed at the back where appropriate. | Sand, re-drill, replace liners, or reject splintered media. |
| Dry overhang | Nesting media stays dry under a roof/overhang with a slight downward or protected posture. | Add roof depth, side shielding, or relocate away from wind-driven rain. |
| Replaceable media | Tubes, liners, trays, or blocks can be replaced or retired without destroying the whole habitat. | Use removable cartridges or design for periodic replacement. |
| Parasite and mold management | Packet includes seasonal retirement, cleaning/replacement cadence, and mold rejection signs. | Add a maintenance calendar; reject permanent damp blocks. |
| Chemical avoidance | No treated wood, pesticide residue, fresh finish, or odorous adhesive contacts nesting tunnels. | Replace contaminated media or isolate finishes away from nest contact. |
| Predator and pest posture | Packet addresses birds, ants, wasps, and rodents without using sticky traps or toxic controls. | Re-site, add physical shielding, or simplify the habitat. |

## Observation-Hive Preflight Gates

Use these gates only for design review and public packet caveats. Route
beekeeping welfare decisions, live colony handling, legal compliance,
transport, feeding, disease, and seasonal management to the observation-hive
project path or a qualified local keeper.

| Gate | Pass condition | Fail remedy |
| --- | --- | --- |
| Qualified keeper review | Packet requires review by a qualified beekeeper before any live colony use. | Mark as concept-only until reviewed. |
| Secure containment | Bee paths, doors, seals, and viewing panels are escape-resistant by design. | Redesign closures, gaskets, and service access before live use. |
| Ventilation and thermal management | Packet documents airflow, heat load, sun exposure, and emergency shade/cooling posture. | Add ventilation analysis or reject the viewing location. |
| Escape-proof service access | Maintenance can be performed without uncontrolled bee release into public or family areas. | Add service protocol constraints or keep as non-live display. |
| Public and privacy safety | Packet excludes private family/media details and names public standoff, signage, and supervision constraints. | Redact private details and add public safety boundaries. |
| Route-out decisions | Colony sourcing, inspection cadence, feeding, disease response, queen status, overwintering, and legal questions are explicitly out of scope. | Route to project-specific beekeeping support. |

## Camera And Electronics Caveats

Apply these gates to any habitat packet that adds a camera, microphone, sensor,
light, battery, solar panel, cable, controller, or networked device.

| Gate | Pass condition | Fail remedy |
| --- | --- | --- |
| No contact protrusions | Components, mounts, screws, and cable ties do not protrude into animal-contact paths. | Move hardware outside the chamber or recess behind a smooth barrier. |
| No exposed wires | Wires are outside occupant paths, strain-relieved, and protected from chewing, claws, moisture, and abrasion. | Externalize wiring or remove electronics. |
| Low heat load | Packet documents device heat, sun exposure, ventilation, and worst-case temperature posture. | Use lower-power gear, external mount, shade, or delete the device. |
| Weatherproof external routing | Cable penetrations shed water and do not wick moisture into nesting/roosting space. | Add drip loops, exterior glands, or sealed external raceways. |
| Service without disturbance | Battery, memory, cleaning, and reset operations do not require opening occupied chambers. | Move service points outside or require unoccupied-season service only. |
| Species-safe sensing | Visible light, IR, audio, ultrasonic, Wi-Fi, or other emissions are absent unless the packet documents species-safe evidence and a disable plan. | Disable emissions, move the sensor outside, or reject the camera feature. |
| Fabrication authority | Camera renders and concept images are labeled non-authoritative; dimensions come from CAD/DXF/JSON or packet drawings. | Update the packet so generated images cannot be mistaken for build geometry. |

## Compact Review Checklist

Use this as the minimum field checklist for bat, bee, observation-hive, or
electronics review packets.

- [ ] Habitat type and target species/group are named.
- [ ] Climate/site preset, mount type, and service calendar are named before
      bat-house deployment or fabrication claims.
- [ ] Welfare gates are pass/fail, not suggestions.
- [ ] Animal-contact surfaces are untreated, non-toxic, and mechanically safe.
- [ ] Maintenance can be done without disturbing occupied chambers.
- [ ] Heat, moisture, and ventilation risks are explicitly addressed.
- [ ] Predator/pest posture avoids perches, ledges, toxic controls, and sticky
      traps.
- [ ] Camera/electronics are outside animal-contact paths by default.
- [ ] Any lights, IR, audio, ultrasonic, wireless, or heat-emitting devices
      have species-safe evidence or are removed.
- [ ] Observation-hive colony decisions are routed out to qualified support.
- [ ] Private family/media details are excluded from public-facing docs.
- [ ] Generated images are marked concept-only when fabrication geometry is
      governed by CAD/DXF/JSON or dimensioned drawings.

## Agent Record Requirements

When producing a bat, bee, observation-hive preflight, or electronics-enabled
habitat packet, record:

- Habitat context: species/group, site, season, sun/heat exposure, moisture
  exposure, mounting location, and occupancy assumptions.
- Welfare decision: gates applied, rejected features, and maintenance cadence.
- Electronics decision: device placement, heat estimate posture, cable route,
  service plan, and emissions disabled or justified.
- Routing decision: any beekeeping, legal, live-handling, private-media, or
  qualified-review items that were explicitly moved out of public docs.
- Validation run: pass/fail checklist, fit check, and any render/CAD/codegen
  checks used for the packet.
