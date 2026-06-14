# Benchmarks And Versioning

Use this file when updating `sheet-metal`, copying it between runtimes, or
checking that the skill still behaves like the surrounding agentic skills.

## Cross-Platform Skill Shape

Follow the current cross-runtime pattern used by the nearby skills:

- Keep `SKILL.md` frontmatter validator-compatible with `name` and
  `description`.
- Put canonical version metadata in `manifest.yaml`.
- Include `agents/openai.yaml` for Codex UI display metadata.
- Put bulky domain detail in one-level `references/` files linked directly
  from `SKILL.md`.
- Put deterministic repeated calculations in `scripts/`.
- Add tests only for scripts or strict contracts that can be verified locally.
- Add `evals/round-N-eval.md` for behavior and benchmark notes.
- Avoid new root `README.md`, `CHANGELOG.md`, or installation docs unless the
  user explicitly asks for repo documentation outside the runtime skill.

This is the compromise visible across `makerspace`, `maker-engineering`,
`skills-meta`, `laser-art`, and related skills: runtime skills stay lean while
repo-side manifests and eval notes carry version and benchmark context.

## Versioning Shape

Use semantic versions in `manifest.yaml`:

- `0.1.0`: first coherent cross-platform sheet metal skill
- `0.2.0`: creative maker expansion modules for lighting, kinetic sculpture,
  shop/camp gear, food/beverage tools, creator rigs, props, furniture, garden,
  repair, STEM, and percussion
- patch versions: corrections, reference refinements, benchmark updates, typo
  fixes, or compatibility changes

On every versioned update:

1. Update `manifest.yaml`.
2. Keep `SKILL.md` trigger description current.
3. Update `agents/openai.yaml` if the user-facing prompt or summary changes.
4. Add or update an eval note under `evals/`.
5. Run structural validation.
6. Run script tests when scripts changed.
7. Copy/sync the repo version into the active runtime install root.

## Benchmark Shape

Each eval should include:

- date and skill path
- structural validation command and result
- YAML/frontmatter parse result
- script test command and result, when scripts exist
- prompt fixtures
- expected behavior
- observed behavior
- pass/fail
- residual risks

Prefer contract-level benchmarks that prove routing, boundaries, and output
shape. Use model-in-the-loop forward tests when available, but keep the prompt
fixtures useful even when a sandbox blocks external execution.

## Round 1 Prompt Fixtures

### Modular Toolbox

Prompt:

```text
Use sheet-metal to design a 20 x 10 x 8 inch modular toolbox for bike spares:
rim tape, tubes, grease, small lights, brushes, and stems. I want drop-in trays
and a clamshell lid.
```

Expected:

- Use the 20 x 10 x 8 platform.
- Ask or assume material/thickness and mark assumptions.
- Include tub/lid/tray parameters, safe rim/hem plan, storage archetypes,
  divider strategy, bend order, DXF checks, and open measurements.

### Horn Segment

Prompt:

```text
Use sheet-metal to plan the flat pattern and shop workflow for a rolled brass
bugle bell segment. I care about SolidWorks Lofted Bend and avoiding a lumpy
seam.
```

Expected:

- Route acoustic bore/tuning to `instrument-maker`.
- Keep this skill on lofted bend, blank segmentation, seam witness marks,
  annealing, rolling, brazing/TIG choice, and planishing.

### Beetleweight Chassis

Prompt:

```text
Use sheet-metal for a 3 lb beetleweight wedge chassis with folded aluminum
armor, guarded wheels, and fast service access.
```

Expected:

- Load combat robotics reference.
- Include weight budget, material warning, bend radius, sloped armor, wheel
  guards, service panel fastening, electronics shock mounting, and script-based
  weight estimate suggestion.

### Electronics Enclosure

Prompt:

```text
Use sheet-metal to design a Mini-ITX cyberdeck enclosure with ventilation,
grounding, and plasma-cut panels.
```

Expected:

- Require exact component models before fabrication-ready hole patterns.
- Include ventilation web-width rules, grounding, cable edge protection, service
  access, DXF layers, and generated-image non-authority if visuals are used.

### RAV4 Roof Rack

Prompt:

```text
Use sheet-metal to plan a flat roof rack for a 2024 Toyota RAV4 Prime so I can
carry a ShiftPod and lumber.
```

Expected:

- Treat as safety-sensitive vehicle work.
- Route to `maker-engineering` safety gate before final build claims.
- Provide only provisional sheet metal geometry planning unless measured
  vehicle interfaces, load cases, OEM ratings, and validation plan are supplied.

### Stacked Wood-Metal Art

Prompt:

```text
Use sheet-metal to make a Gabriel Schama-inspired stacked wood and brass wall
piece with registration pins.
```

Expected:

- Route laser-specific material/vector settings to `laser-art`.
- Include layer offsets, registration holes, material stack, vector authority,
  and test-coupon guidance.

## Round 2 Prompt Fixtures

### Lighting And Shadow

Prompt:

```text
Use sheet-metal to design a perforated brass wall sconce that casts a patterned
shadow and hides a low-voltage LED strip.
```

Expected:

- Load creative maker expansion plus shop DFM guardrails.
- Separate sheet metal shade/bracket design from electrical certification.
- Include perforation web width, heat/air gap, service access, mounting, safe
  edges, finish, and vector authority.

### Kinetic Sculpture

Prompt:

```text
Use sheet-metal to plan a wind-driven kinetic flower with folded petals, a
balanced hub, and replaceable pivot bushings.
```

Expected:

- Include balance, fatigue, pivot clearance, guards, wind load, deburring,
  bearing/bushing choice, and test coupons.

### Camp Gear

Prompt:

```text
Use sheet-metal to make a folding camp stove wind screen and pot stand that
packs flat.
```

Expected:

- Include heat-resistant material, hinge/tab strategy, airflow, sharp-edge
  control, soot/cleaning, stability, and burn/fire stop-work warnings.

### Food Tool

Prompt:

```text
Use sheet-metal to design a stainless pour-over coffee stand with a drip tray.
```

Expected:

- Include food-contact material cautions, cleanability, crevice avoidance,
  stainless finish, drip containment, stiffness, and non-certification wording.

### Costume Prop

Prompt:

```text
Use sheet-metal to design articulated sci-fi shoulder armor for cosplay.
```

Expected:

- Include body-safe edges, articulation clearances, strap/rivet interfaces,
  weight, comfort, movement envelope, finish, and pinch-point checks.

## Local Commands

Structural validation:

```bash
python3 /mnt/c/Users/Tony/.codex/skills/.system/skill-creator/scripts/quick_validate.py /mnt/c/Users/Tony/Documents/GitHub/claude-skills/skills/sheet-metal
```

Script smoke tests:

```bash
python3 /mnt/c/Users/Tony/Documents/GitHub/claude-skills/skills/sheet-metal/scripts/sheet_metal_math.py bend-allowance --angle-deg 90 --radius 0.06 --thickness 0.06 --k-factor 0.44
python3 /mnt/c/Users/Tony/Documents/GitHub/claude-skills/skills/sheet-metal/scripts/sheet_metal_math.py cylinder-blank --diameter 6 --height 12 --trim-margin 1.5
python3 /mnt/c/Users/Tony/Documents/GitHub/claude-skills/skills/sheet-metal/scripts/sheet_metal_math.py combat-budget --class beetleweight
```
