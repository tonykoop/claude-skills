# Weather Balloon Camera Vessel Recovery

Issue: https://github.com/tonykoop/claude-skills/issues/55

## Source

- Capture source: Cowork inventory pass, 2026-05-09.
- Original archive hint: `D:\...\CAD\Weather Balloon Camera Vessel`
- Archive size: ~816.8 MB across 46 files
- Promotion target: new `weather-balloon-camera-vessel` repo

This note inventories what is known from the issue capture and defines the
repo scaffold contract. It does not copy CAD files into `claude-skills`.

## What This Is

A high-altitude photography rig designed (and possibly built) to mount a
camera on a weather balloon. The scale — 817 MB of CAD across only 46 files
— suggests large assemblies with embedded renderings or simulation data,
not just parametric sketches.

The project connects to two other captures:
- **Aerial photography** (#44, #58): if the balloon rig produced images,
  they may overlap with the `104ND300` / `104ND307` / `104ND308` aerial
  folders being recovered in those issues.
- **Kickstarter drone print campaign** (#57): sky-photography context (both
  are "photography from above" projects).

## Inventory Summary (from capture)

| Item | Count / Size | Notes |
|---|---:|---|
| CAD files (all types) | 46 | ~816.8 MB total |
| Images (estimated) | unknown | May be embedded in CAD or separate |
| Flight logs | unknown | May exist if a flight was attempted |

~17.8 MB per file average — consistent with large SolidWorks assemblies
(`.sldasm`) that embed component parts, or with high-resolution renderings
stored alongside the CAD.

## Owner Decisions Required

Before promotion Tony must decide:

1. **Was a physical rig built?** If yes, add build photos and flight/launch
   documentation. If design-only, scope the repo accordingly.
2. **Were images captured?** If balloon flights produced images, decide
   whether they live in `weather-balloon-camera-vessel` or the
   `aerial-photography` repo.
3. **Public vs. private**: no IP or safety restriction on releasing the
   CAD of a camera mount, but the publication decision is Tony's.
4. **Git LFS**: 817 MB across 46 files requires LFS for large assemblies
   and any embedded image/render files.

## Proposed `weather-balloon-camera-vessel` Repo Scaffold

```text
weather-balloon-camera-vessel/
  README.md
  LICENSE
  archive-manifest.csv
  cad/
    assemblies/
    parts/
    drawings/
    exports/
      step/
      stl/
      renderings/
  build/
    photos/
    bom.csv
    build-log.md
  flights/
    flight-log.md
    imagery/
  docs/
    design-intent.md
    recovery-log.md
```

## Scaffold Steps

1. Stage `D:\...\CAD\Weather Balloon Camera Vessel\` to local staging area.
2. Inspect file types and sizes:
   - Separate `.sldprt` / `.sldasm` / `.slddrw` from renderings / images.
   - Identify whether any photos or flight logs are mixed into the CAD folder.
3. Update `archive-manifest.csv` with:
   `filename,extension,size_bytes,type,notes`.
4. Create private repo `tonykoop/weather-balloon-camera-vessel`.
5. Enable Git LFS before copying large files:
   `*.sldprt *.sldasm *.slddrw *.SLDPRT *.SLDASM *.SLDDRW *.step *.STEP *.jpg *.JPG *.png *.PNG`
6. Add `docs/design-intent.md` describing: camera type targeted, expected
   altitude, balloon size/payload spec (if documented in the CAD).
7. If any captured images exist in the archive, evaluate whether to place
   them in `flights/imagery/` here or in the `aerial-photography` repo per
   the relationship review in step 2.
8. Cross-reference with #57 (Kickstarter) during manifest review: confirm
   whether balloon imagery and drone imagery share files.

## Related Work

- `docs/archive-recovery/aerial-photography-recovery.md` (#44, #58) —
  recovering three aerial photography source folders; balloon imagery, if
  any, may belong there.
- `docs/archive-recovery/kickstarter-drone-print-recovery.md` (#57) —
  Kickstarter drone aerial print campaign; different vehicle, potential
  image overlap.
- The `promote-batch-readiness` helper
  (`plugins/maker/skills/idea-incubator/scripts/promote_batch_readiness.py`)
  can generate a readiness matrix for the aerial cluster (#44, #55, #57, #58).

## Review Notes

- The 817 MB / 46 file ratio is large. Before assuming it's all parametric
  CAD, inspect for embedded renders or image archives that may inflate size.
- Do not assert the rig was physically built or flew without evidence in the
  archive (build photos, flight logs, or explicit documentation).
- Aerial photos from a balloon launch would be distinct from the drone
  aerial portfolio (#44) and should be assessed separately for the
  `aerial-photography` repo or a dedicated gallery.
