# Universal Interface Guide (the "Lego rule")

Story #245 of the Cross-Pollination Engine (epic #236). This design guide
establishes standardized mechanical and electrical interfaces so subassemblies
are **swappable across projects** - design like Lego, not like a one-off. It is
the target the constraint-injection prompt (#246) enforces and the vocabulary
the `interfaces:` facet (#243) references.

> Cross-links to **HWE-Pipeline #39** (cross-layer maker signature / cohesion):
> the Universal Interface set is the mechanical expression of the same
> portfolio cohesion goal - one recognizable system, parts that mate across the
> whole body of work.

## The Lego rule

> If two subassemblies perform compatible functions, they should physically and
> electrically mate **without rework**. Standardize the boundary, vary the
> guts.

A Lego brick is interesting because the stud-and-tube interface never changes.
Apply that to the portfolio: a `mount:t-slot-2020` bracket from an instrument
stand should bolt onto a camera rig, a planter trellis, or a shop fixture. The
interface is the contract; everything behind it is free to differ.

## 1. Standard mounting patterns

Pick from this set before inventing a new hole pattern. Tag the choice as
`interfaces: [mount:<value>]` (#243).

| Token | Pattern | Use for |
|---|---|---|
| `mount:t-slot-2020` | 20x20 aluminum extrusion T-slot, M5 | Frames, stands, rails, jigs |
| `mount:t-slot-3030` | 30x30 extrusion T-slot, M6 | Heavier frames, load-bearing |
| `mount:vesa-75` | 75x75 mm, M4 | Panels, displays, swing arms |
| `mount:vesa-100` | 100x100 mm, M4 | Larger panels, wall mounts |
| `mount:hole-pattern-43x43` | 43x43 mm square, M4 | NEMA-17-adjacent, small brackets |
| `mount:dovetail-arca` | Arca-Swiss dovetail | Quick-release camera/optic mounts |
| `mount:keyhole-pair` | Two keyhole slots @ 16 mm o.c. step | Wall-hung modules, STAS-style |
| `mount:magnetic-m4` | N52 magnet + M4 alignment pin, 25 mm disc | Rapid-swap, light-load, no-tool swap modules |

Rule: a new module gets at least **one** standard mount face, even if it also
has a bespoke face. That one standard face is its Lego stud.

`mount:magnetic-m4` notes: N52 (neodymium grade 52) 25 mm disc magnet, retained
with an M4 alignment pin so the joint is rotation-keyed, not free-spinning. Load
limit ~10 N perpendicular, ~2 N shear — suitable for sensors, small tools, and
indicator panels, not structural joints. Pair with a ferrous or matching-magnet
mating plate in the host module.

## 2. Fastener standards

Converge the fastener kit so any module can be serviced with the same drivers.

| Token | Standard | Default use |
|---|---|---|
| `fastener:m3` | M3 socket cap, 2.5 mm hex | Electronics, light brackets |
| `fastener:m5` | M5 socket cap, 4 mm hex | Primary structural default |
| `fastener:1/4-20` | 1/4"-20 UNC | Camera/photo, tripod legacy |
| `fastener:heat-set-m3` | M3 heat-set insert into plastic | 3D-printed threaded joints |
| `fastener:heat-set-m5` | M5 heat-set insert into plastic | Heavier printed joints |

Rules:
- Default to **M5** for structure and **M3** for electronics unless there is a
  reason not to.
- In printed plastic, never tap directly - specify a heat-set insert.
- Mixed imperial only where a legacy interface forces it (`1/4-20` for
  camera/photo); note the exception in the idea frontmatter.

## 3. Tolerance classes

Name the fit, do not re-derive it each time. Tag as `interfaces: [tolerance:<class>]`.

| Token | Fit | Typical clearance (metric H-shaft) | Use |
|---|---|---|---|
| `tolerance:clearance-loose` | Free-running | ~ +0.2 to +0.4 mm | Hand-assembled, printed parts |
| `tolerance:slip-h7` | Slip / locating | ~ +0.0 to +0.05 mm | Dowels, alignment pins |
| `tolerance:press-p7` | Light press | ~ -0.02 to -0.05 mm | Bearings, bushings |
| `tolerance:thread` | Threaded | per fastener spec | Screw joints |

For FDM-printed mating parts, default to `clearance-loose` and add a printed
test coupon before committing the real part.

## 4. Connector / pinout conventions (electrical)

Standardize the electrical boundary so a power or signal module drops into any
project. Tag as `interfaces: [connector:<value>, pinout:<value>]`.

| Token | Standard | Use |
|---|---|---|
| `connector:xt60` | XT60, red = +, polarity keyed | Battery / high-current DC |
| `connector:jst-ph` | JST-PH 2.0 mm | Signal / low-current, removable |
| `connector:usb-c` | USB-C | Data + power, user-facing |
| `connector:grove` | Grove 4-pin | Quick sensor prototyping |
| `connector:can-usbc` | CAN bus tunneled over USB-C (SLCAN or candleLight firmware) | Multi-node CAN networks with a single cable |
| `pinout:i2c-4pin` | GND, VCC(3v3), SDA, SCL (in that order) | I2C sensors |
| `pinout:uart-3v3` | GND, TX, RX, VCC(3v3) | Serial debug / comms |
| `pinout:can-2wire` | CAN_H, CAN_L (120 Ω termination at each bus end) | CAN bus nodes |

Rules:
- One **VCC convention per project**: declare 3v3 or 5v in the project README;
  never mix on the same connector family.
- Power connectors must be **polarity-keyed** (XT60) - no bare-wire DC.
- Pin order is part of the contract; document it where the connector is
  defined, and reference the token in frontmatter.
- `connector:can-usbc` requires a USB-C adapter with SLCAN or candleLight
  firmware (e.g., Canable, Cantact). Declare the adapter model in the
  project README. Bus termination (120 Ω at both ends) is the installer's
  responsibility; note it in the wiring diagram.

## 5. Naming convention

Names are an interface too. A predictable name lets the Cross-Pollination Agent
(#247) and the circuits inventory (#248) match parts without guessing.

```
<domain>-<function>-<variant>
```

- `domain` - matches the `domain:` frontmatter (`maker`, `instrument`, ...).
- `function` - the canonical `functions:` token (`index-detent`, `tension`, ...).
- `variant` - short distinguishing suffix (`v2`, `8mm`, `xt60`).

Examples: `maker-index-detent-8mm`, `instrument-tension-brass`,
`maker-mount-t-slot-2020`.

## 6. Adoption checklist

For any new subassembly or design-generation request:

1. Does it expose **one standard mount** from section 1? If not, add one.
   (Magnetic quick-swap? Use `mount:magnetic-m4`. Structural frame? Use `mount:t-slot-2020`.)
2. Are all fasteners from section 2? Flag any one-off.
3. Is the fit named from section 3?
4. If electrical, are connector + pinout from section 4, with a single VCC?
   (Multi-node CAN network? Add `connector:can-usbc` + `pinout:can-2wire`.)
5. Is it named per section 5?
6. Record the chosen tokens in the idea's `interfaces:` frontmatter (#243).

The constraint-injection prompt (#246) automates steps 1-5 by prepending these
constraints to design-generation requests. The circuits inventory (#248) tracks
which primitives already satisfy this checklist so they can be reused as-is.
