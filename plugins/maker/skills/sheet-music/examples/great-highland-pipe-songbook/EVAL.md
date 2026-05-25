# EVAL — sheet-music v0.1 vs. Great Highland Pipe

Honest evaluation of the v0.1 skill applied to the bagpipe family,
written while building this songbook. Bagpipes were marked
*skeleton-only* in v0.1 with full support deferred to v0.2; this
eval is the punch list that v0.2 should clear.

## What worked

- **Registry mechanics.** Adding the `great-highland-pipe` row to
  `instruments/registry.yaml` was straightforward — the schema
  already had every field GHP needs (range, scale, fingering,
  ornaments list, GM preset). The free-form `notes:` block carried
  the no-rest and sounding-pitch caveats cleanly. **No code changes
  required to register a new bagpipe.**
- **Per-tune `validate_arrangement.py --strict`.** Range checks
  caught nothing problematic (every note was in G4–A5 by
  construction), and required-header enforcement (X/T/M/L/K/Q)
  worked exactly as documented. All 9 tunes in the songbook pass
  strict per-tune validation.
- **MIDI via music21.** Once `music21` was installed
  (`pip install --break-system-packages music21`), every tune
  rendered to MIDI cleanly. `abc_to_midi.py` correctly looked up
  GM preset 110 (Bagpipe) from the registry and wrote it into the
  MIDI track.
- **MusicXML via music21.** Same story — every tune rendered to
  valid MusicXML for DAW handoff.
- **Fingering SVG generation.** `render_fingering_svg.py` correctly
  picked up the `ghp-chanter-9note` scheme and rendered diagrams
  for every distinct pitch. The fingering JSON's `placeholder: true`
  flag was honored — the SVG header notes that the chart is a
  placeholder.
- **One-page songsheet PDF.** The ReportLab fallback in
  `build_songsheet_pdf.py` produced clean per-tune PDFs with title,
  meta line, notation/fingering blocks, and practice tip extracted
  from `notes.md`.
- **`compose_original.py` scaffold.** The script produced a usable
  ABC scaffold and `notes.md` brief from a single CLI call. Filling
  in the melody and ornaments by hand (Claude in the loop) was the
  intended workflow per the script's own docstring.
- **"Fail honestly" behavior.** When LilyPond and `fluidsynth`
  weren't on PATH, the pipeline reported "skipped" with concrete
  install instructions instead of producing fake output. This is
  exactly the behavior the SKILL.md documents.

## What didn't

Specific gaps where the v0.1 skill came up short for the GHP. Each
item names the file and what was missing.

### 1. `references/reeds-and-pipes.md` — bagpipe section is documentation-only
**File:** `references/reeds-and-pipes.md`, lines 48–74.
The bagpipe ornament rules (doubling, throw on D, grip, birl,
taorluath, no-rest constraint) are documented as prose but no
script reads them. I had to re-encode every ornament as raw ABC
grace clusters (`{GdG}`, `{GeG}`, `{gag}`, `{GAGA}`, `{GcdGe}`)
inline in each tune.abc. There is no skill-side library of "the
right ABC grace cluster for a doubling on F#" — every author has
to make the same lookup themselves.

### 2. `validate_arrangement.py` doesn't enforce the no-rest rule
**File:** `scripts/validate_arrangement.py`.
The bagpipe family's defining constraint — *no rests, ever* —
isn't checked. A user could include a `z` rest in a GHP tune.abc
and the validator would pass it. The reeds-and-pipes reference
explicitly says "Bagpipe arrangements without doublings on long
notes are flagged (v0.2 only)" — but the v0.1 validator has no
family-aware rules at all.

### 3. `validate_arrangement.py` directory-mode glob is buggy
**File:** `scripts/validate_arrangement.py`, line 130.
`for tune_dir in target.glob("0*-*/*/")` matches *files* inside
`00-warmup-scales/` (which the spec defines as flat — see
`references/starter-songbook.md` lines 13–19) and reports each as
"missing tune.abc / tune.mid / notes.md". On a properly
spec-shaped songbook the strict directory check fails. **One-line
fix:** add `if not tune_dir.is_dir(): continue` immediately
inside the loop, OR change the glob to only iterate true tune
subfolders by skipping `00-*`.

### 4. `compose_original.py` writes `K:A`, not `K:Amix`
**File:** `scripts/compose_original.py`, line 88.
The scaffold uses `K:{row.get("key_default", "C")}` which for
the GHP row produces `K:A` (no key signature) instead of `K:Amix`
(F# and C# implicit). I had to hand-edit the scaffold's `K:` line
to `K:Amix`. The script should consult the registry's `scale`
field (`mixolydian-A`) and emit a mode-aware ABC key when the
scale isn't plain major.

### 5. `compose_original.py` slug-to-title doesn't add apostrophes
**File:** `scripts/compose_original.py`, line 56.
`title_from_slug("drovers-path")` produced "Drovers Path"; I had
to hand-edit it to "Drover's Path". Not a bagpipe-specific issue,
but it bit me here. The script could accept a `--title` override.

### 6. `render_fingering_svg.py` placeholder flag is the only signal of fidelity
**File:** `scripts/render_fingering_svg.py`, lines 78–95.
A scheme JSON with `"placeholder": true` produces a small note in
the SVG header — but the rendered output looks almost identical to
a non-placeholder. There's no visible "USE WITH CAUTION" treatment
on the diagrams themselves, and no guarantee that the scheme's
`fingerings` map is internally consistent (e.g., monotonic
hole-closure as pitch rises). I left the placeholder as authored
but flag this — a piper using my placeholder JSON might think it's
authoritative.

### 7. The skill's repertoire picker doesn't know about Celtic / pipe-band tradition
**File:** `scripts/deposit_songbook.py`, lines 64–80.
`pick_repertoire()` picks the alphabetically-first 3 PD tunes as
"easy" and the next 2 as "intermediate". For the GHP I bypassed
this entirely and curated the 5 tunes by hand. There's no way for
a user to say "give me 3 Celtic tunes" — and the GHP can only play
A-mixolydian repertoire, but the picker has no notion of "tunes
playable on this instrument". For v0.2: filter the PD pool by
the instrument's `key_default` and `scale` before picking.

### 8. The 02-intermediate convention isn't supported by the deposit script
**Convention from this handoff:** "02-intermediate (2 of those
tunes re-arranged with denser ornamentation)" — i.e., the same
melodies as 01-easy with more ornaments.
The deposit script picks *different* tunes for intermediate, which
is what `references/starter-songbook.md` describes (longer/wider
range tunes from a different pool). Both conventions are
defensible but they conflict. Either the spec changes or the
deposit script grows a `--intermediate-style {different,
re-ornamented}` flag.

### 9. `assets/fingering-icons/ghp-chanter-9note.json` is mine, not measured
**File:** the new file I just wrote.
The fingering map is the textbook beginner positions from memory;
I have no authoritative measurements (e.g., from College of Piping
or the Piobaireachd Society manual). The file declares
`"placeholder": true` to make this honest, but the skill has no
established workflow for "promote a placeholder fingering JSON to
authoritative" — no measurement-import tool, no checklist, no
verification step.

### 10. No bagpipe soundfont packaged
**File:** `assets/soundfonts/README.md`.
GM preset 110 ("Bagpipe") sounds nothing like a Great Highland
chanter — it's a pretty rough approximation. For audio renderings
to be useful for the GHP, the skill needs a packaged bagpipe-
specific soundfont (or at least a pointer to one in
`references/audio-rendering.md`). For this stress test, audio
rendering was skipped entirely — which is honest behavior, but
means the songbook ships without playable WAVs.

### 11. The compose_original.py reference to non-existent file
**File:** `scripts/compose_original.py`, line 98.
Generated `notes.md` instructs: "Read `references/reeds-and-pipes-family.md`" — but that file doesn't exist. The actual file is
`references/reeds-and-pipes.md` (no `-family` suffix). The
template's family-name interpolation appends `-family.md` but the
reeds-and-pipes reference is named without the suffix, while
flute-family.md and strings-family.md do use the suffix. Either
rename `reeds-and-pipes.md` to `reeds-and-pipes-family.md` for
consistency, or special-case the template.

### 12. Filesystem sync drift between Write tool and bash mount
**Process issue, not a code issue.**
During this stress test, several files written via the Cowork
Write tool were truncated when read from the bash sandbox mount
(`catalog/original/drovers-path/tune.abc` was 15 lines via bash
but full via Read). I worked around it by re-writing the affected
files via `cat << 'EOF'` heredoc directly through bash. Worth
noting in the skill's authoring docs since other Cowork users may
hit the same.

## v0.2 recommendations

Concrete, ordered list of diffs that would make GHP production-ready.

### P0 — correctness fixes (block v0.2)

1. **Patch `validate_arrangement.py` directory glob.**
   ```diff
    for tune_dir in target.glob("0*-*/*/"):
   +    if not tune_dir.is_dir():
   +        continue
   ```
   And/or skip `00-*` explicitly. Currently strict directory mode
   fails on every spec-shaped songbook with flat warmups.

2. **Family-aware no-rest validation.** In
   `validate_arrangement.py`, after loading the registry row,
   if `family == "reeds-and-pipes" and subfamily == "bagpipe"`,
   refuse any `z` token in the body.

3. **Mode-aware `K:` line in `compose_original.py`.** When the
   registry `scale` is `mixolydian-A` (or any non-major mode),
   emit `K:Amix`, `K:Adorian`, etc. instead of just `K:A`.

4. **Rename or symlink `references/reeds-and-pipes.md` to
   `reeds-and-pipes-family.md`** so the auto-generated `notes.md`
   pointer resolves. Alternatively patch the template.

### P1 — bagpipe-specific feature work

5. **Ornament library.** Add `assets/ornaments/bagpipe.json` with
   the canonical grace clusters keyed by ornament-on-pitch:
   `{ "doubling": { "A": "{GdG}", "B": "{GdG}", "C#": "{GdG}",
   "D": "{GeG}", "E": "{ge}", "F#": "{gf}", "high-G": "{ag}",
   "high-A": "{gag}" }, "throw-on-D": "{GcdGe}", "birl":
   "{GAGA}", "grip": "{GdG}" }`. Then add a script
   `scripts/insert_ornaments.py --tune <abc> --instrument
   great-highland-pipe --policy
   {long-notes-only,every-quarter,intermediate,piobaireachd}`
   that auto-inserts the right cluster per pitch. This is the
   biggest pedagogical win — beginners shouldn't have to look up
   doubling clusters by hand.

6. **Authoritative fingering JSON.** Promote
   `assets/fingering-icons/ghp-chanter-9note.json` from placeholder
   by sourcing from the College of Piping manual or the
   Piobaireachd Society's published charts. Add a verification
   step that confirms hole-closure is monotonic with falling pitch.

7. **Bagpipe soundfont pointer.** Add a section to
   `references/audio-rendering.md` listing one or two
   freely-available GHP soundfonts (e.g., Sonatina Symphonic
   Orchestra includes a bagpipe; FreePats has options). Don't
   commit soundfonts to the repo — link them.

8. **Family-aware quality gates in `validate_arrangement.py`.** As
   already documented in `references/reeds-and-pipes.md` line 95:
   "Bagpipe arrangements without doublings on long notes are
   flagged (v0.2 only — bagpipes are skeleton in v0.1)." Implement
   this: scan the body for principal notes longer than a quarter
   that aren't preceded by a `{...}` cluster; warn for each.

### P2 — repertoire and pedagogy

9. **Filter `pick_repertoire()` by playable scale.** A tune in
   F major shouldn't get picked for a GHP songbook. Compare the
   tune's `K:` header against the instrument's `scale` and reject
   mismatches.

10. **Add a `--intermediate-style` flag to `deposit_songbook.py`.**
    Two valid conventions: pick different tunes (the existing
    spec) vs. re-ornament easy tunes (the GHP-songbook handoff).
    Let the user choose.

11. **Curate a Celtic tradition folder.** This stress test added
    `catalog/public-domain/celtic/` with three tunes; v0.2 should
    grow it to ~10-15 standard pipe-band repertoire pieces
    (Highland Cathedral, Atholl Highlanders, Mairi's Wedding,
    Skye Boat Song, etc.) so the picker has range when GHP is the
    target.

12. **Title override in `compose_original.py`.** Add `--title
    "Drover's Path"` so the slug-to-title default can be
    overridden when punctuation matters.

### P3 — nice to have

13. **Visible "placeholder" treatment in fingering SVGs.** A
    diagonal "DRAFT" watermark or a red border when
    `placeholder: true`, beyond the small text in the header.

14. **`scripts/render_fingering_svg.py` — render the thumb hole
    on the back.** The current top-down vertical layout shows all
    8 holes on the front; the GHP's thumb hole is on the back of
    the chanter. A side-view diagram with front/back faces would
    be more informative.

15. **Doublings tutorial in `references/reeds-and-pipes.md`.**
    Walk a player through the four canonical doublings with audio
    and notation examples. Today the section is a paragraph; it
    should be a tutorial-grade reference.

## Verdict

The v0.1 skill, advertised as bagpipe-skeleton, **shipped enough
machinery for a stress test to produce a complete, validating,
playable songbook for the Great Highland Pipe in a single Cowork
session.** The chassis is right. The bagpipe-specific gaps are
narrow and clearly identified. v0.2 looks like ~8–12 hours of
focused work, primarily: ornament library, family-aware validator
rules, fingering-JSON promotion, soundfont guidance, and a couple
of one-liner script fixes.

The most important v0.2 win, by far, is the **ornament library
(item #5)** — it's what turns the GHP from "playable in this
skill" into "pleasant to author for in this skill."
