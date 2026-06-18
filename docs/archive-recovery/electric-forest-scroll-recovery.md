# Electric Forest Scroll Design Files Recovery

Issue: #48

## Contract

Issue #48 asks to review Electric Forest scroll design files from
`To Organize2\`, determine scope, and decide whether this belongs in a future
festival/event-design portfolio.

## Archive evidence

The strongest matching files found are in:

`/mnt/d/External Hard Drive Consolidation/`

Electric Forest design files:

- `Koops Scrolls for EF 2015.ai`
- `Koops Scrolls for EF 2015.pdf`
- `Koops Scrolls for EF 2015 V2.pdf`
- `Electric Forest 2017 Junior Scroll Side 1 (reduced).pdf`
- `Electric Forest - 2016.ai`
- `Electric Forest - 2016.pdf`
- `Electric Forest 2017 - Monarch Audition Planning.docx`
- `electric forest logo.png`
- `electric forest sticker.jpg`
- `ElectricForest2016_Schedule_LowRes.pdf`
- `FedEx Office Print Online reciept electric forest.pdf`
- `LodgingMapV2-2000x1313 - Electric Forest 2016.jpg`

Related Electric Forest images were also present in the Stencil Art archive
packet:

- `Stencil Art REV072715/Electric Forest Elephant.jpg`
- `Stencil Art REV072715/Electric Forest Front Gate.jpg`
- `Stencil Art REV072715/Electric Forest Spaceship.jpg`

## Scroll-specific files

The explicitly scroll-named files are:

- `Koops Scrolls for EF 2015.ai`: 274 MiB, Jun 21 2015
- `Koops Scrolls for EF 2015.pdf`: 140 MiB, Jun 20 2015
- `Koops Scrolls for EF 2015 V2.pdf`: 138 MiB, Jun 21 2015
- `Electric Forest 2017 Junior Scroll Side 1 (reduced).pdf`: 20 MiB, Jun 16 2017

`pdftotext` produced no meaningful text for the 2015 scroll PDF or the 2017
reduced scroll PDF, which is consistent with artwork/vector/image-heavy design
files. The artwork itself was not visually inspected in this pass.

## Repo state

No dedicated `tonykoop/event-design` repo was found.

Promotion target remains TBD, but the archive evidence supports a real
festival/event-design packet rather than a vague capture:

- Use an `event-design` umbrella if the goal is a public portfolio of festival
  graphics, print collateral, and venue/event artifacts.
- Use a narrower `electric-forest-scrolls` or similar repo only if the scroll
  work becomes a standalone reference build.
- Keep the files private/archive-only until the artwork is visually reviewed
  for licensing, third-party marks, names, and event-brand permissions.

## Verification commands

Commands run from this `claude-skills` worktree:

```bash
qmd search "Electric Forest scroll design files"
qmd search "Electric Forest scroll"
qmd search "scroll design files" -c makerspace
gh issue view 48 -R tonykoop/claude-skills --json number,title,body,labels
find /mnt/c/Users/Tony/Documents/GitHub/archive -iname '*electric*forest*'
find /mnt/c/Users/Tony/Documents/GitHub/archive -iname '*scroll*'
find /mnt/d/External\ Hard\ Drive\ Consolidation -maxdepth 4 -iname '*Electric*Forest*'
find /mnt/d/External\ Hard\ Drive\ Consolidation -maxdepth 4 -iname '*scroll*'
ls -lh /mnt/d/External\ Hard\ Drive\ Consolidation/Electric\ Forest\ -\ 2016.ai /mnt/d/External\ Hard\ Drive\ Consolidation/Electric\ Forest\ -\ 2016.pdf /mnt/d/External\ Hard\ Drive\ Consolidation/Electric\ Forest\ 2017\ Junior\ Scroll\ Side\ 1\ \(reduced\).pdf /mnt/d/External\ Hard\ Drive\ Consolidation/Koops\ Scrolls\ for\ EF\ 2015\ V2.pdf /mnt/d/External\ Hard\ Drive\ Consolidation/Koops\ Scrolls\ for\ EF\ 2015.ai /mnt/d/External\ Hard\ Drive\ Consolidation/Koops\ Scrolls\ for\ EF\ 2015.pdf
pdftotext /mnt/d/External\ Hard\ Drive\ Consolidation/Koops\ Scrolls\ for\ EF\ 2015.pdf -
pdftotext /mnt/d/External\ Hard\ Drive\ Consolidation/Electric\ Forest\ 2017\ Junior\ Scroll\ Side\ 1\ \(reduced\).pdf -
gh repo view tonykoop/event-design --json nameWithOwner,visibility,url,defaultBranchRef
```

## Assessment

#48 has concrete design-file evidence: large Illustrator/PDF scroll assets from
2015 and a reduced 2017 junior scroll PDF, plus adjacent Electric Forest design
collateral. The next useful step is visual review and licensing/public-release
triage, not repo publication from filenames alone.
