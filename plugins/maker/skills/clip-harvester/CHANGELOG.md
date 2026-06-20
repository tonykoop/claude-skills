# Changelog — clip-harvester

## 0.1.0 — 2026-06-20 (initial)

First release: thin public capture-and-normalize client for the private
ASC (Aesthetic Synthesis Crawler) backend. No matrix, selector, or translation
logic in this public repo.

- **`scripts/clip_harvester.py`** — `call_asc_backend()` + typed dataclasses
  (`ClipNote`, `ClipHandoff`, `ClipBackendResult`). Reads
  `CLIP_HARVESTER_BACKEND_URL` / `CLIP_HARVESTER_BACKEND_TOKEN` from env;
  returns `available=False` silently when unconfigured or on any network error.
  Stdlib-only (`urllib`, `dataclasses`, `json`).
- **`references/ASC_BACKEND_CONTRACT.md`** — documents the public/private IP
  boundary, backend discovery, `asc-handoff-v1` payload schema, response
  schema, and graceful degradation behaviour.
- **`SKILL.md`** — 5-step flow: accept clip → extract content (vision/text) →
  build ClipNote → hand off to ASC backend → save locally.
- **`tests/test_clip_harvester.py`** — 9 unit tests covering: no-backend-URL
  fallback, HTTP 200 ok, HTTP 200 queued, HTTP 500 error, unreachable host,
  payload serialisation, optional-field defaults, and succeeded property.
