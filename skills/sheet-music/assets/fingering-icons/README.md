# Fingering icons

Each instrument's fingering scheme is described by a JSON file here.
`scripts/render_fingering_svg.py` reads these to draw fingering
diagrams. When a scheme file is missing, the script falls back to a
generic 6-hole vertical placeholder and marks the SVG accordingly.

## File naming

`{scheme-name}.json` where `{scheme-name}` matches the `fingering:`
field in `instruments/registry.yaml`.

## Schema

```json
{
  "scheme": "naf-6hole",
  "instrument_family": "flute",
  "holes": [
    { "id": "h1", "y": 0, "label": "thumb (top)" },
    { "id": "h2", "y": 1, "label": "index" },
    { "id": "h3", "y": 2, "label": "middle" },
    { "id": "h4", "y": 3, "label": "ring" },
    { "id": "h5", "y": 4, "label": "index (bottom hand)" },
    { "id": "h6", "y": 5, "label": "middle (bottom hand)" }
  ],
  "fingerings": {
    "A4": ["h1","h2","h3","h4","h5","h6"],
    "C5": ["h1","h2","h3","h4","h5"],
    "D5": ["h1","h2","h3","h4"],
    "E5": ["h1","h2","h3"],
    "G5": ["h1","h2"],
    "A5": []
  }
}
```

`y` orders the holes top-to-bottom in the rendered diagram. `fingerings`
maps scientific-pitch keys (e.g., `A4`, `C#5`) to a list of hole IDs
that should be **closed**. Holes not in the list are open.

## Provided schemes (v0.1)

- `naf-6hole.json` — Native American flute, 6-hole, A-tuned default.
- `simple-system-6hole.json` — generic 6-hole transverse / PVC flute.
- `kena-6hole.json` — kena (notched) 6-hole + thumbhole.
- `fujara-3hole.json` — fujara, three holes only (most pitches via
  overtones, not fingering — see `references/flute-family.md`).
- `violin-positions.json` — violin first position fingerboard.
- `harp-fingerings.json` — string-position layout for floor harp.
- `guitar-tab.json` — six-string fretboard placeholder.
- `chalumeau-fingerings.json` — placeholder.
- `clarinet-fingerings.json` — placeholder.
- `duduk-fingerings.json` — placeholder.

Schemes with the `placeholder: true` flag will render with a dashed
"unknown" indicator on every diagram. Replacing them with real data is
a tracked v0.2 task.

## Adding a new scheme

1. Measure your build (or the reference build) — count holes, document
   their positions.
2. Determine the fingerings empirically: open all, close one at a
   time, and record the resulting pitch.
3. Write the JSON to `{scheme-name}.json`.
4. Reference it from the matching instrument's `fingering:` field in
   `instruments/registry.yaml`.
5. Run a tune through `render_fingering_svg.py` to verify diagrams
   look right.

## Cross-referencing with the build packet

If the instrument was designed with `instrument-maker-v4`, the build
packet's `design.md` or design table includes hole positions and the
calculated pitch for each fingering. Use those values directly — they
match Tony's specific build's measured tuning.
