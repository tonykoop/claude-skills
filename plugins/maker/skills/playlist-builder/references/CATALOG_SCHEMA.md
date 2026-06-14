# Catalog schema

The generator (`scripts/generate_playlist.py`) consumes a categorized catalog JSON. This is the schema.

```jsonc
{
  "version": 1,
  "source": "spotify" | "soundcloud" | "seed-banks" | "custom-xlsx",
  "user": "<optional user identifier>",
  "banks": {
    "A": [Track, ...],
    "B": [Track, ...],
    "C": [Track, ...],
    "D": [Track, ...],
    "E": [Track, ...]
  },
  "exclusions": ["spotify:track:...", "https://soundcloud.com/...", ...]
}
```

Where `Track` is:

```jsonc
{
  "title": "Track Title",
  "artist": "Artist Name",
  "duration_ms": 287000,
  "spotify_uri": "spotify:track:xxxxxxxxxxxxxxxxxxxxxx",   // either spotify_uri or
  "soundcloud_url": "https://soundcloud.com/...",          // soundcloud_url is required
  "genre": "Ambient",
  "bpm": 72,                                               // optional
  "tags": ["meditation", "drone"],                         // optional, used for theme matching
  "audio_features": { ... }                                // optional Spotify audio-features dict
}
```

## SoundCloud xlsx import

Tony's v1 catalog is a SoundCloud xlsx with these columns (the `All Tracks` sheet):

| Col | Field |
|---|---|
| 1 | Source playlist name (used to derive the bank) |
| 8 | Position within source playlist |
| 9 | Title |
| 10 | Artist |
| 11 | Duration ms |
| 12 | Duration formatted (e.g. `4:32`) |
| 13 | SoundCloud URL |
| 14 | Genre |
| 15 | BPM |
| 16 | Play count |
| 17 | Tags (semicolon-separated) |

The bank letter for each source playlist is mapped via `BANK_PLAYLISTS` in v1's `generate_playlist.py`. v2 reads the same xlsx and outputs the JSON schema above.
