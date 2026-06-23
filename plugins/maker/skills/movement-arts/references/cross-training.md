# Cross-Training Generator

`CrossTrainingGenerator` composes two or more movement domains into a single interleaved routine. All domains share one tracker and one `ValidTransitionMachine`, so weight/facing rules are enforced across the domain boundary.

## Usage

```python
import json
from scripts.cross_training import CrossTrainingGenerator

with open("domains/vinyasa.json") as f: vinyasa = json.load(f)
with open("domains/capoeira.json") as f: capoeira = json.load(f)

gen = CrossTrainingGenerator(
    domains=[vinyasa, capoeira],
    weights={"vinyasa": 0.5, "capoeira": 0.5},
    duration_min=45,
)
routine = gen.compile()
print(routine.to_dict())
```

## Named presets

```python
from scripts.cross_training import make_generator_from_preset, list_presets

print(list_presets())  # ['martial-beats', 'vinyasa-capoeira']

gen = make_generator_from_preset(
    "vinyasa-capoeira",
    domain_lookup={"vinyasa": vinyasa, "capoeira": capoeira},
    duration_min=45,
)
routine = gen.compile()
```

### Available presets

| Preset | Domains | Clock | Objective | Description |
|---|---|---|---|---|
| `vinyasa-capoeira` | vinyasa + capoeira | breath | breath_alignment | Flowing yoga + capoeira esquivas on a shared breath arc |
| `martial-beats` | hip_hop + kata | beat | force_output | Hip-hop groove with kata kime bursts |

## Output: CrossTrainingRoutine

```json
{
  "preset": "vinyasa-capoeira",
  "domains": ["vinyasa", "capoeira"],
  "weights": {"vinyasa": 0.5, "capoeira": 0.5},
  "duration_min": 45.0,
  "clock_type": "BreathClock",
  "objective": "BreathAlignmentObjective",
  "blocks": [
    {
      "domain": "vinyasa",
      "primitive_id": "mountain",
      "primitive_name": "Mountain Pose",
      "duration_s": 90.0,
      "energy": 0.12,
      "cue_density": "sparse",
      "weight_shift": "bilateral",
      "facing": "north"
    },
    ...
  ],
  "tracker_final_state": { ... }
}
```

Each block includes `"domain"` so downstream consumers can apply domain-specific formatting (verbal cue templates, audio BPM).

## Cross-domain state machine

Transitions across the domain boundary are filtered by the shared `ValidTransitionMachine` which pools all primitives from all domains. This means:
- A capoeira `au` (unweighted) correctly blocks a vinyasa `warrior_i` (single-foot load) as the immediate next block
- Weight distribution and facing direction are tracked continuously across domain switches

## Adding a preset

Edit `_PRESETS` in `scripts/cross_training.py`:

```python
_PRESETS["my-preset"] = {
    "domains": ["hip_hop", "ballet"],
    "weights": {"hip_hop": 0.6, "ballet": 0.4},
    "clock": "beat",
    "objective": "style_expression",
    "description": "Hip-hop bounce meets ballet barre",
}
```

Domains must be registered in `domains/<name>.json`.
