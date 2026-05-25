# Flute family — notation and arrangement rules

Covers the v0.1 priority instruments: NAF, PVC flute, drone flute, andean
duct flutes, kena, moseno, fujara. The fingering systems differ; the
notation conventions overlap.

## Subfamily map

| Subfamily | Sound source | Examples in registry | Fingering scheme |
|---|---|---|---|
| ducted | block-and-window flue | NAF, PVC, drone-flute | `naf-6hole`, `simple-system-6hole`, `drone-flute-pair` |
| ducted-andean | as above, andean tradition | andean-duct-flute, moseno | `andean-6hole`, `moseno-6hole` |
| transverse | side-blown air-stream | (PVC variants) | `simple-system-6hole` |
| notched | notch instead of duct | kena | `kena-6hole` |
| overtone | mostly-overtone-driven | fujara | `fujara-3hole` |

## Notation conventions

Standard treble staff in concert pitch, regardless of the instrument's
home key. The `K:` line in ABC is set to the *tune's* key, which may
differ from the instrument's `key_default`. The arrangement step is
responsible for transposing the tune into a key the instrument can
actually play.

Breath marks are placed at structural phrase boundaries — typically every
4-8 measures depending on tempo and tune length. In ABC, use `!breath!`
or the comma marker `'`. In LilyPond, use `\breathe`.

Range checks:
- Hard low: `range_low` from registry. Below this is unplayable.
- Soft low: `range_low + minor 3rd`. Below this is hard for beginners.
- Sweet spot: middle 60% of the range. Beginners stay here.
- Soft high: `range_high - minor 3rd`. Above this requires confident
  overblowing (ducted flutes) or strong embouchure (transverse, kena).
- Hard high: `range_high`.

## Ornament catalog (by tradition)

### Native American flute (NAF)

The NAF tradition is intentionally sparse. Beginner arrangements should
include *zero or one* ornament per phrase. Available ornaments:

- **Simple grace** — `{c}d` in ABC. A single grace note one scale step
  above the principal. Use sparingly to mark phrase ends.
- **Finger vibrato** — repeated rapid open/close on a finger below the
  sounded note. Notate as `~d` for "instrument-appropriate ornament";
  the songsheet's accompanying note explains it as finger vibrato.
- **Throat glide** — bend pitch downward slightly with throat tension.
  Notate as `\\glis(d e)` or in ABC as `(de)` slurred plus a margin
  note in the tune's `notes.md`.

The five-tone minor pentatonic (W-W-mW-W-W where mW means minor third)
is the natural scale of an NAF. Arranging non-pentatonic tunes for an
NAF means *picking pitches the flute can play* and either dropping
non-fitting passing tones or substituting them.

### PVC flute / simple-system transverse

Two-octave chromatic-ish range (lower octave fully chromatic with
half-holing, upper octave by overblowing). Beginner arrangements stick
to the lower octave's diatonic notes plus the easiest cross-fingerings.

Articulation: tonguing is the default attack ("tu" or "du"). Slurs are
notated with curved lines as in any classical staff music.

### Drone flute (paired ducts)

The drone duct plays the tonic continuously. The melody duct has a
limited range (typically the tonic up an octave). Arrangements:

- Pick a tune where the melody fits within the melody duct's range.
- The drone is implicit — don't write it on the staff.
- Conjunct motion (small intervals) only; the melody hand can't jump
  far while the other hand sustains the drone.
- Avoid silent rests inside phrases (the drone keeps going either way,
  so rests in the melody read as held drone).

### Andean tradition (kena, moseno, andean duct)

Cross-fingerings give a chromatic palette but specific cross-fingerings
have a *flutter* quality. The tradition uses this flutter as expression.

- Pentatonic core scale; chromatic passing tones permitted.
- Glides between scale steps (especially in slower huayno rhythms) are
  notated as slurs with a margin note "glide."
- Strong articulation between phrases; weak articulation within.
- Quena flutter on sustained tones — finger trill on the lowest open
  hole.

### Fujara (overtone flute)

Three fingerholes and the lip; almost everything is overtones of the
fundamental.

- Pitch is mostly a function of breath pressure, not fingering.
- Arrangements use the natural overtone series of the build:
  fundamental, octave, octave+5th, 2-octave, 2-octave+major-3rd, etc.
- The Slovak shepherd "rozfuk" — a short sharp blast that jumps to a
  high overtone — is idiomatic and fun for beginners.
- Tunes that fit: pentatonic shepherd melodies, slow ballads in the
  natural overtone scale. *Don't* pick chromatic tunes.

## Arrangement workflow (flute-specific)

When a tune comes in (PD or user-supplied), and the target instrument
is in the flute family:

1. **Read the registry row.** Get range, scale, fingering scheme,
   ornament list.
2. **Check key compatibility.** If the tune's key isn't a key the
   instrument plays cleanly, transpose the tune into a key it does.
   For a minor-pentatonic NAF in A, the tune ends up in A minor or D
   minor (the relative pentatonic).
3. **Range-clip or transpose.** If the tune still has notes outside
   range after key fit, either transpose by an octave or rewrite the
   offending phrase to stay in range. Note the change in `notes.md`.
4. **Strip non-scale tones.** For pentatonic instruments, accidental
   passing tones get removed or replaced with adjacent scale tones.
5. **Add ornaments sparingly.** One per major phrase boundary, at
   most. Beginner mode = zero ornaments.
6. **Add breath marks.** Every 4-8 measures, at phrase boundaries.
7. **Generate the fingering chart.** One row per distinct pitch in the
   tune, showing which holes are open/closed.
8. **Write a `notes.md`** with: original key, instrument-target key,
   ornament rationale, range checks, one practice tip ("hold the long
   note in measure 7 — that's where you breathe").

## Output format expectations

- ABC always at the *target instrument's playable pitch* (concert pitch
  for non-transposing flutes; written-pitch for the rare transposing
  flute).
- LilyPond: include the engraved staff plus a small "fingering chart"
  block at the end (use LilyPond's `fingering` syntax).
- MusicXML: clean treble staff with breath marks as `{words}` elements.
- MIDI: one track, soundfont preset from registry, tempo from `Q:`.
- WAV: rendered through fluidsynth if available; the soundfont should
  contain a flute or pan-flute preset. The pan-flute preset (GM 76)
  is closer to NAF/andean tone than the orchestral flute (GM 74).
- Fingering SVG: one diagram per distinct pitch, ordered low → high
  by pitch.
