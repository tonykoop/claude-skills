# Human-Carrying and Floatable-Object Gate

Use this reference when the object will carry, support, restrain, lift, climb,
or float a person, or when failure could put a person in water. Examples:
kayaks, canoes, paddleboards, rafts, chairs, stools, ladders, climbing frames,
play structures, wearable supports, harness-adjacent fixtures, and exercise
equipment.

## Boundary Statement

Always include this language, adapted to the object:

```text
This is a prototype engineering and validation plan, not a certification,
commercial safety approval, or substitute for review by a qualified builder,
engineer, naval architect, instructor, or local authority. Keep the first use
assisted and conservative until the validation gates pass.
```

Do not present the design as safe for open water, overhead lifting, public use,
children, rental/commercial use, rescue use, or high-consequence environments
unless a qualified specialist has reviewed it and the user provided evidence.

## Gate Output

Include these sections before final build packets or specialist handoffs:

```text
Safety boundary:
Intended environment:
Excluded use cases:
User/body assumptions:
Load cases and safety factor:
Prototype vs final-build boundary:
Irreversible steps and pre-step validation:
First-use protocol:
Re-validation triggers:
Specialist handoffs:
```

## Minimum Inputs

State assumptions rather than blocking when reasonable defaults exist, but call
out unknowns that affect safety.

| Input | Why it matters |
| --- | --- |
| User size, mass, mobility, and skill | Sets fit, load, exit/recovery, and misuse risk |
| Intended environment | Water, height, terrain, weather, public/private setting |
| Excluded environments | Prevents quiet scope creep into unsafe use |
| Live load and static load | People move; use dynamic margins, not only body weight |
| Materials and joining method | Failure mode changes with wood, fabric, metal, fasteners, lashings, adhesives |
| Inspection access | Hidden joints or skinned-over structure need earlier checks |
| Rescue or assisted-use plan | First use should not depend on self-rescue |

## Validation Stages

Use staged validation before irreversible steps. Adapt the names to the build.

| Stage | Run before | Checks |
| --- | --- | --- |
| Assumption gate | Detailed design | User/load/environment assumptions, excluded uses, specialist needs |
| Coupon/material gate | Production build | Bend, adhesive, coating, stitch, fastener, or material tests |
| Dry-fit gate | Glue, skin, coating, or final enclosure | Fit, symmetry, clearance, escape/access, visible joint quality |
| Static load gate | First human use | Proof load, deflection, permanent set, joint movement, noises |
| Assisted first-use gate | Independent use | Spotters, rescue plan, PPE, shallow/low-height/low-energy setting |
| Post-use inspection | Continued use | Cracks, looseness, leaks, delamination, wear, fastener movement |

## Trial Matrix Template

For body-load objects:

| Trial | Load/use case | Method | Pass metric | Stop condition |
| --- | --- | --- | --- | --- |
| S1 | Empty/self weight | Visual and dimensional check | No twist, cracks, loose joints | Any structural defect |
| S2 | 0.5x design live load | Static load | No unexpected noise or movement | Joint movement or visible damage |
| S3 | 1.0x design live load | Static load | Deflection within stated limit; no permanent set | Permanent deformation |
| S4 | 1.25-1.5x design live load | Proof load without person | No damage after unloading | Any damage or instability |
| S5 | Assisted first use | Low-energy use with spotter/PPE | Controlled behavior and easy exit | User discomfort or spotter concern |

For floatable objects:

| Trial | Load/use case | Method | Pass metric | Stop condition |
| --- | --- | --- | --- | --- |
| F1 | Empty hull/object | Leak and waterline check | No active leaks; waterline recorded | Any uncontrolled leak |
| F2 | Partial ballast | Shallow protected water | Stable trim; no structure distress | Freeboard collapse or instability |
| F3 | Design displacement | Ballast before person when possible | Minimum freeboard threshold met | Freeboard below threshold |
| F4 | Overload proof | 1.25x design load, no person | No permanent deformation or unsafe trim | Any damage |
| F5 | Assisted human trial | PFD, spotter, tether/shore support | Controlled entry/exit and stability | Capsize tendency or rescue concern |
| F6 | Recovery drill | Wet exit, remount, or assisted recovery | Exit/recovery succeeds within target | Entrapment, panic, cold risk |

## Logging Fields

Record raw measurements, not only pass/fail:

```text
trial_id, date, operator, environment, user_or_ballast_mass,
load_case, measured_deflection_or_freeboard, observed_damage,
repair_or_adjustment, pass_fail, photos_or_sketches, next_action
```

## Re-Validation Triggers

Run the relevant gate again after:

- structural repair;
- material, fastener, adhesive, fabric, coating, or lashing substitution;
- load/user mass change greater than 10 percent;
- environment change, such as calm pond to open water or private chair to public event;
- storage damage, impact, water intrusion, rot, corrosion, UV damage, or loose joints;
- scaling a prototype into a batch or public-facing build.

## Specialist Boundaries

`maker-engineering` owns:

- assumptions, excluded use cases, validation stages, trial matrix, and
  integration checkpoints;
- routing and handoff boundaries;
- explicit non-certification language.

`makerspace` owns:

- jigs, fixtures, workholding, machine setup, steam/heat/chemical process
  safety, inspection gauges, and make/order/buy/borrow decisions;
- shop-specific safety checklists and operation sequence.

Route to another qualified specialist when the project needs certified
structural engineering, naval architecture, rescue/open-water instruction,
child/public-use compliance, or code-regulated construction.

## Example: Steam-Bent Kayak

Safety boundary:
This is a calm-water prototype plan, not a seaworthiness certification or open
water approval. First use requires PFD, spotter, shallow protected water, and a
wet-exit/recovery plan.

Intended environment:
Protected pond, pool, or calm near-shore water in warm conditions.

Excluded use cases:
Open water, cold water without immersion gear, surf, whitewater, expedition
loads, rental/commercial use, child use, and solo first launch.

User/body assumptions:
Adult paddler mass, seated hip width, inseam, foot length, wet-exit ability,
and expected gear load are explicit parameters. Unknowns become conservative
defaults and fit-mockup checks.

Load cases and safety factor:
Use design displacement for paddler plus gear, then a no-person overload test
around 1.25x design displacement before assisted paddler trials.

Irreversible steps and pre-step validation:
Before skinning, inspect rib grain, steam-bend failures, frame symmetry, rocker,
twist, cockpit clearance, and exit path. After coating, run leak, freeboard,
trim, and assisted capsize/recovery trials.

Specialist handoff:
Send steam box, bending forms, backing straps, strongback, station molds,
workholding, coating-area safety, and go/no-go shop checks to `makerspace`.
