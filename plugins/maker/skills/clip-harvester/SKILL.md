---
name: clip-harvester
version: 0.1.0
last-updated: 2026-06-20
description: "Capture a social-feed screenshot, clipped post, or pasted text and normalize it into a structured ClipNote (JSON), then hand it off to the private ASC (Aesthetic Synthesis Crawler) backend. Use this skill when the user wants to: harvest inspiration from social feeds, clip a post for the idea pipeline, save a screenshot as a structured note, send a clip to the ASC matrix, or archive content from Instagram / TikTok / Pinterest / YouTube / Twitter. The inventive matrix and selector logic stays private in StudioPipeline-Selecta; this skill only handles capture → normalize → handoff."
---

# Clip Harvester

You help users capture social-feed screenshots, clipped posts, and pasted text and turn them into structured `ClipNote` records for the idea pipeline. The finished note is handed off (when configured) to the private Aesthetic Synthesis Crawler (ASC) backend for matrix routing and curation scoring.

**IP boundary:** no matrix, selector, or translation logic lives in this skill. This is a thin capture-and-normalize client. See `references/ASC_BACKEND_CONTRACT.md` for the full boundary description.

## Step 1 — accept the clip

The user supplies one or more of:

| Input type | Examples |
|---|---|
| **Screenshot file path** | `/tmp/insta-clip.png`, drag-and-drop into the conversation |
| **URL** | A public post URL (Instagram, TikTok, Pinterest, YouTube, Twitter/X) |
| **Pasted text** | Raw copy-pasted caption, comment, or post body |
| **Multiple** | A screenshot + the source URL |

If the user hasn't supplied anything yet, ask: "Drop a screenshot, paste the post text, or share the URL — any combination works."

## Step 2 — extract content (vision / text)

Use your vision capability when a screenshot is provided. Extract:

- **Author handle** (if visible): `@username` or display name
- **Platform** (infer from visual UI or URL): Instagram, TikTok, Pinterest, YouTube, Twitter/X, Reddit, Other
- **Raw text**: caption, title, or post body — full verbatim content, including line breaks
- **Source URL**: extract from image (if shown in a browser) or use the URL the user provided
- **Media description**: one sentence describing any images or video (do not reproduce private imagery)
- **Engagement signals** (if visible): likes, views, saves — record as strings (e.g. `"12.4K"`)

When input is text-only (no screenshot, no URL), note `source_type: "text_clip"` and record the raw text verbatim.

## Step 3 — build the ClipNote

Format the extraction as a `ClipNote` JSON using the schema in `scripts/clip_harvester.py`.

Required fields:
```json
{
  "note_id": "<uuid4 — generate one>",
  "source_type": "screenshot | text_clip | url_clip",
  "captured_at": "<ISO-8601 UTC timestamp>",
  "raw_text": "<extracted text>",
  "tags": ["<user-supplied or auto-inferred tags>"]
}
```

Optional fields (include when available):
```json
{
  "platform": "instagram | tiktok | pinterest | youtube | twitter | reddit | other",
  "source_url": "<URL>",
  "author": "<@handle or display name>",
  "media_paths": ["<local file path(s)>"],
  "media_description": "<one-sentence description of any image/video>",
  "engagement": {"likes": "12.4K", "views": "88K"}
}
```

Show the filled ClipNote to the user and ask for confirmation or tag additions before proceeding.

## Step 4 — hand off to the ASC backend (optional)

If `CLIP_HARVESTER_BACKEND_URL` is set, use `scripts/clip_harvester.py` to POST the handoff payload to the private ASC backend:

```python
from scripts.clip_harvester import ClipNote, ClipHandoff, call_asc_backend

note = ClipNote(**extracted_fields)
handoff = ClipHandoff(note=note, routing_hint="aesthetic-sync")
result = call_asc_backend(handoff)
if result.succeeded:
    print(f"ASC job queued: {result.job_id}")
# if result.available is False, continue normally — handoff is additive
```

When the backend is absent or returns an error the call returns `ClipBackendResult(available=False)` without raising. The ClipNote is still emitted locally — the backend handoff is additive, never blocking.

## Step 5 — save locally

Write the ClipNote JSON to the user's clip store:

```
~/.clip-harvester/notes/<YYYY-MM-DD>/<note_id>.json    (Linux/macOS)
%APPDATA%/clip-harvester/notes/<YYYY-MM-DD>/<note_id>.json   (Windows)
```

If the clip store path doesn't exist, create it. Tell the user where the note was saved.

## Output

Present the saved ClipNote to the user as a compact summary:

```
ClipNote saved: <note_id>
  Platform:  <platform>
  Author:    <author>
  Tags:      <tags>
  Backend:   <queued as <job_id> | not configured | error: <message>>
  File:      <local path>
```

Then offer: "Say 'harvest another' to capture the next clip, or 'show all today' to list today's notes."
