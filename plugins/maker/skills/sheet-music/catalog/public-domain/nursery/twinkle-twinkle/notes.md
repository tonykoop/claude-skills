# Twinkle Twinkle Little Star

A nursery-rhyme classic, the melody most westerners learn before they
can read music. The lyrics are by Jane Taylor (1806); the melody is
older — it's the same tune as the French nursery song "Ah! vous
dirai-je, maman," which Mozart used as the theme for his 1781 keyboard
variations K. 265.

## Provenance

- **Melody:** trad., earliest printed source the French children's
  song collection *Les Amusemens d'une heure et demy* (~1761).
  Pre-1929 in the US — public domain.
- **Lyrics:** Jane Taylor, 1806 — also pre-1929, also public domain.
- **This canonical ABC arrangement:** Tony Koop / Heifer Zephyr, 2026.
  MIT-licensed within the `sheet-music` repo.

The arrangement itself is intentionally minimal: only quarter notes
and half notes, conjunct motion, no accidentals. It's a workhorse for
testing the rendering pipeline and for arranging across instruments.

## Why it works for beginner songbooks

- Range is narrow (C5 to A5 in the canonical key) — fits almost any
  flute, recorder, ocarina, kena, fujara overtone-series, beginner
  violin, beginner harp, or first-position guitar.
- Rhythm is purely on-the-beat — no syncopation, no rests within
  phrases.
- The phrase structure (4+4+4 bars, AABA-ish) is easy to memorize.

## Per-instrument transposition guide

Most of Tony's ducted flutes and pentatonic instruments need this
tune transposed to fit their scales. The arrangement step
(`deposit_songbook.py`) handles this automatically based on the target
instrument's `key_default` and `scale` from `instruments/registry.yaml`.

Common targets:

| Instrument | Target key | Notes |
|---|---|---|
| NAF (A-tuned, A minor pentatonic) | A minor | Drop the F notes; substitute with E or G to stay pentatonic. |
| PVC flute (C major) | C major | Use the canonical key as-is. |
| Drone flute | C major (matches drone) | Stay within the melody duct's one-octave range. |
| Kena (G minor pentatonic) | G minor | Fits naturally; substitute non-pentatonic passing tones. |
| Fujara | G | Awkward — fujara wants overtone-series melodies. Maybe pick a different tune for fujara. |
| Acoustic violin | D major (open D string anchor) | Sounds bright. |
| Floor harp (C major) | C major | No lever changes needed — easy. |
| Electric guitar | C major | First-position; treat as a single-line melody for beginners. |

## Practice tip

The biggest beginner stumble is the half note at the end of every two
bars. Players rush it. Count out loud — "two beats, *two beats*" — on
those long notes. Once that's locked, the rest of the tune almost
plays itself.
