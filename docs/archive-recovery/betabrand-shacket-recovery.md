# Betabrand Shacket Recovery

Issue: #54

## Contract

Issue #54 asks to review the 2015 Betabrand shirt-jacket archive packet and
decide whether it belongs under the existing `sewing` repo or a broader apparel
umbrella.

## Archive Evidence

The archive recovery copy plan identifies the source as:

`D:\External Hard Drive Consolidation\Lacie Share with photos from 2014\Document Archive 3-3-18\to organize\Shacket Photos and Video`

The planned destination was:

`C:\Users\Tony\Documents\GitHub\sewing\legacy\archive-2018\betabrand-shacket`

Robocopy log inspected:

`/mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools/logs/betabrand-shacket.robocopy.log`

Robocopy result:

- Status: OK
- Directories copied: 3
- Files copied: 39
- Bytes copied: 147.33 MB
- Failed: 0

Recovered local paths inspected:

- `/mnt/c/Users/Tony/Documents/GitHub/fabrication/sewing/legacy/archive-2018/betabrand-shacket`
- `/mnt/c/Users/Tony/Documents/GitHub/fabrication/sewing/projects/Shacket Photos and Video`

Both contain the same visible two-folder structure:

- `Cordaround/`: 19 JPG files
- `Herringbone/`: 20 JPG files

## Repo State

`tonykoop/sewing` exists and is private:

- URL: `https://github.com/tonykoop/sewing`
- Default branch: `main`
- Description: soft-goods craft archive focused on reversible scarves,
  practical sewing, and textile design process.

The local checkout inspected at
`/mnt/c/Users/Tony/Documents/GitHub/fabrication/sewing` was clean on `main`.

## Recommendation

Use the existing `sewing` repo as the promotion target for this packet:

`sewing/projects/2015-betabrand-shacket/`

Do not create a new apparel umbrella from this packet alone. The archive
inventory shows additional textile/apparel material such as `Scarves`, but the
shacket packet itself is only one 39-image case study and does not justify a
separate repo without a broader apparel curation pass.

Because the recovered files are photographs and brand-adjacent Betabrand
submission material, keep the asset copy private until reviewed for publication
rights, third-party marks, and portfolio-safe image selection.

## Verification Commands

```bash
gh issue view 54 -R tonykoop/claude-skills --json number,title,body,labels
qmd search "Betabrand shacket sewing repo organization"
qmd search "shacket Betabrand"
rg -n "betabrand|shacket|Cordaround|Herringbone" /mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools/archive-recovery-copy-plan-2026-05-09.csv
gh repo view tonykoop/sewing --json nameWithOwner,visibility,url,defaultBranchRef,description
sed -n '1,120p' /mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools/logs/betabrand-shacket.robocopy.log
find /mnt/c/Users/Tony/Documents/GitHub -maxdepth 5 -type d -iname '*shacket*'
find /mnt/c/Users/Tony/Documents/GitHub/fabrication/sewing/legacy/archive-2018/betabrand-shacket -type f | wc -l
find /mnt/c/Users/Tony/Documents/GitHub/fabrication/sewing/legacy/archive-2018/betabrand-shacket -maxdepth 2 -type f -printf '%P\n' | sort
git -C /mnt/c/Users/Tony/Documents/GitHub/fabrication/sewing status --short --branch
```

## Assessment

#54 has concrete recovered asset evidence and a natural existing home in
`sewing`. The next useful work belongs in the `sewing` repo: curate the 39
images, add a private/public-safe project note, and only promote selected assets
after rights and branding review.
