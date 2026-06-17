# Functional Tagging Schema

Story #243 of the Cross-Pollination Engine (epic #236). This file defines the
controlled vocabulary and YAML frontmatter spec applied to **every idea at
intake**. It is the backbone the rest of the epic builds on: MOC dashboards
(#244), the Universal Interface guide (#245), the constraint-injection prompt
(#246), the Cross-Pollination Agent (#247), and the circuits inventory (#248)
all key off the `functions:` / `interfaces:` / `materials:` facets defined here.

## Why functional tags

The incubator was a linear conveyor belt: capture -> connect -> promote. Tags
turn it into a semantic web. The moment two ideas share a function such as
`transmit-torque` or `index-detent`, the agent can notice that a mechanism
already solved for one gadget is the exact fit another gadget needs. Tags are
the shared vocabulary that makes that match cheap and reliable, even for
substring-matching agents (Codex, Gemini CLI) that cannot run embeddings.

## Where the tags live

Tags live in a YAML frontmatter block. The same block works in two places:

- **GitHub issue body** - a fenced ```yaml block at the top of the issue body
  (the durable layer). GitHub does not render frontmatter natively, so fence it.
- **Obsidian note** - real `---` frontmatter at the top of the markdown note
  (the vault layer), so Dataview (#244) can query it.

Author the block once; paste it into both layers. Keep keys identical so the
Cross-Pollination Agent can join issue inbox and vault by tag.

## Frontmatter spec

```yaml
---
# --- identity (required) ---
idea: "detent-locking telescoping leg"   # short human title
id: idea-0142                            # stable slug or issue ref (#142)
status: capture                          # capture | connect | review | promote | built
domain: maker                            # maker | instrument | yoga | skills | general
captured: 2026-06-16                      # YYYY-MM-DD

# --- functional facets (functions REQUIRED, >=1) ---
functions:                               # what the subassembly DOES (controlled vocab)
  - index-detent
  - tension
interfaces:                              # how it CONNECTS to neighbors (optional)
  - mount:t-slot-2020
  - fastener:m5
materials:                               # what it is MADE OF (optional)
  - aluminum-6061
  - pla

# --- reuse hints (optional) ---
solved-in: tonykoop/sambuca#88           # repo/issue where this was already solved
reuses: idea-0097                        # this idea borrows a primitive from another
maturity: concept                        # concept | sketch | proto | built | shipped
---
```

### Required vs optional

| Field | Required | Notes |
|---|---|---|
| `idea` | yes | Human-readable title. |
| `id` | yes | Stable handle: a slug or `#N` issue ref. |
| `status` | yes | Mirrors the workflow labels in `label-schema.md`. |
| `domain` | yes | Mirrors the domain labels in `label-schema.md`. |
| `captured` | yes | ISO date. |
| `functions` | yes | At least one value from the controlled vocab below. |
| `interfaces` | no | Add when the idea has a known mating surface. |
| `materials` | no | Add when material choice is part of the idea. |
| `solved-in` | no | Back-link to a repo/issue that already solved this. |
| `reuses` | no | Forward-link to a primitive this idea borrows. |
| `maturity` | no | Defaults to `concept` if omitted. |

If the user has not said enough to fill `functions`, do **not** guess. Add the
`needs-clarification` label and ask which function(s) the mechanism performs.
A wrong function tag is worse than a missing one because it produces false
cross-pollination matches.

## Controlled vocabulary: `functions:`

Functions describe the **verb** of a subassembly - the mechanical or electrical
job it does, independent of the specific gadget. Use the canonical token on the
left. Synonyms map to the canonical token so different agents converge.

| Canonical token | Meaning | Synonyms to fold in |
|---|---|---|
| `fasten` | Hold two parts together removably or permanently | join, bolt, screw |
| `hinge` | Allow constrained rotation about one axis | pivot, swing |
| `damp` | Absorb or dissipate vibration/shock/energy | dampen, isolate, cushion |
| `seal` | Block fluid/gas/dust across a boundary | gasket, o-ring |
| `waterproof` | Maintain seal under submersion/spray | weatherproof, ip-rated |
| `transmit-torque` | Carry rotational force shaft-to-shaft | couple, drive, gear |
| `transmit-linear` | Carry linear force/motion | actuate, push-pull |
| `tension` | Maintain or adjust a pulling force | tighten, preload, string |
| `compress` | Maintain or adjust a pushing force | spring-load, clamp-force |
| `index-detent` | Snap to discrete repeatable positions | detent, click-stop, indexing |
| `latch` | Releasable hold that resists opening | catch, snap-lock |
| `lock` | Positively prevent motion until released | secure, lockout |
| `mount` | Provide a reference surface/pattern for attaching | bracket, fixture-point |
| `align` | Constrain relative position during assembly | locate, register, dowel |
| `route-cable` | Guide and retain wiring/tubing | cable-manage, strain-relief |
| `route-fluid` | Guide liquid/air through a path | plumb, manifold |
| `adjust` | Provide fine continuous setting | trim, calibrate, set-screw |
| `support` | Bear static load along a path | hold, shelf, stand |
| `slide` | Allow low-friction translation | rail, linear-guide |
| `grip` | Apply friction to hold an object | clamp, chuck, jaw |
| `tune` | Set acoustic/resonant property | pitch, voice (instruments) |
| `transduce` | Convert energy domains (e.g. motion->signal) | sense, pickup, mic |
| `power` | Supply or regulate electrical energy | battery, psu, regulate |
| `switch` | Open/close an electrical or fluid path | toggle, valve, relay |

Add a new canonical token only when a function genuinely is not covered. When
you add one, add it here in the same PR and note it in the CHANGELOG so the
vocabulary stays the single source of truth across agents.

## Controlled vocabulary: `interfaces:`

Interfaces describe the **mating boundary** - the noun another subassembly
plugs into. They are `facet:value` pairs so they read cleanly and group well in
Dataview. Values should reference the Universal Interface guide (#245) once it
is adopted.

| Facet | Example values | Notes |
|---|---|---|
| `mount` | `t-slot-2020`, `vesa-75`, `hole-pattern-43x43` | Standard mounting pattern. |
| `fastener` | `m3`, `m5`, `1/4-20`, `heat-set-m3` | Thread/insert standard. |
| `connector` | `xt60`, `jst-ph`, `usb-c`, `grove` | Electrical/data connector. |
| `shaft` | `5mm-d`, `1/4-hex`, `8mm-round` | Rotational interface. |
| `tolerance` | `slip-h7`, `press-p7`, `clearance-loose` | Fit class (see #245). |
| `pinout` | `i2c-4pin`, `uart-3v3` | Signal convention. |

## Controlled vocabulary: `materials:`

Keep materials coarse; the goal is reuse matching, not a full BOM. Use lowercase
hyphenated tokens.

- `pla`, `petg`, `abs`, `asa`, `tpu`, `resin`
- `aluminum-6061`, `aluminum-7075`, `steel-mild`, `steel-stainless`, `brass`
- `plywood`, `hardwood`, `mdf`, `bamboo`
- `acrylic`, `polycarbonate`, `delrin`, `nylon`
- `silicone`, `rubber`, `foam`

## Worked examples

### Example 1 - mechanical idea

```yaml
---
idea: "spring-detent telescoping mic stand leg"
id: idea-0142
status: capture
domain: maker
captured: 2026-06-16
functions:
  - index-detent
  - slide
  - lock
interfaces:
  - shaft:8mm-round
  - fastener:m5
materials:
  - aluminum-6061
  - delrin
maturity: concept
---
```

This idea shares `index-detent` with any camera tripod, monopod, or adjustable
shelf idea in the inbox - the agent (#247) flags those as cross-pollination
candidates.

### Example 2 - instrument idea

```yaml
---
idea: "removable harp string-tension anchor block"
id: idea-0151
status: connect
domain: instrument
captured: 2026-06-16
functions:
  - tension
  - tune
  - mount
interfaces:
  - mount:hole-pattern-43x43
  - fastener:1/4-20
materials:
  - hardwood
  - brass
solved-in: tonykoop/brian-boru-harp-replica#12
maturity: proto
---
```

`tension` + `mount` here overlaps with the mic-stand leg's `tension` cousin and
with any string instrument anchor across the portfolio.

## Intake checklist

When capturing an idea, before saving the issue:

1. Write the identity block (`idea`, `id`, `status`, `domain`, `captured`).
2. Pick **at least one** `functions:` token from the controlled vocab. Fold
   synonyms into the canonical token.
3. Add `interfaces:` only if a mating boundary is actually known.
4. Add `materials:` only if material is part of the idea.
5. If you cannot name a function honestly, add `needs-clarification` and ask.
6. Paste the same block into both the GitHub issue and the Obsidian note.

The MOC dashboard (#244) and the Cross-Pollination Agent (#247) assume this
checklist was followed. Garbage tags in produce noisy suggestions out.
