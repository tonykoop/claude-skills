> **Status: Speculative / Far-Future** — vision capture only, not a build plan.

# Ambient UI + Command-Hub States + Local Container

Personal apps should meet the user where they are — not demand that the user come to them. The same micro-app that presents as a full studio window on a desktop should collapse to a floating HUD during a hands-on session and dissolve entirely into audio and haptic cues when the user is away from a screen. The UI is not a fixed artifact; it is a projection of the task state onto whatever surface is available.

## Three UI States

### State 1 — Studio Window (Focused Mode)

A full-featured, desktop-native window that behaves like a traditional application. Used when the user is seated and actively engaged.

| Element | Description |
|---|---|
| **Command hub** | Top-level bar with search, active micro-apps, context graph peek, and model selector |
| **Canvas area** | Task-specific content: sheet music with fingering overlays, pitch waveform, spaced-repetition flash cards, etc. |
| **Timeline scrubber** | Session history; scrub back to any moment in the current session |
| **Ambient sidebar** | Quiet feed of context graph activity — goals progressing, related sessions, upcoming scheduled drills |
| **Inline chat** | Direct conversation with the agent without leaving the app surface |

The Studio window is the authoring surface: the user can reshape the micro-app by talking to the agent in the inline chat, and the changes take effect immediately in the canvas.

### State 2 — Floating HUD (Ambient Mode)

A small, always-on-top overlay that collapses to a corner of the screen or clips to a hardware frame (e.g. a music stand mount). Used during physical practice, cooking, exercise, or any activity where the user cannot give full attention to a screen.

| Element | Description |
|---|---|
| **Status ticker** | Current task name, elapsed time, and next prompt |
| **Micro-feedback strip** | One-line result of the most recent action (e.g. "Interval: ✓ minor sixth") |
| **Quick-expand button** | Tap to expand into a Studio window |
| **Voice-first trigger** | Wake word or button activates voice input without requiring a tap |

The HUD has no mouse-driven chrome. All interaction is touch or voice. It writes the same session data to the Context Graph as the Studio window; the representation changes, not the substance.

### State 3 — AR Projection (Immersive Mode)

Speculative near-term extension. Spatial overlays anchored to physical objects: fingering diagrams projected onto an instrument's fretboard, pitch guides floating above a keyboard, a rhythm grid superimposed on a drum kit. The device (phone camera, AR glasses) supplies the anchor point; the micro-app supplies the overlay content.

| Element | Description |
|---|---|
| **Spatial anchor** | Object recognition binds overlays to a detected instrument |
| **Gesture input** | Hand-pose detection interprets playing gestures as input events |
| **Haptic beat** | Wearable vibration cue for rhythm guidance |
| **Gaze dismiss** | Look away from anchor for >2 seconds to dissolve the overlay |

AR mode is read-only for app configuration: the user cannot reshape the micro-app while in AR mode; they return to HUD or Studio to do that.

## Ambient / Dematerialized UI

Beyond the three explicit states, some task outputs are best delivered without any visual surface at all:

- **Audio cues**: a tone to mark a transition (session ending, drill phase shift, goal milestone reached)
- **Haptic pulses**: rhythm keeper delivered to a wearable; error-tap when a note is missed
- **Notification fragments**: a single sentence pushed to the system notification center ("Your B-section recall accuracy improved 8% this week")
- **Voice synthesis**: the agent speaks a coaching comment at a natural pause in practice

Dematerialized output does not require a display. A user practicing an instrument in a room without a screen should still receive coaching feedback through audio and haptics. The local container is responsible for routing output to the appropriate channel based on detected context (display available? wearable connected? microphone active?).

## Local Container

The local container is the runtime host for all micro-apps. It is a persistent background process — not a cloud service, not a browser tab — that survives across sessions and manages the lifecycle of every micro-app.

### Container responsibilities

| Responsibility | Detail |
|---|---|
| **Process isolation** | Each micro-app runs in a sandboxed subprocess with scoped filesystem access |
| **Context Graph I/O** | Serializes all session writes to the SQLite context graph; no micro-app writes directly |
| **Module registry** | Maintains the catalog of available capability modules and their versions |
| **State router** | Decides which UI state to render based on available surfaces and user-declared context |
| **Audio session management** | Holds a single CoreAudio (macOS) or WASAPI (Windows) session; micro-apps request audio slices from it |
| **Background sync** | Optional encrypted sync of the blueprint store and context graph to a user-controlled endpoint |

### Technology candidates

| Option | Trade-offs |
|---|---|
| **Electron** | Mature, large ecosystem, high memory footprint |
| **Tauri** | Smaller footprint, Rust core, tighter OS integration, smaller plugin ecosystem |
| **Native daemon + web renderer** | Maximum performance, but platform-specific maintenance burden |

The choice of container is an implementation detail orthogonal to the micro-app model. The container exposes a stable IPC interface; micro-apps target that interface, not the container's internals.

### Startup and teardown

The container starts at login (or on first micro-app request) and runs until the user explicitly exits. Individual micro-apps start and stop on demand. The container itself is never torn down mid-session; only micro-apps are.

## Command Hub

The command hub is the user's single entry point across all micro-apps and UI states. It is persistent — always reachable from the HUD expand button, a keyboard shortcut, or the Studio window's top bar.

Key functions:

1. **Intent entry**: natural-language field that triggers Translation → Execution → Deployment
2. **Active apps list**: all currently running micro-apps with their state and elapsed time
3. **Recent blueprints**: the last N blueprints, launchable with one click
4. **Context graph peek**: a summary of today's activity drawn from the graph
5. **Model selector**: override which LLM handles this session's Translation layer

## Related Captures

- [personal_apps.md](personal_apps.md) — the micro-app lifecycle that populates each UI state
- [model_agnostic.md](model_agnostic.md) — model selector mechanics
- [decentralized_hub.md](decentralized_hub.md) — how the local container participates in P2P agent jams
