# Changelog — source-citations

## 0.2.0 — 2026-06-19

- Add first machine-runnable eval suite (`evals/evals.json`): 5 evals covering
  registry build from TSV, SOURCES.md generation with valid citations,
  unknown-key rejection, blank-why rejection, and citation-candidate proposal
  without auto-write.

## 0.1.0 — 2026-05-22

Initial release.

### Added

- **Bibliography registry** (`references/registry.yaml` + `.json`, 201 keyed
  entries) built from `references/library.tsv` (the Drive source-library
  export) via `scripts/build_registry.py`. Keys are deterministic, unique, and
  treated as a stable contract once cited.
- **Per-repo citation flow.** `scripts/gen_sources.py check` validates a
  repo's `.citations.yaml` against the registry and refuses to ship if any
  key is unknown or any `why` rationale is blank. `gen_sources.py gen` writes
  `SOURCES.md` grouped by lifecycle bucket; the maker hand-edits
  `.citations.yaml`, never the generated file.
- **Techniques catalog** (`references/techniques.yaml`) — companion registry
  of maker demonstrations (timestamped YouTube moments, MakerTok / Instagram
  clips, wikiHow, makerspace notes). Two-status model: `confirmed` (a human
  watched and verified) versus `unconfirmed` seed (creator + URL real, moment
  not yet verified). `scripts/gen_techniques.py check` hard-refuses any
  attempt to cite an unconfirmed seed; `gen` writes per-repo `TECHNIQUES.md`,
  `site` writes a Quarto `.qmd` that embeds confirmed YouTube clips at their
  exact `start` second, and `audit` lists entries by status.
- **Capture flow.** `captures/` holds local Obsidian Web Clipper notes per
  technique key, so the durable record survives if the live URL rots.
- **References.** `references/instrument-tagging.md` (controlled vocabulary
  for instrument tags), `references/rollout.md` (4-state coverage dashboard
  pattern: MISSING / INVALID / UNBUILT / OK), `references/techniques-catalog.md`
  (technique data model + capture flow), `references/citations-template.yaml`
  (copy into a repo as `.citations.yaml`).
- **Smoke tests** (`tests/test_smoke.py`) — round-trip regression rig:
  rebuilds the registry from `library.tsv`, asserts entry/key counts, runs
  `gen_sources.py check`+`gen` on a tiny fixture and diffs the output, and
  runs `gen_techniques.py audit` + `site` against the bundled techniques
  registry. No external deps; run with `python3 tests/test_smoke.py`.

### Fixed

- `_scalar()` in both `gen_sources.py` and `gen_techniques.py` now strips
  unquoted YAML inline comments (` #…`). Without this, a seed declared as
  `platform: web  # youtube | instagram | …` rendered with the comment
  embedded in the URL label. Quoted scalars and mid-token `#` (e.g. URL
  fragments) are left alone.

### Notes

- v0.1.0 ships **no** `source-citations` shell command. Use
  `skills-meta` for version reporting and `python3 scripts/<tool>.py` for
  the actual workflow until a command shim is added.
- Per-repo pilot rollout across the public "done-bar" instrument repos
  (transverse-flute, kora, handpan, tongue-drum, then gemshorn, udu, ocarina,
  …) happens on the desktop where those repos live; this package only ships
  the skill and the registry.
