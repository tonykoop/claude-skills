# Playlist Builder Handoff

Use this reference whenever you produce a full class plan, or whenever the user mentions music, playlists, or `yoga-playlist-builder`.

## Intent

`yoga-sequencer` defines the class arc and timing. The job here is to emit a portable phase map — a chunk of YAML the user can hand to `yoga-playlist-builder`, paste into another Claude session, or feed to any other music-selection tool.

The phase-map YAML is part of the contract for a complete class plan, not an optional add-on. SKILL.md's "When to include the playlist phase-map YAML" rule is the authoritative trigger list — emit the block whenever that rule says to. Skip it only for pure lookup requests (counter-pose, anatomical prep, single-pose modifications).

Always emit the YAML block inline in your reply. Do not assume `yoga-playlist-builder` (or any other companion skill) is installed on the platform the user is on right now — Claude Desktop, mobile zip uploads, Codex, and Gemini installations may all carry different skill sets. The block needs to stand on its own.

Do not generate music selections here.

## Handoff schema

```yaml
class_plan:
  style: vinyasa
  length_min: 60
  level: mixed-level
  theme: hip-opening with steady grounding
  peak_pose: crow
  overall_energy: warm -> focused -> lift -> settle
playlist_handoff:
  total_length_min: 60
  phases:
    - id: arrival
      label: Arrival and breath
      start_min: 0
      end_min: 5
      energy: low
      cue_density: sparse
      notes: settle, arrive, nasal breath
    - id: warmup
      label: Floor warm-up
      start_min: 5
      end_min: 15
      energy: low-medium
      cue_density: moderate
      notes: mobility, spinal articulation, wrist prep
    - id: build
      label: Standing flow and preparation
      start_min: 15
      end_min: 38
      energy: medium-high
      cue_density: rhythmic
      notes: repeated flows, side-to-side symmetry
    - id: peak
      label: Peak-pose work
      start_min: 38
      end_min: 46
      energy: high
      cue_density: focused
      notes: short attempts, clear exit option
    - id: cooldown
      label: Counterpose and floor release
      start_min: 46
      end_min: 55
      energy: low
      cue_density: sparse
      notes: downshift, recovery, integration
    - id: savasana
      label: Savasana
      start_min: 55
      end_min: 60
      energy: very-low
      cue_density: minimal
      notes: quiet landing
```

## Phase notes

- `energy` should describe musical intensity, not pose difficulty alone. Suggested values: `very-low`, `low`, `low-medium`, `medium`, `medium-high`, `high`.
- `cue_density` is **required** on every phase of a full-class plan. Allowed values: `sparse`, `moderate`, `rhythmic`, `focused`, `minimal`. See `references/sequencing-principles.md` ("Cue density across the arc") for the default arcs by class length and style.
- `cue_density` and `energy` are independent. The peak shape is often `high` energy + `focused` cue density (slow, alignment-only cueing). Sun B is often `medium-high` energy + `rhythmic` cueing (one cue per breath cycle). Do not collapse the two fields onto a single intensity scale — playlist-builder uses `cue_density` to avoid pairing lyric-dense tracks with phases where students need quiet for proprioception.
- Keep `start_min` and `end_min` contiguous so the total plan covers the class cleanly.
- If the sequence uses breath counts instead of exact minutes, convert them into approximate phase timing before handoff.

## Example: vinyasa class, 45 minutes

Use this shape when a user asks for a shorter-but-complete public vinyasa class. Compress the build and peak windows before compressing cooldown or savasana.

```yaml
class_plan:
  style: vinyasa
  length_min: 45
  level: mixed-level
  theme: steady legs and clear balance
  peak_pose: standing figure four
  overall_energy: arrive -> build heat -> focus -> settle
playlist_handoff:
  total_length_min: 45
  phases:
    - id: arrival
      label: Arrival and breath
      start_min: 0
      end_min: 4
      energy: low
      cue_density: sparse
      notes: land, set theme, steady breath
    - id: warmup
      label: Floor warm-up and mobility
      start_min: 4
      end_min: 12
      energy: low-medium
      cue_density: moderate
      notes: spinal mobility, hip wake-up, low lunge prep
    - id: build
      label: Standing flow and balance prep
      start_min: 12
      end_min: 29
      energy: medium-high
      cue_density: rhythmic
      notes: sun flow, chair, warrior II, side-to-side symmetry
    - id: peak
      label: Peak-pose work
      start_min: 29
      end_min: 35
      energy: high
      cue_density: focused
      notes: standing figure four, wall or toe-down option
    - id: cooldown
      label: Counterpose and floor release
      start_min: 35
      end_min: 42
      energy: low
      cue_density: sparse
      notes: reclined figure four, supine twist, hamstring release
    - id: savasana
      label: Savasana
      start_min: 42
      end_min: 45
      energy: very-low
      cue_density: minimal
      notes: short quiet landing
```

## Example: vinyasa class, 30 minutes

Use this shape for lunch-break, conference, or between-meetings classes. Keep one clear focal action and avoid adding a second peak.

```yaml
class_plan:
  style: vinyasa
  length_min: 30
  level: mixed-level
  theme: shoulder reset and simple flow
  peak_pose: humble warrior prep
  overall_energy: arrive -> mobilize -> flow -> downshift
playlist_handoff:
  total_length_min: 30
  phases:
    - id: arrival
      label: Arrival and breath
      start_min: 0
      end_min: 3
      energy: low
      cue_density: sparse
      notes: settle, shoulder awareness, breath pacing
    - id: warmup
      label: Shoulder and spine warm-up
      start_min: 3
      end_min: 8
      energy: low-medium
      cue_density: moderate
      notes: cat-cow, thread the needle, low lunge reach
    - id: build
      label: Simple standing flow
      start_min: 8
      end_min: 20
      energy: medium-high
      cue_density: rhythmic
      notes: crescent, warrior II, side angle, repeat both sides
    - id: peak
      label: Focal shoulder work
      start_min: 20
      end_min: 24
      energy: medium
      cue_density: focused
      notes: humble warrior prep, hands to low back or strap option
    - id: cooldown
      label: Counterpose and release
      start_min: 24
      end_min: 28
      energy: low
      cue_density: sparse
      notes: child's pose, seated twist, neck and shoulder release
    - id: savasana
      label: Savasana
      start_min: 28
      end_min: 30
      energy: very-low
      cue_density: minimal
      notes: brief rest
```

## Example: yin class, 60 minutes

```yaml
class_plan:
  style: yin
  length_min: 60
  level: mixed-level
  theme: hip and shoulder release
  peak_pose: supported saddle
  overall_energy: settle -> long holds -> integrate -> rest
playlist_handoff:
  total_length_min: 60
  phases:
    - id: arrival
      label: Arrival and propping
      start_min: 0
      end_min: 6
      energy: very-low
      cue_density: sparse
      notes: settle, set up bolsters and blocks
    - id: hold_1
      label: First long hold (caterpillar / butterfly)
      start_min: 6
      end_min: 18
      energy: low
      cue_density: sparse
      notes: shape set in first minute, then quiet; one prop reminder mid-hold
    - id: transition_1
      label: Transition and reset
      start_min: 18
      end_min: 22
      energy: low
      cue_density: moderate
      notes: mobilize between holds, brief setup language
    - id: hold_2
      label: Second long hold (sphinx / seal)
      start_min: 22
      end_min: 34
      energy: low
      cue_density: sparse
      notes: anterior-chain release; let the shape teach
    - id: hold_3
      label: Third long hold (supported saddle, peak)
      start_min: 34
      end_min: 46
      energy: low
      cue_density: sparse
      notes: heavily propped; teacher voice is minimal once students are in
    - id: integration
      label: Reclined integration (twists, knees-to-chest)
      start_min: 46
      end_min: 55
      energy: very-low
      cue_density: sparse
      notes: counter the long holds with gentle reset
    - id: savasana
      label: Savasana
      start_min: 55
      end_min: 60
      energy: very-low
      cue_density: minimal
      notes: quiet landing
```

## Export rules

- Include only the phases the playlist skill needs.
- Keep names human-readable.
- If the class is shorter than 60 minutes, compress proportionally rather than deleting the cooldown.
- If the user wants music for a subset, export only those phases and say the rest were omitted on purpose.
