# ASC Backend — Public Handoff Contract

**This document defines the interface the public `clip-harvester` skill uses to
invoke the PRIVATE Aesthetic Synthesis Crawler (ASC) matrix/selector backend in
`tonykoop/StudioPipeline-Selecta`. No matrix logic, selector scoring, translation
parameters, or curation algorithms appear here or anywhere else in this public repo.**

## Boundary rule

```
┌────────────────────────────────────────────────────┐
│  PUBLIC (this repo)                                │
│  • Accept screenshot / clip / URL from user        │
│  • Extract & normalize into ClipNote (JSON)        │
│  • POST handoff payload to backend if configured   │
│  • Save ClipNote locally; degrade gracefully       │
└────────────────────────────────────────────────────┘
            │  handoff_payload (JSON)
            ▼
┌────────────────────────────────────────────────────┐
│  PRIVATE (StudioPipeline-Selecta)                  │
│  • ASC matrix routing                             │
│  • Aesthetic selector scoring                     │
│  • Translation / curation pipeline                │
│  • Cross-post deduplication                       │
└────────────────────────────────────────────────────┘
```

## Backend discovery

```
CLIP_HARVESTER_BACKEND_URL    HTTP/HTTPS URL of the private ASC endpoint
CLIP_HARVESTER_BACKEND_TOKEN  Bearer token (optional; sent as Authorization header)
```

When `CLIP_HARVESTER_BACKEND_URL` is unset the thin client returns a
`ClipBackendResult` with `available=False` and logs a single line:

```
ASC backend not configured — set CLIP_HARVESTER_BACKEND_URL to enable
```

No exception is raised; the caller receives a structured fallback and continues
to emit the ClipNote locally without interruption.

## Handoff payload (public → private)

```json
{
  "schema": "asc-handoff-v1",
  "routing_hint": "<optional label for the ASC matrix router>",
  "note": {
    "note_id": "<uuid4>",
    "source_type": "screenshot | text_clip | url_clip",
    "captured_at": "<ISO-8601 UTC>",
    "platform": "<instagram | tiktok | pinterest | youtube | twitter | reddit | other>",
    "source_url": "<optional>",
    "author": "<optional @handle or display name>",
    "raw_text": "<extracted caption / post body>",
    "media_paths": ["<optional local paths>"],
    "media_description": "<optional one-sentence description>",
    "engagement": {"likes": "<optional>", "views": "<optional>"},
    "tags": ["<user or auto-inferred>"]
  }
}
```

## Backend response (private → public)

The backend returns JSON. The public client only reads these fields:

```json
{
  "status": "ok | queued | error",
  "job_id": "<ASC job reference>",
  "message": "<human-readable status string>",
  "output_url": "<optional URL when result is ready>"
}
```

The public client never parses matrix scores, selector results, or pipeline
routing details. It surfaces only `status`, `job_id`, and `output_url` to the user.

## Graceful degradation

When the backend is absent or returns a non-2xx status, the skill:

1. Logs the error at INFO level (not a crash).
2. Returns `ClipBackendResult(available=False, status="unavailable")`.
3. Saves the ClipNote JSON locally as normal — the ASC handoff is additive,
   never a blocker.

See `scripts/clip_harvester.py` for the implementation.

## Related

- Mirrors the CADFit #61/#362 split: public toolset client in claude-skills,
  inventive/proprietary layer kept private in StudioPipeline-Selecta.
- Private backend tracking: StudioPipeline-Selecta ASC cluster under #67.
