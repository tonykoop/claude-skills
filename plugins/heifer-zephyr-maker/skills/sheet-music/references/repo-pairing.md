# Pairing with `instrument-maker-v4`

`instrument-maker-v4` builds the instrument; `sheet-music` writes the
music for it. The two skills share an instrument identifier and a
folder convention so that handoff is mechanical, not interpretive.

## The shared identifier

Each instrument has a stable `id` (snake-case, no version suffix):

```
naf-6hole, pvc-flute, drone-flute, kena, moseno, fujara,
acoustic-violin, electric-violin, ceramic-electric-violin, floor-harp,
electric-guitar, cnc-guitar, chalumeau, clarinet, duduk,
conga, djembe, cajon, dundun, ashiko, frame-drum, tongue-drum,
ceramic-tongue-drum, ceramic-hang
```

This `id` appears in three places:

1. `instrument-maker-v4`'s catalog (the `Catalog v3` table inside
   `Instrument Workshop Master v3.xlsx`, and the SQLite mirror at
   `Instrument Workshop Master.sqlite`).
2. `sheet-music`'s `instruments/registry.yaml`.
3. The build repo folder name on disk, e.g.,
   `~/Documents/GitHub/fujara/`.

When this skill needs an instrument's design parameters (range,
fingering layout, measured spectrum), it reads from
`instrument-maker-v4`'s catalog. When `instrument-maker-v4` ships a
new build packet, the documentarian step adds the `id` to this skill's
registry if it isn't there yet.

## Reading from the instrument-maker catalog

`instrument-maker-v4` exposes the catalog as a SQLite database:

```python
import sqlite3
conn = sqlite3.connect(
    "/path/to/instrument-maker/Instrument Workshop Master.sqlite"
)
row = conn.execute("""
    SELECT id, family, range_low, range_high, default_key, fingering_scheme,
           measured_spectrum_path
    FROM catalog WHERE id = ?
""", ("fujara",)).fetchone()
```

`scripts/sync_with_instrument_maker.py` (v0.2 roadmap) will read the
catalog database periodically and update `instruments/registry.yaml`
with new instruments or revised ranges. Until then, the registry is
maintained by hand — one row per build.

## Writing into a build repo

The deposit step writes `learn-to-play/` into the build repo:

```python
target = Path.home() / "Documents" / "GitHub" / instrument_id
deposit_path = target / "learn-to-play"
```

Build repo names in Tony's GitHub use slightly different conventions than
the instrument `id`:

| Instrument id | Build repo name |
|---|---|
| naf-6hole | flutes |
| pvc-flute | flutes |
| drone-flute | drone-flutes |
| kena | kena |
| moseno | moseno |
| fujara | fujara |
| andean-duct-flute | andean-duct-flutes |
| acoustic-violin | acoustic-violin |
| electric-violin | electric-violin |
| ceramic-electric-violin | ceramic-electric-violin |
| floor-harp | floor-harp |
| electric-guitar | electric-guitar-bodies |
| cnc-guitar | cnc-guitar-bodies |
| chalumeau | chalumeau |
| clarinet | clarinet |
| duduk | duduk |
| conga | conga |
| djembe | djembe |
| cajon | cajon |
| dundun | dundun |
| ashiko | ashiko-drum-workshop |
| frame-drum | frame-drum |
| tongue-drum | ceramic-tongue-drum (no separate wood repo yet) |
| ceramic-tongue-drum | ceramic-tongue-drum |
| ceramic-hang | ceramic-hang |

This mapping lives in the `build_repo` field of each registry row and
is what `deposit_songbook.py --target` resolves to when given just an
instrument `id`.

For instruments where multiple `id`s share a single build repo (NAF
and PVC both under `flutes`), the deposit creates a per-instrument
subfolder: `flutes/learn-to-play/naf-6hole/` and
`flutes/learn-to-play/pvc-flute/`.

## Data flow

```
[user builds instrument from instrument-maker-v4 packet]
           ↓
[Catalog row exists with id, range, fingering, etc.]
           ↓
[user asks Claude for music for that instrument]
           ↓
[sheet-music skill triggers]
           ↓
[skill reads its registry; if missing, syncs from instrument-maker catalog]
           ↓
[skill picks repertoire, arranges, renders, validates]
           ↓
[skill deposits learn-to-play/ into the build repo folder]
           ↓
[skill updates the build repo's README to link to learn-to-play/]
           ↓
[user commits and pushes via GitHub Desktop]
```

## When `instrument-showcase` is also in the picture

Tony has a separate `instrument-showcase` skill that produces a
public-facing build-log site for each instrument. When that skill runs,
it links to `learn-to-play/` from the showcase site's nav. The
relationship is:

- `instrument-maker-v4` owns the *design* (CAD, drawings, BOM, spec).
- `sheet-music` owns the *music* (notation, audio, songbook).
- `instrument-showcase` owns the *narrative* (a polished website).

Each has its own repo. Each reads from the others without owning their
content. `sheet-music` is the middle layer — its outputs are inputs to
`instrument-showcase`.

## Versioning conventions

This skill carries a `version` line in `SKILL.md` (currently `v0.1`).
When a backward-incompatible change happens to the `learn-to-play/`
folder layout or to the registry schema, bump the major version and
note the migration step in `references/changelog.md`.

`instrument-maker-v4`'s version is independent. The two can be at
different versions; the only contract is the shared instrument `id`.
