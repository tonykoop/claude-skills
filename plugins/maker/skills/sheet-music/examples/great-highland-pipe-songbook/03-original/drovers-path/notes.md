# Drover's Path

Original Heifer Zephyr commission for the Great Highland Pipe
(chanter).

## Brief

- **Instrument:** Great Highland Pipe (chanter) (`great-highland-pipe`)
- **Range:** G4 - A5 (all 9 chanter notes used)
- **Key:** A mixolydian (`K:Amix`)
- **Mood:** slow march, dignified, a drover walking cattle through
  highland mist
- **Form:** AABA, 32 bars total
- **Tempo:** q = 76 (slow march)
- **Meter:** 4/4
- **Build repo:** `tonykoop/great-highland-pipe` (placeholder; no
  build repo exists yet — the GHP is a v0.2 stress test, not a Tony
  build)

## Composition status — complete

The melody is filled in. AABA, 32 bars, all in the chanter's
9-note range. Doublings on long notes; throws on D where D follows
a lower pitch. No rests anywhere.

## Form & contour

- **A part (bars 1-8, repeated):** the *home* phrase. Anchors on
  low A, walks up to the fifth (E), settles, walks back down. Each
  long note carries a doubling — the doublings are the rhythm.
- **B part (bars 9-16):** the *bridge*. Rides the upper half of the
  chanter. The high A in bars 11-12 is the emotional peak — sit on
  it, let it ring, then descend back through F# and E into the home
  phrase.
- **Final A (bars 17-24):** restates the home phrase. The final
  cadence is a held low A under one continuous bag of air —
  eight beats, no waver.

## Ornament inventory

| Ornament | ABC | Used in |
|---|---|---|
| Doubling on A | `{GdG}A2` | A part: bars 1, 3, 5, 7; final A: bars 17, 19, 21, 23 |
| Doubling on low A (cadence) | `{GBG}A` | every long-A cadence |
| Doubling on B | `{GBG}B2` | bars 3, 19 |
| Doubling on C# | `{GdG}c2` | bars 1, 3, 5, 7 (and reprise) |
| Doubling on D | `{GeG}d2` | bars 2, 4, 6 (descents) |
| Doubling on E | `{GeG}e4` / `{ge}e2` | settled E's; B-part rises |
| Doubling on F# | `{gf}f2` | bars 4, 9, 10, 11, 13, 14 |
| Doubling on high A | `{gag}a2` | B-part climax |

## Practice tips

1. **Walk the A part first, doublings off.** Play just the principal
   notes at q=60. Get the contour into your hands. Then layer
   doublings back in one bar at a time.
2. **The B-part climb.** The leap from F# to high A in bar 11
   (`{ge}e2 {gf}f2 {gag}a4`) is the test. Build it from a long-tone
   exercise on F# -> A, then add the doubling.
3. **Held cadence — eight beats.** The final low A is one continuous
   tone for two bars worth of pulse. Don't lift the bag, don't let
   the tone wobble, don't anticipate the end. Hold steady for the
   whole eight.
4. **Listen for the drover.** The A part is the cattle's pace —
   plodding, even, dignified. The B part is the drover's whistle
   carrying over them. Final A is the cattle settling back down.
   That's the picture; let it shape the dynamics inside the
   doubling clusters.

## License

MIT — same as the rest of `sheet-music`. *Drover's Path* is yours to
perform, record, arrange, and adapt. Attribution to Heifer Zephyr /
Tony Koop appreciated but not required.
