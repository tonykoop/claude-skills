# Kickstarter Drone Aerial Print Campaign Recovery

Issue: https://github.com/tonykoop/claude-skills/issues/57

## Source

- Capture source: Cowork inventory pass, 2026-05-09.
- Original archive hint: `D:\...\Kickstarter\`, `D:\...\Kickstarter Originals\`
- Archive size: ~342+ MB across two root folders (Kickstarter: ~342 MB;
  Kickstarter Originals: size unknown at capture)
- Promotion target: sub-folder of `aerial-photography` repo OR own repo

This note inventories what is known from the issue capture and defines the
repo scaffold contract. It does not copy image or campaign files into
`claude-skills`.

## What This Is

A Kickstarter campaign Tony ran for a drone-aerial-photography print
product. Backers received WHCC-printed fine-art prints in multiple sizes.
Evidence from the archive folder structure points to:

- A **FlySafe** component — likely a drone safety insert, product bundle,
  or add-on (potentially the campaign's drone regulatory angle).
- **WHCC** (White House Custom Colour) as the print lab — professional
  fine-art printing, consistent with a photography print campaign.
- Multiple print formats: `8x10`, `11x14`, `12x18`, `12x18 Canvas Wrap`.
- Product references from major drone retailers: 3DRobotics, B&H Photo
  Video, Helipal, RCPlant, REI, xaircraftamerica — these are likely
  image source credits or product photo references used in campaign assets.

## Inventory Summary (from capture)

| Folder | Size (approx) | Role |
|---|---:|---|
| `Kickstarter\Flyer` | 217 MB | Campaign flyer assets (images, layouts) |
| `Kickstarter\WHCC\B Side` | 125 MB | WHCC print production B-side |
| `Kickstarter Originals\8x10` | unknown | Original source prints, 8×10 |
| `Kickstarter Originals\11x14` | unknown | Original source prints, 11×14 |
| `Kickstarter Originals\12x18` | unknown | Original source prints, 12×18 |
| `Kickstarter Originals\12x18 Canvas Wrap` | unknown | Canvas variant |
| `Kickstarter Originals\Address Stickers` | unknown | Backer mailing labels |
| `Kickstarter Originals\Backer Reports` | unknown | Campaign backer data |
| `Kickstarter Originals\FlySafe` | unknown | FlySafe product materials |
| `Kickstarter Originals\Manuals` | unknown | Product/drone manuals |
| `Kickstarter Originals\Photo Stickers` | unknown | Photo sticker product |
| `Kickstarter Originals\Receipts` | unknown | Campaign receipts/financials |
| `Kickstarter Originals\Replacement photos` | unknown | Backer replacement prints |

## Owner Decisions Required

Before promotion Tony must decide:

1. **Campaign date and outcome**: determine the Kickstarter campaign date,
   funding outcome (funded/unfunded), and approximate number of backers.
   Backer Reports folder likely contains this.
2. **Backer data privacy**: `Address Stickers` and `Backer Reports` contain
   backer PII (names, addresses). These must remain private or be stripped
   before any public repo.
3. **Financials**: `Receipts` folder contains financial records. Private
   or redacted only.
4. **Repo structure**: sub-folder of `aerial-photography` (if images are
   the same pool) OR own `kickstarter-drone-prints` repo (if the campaign
   and images are a distinct portfolio claim).
5. **FlySafe relationship**: determine if FlySafe is Tony's own product,
   a partner product, or a third-party insert. Affects IP section of README.
6. **Git LFS**: `Kickstarter\Flyer` at 217 MB likely contains large image
   files; enable LFS before copying.

## Proposed Scaffold

Two options based on the promotion target decision:

### Option A — Sub-folder of `aerial-photography`

```text
aerial-photography/
  campaigns/
    kickstarter-drone-prints/
      README.md
      campaign-summary.md
      archive-manifest.csv
      campaign-assets/     (public campaign flyer crops, not full 217 MB)
      prints/
        8x10/
        11x14/
        12x18/
        12x18-canvas-wrap/
      fly-safe/
      docs/
        backer-report-summary.md   (aggregate stats, no PII)
        recovery-log.md
```

### Option B — Own repo `kickstarter-drone-prints`

```text
kickstarter-drone-prints/
  README.md
  LICENSE
  archive-manifest.csv
  campaign-assets/
  prints/
    8x10/
    11x14/
    12x18/
    12x18-canvas-wrap/
  fly-safe/
  docs/
    campaign-summary.md
    backer-report-summary.md   (aggregate stats, no PII)
    recovery-log.md
```

## Scaffold Steps

1. Stage `D:\...\Kickstarter\` and `D:\...\Kickstarter Originals\` locally.
2. Open `Backer Reports` first to determine campaign date and backer count
   for `campaign-summary.md`. Do not commit backer PII.
3. Inventory all image files; generate `archive-manifest.csv` with:
   `folder,filename,extension,size_bytes,print_size,notes`.
4. Confirm whether `Kickstarter Originals` print sizes are source files
   (original aerial shots) or production files (sized for WHCC). This
   determines whether they belong in `prints/` or `aerial-photography/originals/`.
5. Assess `FlySafe` folder: if it's Tony's product, document in its own
   `fly-safe/` section; if third-party, note the relationship only.
6. Enable Git LFS before copying large image files:
   `*.jpg *.JPG *.tif *.TIF *.psd *.PSD *.pdf *.PDF *.png *.PNG`
7. Strip backer PII (name, address, email) from any committed documents.
   Keep only aggregate stats (total backers, funded amount, campaign dates).

## Related Work

- `docs/archive-recovery/aerial-photography-recovery.md` (#44, #58) —
  the primary aerial source archive; confirm whether Kickstarter prints
  draw from the same `104ND300` / `104ND307` / `104ND308` source pool.
- `docs/archive-recovery/weather-balloon-camera-vessel-recovery.md` (#55) —
  separate aerial-photography-adjacent project; distinct vehicle, check for
  image overlap.
- The `promote-batch-readiness` helper
  (`plugins/maker/skills/idea-incubator/scripts/promote_batch_readiness.py`)
  can generate a readiness matrix for the aerial cluster (#44, #55, #57, #58).

## Review Notes

- Do not fabricate the campaign funding outcome, campaign dates, or backer
  count. Extract from `Backer Reports`.
- The `WHCC\B Side` label likely means the print's non-image face (backing
  paper, label) — confirm before interpreting as a "B-roll" or second series.
- Product retailer references (3DRobotics, B&H, REI, etc.) are likely image
  source credits or campaign product references, not partnerships. Confirm
  before claiming endorsement.
- Kickstarter campaign pages are public even after a campaign ends; the
  campaign URL can usually be found by searching Kickstarter for Tony's
  name — include it in `campaign-summary.md` if found.
