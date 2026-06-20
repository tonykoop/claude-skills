# Mastering / Album Backend — Public Handoff Contract

**This document defines the interface the public `playlist-builder` skill uses
to invoke the PRIVATE mastering, MIR-critique, and album-builder backend in
`tonykoop/StudioPipeline-Selecta`. No algorithmic detail, mastering chain
parameters, critique-scoring logic, or segmentation implementation appears
here or anywhere else in this public repo.**

## Boundary rule

```
┌─────────────────────────────────────────────┐
│  PUBLIC (this repo)                         │
│  • Gather playlist manifest                 │
│  • Emit handoff payload (schema below)      │
│  • Call backend if configured               │
│  • Display / save result; degrade gracefully│
└─────────────────────────────────────────────┘
            │  handoff_payload (JSON)
            ▼
┌─────────────────────────────────────────────┐
│  PRIVATE (StudioPipeline-Selecta)           │
│  • Mastering chains                         │
│  • MIR-critique scoring                     │
│  • Album segmentation / sequencing logic    │
│  • Aesthetic Synthesis Crawler (ASC) matrix │
└─────────────────────────────────────────────┘
```

## Backend discovery

The backend endpoint is read from the environment:

```
PLAYLIST_MASTERING_BACKEND_URL   HTTP/HTTPS URL of the private backend endpoint
PLAYLIST_MASTERING_BACKEND_TOKEN Bearer token (optional; sent as Authorization header)
```

When `PLAYLIST_MASTERING_BACKEND_URL` is unset the thin client returns a
`MasteringBackendResult` with `available=False` and logs a single line:

```
mastering backend not configured — set PLAYLIST_MASTERING_BACKEND_URL to enable
```

No exception is raised; the caller receives a structured fallback and can
continue without the backend.

## Handoff payload (public → private)

```json
{
  "schema": "mastering-handoff-v1",
  "playlist_id": "<uuid or user-assigned string>",
  "context": "<context profile name, e.g. yoga-power>",
  "tracks": [
    {
      "phase": "<phase id>",
      "bank": "<A|B|C|D|E>",
      "spotify_uri": "<optional>",
      "search_string": "<Spotify/SoundCloud search query>",
      "approx_duration_s": 240,
      "exact_id_status": "<verified|unverified|requires_auth>"
    }
  ],
  "mastering_intent": {
    "target_lufs": -14,
    "true_peak_dbfs": -1.0,
    "format": "album"
  }
}
```

`mastering_intent` fields are advisory — the private backend applies its own
chain. The public client sets sensible streaming defaults (`-14 LUFS`, `-1 dBTP`)
and the `format` hint (`"album"` | `"class"` | `"single"`).

## Backend response (private → public)

The backend returns JSON. The public client only reads these fields:

```json
{
  "status": "ok | queued | error",
  "job_id": "<backend job reference>",
  "message": "<human-readable status string>",
  "output_url": "<optional URL to download result when ready>"
}
```

The public client never parses or re-emits chain parameters, critique scores,
or segmentation details. It surfaces `status`, `job_id`, and `output_url` to
the user only.

## Graceful degradation

When the backend is absent or returns a non-2xx status, the skill:

1. Logs the error at INFO level (not a crash).
2. Returns `MasteringBackendResult(available=False, status="unavailable")`.
3. Continues to output the raw playlist as normal — mastering is additive,
   never blocking.

See `scripts/mastering_backend.py` for the implementation.
