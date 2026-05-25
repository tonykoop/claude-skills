# sheet-music

A companion to [`instrument-maker-v4`](https://github.com/tonykoop/instrument-maker)
by Tony Koop. Once you've finished a flute, harp, duduk, or guitar from one
of his build packets, this repo gives you the music to play on it: notation,
fingering charts, MIDI, rendered audio, and a printable one-page songsheet
sized to *your specific instrument*.

It's also a skill. Drop the repo into your Cowork or Claude Code skills
folder and Claude will use it to compose, arrange, render, and deposit
starter songbooks into any of Tony's build repos automatically.

## What it does

- Notation in ABC, LilyPond, MusicXML, and ASCII staff
- Fingering charts as SVG, ready to print or embed in a songsheet
- MIDI files for every tune
- Rendered audio (WAV/MP3) using instrument-appropriate soundfonts
- Printable songsheets as one-page PDFs, optionally polished via the
  Adobe Creative Cloud Claude connector
- Backing tracks via the Ableton Claude connector when you want a
  drone, metronome, or full arrangement to practice against
- Pedagogy -- every tune ships with a notes.md containing range
  checks, ornament guidance, and at least one practice tip
- Originals -- composes new "Heifer Zephyr" tunes designed for a
  specific build (range, scale, ornament tradition)

## How it pairs with the build repos

Each build repo (e.g., drone-flutes, fujara, kena, floor-harp,
acoustic-violin) gets a `learn-to-play/` folder deposited at its root:

```
drone-flutes/
├── README.md
├── design-table/
├── drawings/
├── ...
└── learn-to-play/         <- written by this skill
    ├── README.md
    ├── 00-warmup-scales/
    ├── 01-easy/
    ├── 02-intermediate/
    ├── 03-original/
    ├── fingering-charts.svg
    └── songsheet.pdf
```

The folder is self-contained -- anyone who clones the build repo to make
the instrument also gets the music to play on it.

## Repo layout

```
sheet-music/
├── SKILL.md                       # the skill definition Claude consults
├── README.md                      # this file
├── LICENSE                        # MIT
├── instruments/
│   └── registry.yaml              # canonical instrument list
├── catalog/
│   ├── public-domain/             # PD tunes by tradition
│   └── original/                  # Heifer Zephyr originals
├── references/                    # family rules, format guides, MCP handoffs
├── scripts/                       # the working pipeline
├── assets/                        # SVG primitives, PDF/README templates
├── tests/                         # pytest validation
├── evals/                         # skill-creator benchmarks
└── examples/                      # one fully-built reference songbook
```

## Supported instruments (v0.1)

Pulled from `instruments/registry.yaml`. Add a row to support more.

| Instrument | Family | Range | Build repo |
|---|---|---|---|
| Native American flute (6-hole) | flute / ducted | A4-D6 (typ., A-tuned) | flutes |
| PVC flute | flute / ducted | C5-C7 | flutes |
| Drone flute (paired ducts) | flute / ducted | C5-C6 + drone | drone-flutes |
| Andean duct flute (kena, moseno, fujara) | flute / open | varies by length | andean-duct-flutes, kena, moseno, fujara |
| Acoustic violin | strings / bowed | G3-E7 | acoustic-violin |
| Electric violin | strings / bowed | G3-E7 | electric-violin, ceramic-electric-violin |
| Floor harp | strings / plucked | varies by lever range | floor-harp |
| Electric / CNC guitar | strings / fretted | E2-E5 (std tuning) | electric-guitar-bodies, cnc-guitar-bodies |

## Skeleton support (v0.1, full coverage in v0.2)

- Reeds & pipes: chalumeau, clarinet, duduk
- Percussion: conga, djembe, cajon, dundun, ashiko, frame-drum,
  tongue-drum, ceramic-tongue-drum

## Installing as a Cowork / Claude Code skill

Clone the repo into your skills folder, or drop the packaged `.skill`
file into Cowork. Then ask Claude something like:

> "I just built a fujara from the build packet -- give me a starter
> songbook for it."

Claude will read `SKILL.md`, look up `fujara` in `instruments/registry.yaml`,
arrange three PD tunes for the fujara's range and tradition, compose one
original, render the full pipeline, and deposit a `learn-to-play/` folder
into `GitHub/fujara/`.

## Running the pipeline manually

The skill is the recommended entry point, but the scripts run standalone:

```bash
# Render every format from a single ABC file
python scripts/render_pipeline.py \
  --tune catalog/public-domain/nursery/twinkle-twinkle/tune.abc \
  --instrument naf-6hole \
  --out /tmp/twinkle/

# Drop a starter songbook into a build repo
python scripts/deposit_songbook.py \
  --instrument fujara \
  --target ~/Documents/GitHub/fujara/

# Generate range-walk warmup scales
python scripts/generate_scales.py \
  --instrument naf-6hole \
  --out /tmp/scales.abc
```

## Dependencies

The skill is honest about missing tools. Each script checks what's
available and degrades gracefully.

- Required: Python 3.10+
- Recommended: music21 (pip install music21) -- handles ABC parsing,
  MusicXML output, MIDI generation. The pure-stdlib fallback handles
  simple tunes only.
- Optional: lilypond on PATH -- engraved PDF/SVG notation
- Optional: fluidsynth on PATH plus a soundfont (.sf2) -- rendered audio
- Optional: Adobe Creative Cloud Claude connector -- polished
  songsheet PDFs
- Optional: Ableton Claude connector -- backing tracks and arrangements

See `references/audio-rendering.md` for installation tips.

## Contributing

This repo grows alongside Tony's build catalog. To add an instrument or
a tune, follow the recipes in `SKILL.md`:

- "Adding a new instrument" -- registry row, fingering icons, family ref,
  three test cases
- "Adding a new tune to the catalog" -- verify PD status, write canonical
  ABC, render through the pipeline, file under the right tradition

PRs welcome from anyone who builds the instruments and wants to deposit
their own arrangements back into the catalog.

## License

MIT. See `LICENSE`.

## Companion projects

- instrument-maker-v4 -- designs and documents the instrument
- instrument-showcase -- public-facing build-log site that links to
  this skill's `learn-to-play/` deposits
