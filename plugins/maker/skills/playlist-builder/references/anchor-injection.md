# Anchor-Artist Injection Reference

Anchors are artists whose tracks provide a consistent sonic identity across a 4-week series. Every weekly playlist must include one unique track from each configured anchor artist.

## Default anchor artists

| Slot | Default artist | Rationale |
|---|---|---|
| Anchor A | Lane 8 | Melodic progressive house; broad tempo range (120–128 BPM); teach-friendly |
| Anchor B | Tinlicker | Deep/melodic house; more introspective; strong for warm-up and heart-opener |

Both defaults are configurable — see `config/anchor-artists.yaml`.

## No-repeat rule

Within a series (typically 4 weeks / 4 playlists), the same track **must not** appear twice across any anchor slot. The exclusion set is maintained in the series state file (`contexts/series/state.json`, key `anchor_exclusions`).

### Enforcement

1. At generation time, load `anchor_exclusions` from the state file.
2. For each anchor slot, draw a candidate track from the anchor's library or API results.
3. Skip any candidate already in `anchor_exclusions`.
4. If no candidates remain (all tracks exhausted), emit a warning: `ANCHOR POOL EXHAUSTED: [artist] — all tracks used across this series. Start a new series or remove oldest exclusions.`
5. Commit the selected track to `anchor_exclusions` before writing the playlist.

## Configuration file

`config/anchor-artists.yaml` schema:

```yaml
anchor_artists:
  - slot: A
    name: "Lane 8"
    spotify_artist_id: "0XNa1vTidXlvJ2gHSsRi4A"
    preferred_phases: [warm_up, peak, heart_opener]  # see anchor-phase-placement.md
    bpm_range: [118, 130]
    library_tag: lane8  # tag in the user's local playlist library, if any
  - slot: B
    name: "Tinlicker"
    spotify_artist_id: "6bIbLEHj0CjHKjxv9t2Ohu"
    preferred_phases: [warm_up, heart_opener, savasana]
    bpm_range: [116, 126]
    library_tag: tinlicker
```

Users can add/replace anchor slots. The series generator reads this file at start and respects the full list.

## User-configurable list

If the user specifies different anchor artists ("use Innellea and Ben Böhmer instead"), rewrite `anchor_artists` in the config and confirm. Maintain the same no-repeat and phase-placement rules.
