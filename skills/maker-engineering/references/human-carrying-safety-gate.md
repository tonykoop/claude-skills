# Human-Carrying / Floatable-Object Safety Gate

Use this gate **before issuing a final build packet or makerspace handoff**
for any project where failure could injure or drown a person. The gate is
the umbrella skill's responsibility — `makerspace`, `instrument-maker`, and
`reverse-engineer` all assume it has already been run.

## When this gate is required

Required for any object that:

- Carries a person (kayak, canoe, rowboat, raft, treehouse, climbing rig,
  trailer, bike frame, sled, ladder, scaffold, swing, hammock stand, child
  seat, lift platform).
- Floats with a person aboard or is intended to be relied on as flotation
  (paddleboard, surfboard, life-buoy, dock float, swim platform).
- Could fail above a person (suspended fixture, overhead shelf above a
  workstation, ceiling-mounted lighting truss).
- Will be used by a child, an elderly user, or a user who cannot self-rescue.

If you are unsure whether the project qualifies, run the gate. False
positives cost a few paragraphs; false negatives can cost a person.

## Gate sections (all required in the output)

The gate template below produces a single short section that lives at the
top of the build packet, before any per-specialist handoff. Every gate
output must include all eight sub-sections.

### 1. Intended environment and excluded use cases

State exactly where the object is intended to be used and exactly where
it must not be used. Be specific about water class, load class, weather,
temperature, audience.

> Example: Intended for protected-coastal day paddling in fair weather,
> water temperature ≥ 12 °C, paddler within sight of shore. Excluded:
> open ocean, surf launches, whitewater, expedition loads, cold-water
> paddling without dry-suit and rescue plan, child solo use.

### 2. User / body-size assumptions

Document the anthropometric envelope the design assumes. State paddler
weight range, height range, foot size, and any other body dimension that
drove a parameter. Name the design center and the supported range.

> Example: Design center: adult paddler 82 kg / 178 cm / size-9 foot.
> Supported range: 70–95 kg paddler weight, 165–190 cm height. Outside
> this range: re-derive station offsets from the parametric schema and
> re-run validation.

### 3. Load cases and safety factor

List the load cases the design must survive and the multiplier applied
above expected use load.

> Example: Static seated paddler (1.0×). Loaded paddler + day gear
> (1.0×). Cockpit-only static load test (1.25×) — sandbags simulating
> seated load + 25% margin. Capsize impact loads (uncharacterized for
> SOF; assumed within elastic recovery of 6mm white oak ribs but not
> verified analytically).

### 4. Prototype vs final-build boundary

State explicitly whether the artifact is a prototype, a working build, or
a production-intent build. Prototypes get more validation gates and less
load tolerance.

> Example: This is a single-prototype build for personal use under
> validation conditions in §6. Not a production-intent design. Not a
> commercial product. Not for sale or loan to other paddlers without
> independent inspection by a qualified boatbuilder.

### 5. Staged validation before irreversible steps

List validation stages that must pass *before* the next irreversible
step. The full trial matrix lives in DoE mode (see
`references/doe-template.md`); the gate just enumerates the gates.

| Stage | Before this irreversible step | Pass criteria |
| --- | --- | --- |
| Frame symmetry / fairness | Skinning | Stations within ±5 mm port/starboard; sheer fair to batten |
| Static load (frame) | First float | 1.25× design payload at cockpit zone for 30 min, no creak / no permanent set |
| Coupon + panel coating | Hull coating | Coupons pass flex + abrasion + leak tests |
| Pinhole leak (skinned + cured) | First paddler | Zero visible weeping in 30 min |
| Empty float | Loaded float | Floats level; no obvious imbalance |
| Loaded ballast float | Assisted paddler | Loaded freeboard ≥ 80 mm at lowest point |
| Assisted shallow-water float | Solo paddle | Stable at design displacement; wet-exit ≤ 4 s |

Each row is a stop-the-build gate. A failed gate triggers diagnose →
fix → re-test, not "skip and continue".

### 6. Assisted first-use protocol

Describe the conditions under which a person first uses the object.

> Example: First in-water trial: shallow protected water (<1 m depth),
> water temperature ≥ 15 °C, air temperature ≥ 18 °C, wind < 5 m/s,
> paddler in PFD, rescue spotter in second boat or on shore with throw
> rope, float bags installed bow and stern, no cargo, no current. Wet
> exit attempted on command before any solo paddling.

### 7. Re-validation triggers

List the events that require part or all of the validation matrix to be
re-run.

| Event | Re-run |
| --- | --- |
| Structural repair (rib replacement, masik replacement) | Symmetry + static load + first float |
| Skin patch > 100 cm² or full re-coat | Pinhole leak + ballast float |
| Material substitution (different oak, different fabric) | Coupon + panel + pinhole + ballast float |
| New paddler outside design body-size envelope | Anthropometric re-derive + ballast float at new mass |
| Use-class change (protected → open water, day → expedition) | Whole gate |
| Storage > 1 year, or visible UV / mold damage | Pinhole + static load |

### 8. "Not a certification" language (mandatory)

Every human-carrying / floatable build packet must include this clause
verbatim or in equivalent words:

> This packet is a maker's design and validation plan. It is **not** a
> commercial certification, marine-survey approval, naval-architecture
> sign-off, structural-engineering sign-off, or insurance qualification.
> Build, inspect, and use at the builder's and user's own informed risk.
> If commercial sale, public hire, or use in regulated waters is
> intended, retain a credentialed specialist for review before that use.

Do not soften this clause. Do not bury it. Place it in the gate section
at the top of the packet.

## Specialist handoff shape (engineering-assumptions vs makerspace)

The gate's output sets up later specialist handoffs by separating what
belongs to engineering assumptions from what belongs to shop process.

Belongs in the gate (engineering assumptions, owned by
`maker-engineering`):

- Anthropometric envelope and design center
- Load cases, safety factor, and the rationale
- Use-case scope and exclusions
- Prototype/final boundary and "not a certification" clause
- Validation stage list and pass criteria (the *what* and *when*)
- Re-validation trigger list

Belongs in the `makerspace` handoff (shop process):

- Fixture builds for any test rig (load frame, ballast cradle)
- Workholding for the artifact during static-load testing
- Safety equipment selection for shop tests (lanyards, cribbing, eye
  protection)
- The *how* of running each validation stage in the shop

Belongs to the user (cannot be delegated to either skill):

- Decision to actually use the object after the gate is met
- Choice to operate outside the documented envelope (and the consequences)
- Final inspection by a credentialed specialist if commercial use is intended

## Gate output template (copy-paste)

```markdown
## Safety Gate — human-carrying / floatable object

**Object class:** <kayak | bike frame | treehouse | …>
**Maturity:** <prototype | working build | production-intent>

### Intended environment
<…>

### Excluded use cases
<…>

### Anthropometric envelope
- Design center: <weight, height, foot, etc.>
- Supported range: <range>
- Outside range: re-run schema and gate

### Load cases and safety factor
<…>

### Prototype vs final
<…>

### Staged validation gates
| Stage | Before | Pass criteria |
| --- | --- | --- |
| <…> | <…> | <…> |

### Assisted first-use protocol
<…>

### Re-validation triggers
| Event | Re-run |
| --- | --- |
| <…> | <…> |

### Not a certification
This packet is a maker's design and validation plan. It is not a
commercial certification, marine-survey approval, naval-architecture
sign-off, structural-engineering sign-off, or insurance qualification.
Build, inspect, and use at the builder's and user's own informed risk.
If commercial sale, public hire, or use in regulated waters is
intended, retain a credentialed specialist for review before that use.
```

## Worked example: steam-bent kayak (Round 7)

The Round 7 TwinGrid steam-bent kayak packet (lane Frank, both A and B
sides) is the canonical example for this gate.

**Object class:** kayak (human-carrying + floatable).
**Maturity:** single prototype for personal use.

**Intended environment:** protected-coastal day paddling, water ≥ 12 °C,
paddler within sight of shore.
**Excluded:** open ocean, surf, whitewater, expedition loads, cold water
without dry-suit, child solo use.

**Anthropometric envelope:** design center 82 kg / 178 cm; supported
70–95 kg / 165–190 cm. Outside → re-derive offsets from
`v2_parametric_schema.yaml` via `derive_offsets.py` and re-run gate.

**Load cases:** seated 1.0×; loaded 1.0× (paddler + 5 kg gear); static
test 1.25× sandbags. Capsize loads not analytically verified.

**Prototype vs final:** single prototype; not for sale or loan; no
public-water hire.

**Staged validation gates:** see the table above; all seven stages must
pass in order. The gate maps directly onto the existing Round 7 packet
files `04_validation_safety_plan.md` (trial matrix) and
`v2_parametric_schema.yaml#constraints` (numeric tolerances).

**Assisted first use:** shallow water, PFD, rescue spotter, float bags,
no cargo, wet-exit drill before solo paddle.

**Re-validation:** rib replacement → symmetry + static + first float;
skin patch → pinhole + ballast float; new paddler outside envelope →
re-derive + ballast.

**Not a certification:** standard clause as above.

The gate would have caught one omission in the original Round 7 packet:
the original packet's "validation/safety" section was thorough on
*method* but did not state the load safety factor (1.25× sandbag) as a
numeric requirement, only as a paragraph. The gate's load-cases
sub-section makes that requirement explicit and machine-checkable
against the schema's `constraints` block.

## Companion references

- `references/doe-template.md` — owns the trial-matrix discipline. The
  gate references it but does not duplicate the DoE structure.
- `references/routing-decision-tree.md` — adds a Safety-Critical Object
  branch that calls into this gate.
- `references/specialist-registry.md` — names canonical specialists used
  in handoffs.
