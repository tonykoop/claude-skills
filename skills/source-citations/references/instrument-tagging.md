# Tagging The Library By Instrument

Tagging sources by instrument *first* is the recommended first pass: it converts
per-repo citation from a search ("which of 200 sources apply to my kora?") into
a menu pick ("show me everything tagged `string` and `kora`"). This is the
choice made for this rollout.

## Why tag before citing

- A source like Demakein applies to many woodwinds; tagging it once with
  `flute, whistle, recorder, woodwind` means every woodwind repo's curation
  starts from a short relevant list.
- General-physics sources (Fletcher & Rossing, JASA) get a broad family tag,
  not a specific instrument, so they surface for the right repos without
  polluting unrelated ones.
- Tagging is still **human judgement**. A tag asserts "this source is plausibly
  relevant to this instrument class," not "this repo cites it." The actual
  citation decision — and the `why` — still happens per repo in step 2.

## Controlled vocabulary

Use family tags for breadth and instrument tags for specificity. Prefer the
fewest tags that are true.

**Families:** `woodwind`, `string`, `percussion`, `idiophone`, `membranophone`,
`free-reed`, `electronic`, `general` (cross-cutting theory/tooling).

**Instruments (extend as repos demand):** `flute`, `whistle`, `recorder`,
`ocarina`, `gemshorn`, `duduk`, `clarinet`, `panpipe`, `kora`, `harp`, `ngoni`,
`violin`, `guitar`, `ukulele`, `zither`, `tongue-drum`, `handpan`, `marimba`,
`xylophone`, `chime`, `bell`, `udu`, `djembe`, `ashiko`, `conga`, `rainstick`.

**Lifecycle/tooling tags already on each entry** (from the spreadsheet `tags`
column — solver, calculator, CAD, CAM, library, hardware, FEM, community) stay
as-is; instrument tags are *added*, not a replacement.

## Procedure

Two equivalent ways to hold the instrument tags:

1. **In the spreadsheet (preferred for Tony's workflow).** Add an `instruments`
   column to the Drive sheet, fill it with semicolon-separated tags, and
   re-export to `library.tsv` with that column. `build_registry.py` already
   carries an `instruments` list on every entry; extend the TSV reader to read
   the column if you add it. This keeps the human-maintained master complete.

2. **Directly in `registry.yaml`.** Edit the `instruments: []` line on each
   entry. Faster for a quick pass, but remember the registry is regenerated
   from the TSV, so a sheet column is the durable home.

Suggested order:

- Start with the ★ priority entries — they are the sources most likely to be
  cited and the highest-value to tag well.
- Tag by section: a whole spreadsheet section often shares a family
  (e.g. §2 Flute & whistle calculators → `woodwind, flute, whistle`).
- Leave `general` theory sections (§32) mostly family-level or `general`.

## How an agent may help (within the integrity rule)

An agent may **propose** instrument tags for the maker to confirm, since a tag
is a weaker claim than a citation. Present proposals as a table the maker edits;
do not silently write them as final. The hard rule still holds at the citation
step: the agent never writes a repo's `.citations.yaml` entries on its own.
