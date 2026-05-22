# Starter songbook layout — `learn-to-play/`

The deliverable shape for Mode A. When the user says "give me music for
the [instrument] I built," the skill writes a `learn-to-play/` folder
into the matching build repo.

## Folder layout

```
learn-to-play/
├── README.md                       # entry point — what this folder is, how to use it
├── 00-warmup-scales/
│   ├── range-walk.abc              # full range, slow, ascending then descending
│   ├── range-walk.mid
│   ├── range-walk.wav              # if soundfont present
│   ├── intervals.abc               # 2nds, 3rds, 4ths, 5ths up the scale
│   ├── intervals.mid
│   └── ornament-drill.abc          # family-specific ornament practice
│
├── 01-easy/
│   ├── tune-1/                     # 3 PD beginner tunes (typical: nursery + folk + hymn)
│   │   ├── tune.abc                # canonical
│   │   ├── tune.ly                 # engraved (LilyPond)
│   │   ├── tune.musicxml
│   │   ├── tune.mid
│   │   ├── tune.wav                # if rendered
│   │   ├── tune.svg                # engraved notation as SVG
│   │   ├── tune-fingering.svg      # fingering chart
│   │   └── notes.md                # provenance, range checks, practice tip
│   ├── tune-2/
│   └── tune-3/
│
├── 02-intermediate/
│   ├── tune-1/                     # 2 PD tunes with simple ornamentation
│   └── tune-2/
│
├── 03-original/
│   └── heifer-zephyr-original/     # 1 original commission for THIS instrument
│       ├── tune.abc
│       ├── ...
│       └── notes.md                # composition notes, why this tune for this build
│
├── fingering-charts.svg            # combined chart covering the instrument's full range
├── songsheet.pdf                   # one-page printable summary (notation + fingering + tips)
└── stroke-key.svg                  # percussion only — replaces fingering chart
```

## README.md template

Each `learn-to-play/` folder ships with a README that:

- Identifies the instrument (matches the registry's `display_name`).
- Lists the tunes by difficulty, with a one-sentence what-it-is each.
- Gives a "how to read this folder" pointer (canonical = ABC; MIDI to
  hear; SVG/PDF to print; `notes.md` for practice tips).
- Links back to:
  - the build repo's main README (so the player can revisit how the
    instrument was made)
  - the `sheet-music` repo (so they know where to look for more)
  - the `instrument-showcase` build-log site if one exists for this
    instrument
- Acknowledges PD provenance and the Heifer Zephyr-original license
  (MIT).

The template lives at `assets/templates/learn-to-play-README.md` and
gets populated with instrument-specific values when
`deposit_songbook.py` runs.

## File-naming conventions

- Lowercase, hyphenated, no spaces.
- `range-walk` not `RangeWalk` not `range_walk`.
- Tune slugs match the catalog: `twinkle-twinkle`,
  `simple-gifts`, `river-reed-waltz`.
- Original tunes use the brand's two-or-three-word naming — short,
  evocative, no cleverness.

## Difficulty guidance per family

The `01-easy` and `02-intermediate` divisions are calibrated by family:

| Family | 01-easy means... | 02-intermediate means... |
|---|---|---|
| flute | Conjunct motion, single octave, no ornaments | Wider intervals, range stretches near soft-low/high, 1 ornament per phrase |
| strings (bowed) | First position only, all open-string-friendly keys, no double-stops | Position changes within phrases, occasional double-stops |
| strings (harp) | C major (no lever changes), single-line melody | One lever change, simple two-handed accompaniment |
| strings (fretted) | Three open chords or fewer, simple strum, melody in first position | Up to five open chords + barre, fingerstyle pattern, melody in 1st-2nd position |
| reeds-and-pipes | Lower octave only, no register-key crossings (clarinet) | Full range, register crossings allowed |
| percussion (pitched) | Single bar pattern, all in scale | 2-bar pattern, layout-aware extensions |
| percussion (unpitched) | 1-bar loop, two stroke types | 2-4 bar loop, three stroke types + occasional fill |

`scripts/validate_arrangement.py` warns when a tune classified as
`01-easy` doesn't match the criteria.

## Repertoire selection rules

For each instrument's `01-easy` set, the skill picks three PD tunes
that:

1. Fit the instrument's range without transposing more than ±2 octaves
   from concert.
2. Cover three different traditions where possible (e.g., one
   nursery, one folk, one hymn) — keeps the pedagogical menu varied.
3. Don't overlap with the `02-intermediate` set.
4. Have a clear cultural origin documented in `notes.md`.

For `02-intermediate`, two tunes that:

1. Stretch the range a little beyond `01-easy`.
2. Introduce one family-appropriate ornament each.
3. Run longer (8-16 bars vs. 4-8 for easy).

The `03-original` slot is one Heifer Zephyr commission written
specifically for this build's range and tradition. Tony's instruments
each deserve at least one original. Suggested mood pairings:

| Instrument | Suggested mood for original |
|---|---|
| NAF | Contemplative, slow, single-octave pentatonic |
| Drone flute | Mantric, conjunct, long phrases over the drone |
| Fujara | Slow, overtone-leaping, shepherd-song character |
| Kena | Brisk, glissando-rich, small-form (huayno-adjacent) |
| Acoustic violin | Lyrical, first-position, small-form |
| Floor harp | Reverent, C-major, two-handed |
| Electric guitar | Riff-based, single-note line plus chord stabs |
| Duduk | Slow, glide-rich, drone-anchored |

## Quality gates for `learn-to-play/`

`scripts/validate_arrangement.py --strict --target learn-to-play/`
checks that:

- Every required folder is present (`00-warmup-scales/`, `01-easy/`,
  `02-intermediate/`, `03-original/`).
- Each tune subfolder has at least: `tune.abc`, `tune.mid`, `notes.md`.
- The combined fingering chart covers every distinct pitch in every
  tune.
- The songsheet PDF renders without errors.
- The README links resolve (build repo, sheet-music repo).
- All tunes pass the per-family quality gates.

## Updating the build repo's main README

`deposit_songbook.py` also appends a section to the build repo's
existing `README.md`:

```markdown
## Learn to play

A starter songbook for this instrument lives in
[`learn-to-play/`](learn-to-play/). It includes warmup scales, three
beginner tunes, two intermediate tunes, one original, and a printable
one-page songsheet. Generated by
[sheet-music](https://github.com/tonykoop/sheet-music).
```

If a `## Learn to play` section already exists, the script updates it
instead of duplicating.
