# Expo Go Native-Mobile Preview Recipe

**Epic:** #479  
**Version:** v1  
**Date:** 2026-06-22  
**Snapshot:** Tool behavior and SDK versions are as of 2026-06-22. Expo SDK evolves frequently — verify against current Expo docs before use.

---

## Why Expo Go

Web-based preview tools (v0.dev, Replit) serve the browser's `MediaDevices` API for mic access, but camera frame rates, low-latency audio buffers, and hardware GPU shaders require a native runtime. Expo Go delivers a full React Native runtime to your phone via a QR scan — no App Store submission, no Xcode/Android Studio setup. Use it when:

- You need real mic input (pitch detection, tapping-in rhythm, kora note recognition)
- You need hardware-accelerated canvas (kora-hero highway rendering via `expo-gl`)
- You want to test on an actual device in under 5 minutes

If you only need a UI mockup with no device sensors, use v0.dev instead (see [`deploy_bridge.md`](deploy_bridge.md)).

---

## Prerequisites

| Requirement | Version |
|---|---|
| Node.js | 20 LTS or 22 LTS |
| Expo Go app | Latest from App Store / Google Play |
| Same Wi-Fi network | dev machine and phone must share a LAN |

---

## QR Preview Flow

```bash
# 1. Scaffold a new Expo app
npx create-expo-app@latest kora-preview --template blank

# 2. Enter the project
cd kora-preview

# 3. Install any device-access packages you need (examples below)
npx expo install expo-av expo-gl

# 4. Start the dev server — prints a QR code in the terminal
npx expo start
```

Scan the QR code with:
- **iOS** — the default Camera app (Expo Go opens automatically)
- **Android** — the Expo Go app's built-in scanner

The app hot-reloads on every file save. No build step required.

---

## Mic Access

Use `expo-av` for audio recording (Expo SDK 50+):

```bash
npx expo install expo-av
```

```typescript
import { Audio } from 'expo-av';

async function startRecording() {
  const { granted } = await Audio.requestPermissionsAsync();
  if (!granted) return;

  await Audio.setAudioModeAsync({ allowsRecordingIOS: true });
  const { recording } = await Audio.Recording.createAsync(
    Audio.RecordingOptionsPresets.HIGH_QUALITY
  );
  // recording.getURI() returns a local file path when stopped
}
```

**Permission declarations** are injected automatically by Expo when `expo-av` is installed:
- iOS — `NSMicrophoneUsageDescription` in `app.json` → `expo.ios.infoPlist`
- Android — `RECORD_AUDIO` in `AndroidManifest.xml`

Add a human-readable reason to `app.json` so the OS permission dialog makes sense:

```json
{
  "expo": {
    "plugins": [
      ["expo-av", { "microphonePermission": "Allow kora-preview to record your playing." }]
    ]
  }
}
```

---

## GPU / Hardware-Accelerated Canvas

Use `expo-gl` for a WebGL-like surface backed by the device GPU:

```bash
npx expo install expo-gl
```

```typescript
import { GLView } from 'expo-gl';

export function KoraHighway() {
  return (
    <GLView
      style={{ flex: 1 }}
      onContextCreate={(gl) => {
        // gl is a WebGL2RenderingContext-compatible object
        gl.clearColor(0, 0, 0, 1);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.endFrameEXP(); // required — flushes the frame
      }}
    />
  );
}
```

For the kora-hero highway, render falling note columns with `gl.drawArrays`. Sixty FPS is achievable on mid-range devices. See the kora-hero template at [`../templates/v0_prompts/kora-hero.md`](../templates/v0_prompts/kora-hero.md) for the full prompt that scaffolds this component.

---

## Hard Constraints

| Constraint | Detail |
|---|---|
| No custom native modules in Expo Go | Expo Go ships a fixed set of modules. Any package that requires a native `.xcframework` / `.aar` that is not in Expo Go's bundle will crash. |
| Custom modules require EAS Build | To use packages outside Expo Go's bundle (e.g., `react-native-audio-toolkit`), run `eas build --profile preview` to produce a custom dev client. This takes ~15 min the first time. |
| LAN only for QR preview | Expo Go connects over LAN by default. Tunnel mode (`npx expo start --tunnel`) uses `ngrok` to bridge firewalled networks but adds ~100 ms latency — unsuitable for real-time pitch detection. |
| iOS simulator has no mic | Test mic features on a real device; the iOS simulator's mic is always silent. |
| Expo Go SDK version must match | The Expo Go app version must match your project's SDK version. Mismatches produce a red error screen. Run `npx expo upgrade` to align. |

---

## Cross-links

- Decision guide across all three tools: [`deploy_bridge.md`](deploy_bridge.md)
- Copy-paste prompts for UI scaffolding: [`../templates/v0_prompts/`](../templates/v0_prompts/)
