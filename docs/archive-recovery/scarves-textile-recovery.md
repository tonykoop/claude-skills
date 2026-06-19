# Scarves — Commercial Textile Portfolio Recovery

Issue: https://github.com/tonykoop/claude-skills/issues/56

## Source

- Capture source: Cowork inventory pass, 2026-05-09.
- Original archive hint: `D:\...\Scarves\` (multiple sub-folders)
- Archive size: ~570 MB across 100+ files
- Promotion target: extend `sewing` repo (`sewing/scarves/`) OR scaffold
  a new `apparel` umbrella repo with scarves/shackets/hats sub-categories

This note inventories what is known from the issue capture and defines the
repo scaffold contract. It does not copy textile assets into `claude-skills`.

## What This Is

A commercial scarves practice — not one-offs but a developed portfolio with
multiple categorized inventories reflecting production lifecycle status.
The folder structure encodes the state machine Tony used to manage inventory:

| Folder | Size (approx) | Role |
|---|---:|---|
| `Scarves\For Sale` | 264 MB | Ready-to-sell items |
| `Scarves\Not Yet Ready` | 172 MB | Items in progress or pending |
| `Scarves\No Pocket - For Sale` | 64 MB | Variant without pocket; sellable |
| `Scarves\Christmas Scarves 2017` | unknown | Seasonal 2017 run |
| `Scarves\Not FS` | unknown | Not for sale (samples, rejects, personal) |

The folder taxonomy (`For Sale` / `Not Yet Ready` / `Not FS`) is a live
inventory management system, not just an archive. This matters for how the
recovery is structured: the categories are meaningful and should be
preserved in the repo scaffold.

## Related Captures

This issue connects to the broader apparel decision surfaced in round 1:

- **#54 (Betabrand shacket)** — another apparel piece in the archive;
  both point toward an `apparel` umbrella.
- The `sewing` repo already exists (or is planned); decide whether
  scarves live there as a sub-category or anchor a new `apparel` top-level.

## Owner Decisions Required

Before promotion Tony must decide:

1. **Repo structure**: `sewing/scarves/` (extend existing sewing repo) OR
   new `apparel/scarves/` (umbrella with shackets, hats, etc. per round 1).
2. **What the files are**: 570 MB for 100+ items is ~5.7 MB each — could be
   high-res product photography, design files, or pattern PDFs. The
   content type determines the LFS plan.
3. **Commercial status**: which items in `For Sale` are still actively sold,
   and where (Etsy, local markets, private)? README should reflect current
   availability, not archive labels.
4. **`Christmas Scarves 2017`**: seasonal run — date-stamp as a past
   collection, not current inventory.
5. **`Not FS` items**: clarify whether "Not FS" means private/personal or
   returned/defective. Affects whether they should be committed at all.

## Proposed Scaffold

### Option A — Extend `sewing` repo

```text
sewing/
  scarves/
    README.md
    archive-manifest.csv
    for-sale/
    not-yet-ready/
    no-pocket-for-sale/
    collections/
      christmas-2017/
    not-for-sale/    (if committing samples; otherwise omit)
    docs/
      recovery-log.md
      commercial-notes.md
```

### Option B — New `apparel` umbrella

```text
apparel/
  README.md
  scarves/
    README.md
    archive-manifest.csv
    for-sale/
    not-yet-ready/
    no-pocket-for-sale/
    collections/
      christmas-2017/
    docs/
      recovery-log.md
  shackets/    (from #54 when recovered)
  docs/
    apparel-overview.md
    recovery-log.md
```

## Scaffold Steps

1. Stage `D:\...\Scarves\` locally; keep sub-folder structure intact.
2. Inspect 5 representative files to determine content type (photography,
   pattern PDFs, design files, or mix). This determines the LFS plan.
3. Generate `archive-manifest.csv` with:
   `folder,filename,extension,size_bytes,status,notes`.
   `status` maps to the source folder: `for_sale`, `not_yet_ready`,
   `no_pocket_for_sale`, `collection_christmas_2017`, `not_fs`.
4. Enable Git LFS before copying, based on content type:
   - If photography: `*.jpg *.JPG *.tif *.TIF *.png *.PNG`
   - If patterns/design: `*.pdf *.PDF *.ai *.AI *.psd *.PSD`
5. Create the repo (Option A or B) and copy staged files into the
   appropriate sub-folders.
6. Add `commercial-notes.md` documenting: approximate number of pieces
   sold, venues used (Etsy, markets, etc.), and the practice's current
   status (active / retired / seasonal-only).
7. Cross-reference the shacket recovery (#54) when structuring the
   Option B umbrella — it resolves to the same apparel question.

## Related Work

- `docs/archive-recovery/betabrand-shacket-recovery.md` (PR #285, #54) —
  sibling apparel capture; drives the `apparel` umbrella decision.
- The `promote-batch-readiness` helper
  (`plugins/maker/skills/idea-incubator/scripts/promote_batch_readiness.py`)
  can generate a readiness matrix for the apparel cluster (#54, #56).

## Review Notes

- Do not infer the content type from file size alone — 5.7 MB/file could
  be a compressed JPEG, a pattern PDF, or a design file. Inspect before
  choosing an LFS plan.
- The `For Sale` / `Not Yet Ready` folder taxonomy is meaningful; preserve
  it so the archived state is intelligible without re-reading the archive.
- Avoid committing `Not FS` items without Tony's explicit sign-off, as this
  may include personal or defective pieces he doesn't want public.
