# Movement-Engine → Playlist Data Bridge Contract

**Epic:** #471 — playlist-builder audio-dynamic  
**Story:** #475  
**Version:** v1.0  

---

## Overview

The movement bridge is the integration seam between the `movement_arts` engine (#463) and the
`playlist-builder` audio-dynamic layer (#471). The bridge:

1. Accepts a `MovementRoutinePayload` — a JSON object describing the routine's blocks with BPM,
   energy, and kinetic-texture constraints.
2. Runs BPM matching, texture filtering, and sonic-anchor alignment for each block.
3. Returns a `MixPlan` — a parallel list of `MixBlock` objects, each pairing the input block
   with its selected tracks and anchor offsets.

---

## Constraint Payload Schema

Schema: `schemas/agent_packets/MovementRoutinePayload.schema.json`

**Top-level fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `routine_id` | string | yes | Unique routine identifier |
| `style` | string | yes | Movement style (hip-hop, vinyasa, ballet, …) |
| `total_duration_s` | number | yes | Total routine duration in seconds |
| `blocks` | array | yes | Ordered list of `RoutineBlock` objects |
| `bpm_global` | number | no | Default BPM (overridden per block) |
| `source_engine` | string | no | Engine ID that generated this payload |
| `created_at` | date-time | no | ISO-8601 generation timestamp |

**Per-block fields (`RoutineBlock`):**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Block label |
| `bpm_target` | number | yes | Ideal BPM |
| `bpm_range` | [min, max] | no | Defaults to bpm_target ±10 |
| `duration_s` | number | yes | Block duration |
| `energy` | number 0–1 | no | Target energy (secondary rank signal) |
| `kinetic_texture` | string | no | Texture from KINETIC_TEXTURE_MAP.md |
| `peak_count_s` | number | no | Seconds into block for choreographic peak |
| `notes` | string | no | Human-readable annotation |

---

## MixPlan Return Schema

The bridge returns a `MixPlan` object with these fields:

| Field | Type | Description |
|---|---|---|
| `routine_id` | string | Echoes the input `routine_id` |
| `style` | string | Echoes the input `style` |
| `total_duration_s` | number | Echoes the input total duration |
| `blocks` | list[MixBlock] | One entry per input block, in order |

Each `MixBlock` contains:

| Field | Type | Description |
|---|---|---|
| `name` | string | Block name (from input) |
| `bpm_target` | number | Target BPM (from input) |
| `duration_s` | number | Block duration (from input) |
| `kinetic_texture` | string | Texture (from input, may be None) |
| `peak_count_s` | number | Peak timestamp (from input, may be None) |
| `candidates` | list[dict] | BPM+texture-ranked track candidates (top 5) |
| `anchor_offset_s` | number | Seconds to shift track start for anchor alignment |
| `anchor_fallback` | bool | True if no reliable anchor found |
| `anchor_type_used` | str | The anchor type that was aligned (may be absent) |

---

## Round-Trip Protocol with movement_arts #463

```
movement_arts engine
        │
        │  MovementRoutinePayload (JSON)
        ▼
playlist-builder/movement_bridge.py
        │  build_mix_plan(payload, catalog) → MixPlan
        │
        ▼
Caller: serialize MixPlan to JSON and return to movement_arts
        or hand off to release_hook.py for bundle compilation
```

The movement_arts engine (#463) generates the `MovementRoutinePayload`; the bridge is a
pure function: same payload + same catalog → same MixPlan. There is no network call inside
the bridge itself. The caller handles I/O.

**Dependency note:** Full round-trip requires `tonykoop/claude-skills#463` merged. The bridge
can run standalone with a hand-authored `MovementRoutinePayload` JSON for testing or prototyping.

---

## Validation

`movement_bridge.validate_payload(d)` checks the dict against
`schemas/agent_packets/MovementRoutinePayload.schema.json` using `jsonschema` if available,
or a lightweight structural check otherwise. It raises `ValueError` with a descriptive message
on failure.

---

## Error Handling

| Condition | Behaviour |
|---|---|
| `bpm_target` missing from a block | `validate_payload` raises before `build_mix_plan` is called |
| No catalog tracks match a block | `MixBlock.candidates` is an empty list; the block is still emitted |
| `kinetic_texture` unknown | `texture_map.py` raises `ValueError`; callers should catch and log |
| `peak_count_s` absent | `align_timeline` uses `0.0`; `anchor_offset_s` is relative to track start |

---

## Integration Points

- `scripts/bpm_match.py` — `match_blocks(routine_blocks, catalog)`
- `scripts/texture_map.py` — `filter_tracks_by_texture(catalog, texture)`
- `scripts/sonic_anchor.py` — `align_timeline(blocks, anchored_tracks)`
- `scripts/release_hook.py` — consumes `MixPlan` to compile the multimedia release bundle
- Schema: `schemas/agent_packets/MovementRoutinePayload.schema.json`
