# Yearbook And Design-Book Rollout Promotion

Use this reference when promoting ideas about yearbooks, design books, cohort
books, school archives, class books, team books, workshop books, private
print-on-demand books, or public/private media rollouts that include
identifiable people, private source images, scans, names, schools, homes,
events, or location history.

The promotion goal is a downstream rollout issue that protects people,
source provenance, and proof-review integrity before layout polish, print
automation, or image-gen exploration.

## Default Posture

- Private repo by default until the privacy boundary explicitly permits public
  source or public exports.
- Start with one pilot edition, cohort, event, class, chapter, or sample
  section before a full archive or full-school rollout.
- Name a privacy reviewer and proof reviewer before export or print sharing.
- Keep originals external with source-ledger references unless LFS-backed
  import is explicitly chosen.
- Treat generated covers, layout studies, collage concepts, restorations, and
  mockups as derivatives, not source evidence.
- Use `Refs #N` for the source idea until the scaffold, privacy boundary,
  source ledger, and proof workflow exist.

## Rollout-Readiness Gates

Add these checks to the standard Promote readiness matrix:

| Gate | Ready signal | Blocker signal |
|---|---|---|
| Edition scope | One named year, cohort, event, class, chapter, or sample section | "All years", "all students", or unbounded archive import |
| Visibility | Private repo or explicitly private placeholder chosen | Public repo/default visibility unresolved |
| People boundary | Minors, staff, families, alumni, or guests are named as categories, not exposed individually | Full names/faces/locations assumed shareable |
| Consent/off-limits | Off-limits people, events, locations, and date ranges listed or explicitly unknown | No consent review owner |
| Reviewer path | Privacy reviewer and proof reviewer named | Nobody owns final approval before print/share |
| Source policy | External originals or LFS-original import decided before copy | Raw media copied before LFS and privacy policy |
| Metadata policy | EXIF/GPS strip-or-quarantine rule chosen | Review copies keep location metadata by accident |
| Provenance | Source/evidence ledgers planned for images, captions, rosters, credits, and inferred story claims | Captions, names, or memories treated as verified facts |
| Image-gen boundary | Generated/restored/layout assets labeled as derivatives | Generated image treated as a documentary original |
| Proof/export gate | Watermarked review proof and signoff path defined before vendor/export package | Print-ready export created before privacy/proof review |

If any privacy, consent, provenance, or proof-review gate is unknown, surface
it as a blocker in the handoff instead of silently choosing a public rollout
or shareable-by-default path.

## Required Handoff Sections

For yearbook/design-book rollout promotions, include these sections in the
downstream issue:

1. **Privacy boundary** - repo visibility, collaborators, reviewers,
   off-limits categories, and export/sharing rules.
2. **Pilot edition** - the one year, cohort, event, chapter, class, or sample
   section to process first.
3. **People and consent gate** - how minors, names, faces, school/team names,
   homes, addresses, and sensitive dates are reviewed before publication.
4. **Source policy** - whether originals stay external with ledger references
   or are imported with Git LFS after `.gitattributes` exists. Record the
   decision as `external-ledger-only`, `lfs-original`, `derived-only`, or
   `exclude`.
5. **Metadata policy** - strip EXIF/GPS from derived proofs and exports by
   default, or quarantine originals that must preserve metadata.
6. **Evidence/source ledger** - separate observed file facts from captions,
   rosters, memories, identifications, credits, and inferred story claims.
7. **Editorial and layout style** - naming conventions, caption tone, credit
   policy, restoration limits, image-gen boundaries, and proof-review steps.
8. **Proof/export workflow** - watermarked review proofs first, signoff log,
   then print/vendor/export package only after review.

## Repo Scaffold Hints

Use this shape as the starting point for a private yearbook/design-book repo:

```text
yearbook-or-design-book/
  README.md
  .gitignore
  .gitattributes
  docs/
    privacy-boundary.md
    editorial-style.md
    evidence-ledger.md
    proof-workflow.md
    export-rules.md
  source-ledger/
    README.md
    originals.csv
    roster-sources.md
    import-batches.md
    selection-decisions.md
  editions/
    00-template/
    01-pilot/
  spreads/
    00-template/
    01-pilot/
  prompts/
    cover/
    layout/
    restoration/
    collage/
    caption-tone/
    proof-review/
  reviews/
    privacy-review.md
    consent-log.md
    proofing-notes.md
    signoff-log.md
  derived/
    README.md
  exports/
    README.md
```

Keep raw imports out of `exports/`. Use `derived/` for watermarked proofs,
contact sheets, restoration studies, layout concepts, and image-gen studies.
Use `exports/` only for reviewed print/vendor/share packages.

## Source Media Policy

Choose one source-media policy for the pilot before copying photos, scans,
videos, PDFs, ZIPs, design files, or print assets into the downstream repo:

- `external-ledger-only` - originals stay outside the repo and are cited in
  `source-ledger/originals.csv`.
- `lfs-original` - selected originals may enter the repo only after
  `.gitattributes` and Git LFS tracking are committed.
- `derived-only` - only watermarked proofs, contact sheets, restoration
  studies, layout studies, or other derivatives enter the repo.
- `exclude` - source media is intentionally left out because it is off-limits,
  lacks consent, has sensitive metadata, or is not needed for the pilot.

Never place private originals in `exports/`, public README examples, issue
screenshots, or generated documentation. Derivative filenames should preserve
traceability to source IDs, such as `<source_id>-proof.jpg` or
`<source_id>-layout-study.png`.

## Evidence Ledger Template

`docs/evidence-ledger.md` should keep source facts separate from editorial
claims:

```markdown
# Evidence Ledger

| Source ID | Observed file fact | Roster / caption / memory | Inferred story claim | Privacy status | Reviewer | Status |
|---|---|---|---|---|---|---|
| pilot-img001 | Filename, folder, visible scene, file date | Who/what a reviewer remembers | PROVISIONAL interpretation | unreviewed / private / shareable / exclude | reviewer name | unreviewed / accepted / disputed |
```

Public captions, credits, and layouts may use accepted observed facts and
reviewed memories. Inferred story claims stay marked `PROVISIONAL` until a
reviewer accepts them.

## Image-Gen And Restoration Boundary

Image generation may support cover studies, layout thumbnails, collage
composition, restoration mockups, caption-tone prompts, and proof-review
checklists. It must not replace the source ledger, invent identities, rewrite
school/family history, or stand in for release/consent review.

Required labels for generated or heavily transformed outputs:

- `cover concept`
- `layout concept`
- `collage concept`
- `restoration study`
- `not a documentary original`

Avoid prompts that include full names, home addresses, school names, exact
locations, sensitive dates, or uncleared faces. When a real source image is
used only as inspiration, say so in the prompt log and ledger; do not imply the
generated output is an archival photograph.

## Copy-Pasteable Downstream Issue

```markdown
Refs #<source-issue>

## Summary

Create a private yearbook/design-book rollout scaffold for one pilot edition,
with privacy boundaries, consent/proof gates, source/evidence ledgers, Git LFS
tracking, and review-safe derived outputs before any broad media import,
print export, or public sharing.

## Requested output

- Private repo scaffold with `docs/privacy-boundary.md`,
  `docs/editorial-style.md`, `docs/evidence-ledger.md`,
  `docs/proof-workflow.md`, `source-ledger/`, `editions/`, `spreads/`,
  `derived/`, `exports/`, and review logs.
- `.gitattributes` with Git LFS rules for photos, scans, video, PDFs, ZIPs,
  design files, and print assets before media import.
- `.gitignore` to prevent accidental raw imports.
- One named pilot edition, cohort, class, event, chapter, or sample section.
- Source-media policy: external-ledger-only / lfs-original / derived-only /
  exclude.
- Consent/off-limits checklist for people, schools/teams, events, locations,
  and sensitive dates.
- EXIF/GPS strip-or-quarantine policy for derived proofs and exports.
- Source/evidence ledger that separates observed source facts from captions,
  rosters, memories, credits, and inferred story claims.
- Image-gen/restoration prompt boundaries that label generated outputs as
  derivatives, not documentary originals.
- Proof workflow that requires watermarked review artifacts and signoff before
  print/vendor/export packages.

## Acceptance criteria

- No full archive, all-year, all-student, or public rollout happens before the
  pilot edition is reviewed.
- Privacy boundary, reviewer/consent rules, and off-limits categories exist
  before sharing, export, or print.
- Source and evidence ledgers distinguish observed file facts from captions,
  rosters, memories, credits, and inferred story claims.
- Large media import is blocked until LFS tracking is committed.
- Pilot source media uses an explicit policy: external-ledger-only,
  lfs-original, derived-only, or exclude.
- Derived proofs and exports strip or quarantine sensitive metadata.
- Generated/restored/layout assets are labeled as derivatives and never treated
  as documentary originals.
- Source issue remains open as a provenance anchor.
```

## Questions To Surface

Ask or record these as explicit blockers when the answer is unknown:

- What is the private repo name and owner?
- Which one edition, cohort, class, event, chapter, or section is the pilot?
- Who owns privacy review and final proof signoff?
- Which people, schools/teams, homes, events, locations, or date ranges are
  off limits?
- Are minors or other consent-sensitive people included?
- Do originals stay external, or are selected originals imported with LFS?
- Should derived proofs/exports strip EXIF/GPS, quarantine sensitive
  originals, or preserve metadata only in private?
- What print or export target matters first?
- What level of image-gen cover/layout/restoration intervention is acceptable?
