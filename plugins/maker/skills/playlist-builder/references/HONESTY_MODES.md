# Honesty Modes — playlist-builder

This reference defines the four output modes the generator may emit, the schema every row carries, and worked examples of each.

## Why this exists

Round 7 TwinGrid (lane Gina, May 2026) found that both Claude and Codex agents will fabricate plausible track names with confident-looking runtimes when the bundled catalog is sparse and no Spotify/SoundCloud auth is reachable. The teacher then discovers the gap at paste time, not at planning time.

The fix is structural: the skill picks an output *mode* based on what is actually in the catalog, and the mode determines what the agent is allowed to claim.

## The four modes

### `verified`

**Trigger condition:** any of:
- a categorized user catalog (Mode A) is loaded with ≥ 30 tracks; OR
- Spotify or SoundCloud auth is reachable; OR
- any seed bank has ≥ 8 tracks.

**Generator behavior:**
- Emit a numbered tracklist that fills every slot of the context profile.
- Every row has `exact_id_status: verified` and a real `spotify_uri` or `soundcloud_url`.
- `verification_required` is `false` for every row.
- The teacher can paste the URIs directly into a new playlist.

**Failure mode this protects against:** the legacy v1 generator assumed verified output unconditionally. When the catalog was actually sparse, it silently hallucinated.

### `search-assisted`

**Trigger condition:** Mode B (Tony Koop catalog reference loaded) but no auth and bundled banks are sparse.

**Generator behavior:**
- Emit a numbered tracklist — Mode B is large enough to carry a class.
- Mark each row's `exact_id_status` honestly: `verified` if it has a verified URI in the catalog, `unverified` if it is a search-string-only candidate.
- `verification_required` is `true` for every `unverified` row.
- Include a verification checklist at the bottom of the markdown (search → runtime ±10s → is_explicit check → arc-length recheck).

**Failure mode this protects against:** treating Mode B's search-string entries as if they were verified URIs.

### `sparse`

**Trigger condition:** bundled banks have content but no Mode B and no auth.

**Generator behavior:**
- Do **not** emit a single numbered tracklist — the visual structure must make the verification gap obvious.
- Emit a **three-tier honesty block**:
  1. **Tier 1 — Verified bundled tracks.** Each row has `exact_id_status: verified` and a real URI from `seed-banks/*.json`.
  2. **Tier 2 — Copy-paste curation prompt.** A self-contained text block the teacher pastes into another LLM/tool to extend the catalog. Theme, energy arc, slot timings, and content filter must all be baked in.
  3. **Tier 3 — Recall-only candidate ladder.** Optional. Every row marked `exact_id_status: unverified` and `verification_required: true`. Offered as scaffolding, not as an answer.

**Failure mode this protects against:** blending verified and recall-only rows into a single ranked list, which makes the verification gap invisible to the teacher.

### `manual-curation`

**Trigger condition:** all banks empty, no Mode B, no auth.

**Generator behavior:**
- Emit ONLY:
  - The class metadata (theme, total runtime, level)
  - The slot-by-slot energy arc (phase, start/end minutes, target energy, BPM range, role)
  - The copy-paste curation prompt
- Do NOT emit any track names — even as candidates. The pool of training-recall guesses is too brittle when there is no anchoring evidence.

**Failure mode this protects against:** a fully-fabricated playlist masquerading as a real one because the empty catalog left no anchor to honest output.

## Required output schema fields

Every row of generator output, regardless of mode, carries these seven fields:

| Field | Type | Meaning |
|---|---|---|
| `phase` | string | Phase name from the context profile |
| `bank` | enum: `A`, `B`, `C`, `D`, `E` | Energetic role |
| `search_string` | string | Spotify/SoundCloud-ready search query |
| `approx_duration` | string | Best estimate, `mm:ss` or `~mm` |
| `exact_id_status` | enum: `verified`, `unverified`, `requires_auth` | Confidence in the platform ID |
| `verification_required` | boolean | True unless `exact_id_status == verified` |
| `platform_auth_available` | boolean | Mirrors the preflight `auth.any_platform_auth_available` field |

Optional fields: `spotify_uri`, `soundcloud_url`, `bpm`, `tags`, `verification_notes`. These are non-substitutable — they may augment, not replace, the seven required fields above.

## Worked example — `sparse` mode for a 60-minute yin class

Input: 60-minute yin core-restore class, theme "Hara — Coming Home to Center", `seed-banks/A.json` has Marconi Union "Weightless", B/C/D/E.json are empty, no Mode B, no Spotify auth.

Preflight result:
```json
{
  "recommended_output_mode": "sparse",
  "seed_banks": {"counts": {"A": 1, "B": 0, "C": 0, "D": 0, "E": 0}, "total_count": 1},
  "platform_auth_available": false
}
```

Generator output structure:

```markdown
# Hara — Coming Home to Center (60-min yin)

## Tier 1 — Verified bundled tracks

| phase | bank | track | spotify_uri | exact_id_status | verification_required |
|---|---|---|---|---|---|
| savasana | A | Weightless · Marconi Union (8:08) | spotify:track:5oLh8s49fbTuxKBL5n8sHE | verified | false |

## Tier 2 — Copy-paste curation prompt

[A self-contained prompt that bakes in the theme, energy arc, slot
 timings, content filter, and Tier 1 anchor placement.]

## Tier 3 — Recall-only candidate ladder (verify before paste)

| phase | bank | search_string | approx_duration | exact_id_status | verification_required |
|---|---|---|---|---|---|
| arrival | A | Hania Rani Glass Esja album | 5:00 | unverified | true |
| ... | ... | ... | ... | ... | ... |

## Verification checklist
- [ ] Search each Tier-3 track on Spotify; runtime within ±10 sec
- [ ] Confirm is_explicit=false on every track
- [ ] Confirm playlist totals 58-62 minutes after substitutions
```

## Worked example — `verified` mode

Input: same class, but the teacher has a 1,200-track categorized library cached.

Preflight result:
```json
{
  "recommended_output_mode": "verified",
  "user_catalog": {"loaded": true, "track_count": 1247}
}
```

Generator output structure:

```markdown
# Hara — Coming Home to Center (60-min yin)

| phase | bank | track | spotify_uri | exact_id_status |
|---|---|---|---|---|
| arrival | A | Glass · Hania Rani | spotify:track:... | verified |
| ... | ... | ... | ... | ... |

All rows verified. Playlist is paste-ready.
```

No three-tier block, no curation prompt, no verification checklist — they would be noise when every row is already verified.

## Mode override

The `--catalog-state` flag on `generate_playlist.py` accepts:
- `auto` (default) — runs preflight, honors result
- `verified` / `search-assisted` / `sparse` / `manual-curation` — forces a mode

Override is allowed for testing and for deliberate teacher choices ("I know my Mode B is loaded but I want the tier-3 ladder anyway"). Override does NOT relax the schema requirements — every row still carries the seven required fields, and `verification_required` is still calculated from `exact_id_status`.

## See also

- `scripts/inspect_catalog.py` — the preflight implementation
- `scripts/generate_playlist.py` — the generator that honors the mode
- `seed-banks/README.md` — bundled catalog state
