# Jianpu (numbered notation) — quick reference

Jianpu (简谱, "simplified notation") is the numbered-notation system used
throughout China, Taiwan, and much of East and Southeast Asia. For the
East-Asian instruments in the registry (guzheng, pipa, erhu, konghou,
sheng, and future additions), Jianpu is the culturally-native tab —
shipping a `learn-to-play/` songbook in staff notation only is a poor
fit for those players.

Jianpu is a **render target**, not a separate authoring path. The
canonical `tune.abc` stays the single source of truth; `abc_to_jianpu.py`
derives numbered-notation text from it, the same way `abc_to_lilypond.py`
and `abc_to_musicxml.py` derive their formats.

## Running it

```
python scripts/abc_to_jianpu.py --tune tune.abc --out tune-jianpu.txt
```

It's also wired into `render_pipeline.py` as the `jianpu` stage — no
extra flags needed; it runs for every instrument since it has no
external dependency to be missing.

## The encoding, in brief

- **Pitch** — numbers `1`–`7` for the movable-do scale degrees (Do Re Mi
  Fa Sol La Ti); `0` for a rest.
- **Key** — *movable-do*: the header shows `1=<note>`, meaning that note
  is scale degree 1 for this piece. For a **major** ABC key (`K:C`,
  `K:G`, ...), the tonic itself is `1=`. For a **minor** ABC key
  (`K:Am`, `K:Em`, ...), Jianpu convention notates under the *relative
  major*'s `1=` header, with the minor tonic written as scale degree
  `6` — e.g. `K:Am` renders as `1=C`, and the A itself appears as `6`,
  not `1`. This matches how real Jianpu scores handle minor-key tunes.
- **Chromatic passing tones** — a semitone outside the 7-note scale is
  written as `#` (sharp) of the scale degree one semitone below it
  (e.g. `#4` between Fa and Sol). This is the common simplified-Jianpu
  convention; it is not a full enharmonic-spelling engine.
- **Octave** — a dot **above** the digit raises it an octave; a dot
  **below** lowers it. Plain text can't stack a real dot on a digit, so
  the generator prints a separate row of `.` characters above (and/or
  below) the digit row, column-aligned to it.
- **Duration** — a bare digit is one beat (the tune's `L:` default
  length). A trailing `-` (dash) after the digit holds it one *extra*
  beat (so a half note relative to a quarter-note beat is `1-`). A row
  of `_` characters printed **beneath** the digit row subdivides the
  beat: one underline row = eighth notes, two = sixteenth notes.
- **Barlines** — carried straight through from the ABC `|` markers.

## Example

Input (`tests/sample_inputs/tiny-pentatonic.abc`, `K:Am`, notes
`A B c d e | e d c B A`):

```
    . . .   . . .
6 7 1 2 3 | 3 2 1 7 6
```

The header line reads `1=C` (Am's relative major) with a note that the
tonic (A) is shown as `6`. The dots above `1 2 3` mark the lowercase
ABC letters (`c d e`) as one octave above the written register — pure
mechanical translation of ABC's own octave-shift convention (`c` vs
`C`, `'` and `,`), which the generator reuses directly for the dot rows.

## Known limitations (v1)

- Single voice; no chord/harmony line underneath the melody number row.
- Ties/slurs/grace-notes/triplets are stripped like the other
  from-ABC generators (`abc_to_midi.py`'s stdlib fallback has the same
  limitation) — pitch and plain duration only.
- Modal keys other than plain major/minor (`K:Amix`, `K:Ddor`, ...) fall
  back to being treated as major-scale-relative. No modal Jianpu
  spelling rules are implemented.
- No instrument-specific ornament marks (bends, glissandi, finger
  indicators) yet — those are add-ons for a future story once a pilot
  instrument (guzheng) validates the base numbered-notation output.

## Deposit

When depositing a `learn-to-play/` folder for a Jianpu-reading
instrument, include `tune-jianpu.txt` alongside the existing
`tune.abc` / `tune.ly` / etc. in each tune folder (see
`references/starter-songbook.md`), and mention in that tune's
`notes.md` that Jianpu was generated, not hand-transcribed.
