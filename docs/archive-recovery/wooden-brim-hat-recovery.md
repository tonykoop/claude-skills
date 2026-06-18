# Wooden Brim Hat Design Inspiration Recovery

Issue: #47

## Contract

Issue #47 asks to review the `To Organize2\` wooden brim hat material and
determine whether it is a build project or only an inspiration board.

The issue is labeled `needs-clarification`, so this note records only recovered
archive evidence and the next routing decision. It does not claim a finished
wearable design, dimensions, fabrication method, or build readiness.

## Archive evidence

The strongest matching files found are in the external-drive consolidation
packet that also held the stencil-art archive:

`/mnt/d/External Hard Drive Consolidation/Stencil Art REV072715/`

Matching files:

- `wood brim pattern 1.AI`
- `wood brim pattern 1.SLDPRT`
- `~$wood brim pattern 1.SLDPRT`

The two non-temp files have September 2017 filesystem timestamps in the mounted
archive view:

- `wood brim pattern 1.AI`: 733 KiB, Sep 5 2017
- `wood brim pattern 1.SLDPRT`: 114 KiB, Sep 4 2017

The archive folder also contains Illustrator, SolidWorks, PDF, SVG, PSD, NEF,
PNG, and JPG material for stencil/artwork work. That context makes the wooden
brim files look like a real design-file seed rather than a text-only idea, but
the inspected evidence is still only two named design files plus a SolidWorks
lock/temp file.

## Repo state

No dedicated GitHub repo was found for:

- `tonykoop/wooden-brim-hat`

The promotion target should remain TBD until the files are opened or visually
reviewed. Plausible homes:

- An apparel/accessory portfolio repo if this is a distinct wearable project.
- A stencil-art/archive-recovery repo if the files are an art-pattern sidecar.
- A woodworking or mixed-media shop-project repo if the SolidWorks file proves
  to be a physical wooden brim component.

## Verification commands

Commands run from this `claude-skills` worktree:

```bash
qmd search "Wooden brim hat design inspiration"
qmd search "wooden brim hat" -c woodworking
qmd search "wood hat brim"
gh issue view 47 -R tonykoop/claude-skills --json number,title,body,labels
find /mnt/c/Users/Tony/Documents/GitHub/archive -iname '*hat*'
find /mnt/c/Users/Tony/Documents/GitHub/archive -iname '*brim*'
find /mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools -iname '*hat*'
find /mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools -iname '*brim*'
find /mnt/d -maxdepth 5 -iname '*brim*'
find /mnt/d -maxdepth 5 -iname '*hat*'
find /mnt/d/External\ Hard\ Drive\ Consolidation/Stencil\ Art\ REV072715 -maxdepth 1 -type f -printf '%f\n'
ls -lh /mnt/d/External\ Hard\ Drive\ Consolidation/Stencil\ Art\ REV072715/wood\ brim\ pattern\ 1.AI /mnt/d/External\ Hard\ Drive\ Consolidation/Stencil\ Art\ REV072715/wood\ brim\ pattern\ 1.SLDPRT
gh repo view tonykoop/wooden-brim-hat --json nameWithOwner,visibility,url,defaultBranchRef
```

One broader exact-name search was started and then stopped after it ran too long
over the full external-drive consolidation tree:

```bash
find /mnt/d/External\ Hard\ Drive\ Consolidation -iname '*wood*brim*'
```

## Assessment

#47 is not just a vague inspiration note: the archive has both Illustrator and
SolidWorks files named `wood brim pattern 1`. The next useful step is to inspect
those design files in the appropriate tools and decide whether they represent a
wearable hat-brim project, a stencil/pattern asset, or a mixed-media shop
experiment.

Until that inspection happens, keep the issue in clarification mode and avoid
creating a public repo with fabricated design claims.
