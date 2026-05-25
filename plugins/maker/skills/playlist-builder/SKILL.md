---
name: playlist-builder
version: 0.1.0
last-updated: 2026-05-10
description: "Build energy-arc-mapped playlists for any context where music carries an emotional or physical arc — power vinyasa yoga (heated, sustained, restorative, sculpt), spa, spin, party, group fitness. Use this skill when the user wants to: create a class playlist, generate a workout playlist, build a flow-mapped tracklist, curate music for a yoga or fitness class, build a spa/massage soundtrack, or create a Spotify or SoundCloud playlist organized around an energy arc. Also trigger when the user mentions energy phases, song banks, class themes, intentions, or wants the skill to read from their own Spotify or SoundCloud library. Works with three catalog modes: the user's own library (auto-categorized via audio features), curated seed banks bundled with the skill (for users with no library), or Tony Koop's hand-curated public catalog. IMPORTANT: also use this skill when the user wants the playlist created on Spotify or SoundCloud — it includes the platform automation."
---

# Playlist Builder

You help users build context-aware playlists organized around an energy arc. The original use case is a 60-minute power vinyasa class; the same machinery generalizes to spin, sculpt, spa, party, and other contexts where music shapes an experience over time.

## Connectors

This skill works best with these MCP connectors. Claude will suggest connecting any that aren't already linked at the point they're needed (via `mcp__mcp-registry__suggest_connectors`).

- **Spotify** (`86925244-b3bb-415b-b7e8-6e3cd1392247`) — required for first-party playlist creation, currently-playing context, library reads, and audio-feature lookups for the auto-categorization mode. Suggest at the start of any non-seed-bank generation. Without it, the skill falls back to seed banks and Tony's hand-curated public catalog.

## Mental model — three ingredients

1. **Context profile** (`contexts/*.json`) — the named arc: phases, durations, energy targets, optional theme anchor.
2. **Song banks** — the catalog partitioned by energetic role (A = opening/closing, B = rising, C = theme anchor, D = peak, E = descent). The song-bank pattern is Tony Koop's own working method: keep repositories of favorite tracks grouped energetically so any class playlist becomes a matter of arranging, not searching.
3. **Exclusion tracking** — per-user state of what's been used, so playlists never repeat tracks.

A playlist is built by walking the context's phase list, drawing tracks from the relevant bank, respecting exclusions, then optionally inserting a theme-anchor track.

## The three-function music model (group-fitness music pedagogy)

Music in a fitness class is a teaching tool, not background. Every track choice should support these three functions — this is widely-discussed group-fitness pedagogy, not specific to any studio:

1. **Beat (Movement)** — the beat is clear and consistent so the instructor cues actions and breath on the beat. Two full reps of a movement or breath cycle should land cleanly on bars.
2. **Voice (Coaching)** — the middle of the track (especially during higher intensity sections) leaves headroom for the instructor's voice. No vocal pile-ups during peak intensity.
3. **Count (Transitions)** — predictable structure that supports an 8-count or 4-count countdown to transition between poses or reps.

Tracks that satisfy all three are *teach-friendly*. The skill should weight teach-friendliness when scoring tracks for C-bank theme anchors and D-bank peaks.

### Content propriety filter

Studio classes are public-facing. The skill filters tracks for studio-friendliness:
- **No explicit content** — filter out tracks with sexually explicit, defamatory, or otherwise offensive lyrics. Spotify's `is_explicit` flag is a useful first pass.
- **Tasteful** — music should support a positive room. The skill defaults to filtering `is_explicit=true`; user can opt in to allow.

## Step 1 — figure out what the user wants

If the user hasn't specified everything, **open the intake form** in their browser:

```
intake/intake.html
```

The form collects: platform (Spotify / SoundCloud / both), class type, duration, padding after class, theme, catalog source, must-include / avoid tracks, repeat policy.

If the user gives the answers conversationally, skip the form. Either path produces the same JSON config that drives the rest of the flow.

## Step 2 — pick the context profile

| Class type | Profile file | Notes |
|---|---|---|
| **Power Vinyasa** (60-min heated) | `yoga-power.json` | Steady build through Sun A, peak through Sun B |
| **Sustained Power Flow** (60-min, drill block) | `yoga-power-sustained.json` | Integration → Sun A & B → Drills → Standing → Savasana |
| **Sculpt / Yoga Sculpt** | `yoga-sculpt.json` | Drill-format, BPM-locked, repetitive movements with weights |
| **Restorative / Yin** (75-min) | `yoga-restorative.json` | Surrender energy throughout, long holds, conscious rest |
| **Vinyasa** (general) | `yoga-vinyasa.json` | The legacy 65-min arc |
| **Spa / Massage** | `spa-massage.json` | Drift profile, no peak |
| **Spin / Cycling** | `spin-bike.json` | Climb / sprint intervals |
| **Party / Event** | `party.json` | (TODO) |

If the user requests a class type that doesn't exist, fall back to `yoga-vinyasa.json` and surface that you did so.

## Step 3 — get the catalog

Three catalog modes. The intake form picks one:

### Mode A — user has a Spotify library
Read tracks via the Claude Spotify connector, then auto-categorize into A–E using the rules in `scripts/categorize_library.py`. Cache the categorized catalog as JSON in the user's chosen output folder.

**Connector capability note (verified 2026-05):** the Spotify MCP connector exposes `search`, `create_playlist`, `get_currently_playing`, `add_to_library`, `fetch_tracks`, `Remove_from_library`. The `search` tool can read user library (liked songs, saved shows, followed artists, user playlists). The `create_playlist` tool is **vibe-based AI playlist generation**, not exact-tracklist creation — for exact-tracklist playlists, generate the tracklist + URIs locally and have the user paste them into Spotify (or use a small Web API script with their own token). Audio-features is not exposed by the connector; full auto-categorization requires direct OAuth.

### Mode B — Tony Koop's hand-curated catalog (public, opt-in)
Tony's vinyasa catalog (~1,130 tracks across 5 banks A/B/C/D/E) is shareable for teacher-trainee use. Trainees can use it as their starting library while they grow their own. See `references/CATALOG_TONY_KOOP.md`. Attribute as "catalog by Tony Koop, github.com/tonykoop".

### Mode C — seed banks (no user library)
The skill ships with public-domain / streaming-licensed seed banks in `seed-banks/`. Banks are intentionally sparse — the bundled catalog can seat one or two anchor tracks per class but cannot fill a 60-minute arc on its own. **Always run the catalog/auth-state preflight before assuming a bank is rich enough to fill the arc** — see Step 3.5.

### Cross-platform mirroring
There is no SoundCloud MCP connector and no dedicated cross-platform migration MCP. Recommend external services:
- **Soundiiz** (soundiiz.com) — free tier ≤200 tracks, paid handles bulk
- **TuneMyMusic** (tunemymusic.com) — similar
- **Songlink / Odesli** (song.link) — single-track URL converter

## Step 3.5 — catalog/auth-state preflight (REQUIRED)

Before generating any tracklist, **run the preflight** so you know whether you are allowed to emit exact platform IDs. This step is required, not optional. It exists because Round 7 TwinGrid showed both Claude and Codex agents will fabricate plausible-but-unverified track names (with confident-looking runtimes) when the bundled catalog is sparse and no auth is reachable, leaving the teacher to discover the gap at paste time.

```bash
python <skill-path>/scripts/inspect_catalog.py \
    --skill-dir <skill-path> \
    [--catalog <path-to-categorized-catalog.json>]
```

The preflight reports seed-bank counts, Tony catalog (Mode B) presence, auth signals (Spotify/SoundCloud env vars or cache), and a `recommended_output_mode` field with one of four values:

| Mode | When the preflight returns it | What the generator must do |
|---|---|---|
| `verified` | ≥30 tracks in user catalog OR auth available OR any bank ≥ 8 tracks | Emit exact tracklist; every row is `exact_id_status: verified`. |
| `search-assisted` | Mode B (Tony catalog) loaded but no auth and bundled banks sparse | Emit tracklist; mark each row's `exact_id_status` as `verified` (if it has a verified URI) or `unverified` (if search-only). |
| `sparse` | Bundled banks have content but no Mode B and no auth | Emit a **three-tier honesty block** (verified bundled tracks; copy-paste curation prompt; recall-only candidate ladder). Do NOT emit a single numbered "tracklist" — the tiers must be visually distinct so the teacher can see which lines are load-bearing. |
| `manual-curation` | All banks empty, no Mode B, no auth | Emit ONLY the copy-paste curation prompt and the slot-by-slot energy-arc plan. No track names, even as candidates. |

See `references/HONESTY_MODES.md` for the full taxonomy, output schema, and worked examples.

## Step 4 — generate the tracklist

```bash
python <skill-path>/scripts/generate_playlist.py \
    --context <skill-path>/contexts/yoga-power.json \
    --catalog <path-to-categorized-catalog.json> \
    --catalog-state auto \
    --theme "aparigraha letting go non-attachment" \
    --number 37 \
    --output playlist.md
```

The `--catalog-state` flag accepts `auto` (default — runs the preflight and honors the result), `verified`, `search-assisted`, `sparse`, or `manual-curation`. The output markdown includes a copy-paste-ready **description block**, **suggested tags**, and an arc-aligned tracklist or honesty block depending on mode.

### Output schema fields (always present, regardless of mode)

Every row of generated playlist output carries:

- `phase` — phase name from the context profile
- `bank` — A, B, C, D, or E
- `search_string` — Spotify/SoundCloud-ready search query
- `approx_duration` — best estimate (`mm:ss` or `~mm`)
- `exact_id_status` — `verified` | `unverified` | `requires_auth`
- `verification_required` — boolean; true unless `exact_id_status == verified`
- `platform_auth_available` — boolean; mirrors the preflight result

Rows MAY also carry `spotify_uri`, `soundcloud_url`, `bpm`, `tags`, `verification_notes`. These are optional and never substitute for the required fields above.

## Step 5 — create the playlist on the chosen platform

### SoundCloud (browser automation, uses Claude in Chrome)
Detailed in `platforms/soundcloud.md`. The user must be logged in to soundcloud.com.

### Spotify (manual paste, with the URI block)
The MCP connector's `create_playlist` doesn't honor exact track lists, so the path is:
1. User creates a new playlist in Spotify (desktop, mobile, or web).
2. User copies the track URI block from the generated markdown.
3. User pastes URIs into Spotify's search bar one at a time, or uses the Web API with a personal token.

### Both platforms
Run SoundCloud first via browser automation. Then provide the Spotify URI block for paste.

## Step 6 — record the exclusion

Append the used track URIs to the user's exclusion file:

```
~/.playlist-builder/used_tracks.json    (Linux/macOS)
%APPDATA%/playlist-builder/used_tracks.json   (Windows)
```

The repeat policy from intake (`never` / `per-quarter` / `per-month` / `allow`) controls whether old entries expire.

## When candidate playlists are useful but not paste-ready

A candidate playlist (any output where the preflight returned `search-assisted` or `sparse`) is a **drafting tool, not a finished artifact**. It is useful because:

- It bootstraps a teacher who has zero playlist faster than a blank page would.
- It enforces the energy arc, BPM ceiling, slot timings, and content filter even when track-level certainty is low.
- It carries the theme into every search string so the teacher's verification step is theme-aware.

It is NOT paste-ready because:

- Track titles and runtimes are recalled from training data and may be wrong, outdated, or refer to alternate album versions whose duration breaks the arc.
- The `is_explicit` flag cannot be checked without a live API call.
- Geographic licensing means a track that exists for the agent may not stream for the teacher's region.

**Rule:** every candidate playlist must include a verification checklist for the teacher (search each track on the platform, confirm runtime ±10 sec, confirm `is_explicit=false`, confirm the playlist still totals the arc length after substitutions). The output schema's `verification_required` field is the machine-readable form of that contract.

## Theme curation tips

- Search for tracks with lyrics or titles that match themes like "Trust," "Self-Love," "Community," "Letting Go," "Showing Up," "Resilience."
- A theme often has a **Launch** track (early in the build) and a **Land** track (the C-bank theme anchor at minute 20-30).
- Universal themes (let go, rise, breathe, return, surrender, gratitude, courage) score better than narrowly specific ones — they pull from a richer track pool.
- Yamas and niyamas (the first two limbs of yoga's 8-limb path) are evergreen — Aparigraha, Ahimsa, Santosha, etc.

## For Tony specifically

Tony's `yoga-playlist-builder` v1 still works as before — his catalog is in `references/TonyKoop_Yoga_Playlists.xlsx` (gitignored, lives on his machine). Tony can keep using v1 or migrate to v2 by passing `--context contexts/yoga-vinyasa.json`. His public playlists are also offered to trainees as Mode B.

## TODOs

- [ ] Spotify Web API OAuth flow (full library pull + `audio-features`)
- [ ] Seed banks B/C/D/E populated (only A has an example track)
- [ ] Intake form energy-arc preview that updates live as the class type changes
- [ ] Lyric-based theme matching for C bank (Genius/Musixmatch)
- [ ] Helper script that adds URI list to a Spotify playlist via user's Web API token
- [ ] Port v1 duration-enforcement loop to v2 generator

See `../../DESIGN.md` for the full design doc.
