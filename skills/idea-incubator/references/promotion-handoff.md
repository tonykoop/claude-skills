# Promotion Handoff

Promotion means moving an incubated idea into a target repo, project board, or
specialist skill without losing the original issue trail.

## Handoff pattern

1. Restate the idea in one sentence.
2. Name the target repo or specialist skill.
3. Say what should exist when the handoff is done.
4. Link the source issue.
5. Include `closes #N` only when the downstream issue should close the source.

## Copy-pasteable handoff

```markdown
Promoting idea #<N> into <target>.

Source: #<N>
Summary: <one sentence>
Why now: <one sentence>
Related links: <issue links or URLs>

Requested output:
- <deliverable 1>
- <deliverable 2>

If the target work should close the source issue, use `closes #<N>` in the
downstream issue or PR body.
```

## Specialist pairings

- `maker-engineering` for fabrication and shop ideas.
- `instrument-maker` for instrument concepts and acoustics.
- `yoga-sequencer` for class and sequence ideas.
- `skills-meta` for skill ecosystem or routing ideas.

## Ownership note

Do not hard-code future repo ownership or visibility in the handoff. Keep the
target repo as an explicit input unless the user has already chosen it.

## Promotion-readiness matrix

Always run a readiness matrix before selecting which issue to promote. For
single-issue Promote, the matrix has one row plus its visible siblings. For
Promote-batch, the matrix covers the entire cluster. Treat any "already
satisfied" or "blocked" row as a `close` or `defer` candidate, not a promote.

```markdown
| Issue | State | Evidence | Blockers | Best next route | Decision |
|---|---|---|---|---|---|
| #N | capture / promote / ready-now | paths, files, repo state | owner decision, missing assets, IP / provenance risk | specialist skill or repo | promote / defer / close / comment |
```

A complete row names a concrete artifact under "Evidence" (a path that
exists, a CSV, a confirmed repo absence). Rows whose evidence is hand-wavy
("looks promising") are not ready to promote yet — push them back to the
Connect or Review modes.

## Binary-asset / Git LFS prompts

Run these prompts whenever the capture mentions CAD, photos, video, audio,
ZIPs, PDFs, or any asset likely to exceed 100 MB (GitHub's per-file hard
limit). The order matters: LFS rules MUST be committed before the first
large file lands, or the import has to be rewritten with `git lfs migrate`.

For private media, family archives, photo albums, scanned documents, and
personal video, run this section plus the privacy-first checklist in
[`private-media-family-archive.md`](private-media-family-archive.md) before
drafting the downstream issue. Those promotions default to a private repo,
one curated pilot batch, explicit reviewer/consent boundaries, EXIF/GPS
strip-or-quarantine handling, and `Refs #N` until the scaffold and ledgers
exist.

For yearbooks, design books, cohort books, school archives, team/class books,
or private print-book rollouts, also run
[`yearbook-design-book-rollout.md`](yearbook-design-book-rollout.md). Those
promotions require a named pilot edition, people/consent gate, proof-review
owner, source/evidence ledger, image-gen derivative labels, and reviewed
export path before any public sharing or print/vendor package.

For photo-album or private-media pilot work, also use
[`photo-album-private-media-pilot.md`](photo-album-private-media-pilot.md) to
lock the source-photo policy before any media import or imagegen concept work.

1. Does the target repo already exist? If yes, does it have `.gitattributes`
   with LFS rules covering the expected extensions?
2. Are large files staged already, or do they still need copying from a
   source path (D:\, an external drive, a mounted archive)?
3. Does Git LFS need to be installed and tracked before the first import
   commit? Default extensions for SolidWorks/CAD work:
   `*.sldprt *.sldasm *.eprt *.stl *.step *.stp`. Add audio/video/ZIP/PDF
   extensions as needed.
4. What source-of-truth provenance file should be cited (an inventory CSV,
   a backup manifest, a vendor receipt)? Link it from the new repo's README.
5. Should the source issue use `Refs #N` or `Closes #N`? For recovery/import
   work the default is `Refs` — keep the source open as a provenance anchor
   until the evidence ledger lands.

If any binary-asset prompt is "unknown", surface it in the handoff as an
explicit unknown rather than picking a default silently.

### LFS-first scaffold sequence

```bash
gh repo create owner/repo --private --clone
cd repo
git lfs install --local
git lfs track "*.sldprt" "*.sldasm" "*.eprt" "*.stl" "*.step" "*.stp"
git add .gitattributes
git commit -m "chore: LFS tracking before any large file"
# only NOW copy large files into cad/, then commit as a separate import.
```

## Evidence ledger (recovery / import promotions)

When a capture's source artifacts already exist offline (D:\ archive, a
vendor zip, a defunct service export), the target repo gets an
`docs/evidence-ledger.md` whose job is to separate archive facts from
inferred claims. This is the firewall that prevents speculative wording
from leaking into a public README.

```markdown
# Evidence Ledger

| File | Size (MB) | Modified | Type | Source path | Observed | Inferred |
|------|-----------|----------|------|-------------|----------|----------|
| ... | ... | ... | ... | ... | "filename present in archive at <path>" | "purpose: <best guess, marked PROVISIONAL>" |
```

Public-facing README copy MAY repeat anything in the "Observed" column
verbatim. It MUST mark anything from the "Inferred" column as
PROVISIONAL until reviewed.

## Refs vs Closes (provenance anchors)

| Situation | Use |
|---|---|
| Downstream work fully delivers the captured idea, no provenance to preserve. | `Closes #N` |
| Source capture should remain open until evidence ledger / scaffold review lands. | `Refs #N` |
| Recovery / legacy-import / archive-pull promotion. | `Refs #N` (default) |
| Source capture is itself a tracking issue that the user wants to keep open. | `Refs #N` |

Default to `Refs` whenever a recovery cluster is involved.

## Private media / family archive promotions

Use [`private-media-family-archive.md`](private-media-family-archive.md) when
a capture proposes photo albums, family archives, scanned documents, personal
video, memorial/family-history projects, or image-gen assisted private album
work. The downstream handoff must protect privacy and provenance before it
optimizes for visual polish:

- private repo by default;
- one curated pilot batch, not a full archive import;
- `.gitattributes` / Git LFS rules before media import;
- privacy boundary and reviewer/consent plan before publishing or sharing;
- EXIF/GPS strip-or-quarantine policy for derived review artifacts;
- source/evidence ledger that separates observed archive facts from captions,
  memories, and inferred story claims.
- source-photo rules that keep originals external by default, require LFS
  before selected original imports, and keep shareable exports derivative-only.

## Yearbook / design-book rollout promotions

Use [`yearbook-design-book-rollout.md`](yearbook-design-book-rollout.md) when
a capture proposes a yearbook, design book, cohort book, school archive,
class/team book, workshop book, or print-on-demand rollout involving private
media or identifiable people. The downstream handoff must add rollout-specific
gates on top of the private-media baseline:

- private repo by default until the privacy boundary permits otherwise;
- one named pilot edition, cohort, class, event, chapter, or sample section;
- consent/off-limits handling for minors, names, faces, schools/teams, homes,
  events, locations, and sensitive dates;
- privacy reviewer plus proof reviewer before export or print sharing;
- source/evidence ledger for images, scans, captions, rosters, credits, and
  inferred story claims;
- image-gen, restoration, collage, and layout outputs labeled as derivatives,
  not documentary originals;
- watermarked proof artifacts and signoff log before print/vendor/export
  packages.
