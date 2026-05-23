# Spotify platform adapter

## Use the MCP connector when possible

If the user has the Spotify MCP connector enabled in Claude Desktop (most common case), prefer it. The relevant tools:

- `mcp__spotify__search` — `(query, type="track", limit=20)` → returns tracks with `uri` field
- `mcp__spotify__create_playlist` — `(name, description, public=false, tracks=[uris])` → creates the playlist
- `mcp__spotify__get_currently_playing` — useful for sanity-checking the connector

Flow when using the MCP connector:

1. For each track in the generated tracklist, call `mcp__spotify__search` with `"<artist> <title>"`. Take the top result's `uri`.
2. If the catalog already has a Spotify URI (seed banks always do), skip the search.
3. Once all URIs are collected, call `mcp__spotify__create_playlist` with the playlist name, the user's stated description (often the theme), and the URI list.
4. Return the playlist URL to the user so they can verify.

Always **ask the user for permission before creating the playlist** — this writes to their account.

## Direct Web API (catalog-import flow)

Out of MVP scope, but documented for the next milestone. To pull a user's saved tracks and auto-categorize them into A–E banks:

1. **OAuth 2.0 PKCE flow** — register a Spotify app, redirect URI `http://localhost:8888/callback`. Required scopes: `user-library-read` (saved tracks), `playlist-read-private` (their existing playlists), `user-read-private`.
2. **`GET /v1/me/tracks`** — paginated, 50 at a time. Pull every saved track.
3. **`GET /v1/audio-features?ids=...`** — batched 100 at a time. Returns `energy`, `valence`, `tempo`, `acousticness`, `instrumentalness`, `speechiness`, `danceability` for each track.
4. **Apply the bank rules** in `scripts/categorize_library.py`:

   | Bank | Energy | Valence | Tempo | Other |
   |---|---|---|---|---|
   | A | < 0.30 | any | < 80 | high acousticness or high instrumentalness |
   | B | 0.30–0.60 | 0.30–0.70 | 90–115 | low to mid speechiness |
   | C | 0.40–0.80 | high | any | **high speechiness or vocals detected** (theme anchor needs lyrics) |
   | D | > 0.70 | > 0.50 | 115–135 | low acousticness, high danceability |
   | E | 0.30–0.60 | mid | 80–110 | mid acousticness |

5. Write the categorized catalog to `~/.playlist-builder/catalog_<user>.json` so we don't re-pull on every run.

## Caveats

- Spotify's `audio-features` is heuristic — a slow ballad with strong vocals can land in B if its energy reading is high. Surface auto-categorization to the user with a "review your A bank" / "review your D bank" pass before first use.
- The `speechiness` field doesn't reliably distinguish lyrics from spoken word. For better C-bank detection, a future enhancement would query lyrics from Genius or Musixmatch.
- Track availability varies by region. The catalog should record the user's market and filter accordingly.
