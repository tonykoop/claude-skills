# Family Photo Album — Repo Scaffold and LFS Plan

Issue: https://github.com/tonykoop/claude-skills/issues/101

Repo structure, Git LFS plan, and promotion readiness checklist for the
family-and-friends photo album project. The issue names the repo shape clearly;
this doc fleshes it out and adds the Git configuration that must precede any
photo import.

For the editorial pilot plan (pilot batch selection, narrative arc, image-gen-2
role): see `docs/image-gen-2/family-photo-album-pilot-plan.md` (Refs #93)

For the privacy/consent workflow: see
`plugins/maker/skills/idea-incubator/references/photo-album-private-media-pilot.md`

## Promotion readiness gates (before creating the repo)

Per idea-incubator promote mode:

- [ ] Tony has chosen the initial photo folder (one trip, one era, or one
  relationship — see pilot plan).
- [ ] Privacy boundary stated: which people in the source photos require consent
  before any export/sharing? Name them or define the rule.
- [ ] Print target confirmed: home printer, online print lab (WHCC, Artifact
  Uprising, Minted), or physical booklet service (Blurb, Mixbook)?
- [ ] Source-photo policy chosen: `external-ledger-only` (photos stay on disk,
  repo holds only metadata + derived assets) OR `lfs-original` (selected
  originals imported with Git LFS).
- [ ] Git LFS confirmed available in the target environment.

## Repo scaffold

```text
family-photo-album/            (private)
  README.md
  .gitattributes               (LFS tracking — commit before any photo import)
  .gitignore
  source-ledger/
    originals.csv              (path|date|location|people|rights|notes)
    consent-log.md             (who consented to what, when)
  chapters/
    pilot-01-[trip-or-era]/
      sequence.md              (ordered photo list + caption drafts)
      selects/                 (symlinks or LFS-tracked originals)
      comps/                   (image-gen-2 comps — all derivative: true)
      prompts/
        cover-prompt.md
        spread-03-prompt.md
      reviews/
        proof-v1.pdf           (watermarked — for review only)
        proof-v1-signoff.md    (who reviewed, what was approved)
      exports/
        final-v1.pdf           (after signoff)
  prompts/                     (reusable prompts across chapters)
    style-guide.md             (album visual language — type, palette, grid)
    restoration-template.md    (restoration prompt structure)
    cover-template.md          (cover prompt structure)
  docs/
    album-concept.md           (what this album is, who it's for, tone)
    privacy-rules.md           (project-level privacy boundary)
    lfs-guide.md               (how to work with photos in this repo)
    recovery-log.md            (how source material entered the project)
```

## Git LFS configuration

Commit `.gitattributes` before copying any photos:

```gitattributes
# Git LFS tracking for all photo/image/export types
*.jpg  filter=lfs diff=lfs merge=lfs -text
*.JPG  filter=lfs diff=lfs merge=lfs -text
*.jpeg filter=lfs diff=lfs merge=lfs -text
*.JPEG filter=lfs diff=lfs merge=lfs -text
*.tif  filter=lfs diff=lfs merge=lfs -text
*.TIF  filter=lfs diff=lfs merge=lfs -text
*.tiff filter=lfs diff=lfs merge=lfs -text
*.TIFF filter=lfs diff=lfs merge=lfs -text
*.png  filter=lfs diff=lfs merge=lfs -text
*.PNG  filter=lfs diff=lfs merge=lfs -text
*.psd  filter=lfs diff=lfs merge=lfs -text
*.PSD  filter=lfs diff=lfs merge=lfs -text
*.pdf  filter=lfs diff=lfs merge=lfs -text
*.PDF  filter=lfs diff=lfs merge=lfs -text
*.heic filter=lfs diff=lfs merge=lfs -text
*.HEIC filter=lfs diff=lfs merge=lfs -text
*.mp4  filter=lfs diff=lfs merge=lfs -text
*.MP4  filter=lfs diff=lfs merge=lfs -text
*.mov  filter=lfs diff=lfs merge=lfs -text
*.MOV  filter=lfs diff=lfs merge=lfs -text
```

Also commit `.gitignore` before importing:

```gitignore
# Never commit proof watermarks outside the reviews/ folder
exports/**/watermarked-*
# Mac metadata
.DS_Store
# RAW camera files (use external ledger, not LFS, for large RAW archives)
*.raw *.RAW *.cr2 *.CR2 *.nef *.NEF *.arw *.ARW
```

## source-ledger/originals.csv schema

```csv
path,filename,date,location,people,rights,import_state,notes
/path/to/external/archive/trip-01/IMG_0001.jpg,IMG_0001.jpg,2018-07-14,Portland OR,Alice,consent-confirmed,ledger-only,
/path/to/external/archive/trip-01/IMG_0042.jpg,IMG_0042.jpg,2018-07-15,Portland OR,Bob|Alice,consent-pending,excluded,
```

Field rules:
- `path` — absolute path to source on external disk (not a repo path)
- `people` — pipe-separated names; use first name or initials if preferred
- `rights` — `consent-confirmed`, `consent-pending`, `excluded`, `public`
- `import_state` — `ledger-only` (path only, no LFS import), `lfs-imported`
  (selected original brought into repo with LFS), `excluded` (not imported,
  not in ledger)

## Prompt organization

Each chapter's `prompts/` sub-folder holds one Markdown file per image-gen-2
call, named by the spread or asset it targets:

```text
chapters/pilot-01/prompts/
  cover-v1.md          (cover comp prompt)
  spread-03-v1.md      (mid-chapter spread layout prompt)
  restoration-01-v1.md (restoration comp prompt for a specific source photo)
```

Each prompt file:

```markdown
# Prompt: [asset name]

**Asset:** `comps/cover-v1.jpg`
**Purpose:** cover comp for the Portland 2018 chapter
**Kind:** cover (derivative: true)
**Prompt:**

[exact text sent to image-gen-2]

**Notes:** generated from this prompt on 2026-06-19; used as the basis for the
final cover layout.
```

## Repo creation sequence

1. Create private repo `tonykoop/family-photo-album`.
2. Initialize with README (album concept, audience, privacy rules, print target).
3. Commit `.gitattributes` and `.gitignore` first — before any photo import.
4. Run `git lfs install` and push LFS config.
5. Create `source-ledger/originals.csv` with the pilot batch rows (paths only;
   `import_state: ledger-only` for all unless explicitly importing originals).
6. Create `chapters/pilot-01-[name]/` with the sequence and prompts structure.
7. Run image-gen-2 for cover comp; commit result to `comps/` with `derivative:
   true` noted in the file or a sidecar.
8. Import selects via LFS only after `originals.csv` is complete and consent
   is confirmed for each selected photo.
9. Generate proof PDF; commit to `reviews/` with watermark.
10. Proof review sign-off → final export → `exports/`.
