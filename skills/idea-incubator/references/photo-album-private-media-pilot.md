# Photo Album Private Media Pilot Workflow

Use this workflow when an idea asks to turn private photos, scanned albums,
phone videos, family archive folders, or personal media exports into an album,
story collection, print proof, or imagegen-assisted layout study.

The goal is a small repo-ready pilot that protects source photos, consent
boundaries, and proof-review integrity before any visual polish, broad import,
vendor upload, or public-facing storytelling.

## Routing Rule

Route here when the capture includes any of these signals:

- photo album, family album, memorial book, family archive, scanned album,
  private media, phone camera roll, home video, or personal video;
- imagegen used for album covers, layouts, restoration studies, collage ideas,
  caption tone, or proof review;
- a folder/export/archive that may include identifiable people, homes, schools,
  events, locations, minors, or sensitive dates.

If the user only wants a generic public design asset and no private source
media is involved, use the normal `imagegen` skill instead.

## Pilot-First Steps

1. Pick exactly one pilot batch: one album, folder, event, date range, export,
   or scanned envelope.
2. Draft the downstream issue with `Refs #N`, not `Closes #N`, until the
   scaffold, privacy boundary, source ledger, and evidence ledger exist.
3. Default the target repo to private, or write the repo visibility as an
   explicit blocker if the user has not chosen it.
4. Decide the source-photo policy before import: `external-ledger-only`,
   `lfs-original`, `derived-only`, or `exclude`.
5. Commit `.gitattributes` and `.gitignore` before copying photos, scans,
   video, PDFs, ZIPs, or print assets into the repo.
6. Create review-safe derivatives only after privacy, metadata, consent, and
   reviewer rules are recorded.
7. Require watermarked review proofs and a signoff log before any
   print/vendor/export package.

## Source-Photo Rules

- Treat original photos, scans, and videos as source evidence, not design
  material to be overwritten.
- Keep originals outside the repo by default and cite them in
  `source-ledger/originals.csv`.
- If selected originals must enter the repo, import them only after Git LFS
  tracking is committed and the batch is named.
- Never put private originals in `exports/`, public README examples, issue
  screenshots, or generated documentation.
- Use derivative filenames that preserve traceability, such as
  `<source_id>-review.jpg` or `<source_id>-layout-study.png`.
- Store captions, memories, identifications, and inferred stories separately
  from observed source facts.

## LFS And Ignore Baseline

Before any media import, the downstream repo should commit `.gitattributes`
for the expected binary extensions. Start from the media list in
[`private-media-family-archive.md`](private-media-family-archive.md), then add
project-specific formats such as `.psd`, `.afphoto`, `.indd`, or vendor proof
packages when needed.

Use `.gitignore` to block accidental local imports before review:

```gitignore
incoming/
raw-import/
staging/
private-originals/
```

Do not use broad ignore rules to hide unknown media already inside the repo.
Record those files in the source ledger and decide whether to import, derive,
or exclude them.

## Privacy And Metadata Gates

The downstream issue must name or explicitly mark unknown:

- privacy/family reviewer;
- off-limits people, faces, minors, events, locations, schools, homes,
  addresses, date ranges, and sensitive documents;
- allowed collaborators and export/share destinations;
- EXIF/GPS policy: `strip-derived`, `quarantine-originals`, or
  `preserve-private`;
- proof-review owner before any vendor upload, family share, or public preview.

If any gate is unknown, keep it in the handoff as a blocker. Do not fill the
gap with a shareable-by-default assumption.

## Imagegen Boundary

Imagegen may support:

- layout concepts;
- cover explorations;
- restoration studies;
- collage composition;
- caption tone examples;
- proof-review prompts.

Imagegen must not replace source photos, invent documentary scenes, identify
people, rewrite family history, or remove privacy review. Label generated or
heavily transformed outputs as `not a documentary original`.

Prompts and prompt logs should avoid full names, addresses, school names,
exact locations, sensitive dates, and faces that are not cleared by the
privacy boundary.

## Proof And Export Gate

- Create watermarked review proofs before any print-ready or vendor-ready
  export.
- Keep proof artifacts in a review-only location until privacy and proof
  reviewers sign off.
- Record signoff in `reviews/proof-signoff.md`, including reviewer, date,
  batch, export target, and unresolved blockers.
- Do not upload to a vendor, share a family preview, or publish a public
  sample until the signoff log confirms that off-limits people, faces, places,
  dates, captions, and metadata have been reviewed.

## Copy-Pasteable Pilot Handoff

```markdown
Refs #<source-issue>

## Summary

Create a private photo-album / private-media pilot repo for one named batch,
with source-photo rules, Git LFS tracking, privacy review, metadata handling,
and imagegen derivative boundaries before any broad archive import.

## Pilot batch

- Batch: <one album/folder/event/date range/export>
- Source location: <external path, drive, cloud export, or unknown>
- Source-photo policy: external-ledger-only / lfs-original / derived-only / exclude

## Privacy boundary

- Repo visibility: private
- Reviewer: <name or unknown>
- Proof reviewer: <name or unknown>
- Off-limits: <people/faces/minors/schools/homes/events/locations/date ranges or unknown>
- Sharing/export rule: <private proof only / family review / vendor print / unknown>
- EXIF/GPS rule: strip-derived / quarantine-originals / preserve-private

## Requested output

- `.gitattributes` with LFS rules before media import.
- `.gitignore` blocking accidental raw imports.
- `source-ledger/originals.csv` for source-photo facts and import decisions.
- `docs/evidence-ledger.md` separating observed facts from captions,
  memories, and inferred story claims.
- `docs/privacy-boundary.md` and `reviews/privacy-review.md`.
- `reviews/proof-signoff.md` for watermarked proof review before export.
- `derived/` and `exports/` rules that keep originals out of shareable output.
- Imagegen prompts labeled as layout/restoration/collage concepts, never
  documentary originals.

## Acceptance criteria

- No source photos, scans, videos, PDFs, ZIPs, or print assets are imported
  before LFS tracking and the privacy boundary are committed.
- The pilot uses one named batch, not an open-ended archive dump.
- Review/export copies strip or quarantine sensitive metadata according to the
  chosen policy.
- Watermarked proofs and signoff are complete before vendor upload, public
  preview, or family-share export.
- Generated or restored outputs remain traceable derivatives of source IDs.
- The source issue remains open as a provenance anchor until scaffold and
  ledgers are reviewed.
```
