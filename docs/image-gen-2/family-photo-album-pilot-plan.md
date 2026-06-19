# Family Photo Album — Pilot Plan

Issue: https://github.com/tonykoop/claude-skills/issues/93

A repo-backed family photo album book: curate twenty years of photos into a
thoughtful, polished book workflow. The issue names two blockers: design
confidence and tooling. This plan addresses both with a pilot-first approach.

For the privacy workflow (source-photo policy, consent, metadata rules,
proof-review gates), see:

`plugins/maker/skills/idea-incubator/references/photo-album-private-media-pilot.md`
`plugins/maker/skills/idea-incubator/references/private-media-family-archive.md`

This doc covers the **pilot scope, selection heuristic, narrative arc, and the
image-gen-2 role** — the editorial and creative side, not the privacy/pipeline
side.

## Pilot-first rule

A twenty-year archive produces a thousand good candidates. The first pass is
not about choosing; it's about finding one batch small enough to finish and
polished enough to prove the workflow. A finished pilot of 30 photos beats an
unfinished shortlist of 300.

**Pilot batch criteria (pick one):**

1. **One trip** (e.g., a specific holiday, a reunion, a road trip): bounded by
   dates, a clear narrative arc, a manageable count. A 5-day trip likely yields
   50–200 source photos; a polished chapter picks 15–25.
2. **One era** (e.g., a span of years when the same group of people were
   regularly together): more varied but still narratively unified.
3. **One recurring relationship** (e.g., the same two or three people across
   multiple years): a friendship or family thread that shows time passing.

Option 1 (a single trip) is the recommended first pilot: it has a hard start
and end, a clear setting, and a natural opener and closer.

## Narrative arc for a pilot chapter

A photo album chapter is not a timeline. It's a story. The structure:

1. **Opening image** — the one photo that makes someone say "I want to see more
   of this." Not necessarily the first chronological photo. Often a candid or a
   decisive moment of connection, not a group shot.
2. **Early pages — arrival and context** — where are we, who's here, what's the
   mood. Establishing shots are acceptable here but only as support.
3. **Middle — the moments** — the 8–12 photos that carry the actual story. Each
   has a reason to be here that is different from the others.
4. **Late — winding down** — the quieter end-of-trip photos. Laughter after
   exhaustion, the last meal, the airport goodbye, the drive home.
5. **Closing image** — the last photo a reader sees. It should land like an
   ending, not just stop.

## image-gen-2 role in a family photo album

image-gen-2 is a layout and polish tool, not a content creator. Specifically:

### What it's good for in this project:

- **Cover design** — generate layout comp candidates for the cover (title,
  typography, photo placement). Use source photos as reference; the generated
  output is a comp, not a final.
- **Restoration prompts** — old photos with color cast, scratches, or low
  resolution can be described to image-gen-2 for restoration concept comps.
  The original is always preserved; the generated version is a polish candidate.
- **Layout spread exploration** — given two or three photos and their rough
  positions, generate layout comp variants to choose from before committing
  to a layout tool.
- **Caption tone exploration** — not captioning itself (that requires knowing
  the people and the story) but drafting a few tone alternatives for a caption
  once the caption content is known: factual vs. warm, long vs. short.
- **Background and texture fills** — generating backgrounds for pages that
  carry only one photo or a title.

### What it is NOT for:

- **Generating people who aren't there.** No inpainting family members who
  didn't appear in a photo, no generating "what it would look like if."
- **Replacing a photo** that exists but is blurry or poorly composed.
  Keep the original; use image-gen-2 only for comps and presentation polish.
- **Producing captions or narrative.** The narrative must come from the person
  who was there. image-gen-2 can suggest tone, not facts.

## Pilot production sequence

1. **Select the pilot batch** — pick one trip (see criteria above). Target
   15–25 final photos from 50–200 source photos.
2. **Set the privacy boundary** — which photos include people who haven't
   consented to a shared album? Mark them as `consent-pending` or `excluded`.
   See `photo-album-private-media-pilot.md` for the full consent workflow.
3. **Build the source ledger** — a simple CSV: `filename, date, location,
   people, rights_status, notes`. One row per candidate photo.
4. **Sequence the 15–25 selects** — lay them out in order on a digital
   surface (Miro, Obsidian canvas, a folder with numbered prefixes). The order
   is the story arc: opening → context → moments → winding down → close.
5. **Draft captions** — one sentence per photo, from memory. This is the
   hardest step and must happen before any image-gen-2 work. The captions
   carry the story; the layouts serve the captions.
6. **Run image-gen-2 for cover comp** — describe the pilot's mood, palette,
   and dominant image to image-gen-2. Generate 3–5 cover layout comps. Pick
   the direction; don't finalize yet.
7. **Layout in a print-ready tool** — take the sequence and cover direction
   into a layout tool (Affinity Publisher, Canva Pro, InDesign). Set type
   scale, margins, and grid before placing photos.
8. **Proof review** — share a PDF proof with one trusted person from the pilot
   (someone who was there). Corrections before print order.
9. **Print one copy** — the pilot is proved when a physical copy exists.

## Pilot repo scaffold

When the pilot is ready for a repo:

```text
family-photo-album/
  README.md
  LICENSE
  source-ledger/
    originals.csv          (path, date, location, people, rights)
    pilot-batch-01/        (symlinks or notes to source locations — NOT copies)
  pilot-01-[trip-name]/
    sequence/
      01-opening.md        (selected photo ref + caption draft)
      02-...
      ...
      15-close.md
    comps/
      cover-comp-01.jpg    (image-gen-2 cover comp — derivative: true)
      cover-comp-02.jpg
      layout-spread-03.jpg (image-gen-2 layout comp — derivative: true)
    exports/
      proof-v1.pdf         (watermarked)
      final-v1.pdf         (after proof sign-off)
    docs/
      pilot-notes.md
      consent-log.md
```

## Success criteria for the pilot

- 15–25 photos sequenced with captions, proof-reviewed, and printed once.
- `source-ledger/originals.csv` complete for the pilot batch.
- At least one image-gen-2 cover comp in the comp folder with a `derivative:
  true` note.
- Proof reviewed by at least one person who was in the pilot.
- The workflow repeatable: a second chapter should take less time than the first.
