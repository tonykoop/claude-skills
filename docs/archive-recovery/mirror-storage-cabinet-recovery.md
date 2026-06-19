# Mirror Storage Cabinet System Recovery

Issue: https://github.com/tonykoop/claude-skills/issues/59

## Source

- Capture source: Cowork inventory pass + Tony, 2026-05-09.
- Original archive hint: `D:\...\CAD\Gun Safe\EP15847–EP15859`
- Archive size: ~357 MB
- Promotion target: new `mirror-storage-cabinet` repo, or extend
  `retail-displays` if that project exists.

This note inventories what is known from the issue capture and defines the
repo scaffold contract. It does not copy CAD files into `claude-skills`.

## What This Is

A professional-grade gun safe / showcase / display cabinet system. The
sequential `EP`-prefix part numbering (EP15847 → EP15859) indicates a
developed series where each part number is a distinct component type, not
a revision — they are sibling assemblies in a single cabinet ecosystem.

Inferred from the folder name and the EP-prefix convention:

| Part # | Inferred assembly name |
|---|---|
| EP15847 | Cabinet panels |
| EP15848 | Shelf panels |
| EP15849 | Vitrine (glass/display) panels |
| EP15850–EP15855 | Showcase cabinet variants (6 distinct cabinet configs) |
| EP15856 | Handgun magnet panels |
| EP15857 | Handgun magazine inserts |
| EP15858 | Handgun dowel brackets |
| EP15859 | Long-gun panels |

A McMaster sourcing reference was also noted in the capture — meaning
hardware was being specified for procurement, not just modeled.

## Inventory Summary (from capture)

| Item | Count / Size | Notes |
|---|---:|---|
| CAD files (all types) | ~46 (estimated) | 357 MB total |
| McMaster sourcing ref | 1 | Hardware spec; not a CAD file |

Exact file counts and formats (SolidWorks `.sldprt`/`.sldasm`/`.slddrw`,
STEP, STL, DXF, etc.) must be confirmed when the archive is staged.

## Owner Decisions Required

Before promotion Tony must decide:

1. **Scope**: publish as own repo, keep private as portfolio reference, or
   extend an existing `retail-displays` project.
2. **IP**: all hardware was designed by Tony; McMaster hardware is
   commercial off-the-shelf — no third-party IP concerns beyond the sourcing
   ref itself.
3. **Public vs. private**: the product category (gun storage) carries no
   legal or safety restriction on releasing CAD, but a personal-portfolio
   decision is still required.
4. **LFS**: 357 MB of CAD requires Git LFS for any file types over the
   GitHub 100 MB limit (e.g., large assemblies, renderings).

## Proposed `mirror-storage-cabinet` Repo Scaffold

```text
mirror-storage-cabinet/
  README.md
  LICENSE
  archive-manifest.csv
  cad/
    EP15847-cabinet-panels/
    EP15848-shelf-panels/
    EP15849-vitrine-panels/
    EP15850-showcase-cabinet-v1/
    EP15851-showcase-cabinet-v2/
    EP15852-showcase-cabinet-v3/
    EP15853-showcase-cabinet-v4/
    EP15854-showcase-cabinet-v5/
    EP15855-showcase-cabinet-v6/
    EP15856-handgun-magnet-panels/
    EP15857-handgun-magazine-inserts/
    EP15858-handgun-dowel-brackets/
    EP15859-long-gun-panels/
  hardware/
    mcmaster-sourcing/
      mcmaster-parts-list.md
  docs/
    recovery-log.md
    design-intent.md
    assembly-overview.md
  exports/
    step/
    stl/
    renders/
```

## Scaffold Steps

1. Stage `D:\...\CAD\Gun Safe\EP15847–EP15859` to local staging area.
2. Inspect file types and sizes; update `archive-manifest.csv` with:
   `part_number,filename,extension,size_bytes,assembly_role,notes`.
3. Confirm EP15850–EP15855 are 6 distinct showcase cabinet configs (not
   revisions of the same part). If revisions, collapse into one folder per
   part with a `/revisions/` sub-folder.
4. Extract the McMaster sourcing reference (CSV, BOM sheet, or PDF) into
   `hardware/mcmaster-sourcing/`.
5. Create private repo `tonykoop/mirror-storage-cabinet` (or evaluate
   `retail-displays` extension).
6. Enable Git LFS for large file types before copying:
   `*.sldprt *.sldasm *.slddrw *.SLDPRT *.SLDASM *.SLDDRW *.step *.STEP`
7. Add `docs/design-intent.md` with what is known: display cabinet system,
   gun-safe and showcase variants, metal construction implied by McMaster
   sourcing.
8. Write `docs/assembly-overview.md` tracing the EP-prefix chain once
   files are inspected.

## Related Work

- Structurally similar to the stencil and chessboard-table CAD recovery
  (`docs/archive-recovery/stencil-art-recovery.md`,
  `docs/archive-recovery/chessboard-table-cad-verification.md`).
- The `promote-batch-readiness` helper
  (`plugins/maker/skills/idea-incubator/scripts/promote_batch_readiness.py`)
  can generate a readiness matrix for this cluster.

## Review Notes

- Do not guess the number of showcase cabinet variants. The EP15850–EP15855
  range spans six part numbers; they may be 6 variants or fewer if some
  numbers were skipped. Confirm when staged.
- Do not publish the McMaster sourcing reference without stripping any
  Tony-specific pricing or quote data.
- The "Gun Safe" folder name in the archive is the source folder label, not
  a product name — the actual product category needs to be confirmed from
  the CAD content before public copy is written.
