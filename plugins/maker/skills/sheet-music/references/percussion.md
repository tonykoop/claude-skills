# Percussion — notation and arrangement rules

**v0.1 status: skeleton.** Pitched percussion (tongue drums, hang) is
treated like a flute (melodic notation). Unpitched percussion uses
stroke notation, documented here for the skill to reference; the
rendering scripts handle it loosely until v0.2.

## Two notation worlds

### Pitched percussion: tongue drum, hang

These instruments have a fixed scale layout. Treat them as melodic:

- Treble staff, concert pitch.
- Range and scale come from the registry row (typically pentatonic).
- Arrangements are constrained to the layout — if a note isn't on the
  drum, it can't be played. `validate_arrangement.py` flags out-of-
  layout pitches.
- Mallet rolls notated as tremolo bars on the note (`/` slashes
  through the stem).
- Soundfont preset: GM 13 (Marimba) or GM 116 (Steel Drums) depending
  on the instrument's tonal character. Steel drum preset is mellower
  and matches Tony's slip-cast ceramic builds more closely than
  marimba.

### Unpitched percussion: conga, djembe, cajón, dundun, ashiko, frame drum

Stroke notation lives on a single-line staff or on a percussion clef.
Each stroke type gets a letter or symbol.

| Stroke | Conga | Djembe | Cajón | Frame drum |
|---|---|---|---|---|
| Bass | B (heel-of-hand at center) | B (open hand at center) | B (low-front strike) | B (full-finger thump) |
| Open tone | O (fingertips at edge) | T (fingers at edge) | T (high-front strike) | T (fingertip ring) |
| Slap | S (sharp pop at edge) | S (cupped slap) | — | S (sharp edge) |
| Mute | M (palm rest, soft strike) | — | — | M (damped) |
| Heel | H | — | — | — |
| Toe | h | — | — | — |
| Snare | — | — | s (snare-side) | — |

Patterns loop. Notate one bar (or 4 bars for clave) and mark `||: :||`
repeat. Tempo from `Q:` as usual.

## ABC for unpitched percussion

ABC's `K:perc` is rarely useful. Instead, the skill writes percussion
patterns as plain text inside a code block with a header:

```
Pattern: Tumbao (conga, 4/4, q=100)
Beat:    1 . . . | 2 . . . | 3 . . . | 4 . . . |
Stroke:  H . T . | H . T . | H . T O | S . O . |
```

The accompanying MIDI file uses GM percussion channel 10. Conga maps:
GM 60 (high conga), 62 (mute conga), 64 (low conga). Djembe doesn't
have a dedicated GM mapping; the skill uses GM 60 (high conga) as a
substitute and notes the substitution in `notes.md`.

## Arrangement workflow (percussion)

For pitched percussion, follow the flute-family workflow but constrain
to the drum's exact layout.

For unpitched percussion:

1. Pick a pattern appropriate to the player's level. Beginner mode:
   single 1-bar pattern that loops. Intermediate: 2-3 bar patterns
   with a fill every 4 bars.
2. Confirm the strokes used are in the instrument's vocabulary (see
   table above).
3. Write the pattern as text + MIDI.
4. The "fingering chart" is replaced by a "stroke key" — a small
   diagram showing where on the drum each stroke type lands.
5. `notes.md` includes the pattern's tempo, the cultural origin, and a
   slow-practice tempo (typically 60-70% of target).

## Quality gates specific to this family

- Pitched percussion arrangements with out-of-layout pitches: flag.
- Unpitched percussion patterns missing a tempo: flag.
- Patterns longer than 4 bars in a beginner songbook: warn (consider
  splitting into multiple patterns).
- Missing stroke-key diagram in `learn-to-play/`: flag.
