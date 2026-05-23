# MANIFEST — Great Highland Pipe starter songbook

Every file written for this v0.2 stress test, with a one-line purpose
each. Paths are relative to the songbook root
(`examples/great-highland-pipe-songbook/`).

## Songbook root

- `README.md` — entry point: how to use the folder, file legend, practice path, pipe-specific notes (no rests, sounding pitch).
- `MANIFEST.md` — this file (file inventory).
- `EVAL.md` — honest assessment of how the v0.1 skill handled GHP and what to fix in v0.2.
- `fingering-charts.svg` — combined chanter chart covering all 9 distinct chanter pitches (G4–A5).
- `songsheet.pdf` — one-page printable summary of the whole songbook (title, range, contents, practice path).

## 00-warmup-scales/

- `00-warmup-scales/range-walk.abc` — full chanter range, ascending then descending, 1/4=70.
- `00-warmup-scales/range-walk.mid` — playable MIDI of the range walk.
- `00-warmup-scales/range-walk.musicxml` — MusicXML of the range walk for DAWs/notation editors.
- `00-warmup-scales/intervals.abc` — 2nds, 3rds, 4ths, 5ths walk up the chanter, 1/4=72.
- `00-warmup-scales/intervals.mid` — playable MIDI.
- `00-warmup-scales/intervals.musicxml` — MusicXML.
- `00-warmup-scales/ornament-drill.abc` — one ornament family per line (doubling on each chanter note, throw on D, birl), 1/4=60.
- `00-warmup-scales/ornament-drill.mid` — playable MIDI (graces stripped — they don't sound here).
- `00-warmup-scales/ornament-drill.musicxml` — MusicXML.

## 01-easy/scotland-the-brave/

- `tune.abc` — canonical pipe-band setting of the trad. Scottish march, AABA, K:Amix, 1/4=90 (PD melody only — Hanley 1951 lyrics excluded).
- `tune.musicxml` — MusicXML for DAWs/Sibelius/MuseScore.
- `tune.mid` — playable MIDI.
- `tune-fingering.svg` — fingering chart for every distinct pitch in the tune.
- `tune.pdf` — one-page printable songsheet.
- `notes.md` — provenance, ornament inventory, range check, practice tips.
- `render-summary.json` — pipeline run log.

## 01-easy/loch-lomond/

- `tune.abc` — slow air, AB form, K:Amix, 1/4=68 (PD; melody contour adapted to chanter).
- `tune.musicxml`, `tune.mid`, `tune-fingering.svg`, `tune.pdf` — derived files.
- `notes.md` — provenance (1841 first publication), arrangement notes, practice tips.
- `render-summary.json` — pipeline run log.

## 01-easy/auld-lang-syne/

- `tune.abc` — through-form, K:Amix, 1/4=80, original F-major melody transposed up a major 3rd to fit the chanter.
- `tune.musicxml`, `tune.mid`, `tune-fingering.svg`, `tune.pdf` — derived files.
- `notes.md` — provenance (Burns 1788 + trad. melody, both PD), ornament inventory, practice tips.
- `render-summary.json` — pipeline run log.

## 02-intermediate/loch-lomond-ornamented/

- `tune.abc` — same melody as 01-easy/loch-lomond, every long note doubled, throws on D, grips between B–c upbeats, grip-into-cadence.
- `tune.musicxml`, `tune.mid`, `tune-fingering.svg`, `tune.pdf` — derived files.
- `notes.md` — what changed vs. easy version, layered-practice tips.
- `render-summary.json` — pipeline run log.

## 02-intermediate/auld-lang-syne-ornamented/

- `tune.abc` — same melody as 01-easy/auld-lang-syne, with birls on repeated low A's, doublings on every quarter, grips on repeated B–c upbeats.
- `tune.musicxml`, `tune.mid`, `tune-fingering.svg`, `tune.pdf` — derived files.
- `notes.md` — what changed vs. easy version, birl-isolated practice.
- `render-summary.json` — pipeline run log.

## 03-original/drovers-path/

- `tune.abc` — Heifer Zephyr original "Drover's Path", AABA slow march, 32 bars, K:Amix, 1/4=76, MIT-licensed.
- `tune.musicxml`, `tune.mid`, `tune-fingering.svg`, `tune.pdf` — derived files.
- `notes.md` — composition brief, form/contour, ornament inventory, practice tips.
- `render-summary.json` — pipeline run log.

## Files written outside this folder (skill-level changes that support the songbook)

- `instruments/registry.yaml` — added `great-highland-pipe` row under the `reeds-and-pipes:` family (range G4–A5, scale mixolydian-A, fingering ghp-chanter-9note, ornaments doubling/throw-on-d/grip/birl/taorluath, GM preset 110, no-rest constraint captured in notes).
- `assets/fingering-icons/ghp-chanter-9note.json` — placeholder fingering scheme (8 holes = 7 finger + 1 thumb, 9 chanter notes; `placeholder: true`).
- `catalog/public-domain/celtic/scotland-the-brave/tune.abc` — canonical PD setting.
- `catalog/public-domain/celtic/scotland-the-brave/notes.md` — provenance, arrangement notes.
- `catalog/public-domain/celtic/loch-lomond/tune.abc` — canonical PD setting.
- `catalog/public-domain/celtic/loch-lomond/notes.md` — provenance, arrangement notes.
- `catalog/public-domain/celtic/auld-lang-syne/tune.abc` — canonical PD setting.
- `catalog/public-domain/celtic/auld-lang-syne/notes.md` — provenance, arrangement notes.
- `catalog/original/drovers-path/tune.abc` — Heifer Zephyr original (canonical, MIT-licensed).
- `catalog/original/drovers-path/notes.md` — composition brief.

## Stages skipped (documented "fail honestly" behavior)

- LilyPond engraving (`tune.ly`, `tune.svg`) — needs the `lilypond` binary on PATH; not available in the build environment used for this stress test.
- Audio rendering (`tune.wav`) — needs `fluidsynth` + a bagpipe-compatible soundfont; not available in the build environment.
