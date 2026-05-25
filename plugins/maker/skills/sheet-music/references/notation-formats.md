# Notation formats — quick reference

ABC is the canonical source. Everything else converts from it. This file
captures just enough of each format to write correct examples and to
debug round-trip failures.

## ABC notation

Plain text, header-then-body. Excellent for round-tripping and for
human editing. The skill's `tune.abc` files always carry these headers:

```
X:1                          % index (always 1 for single-tune files)
T:Twinkle Twinkle Little Star
C:Trad. (W. A. Mozart, "Ah! vous dirai-je, maman", 1781)
S:Public domain (US, pre-1929)
M:4/4                        % meter
L:1/4                        % default note length (a quarter note)
Q:1/4=90                     % tempo: quarter = 90 bpm
K:C                          % key
H:Arranged for Native American flute (A-tuned); transposed to A minor pentatonic.
```

Body uses letter names: `C D E F G A B c d e f g a b`. Lower-case letters
are one octave above upper-case. Octave shifts: `C,` is one octave below
`C`; `c'` is one octave above `c`. Sharps and flats: `^C` (sharp), `_C`
(flat), `=C` (natural). Note lengths are multipliers of `L:`: `C2` is
twice as long, `C/2` is half. Rests are `z`.

Ornament shorthand the skill uses:
- `~C` — generic ornament (interpretation depends on instrument family)
- `{cd}C` — grace notes leading to C
- `(3CDE` — triplet
- `C-D` — slur from C to D (also: tie when same pitch)
- Bagpipe doublings: written explicitly with `{XYZ}` grace cluster

## LilyPond

Engraved output. The skill writes `.ly` files that render via
`lilypond` to PDF and SVG. Skill-generated LilyPond always opens with:

```
\version "2.24.0"
\header {
  title = "Twinkle Twinkle Little Star"
  composer = "Trad. arr. Heifer Zephyr"
  copyright = "MIT (this arrangement); melody PD"
}
\score {
  \new Staff {
    \relative c' {
      \tempo 4 = 90
      \time 4/4
      \key c \major
      c4 c g' g a a g2 |
      f4 f e e d d c2 |
    }
  }
  \layout { }
  \midi { }
}
```

The conversion `abc_to_lilypond.py` handles ABC → LilyPond. We don't
edit the `.ly` directly — if it looks wrong, fix the ABC and rerun.

## MusicXML

Verbose XML, but it's the lingua franca for DAWs (Ableton, Logic, Sibelius,
MuseScore). The skill writes MusicXML 4.0 via `music21`'s `parseFile`
→ `.write('musicxml')`. We never hand-write it.

The Ableton handoff specifically expects a MusicXML file alongside the
MIDI for richer interpretation when the user pastes the prompt template
into the Claude+Ableton connector.

## MIDI

Generated from ABC via either:
- `music21` (preferred, pure-Python) — `converter.parse(abc).write('midi')`
- `abc2midi` (the `abcMIDI` tool by James Allwright) — fast, command-line

The skill writes Format 1 MIDI with one track per voice, plus a tempo
track. Channel 10 is reserved for percussion (per General MIDI). The
program change at the start of each non-percussion track uses the
`soundfont_preset` from `instruments/registry.yaml`.

## ASCII staff (last-resort fallback)

When neither LilyPond nor `music21` is available, the skill emits an
ASCII-staff representation suitable for a chat reply:

```
  Twinkle Twinkle Little Star (in C, 4/4, q=90)

E |---o---o---o-o-|---o-o---o-o-|
B |-----------------|-------------|
C |-o-o------------|-o-o-o-o----|
   1   2   3 4    1 2 3 4

  C C G G | A A G - | F F E E | D D C - |
```

ASCII staff is for *checking* a tune at a glance, not for performance.
Don't deposit ASCII staffs in `learn-to-play/` folders unless the user
explicitly asks for it.
