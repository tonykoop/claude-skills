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

- `energy` should describe musical intensity, not pose difficulty alone.
- `cue_density` helps the playlist skill distinguish sparse teaching sections from more rhythmic flow sections.
- Keep `start_min` and `end_min` contiguous so the total plan covers the class cleanly.
- If the sequence uses breath counts instead of exact minutes, convert them into approximate phase timing before handoff.

## Export rules

- Include only the phases the playlist skill needs.
- Keep names human-readable.
- If the class is shorter than 60 minutes, compress proportionally rather than deleting the cooldown.
- If the user wants music for a subset, export only those phases and say the rest were omitted on purpose.
