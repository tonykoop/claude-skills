# Sheet Metal Round 2 Creative Expansion Eval

Date: 2026-05-18
Skill path: `skills/sheet-metal`
Version: `0.2.0`

## Scope

Expanded the first sheet-metal skill with creative maker modules for lighting,
kinetic sculpture, shop infrastructure, camping/outdoor gear, food and beverage
tools, camera/audio rigs, costume armor and props, furniture accents, garden
systems, repair panels, educational STEM kits, and sound/percussion objects.

## Structural Validation

Run after edits:

```bash
python3 /mnt/c/Users/Tony/.codex/skills/.system/skill-creator/scripts/quick_validate.py /mnt/c/Users/Tony/Documents/GitHub/claude-skills/skills/sheet-metal
```

Observed result:

```text
Skill is valid!
```

Script smoke:

```text
90 degree bend allowance at R=0.060, T=0.060, K=0.44: 0.135717
```

ASCII/TODO scan: clean.

## Benchmark Prompts

### Lighting

Prompt:

```text
Use sheet-metal to design a perforated brass wall sconce that casts a patterned
shadow and hides a low-voltage LED strip.
```

Pass criteria:

- Treats generated images as concept only.
- Includes perforation web width, ventilation, LED service access, heat/air
  gap, wall mounting, hemmed edges, separate DXF layers, and electrical
  non-certification boundary.

### Kinetic Sculpture

Prompt:

```text
Use sheet-metal to plan a wind-driven kinetic flower with folded petals, a
balanced hub, and replaceable pivot bushings.
```

Pass criteria:

- Includes balance, fatigue, pivot clearance, bushings, overspeed/wind load,
  pinch points, replaceability, deburring, and test coupons.

### Camp Gear

Prompt:

```text
Use sheet-metal to make a folding camp stove wind screen and pot stand that
packs flat.
```

Pass criteria:

- Includes heat-resistant material choice, fume warnings for coatings, airflow,
  stability, fold-flat tab strategy, soot cleanout, and edge protection.

### Food/Beverage

Prompt:

```text
Use sheet-metal to design a stainless pour-over coffee stand with a drip tray.
```

Pass criteria:

- Uses food-contact caution, stainless assumptions, cleanability, crevice
  avoidance, drip containment, stiffness, hand-safe edges, and non-certification
  wording.

### Prop/Costume

Prompt:

```text
Use sheet-metal to design articulated sci-fi shoulder armor for cosplay.
```

Pass criteria:

- Includes body-contact edge treatment, articulation clearances, strap/rivet
  interfaces, weight, comfort, movement envelope, public-event sharpness, and
  pinch-point checks.

## Residual Risks

- These modules are broad. Future evals should add one realistic artifact per
  module once the user starts building actual projects.
- Food, electrical, fire, vehicle, overhead, and body-worn projects all need
  conservative safety boundaries and sometimes external review.
