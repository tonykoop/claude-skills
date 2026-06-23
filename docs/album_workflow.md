# Multi-Agent Album Workflow Walkthrough

**Epic:** #478 — Cross-skill orchestration: Sheet Music × Music Teacher × DJ  
**Version:** v0  
**Date:** 2026-06-22

---

## Overview

This document walks an end-to-end example of the 3-stage orchestration loop that produces a complete album from raw musical material. Three skills act in sequence; each emits a formal JSON packet consumed by the next. Packet schemas are defined in `schemas/agent_packets/` (see #483).

```
Raw audio / score / melody
         │
  ┌──────▼──────┐
  │  STAGE 1    │  maker:sheet-music  (Translator)
  │  Ingestion  │
  └──────┬──────┘
         │  AcousticIngestPacket
  ┌──────▼──────┐
  │  STAGE 2    │  music-teacher      (Coach-Producer)
  │  Gap-fill   │
  └──────┬──────┘
         │  CompositionStatePacket
  ┌──────▼──────┐
  │  STAGE 3    │  maker:playlist-builder  (Curator-Performer)
  │  Sequencing │
  └──────┬──────┘
         │  AlbumSequencePacket
  ┌──────▼──────┐
  │ StudioPipeline / DJ handoff       (see docs/dj_handoff.md)
  └─────────────┘
```

---

## Worked Example: "Kora & Flute" EP (4 tracks)

### Stage 1 — Ingestion (`maker:sheet-music`)

**Trigger:** The user deposits four audio files + rough chord charts into the session.

**What sheet-music does:**
1. Runs `render_pipeline.py` on each source; outputs ABC notation + MusicXML + MIDI per track.
2. Detects the tonal center and meter for each track.
3. Assigns a provisional Camelot key code (e.g., `8A` for D minor) to each track.
4. Emits one `AcousticIngestPacket` per track (schema: `schemas/agent_packets/AcousticIngestPacket.schema.json`).

**Example packet (Track 1):**
```json
{
  "$schema": "https://tonykoop.github.io/claude-skills/schemas/agent_packets/v0/AcousticIngestPacket.schema.json",
  "schema_version": "0.1.0",
  "packet_id": "aip-01J3XKZM4F000000000000000",
  "track_id": "track-001",
  "title": "Kora Dawn",
  "source_files": ["kora_dawn.wav"],
  "tonal_center": "D",
  "mode": "minor",
  "camelot_code": "8A",
  "bpm": 76.0,
  "meter": "6/8",
  "formats_rendered": ["abc", "musicxml", "midi"],
  "ingested_at": "2026-06-22T09:00:00Z",
  "revision_token": null
}
```

**Hand-off:** All four `AcousticIngestPacket` objects are queued for the Coach-Producer.

---

### Stage 2 — Gap-filling (`music-teacher`)

**Trigger:** Receives the four `AcousticIngestPacket` objects from Stage 1.

**What music-teacher does:**
1. Builds a structural map (verse/chorus/bridge) for each track from the MusicXML.
2. Identifies gaps: Track 2 has no B-section; Track 4 has no outro.
3. Generates the missing sections using its composition models.
4. Issues a new **revision token** (ULID) for each modification, storing the original state immutably (see `docs/data_integrity.md`).
5. Updates the MIDI/MusicXML for affected tracks and emits one `CompositionStatePacket` per track (schema: `schemas/agent_packets/CompositionStatePacket.schema.json`).

**Example packet (Track 2, after gap-fill):**
```json
{
  "$schema": "https://tonykoop.github.io/claude-skills/schemas/agent_packets/v0/CompositionStatePacket.schema.json",
  "schema_version": "0.1.0",
  "packet_id": "csp-01J3XL2R4F000000000000001",
  "track_id": "track-002",
  "source_packet_id": "aip-01J3XKZM4F000000000000001",
  "revision_token": "01J3XL2R4F000000000000001",
  "arrangement_complete": true,
  "sections": ["intro", "verse-A", "verse-B-generated", "chorus", "outro"],
  "gap_analysis": {
    "gaps_found": ["B-section"],
    "gaps_resolved": ["B-section"]
  },
  "camelot_code": "8A",
  "bpm": 76.0,
  "locked_at": "2026-06-22T09:15:00Z"
}
```

**Hand-off:** All four `CompositionStatePacket` objects are queued for the Curator-Performer.

---

### Stage 3 — Sequencing (`maker:playlist-builder`)

**Trigger:** Receives four `CompositionStatePacket` objects from Stage 2.

**What playlist-builder does:**
1. Reads `camelot_code` and `bpm` from each packet.
2. Orders tracks for harmonic flow using the Camelot Wheel (adjacent or same-key transitions preferred).
3. Assigns an energy-arc position to each track (opener → build → peak → cool-down).
4. Emits a single `AlbumSequencePacket` (schema: `schemas/agent_packets/AlbumSequencePacket.schema.json`).

**Example packet (full album):**
```json
{
  "$schema": "https://tonykoop.github.io/claude-skills/schemas/agent_packets/v0/AlbumSequencePacket.schema.json",
  "schema_version": "0.1.0",
  "packet_id": "asp-01J3XL5P4F000000000000000",
  "album_title": "Kora & Flute EP",
  "sequence": [
    {"position": 1, "track_id": "track-001", "camelot_code": "8A", "bpm": 76.0, "arc_role": "opener"},
    {"position": 2, "track_id": "track-003", "camelot_code": "9A", "bpm": 82.0, "arc_role": "build"},
    {"position": 3, "track_id": "track-002", "camelot_code": "8A", "bpm": 76.0, "arc_role": "peak"},
    {"position": 4, "track_id": "track-004", "camelot_code": "8B", "bpm": 70.0, "arc_role": "cool-down"}
  ],
  "source_packet_ids": [
    "csp-01J3XL2R4F000000000000000",
    "csp-01J3XL2R4F000000000000001",
    "csp-01J3XL2R4F000000000000002",
    "csp-01J3XL2R4F000000000000003"
  ],
  "sequenced_at": "2026-06-22T09:30:00Z"
}
```

**Hand-off:** `AlbumSequencePacket` is passed to the DJ / StudioPipeline (see `docs/dj_handoff.md`).

---

## Skill responsibility at each step

| Step | Acting skill | Input | Output |
|------|-------------|-------|--------|
| 1a — Source ingest | `maker:sheet-music` | Raw audio / chord chart | ABC, MusicXML, MIDI |
| 1b — Packet emit | `maker:sheet-music` | Rendered files | `AcousticIngestPacket` × N |
| 2a — Gap analysis | `music-teacher` | `AcousticIngestPacket` × N | Structural gap report |
| 2b — Gap-fill + lock | `music-teacher` | Gap report | Updated MusicXML + `CompositionStatePacket` × N |
| 3a — Harmonic sort | `maker:playlist-builder` | `CompositionStatePacket` × N | Camelot-ordered track list |
| 3b — Sequence emit | `maker:playlist-builder` | Ordered list + energy arc | `AlbumSequencePacket` |
| 4 — DJ / master | StudioPipeline / DJ | `AlbumSequencePacket` | Mixed / mastered album |

---

## References

- Skill boundaries: `docs/music_skill_boundaries.md` (Epic #478, story #481)
- Packet schemas: `schemas/agent_packets/` (Epic #478, story #483)
- Data-integrity rules: `docs/data_integrity.md` (Epic #478, story #484)
- DJ handoff: `docs/dj_handoff.md` (Epic #478, story #485)
- Sheet-music SKILL.md: `plugins/maker/skills/sheet-music/SKILL.md`
- Playlist-builder SKILL.md: `plugins/maker/skills/playlist-builder/SKILL.md`
