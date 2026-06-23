# Core Data-Integrity Rules

**Epic:** #478 — Cross-skill orchestration: Sheet Music × Music Teacher × DJ  
**Version:** v0  
**Date:** 2026-06-22

These rules govern all data exchanged between the three music skills via the agent packets defined in `schemas/agent_packets/`. They prevent multi-agent edits from corrupting shared state.

---

## 1. Revision Tokens (Immutability)

### Rule

**Every packet is immutable once emitted.** No skill may edit a packet it did not originate, and no skill may edit its own past packets in place.

### Revision token scheme

- Tokens are **ULIDs** (Universally Unique Lexicographically Sortable Identifiers): 26-character, monotonically increasing, time-prefixed, URL-safe.
- **Coach-Producer (`music-teacher`) is the sole minter of revision tokens.** It mints a new ULID for every composition pass and writes it into `CompositionStatePacket.revision_token`.
- Translator (`maker:sheet-music`) emits `AcousticIngestPacket` with `revision_token: null`. Only after Coach-Producer processes the packet may a token be assigned.
- Curator-Performer (`maker:playlist-builder`) never mints tokens; it reads and forwards `revision_token` values from the `CompositionStatePacket` objects it consumed.

### Immutability rule

When Coach-Producer needs to re-process a track (e.g., a second gap-fill pass), it emits a **new** `CompositionStatePacket` with a **new** `packet_id` and a **new** `revision_token`. The original packet is archived, not overwritten. Consumers must always use the packet with the highest (most recent) ULID token.

### ULID format reference

```
01ARZ3NDEKTSV4RRFFQ69G5FAV
└── 10-char timestamp ──┘└── 16-char random ──┘
```

Libraries: `python-ulid`, `ulid-ts`, `ulid` (Go). Generation must occur at packet-emit time inside the skill, not inside this repo.

---

## 2. Clock Synchronization

### Rule

**All timestamps in all packets must be ISO-8601 format in UTC with no local timezone offset.**

### Required format

```
YYYY-MM-DDTHH:MM:SSZ
```

Examples:
- `2026-06-22T09:00:00Z` ✓
- `2026-06-22T09:00:00+05:30` ✗ (timezone offset forbidden)
- `2026-06-22 09:00:00` ✗ (missing T and Z)

### Timestamp fields

| Packet | Field | Set by |
|--------|-------|--------|
| `AcousticIngestPacket` | `ingested_at` | Translator, at render completion |
| `CompositionStatePacket` | `locked_at` | Coach-Producer, at arrangement lock |
| `AlbumSequencePacket` | `sequenced_at` | Curator-Performer, at sequence finalization |

### Rationale

Multi-agent sessions may span multiple machines and timezones. UTC prevents ambiguity when sequencing packets by time and computing inter-stage latency.

---

## 3. Timing Conventions

Two timing representations are used depending on context:

### Absolute-sample timing

Used for **audio editing** operations (splice points, loop boundaries, fade positions):

```
sample_position = floor(time_seconds × sample_rate_hz)
```

- Always integer-valued.
- The `sample_rate_hz` from `AcousticIngestPacket` is authoritative; must not change between stages.
- If a generated section changes the sample count, Coach-Producer must update the rendered MIDI/MusicXML and note the new total in `CompositionStatePacket`.

### Relative-millisecond timing

Used for **playback sequencing** and **transition metadata** (crossfade duration, beatmatch ramp length):

```
duration_ms = round(time_seconds × 1000)
```

- Always integer-valued.
- Used in `AlbumSequencePacket.sequence[*].transition_notes` and in the DJ handoff (see `docs/dj_handoff.md`).

### Never mix the two

A field that represents a playback-layer position (e.g., crossfade start) must use relative-ms. A field that represents an edit-layer position (e.g., splice frame) must use absolute-samples. If a field's unit is ambiguous, suffix the key name: `_samples` or `_ms`.

---

## 4. Cross-references in Packet Schemas

The schemas in `schemas/agent_packets/` implement these rules as follows:

| Rule | Schema field | Schema constraint |
|------|-------------|-------------------|
| Immutability / revision token | `CompositionStatePacket.revision_token` | `type: string, pattern: ULID` |
| Null token on first emission | `AcousticIngestPacket.revision_token` | `type: ["string","null"], default: null` |
| UTC timestamps | `*.ingested_at`, `*.locked_at`, `*.sequenced_at` | `type: string, format: date-time` |
| BPM range guard | `*.bpm` | `minimum: 20, maximum: 400` |
| Camelot code format | `*.camelot_code` | `pattern: ^(1[0-2]|[1-9])[AB]$` |

---

## 5. Violation handling

If a consuming skill receives a packet that violates any rule above:

1. **Reject** the packet — do not process it.
2. **Log** the violation with the offending `packet_id` and the rule broken.
3. **Comment** on the originating issue or session indicating the violation; do not silently discard.

---

## References

- Packet schemas: `schemas/agent_packets/README.md`
- Skill boundaries: `docs/music_skill_boundaries.md`
- Workflow walkthrough: `docs/album_workflow.md`
- DJ handoff: `docs/dj_handoff.md`
