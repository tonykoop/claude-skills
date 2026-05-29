# Original tunes

Heifer Zephyr originals. Each tune is composed for a specific Tony
Koop instrument (or instrument family). MIT-licensed alongside the
rest of the `sheet-music` repo.

## Folder layout

```
original/
├── {tune-slug}/
│   ├── tune.abc        canonical
│   ├── tune.ly         engraved
│   ├── tune.musicxml   DAW-ready
│   ├── tune.mid        playable
│   ├── tune.svg        engraved as SVG
│   ├── tune-fingering.svg  if a fingering chart is meaningful
│   └── notes.md        composition brief, license, practice tip
```

Use `scripts/compose_original.py` to scaffold a new original. The
script writes the headers and a TODO marker for the LLM to fill in,
then the standard render pipeline produces the rest.

## Naming conventions

Two- or three-word evocative titles. No cleverness, no puns. The
brand voice prefers simple imagery: places, weather, animals, gentle
verbs. "River Reed Waltz" is canonical. So is "Dust Lullaby." Avoid
"Frequency Symphony No. 7 in B-flat Sharp" energy.

## License

Every original here is MIT-licensed. Anyone who builds the matching
instrument is free to perform, record, arrange, and adapt these
tunes. Attribution welcome but not required.

If you arrange one of these for an instrument outside Tony's catalog
and want to contribute it back, open a PR — your arrangement gets
filed alongside the original under the same license.
