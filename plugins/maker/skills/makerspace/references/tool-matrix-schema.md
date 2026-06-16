# Tool-matrix schema (Alpha Workspace Compiler)

> **Source of truth.** As of the S8 decision (issue #219, 2026-06-15) the
> Alpha tool-matrix schema is **promoted into makerspace** and lives here.
> The Evolution Pipeline's *Alpha Workspace Compiler* (issue #206) consumes
> this schema; it does not define its own. See
> `references/tool-matrix-promotion-decision.md` for the rationale.

## What a tool-matrix is

A **tool-matrix** is a normalized, capability-oriented view of the
fabrication tools a user can actually reach, used to answer one question:

> *Given this master design, what can THIS person make on THIS equipment,
> and what has to be reslices / downgraded / split / outsourced?*

The Alpha Workspace Compiler reads a tool-matrix to downgrade a
high-fidelity master design to the user's local reality — reslice a part
to a printable shell, flatten a housing into laser-nested panels, or fall
back to make/order/buy/borrow when nothing local fits.

A tool-matrix is **derived from**, not a competitor to, the makerspace
space profile (`spaces/<slug>/profile.yaml`, see
`references/space-profile-schema.md`). The space profile is the rich,
human-curated inventory. The tool-matrix is the lean machine-readable
capability projection the compiler reasons over.

## Relationship to the space profile

```
spaces/<slug>/profile.yaml   →  (project)  →   tool-matrix
   rich inventory                                lean capability view
   tools[].specs / inventory                     process envelopes
   allowed/banned materials                      material gates
   certs, reservations, hours                    availability flags
```

Every tool-matrix entry **must** trace back to a `profile.yaml` `tools[].id`
(or be explicitly flagged `synthetic: true` for a hypothetical / planned
tool). This keeps one source of truth: edit the space profile, regenerate
the matrix.

## Schema

A tool-matrix is a YAML (or JSON) document. Keep it lean — it is meant to
be diffed and reasoned over, not read as prose.

```yaml
# tool-matrix.yaml
schema_version: 1                 # this schema's version
generated_from: maker-nexus       # space profile slug, or "home-shop-default"
generated_at: 2026-06-15
units: metric                     # metric | imperial — applies to all envelopes

processes:
  - id: laser-trotec-1            # MUST match a space-profile tools[].id …
    source_tool_id: laser-trotec-1   # … recorded explicitly here too
    process: laser-cut            # normalized process verb (enum below)
    category: laser-cutter        # mirrors space-profile category enum
    # The work envelope the compiler downgrades geometry into:
    envelope:
      x_mm: 600
      y_mm: 900
      z_mm: 0                     # 0 = 2D process (flat-pattern target)
      max_thickness_mm: 12
    # What this process can physically accept:
    materials_allow: [plywood, mdf, acrylic, hardboard]
    materials_ban: [metal, pvc, polycarbonate]
    tolerance_mm: 0.2             # achievable, not nominal
    # Availability / friction gates (from the space profile):
    availability:
      cert_required: laser-cert
      reservation: required
      cost_signal: low            # low | medium | high | per-quote
    synthetic: false              # true = planned/hypothetical, no real tool yet
    notes: "kerf ~0.2mm; engrave + cut in one pass"

  - id: cnc-onsrud-1
    source_tool_id: cnc-onsrud-1
    process: cnc-mill-3axis
    category: cnc-router
    envelope: {x_mm: 1219, y_mm: 2438, z_mm: 203, max_thickness_mm: 203}
    materials_allow: [hardwood, plywood, mdf, hdpe, foam]
    materials_ban: [aluminum, steel, brass, ferrous]
    tolerance_mm: 0.1
    availability: {cert_required: cnc-router-cert, reservation: required, cost_signal: medium}
    synthetic: false

  - id: fdm-prusa
    source_tool_id: fdm-prusa-mk4
    process: fdm-print
    category: 3d-printer-fdm
    envelope: {x_mm: 250, y_mm: 210, z_mm: 220, max_thickness_mm: 220}
    materials_allow: [pla, petg, abs, tpu]
    materials_ban: []
    tolerance_mm: 0.3
    availability: {cert_required: null, reservation: none, cost_signal: low}
    synthetic: false
```

### `process` enum

Normalized process verbs the compiler can route to. Each maps to one or
more space-profile `category` values.

```
laser-cut | laser-engrave | cnc-mill-3axis | cnc-mill-4axis |
cnc-mill-5axis | cnc-lathe-turn | fdm-print | sla-print | sls-print |
waterjet-cut | plasma-cut | sheet-brake-bend | sheet-shear |
manual-mill | manual-lathe | bandsaw-cut | tablesaw-cut |
router-table | drill | weld | sew | vinyl-cut | other
```

### Required fields per process row

| Field            | Why the compiler needs it                              |
|------------------|--------------------------------------------------------|
| `id`             | Stable handle, used in compiler trade-off reports      |
| `source_tool_id` | Traceability back to `profile.yaml` (or `synthetic`)   |
| `process`        | Routing — which downgrade strategy applies             |
| `category`       | Cross-check against space-profile category enum        |
| `envelope`       | The geometry budget downgrades must fit inside         |
| `materials_allow`/`materials_ban` | Material gate                         |
| `tolerance_mm`   | DFM check — can the design's tightest tolerance hold?  |

`availability`, `synthetic`, and `notes` are optional but recommended.

## Generating a tool-matrix

1. Start from a space profile (`spaces/<slug>/profile.yaml`) or the
   `home-shop-default` profile.
2. For each `tools[]` entry that performs a making process, emit one
   `processes[]` row, projecting `specs` → `envelope`, copying material
   gates, and normalizing the tool `category` to a `process` verb.
3. Carry `cert_required` / `reservation` into `availability`.
4. A hand / planned tool with no real inventory entry gets
   `synthetic: true` and no `source_tool_id`.
5. Validate: every non-synthetic `source_tool_id` resolves in the source
   profile; every `process` and `category` is in-enum; `envelope` units
   match the document `units`.

## How the Alpha Workspace Compiler uses it

- **Fit check:** does the master design's bounding geometry fit any
  process `envelope`? If not → reslice / split / flatten.
- **Material gate:** is the design material in some process'
  `materials_allow` and not in `materials_ban`? If not → substitute or
  outsource.
- **Tolerance gate:** is the design's tightest tolerance ≥ a process
  `tolerance_mm`? If not → escalate to a tighter process or order out.
- **Fallback:** when nothing local clears all three gates, hand off to
  `references/make-order-buy-borrow.md` (make/order/buy/borrow) and, for
  on-demand vendors, the Evolution Pipeline's Beta Vendor Broker.

## Versioning

This schema is versioned by the `schema_version` field (currently `1`) and
by the makerspace skill version. Breaking changes to field names or the
`process` enum bump both. The Evolution Pipeline pins the makerspace skill
version it was validated against.
