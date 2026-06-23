> **Status: Speculative / Far-Future** — vision capture only, not a build plan.

# Model-Agnostic / BYOK Architecture

The inference engine is a utility, not a platform. A personal-app platform built on top of a single provider's API is not portable — it is merely a skin on that provider's lock-in. The goal is a clean separation between the tasks an agent performs and the model that performs them, so the user can swap, upgrade, downgrade, or self-host the inference layer without touching the applications built on top.

## Core Principle: LLM as Swappable Utility

The platform treats an LLM the same way a UNIX process treats a file descriptor — an abstract handle to a capability, not a named dependency. Micro-apps declare what they need from inference (latency, context window, tool-call support, multimodal input) rather than which provider delivers it. The routing layer resolves declarations to concrete endpoints at runtime.

```
Micro-app declares:
  inference_profile: "low-latency, tool-calls, ≤128k context"

Swap-Out Registry resolves:
  → claude-haiku-4-5 (local preference)
  → [fallback] gpt-4o-mini (if Haiku quota exhausted)
  → [offline fallback] llama-3.1-8b via Ollama (if no network)
```

The micro-app never imports an SDK. It calls the platform's inference interface; the platform calls the provider.

## Swap-Out Registry

The Swap-Out Registry is the local routing table that maps inference profile declarations to provider endpoints.

### Registry schema (local JSON / SQLite)

```json
{
  "profiles": {
    "low-latency": {
      "preferred": { "provider": "anthropic", "model": "claude-haiku-4-5" },
      "fallback":   { "provider": "openai",    "model": "gpt-4o-mini" },
      "offline":    { "provider": "ollama",     "model": "llama-3.1-8b" }
    },
    "high-reasoning": {
      "preferred": { "provider": "anthropic", "model": "claude-opus-4-8" },
      "fallback":   { "provider": "openai",    "model": "o3" },
      "offline":    null
    },
    "multimodal": {
      "preferred": { "provider": "anthropic", "model": "claude-sonnet-4-6" },
      "fallback":   { "provider": "google",   "model": "gemini-2.0-flash" },
      "offline":    { "provider": "ollama",   "model": "llava-v1.6" }
    }
  }
}
```

Users can edit this file directly (it is plain JSON, not a binary blob) or through the command hub's model selector.

### Routing decision tree

```
1. User has set a session-level override in the command hub → use it
2. Micro-app declares a named profile → look up in registry, try preferred
3. Preferred provider unreachable (network error / quota) → try fallback
4. Fallback unreachable → try offline, or surface error if offline is null
5. All routes fail → halt the micro-app task and notify the user
```

Every routing decision is logged to the local context graph: which provider served which request, latency, and token cost. The user can query "how much have I spent on OpenAI this week?" without leaving the platform.

## BYOK — Bring Your Own Key

Each provider entry in the registry has a corresponding key slot. Keys live in the local OS keychain (Keychain Access on macOS, Credential Manager on Windows) — never in environment variables, never in files, never transmitted to the platform's own servers (there are none).

### Key management

| Operation | Where it happens |
|---|---|
| Initial key entry | Command hub "Keys" panel → writes to OS keychain |
| Key rotation | Same panel; old key is overwritten, not archived |
| Key revocation | Remove the entry; the platform immediately falls back to the next route |
| Key audit | Local log: which key was used for which request, timestamp, token count |

The platform never proxies keys. If the user wants to use a corporate API key through a proxy, they configure the proxy URL in the provider's registry entry — the platform passes requests to that URL, and the key management is handled by the proxy.

### Zero-knowledge guarantee

The platform cannot exfiltrate keys because there is no platform server. All routing happens in the local container. Keys go directly from the OS keychain to the provider's HTTPS endpoint via a local TLS connection. The platform process itself is the only intermediary.

## Local State Ownership

All state produced by micro-apps stays local by default.

### State layers

| Layer | Format | Location | Sync |
|---|---|---|---|
| **Context Graph** | SQLite | `~/.local/share/personal-apps/context.db` | Never, unless user opts in |
| **Blueprint Store** | JSON files | `~/.local/share/personal-apps/blueprints/` | Optional encrypted export |
| **Session recordings** | WAV / MIDI | User-chosen directory | User-managed |
| **Model response cache** | SQLite (keyed by prompt hash) | `~/.cache/personal-apps/` | Never |
| **Preferences & registry** | JSON | `~/.config/personal-apps/` | Optional cross-device sync |

### Data portability

Every data layer is in an open, documented format:

- **SQLite** databases can be opened by any SQLite-compatible tool
- **JSON** blueprints can be read, edited, or shared by any text editor
- **WAV / MIDI** recordings are standard audio formats

The user can back up their entire personal-app state with a single `rsync` or Time Machine snapshot.

### No home-call telemetry

The local container does not phone home. No usage data is reported to any third party, including the inference providers (beyond what is inherent in the API call itself — providers see the prompt, not the surrounding context graph or user identity).

## Per-Task Model Selection

Some tasks benefit from a heavier model; others need low latency more than high accuracy. The platform supports task-level overrides without the user having to think about it:

| Task type | Default profile | Rationale |
|---|---|---|
| Intent translation (NL → task spec) | `low-latency` | Needs to feel instant; most intents are simple |
| Complex orchestration planning | `high-reasoning` | Rare; user can wait a few seconds |
| Multimodal analysis (photo, audio) | `multimodal` | Requires vision/audio capability |
| Background blueprint generation | `high-reasoning` | Runs overnight; latency irrelevant |
| Context graph summarization | `low-latency` | Frequent; must not feel sluggish |

The user can promote or demote any task's default profile from the command hub.

## Related Captures

- [personal_apps.md](personal_apps.md) — the micro-app lifecycle that makes inference calls
- [ui_states.md](ui_states.md) — the command hub model selector UI
- [blind_spot_engine.md](blind_spot_engine.md) — the overnight Shadow Worker that uses `high-reasoning` profile
