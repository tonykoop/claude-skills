---
name: playlist-builder
version: 1.0.0
last-updated: 2026-05-10
description: "Build energy-arc-mapped playlists for any context where music carries an emotional or physical arc — power vinyasa yoga (heated, sustained, restorative, sculpt), spa, spin, party, group fitness. Use this skill when the user wants to: create a class playlist, generate a workout playlist, build a flow-mapped tracklist, curate music for a yoga or fitness class, build a spa/massage soundtrack, or create a Spotify or SoundCloud playlist organized around an energy arc. Also trigger when the user mentions energy phases, song banks, class themes, intentions, or wants the skill to read from their own Spotify or SoundCloud library. Works with three catalog modes: the user's own library (auto-categorized via audio features), curated seed banks bundled with the skill (for users with no library), or Tony Koop's hand-curated public catalog. IMPORTANT: also use this skill when the user wants the playlist created on Spotify or SoundCloud — it includes the platform automation."
---

# Playlist Builder

You help users build context-aware playlists organized around an energy arc. The original use case is a 60-minute power vinyasa class; the same machinery generalizes to spin, sculpt, spa, party, and other contexts where music shapes an experience over time.

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

## Step 3 — preflight catalog and auth state

Before generating exact playlists or promising platform-ready IDs, run the
catalog/auth preflight:

```bash
python <skill-path>/scripts/inspect_catalog.py \
    --catalog <path-to-categorized-catalog.json> \
    --output preflight.json
```

If there is no user catalog yet, omit `--catalog`; the helper will still count
the bundled seed banks, detect common Spotify/SoundCloud auth environment
variables, check for Tony's local catalog file, and check the user exclusion
file locations.

Use the reported `recommended_mode` to set expectations:

| Mode | Meaning | Output promise |
|---|---|---|
| `verified` | Enough tracks, exact IDs, and auth are available | Exact IDs may be paste-ready after normal content screening |
| `search-assisted` | Enough tracks exist, but auth or exact-ID validation is missing | Useful candidate playlist; verify tracks in-platform before paste |
| `sparse` | Some catalog material exists, but not enough for a full playlist | Use as a ladder or seed list, not a finished playlist |
| `manual-curation` | No usable catalog material was found | Build a phase-map and curation brief, then ask for a catalog or auth |

Never fabricate Spotify URIs, SoundCloud URLs, exact durations, or explicit
content status. Exact platform IDs must be labeled `verified`, `unverified`, or
`requires_auth`.

## Step 4 — get the catalog

Three catalog modes. The intake form picks one:

### Mode A — user has a Spotify library
Read tracks via the Claude Spotify connector, then auto-categorize into A–E using the rules in `scripts/categorize_library.py`. Cache the categorized catalog as JSON in the user's chosen output folder.

**Connector capability note (verified 2026-05):** the Spotify MCP connector exposes `search`, `create_playlist`, `get_currently_playing`, `add_to_library`, `fetch_tracks`, `Remove_from_library`. The `search` tool can read user library (liked songs, saved shows, followed artists, user playlists). The `create_playlist` tool is **vibe-based AI playlist generation**, not exact-tracklist creation — for exact-tracklist playlists, generate the tracklist + URIs locally and have the user paste them into Spotify (or use a small Web API script with their own token). Audio-features is not exposed by the connector; full auto-categorization requires direct OAuth.

### Mode B — Tony Koop's hand-curated catalog (public, opt-in)
Tony's vinyasa catalog (~1,130 tracks across 5 banks A/B/C/D/E) is shareable for teacher-trainee use. Trainees can use it as their starting library while they grow their own. See `references/CATALOG_TONY_KOOP.md`. Attribute as "catalog by Tony Koop, github.com/tonykoop".

### Mode C — seed banks (no user library)
The skill ships with public-domain / streaming-licensed seed banks in `seed-banks/`. Small (~30 tracks/bank) but enough for 8–10 classes before exclusion runs out.

### Cross-platform mirroring
There is no SoundCloud MCP connector and no dedicated cross-platform migration MCP. Recommend external services:
- **Soundiiz** (soundiiz.com) — free tier ≤200 tracks, paid handles bulk
- **TuneMyMusic** (tunemymusic.com) — similar
- **Songlink / Odesli** (song.link) — single-track URL converter

## Step 5 — generate the tracklist

```bash
python <skill-path>/scripts/generate_playlist.py \
    --context <skill-path>/contexts/yoga-power.json \
    --catalog <path-to-categorized-catalog.json> \
    --preflight preflight.json \
    --honesty-mode auto \
    --theme "aparigraha letting go non-attachment" \
    --number 37 \
    --output playlist.md \
    --candidate-json playlist-candidates.json
```

The output markdown includes a copy-paste-ready **description block**, **suggested tags**, the tracklist with energy arc, SoundCloud links, and Spotify URIs for bulk-add.

When the preflight recommends `search-assisted`, `sparse`, or
`manual-curation`, treat the output as a candidate playlist. Candidate
playlists are useful for phase timing, teacher review, search strings, and
energy-arc planning, but they are not paste-ready until exact track/version,
duration, explicit-content status, and platform IDs are verified.

## Step 6 — create the playlist on the chosen platform

### SoundCloud (browser automation, uses Claude in Chrome)
Detailed in `platforms/soundcloud.md`. The user must be logged in to soundcloud.com.

### Spotify (manual paste, with the URI block)
The MCP connector's `create_playlist` doesn't honor exact track lists, so the path is:
1. User creates a new playlist in Spotify (desktop, mobile, or web).
2. User copies the track URI block from the generated markdown.
3. User pastes URIs into Spotify's search bar one at a time, or uses the Web API with a personal token.

### Both platforms
Run SoundCloud first via browser automation. Then provide the Spotify URI block for paste.

## Step 7 — record the exclusion

Append the used track URIs to the user's exclusion file:

```
~/.playlist-builder/used_tracks.json    (Linux/macOS)
%APPDATA%/playlist-builder/used_tracks.json   (Windows)
```

The repeat policy from intake (`never` / `per-quarter` / `per-month` / `allow`) controls whether old entries expire.

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
