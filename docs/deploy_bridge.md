# Deployment Bridge — Share a Skill as an Interactive App Today

**Epic:** #479  
**Version:** v1  
**Date:** 2026-06-22  
**Snapshot:** v0.dev, Replit Agent, and Expo Go are fast-moving third-party services. Capabilities, quotas, and URLs documented here reflect the state as of 2026-06-22 and will drift. Re-verify before use.

---

## Decision Matrix

Pick the column that matches your primary goal.

| Goal | v0.dev | Replit Agent | Expo Go |
|---|---|---|---|
| Instant UI mockup, no backend | ✅ Best fit | ⚠ Overkill | ❌ Wrong tool |
| Functional prototype with a server | ❌ No runtime | ✅ Best fit | ❌ Wrong tool |
| Native mic / low-latency audio | ❌ No device access | ⚠ Browser mic only (HTTPS) | ✅ Best fit |
| Hardware-accelerated GPU canvas | ❌ No device access | ⚠ WebGL via browser | ✅ Best fit |
| Shareable link (no install) | ✅ v0.dev URL | ✅ Replit URL | ❌ Requires Expo Go app |
| Time to first preview | ~2 min | ~5 min | ~5 min |
| Production path | Export → Vercel / Netlify | Replit Deployments / Railway | EAS Build → App Store |

---

## v0.dev

**Best for:** instant React component previews that look polished with no backend.

Paste a prompt, get a live React/Tailwind component in seconds. v0 generates, you iterate. Use it to quickly validate a UI idea before wiring up real data.

**What it can do:**
- React (Next.js 14 app router compatible), Tailwind CSS, shadcn/ui components
- Animated layouts, responsive grids, data tables, charts (recharts/visx)
- Mock data inline (hardcoded JSON — no fetch calls to external APIs)

**What it cannot do:**
- Run Node.js server code (no API routes, no file system)
- Access browser `MediaDevices` (no mic, no camera) — it runs in a sandboxed iframe
- Authenticate users or persist state beyond a page reload

**How to use with a skill:**
1. Choose a prompt template from [`../templates/v0_prompts/`](../templates/v0_prompts/).
2. Open `v0.dev`, paste the prompt into the chat box.
3. Click **Deploy** to get a shareable `v0.dev/...` URL.
4. Share the URL — anyone with the link can interact with the preview.

**Limits to communicate:** Tell users the preview has no real data — it is a UI shell. Mic features require Expo Go (see below).

---

## Replit Agent

**Best for:** a working prototype with a real server — auth, data persistence, API calls, or a Python/Node backend alongside the UI.

Replit Agent scaffolds a full-stack app from a prompt. The result runs on Replit's servers and gets a public `replit.app` URL immediately.

**What it can do:**
- Full-stack: React + Express, Next.js, Flask, FastAPI — pick in your prompt
- Browser `MediaDevices.getUserMedia()` for mic — works on HTTPS (all Replit apps are HTTPS)
- WebGL in the browser (`<canvas>`) for GPU-accelerated graphics
- Persistent storage: SQLite, Replit DB key-value store
- Environment variables for secrets

**What it cannot do:**
- Native mic buffers below ~20 ms latency (browser AudioContext bottleneck)
- Raw GPU compute (WebGPU is partially available in Chrome but not guaranteed in Replit's iframe)
- Long-running background processes without always-on compute (paid tier)

**Mic access via browser (Replit):**

```javascript
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const ctx = new AudioContext();
const source = ctx.createMediaStreamSource(stream);
const analyser = ctx.createAnalyser();
source.connect(analyser);
// analyser.getFloatTimeDomainData(buf) → pitch detection loop
```

The browser prompts the user for mic permission on first load. No manifest edits needed.

**Limits to communicate:** Cold-start latency on free-tier (~5 s) makes real-time audio awkward. For sub-20 ms latency, use Expo Go.

---

## Expo Go

**Best for:** native mic (pitch detection, rhythm tapping), hardware GPU canvas (falling-note game), or any sensor that a browser cannot provide.

Expo Go delivers a full React Native runtime to a phone via QR scan. No App Store submission, no Xcode.

See the full recipe at [`expo_preview.md`](expo_preview.md).

**Quick path:**
```bash
npx create-expo-app@latest my-skill-preview --template blank
cd my-skill-preview
npx expo install expo-av expo-gl
npx expo start   # prints QR code
```

Scan the QR with the Expo Go app → live preview on device.

**Hard constraint:** Expo Go includes a fixed set of native modules. Any package that requires a custom `.xcframework` / `.aar` not in that set will crash in Expo Go. For those, build a custom dev client with `eas build --profile preview` (~15 min first build).

**Limits to communicate:** Expo Go requires the user to install the Expo Go app (~30 MB). The QR link is not shareable to people without the app. For a zero-install share, use v0.dev or Replit instead.

---

## When None of These Fit

If the prototype has outgrown these tools:

| Situation | Recommended path |
|---|---|
| Need a production mobile app | `eas build --platform ios` / `android` → App Store / Play Store |
| Need a production web app | Export from v0 / Replit → deploy to Vercel, Netlify, or Railway |
| Need low-latency native audio in production | React Native + custom native module, EAS Build |
| Need GPU compute (ML inference, shaders) | Expo + `expo-gl` for rendering; offload inference to an API |

---

## Cross-links

- Expo Go full recipe: [`expo_preview.md`](expo_preview.md)
- Copy-paste prompt templates: [`../templates/v0_prompts/`](../templates/v0_prompts/)
- Music-skill orchestration boundaries: [`music_skill_boundaries.md`](music_skill_boundaries.md)
