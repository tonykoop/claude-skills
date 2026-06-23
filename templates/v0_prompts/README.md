# v0 / Replit Prompt Templates

**Epic:** #479 — Deployment bridge  
**Date:** 2026-06-22

These templates are copy-paste prompts for spinning up interactive skill previews in v0.dev or Replit Agent. Each produces a working UI in under 5 minutes with no local setup.

---

## How to Use

**v0.dev:**
1. Open [v0.dev](https://v0.dev)
2. Paste the prompt from a template's "Paste This Prompt" code block into the chat
3. Iterate with follow-up messages if needed
4. Click **Deploy** → share the resulting URL

**Replit Agent:**
1. Open [replit.com/new](https://replit.com/new) → "Build with Agent"
2. Paste the same prompt
3. Replit Agent scaffolds the project and starts a dev server
4. Share the `replit.app` URL

Both paths work for these templates. v0 is faster for pure UI; Replit gives a real Node runtime if you need a backend later.

---

## Templates

| File | What it builds | Key feature |
|---|---|---|
| [`sheet-music-viewer.md`](sheet-music-viewer.md) | ABC notation staff renderer | Playback animation, tempo slider, instrument selector |
| [`kora-hero.md`](kora-hero.md) | Falling-note highway game | Two-lane kora thumb patterns, BPM slider, scoring HUD |

---

## Choosing the Right Tool

For a decision guide across v0.dev, Replit Agent, and Expo Go (native mic/GPU), see [`../../docs/deploy_bridge.md`](../../docs/deploy_bridge.md).

For native device features (mic input, GPU canvas) that these web-based previews cannot provide, see [`../../docs/expo_preview.md`](../../docs/expo_preview.md).
