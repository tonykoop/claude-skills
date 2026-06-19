# Additional Aerial Folders — 104ND307 and 104ND308

Issue: https://github.com/tonykoop/claude-skills/issues/58

## Source

- Capture source: Cowork inventory pass, 2026-05-09.
- Original archive hint: `D:\...\to organize\104ND307` (41 MB),
  `D:\...\to organize\104ND308` (204 MB)
- Promotion target: `aerial-photography` repo (extends issue #44)

This note documents the two additional aerial source folders discovered
in the round-2 inventory pass. The primary `104ND300` folder was captured
in #44; this issue expands the scope.

**Note:** The `aerial-photography-recovery.md` (#44) already inventoried
all three folders — `104ND307` and `104ND308` are physically present in the
staged source documented there. This issue exists to ensure the expanded
scope is tracked and the two additional folders are not overlooked when
the `aerial-photography` repo is created.

## Known Inventory

From the staged source documented in the #44 recovery note:

| Folder | Staged files | Size (capture) |
|---|---:|---:|
| `104ND300` | 179 JPG | 1,343 MB |
| `104ND307` | 5 JPG | 41 MB |
| `104ND308` | 46 JPG | 204 MB |
| `art-force-m-health` | 1 PDF | — |

The `104ND307` and `104ND308` folders appear to be sibling shoots to
`104ND300` — same naming convention (`104ND` prefix), same source location
(`to organize\`), same file type (JPG aerial photographs).

## Interpretation

The `104ND` prefix likely encodes a drone/camera model or a job/project
identifier. The three-digit suffix (300, 307, 308) may encode:

- **Sequential flight sessions** (300 = first, 307 + 308 = later flights)
- **Date codes** (e.g., day-of-year or a project identifier)
- **Card or import numbers** (card dumps from a specific SD card)

The correct interpretation is recoverable from EXIF metadata — each JPG
should carry a capture date, GPS location (if not stripped), and camera
model. Inspecting EXIF on a sample from each folder will reveal whether
the folders represent distinct flights or dates.

## Recovery Steps

This issue resolves during the `aerial-photography` repo creation (issue
#44). No separate recovery action is needed beyond ensuring that when the
repo is scaffolded:

1. **All three folders are included** in `originals/`:
   - `originals/104ND300/` — 179 files (issue #44 anchor)
   - `originals/104ND307/` — 5 files (this issue)
   - `originals/104ND308/` — 46 files (this issue)

2. **EXIF inspection on 104ND307 and 104ND308**:
   ```bash
   exiftool -DateTimeOriginal -GPSLatitude -GPSLongitude -Model \
     "104ND307/*.jpg" | head -20
   exiftool -DateTimeOriginal -GPSLatitude -GPSLongitude -Model \
     "104ND308/*.jpg" | head -20
   ```
   Record capture dates, drone model, and any GPS present.

3. **Update `archive-manifest.csv`** with the `source_folder` column
   distinguishing all three folders, so the manifest tracks provenance.

4. **Cross-reference with Kickstarter** (#57): if any 104ND307 / 104ND308
   images appear in the Kickstarter print selections, note it in both
   `docs/archive-map.md` and the Kickstarter campaign summary.

## Cross-Pollination Note

- `docs/archive-recovery/aerial-photography-recovery.md` (#44) — primary
  recovery doc; 104ND307 and 104ND308 are staged there and documented in
  the "Related Work" section.
- `docs/archive-recovery/kickstarter-drone-print-recovery.md` (#57) —
  Kickstarter prints draw from aerial source files; check for overlap.
- `docs/archive-recovery/weather-balloon-camera-vessel-recovery.md` (#55) —
  separate aerial vehicle; confirm no image overlap during manifest review.

## Review Notes

- Do not guess flight dates or locations. EXIF must confirm them before
  any caption or metadata is written.
- 104ND307 has only 5 files (41 MB) — small enough that it might be a
  single flight or a targeted selection, not a full shoot. Treat as
  incomplete until EXIF confirms.
- If GPS data is present in the originals, strip it from web-preview
  exports before public release (unless the shoot location is already
  public, e.g. M Health installation site).
