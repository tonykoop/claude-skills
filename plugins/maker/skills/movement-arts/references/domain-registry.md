# Domain Registry

Each domain is a JSON file in `domains/` following the motion-primitives schema (see `motion-primitives-import.md`).

## How the engine loads a domain

```python
import json
from scripts.sequencer import MovementSequencer

with open("plugins/maker/skills/movement-arts/domains/vinyasa.json") as f:
    domain = json.load(f)

seq = MovementSequencer(domain=domain)
routine = seq.compile(duration_min=60)
```

The sequencer reads:
- `domain.clock` → instantiates `BreathClock` or `BeatClock`
- `domain.objective` → maps to the registered `ObjectiveFn` (see `objective-functions.md`)
- `domain.primitives` → populates `ValidTransitionMachine`
- `domain.requires_clinical_review` → gates PT output

## Available domains

| File | Domain | Clock | Objective | Safety gate |
|---|---|---|---|---|
| `vinyasa.json` | vinyasa | breath 12bpm | breath_alignment | no |
| `hip_hop.json` | hip_hop | beat 90–110bpm/8ct | style_expression | no |
| `salsa.json` | salsa | beat 160–180bpm/8ct | style_expression | no |
| `ballet.json` | ballet | beat 60–100bpm/8ct | style_expression | no |
| `tai_chi.json` | tai_chi | breath slow-arc | breath_alignment | no |
| `capoeira.json` | capoeira | beat 3-count | style_expression | no |
| `kata.json` | kata | breath/embusen | force_output | no |
| `physical_therapy.json` | physical_therapy | breath | joint_safety | **YES** |

## Adding a new domain

1. Create `domains/<name>.json` following the schema in `motion-primitives-import.md`.
2. Ensure every primitive has at least one `valid_next` entry.
3. Set `clock.type` to `"beat"` or `"breath"`.
4. Set `objective` to one of: `style_expression`, `breath_alignment`, `force_output`, `joint_safety`.
5. Set `requires_clinical_review: true` for any domain with therapeutic safety implications.
6. Add a test in `tests/test_movement_arts_domain_<category>.py`.

## Domain JSON — required fields

```json
{
  "schema_version": 1,
  "domain": "<name>",
  "clock": { "type": "beat|breath", ... },
  "objective": "<objective_name>",
  "requires_clinical_review": false,
  "primitives": [
    {
      "id": "<kebab-case>",
      "name": "<human readable>",
      "weight_shift": "left|right|bilateral|unweighted",
      "facing": "north|south|east|west|any",
      "tempo_class": "slow|medium|fast",
      "energy_delta": 0.0,
      "duration_beats": 4,
      "valid_next": ["<id>", ...]
    }
  ]
}
```
