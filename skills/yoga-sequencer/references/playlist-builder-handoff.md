# Playlist Builder Handoff

Use this reference when the user wants music or says "now build music for this class."

## Intent

`yoga-sequencer` defines the class arc and timing. `yoga-playlist-builder` picks tracks that match each phase.

Do not generate music selections here. Instead, export a clean phase map that another skill can consume.

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

- `energy` should describe musical intensity, not pose difficulty alone.
- `cue_density` helps the playlist skill distinguish sparse teaching sections from more rhythmic flow sections.
- Keep `start_min` and `end_min` contiguous so the total plan covers the class cleanly.
- If the sequence uses breath counts instead of exact minutes, convert them into approximate phase timing before handoff.

## Export rules

- Include only the phases the playlist skill needs.
- Keep names human-readable.
- If the class is shorter than 60 minutes, compress proportionally rather than deleting the cooldown.
- If the user wants music for a subset, export only those phases and say the rest were omitted on purpose.
