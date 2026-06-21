# Library-vs-API Track Sourcing Toggle

The playlist builder supports two track sourcing modes, switchable per-series or per-generation.

## Modes

### `library` mode (default)

Pulls tracks from the user's curated personal library — typically a Spotify playlist or tagged local collection.

- **Source**: User's Spotify library (saved tracks, playlists) or the skill's bundled seed banks
- **Matching**: Filter by energy tag, BPM range, and phase compatibility from existing library metadata
- **Guarantee**: Every suggested track is one the user already knows and has access to
- **Thin-catalog warning**: If fewer than 3 candidates exist for any phase, emit: `LIBRARY THIN: [phase] — only [N] candidates. Consider switching to API mode or adding more tracks to your [tag] playlist.`

### `api` mode

Discovers new matching releases via the Spotify API, filtered to match the week's energy profile.

- **Source**: Spotify new releases + artist-radio for anchor artists (Lane 8, Tinlicker) and related artists
- **Matching**: Audio-feature query — target `energy`, `danceability`, `tempo` ranges from the week's sonic blueprint
- **Filter**: `is_explicit=false` by default; studio-friendly filter on
- **Honest-candidate flag**: When the API returns a track the user hasn't heard, flag it as `NEW — unverified for teach-friendliness`; the user must confirm before it's committed to the playlist

### `hybrid` mode (future)

Fills from library first; falls back to API for phases where the library is thin. Not yet implemented; document as planned.

## Toggle configuration

In `contexts/series/state.json` (or per-series config):

```json
"sourcing_mode": "library",   // or "api" or "hybrid"
"api_sourcing": {
  "new_release_window_days": 90,
  "related_artist_depth": 2,
  "honest_candidate_flag": true
}
```

The user can switch modes mid-series. Switching from `library` to `api` mid-series does not affect already-generated weeks; only future weeks use the new mode.

## API sourcing — energy-profile matching

When in `api` mode, query Spotify for tracks matching the week's profile:

| Parameter | Week 1 | Week 2 | Week 3 | Week 4 |
|---|---|---|---|---|
| target_energy | 0.72 | 0.76 | 0.80 | 0.72 |
| target_tempo | 124 | 127 | 129 | 124 |
| target_danceability | 0.70 | 0.72 | 0.75 | 0.70 |
| min_tempo | 88 | 88 | 88 | 88 |
| max_tempo | 130 | 130 | 132 | 130 |

Values are illustrative; they pull from `sonic-blueprint.md` at generation time.

## Honest-candidate mode

When the catalog is thin (< 3 library candidates for a phase) and API sourcing is off, the skill falls back to honest-candidate mode:

1. List the best 1–2 library candidates (even if BPM is slightly off)
2. Flag them as `CATALOG THIN — [N] candidates; [artist/title] is closest match but [BPM difference] outside target range`
3. Ask the user to confirm or provide an alternative

Do not fabricate tracks or claim Spotify API results without actually querying.
