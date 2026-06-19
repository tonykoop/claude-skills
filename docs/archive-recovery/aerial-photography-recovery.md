# Aerial Photography Archive Recovery

Issue: https://github.com/tonykoop/claude-skills/issues/44

## Source

- Capture source: Cowork conversation, 2026-05-09.
- Original archive hint: `D:\...\to organize\104ND300`
- Local staged source:
  `/mnt/c/Users/Tony/Documents/GitHub/archive/_archive-recovery-staging/aerial-photography`
- Promotion target: new `aerial-photography` repo.
- Existing GitHub repo check: `tonykoop/aerial-photography` does not currently
  resolve via `gh repo view`.

This note inventories the staged archive and defines the repo scaffold contract.
It does not copy image assets into `claude-skills`.

## Inventory Summary

The staged source contains 231 files:

| Type | Count | Notes |
|---|---:|---|
| JPG images | 230 | Aerial/source photographs across `104ND300`, `104ND307`, and `104ND308`. |
| PDF | 1 | ART FORCE / M Health selection evidence. |

Top-level staged folders:

| Folder | File count | Role |
|---|---:|---|
| `104ND300` | 179 | Primary aerial source folder named in #44. |
| `104ND307` | 5 | Additional aerial source folder; likely related to #58. |
| `104ND308` | 46 | Additional aerial source folder; likely related to #58. |
| `art-force-m-health` | 1 | Selection/installation evidence. |

Selection evidence found:

- `art-force-m-health/Koop, Anthony_21 prints.pdf`

The PDF filename matches the issue note that roughly 21 prints were selected
for the M Health Clinics and Surgery Center installation.

## Anchor Installation

- Installation: M Health Clinics and Surgery Center.
- Address from issue capture: 515 Ontario St SE, Minneapolis, MN.
- Selection process: ART FORCE photo selection approval.
- Print production: digital files printed by University of Minnesota per issue
  capture.
- Portfolio claim status: strong, but should be sourced from the selection PDF
  and any installation photos/correspondence before public copy is written.

## Proposed `aerial-photography` Repo Scaffold

```text
aerial-photography/
  README.md
  LICENSE
  archive-manifest.csv
  originals/
    104ND300/
    104ND307/
    104ND308/
  installations/
    m-health-clinics-surgery-center/
      README.md
      selection/
        Koop, Anthony_21 prints.pdf
      selected-prints/
      installation-photos/
      provenance.md
      rights-review.md
  portfolios/
    aerial-series/
  exports/
    web-previews/
  docs/
    recovery-log.md
    archive-map.md
    public-caption-style.md
```

## Scaffold Steps

1. Create private repo `tonykoop/aerial-photography`.
2. Copy staged folders into `originals/`, preserving original filenames.
3. Generate `archive-manifest.csv` with:
   `path,filename,extension,size_bytes,source_folder,selected_for_m_health,rights_status,notes`.
4. Copy `art-force-m-health/Koop, Anthony_21 prints.pdf` into
   `installations/m-health-clinics-surgery-center/selection/`.
5. Extract the selected print filenames/titles from the PDF into
   `installations/m-health-clinics-surgery-center/README.md`.
6. Populate `selected-prints/` with copies or pointers only after the PDF is
   reviewed, so the selected set is not guessed from filename order.
7. Add `rights-review.md` before public release: confirm Tony's authorship,
   any ART FORCE display rights, University of Minnesota print-production
   language, and whether location/clinic branding can be named in captions.
8. Add web previews separately from originals; keep originals unmodified.

## Related Work

- #58 tracks additional aerial folders `104ND307` and `104ND308`; both are
  already present in the staged source and should be included when the repo is
  created.
- #57 tracks a Kickstarter drone aerial print campaign; keep it separate unless
  the source files overlap during manifest generation.

## Review Notes

- This is one of the strongest portfolio captures because it has institutional
  placement and a named selection process, not only image files.
- Do not fabricate installation year, selected print names, or print sizes from
  memory. Extract them from `Koop, Anthony_21 prints.pdf` or installation
  correspondence.
- Treat `104ND300` as the issue #44 anchor and `104ND307`/`104ND308` as related
  folders until manifest review proves their exact relationship.
