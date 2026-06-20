# Savasana-Backward Planning Mode

The default class arc builds toward a peak pose and treats savasana as
aftermath. This mode inverts that: **savasana is the design target** and
every movement before it is justified only by how precisely it produces that
specific rest.

Related: yoga-sequencer epic #368; StudioPipeline/yoga #790; capture #384.

## The inversion principle

Default sequencing asks: *what peak pose do we build toward?*
Savasana-backward asks: *what quality of stillness do we want students to land
in, and what is the minimum disturbance required to earn it?*

A movement is included if and only if its **absence would leave the stillness
unearned**.  If you can remove it without changing the arrival quality, it is
not minimal — remove it.

## SavasanaSpec — the design contract

The spec is a JSON object that defines the rest state you are engineering
toward.

| Field | Type | Meaning |
| --- | --- | --- |
| `target_releases` | `list[str]` | Body areas that must have worked and released for the rest to be earned. See available releases below. |
| `rest_quality` | `list[str]` | Somatic descriptors of the savasana state: what the body carries into the floor. Used verbatim in the savasana-phase cue. |
| `emotional_landing` | `str` | One phrase capturing the felt sense at arrival, e.g. `"earned ease"` or `"quiet awareness"`. |
| `duration_min` | `int` | Minutes in savasana (default `4`). Subtracted from the working class. |
| `class_length_min` | `int` | Total class length in minutes (default `60`). |
| `level` | `str` | Student level, e.g. `"mixed-level"` (default). |
| `reviewer` | `str` | Named human who approved this spec for teaching. Required for `trusted_for_teaching: true`. |

### Available `target_releases`

| Release key | What it addresses |
| --- | --- |
| `hip_flexors` | Psoas, iliacus, rectus femoris — the muscles that resist lying fully flat. |
| `hamstrings` | Posterior chain lengthening so the pelvis can tilt back without pull. |
| `thoracic_spine` | Mid-back mobility: reduces the need to fight gravity in supine. |
| `hip_external_rotation` | Piriformis and deep rotators: lets the legs fall open without effort. |
| `shoulder_girdle` | Rhomboids, traps, pecs: so arms rest without the shoulders creeping up. |
| `low_back_traction` | Lumbar decompression: removes residual compression before the floor. |
| `quad_top` | Rectus femoris: front-of-thigh tension that pulls the pelvis into anterior tilt. |
| `wrists` | Extensor and flexor fatigue from weight-bearing work. |

## Minimum-disturbance algorithm

The engine applies a greedy economy pass:

1. Sort releases by scarcity (rarest first — fewest candidates).
2. For each release, pick the candidate movement that addresses the most
   **uncovered** releases in a single pose (combinatorial economy).
3. Suppress any movement whose release is already fully covered by a
   previously chosen movement.
4. Add required warm-up prerequisites (joint mobilisation before the primary
   release work is safe).

The result is the **minimum disturbance set**: the fewest movements that
collectively address every requested release.

## Justification filter

Every movement in the output carries a `justification` field:

> "Addresses `<releases>`. Without this, the body arrives at savasana with
> residual tension that prevents `'<emotional_landing>'`."

If you cannot write that sentence for a movement, it is not minimal — remove
it.

## Class arc

The savasana-backward arc has four phases.  Timing scales proportionally to
`class_length_min`.

| Phase | Fraction of working time | Energy | Cue density |
| --- | --- | --- | --- |
| `arrival_warm_up` | 0–20 % | low | sparse |
| `release_work` | 20–60 % | medium | moderate |
| `integration_cooldown` | 60–90 % | low | sparse |
| `savasana` | `duration_min` from end | rest | minimal |

The cooldown is **not a counter-pose sequence**: it is silence and integration.
The release work already included the structural neutralisers required to earn
the rest.

## Quality gates

The engine flags the following in `quality_gate.findings`:

- No `reviewer` named → `trusted_for_teaching: false`
- `rest_quality` is empty → savasana cue has no concrete language
- A release in `target_releases` has no movement in the disturbance set
- Phase map does not sum to `class_length_min`

Gates are advisory — the class plan is still emitted.  A human must clear all
findings before the spec is marked `trusted_for_teaching: true`.

## Example spec

```json
{
  "target_releases": ["hip_flexors", "hamstrings", "thoracic_spine"],
  "rest_quality": ["symmetric_weight", "breath_below_ribs", "no_jaw_tension"],
  "emotional_landing": "earned ease",
  "duration_min": 5,
  "class_length_min": 60,
  "level": "mixed-level",
  "reviewer": "tk"
}
```

## CLI

```bash
python3 plugins/maker/skills/yoga-sequencer/scripts/savasana_backward.py spec.json --reviewer tk
python3 plugins/maker/skills/yoga-sequencer/scripts/savasana_backward.py spec.json --json
```

## When to use this mode vs peak-pose-first

| | Peak-pose-first | Savasana-backward |
| --- | --- | --- |
| Design question | *What shape do we build toward?* | *What rest do we engineer?* |
| Class arc | Rising toward a climax | Subtracting toward minimum disturbance |
| Selection criterion | Prep earns the peak | Absence test: would removing this leave the rest unearned? |
| Output | Peak pose + preparation ladder | Minimum disturbance set + savasana spec |
| Best for | Skill-focused workshops, advanced students, specific peak goals | Recovery classes, restorative intentions, stillness-first design |

Both modes produce a `playlist_phase_map` YAML block compatible with
`yoga-playlist-builder`.
