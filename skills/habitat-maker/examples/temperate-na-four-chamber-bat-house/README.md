# Canonical Example - Temperate North America Four-Chamber Bat House

This packet adds bat-house-specific habitat support to `habitat-maker`.
It is a builder-facing example for small-to-medium North American
crevice-roosting bats that may use artificial roosts.

The design is a tall four-chamber warm-season roost with climate/site
presets, explicit welfare gates, and generator-backed layout helpers.
It is not a generic birdhouse-derived box.

## Files

| File | Role |
|---|---|
| `geometry_params.json` | Single source of truth for dimensions, welfare gates, climate presets, mounting constraints, and references |
| `four-chamber-bat-house-layout.svg` | Generated layout sanity check; do not hand-edit |
| `generated-cut-list.csv` | Generated cut-list CSV; do not hand-edit |
| `cut-list.md` | Human-readable cut list and dimension notes |
| `BOM.md` | Bill of materials |
| `mounting-worksheet.md` | Site, climate, orientation, paired-house, and disallowed-placement worksheet |
| `validation-checklist.md` | Pass/fail welfare and deployment gates |
| `validation-report.schema.json` | Machine-readable validation report schema |
| `validation-report.json` | Example validation report for the default packet |
| `safety-notes.md` | Shop, finish, wildlife, and maintenance safety notes |
| `agent-record.md` | Provenance |

## Recommended Geometry

| Feature | Metric | Imperial |
|---|---:|---:|
| Overall width | 508 mm | 20 in |
| Back panel height | 914 mm | 36 in |
| Roost chambers | 4 | 4 |
| Clear chamber gap | 19 mm | 3/4 in |
| Landing extension | 152 mm | 6 in |
| Partition passage holes | 38 mm | 1-1/2 in |
| Minimum mount height | 3.7 m | 12 ft |
| Preferred mount height | 4.6-6.1 m | 15-20 ft |
| Minimum clear drop below exit | 3.7 m | 12 ft |

## Welfare Design Rules

- Four chambers are the default because taller multi-chamber houses provide
  more thermal choice than single-chamber boxes.
- Roost gaps stay in the 19-25 mm range; this packet uses 19 mm.
- All roost and landing surfaces are roughened with kerfs or dense grooves.
- Mesh, screen, and netting are forbidden on roost surfaces.
- Interior paint, stain, oil, and sealer are forbidden.
- Treated or chemically finished lumber is forbidden inside the roost.
- The bottom remains open; do not caulk it shut.
- Tree mounting is discouraged as the default because branches reduce sun,
  obstruct drop-flight, and can help predators reach the roost.
- Inspection or repair happens only when bats are absent.

## Climate And Site Presets

Use `geometry_params.json` to select a climate profile before building:

- `cool_to_mild`: dark exterior, 6-8+ hours direct sun.
- `warm`: medium exterior, morning to mid-day sun, vents required.
- `very_hot`: light exterior, afternoon shade or paired thermal options,
  and a site-specific overheating check.

When the site allows it, install two nearby houses with different color or
exposure so bats can shift between thermal conditions.

## Regenerate Generated Artifacts

From the repo root:

```bash
python3 skills/habitat-maker/scripts/generate_bat_house_packet.py \
  --packet skills/habitat-maker/examples/temperate-na-four-chamber-bat-house
```

The generator reads `geometry_params.json` and writes
`four-chamber-bat-house-layout.svg` plus `generated-cut-list.csv`.

## Validate

```bash
python3 -m unittest discover skills/habitat-maker/tests
```

The smoke tests parse the parameter file, confirm bat welfare gates, run
the generator in a temporary packet copy, parse the emitted SVG, and verify
the validation-report schema/report pair.
