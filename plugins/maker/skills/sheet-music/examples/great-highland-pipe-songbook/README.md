# learn-to-play / Great Highland Pipe (chanter)

Starter songbook for the **Great Highland Pipe (chanter)**, the
9-note A-mixolydian pipe-band instrument. There is no Tony-Koop GHP
build repo (the GHP isn't a Tony-built instrument) — this songbook
lives under `examples/` in the [`sheet-music`](https://github.com/tonykoop/sheet-music)
repo as a v0.2 stress-test reference rather than a build deposit.

> **Status: v0.1 skeleton-plus.**  The bagpipe family was marked
> *skeleton* in v0.1 of `sheet-music`. This songbook was produced as
> the stress test that motivates v0.2 full-bagpipe support — see
> `EVAL.md` for what the v0.1 skill handled cleanly and what had to
> be hand-authored.

## How to use this folder

Every tune has multiple files. The canonical source for each is
`tune.abc` — everything else is generated from it.

| File | Purpose |
|---|---|
| `tune.abc` | Canonical notation in ABC format (plain text) |
| `tune.musicxml` | Notation for Ableton, Logic, MuseScore, Sibelius, etc. |
| `tune.mid` | Playable MIDI (open in any media player) |
| `tune-fingering.svg` | Fingering chart for every distinct pitch |
| `tune.pdf` | One-page printable songsheet |
| `notes.md` | Source / provenance, range checks, practice tips |
| `tune.ly` / `tune.svg` / `tune.wav` | Skipped — needs LilyPond and fluidsynth |

## Folder map

- `00-warmup-scales/` — range walk, interval drill, ornament drill.
- `01-easy/` — three beginner public-domain tunes.
- `02-intermediate/` — same melodies as 01-easy, **denser ornaments**.
- `03-original/` — one Heifer Zephyr original (`drovers-path`).
- `fingering-charts.svg` — combined chart covering all 9 chanter notes.
- `songsheet.pdf` — one-page printable summary of the whole songbook.
- `MANIFEST.md` — bullet list of every file, with a one-line purpose.
- `EVAL.md` — honest assessment of how the v0.1 skill handled GHP.

## Tunes in this songbook

| Tier | Slug | What it is |
|---|---|---|
| 01-easy | `scotland-the-brave` | Trad. Scottish pipe-band march (PD melody) |
| 01-easy | `loch-lomond` | Slow air, lyrics first published 1841 (PD) |
| 01-easy | `auld-lang-syne` | Burns 1788 lyrics, trad. melody (PD) |
| 02-intermediate | `loch-lomond-ornamented` | Same melody as easy, denser ornaments |
| 02-intermediate | `auld-lang-syne-ornamented` | Same melody as easy, with birls and grips |
| 03-original | `drovers-path` | AABA slow march, MIT-licensed |

## Suggested practice path

1. Run the warmup scales in `00-warmup-scales/` for 5 minutes.
2. Pick one tune from `01-easy/`. Open its `tune.mid` in any media
   player to hear the pitch contour (the MIDI plays principal notes
   only — grace notes don't sound).
3. Read the `notes.md` for that tune — range check, practice tip.
4. Play the first phrase slowly with `tune-fingering.svg` open.
5. When the easy set feels comfortable, move to `02-intermediate/`
   for the same melodies with denser ornaments.
6. Save `03-original/drovers-path/` for when you're ready to learn
   something new — it's MIT-licensed and yours to perform.

## Pipe-specific notes

- **9-note chanter:** low G, low A, B, C#, D, E, F#, high G, high A.
  The chanter cannot play any note outside this range.
- **No rests, ever.** Every tune holds its phrase ends; the bag
  stores air so the chanter never stops sounding. Phrasing is
  articulated through grace clusters (doublings, throws, grips,
  birls) — *the embellishments are the rhythm*.
- **Sounding pitch.** Pipe "low A" sounds closer to B♭4 (~466 Hz)
  on most modern pipes — pipes are not concert-pitched. Standard
  pipe notation writes it as A4 for readability and that's what
  these scores use. MIDI playback through GM preset 110 sounds
  written-pitch; don't try to play along with a piano at concert
  pitch unless the pianist transposes.

## Re-generating

If you change a `tune.abc` (transposing, ornamenting, fixing a typo),
regenerate the derived files:

```bash
# from the sheet-music repo root:
python scripts/render_pipeline.py \
  --tune <tune.abc path> \
  --instrument great-highland-pipe \
  --out <output dir>
```

`tune.ly`, `tune.svg`, and `tune.wav` are skipped unless LilyPond
and fluidsynth are installed — see `references/audio-rendering.md`.

## License

The original tune in `03-original/` (`drovers-path`) is MIT-licensed
along with the rest of `sheet-music`. The public-domain tunes are PD
by virtue of their original publication date; per-tune provenance is
documented in each `notes.md`.

## Where to ask for more

- More tunes for the GHP: open an issue in
  [`sheet-music`](https://github.com/tonykoop/sheet-music) with the
  tradition or mood you want.
- Bagpipe support is on the v0.2 roadmap — see `EVAL.md` here for
  the diffs that would land it.
