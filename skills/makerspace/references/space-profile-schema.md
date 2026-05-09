# Space profile schema

## Table of contents

- Why YAML *and* markdown?
- Top-level structure
- Tools
- Materials
- Certifications
- Classes
- Optional top-level fields
- Markdown attachments
- Provenance and visibility
- Modeling real-world tool entries
- Adding a new space
- Example fragments

Every makerspace this skill knows about has a folder under `spaces/`.
The folder contains one `profile.yaml` and a few markdown attachments.
This doc is the canonical schema for `profile.yaml`.

## Why YAML *and* markdown?

`profile.yaml` carries **structured data** — lookups, filters, and
constraints the skill can reason over (does this tool exist? does the
user have this cert? is this material allowed?).

Markdown carries **prose** — long-form rules, class descriptions,
safety policies, hand-curated context the skill quotes from but
doesn't try to parse.

Keep the YAML lean. If a field would be a paragraph of prose, point
to a markdown file instead.

## Top-level structure

```yaml
# Required
slug: maker-nexus              # URL-safe, used as the folder name
name: Maker Nexus              # Human-readable name
location:
  city: Sunnyvale
  state: CA
  country: US
url: https://www.makernexus.org

# Required, but can be empty lists for a brand-new profile
tools: []
materials: []
certifications: []
classes: []

# Optional
hours:
  monday:  "open 24/7 to members"
  # ...
membership_tiers: []
notes_md: notes.md             # Pointer to long-form prose
safety_rules_md: safety-rules.md
materials_policy_md: materials-policy.md
classes_md: classes.md
certifications_md: certifications.md
tools_md: tools.md             # If tool entries below are summaries
                               # and the long-form lives here

# Optional — provenance
last_updated: 2026-05-07
last_updated_by: tony-koop
data_sources:
  - https://wiki.makernexus.org/equipment/   # If scraped
notebooklm_url: ""              # Optional NotebookLM brain pointer
```

## `tools` — the tool catalog

Every callable tool the skill might cite goes here. One entry per
distinct machine. If a shop has three identical 3D printers, they can
share an entry with a `count` field.

```yaml
tools:
  - id: cnc-onsrud-1            # Stable id used in cut lists, op-seq
    name: Onsrud 4-axis CNC router
    category: cnc-router        # One of the standard categories below
    location: woodshop
    specs:
      bed_size_in: [48, 96]
      max_z_in: 8
      spindle_hp: 5
      spindle_max_rpm: 24000
      tool_holder: ER32
      vacuum_table: true
    inventory:
      bits:
        - {type: compression-spiral, dia_in: 0.25, flutes: 2, qty: 4}
        - {type: ball-end, dia_in: 0.125, flutes: 2, qty: 2}
      tooling_notes: bring your own ¼" or smaller, shop owns the
        rest
    allowed_materials: [hardwood, plywood, mdf, hdpe, foam]
    banned_materials: [aluminum, steel, brass, ferrous]
    cert_required: cnc-router-cert
    reservation: required
    reservation_url: https://www.makernexus.org/reserve/onsrud
    notes_md_section: "#cnc-onsrud-1"   # Anchor in tools.md
```

`category` enumerates to one of:

```
cnc-router | laser-cutter | 3d-printer-fdm | 3d-printer-sla |
3d-printer-sls | mill-vertical | mill-horizontal | lathe-wood |
lathe-metal | bandsaw | tablesaw | jointer | planer | drum-sander |
spindle-sander | drill-press | mortiser | router-table | scroll-saw |
welder-mig | welder-tig | welder-stick | plasma-cutter | shear |
brake | english-wheel | sewing-machine-domestic |
sewing-machine-industrial | serger | embroidery-machine |
vinyl-cutter | heat-press | screen-printer | electronics-bench |
oscilloscope | function-generator | spectrum-analyzer | reflow-oven |
pick-and-place | pottery-wheel | kiln-electric | kiln-gas |
slip-casting-bench | photo-booth | spray-booth | hand-tools |
other
```

If your shop has a tool that doesn't fit, use `other` and explain in
`tools.md`.

## `materials` — the material catalog

Each row tells the skill what's allowed where. Most home shops can
skip this and the home-shop default profile fills in.

```yaml
materials:
  - id: baltic-birch-quarter
    name: Baltic birch plywood, ¼"
    category: plywood
    sheet_size_in: [60, 60]
    thickness_in: 0.25
    typical_cost_usd: 35
    available_in_shop: false   # Member-supplied
    allowed_on_tools: [cnc-onsrud-1, laser-trotec, bandsaw, tablesaw]
    notes: "Most members buy from MacBeath in Berkeley."
```

## `certifications` — what the user can be cleared on

```yaml
certifications:
  - id: cnc-router-cert
    name: CNC Router (Onsrud) Certification
    grants_access_to: [cnc-onsrud-1]
    granted_by_class: class-cnc-intro
    duration_hours: 4
    cost_usd: 125
    notes_md_section: "#cnc-cert"
```

## `classes` — the class catalog

```yaml
classes:
  - id: class-cnc-intro
    name: Intro to CNC Routing
    grants_certs: [cnc-router-cert]
    duration_hours: 4
    cost_usd: 125
    schedule_url: https://www.makernexus.org/classes/cnc-intro
    next_dates: [2026-05-15, 2026-06-12, 2026-07-10]
    notes_md_section: "#class-cnc-intro"
```

The skill treats `next_dates` as advisory — class schedules change.
When advising "next class is on X," include "(verify via the schedule
URL)."

## Markdown attachments

The skill expects (but doesn't require) these files in the same
folder:

| File | Purpose |
|------|---------|
| `tools.md` | Long-form tool descriptions, anchored by `id` |
| `materials-policy.md` | Plain-English material rules — what's banned where, why |
| `certifications.md` | What each cert covers, refresher policy, instructor names |
| `classes.md` | Class descriptions, prerequisites, who runs them |
| `safety-rules.md` | Shop-wide safety policy, PPE requirements, dust collection |
| `notes.md` | Anything else worth keeping (history, culture, inside jokes) |

The skill loads these on demand. Anchor headings to ids — e.g., a
section header `## #cnc-onsrud-1` in `tools.md` lets the YAML
reference a deep link.

## Adding a new space — recipe

```bash
cp -r spaces/_template spaces/<your-slug>
cd spaces/<your-slug>
# Edit profile.yaml — fill every "REQUIRED" field
# Edit tools.md, materials-policy.md, etc. as far as you have content
git add . && git commit -m "Add <space-name> profile"
```

If your shop runs DokuWiki, run `scripts/scrape_maker_nexus.py` after
adapting the parser — most DokuWiki equipment pages share a structure.

## Privacy

If your shop's profile contains member-only information, mark it:

```yaml
visibility: private
```

The skill respects this and won't suggest sharing the profile, won't
include it in any public artifact, and won't push it to a remote
without explicit user confirmation.

## Schema validation

`scripts/validate_packet.py --check-profile <slug>` walks the profile
and reports missing required fields, undefined tool ids referenced
elsewhere, materials banned on tools they're listed as `allowed_on`,
and other consistency issues.
