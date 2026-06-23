# Changelog — playlist-builder

## 0.5.0 — 2026-06-22 (audio-dynamic — movement→music sync engine, Epic #471)

Five new scripts, five reference docs, five test modules, one JSON schema, one example:

- **`scripts/texture_map.py`** — kinetic-texture → sonic mapping; `TEXTURE_SONIC_MAP` for 6
  textures (staccato/fluid/tutting/explosive/grounded/suspended); composite textures via `+`.
- **`scripts/bpm_match.py`** — BPM matching to choreography blocks; 70/30 BPM+energy ranking.
- **`scripts/sonic_anchor.py`** — `AnchorTag` dataclass + `align_timeline()` to shift routine
  timeline so choreographic peaks land on audio drop/breakdown timestamps.
- **`scripts/movement_bridge.py`** — `build_mix_plan()` composes texture filter → BPM match →
  anchor alignment; `MovementRoutinePayload` / `MixPlan` / `MixBlock` dataclasses;
  `validate_payload()` with optional `jsonschema` pass.
- **`scripts/release_hook.py`** — `compile_release()` writes
  `choreo_script.md + audio_mix_plan.json + provenance_block.json` (SHA-256 + ISO-8601 stamp);
  non-blocking StudioPipeline handoff via `STUDIOPIPELINE_HOOK_URL`.
- **`schemas/agent_packets/MovementRoutinePayload.schema.json`** — JSON Schema 2020-12 for the
  movement-engine constraint payload.
- **`references/KINETIC_TEXTURE_MAP.md`**, **`AUDIO_TRIGGER_ANCHORS.md`**,
  **`MOVEMENT_BRIDGE_CONTRACT.md`**, **`RELEASE_HOOK_CONTRACT.md`** — full spec docs.
- **`examples/interpretive-dance-release.md`** — worked end-to-end hip-hop example.
- **`SKILL.md` Audio-Dynamic section** — additive section documenting all new capabilities.
- **`docs/dj_handoff.md`** (story #485) — tagged with `Story: #485` header; authored under
  Epic #478 but satisfies all #485 acceptance criteria.
- 57 new tests across 5 test modules, all passing.

## 0.3.0 — 2026-06-20 (mastering backend handoff)

Adds a thin public client for the private mastering / MIR-critique / album-builder backend.
All mastering logic stays in `tonykoop/StudioPipeline-Selecta`; this release only adds the
handoff contract and a gracefully-degrading client stub.

- **`scripts/mastering_backend.py`** — `call_mastering_backend()` + typed dataclasses
  (`MasteringHandoff`, `MasteringTrack`, `MasteringIntent`, `MasteringBackendResult`).
  Reads `PLAYLIST_MASTERING_BACKEND_URL` / `PLAYLIST_MASTERING_BACKEND_TOKEN` from env;
  returns `available=False` silently when unconfigured or on any network error.
  No third-party dependencies — stdlib only (`urllib`, `dataclasses`, `json`).
- **`references/MASTERING_BACKEND_CONTRACT.md`** — documents the public/private boundary,
  backend discovery, `mastering-handoff-v1` payload schema, response schema, and graceful
  degradation behaviour.
- **`SKILL.md` Step 6 (optional) — mastering backend handoff** — added between Step 5
  (platform creation) and Step 7 (exclusion recording). Existing Step 6 renumbered to Step 7.
- Version bump: 0.2.0 → 0.3.0.

## 0.2.0 — 2026-06-19 (eval suite)

Adds the first machine-runnable eval suite (5 evals) and bumps SKILL.md to v0.2.0.

- `evals/evals.json` — 5 evals: preflight-required-before-tracklist,
  no-fabrication-when-sparse (three-tier honesty block), content-propriety-
  filter default (explicit tracks filtered), teach-friendliness weighting
  for D-bank peak selection, and unknown-context fallback disclosed.

## 0.1.0 — 2026-05-10

Initial repo snapshot (sourced from `/home/tony/.claude/skills/playlist-builder`)
plus the catalog/auth-state preflight contract from issue #72.

- **New `scripts/inspect_catalog.py`** — preflight that reports seed-bank
  counts, Mode B (Tony catalog) presence, Spotify/SoundCloud auth signals,
  and a `recommended_output_mode` field with one of four values:
  `verified`, `search-assisted`, `sparse`, `manual-curation`.
- **`SKILL.md` Step 3.5 — catalog/auth-state preflight (REQUIRED)** —
  spelled out as required, not optional, before any tracklist generation.
  Driven by lessons from Round 7 TwinGrid lane Gina, where both Claude
  and Codex agents fabricated plausible-but-unverified track names when
  the bundled catalog was sparse.
- **`SKILL.md` output schema** — every generator row must carry the seven
  required fields: `phase`, `bank`, `search_string`, `approx_duration`,
  `exact_id_status`, `verification_required`, `platform_auth_available`.
- **`SKILL.md` "When candidate playlists are useful but not paste-ready"** —
  documents the verification contract for `search-assisted` and `sparse`
  outputs.
- **`scripts/generate_playlist.py`** — added `--catalog-state {auto,
  verified, search-assisted, sparse, manual-curation}` and `--skill-dir`
  flags; `--catalog` is no longer required when mode is `sparse` or
  `manual-curation`. New `emit_honesty_block()` produces the three-tier
  output for `sparse` mode and the curation-prompt-only output for
  `manual-curation` mode.
- **`references/HONESTY_MODES.md`** — full taxonomy, schema, and worked
  examples for each mode.
- **`tests/test_inspect_catalog.py`** — 10 focused unit tests covering
  every mode-selection path, malformed-JSON robustness, missing-file
  handling, and the schema contract.
- **Frontmatter** — added top-level `version` and `last-updated` to keep
  the skill out of `skills-meta` drift on day 1.
- **Source artifacts** — Round 7 evidence at
  `/tmp/twingrid-r7-claude-gina-yin-core-restore/skill-improvement-recommendation.md`
  and `/tmp/twingrid-r7-codex-gina-core-restore-yin/partner-peek-improvements.md`
  drove this design.
