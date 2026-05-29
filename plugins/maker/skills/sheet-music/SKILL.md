---
name: sheet-music
version: 0.1.0
last-updated: 2026-05-20
description: Generate sheet music, fingering charts, MIDI, audio renderings, and printable songsheets for the musical instruments built from Tony Koop's instrument-maker repos. Trigger whenever the user mentions writing/transcribing/arranging a song or tune, ABC/LilyPond/MusicXML, sheet music, fingering chart, tablature, songbook, beginner songbook, learning to play a flute/violin/harp/duduk/etc., pairing music with a build packet, generating practice scales or warm-up exercises for a custom-built instrument, dropping a `learn-to-play/` folder into a build repo, or commissioning an original "Heifer Zephyr" tune. Also trigger when an instrument-maker-v4 packet ships and the user wants a starter songbook to accompany it. Pairs with `instrument-maker-v4`, reads its `instruments/registry.yaml`, and can deposit per-instrument songbooks into sibling build repos under `C:\Users\Tony\Documents\GitHub\{instrument}\learn-to-play\`.
---

# sheet-music

The companion skill to `instrument-maker-v4`. Once a builder has finished their
flute, harp, duduk, or guitar from a Tony Koop build packet, this skill
produces the music to play on it: notation in multiple formats, fingering
charts, MIDI, rendered audio, and a printable one-page songsheet — sized to
the instrument's range and ornament tradition.

This skill is built for **Cowork mode** where Claude can generate real `.abc`,
`.ly`, `.musicxml`, `.mid`, `.wav`, `.svg`, and `.pdf` files. When an MCP
connector is available (Adobe Creative Cloud for PDF/SVG export, Ableton for
DAW-side rendering), the skill orchestrates handoff. When tools are missing,
it gracefully degrades to text-only deliverables (ABC + ASCII fingering)
and explicitly marks which generators were skipped.

## Connectors

This skill works best with these MCP connectors. Claude will suggest connecting any that aren't already linked at the point they're needed (via `mcp__mcp-registry__suggest_connectors`).

- **Spotify** (`86925244-b3bb-415b-b7e8-6e3cd1392247`) — optional for referencing recorded versions of public-domain tunes, building a "listen-along" playlist for the starter songbook, and pulling track audio features.
- **Adobe for Creativity** (`22854937-9510-4b57-9230-62c820102d8f`) — optional for SVG to PDF polish on songsheets, photo overlays on cover pages, Quick Cut of performance videos.
- **GitHub** — optional for depositing the per-build `learn-to-play/` folder as a PR or commit into the target instrument repo. No registry UUID; configure via the Claude Code GitHub connector if available.

## Output shape: per-build "starter songbook" + central catalog

The skill produces deliverables in **one of two folder shapes**, picked by
intent. Most of the time, both run together.

**Mode A — Starter songbook deposit** (default for "make me music for the
[instrument] I just built"). The skill writes a `learn-to-play/` folder into
the *target build repo* (e.g.,
`C:\Users\Tony\Documents\GitHub\drone-flutes\learn-to-play\`). Contents:

```
learn-to-play/
├── README.md            # how to read the materials, range chart
├── 00-warmup-scales/    # range walk, intervals, ornament drills
├── 01-easy/             # 3 PD beginner tunes arranged for THIS instrument
├── 02-intermediate/     # 2 tunes with simple ornamentation
├── 03-original/         # 1 Heifer Zephyr original written for this build
├── fingering-charts.svg # combined chart for the instrument's full range
└── songsheet.pdf        # printable one-page reference
```

Each tune folder contains: `tune.abc` (canonical), `tune.ly` (engraved),
`tune.musicxml` (DAW-ready), `tune.mid` (playable), `tune.wav` (rendered
preview, if soundfont present), `tune-fingering.svg` (notes annotated with
fingering), and `notes.md` (history, range checks, practice tips).

Use Mode A when the prompt names a target instrument or build repo.

**Mode B — Central catalog entry** (use when growing the shared library).
Files land in `catalog/public-domain/{tradition}/{tune-slug}/` or
`catalog/original/{tune-slug}/` inside the `sheet-music` repo itself. Same
file types, but the canonical ABC is written for *concert pitch* and the
arrangement step is deferred — the same canonical tune can later be deposited
into many build repos. Use Mode B when the prompt is "add tune X to the
catalog" or "transcribe this PD tune for the library."

The two modes share the engine. Mode A is Mode B + arrange-for-instrument +
deposit. If the user's intent is ambiguous, ask which mode.

## Operating principles

- **Notation first, audio second.** ABC is the canonical source. LilyPond,
  MusicXML, MIDI, WAV, and SVG fingering charts are all derived. Never edit
  the derived files by hand; regenerate from ABC.
- **Range-validate every arrangement.** Before producing a derived file,
  check the melody fits the target instrument's range and fingering system.
  Refuse silently-clipped output: either transpose, simplify, or surface
  the problem to the user.
- **Copyright is non-negotiable.** Public-domain only for traditional
  repertoire (pre-1929 in the US, plus explicitly-PD modern works). Originals
  are composed fresh and licensed under MIT alongside the rest of the repo.
  User-supplied melodies require the user to assert provenance — capture
  this in `notes.md` for that tune.
- **Pedagogy beats virtuosity.** This is a beginner skill. Prefer simple
  rhythms, conjunct motion, ornament-light arrangements with optional
  ornamented variants for advanced players. Drone-flute and bagpipe
  ornaments are the exception — those traditions *require* embellishment.
- **Honor the tradition.** Bagpipe music has no rests. Duduk has glides.
  Andean duct flutes use specific cross-fingerings. The skill's
  family-reference docs encode the rules per tradition.
- **Fail honestly.** If `fluidsynth` isn't installed, don't fake a WAV — say
  "WAV skipped: fluidsynth not on PATH; install via apt/brew/choco and rerun
  `scripts/render_audio.py`." Same for `lilypond`, `abc2midi`, `music21`,
  Adobe MCP, Ableton MCP. The print packet generators in `instrument-maker-v4`
  follow the same convention.

## Core workflow (orchestrator view)

You — the orchestrator — read this SKILL.md, look at the prompt, and walk the
pipeline. Steps marked with **(family-specific)** branch into the relevant
reference doc.

1. **Identify the instrument.** Read `instruments/registry.yaml`. If the
   instrument isn't there, add a row from the user's `instrument-maker-v4`
   build packet (read `Catalog v3` table from the workshop master, or ask).
2. **Identify the deliverable.** Starter songbook (Mode A)? Single tune
   (Mode B)? Practice scales? Range chart? Original commission? Existing
   catalog tune arranged for a new instrument?
3. **Pick the family.** Read the relevant reference doc for the rules:
   - `references/flute-family.md` — open/stopped/ducted/transverse, breath
     marks, simple ornaments, range mapping (NAF, PVC, fujara, andean
     duct, drone-flutes, kena, moseno).
   - `references/strings-family.md` — staff + TAB for guitars, bowing for
     violin, lever changes for harp (electric/acoustic violin, floor-harp,
     guitars).
   - `references/reeds-and-pipes.md` — bagpipe ornaments, duduk glides,
     chalumeau range (chalumeau, clarinet, duduk, future bagpipe).
   - `references/percussion.md` — stroke notation (B/T/S/M), pattern
     loops (conga, djembe, cajon, dundun, ashiko, frame-drum, tongue-drum).
4. **Compose or arrange (family-specific).** For PD tunes, look up the
   canonical ABC in `catalog/public-domain/{tradition}/`. For originals,
   compose using the family-spec parameters. For user-supplied melodies,
   parse to ABC.
5. **Validate range and fingering.** Run `scripts/validate_arrangement.py`
   against the target instrument. If notes fall outside range, transpose;
   if they require unsupported cross-fingerings, simplify or substitute.
6. **Render the pipeline.** Run `scripts/render_pipeline.py` which calls,
   in order: `abc_to_midi.py`, `abc_to_lilypond.py`, `abc_to_musicxml.py`,
   `render_fingering_svg.py`, `render_audio.py`, `build_songsheet_pdf.py`.
   Each step is independently re-runnable.
7. **Deposit (Mode A only).** Run `scripts/deposit_songbook.py
   --target {build-repo}` to write the `learn-to-play/` folder into the
   target build repo. The script also updates that repo's README to link
   to the new songbook.
8. **Commit signals.** Print the list of files written, the path to each
   one (using `computer://` links so the user can open them), and the
   intended next step ("commit and push from GitHub Desktop").

## When to call which sub-routine

| User says... | Run... |
|---|---|
| "make a starter songbook for my [instrument]" | Mode A pipeline, end-to-end |
| "add [PD tune] to the catalog" | Mode B, single tune |
| "compose an original for the [instrument]" | `scripts/compose_original.py` then Mode A pipeline for that one tune |
| "I just built a [instrument] from my [repo] — give me music" | Mode A, end-to-end |
| "warm-up scales for [instrument]" | `scripts/generate_scales.py`, range-walk + intervals |
| "transcribe this melody for [instrument]" | parse user input → ABC → Mode A pipeline |
| "what fingerings for [pitch] on [instrument]?" | read `instruments/registry.yaml`, render fingering SVG only |
| "render audio for [tune]" | `scripts/render_audio.py` only |
| "make a printable songbook PDF" | `scripts/build_songsheet_pdf.py`, optionally via Adobe MCP |
| "open this in Ableton" | `references/ableton-handoff.md` — produce MusicXML + MIDI + a prompt template the user pastes into the Claude+Ableton connector |

## Cross-skill handoffs

- **Coming in from `instrument-maker-v4`.** When a build packet ships, the
  `documentarian` agent links the new instrument's row in
  `Catalog v3` to a `learn-to-play/` URL. This skill produces that folder.
  Read `instrument-maker-v4`'s `references/build-log-site.md` for the
  build-log site template — the songbook lives at `/learn-to-play` in
  that site's nav.
- **Outgoing to Adobe Creative Cloud.** For polished printable
  songsheets, route through the Adobe MCP (`document_render_layout`,
  `document_convert_pdf`). Fall back to ReportLab if the connector
  isn't available. See `references/adobe-handoff.md`.
- **Outgoing to Ableton.** For backing tracks or audio polish, hand off
  the MIDI + MusicXML to the Ableton connector. The skill writes a
  ready-to-paste prompt that names the tempo, key, instrument timbre, and
  song structure. See `references/ableton-handoff.md`.

## Bundled resources

- `instruments/registry.yaml` — canonical instrument list. Each entry
  has range, transposition, fingering system, family, default soundfont
  preset, ornament conventions, and the GitHub repo URL it pairs with.
  Adding a new instrument = adding a row.
- `catalog/public-domain/` — curated PD tunes by tradition (irish,
  appalachian, andean, sea-shanty, hymn, nursery, etc.). Each tune has its
  canonical concert-pitch ABC, a `notes.md` with provenance, and (where
  it exists) a license-clearance note.
- `catalog/original/` — Heifer Zephyr originals. MIT licensed. Each tune
  has the same shape as PD tunes plus a "designed for" field linking to
  the build the tune was commissioned for.
- `references/` — family rules (flute, strings, reeds-and-pipes,
  percussion), notation format cheatsheet, audio-rendering pipeline,
  Adobe handoff, Ableton handoff, starter-songbook layout.
- `scripts/` — the actual converters and pipeline orchestrators.
- `assets/` — SVG fingering primitives, the songsheet PDF template, the
  README template that ships inside each `learn-to-play/` folder.
- `tests/` — pytest suite that validates every script with sample
  inputs.
- `evals/` — skill-creator eval prompts used to benchmark this skill.

## Adding a new instrument

1. Add a row to `instruments/registry.yaml`. Pull range and tuning from
   the matching `instrument-maker-v4` build packet's design table.
2. If the instrument introduces a new fingering system not yet in
   `assets/fingering-icons/`, add the SVG primitives (one per hole or key,
   open/closed states).
3. If the family isn't covered by an existing reference doc, write a new
   one in `references/` and link it from the routing table above.
4. Add three test cases to `tests/`: range-walk scales, one PD tune
   arrangement, one original commission.
5. Update `README.md`'s instrument table.

## Adding a new tune to the catalog

1. Confirm public-domain status. US: published before 1929, or explicit
   PD declaration. Note source in `notes.md` (e.g., "from Cecil Sharp's
   *English Folk Songs from the Southern Appalachians*, 1917, PD").
2. Write canonical ABC at concert pitch in
   `catalog/public-domain/{tradition}/{slug}/tune.abc`. Include `T:`,
   `C:`, `M:`, `L:`, `K:` headers and source attribution in `H:`.
3. Run `scripts/render_pipeline.py --tune {path}` to verify it renders
   in all formats.
4. Don't pre-arrange for any instrument. Arrangements happen on deposit
   (Mode A) or on demand.

## Composing originals

Run `scripts/compose_original.py --instrument {id} --mood {mood} --form {form}`.
The script doesn't actually compose by itself — it scaffolds an ABC stub
with the instrument's range, scale, and a structural template (AABA, ABAB,
through-composed) and asks Claude (the orchestrator) to fill in the notes
based on the family reference rules. Originals are filed under
`catalog/original/{slug}/` and licensed MIT alongside the rest of the repo.

The Heifer Zephyr brand voice for original tune titles: italic-serif on
wordmark only, otherwise plain. Tunes are named with simple, evocative
two-or-three-word titles ("River Reed Waltz" was a perfect example).
Don't get cute.

## Quality gates

Before declaring a tune "done":

- [ ] ABC parses cleanly (round-trips to MIDI without errors)
- [ ] All notes fall within the target instrument's range
- [ ] Required ornaments present (bagpipe doublings, duduk glides, etc.)
- [ ] LilyPond renders without warnings
- [ ] MIDI plays at the declared tempo
- [ ] Fingering SVG includes every distinct pitch in the tune
- [ ] Songsheet PDF fits one page at the declared paper size
- [ ] `notes.md` has provenance, range info, and at least one practice tip
- [ ] If WAV was rendered, soundfont preset matches the instrument family

`scripts/validate_arrangement.py --strict` enforces the first six.

## Failure modes to watch for

- **Out-of-range arrangements.** A C-major folk tune drops below the
  fundamental of an A-tuned NAF. Solution: transpose, or pick a different
  tune. Don't silently clip.
- **Wrong-tradition ornamentation.** Adding bagpipe doublings to an
  Appalachian fiddle tune. Solution: ornaments are family-specific; check
  the family reference before adding any.
- **Stale derived files.** ABC was edited but the MIDI/SVG/PDF weren't
  re-rendered. Solution: re-run `scripts/render_pipeline.py` after every
  ABC edit. The pipeline is idempotent.
- **Fake-rendered audio.** Skipping `fluidsynth` and pretending a WAV was
  produced. Don't. Mark it "skipped, install fluidsynth to render."
- **Copyright drift.** A PD tune is *credited* to a public-domain author
  but the *specific arrangement* the user transcribed was published
  recently. The melody line is fine; verbatim modern arrangements are not.
  When in doubt, write the arrangement fresh from the lead sheet.
- **Hard-coded build-repo paths.** `deposit_songbook.py` accepts a
  `--target` path; never hard-code Tony's specific Documents folder
  inside the script. The skill should work for anyone who clones the repo.

## What this skill is *not*

- Not a real-time performance tool. No live MIDI playback, no recording.
- Not a music theory tutor. The accompanying `notes.md` files include
  practice tips but assume the user can read basic notation. If a deeper
  theory tutorial is needed, the user can ask Claude directly — it's not
  this skill's job.
- Not a transcription engine for audio. Audio-to-notation is its own beast
  and would belong in a separate skill (or be handled by the Ableton
  connector's MIDI extraction).
- Not a copyright-laundering tool. If a tune's status is unclear,
  `validate_arrangement.py` flags it and refuses to write to the catalog.

## Scope of v0.1 (current release)

**Fully supported families:** flutes (NAF, PVC, drone-flutes, andean
duct, fujara, kena, moseno) and strings (electric/acoustic violin, floor
harp, electric/CNC guitars).

**Skeleton support:** reeds-and-pipes (chalumeau, clarinet, duduk) and
percussion (conga, djembe, cajon, dundun, ashiko, frame-drum,
tongue-drum, ceramic-tongue-drum). The reference docs exist; the
fingering/stroke icons are partial; arrangements pass through the
pipeline but expect rougher output until v0.2.

**Roadmap (v0.2+):**

- Full bagpipe support (Great Highland chanter, plus chalumeau-as-chanter
  experiments using Tony's reed flutes).
- Audio-aware composition: feed `instrument-maker-v4`'s measured spectrum
  data into a soundfont selection step so rendered audio actually
  matches the maker's specific build.
- Hand-tracked fingering animation (SVG → animated GIF showing finger
  motion through a tune).
- Songbook PDF templates per tradition (Celtic-styled, Andean-styled,
  Appalachian-styled).

## References

- `references/notation-formats.md` — ABC, LilyPond, MusicXML, MIDI primer.
- `references/flute-family.md` — flute notation rules and fingering systems.
- `references/strings-family.md` — staff/TAB rules and harp lever handling.
- `references/reeds-and-pipes.md` — ornaments, glides, chanter ranges.
- `references/percussion.md` — stroke notation and pattern loops.
- `references/audio-rendering.md` — MIDI → WAV pipeline, soundfont sources.
- `references/adobe-handoff.md` — printable PDF via Adobe Creative Cloud MCP.
- `references/ableton-handoff.md` — backing tracks via Ableton MCP.
- `references/starter-songbook.md` — `learn-to-play/` folder layout.
- `references/repo-pairing.md` — how to read `instrument-maker-v4`'s
  catalog and pair with build packets.

Companion skill: **instrument-maker-v4** (designs the instrument; this
skill writes the music for it).
