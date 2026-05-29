# Audio rendering pipeline

Two-step pipeline: ABC → MIDI → WAV (or MP3). Each step has a
preferred path and a fallback. The skill checks what's installed and
takes the best available route. If nothing renders audio, the
pipeline produces MIDI only and labels the WAV as "skipped."

## Step 1 — ABC → MIDI

**Preferred: `music21`** (`pip install music21`).

```python
from music21 import converter
score = converter.parse('tune.abc')
score.write('midi', fp='tune.mid')
```

`music21` handles ABC's full feature set, including ornaments, ties,
voicing. It's the option the skill picks first.

**Fallback: `abc2midi`** (the `abcMIDI` toolkit by James Allwright).

```bash
abc2midi tune.abc -o tune.mid
```

Faster than `music21`, but more permissive — silently produces output
even for malformed ABC. Use it when `music21` isn't available.

**Last resort: pure-Python MIDI writer.**

`scripts/abc_to_midi.py` includes a minimal stdlib-only writer that
handles single-voice tunes with notes, rests, and a constant tempo.
No ornaments, no slurs. Good enough for a smoke test.

## Step 2 — MIDI → WAV/MP3

**Preferred: `fluidsynth` + a soundfont (`.sf2`).**

```bash
fluidsynth -ni -F tune.wav -r 44100 \
  /path/to/soundfont.sf2 tune.mid
```

The flag `-ni` disables interactive mode; `-F` writes a WAV file.

Recommended soundfonts (free, redistributable):

- **FluidR3_GM.sf2** — the canonical free GM soundfont, 140 MB. Good
  flute and pan-flute presets. ([source](https://member.keymusician.com/Member/FluidR3_GM/index.aspx))
- **GeneralUser GS** — slightly smaller (30 MB), cleaner balance.
  ([source](https://schristiancollins.com/generaluser.php))
- **Sonatina Symphonic Orchestra** — bigger but realistic strings;
  use for violin/harp arrangements.

Soundfonts go in `assets/soundfonts/` (gitignored — too big and often
license-encumbered to commit). The directory ships with a README
pointing to download sources.

**Fallback: `timidity`** (older, slower, simpler MIDI synth).

```bash
timidity tune.mid -Ow -o tune.wav
```

**No-audio fallback:** Skip the WAV step. The pipeline produces MIDI
and labels the WAV "skipped: install fluidsynth or timidity to render
audio." Beginners can play the MIDI in any media player or DAW.

## MP3 conversion

After WAV is generated, an optional MP3 step uses `ffmpeg` if
available:

```bash
ffmpeg -i tune.wav -codec:a libmp3lame -qscale:a 2 tune.mp3
```

The skill writes both formats by default if `ffmpeg` is on PATH;
otherwise WAV-only.

## Soundfont preset selection

Each registry row has a `soundfont_preset` field — the General MIDI
program number (1-128). The pipeline issues a Program Change event at
the start of the MIDI track to that preset.

Common defaults:

| Instrument family | GM preset | Why |
|---|---|---|
| NAF, andean duct, drone flute | 76 (Pan Flute) | Closer than orchestral flute |
| PVC flute (transverse) | 74 (Flute) | Standard orchestral flute timbre |
| Kena | 75 (Recorder) | Slightly thinner than flute, closer to kena |
| Violin (acoustic / electric) | 41 (Violin) | Standard |
| Floor harp | 47 (Orchestral Harp) | Standard |
| Electric guitar (clean) | 28 (Electric Guitar, clean) | Default; user can override |
| Acoustic / CNC guitar | 25 (Acoustic Guitar, steel) | Adjust if nylon-strung |
| Clarinet, chalumeau | 72 (Clarinet) | Standard |
| Duduk | 110 (Bagpipe) | Imperfect; closer than woodwind presets |
| Tongue drum (wood) | 13 (Marimba) | Bright wooden tone |
| Ceramic tongue drum, hang | 116 (Steel Drums) | Mellower, sustained |
| Unpitched percussion | n/a | uses GM channel 10 |

Override the default by passing `--preset {num}` to `render_audio.py`.

## Cowork / sandbox notes

In Cowork's Linux sandbox:

```bash
apt-get install -y fluidsynth ffmpeg lilypond
pip install --break-system-packages music21
```

Soundfonts need to be downloaded once; cache them under
`/sessions/.../mnt/...` if the user has a persistent workspace, or
fetch fresh per session and accept the cost.

## When to escalate to Ableton

The skill's local audio renders are good enough for *practice* —
correct pitches at the correct tempo, with a recognizable timbre. They
are *not* good enough for a polished demo or for a backing track the
user wants to play along with. For polished output:

- Hand off to the Claude Ableton connector (see
  `references/ableton-handoff.md`).
- The Ableton handoff produces a `.als` project with the melody on a
  software-instrument track, optionally with a drone and metronome.
- The user can then add backing instruments, mix, and export from
  Ableton.

The local pipeline writes the MIDI and MusicXML the Ableton handoff
expects; the user just clicks "open in Ableton" or pastes the prompt
template into the connector.
