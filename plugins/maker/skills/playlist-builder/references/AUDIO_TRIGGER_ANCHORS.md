# Audio-Trigger Sonic Anchors

**Epic:** #471 — playlist-builder audio-dynamic  
**Story:** #473  
**Version:** v1.0  

---

## Overview

An *audio-trigger anchor* is a known timestamp in a track where a structural musical event occurs
(a drop, a breakdown, the release of a build, a sudden pause). By tagging tracks with their anchor
timestamps and aligning those timestamps to the routine's *peak counts* (the choreographic
climax of each block), we ensure that the peak choreography lands on a musical event rather than
mid-phrase.

`sonic_anchor.py` implements the tagging schema and the timeline-shift algorithm.

---

## Anchor Timestamp Schema

Each track in the catalog may carry an `anchors` key — a list of anchor objects:

```jsonc
{
  "title": "Gravity Drop",
  "bpm": 97,
  "anchors": [
    {
      "anchor_ts_s": 62.5,
      "anchor_type": "drop",
      "confidence": 0.95,
      "source": "manual"
    },
    {
      "anchor_ts_s": 125.0,
      "anchor_type": "breakdown",
      "confidence": 0.80,
      "source": "manual"
    }
  ]
}
```

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `anchor_ts_s` | float | yes | Seconds from track start where the event occurs |
| `anchor_type` | str | yes | One of: `drop`, `breakdown`, `build`, `pause`, `peak` |
| `confidence` | float | no | 0–1 confidence; < 0.5 triggers manual-fallback mode |
| `source` | str | no | `"manual"` (human-tagged) or `"auto"` (detected) |

### Anchor types

| Type | Description | Choreographic use |
|---|---|---|
| `drop` | Energy suddenly releases to peak intensity | Explosive, tutting peak |
| `breakdown` | Texture strips back to minimal | Staccato contrast block |
| `build` | Tension accumulates toward a release | Rising footwork / isolations |
| `pause` | Complete musical stop (one or two beats) | Freeze, held balance |
| `peak` | Maximum energy point (sustained, not a drop) | Grounded stomp sequence |

---

## Manual-Tag Format

When auto-detection confidence is below threshold (< 0.5) or not available, the curator
adds anchors manually. The manual format is identical to the schema above, with
`"source": "manual"` and `confidence: 1.0` (the human's judgment is authoritative).

A track with **no `anchors` key** or an **empty anchors list** is treated as unanchored.
`align_timeline()` passes unanchored tracks through unchanged.

---

## Timeline-Shift Algorithm

Given a routine block with a `peak_count_s` (seconds into the block when the choreographic
climax occurs) and a set of selected tracks with anchor timestamps, the algorithm:

1. **Identify the best anchor** in the selected track: prefer `drop` or `peak` type; take the
   anchor with the highest `confidence`; tie-break by proximity to `peak_count_s`.

2. **Compute the offset**: `offset_s = peak_count_s - anchor_ts_s`

   A *positive* offset means the track needs to start early (or the block starts late) to bring
   the anchor forward to align with the peak. A *negative* offset means the anchor comes before
   the peak count — the block needs to start later or the track is played from an earlier point.

3. **Emit an `anchor_offset_s` field** on the block: the caller applies this to the track
   start-time when building the mix plan. The skill does not modify the audio file.

4. **Fallback**: if the track has no anchors (or all confidence < 0.5), `anchor_offset_s` is set
   to `0.0` and `anchor_fallback: true` is added to the block result.

### Limits

- The shift is capped at ±30 s by default to avoid playing a long silent intro.
- If the computed offset exceeds the cap, a `anchor_warning` message is added and the offset
  is clamped.

---

## Worked Example

Routine block: "Hip-hop peak", `duration_s=120`, `peak_count_s=75` (1:15 into the block).  
Selected track: "Gravity Drop" — anchor at `62.5 s` (type: `drop`, confidence: 0.95).

```
offset_s = 75 - 62.5 = +12.5 s
```

Start the track 12.5 seconds *early* relative to the block start so the drop (at 62.5 s in the
track) lands at exactly 75 s into the block.

---

## Integration

`sonic_anchor.py` is called by `movement_bridge.py` after BPM matching and texture filtering.
The bridge passes the chosen track + the block's `peak_count_s` and receives the adjusted
`anchor_offset_s` back.
