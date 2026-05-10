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

## Catalog/auth preflight schema

Run `scripts/inspect_catalog.py` before exact playlist generation. It emits a
JSON report like:

```jsonc
{
  "schema_version": 1,
  "seed_banks": {
    "counts_by_bank": {"A": 1, "B": 0, "C": 0, "D": 0, "E": 0},
    "total_tracks": 1,
    "platform_id_counts": {
      "spotify_uri": 1,
      "soundcloud_url": 0,
      "any_platform_id": 1
    }
  },
  "catalog": {
    "present": true,
    "counts_by_bank": {"A": 12, "B": 18, "C": 8, "D": 20, "E": 16},
    "total_tracks": 74,
    "platform_id_counts": {
      "spotify_uri": 74,
      "soundcloud_url": 0,
      "any_platform_id": 74
    }
  },
  "auth": {"spotify": false, "soundcloud": false},
  "tony_catalog": {"present": false},
  "exclusions": {"present": true},
  "recommended_mode": "search-assisted"
}
```

`recommended_mode` is one of:

- `verified`: enough tracks, exact IDs, and auth are available.
- `search-assisted`: enough tracks exist, but exact platform readiness is not
  verified.
- `sparse`: some catalog material exists, but not enough for a complete
  playlist.
- `manual-curation`: no usable catalog material was found.

## Candidate playlist schema

When exact IDs are not verified, `generate_playlist.py --candidate-json` emits
candidate entries instead of implying a paste-ready playlist:

```jsonc
{
  "context": "yoga-restorative",
  "theme": "hara core restore",
  "honesty_mode": "sparse",
  "platform_auth_available": false,
  "candidate_playlist_is_paste_ready": false,
  "verification_required": [
    "Treat search-assisted, sparse, and manual-curation outputs as useful planning aids, not paste-ready exact playlists.",
    "Only exact IDs marked verified should be bulk-pasted or automated into a platform playlist."
  ],
  "tracks": [
    {
      "phase": "Savasana",
      "bank": "A",
      "artist": "Marconi Union",
      "title": "Weightless",
      "search_string": "Marconi Union Weightless",
      "approx_duration": "8:08",
      "spotify_uri": "spotify:track:...",
      "soundcloud_url": null,
      "exact_id_status": "requires_auth",
      "verification_required": [
        "Confirm the exact platform result matches artist, title, and duration.",
        "Confirm explicit-content flags and disruptive vocals before teaching.",
        "Confirm playlist order, no shuffle, and crossfade settings in-platform."
      ],
      "platform_auth_available": false
    }
  ]
}
```

Candidate playlists are useful for teacher review, phase timing, and search
workflows. They are not paste-ready until exact track versions, durations,
explicit flags, and platform IDs are verified.

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
