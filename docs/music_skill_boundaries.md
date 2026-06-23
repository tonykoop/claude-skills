# Music Skill Boundaries Charter

**Epic:** #478 — Cross-skill orchestration: Sheet Music × Music Teacher × DJ  
**Version:** v0  
**Date:** 2026-06-22

---

## Role Cards

### Translator — `maker:sheet-music`

**Purpose:** Convert between musical representations (audio, score, ABC notation, LilyPond, MusicXML, MIDI) and deposit playable artifacts into a build repo or central catalog.

**Owns:**
- Source ingestion: audio files, hummed melodies, user-described progressions
- Score generation: ABC/LilyPond/MusicXML/MIDI/WAV/SVG/PDF rendering
- Instrument-specific arrangement layout (fingering, clef, key transposition)
- The `AcousticIngestPacket` — the authoritative first-stage output of the 3-stage loop
- Catalog deposit (`learn-to-play/` repo structure, Mode A/B catalog entries)

**Does not own:**
- Compositional gap-filling (bridges, B-sections, transitions) → Coach-Producer
- Playlist sequencing and energy arc → Curator-Performer
- Mastering / mix decisions → StudioPipeline

---

### Coach-Producer — `music-teacher` (tonykoop/music-teacher)

**Purpose:** Analyze compositions for structural gaps, generate missing sections, and produce a complete arrangement state ready for sequencing.

**Owns:**
- Structural analysis: verse/chorus/bridge map, gap detection
- Compositional gap-filling: generating B-sections, transitions, intros/outros
- Harmonic guidance: chord substitutions, modal suggestions
- The `CompositionStatePacket` — the authoritative second-stage output
- Revision tokens for immutable edit history (see `docs/data_integrity.md`)

**Does not own:**
- Initial score transcription → Translator
- Playlist ordering, energy arcs, BPM matching → Curator-Performer
- Audio rendering / WAV production → Translator (via `render_pipeline.py`)

---

### Curator-Performer — `maker:playlist-builder`

**Purpose:** Sequence a set of composed tracks into a listener-ready album or playlist with harmonic flow, energy arc, and beatmatch continuity.

**Owns:**
- Energy-arc mapping (power → sustained → sculpt → restorative or DJ equivalents)
- Camelot Wheel harmonic sequencing
- BPM / beatmatch decisions between tracks
- The `AlbumSequencePacket` — the authoritative third-stage output
- Handoff to mastering backend (`tonykoop/StudioPipeline-Selecta`)

**Does not own:**
- Track composition or arrangement → Coach-Producer
- Score/notation rendering → Translator
- Sourcing tracks outside the approved catalog modes (Spotify / Tony Koop catalog / seed banks)

---

## Hand-off Points

| From | To | Packet | Trigger |
|------|----|--------|---------|
| Translator | Coach-Producer | `AcousticIngestPacket` | Score/audio successfully ingested and rendered |
| Coach-Producer | Curator-Performer | `CompositionStatePacket` | All structural gaps resolved; arrangement locked |
| Curator-Performer | StudioPipeline / DJ | `AlbumSequencePacket` | Sequence ordered, Camelot codes assigned |

Packet schemas are defined in `schemas/agent_packets/` (see `schemas/agent_packets/README.md`).

---

## Anti-overlap Rules

| Responsibility | Owner | Non-owner action |
|----------------|-------|-----------------|
| Audio/score transcription | Translator | Coach-Producer passes raw source to Translator; never transcribes itself |
| Compositional gap-filling | Coach-Producer | Translator outputs what it receives; Curator-Performer does not rewrite sections |
| BPM / Camelot sequencing | Curator-Performer | Coach-Producer may suggest a key; final Camelot code assignment belongs to Curator-Performer |
| Revision tokens / edit history | Coach-Producer (issues tokens) | Translator and Curator-Performer consume tokens, never mint new ones |
| Mastering decisions | StudioPipeline | All three music skills are pre-master; none applies EQ/compression/loudness normalization |
| Catalog sourcing honesty modes | Curator-Performer | Translator and Coach-Producer do not query Spotify or seed banks directly |

---

## Version history

| Version | Date | Notes |
|---------|------|-------|
| v0 | 2026-06-22 | Initial charter. Derived from Epic #478 and existing SKILL.md interfaces. Expect iteration as music-teacher J1/J2 and sheet-music H emit/consume real packets. |
