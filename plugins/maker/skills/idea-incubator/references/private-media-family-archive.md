# Private Media And Family Archive Promotion

Use this reference when promoting ideas about photo albums, family archives,
scanned documents, personal video, memorial projects, private image-gen album
work, or any media collection involving identifiable people, homes, schools,
events, locations, or family history.

For yearbooks, design books, cohort books, school archives, team/class books,
or print-book rollouts, use this privacy-first baseline plus the rollout gates
in [`yearbook-design-book-rollout.md`](yearbook-design-book-rollout.md).

The promotion goal is a repo-ready downstream issue that protects privacy and
provenance before it optimizes for visual polish.

## Default Posture

- Create a private repo by default.
- Start with one curated pilot batch, not a full archive import.
- Commit Git LFS tracking and `.gitignore` rules before any media import.
- Keep originals external with source-ledger references unless the owner
  explicitly chooses LFS-backed original import.
- For photo-album or private-media pilot requests, run
  [`photo-album-private-media-pilot.md`](photo-album-private-media-pilot.md)
  before drafting downstream repo work.
- Treat image-gen outputs, restorations, collages, and print layouts as
  derivatives, not documentary originals.
- Require watermarked review proofs and proof-review signoff before vendor
  upload, family sharing, public preview, or print-ready export.
- Use `Refs #N` for the source issue until the scaffold, privacy boundary, and
  ledgers exist.

## Promotion-Readiness Matrix Additions

Add these checks to the standard Promote readiness matrix:

| Check | Ready signal | Defer signal |
|---|---|---|
| Pilot scope | One named album/export/folder or date/event batch | "All family photos" or open-ended archive dump |
| Repo visibility | Private repo chosen or placeholder explicitly private | Public/default visibility unresolved |
| Reviewer boundary | Privacy reviewer, family reviewer, and proof reviewer named where relevant | No human review owner |
| Consent/off-limits | Off-limits people, faces, minors, events, schools, homes, locations, and date ranges listed or explicitly unknown | Assumes all media is shareable |
| Originals policy | LFS import vs external originals decided | Original media copied before policy exists |
| Metadata policy | EXIF/GPS strip-or-quarantine rule chosen | Derived review copies preserve location metadata by accident |
| Provenance | Source ledger and evidence ledger planned | Captions or memories are treated as archive facts |

If any privacy or provenance check is unknown, surface it as a blocker in the
handoff instead of silently choosing a public, full-import, or shareable-by-
default path.

## Required Handoff Sections

For private-media promotions, include these sections in the downstream issue:

1. **Privacy boundary** - repo visibility, allowed collaborators, reviewer,
   off-limits people/events/locations, and sharing/export rules.
2. **Pilot batch** - the one folder, album, event, date range, or export to
   process first.
3. **Source policy** - whether originals stay external with ledger references
   or are imported into Git LFS.
4. **Metadata policy** - strip EXIF/GPS from derived review/export artifacts by
   default, or quarantine originals that must preserve metadata.
5. **Evidence/source ledger** - separate observed file facts from captions,
   memories, identifications, and inferred story claims.
6. **Editorial style** - caption tone, naming conventions, restoration limits,
   image-gen boundaries, and proof-review steps.
7. **LFS-first import** - `.gitattributes` committed before any heavy binary
   files land.
8. **Source-photo rules** - originals stay external by default, imported
   originals require LFS first, and derivatives remain traceable to source IDs.
9. **Proof/export gate** - watermarked review proofs and signoff log before
   print/vendor/export packages.

## Repo Scaffold Hints

Use this shape as the starting point for a private family archive or photo
album repo:

```text
family-archive-or-photo-album/
  README.md
  .gitignore
  .gitattributes
  docs/
    privacy-boundary.md
    editorial-style.md
    evidence-ledger.md
  source-ledger/
    README.md
    originals.csv
    import-batches.md
    selection-decisions.md
  chapters/
    00-template/
    01-pilot/
  spreads/
    00-template/
  print-proof/
    README.md
  prompts/
    layout/
    restoration/
    collage/
    cover/
    caption-tone/
    proof-review/
  reviews/
    privacy-review.md
    family-review-log.md
    proofing-notes.md
    proof-signoff.md
  derived/
    README.md
  exports/
    README.md
```

Use `source-ledger/` for source facts and import decisions. Use `derived/` for
working derivatives, contact sheets, watermarked review copies, restorations,
or image-gen studies. Use `exports/` for print/vendor packages and shareable
deliverables. Do not place private originals in `exports/`.

## LFS Defaults

For media-heavy archives, recommend this `.gitattributes` baseline before the
first media import:

```gitattributes
*.jpg filter=lfs diff=lfs merge=lfs -text
*.jpeg filter=lfs diff=lfs merge=lfs -text
*.png filter=lfs diff=lfs merge=lfs -text
*.tif filter=lfs diff=lfs merge=lfs -text
*.tiff filter=lfs diff=lfs merge=lfs -text
*.heic filter=lfs diff=lfs merge=lfs -text
*.webp filter=lfs diff=lfs merge=lfs -text
*.pdf filter=lfs diff=lfs merge=lfs -text
*.mov filter=lfs diff=lfs merge=lfs -text
*.mp4 filter=lfs diff=lfs merge=lfs -text
*.m4v filter=lfs diff=lfs merge=lfs -text
*.avi filter=lfs diff=lfs merge=lfs -text
*.zip filter=lfs diff=lfs merge=lfs -text
```

Keep Markdown, CSV, JSON, small scripts, prompt text, and ledger files in
normal Git.

## `.gitignore` Defaults

Use `.gitignore` to prevent accidental imports before the privacy boundary and
LFS rules are committed:

```gitignore
# unreviewed local imports
incoming/
raw-import/
staging/

# OS/app noise
.DS_Store
Thumbs.db

# local proof exports
*.tmp
*.bak
```

If originals remain external, keep the source path in `source-ledger/` rather
than adding a broad ignore rule that hides unreviewed media sitting inside the
repo.

## Source Ledger Template

`source-ledger/originals.csv` should start with:

```csv
source_id,batch_id,original_path_or_archive,file_name,media_type,approx_date,people,status,privacy_notes,import_decision
```

Suggested status values:

- `unreviewed`
- `allowed-private`
- `allowed-shareable`
- `needs-consent`
- `exclude`
- `unknown`

Suggested import decisions:

- `external-ledger-only`
- `lfs-original`
- `derived-only`
- `exclude`

## Evidence Ledger Template

`docs/evidence-ledger.md` should distinguish observed facts from human memory
and inferred story:

```markdown
# Evidence Ledger

| Source ID | Observed file fact | Caption / memory | Inferred story claim | Reviewer | Status |
|---|---|---|---|---|---|
| batch01-img001 | Filename, date, folder, visible scene | Who/what a reviewer remembers | PROVISIONAL interpretation | reviewer name | unreviewed / accepted / disputed |
```

Public or family-facing captions may use accepted observed facts and reviewed
memories. Inferred story claims stay marked `PROVISIONAL` until a reviewer
accepts them.

## EXIF/GPS Handling

Default rule: strip EXIF/GPS from derived review artifacts and exports unless
the privacy boundary explicitly says location metadata is safe to preserve.

Use one of these outcomes in the handoff:

- `strip-derived` - originals may retain metadata, but review/export copies
  are stripped.
- `quarantine-originals` - originals with sensitive metadata stay outside the
  repo or in a restricted folder until reviewed.
- `preserve-private` - metadata is preserved only in a private repo and never
  in exports.

Do not publish or share review copies with GPS metadata by accident.

## Image-Gen And Restoration Boundary

Image-gen tools may help with layout studies, cover exploration, restoration
mockups, collage composition, caption tone, and proof-review prompts. They must
not rewrite family history.

Required labels:

- `restoration study` for cleanup/colorization suggestions.
- `layout concept` for spread/composition studies.
- `collage concept` for generated montage ideas.
- `not a documentary original` for any generated or heavily transformed image.

Avoid prompts that include full names, home addresses, school names, exact
locations, sensitive dates, or faces of people who have not been cleared by the
privacy boundary.

## Copy-Pasteable Downstream Issue

```markdown
Refs #<source-issue>

## Summary

Create a private family media archive scaffold for one curated pilot batch,
with privacy boundaries, source/evidence ledgers, Git LFS tracking, and
review-safe derived outputs before any broad media import.

## Requested output

- Private repo scaffold with `docs/privacy-boundary.md`,
  `docs/editorial-style.md`, `docs/evidence-ledger.md`, `source-ledger/`,
  `spreads/`, `print-proof/`, `derived/`, and `exports/`.
- `.gitattributes` with Git LFS rules for photos, scans, video, PDFs, ZIPs,
  and print assets before media import.
- `.gitignore` to prevent accidental raw imports.
- One named pilot batch and import decision: external-ledger-only,
  LFS-original, derived-only, or exclude.
- EXIF/GPS strip-or-quarantine policy for derived review artifacts.
- Reviewer/consent checklist and off-limits people/events/locations.
- Watermarked review proofs and `reviews/proof-signoff.md` before print,
  vendor, public-preview, or family-share exports.
- Image-gen/restoration prompt boundaries that label generated outputs as
  derivatives, not documentary originals.

## Acceptance criteria

- No full archive import happens before the pilot batch is reviewed.
- Privacy boundary and reviewer/consent rules exist before sharing/export.
- Source and evidence ledgers distinguish observed file facts from captions,
  memories, and inferred story claims.
- Large media import is blocked until LFS tracking is committed.
- Proof signoff exists before vendor upload, print-ready export, public
  preview, or family sharing.
- Source issue remains open as a provenance anchor.
```

## Questions To Surface

Ask or record these as explicit blockers when the answer is unknown:

- What is the private repo name and owner?
- Which one batch is the pilot?
- Who is the privacy/family reviewer?
- Which people, events, locations, or date ranges are off limits?
- Do originals stay external, or are selected originals imported with LFS?
- Should derived exports strip EXIF/GPS, quarantine sensitive originals, or
  preserve metadata only in private?
- What print target or proof format matters first?
- What level of image-gen restoration or layout intervention is acceptable?
