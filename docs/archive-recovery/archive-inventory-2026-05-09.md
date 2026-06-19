# Archive Inventory 2026-05-09

Issue: #53

## Contract

Issue #53 asks for the full archive inventory CSV from the 2026-05-09 Cowork
archive pass to be committed at:

`data/archive-inventory-2026-05-09.csv`

## Source Used

The requested CSV already existed locally at:

`/mnt/c/Users/Tony/Documents/GitHub/archive/archive-inventory-2026-05-09.csv`

That file was copied into this repo as:

`data/archive-inventory-2026-05-09.csv`

The committed CSV preserves the original one-off inventory column shape:

- `RelativePath`
- `Depth`
- `FileCount`
- `TotalSizeMB`
- `LastModified`
- `Extensions`

## Verification Notes

The reusable tool in `_meta/archive-inventory-tools/Invoke-ArchiveInventory.ps1`
has a newer multi-root column shape with `RootName` and `RootPath`, but the
issue's promotion target names the original one-off CSV. This branch therefore
commits the existing original CSV rather than regenerating a new incompatible
schema.

The mounted drive also contains a path matching the README example under:

`/mnt/d/Videos/External Hard Drive Consolidation/Lacie Share with photos from 2014/Document Archive 3-3-18`

That copy was inspected but not used because it has only 11 directory rows and
is dominated by MP4 files, which does not match the CAD/archive recovery context
or the existing inventory artifact.

## Commands Run

```bash
gh issue view 53 -R tonykoop/claude-skills --json number,title,body,labels
qmd search "Full inventory pass D archive 1.67 GB 140 folders"
qmd search "archive inventory To Organize2"
find /mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools -maxdepth 3 -type f -printf '%P\n'
sed -n '1,240p' /mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools/README.md
sed -n '1,260p' /mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools/Invoke-ArchiveInventory.ps1
find /mnt/d -maxdepth 6 -type d -iname '*Document*Archive*'
find /mnt/c/Users/Tony/Documents/GitHub -iname '*archive-inventory*2026*05*09*.csv'
cp /mnt/c/Users/Tony/Documents/GitHub/archive/archive-inventory-2026-05-09.csv data/archive-inventory-2026-05-09.csv
wc -l data/archive-inventory-2026-05-09.csv
head -8 data/archive-inventory-2026-05-09.csv
```

## Assessment

#53's requested deliverable is now present in the repository at the requested
path. The CSV is an archive map, not a source-asset copy; downstream recovery
issues should continue to use it as discovery evidence before deciding repo
strategy.
