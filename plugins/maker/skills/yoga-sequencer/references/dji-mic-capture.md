# DJI Mic Capture Ingest

Use this reference when a live class captured on DJI Mic needs to feed both the language side and the playlist/DJ side.

## Public Capture Manifest

The public repo only defines the manifest and quality gate. Raw audio, private transcripts, and ASR outputs stay local/private.

```json
{
  "capture_id": "dji-2026-06-20-class",
  "device": "DJI Mic 2",
  "audio_file": "private://captures/class.wav",
  "duration_sec": 3600,
  "quality": {
    "music_bed_db": -28,
    "movement_noise": "low",
    "breath_noise": "moderate",
    "dropouts": 0,
    "clipping": false
  },
  "transcript": [
    {
      "start_sec": 0,
      "end_sec": 45,
      "text": "Settle into your breath and notice the space around effort."
    }
  ],
  "timeline": [
    {
      "start_sec": 0,
      "end_sec": 300,
      "phase": "arrival",
      "energy": "low",
      "cue_density": "sparse"
    }
  ]
}
```

## Split Outputs

Path A produces:

- transcript spans
- thematic script extraction
- Rosetta-ready quality status

Path B produces:

- audio timeline handoff
- playlist phase-map compatible fields
- capture-quality notes for DJ/playlist work

## Capture Quality Gate

Before transcript spans can enter the Rosetta parallel dataset:

- duration must be positive
- every transcript span must have positive timing and non-empty text
- music bed should sit below the teacher voice (`music_bed_db <= -18`)
- movement noise must not be `high`
- clipping must be false
- dropouts must be zero

If any gate fails, Path A still emits transcript/thematic data for human repair, but `rosetta_ready` is false.
