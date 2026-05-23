# Spin arc — what Tony's old playlists reveal

Tony's three public Spin playlists on Spotify (Spin-1, Spin-2, Spin-3, all 2011-2012 vintage) were analyzed to derive the structural pattern in `contexts/spin-bike.json`. Tracks themselves are dated; the **shape** is what's portable.

## The data

| Playlist | Tracks | Duration | Avg track length |
|---|---|---|---|
| Spin-1 | 8 | 41:54 | 5:14 |
| Spin-2 | 6 | 34:48 | 5:48 |
| Spin-3 | 8 | 41:02 | 5:08 |

## The shape (consistent across all three)

```
Energy
 10 │              ██████          ██████        <- Peak Wave 2 (final sprint)
  9 │      ██████  ██████          ██████
  8 │      ██████  ██████          ██████  ██
  7 │      ██████  ██████          ██████  ██
  6 │  ██  ██████  ██████          ██████  ██████
  5 │  ██  ██████  ██████  ██████  ██████  ██████
  4 │  ██  ██████  ██████  ██████  ██████  ██████ <- closing anthem
  3 │██  ██████  ██████  ██████  ██████  ██████
    └─────────────────────────────────────────────
     0    4    12    22    27    36    45 min
     ^warmup ^build ^peak ^recover ^peak2 ^cool
```

## Key takeaways

1. **Short, dense classes.** ~40 minutes total. That's shorter than the 45-60 min spin format common at gyms. Either Tony's classes ran short or these are the "ride portion" with separate warmup/cooldown elsewhere. Either way: the skill defaults to 40 min, acceptable 35-50 min.

2. **Few but long tracks.** 6-8 tracks, average 5-6 min each. Spin classes need long extended-mix trance and EDM anthems so each climb or sprint can ride a single track without an awkward fade.

3. **Two-peak structure.** Not one big buildup like a yoga peak — two separate climaxes with a recovery valley in between. This maps to the cycling reality of climb → sprint → catch breath → climb again → final sprint.

4. **Genre profile.** Progressive house, trance, EDM (Tiësto, Mat Zo, Above & Beyond, Avicii, deadmau5, Skrillex, Eric Prydz). Drum & bass shows up sparingly (Netsky in Spin-3). Chill-out / balearic at the end (Funki Porcini, Blue Tente).

5. **Emotional anthem closer.** Five of the six closing tracks across the three playlists have prominent vocals or emotional swells — Skrillex/Ellie Goulding's *Summit*, Forerunners' *Dragonfly*, Funki Porcini's *Long Road*. This is the "you did it" moment, not a comedown.

## How to use this for new spin playlists

- Keep the **shape** — warmup, build, peak wave 1, recovery, peak wave 2, anthem closer.
- **Update the artists.** The genre lane (prog house / trance / EDM) is timeless for spin, but the specific tracks are dated. Reach for current-era artists in those lanes: Lane 8, Yotto, Ben Böhmer, ARTBAT, Massano, RÜFÜS DU SOL, Anyma, etc.
- **Match BPM to cadence.** Climb tracks should be 60-90 BPM (slow legs, heavy resistance). Sprint tracks should be 125-150 BPM. The skill's `bpm_target` fields encode this per phase.
- **Long extended mixes are OK.** Unlike yoga (where a 7-min track in the wrong place stalls the flow), spin invites the long form.
