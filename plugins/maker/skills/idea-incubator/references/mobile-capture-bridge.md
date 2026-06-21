# Mobile Capture Bridge — iOS Shortcuts / Android Tasker → Obsidian

Design doc and setup guide for Story #407 (Epic #406). Closes the first gap in the
mobile→Obsidian→incubator→dispatch pipeline: getting a Gemini brainstorm off the
phone and into the Obsidian vault inbox with minimal friction.

## Overview

```
[Gemini app on phone]  →  [iOS Shortcut / Android Tasker]
      |                              |
      | share / copy URL             | Obsidian Advanced URI
      v                              v
[Gemini chat URL]        [vault/00-inbox/<stable-filename>.md]
                                     |
                          [inbox_watcher.py polls & triggers]
```

The bridge is a one-tap share action that:
1. Takes the current Gemini chat URL (or clipboard).
2. Derives a stable filename via `url_upsert.py` conventions (see
   `scripts/url_upsert.py`).
3. Writes a stub `.md` file into the Obsidian vault inbox using the
   **Obsidian Advanced URI** plugin, pre-stamped with provenance front-matter.

Once the file lands in the inbox, `inbox_watcher.py` picks it up and fires the
ingestion pipeline automatically on the home PC (Story #409, dispatched via
Tailscale in Story #412).

---

## Prerequisites

| Item | Notes |
|------|-------|
| Obsidian (iOS / Android) | Free tier sufficient |
| **Obsidian Advanced URI** plugin | Community plugin — enables URL-scheme writes |
| Gemini app (iOS / Android) | For conversation share |
| The vault synced to phone | iCloud / Obsidian Sync / Syncthing |
| Home PC running `inbox_watcher.py` | Stories #409 + #412 |

---

## Obsidian Advanced URI setup

1. In Obsidian → Settings → Community Plugins → search **Advanced URI** → install + enable.
2. Note your vault name (e.g. `Tony`). Used in the URI below.
3. Test that `obsidian://advanced-uri?vault=Tony&...` opens Obsidian on the phone.

### Inbox folder

Create `00-inbox/` in your vault root if it does not exist. The watcher
(`inbox_watcher.py`) defaults to this folder.

---

## iOS Shortcut

### Setup

1. Open the **Shortcuts** app → tap **+** to create a new shortcut.
2. Name it: `Gemini → Obsidian Inbox`.
3. Actions (in order):

**Action 1 — Get URL from Share Sheet**
```
Action: "Receive" (at the top)
  Input: URLs, Text
  Run on share: ON
```

**Action 2 — Get text from input**
```
Action: Get Text from Input
  Input: Shortcut Input
```

**Action 3 — URL Encode**
```
Action: URL Encode
  Text: [output of Action 2]
```
Store result as variable `EncodedURL`.

**Action 4 — Get current date/time (ISO)**
```
Action: Format Date
  Date: Current Date
  Format: ISO 8601
```
Store as `ISODate`.

**Action 5 — Build front-matter block**
```
Action: Text
Content:
---
source: gemini
chat_url: [Shortcut Input URL]
exported_at: [ISODate]
title: Gemini clip [ISODate]
---

> Clipped from Gemini: [Shortcut Input URL]
>
> **Next step:** run the idea-incubator ingestion pipeline.
```
Store as `FrontMatter`.

**Action 6 — URL Encode the content**
```
Action: URL Encode
  Text: [FrontMatter]
```
Store as `EncodedContent`.

**Action 7 — Build Obsidian URI**
```
Action: Text
obsidian://advanced-uri?vault=Tony&filepath=00-inbox%2Fgemini-[EncodedURL].md&data=[EncodedContent]&mode=new
```
Replace `Tony` with your vault name. Store as `ObsidianURI`.

**Action 8 — Open URL**
```
Action: Open URLs
  URL: [ObsidianURI]
```

4. **Add to Share Sheet:** in the shortcut editor → tap the ⓘ → enable "Show in Share Sheet".

### Usage

While reading a Gemini conversation on iOS:
1. Tap **Share** (the box-and-arrow icon).
2. Select **Gemini → Obsidian Inbox**.
3. Obsidian opens briefly, writes the file, and returns to Gemini.
4. The file lands in `00-inbox/` in your vault.

---

## Android — Tasker

Tasker + AutoShare + Obsidian Advanced URI achieves the same result.

### Prerequisites (Android)

- **Tasker** (paid, ~$3)
- **AutoShare** Tasker plugin (for sharing from other apps)
- Obsidian Advanced URI plugin enabled (same as iOS)

### Task: "Gemini → Obsidian Inbox"

Create a new Task:

**Action 1 — AutoShare Receive**
```
Plugin: AutoShare
Configuration: AutoShare Receive
  Label: Gemini → Obsidian Inbox
  Filter: URL, text
```
This provides `%as_text` (the shared URL/text) and `%as_subject`.

**Action 2 — Variable Set: timestamp**
```
Action: Variable Set
  Name: %ts
  To: %TIMES    (Unix seconds — Tasker built-in)
```

**Action 3 — Variable Set: front-matter**
```
Action: Variable Set
  Name: %fm
  To:
---
source: gemini
chat_url: %as_text
exported_at: %ts
title: Gemini clip %ts
---

> Clipped from Gemini: %as_text
>
> **Next step:** run the idea-incubator ingestion pipeline.
```

**Action 4 — URL Encode content**
```
Action: Variable Set
  Name: %enc_content
  To: %fm
  (then: JavaScript action or HTTP Request to encode — see note)
```

> **Note:** Tasker's built-in `%enc_content = urlencode(%fm)` requires Tasker
> 5.12+. On older builds, use a **JavaScriptlet** action:
> `var out = encodeURIComponent(global('%fm')); setLocal('enc_content', out);`

**Action 5 — Launch Obsidian URI**
```
Action: Launch App
  URI: obsidian://advanced-uri?vault=Tony&filepath=00-inbox%2Fgemini-%ts.md&data=%enc_content&mode=new
```
Replace `Tony` with your vault name.

### Register AutoShare

In AutoShare's **Services** tab, add your new Task as a share target.
It will appear in Android's share sheet alongside other apps.

### Usage (Android)

1. Long-press a Gemini conversation link (or use Chrome's share button).
2. Select **Gemini → Obsidian Inbox** from the share sheet.
3. Tasker fires the task; Obsidian writes the file.

---

## Filename stability

The bridge writes a file named after the URL or timestamp. The `url_upsert.py`
script (Story #408) provides `sanitize_chat_url(url)` to convert a Gemini chat
URL to a stable, reproducible filename stem — so clipping the same conversation
twice maps to the same filename, enabling APPEND_MODE dedup (Story #410).

For the Shortcut/Tasker actions above you can use the URL-encoded chat URL as the
filename stem directly; `url_upsert.py` will normalize it at ingest time.

**Stable filename convention:**
```
gemini-<sha8 of normalized URL>-<first 32 chars of slug>.md
```

---

## Failure modes and mitigations

| Failure | Symptom | Mitigation |
|---------|---------|-----------|
| Obsidian Advanced URI not installed | Obsidian opens but no file appears | Install the plugin; test with a manual URI first |
| Vault not synced | File written to device but not on PC | Verify sync app is running; iCloud / Obsidian Sync / Syncthing |
| Gemini URL unstable (redirects) | Different URL each time → two files for same convo | `url_upsert.py` normalizes; APPEND_MODE merges by conversation_id |
| Share sheet missing shortcut/task | Shortcut not added to Share Sheet | iOS: ⓘ → enable "Show in Share Sheet"; Android: AutoShare Services |
| File already exists | Duplicate stub | `url_upsert.py` returns `'existing'` and skips overwrite by default |

---

## References

- `scripts/url_upsert.py` — URL normalization + inbox upsert (Story #408)
- `scripts/inbox_watcher.py` — daemon that polls the inbox and fires the pipeline (Story #409)
- `scripts/append_mode.py` — CREATE/APPEND dedup logic (Story #410)
- `references/gemini-export-pipeline.md` — end-to-end pipeline design
- `references/tailscale-dispatch.md` — wake the home grid from mobile (Story #412)
- [Obsidian Advanced URI docs](https://vinzent03.github.io/obsidian-advanced-uri/)
