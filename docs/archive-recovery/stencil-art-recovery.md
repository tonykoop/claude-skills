# Stencil Art Archive Recovery

Issue: https://github.com/tonykoop/claude-skills/issues/42

## Source

- Capture source: Cowork conversation, 2026-05-09.
- Archive path found locally:
  `/mnt/d/External Hard Drive Consolidation/Stencil Art REV072715`
- Original Windows hint: `D:\...\to organize\Stencil Art REV072715`
- Revision clue: `REV072715` likely means 2015-07-27.
- Promotion target: new `stencil-art` repo.
- Existing GitHub repo check: `tonykoop/stencil-art` does not currently
  resolve via `gh repo view`.

This note inventories the archive and defines the scaffold contract. It does
not copy archive assets into `claude-skills`.

## Inventory Summary

The archive is a flat folder with 72 top-level files.

| Extension | Count | Meaning |
|---|---:|---|
| `jpg` / `JPG` | 25 | Reference photos and source imagery |
| `ai` / `AI` | 20 | Illustrator stencil/vector working files |
| `pdf` | 8 | Exported vector/PDF revisions and paint reference |
| `SLDPRT` | 5 | SolidWorks part models |
| `NEF` | 5 | Nikon raw photo references |
| `psd` | 3 | Photoshop working files |
| `SLDDRW` | 2 | SolidWorks drawings |
| `png` | 2 | Raster export/reference |
| `svg` | 1 | Web/vector export |
| `ase` | 1 | Adobe swatch palette |

Largest files by size:

| Size bytes | File |
|---:|---|
| 31294283 | `Jane Goodall.ai` |
| 26420672 | `ADK_7708.NEF` |
| 26251136 | `ADK_7717.NEF` |
| 26037472 | `ADK_7741.NEF` |
| 25997120 | `ADK_7760.NEF` |
| 25921696 | `ADK_5498.NEF` |
| 11867695 | `Minneapolis Skyline from Calhoun.ai` |
| 8114702 | `Bill Nye V2.ai` |
| 6938112 | `Trispoke Tesselation.SLDPRT` |
| 5286327 | `dalai-lama.psd` |

## Apparent Work Clusters

| Cluster | Evidence files | Recovery treatment |
|---|---|---|
| Portrait stencil studies | `Bill Nye*.ai`, `Dalai Lama*.ai`, `Jane Goodall.ai`, `Neil Degrasse Tyson.ai` plus JPG/PSD/PNG references | Keep original source images beside vector derivatives; record public-domain/licensing status before publishing. |
| Trispoke/tessellation geometry | `Trispoke Tesselation*`, `TriSpoke Drawing*`, `practice tesselation*`, `sacred geometry - tesselating trispokes.ai` | Preserve Illustrator, PDF/SVG exports, and SolidWorks files as one parametric/vector family. |
| Minneapolis skyline/place references | `Minneapolis Skyline from Calhoun.ai`, `33 South 6th St.jpg`, `IDS Tower.jpg`, `Calhoun Bridge.jpg`, `Target_Plaza_South.JPG`, `The Tin Fish.jpg` | Treat as source-photo/reference set plus derived skyline vector. |
| Electric Forest references | `Electric Forest Elephant.jpg`, `Electric Forest Front Gate.jpg`, `Electric Forest Spaceship.jpg` | Likely reference imagery; verify rights before public repo inclusion. |
| Wood brim / pattern overlap | `wood brim pattern 1.AI`, `wood brim pattern 1.SLDPRT` | Cross-link to issue #47 if that branch becomes the owner for hat/brim work. |
| Palette / paint reference | `1009_Montana_GOLD_CMYK_colors.ase`, `1312_GOLD_DinLang_16s_GB_web.pdf` | Keep under references; document that these are vendor palette/material references. |

## Proposed `stencil-art` Repo Scaffold

```text
stencil-art/
  README.md
  LICENSE
  archive-manifest.csv
  originals/
    REV072715/
      vectors/
      raster-references/
      raw-photos/
      photoshop/
      solidworks/
      palettes/
      vendor-reference/
  projects/
    portraits/
    trispoke-tessellation/
    minneapolis-skyline/
    electric-forest/
    wood-brim-pattern/
  exports/
    svg/
    pdf/
    preview-images/
  docs/
    provenance.md
    rights-review.md
    recovery-log.md
```

## Copy / Scaffold Steps

1. Create private repo `tonykoop/stencil-art`.
2. Copy the archive folder into `originals/REV072715/`, preserving filenames.
3. Generate `archive-manifest.csv` with at least:
   `path,filename,extension,size_bytes,cluster,derived_from,rights_status,notes`.
4. Move files into typed subfolders only after the manifest captures their
   original path.
5. Add `docs/provenance.md` with the source path, capture issue, and date.
6. Add `docs/rights-review.md` before any public release; several portrait,
   festival, skyline, vendor-palette, and NASA/reference files may have
   third-party rights constraints.
7. Add previews from derived exports only; do not publish raw reference photos
   until rights are checked.
8. Cross-link likely related claude-skills issues:
   - #47, wooden brim hat design inspiration.
   - #48, Electric Forest scroll design files.

## Review Notes

- The archive is substantive enough for a repo: it contains working vector
  files, parametric/solid-model experiments, raster references, and export
  revisions.
- This is not yet public-ready. Rights/provenance review is the main blocker,
  not file discovery.
- The `~$wood brim pattern 1.SLDPRT` file looks like a SolidWorks lock/temp
  file; preserve it during first copy for provenance, then decide whether to
  exclude it from the cleaned repo.
