# Strings family — notation and arrangement rules

Covers the v0.1 priority: acoustic violin, electric violin, ceramic
electric violin, floor harp, electric guitar, CNC guitar.

## Subfamily map

| Subfamily | Examples | Notation |
|---|---|---|
| bowed | acoustic violin, electric violin, ceramic electric violin | staff + bowing marks + position numbers |
| plucked / lever-tuned | floor harp | staff + lever change marks + finger numbers |
| fretted | electric guitar, CNC guitar | staff + tablature + chord diagrams |

## Bowed strings (violin family)

Standard treble staff in concert pitch. First-position arrangements only
for v0.1 beginner songbooks (notes in the easy span on each string).

Conventions:

- Open-string notation: `0` above the note (sounds the open string).
- Position number (`1`, `2`, `3`...) above the staff at position
  changes. Beginner arrangements stay in 1st position.
- Bowing: `↓` (down-bow) and `↑` (up-bow) above the note. Default to
  down-bow on strong beats, up-bow on weak beats. Mark only when the
  pattern breaks the default.
- Slurs: notes joined under one bow, indicated by curved line above
  the staff (or `( )` in ABC).
- Vibrato: implicit on long sustained notes; mark explicitly only when
  it's musically required (`vib.` text marking).
- Double-stops: two stacked notes; check that both are playable in the
  same position. Avoid double-stops in beginner arrangements.

ABC for violin uses straight pitch letters; bowing isn't first-class in
ABC, so the LilyPond conversion adds bowings based on `notes.md`
guidance. For beginner arrangements, the rule is "down on every
downbeat" and don't worry about it.

## Floor harp (plucked, lever-tuned)

Grand staff (treble + bass). String layout from low (left) to high
(right). Lever changes are the harp-specific complication.

Conventions:

- Lever changes: `+` above the note (raise that pitch one half-step
  via the lever) or `−` (lower it back). Place at the moment of the
  change.
- Finger numbers: `1` (thumb) through `4` (ring finger); `5` (pinky)
  is *not* used in standard harp technique. Place above the note.
- Rolled chords: wavy line `〰` to the left of a stacked chord. In
  ABC, mark with `[` and add `arpegg.` text.
- Glissandi: straight line between start and end pitches, with
  `gliss.` marking.
- Pedal-position changes (for pedal harps; floor harp has levers, not
  pedals): N/A for Tony's floor harp.

Range varies by string count of the specific build. Read the design
table for the exact range and the tuning of each string.

Beginner arrangements:
- Stay in C major (no lever changes needed).
- Two-handed accompaniment patterns (RH plays melody, LH plays root +
  fifth on strong beats).
- One ornament per major phrase boundary at most.

## Fretted strings (guitar family)

Standard guitar notation is one octave higher than sounding (treble-8
clef in formal contexts; ordinary treble clef in lead-sheet style with
the convention understood).

The skill produces both staff and tablature. ABC's TAB extensions are
nonstandard — the skill converts ABC → MusicXML and lets the renderer
emit TAB, or generates TAB directly via `scripts/abc_to_tab.py` (v0.2).

Conventions:

- Standard tuning EADGBE assumed unless specified.
- TAB: six lines representing six strings, lowest pitch on the bottom.
  Numbers indicate fret positions.
- Chord diagrams: 6×5 grid for the first 5 frets, with dots showing
  finger placement, `o` for open strings, `x` for muted.
- Hammer-ons: `h` between two TAB numbers (`5h7`).
- Pull-offs: `p` between two TAB numbers (`7p5`).
- Slides: `/` (slide up) or `\` (slide down) between numbers (`5/7`).
- Bends: `b` after the bent note with the target pitch in parens
  (`7b9`).
- Strum patterns: small arrows or `D` (down) / `U` (up) above the
  staff for beginner songbooks.

Beginner arrangements:
- Use only first-position open chords (G, C, D, Em, Am, E, A, D7).
- Single-strum-per-beat or down-down-up-up-down-up patterns.
- Melodies stay in first position (frets 0-3) until the player is
  ready for moveable shapes.

## Arrangement workflow (strings-specific)

1. **Read registry row.** Get range, transposition (guitar is -P8
   written), fingering scheme.
2. **Check key for open-string suitability.** Bowed: keys with open-
   string roots (G, D, A, E for violin) sound bright and are easier.
   Guitar: keys with open chords (C, G, D, A, E, Em, Am) are easier
   for beginners. Harp: C major (no lever changes) is easiest.
3. **Transpose** if needed.
4. **Add idiom-specific markings.** Bowing for violin, fingerings for
   harp, TAB and chord diagrams for guitar.
5. **Generate fingering chart / chord chart.** For guitar, this is the
   chord-diagram strip at the top of the songsheet.
6. **Write `notes.md`** with: tuning, position(s) used, any unusual
   technique markings, and a practice tip per phrase.

## Output format expectations

- ABC: at sounding pitch for violin/harp; at written pitch (one octave
  up) for guitar. Mark `K:` accordingly.
- LilyPond: full staff for violin/harp; staff + tab for guitar.
- MusicXML: includes the bowing/finger/TAB elements properly.
- MIDI: violin uses GM preset 41, harp 47, guitar 25 or 28 depending
  on body type.
- WAV: rendered with the soundfont preset.
- Fingering / chord SVG: violin gets a fingerboard diagram per phrase,
  harp gets a string-layout diagram with finger numbers, guitar gets
  chord diagrams + a TAB strip.
