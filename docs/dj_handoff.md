# DJ / Playlist-Builder Handoff Contract

**Epic:** #478 — Cross-skill orchestration: Sheet Music × Music Teacher × DJ  
**Version:** v0  
**Date:** 2026-06-22  
**Related epics:** tonykoop/claude-skills#471, tonykoop/claude-skills#419

---

## Overview

This document defines how the `AlbumSequencePacket` (Stage-3 output of the orchestration loop) is translated into the `maker:playlist-builder` catalog input format, enabling the Curator-Performer to hand off a sequenced album to the DJ / mastering pipeline.

The `maker:playlist-builder` skill (v0.4.0) already operates a three-mode catalog system (Spotify / Tony Koop catalog / seed banks) with Camelot Wheel harmonic sequencing. This handoff wires the newly composed tracks produced by the music-teacher loop into that existing catalog without breaking the skill's sourcing-honesty modes.

---

## Field Mapping: AlbumSequencePacket → playlist-builder Catalog Track

Each entry in `AlbumSequencePacket.sequence` maps to one `Track` object in the playlist-builder catalog schema (`plugins/maker/skills/playlist-builder/references/CATALOG_SCHEMA.md`):

| AlbumSequencePacket field | Catalog Track field | Notes |
|--------------------------|---------------------|-------|
| `sequence[*].title` | `title` | Direct copy |
| _(not in packet)_ | `artist` | Set to `"tonykoop/music-teacher"` (synthetic source) |
| _(derived)_ | `duration_ms` | Read from `CompositionStatePacket` or rendered MIDI; convert with `round(duration_s × 1000)` |
| _(none — internally generated)_ | `spotify_uri` | Omit; these are original compositions, not Spotify tracks |
| _(none)_ | `soundcloud_url` | Omit unless the track is later uploaded |
| `sequence[*].camelot_code` | `tags[]` | Append `"camelot:<code>"` (e.g., `"camelot:8A"`) to `tags` |
| `sequence[*].bpm` | `bpm` | Direct copy (integer-rounded) |
| `sequence[*].arc_role` | `tags[]` | Append `"arc:<role>"` (e.g., `"arc:opener"`) to `tags` |
| `packet_id` | `tags[]` | Append `"asp:<packet_id>"` for provenance tracing |
| `sequence[*].camelot_code` | `audio_features.key` / `.mode` | Decode from Camelot code (see table below) and populate Spotify-compatible `audio_features` if needed by downstream |

The catalog entry uses `"source": "custom-xlsx"` or a new `"source": "music-teacher"` value (to be added in a future catalog schema revision). Until then, use `"source": "custom-xlsx"` and distinguish via tags.

---

## Camelot → Spotify Key/Mode Mapping

Playlist-builder's `audio_features` dict uses Spotify's integer key (0=C, 1=C#, …, 11=B) and mode (0=minor, 1=major). The mapping from Camelot codes:

| Camelot | Key name | Spotify key int | Mode int |
|---------|----------|----------------|---------|
| 1A | A minor | 9 | 0 |
| 2A | E minor | 4 | 0 |
| 3A | B minor | 11 | 0 |
| 4A | F# minor | 6 | 0 |
| 5A | C# minor | 1 | 0 |
| 6A | G# minor | 8 | 0 |
| 7A | Eb minor | 3 | 0 |
| 8A | Bb minor | 10 | 0 |
| 9A | F minor | 5 | 0 |
| 10A | C minor | 0 | 0 |
| 11A | G minor | 7 | 0 |
| 12A | D minor | 2 | 0 |
| 1B | C major | 0 | 1 |
| 2B | G major | 7 | 1 |
| 3B | D major | 2 | 1 |
| 4B | A major | 9 | 1 |
| 5B | E major | 4 | 1 |
| 6B | B major | 11 | 1 |
| 7B | F# major | 6 | 1 |
| 8B | Db major | 1 | 1 |
| 9B | Ab major | 8 | 1 |
| 10B | Eb major | 3 | 1 |
| 11B | Bb major | 10 | 1 |
| 12B | F major | 5 | 1 |

---

## Beatmatch / BPM Continuity Rules

When consuming an `AlbumSequencePacket`, the Curator-Performer (or a downstream DJ skill) applies:

1. **Adjacent Camelot compatibility:** Transitions between tracks should be same-number same-letter, adjacent numbers same-letter, or same-number A↔B. Exceptions allowed for `interlude` arc roles.
2. **BPM delta rule:** Adjacent tracks in the sequence should differ by ≤ 10 BPM without a bridge. If the delta exceeds 10 BPM, add a `transition_notes` entry on the higher-energy track explaining the BPM ramp strategy.
3. **Energy arc enforcement:** The `arc_role` order must follow the chosen arc template. For `album` arc type: `opener` → `build` → `peak` → (`sustain` optional) → `cool-down` → `closer`. A `closer` that is higher energy than the `peak` is a sequencing error.
4. **No Camelot jump > 2:** Transitions that skip more than 2 positions on the Camelot Wheel without an energy justification (e.g., a deliberate genre break) should be flagged in `transition_notes`.

---

## Resulting Catalog Entry (Example)

Continuing the "Kora & Flute EP" example from `docs/album_workflow.md`, Track 1 ("Kora Dawn", Camelot 8A, 76 BPM, arc: opener) becomes:

```jsonc
{
  "title": "Kora Dawn",
  "artist": "tonykoop/music-teacher",
  "duration_ms": 214000,
  "genre": "World",
  "bpm": 76,
  "tags": ["camelot:8A", "arc:opener", "asp-01J3XL5P4F000000000000000"],
  "audio_features": {
    "key": 10,
    "mode": 0,
    "tempo": 76.0,
    "energy": 0.42,
    "valence": 0.55
  }
}
```

This entry can be placed into bank `A`–`E` at the curator's discretion (no automatic bank mapping; original compositions do not have SoundCloud play-count data to inform bank assignment).

---

## Sourcing Honesty Mode

Original compositions produced by the music-teacher loop must be cataloged under the `manual-curation` honesty mode (see `plugins/maker/skills/playlist-builder/references/HONESTY_MODES.md`). The skill must not claim Spotify or SoundCloud provenance for synthetic tracks.

---

## Cross-links

- `maker:playlist-builder` catalog epics: tonykoop/claude-skills#471, tonykoop/claude-skills#419
- AlbumSequencePacket schema: `schemas/agent_packets/AlbumSequencePacket.schema.json`
- Playlist-builder catalog schema: `plugins/maker/skills/playlist-builder/references/CATALOG_SCHEMA.md`
- Playlist-builder mastering backend: `plugins/maker/skills/playlist-builder/references/MASTERING_BACKEND_CONTRACT.md`
- Skill boundaries: `docs/music_skill_boundaries.md`
- Workflow walkthrough: `docs/album_workflow.md`
- Data integrity: `docs/data_integrity.md`
