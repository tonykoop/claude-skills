# Cue Output Format

`CueFormatter` converts a `CompiledRoutine` into consumer-specific output formats.

## Usage

```python
import json
from scripts.sequencer import MovementSequencer
from scripts.cue_output import CueFormatter

with open("domains/hip_hop.json") as f:
    domain = json.load(f)

seq = MovementSequencer(domain=domain)
routine = seq.compile(45.0)

formatter = CueFormatter(routine, domain)

# pick a format:
verbal      = formatter.format("verbal")
audio_handoff = formatter.format("audio_energy")
```

## Format: `"verbal"` (default)

Instructor script — one entry per block.

```json
{
  "block_index": 0,
  "primitive_id": "neutral_bounce",
  "primitive_name": "Neutral Bounce",
  "duration_s": 90.0,
  "energy_level": "low",
  "cue_density": "sparse",
  "instructor_cue": "We begin: on count 1, neutral bounce — distribute weight evenly through both feet."
}
```

- `energy_level`: one of `rest / low / moderate / high / peak`
- `instructor_cue`: ready-to-speak text combining movement name, weight cue, facing cue, and count anchor

## Format: `"audio_energy"`

Playlist-builder handoff — consumed by the DJ / audio-energy agent.

```json
{
  "block_index": 2,
  "block_id": "two_step",
  "energy_level": "moderate",
  "energy_raw": 0.421,
  "bpm_target": 100.0,
  "cue_density": "rhythmic",
  "duration_s": 75.0
}
```

- `bpm_target`: mid-point of the domain's `bpm_range` (or the scalar `bpm` for breath clocks)
- Every block has a `bpm_target` — this field is guaranteed present

## Format: `"pt_biomechanical"`

Compensation cue layer for physical therapy routines (only meaningful for `physical_therapy` domain).

```json
{
  "block_index": 5,
  "primitive_id": "step_up_left",
  "primitive_name": "Step Up — Left Leg Leading",
  "duration_s": 45.0,
  "energy_level": "moderate",
  "velocity_cap_m_per_s": 0.3,
  "unilateral_load": true,
  "ROM_target_deg": 60,
  "compensation_cues": [
    "monitor asymmetry — stop if compensating",
    "target ROM: 60° — do not force end-range",
    "single-limb load on left — brace core"
  ]
}
```

- `compensation_cues`: list of strings ready to read aloud or display in UI
- `velocity_cap_m_per_s` / `unilateral_load` / `ROM_target_deg`: raw domain values, pass-through
- When using `pt_biomechanical` on a non-PT domain, `velocity_cap_m_per_s` / `ROM_target_deg` will be `null` and `compensation_cues` may be empty

## Guard: verbal output excludes PT biomechanical fields

When `format="verbal"` is called on a PT routine, the output contains no PT-specific fields
(`velocity_cap_m_per_s`, `unilateral_load`, `ROM_target_deg`, `compensation_cues`).
Use `format="pt_biomechanical"` explicitly to access those.

## Adding a new format

1. Add the new name to `_FORMAT_TYPES` in `cue_output.py`.
2. Add `_fmt_<name>(self, idx, block) -> dict` method.
3. Add tests in `tests/test_movement_arts_cue_output.py`.
