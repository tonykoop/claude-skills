# Seed banks

Bundled, license-friendly tracks the skill ships with so users without their own catalog can build a playlist on day one. Each bank has ~30 tracks (target). With ~150 total tracks and lifetime exclusions, that's roughly 8–10 classes before the catalog runs out — enough for a teacher trainee to learn the flow, then graduate to their own library.

## Schema

Each bank is a JSON file: `A.json`, `B.json`, `C.json`, `D.json`, `E.json`.

```jsonc
[
  {
    "title": "Track Title",
    "artist": "Artist Name",
    "duration_ms": 287000,
    "spotify_uri": "spotify:track:xxxxxxxxxxxxxxxxxxxxxx",
    "soundcloud_url": "https://soundcloud.com/artist/track",   // optional
    "genre": "Ambient",
    "bpm": 72,
    "tags": ["meditation", "drone", "no-percussion"],
    "license_note": "Spotify streaming"                        // why this is OK to include
  }
]
```

## Status

- **A.json** — example with one track populated. Add ~29 more.
- **B.json, C.json, D.json, E.json** — empty arrays. To be filled.

## Curation guidelines

- Prefer tracks available on **both Spotify and SoundCloud** so the seed banks work on either platform.
- Avoid region-locked tracks where possible. If a track is only available in some regions, note it in `license_note`.
- For **Bank C**, lyrics matter — pick tracks with clear, theme-friendly lyrical content. Universal themes (let go, rise, breathe, return, surrender, gratitude, courage) score better than narrowly specific ones.
- Diversity matters more than coolness. A trainee in Boise should be able to use the same banks as one in Berlin.
