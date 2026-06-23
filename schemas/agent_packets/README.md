# Agent Packet Schemas — Music Skill Orchestration

**Epic:** #478 — Cross-skill orchestration: Sheet Music × Music Teacher × DJ  
**Schema version:** v0  
**JSON Schema draft:** Draft-07

---

## Overview

This directory contains the formal JSON Schema definitions for the three inter-agent packets used in the music skill orchestration loop. Each packet is the authoritative output of one stage and the authoritative input to the next.

```
Stage 1 → AcousticIngestPacket    (maker:sheet-music emits)
Stage 2 → CompositionStatePacket  (music-teacher emits)
Stage 3 → AlbumSequencePacket     (maker:playlist-builder emits)
```

---

## Schemas

| File | Stage | Emitted by | Consumed by |
|------|-------|-----------|-------------|
| `AcousticIngestPacket.schema.json` | 1 — Ingestion | `maker:sheet-music` | `music-teacher` |
| `CompositionStatePacket.schema.json` | 2 — Gap-fill | `music-teacher` | `maker:playlist-builder` |
| `AlbumSequencePacket.schema.json` | 3 — Sequencing | `maker:playlist-builder` | StudioPipeline / DJ |

---

## Camelot Wheel codes

The `camelot_code` field appears in all three packets. Valid values are `1A`–`12A` (minor keys) and `1B`–`12B` (major keys):

| Code | Key |  | Code | Key |
|------|-----|-|------|-----|
| 1A | A minor | | 1B | C major |
| 2A | E minor | | 2B | G major |
| 3A | B minor | | 3B | D major |
| 4A | F# minor | | 4B | A major |
| 5A | C# minor | | 5B | E major |
| 6A | G# minor | | 6B | B major |
| 7A | Eb minor | | 7B | F# major |
| 8A | Bb minor | | 8B | Db major |
| 9A | F minor | | 9B | Ab major |
| 10A | C minor | | 10B | Eb major |
| 11A | G minor | | 11B | Bb major |
| 12A | D minor | | 12B | F major |

Adjacent codes on the wheel (±1 number, or same number A↔B) are harmonically compatible transitions.

---

## Versioning

Schemas are versioned under `v0/` in the `$id` URLs. Breaking changes increment the major segment. Minor additions are backwards-compatible within the same major version. Expect iteration as music-teacher J1/J2 and sheet-music H start emitting/consuming real packets.

---

## References

- Workflow walkthrough: `docs/album_workflow.md`
- Skill boundaries: `docs/music_skill_boundaries.md`
- Data-integrity rules (revision tokens, timestamps): `docs/data_integrity.md`
- DJ / playlist-builder handoff: `docs/dj_handoff.md`
