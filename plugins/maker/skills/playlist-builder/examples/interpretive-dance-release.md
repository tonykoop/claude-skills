# Worked Example — Interpretive Dance Release Bundle

**Epic:** #471 — playlist-builder audio-dynamic  
**Story:** #476  

This document walks through one end-to-end execution of the audio-dynamic pipeline for a
hip-hop interpretive dance routine, from movement payload → mix plan → release bundle.

---

## Input: MovementRoutinePayload

A 4-block, 8-minute hip-hop routine targeting the 95–100 BPM sweet spot.

```json
{
  "routine_id": "hip-hop-interpretive-2026-06-22",
  "style": "hip-hop",
  "total_duration_s": 480,
  "source_engine": "movement_arts@1.0.0",
  "blocks": [
    {
      "name": "Warm-up",
      "bpm_target": 80,
      "bpm_range": [72, 88],
      "duration_s": 120,
      "energy": 0.25,
      "kinetic_texture": "fluid",
      "notes": "Slow groove, spine rolls and level changes"
    },
    {
      "name": "Groove Build",
      "bpm_target": 92,
      "bpm_range": [88, 98],
      "duration_s": 120,
      "energy": 0.50,
      "kinetic_texture": "fluid+grounded",
      "notes": "Rising footwork, weight-down isolations"
    },
    {
      "name": "Tutting Peak",
      "bpm_target": 97,
      "bpm_range": [90, 105],
      "duration_s": 120,
      "energy": 0.70,
      "kinetic_texture": "tutting",
      "peak_count_s": 75.0,
      "notes": "Box geometry, arm planes. Peak at 1:15 into block."
    },
    {
      "name": "Cool-down",
      "bpm_target": 78,
      "bpm_range": [70, 85],
      "duration_s": 120,
      "energy": 0.20,
      "kinetic_texture": "fluid",
      "notes": "Floor work, breath-driven dissolve"
    }
  ]
}
```

---

## Step 1 — Run the bridge

```python
from scripts.movement_bridge import build_mix_plan, validate_payload

validate_payload(payload)
mix_plan = build_mix_plan(payload, catalog)
```

The bridge runs per-block:

| Block | Texture filter | BPM candidates (top-1 title) | Anchor offset |
|---|---|---|---|
| Warm-up | fluid | ambient/deep-house track ~80 BPM | 0.0 s (no peak_count_s) |
| Groove Build | fluid+grounded | lo-fi or reggaeton ~92 BPM | 0.0 s (no peak_count_s) |
| Tutting Peak | tutting | polyrhythmic hip-hop ~97 BPM | +12.5 s (drop at 62.5 s, peak at 75 s) |
| Cool-down | fluid | ambient/neo-classical ~78 BPM | 0.0 s (no peak_count_s) |

The +12.5 s offset on the tutting block means the track is cued 12.5 seconds early so its
drop at 62.5 s lands precisely at the 1:15 choreographic peak.

---

## Step 2 — Compile the release bundle

```python
from scripts.release_hook import compile_release

bundle = compile_release(
    mix_plan=mix_plan,
    choreo_script_path="routines/hip-hop-interpretive-2026-06-22.md",
    output_dir="releases/hip-hop-interpretive-2026-06-22/",
)
```

### Output files written

```
releases/hip-hop-interpretive-2026-06-22/
├── choreo_script.md            ← verbatim copy of the choreography Markdown
├── audio_mix_plan.json         ← serialised MixPlan (per-block candidates + offsets)
└── provenance_block.json       ← IP timestamp + SHA-256 fingerprints
```

### Provenance block (example)

```json
{
  "routine_id": "hip-hop-interpretive-2026-06-22",
  "generated_at": "2026-06-22T18:30:00Z",
  "choreo_script_sha256": "a3f5c2d8...",
  "audio_mix_plan_sha256": "bb12e49a...",
  "epic": "tonykoop/claude-skills#471",
  "skill_version": "playlist-builder/release-hook@1.0.0"
}
```

---

## Step 3 — StudioPipeline handoff (optional)

If `STUDIOPIPELINE_HOOK_URL` is set in the environment, `compile_release()` automatically
POSTs the bundle metadata to the pipeline. Otherwise, the bundle directory is the delivery
artifact and can be zipped and attached to a GitHub release or shared via Google Drive.

```bash
export STUDIOPIPELINE_HOOK_URL="https://studio.example.com/hooks/routine-release"
python3 -c "
from scripts.release_hook import compile_release
bundle = compile_release('mix_plan.json', 'choreo.md', 'releases/')
print('hook_sent:', bundle.hook_sent)
"
```

---

## Key design decisions

- **No audio rendering.** The bundle contains a *mix plan* (which tracks, at which offset),
  not rendered audio. Rendering is a StudioPipeline concern.
- **Non-blocking hook.** If StudioPipeline is unreachable, compilation still succeeds.
- **Provenance is SHA-256, not a signature.** For full IP provenance, pipe the
  `provenance_block.json` through an offtheshelf notarisation step (offtheshelf #35).
- **v1 = curation + splice of owned tracks.** Audio generation is explicitly out of scope
  per the epic's red-team note.
