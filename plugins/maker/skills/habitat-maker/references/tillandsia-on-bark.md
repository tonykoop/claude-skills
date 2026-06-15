# Tillandsia-on-bark sculpture (build-packet reference)

Botanical sculpture: air plants (*Tillandsia*) mounted on a bark or cork
substrate. Folded into `habitat-maker` as a **reference + example**, not a
standalone skill — see "Form decision" below. Originating issue: #45 (epic
#211).

## Form decision (why it lives here)

Issue #45 captured a one-off build idea ("Tillandsia on bark sculpture") and
explicitly left the home **TBD — own repo or `planters/` sub-folder**. It is a
reusable *build pattern*, not a reusable *skill*: it has no new trigger surface,
no new mode, and no new validation machinery beyond what `habitat-maker`
already provides for `planters` / `plant-supports`. Forcing a thin standalone
skill would duplicate habitat-maker's build-packet contract for one micro-line.

So:

- **Fabrication / mounting / build packet** lives here in `habitat-maker`,
  which already owns `planters` and `plant-supports` and emits build packets in
  the instrument-maker convention.
- **Tillandsia care, watering, the digital-twin of a living specimen** is owned
  by the `houseplant` skill (Tillandsia is part of Eugene's indoor-cultivation
  lineage). Route care questions there.
- If this micro-line ever grows its own catalog of designs, promote it to a
  `planters/tillandsia-on-bark/` sub-folder per the issue's own suggestion;
  this reference is the seed for that.

## What the build is

A mount, not a planter: Tillandsia are epiphytes with no soil. The bark/cork
is a display substrate the plant clings to; it is not a growing medium. The
sculpture's job is to hold the plant securely, stay safe for a living
epiphyte, and let the maker remove the plant for its periodic soak.

## Substrate options

| Substrate | Notes |
|---|---|
| Cork bark (virgin cork) | rot-resistant, light, classic; safe, no treatment |
| Grapewood / manzanita | sculptural, durable; rinse, no sealant on contact zones |
| Driftwood | only if salt-leached and fully dry; reject if salty or resinous |
| Live-edge hardwood offcut | ties into the woodworking offcut stream; seal only the *back* |

**Reject**: pressure-treated lumber, cedar/aromatic resinous woods in the
contact zone (oils can harm the plant), anything painted or finished where the
roots touch, and copper hardware (copper is toxic to Tillandsia).

## Welfare / safety gates (Tillandsia-specific)

These are pass/fail gates in the habitat-maker sense. See
`references/welfare-gate-schema.md` for the gate record shape.

1. **No copper contact.** No copper wire, fasteners, or copper-treated wood
   touches the plant. Use nylon, stainless, or coated/galvanized hardware, or
   plant-safe adhesive only.
2. **Removable for soaking.** The plant must be removable (or the whole piece
   submersible/wettable) so it can be soaked ~weekly and drained fully —
   standing water at the base rots the plant.
3. **No glue on the growing point.** If adhesive-mounting, glue contacts only
   the lower stem/roots, never the central crown. Prefer mechanical mounting
   (nestled in a crevice, tied with fishing line or coated wire) over glue.
4. **Drainage / no water trap.** The mount orientation must let water run off;
   no cupped pocket that holds water against the base.
5. **Light-honest placement note.** Packet states the light the chosen species
   needs (most Tillandsia want bright indirect light) — a display note, not a
   care service. Detailed care routes to `houseplant`.
6. **Mass / wall safety.** If wall-hung, the hanger is rated for the wet mass
   of substrate + soaked plant; route the hanger detail to `makerspace` if it
   needs a real fixture.

## Mounting methods (lowest-intervention first)

1. **Crevice nest** — wedge the plant into a natural hollow; no hardware. Best.
2. **Tie-down** — fishing line or coated/nylon-jacketed wire around the lower
   stem to the substrate; reversible, soak-friendly.
3. **Adhesive** — plant-safe waterproof adhesive (e.g. aquarium-grade silicone)
   on lower stem only; last resort, not removable.

## Build packet output

A Tillandsia-on-bark packet follows the habitat-maker build-packet contract for
a **non-cavity, non-digitally-driven** habitat (hand-mounted), so prose drawings
+ a dimensioned sketch are the artifact of record — no generator script is
required (no laser/CNC geometry). It must ship:

- `design.md` — substrate choice, species/light note, mounting method, mount
  orientation.
- `bill-of-materials.csv` — substrate, hardware (copper-free), adhesive if any,
  hanger.
- `validation-checklist.md` — the six gates above as pass/fail items.
- `agent-record.md` — assumptions, sources, what was inferred vs. stated.

See [`examples/tillandsia-on-cork-mount/`](../examples/tillandsia-on-cork-mount/)
for the canonical minimal packet.

## Cross-references

- `houseplant` — Tillandsia care, watering/soak schedule, specimen digital twin.
- `makerspace` — wall-hanger fixture if the mount needs a real bracket.
- `idea-incubator` #45 — origin capture; promote to `planters/tillandsia-on-bark/`
  if the micro-line grows.
