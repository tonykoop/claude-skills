# Wood Mallet CAD Recovery Verification

Issue: #46

## Contract

Issue #46 asks to review the wood mallet CAD from `To Organize2\`, decide whether
it belongs in `woodworking/designs/mallets/` or a new shop-tools umbrella, and
use the existing `woodworking` repo as the likely promotion target.

## Current downstream state

The promotion target already exists:

- Repo: `tonykoop/woodworking`
- URL: `https://github.com/tonykoop/woodworking`
- Visibility: public
- Default branch: `main`
- Local checkout inspected: `/mnt/c/Users/Tony/Documents/GitHub/woodworking`

The repo's current `main` head is:

- `6b90442 Scaffold recovery packet for wood mallet (Refs #46, #212) (#1)`

That commit is present at `HEAD`, `origin/main`, and `origin/HEAD` in the local
checkout inspected for this verification.

## Recovered files

The CAD recovery packet is already tracked in `tonykoop/woodworking` under:

`legacy/archive-2018/wood-mallet/`

Tracked files:

- `legacy/archive-2018/wood-mallet/Mallet.SLDASM`
- `legacy/archive-2018/wood-mallet/Mallet Head.SLDPRT`
- `legacy/archive-2018/wood-mallet/Mallet Handle.SLDPRT`
- `legacy/archive-2018/wood-mallet/Mallet Handle Turned.SLDPRT`
- `legacy/archive-2018/wood-mallet/README.md`

The related project photo is also tracked:

- `projects/mallet/wooden mallet.jpg`

## README evidence

The downstream README describes the packet as a wooden shop mallet for chisel
and joinery work, with a turned handle seated into a solid head. It states that
the folder holds SolidWorks CAD only and that the files were recovered from the
`D:\` external hard drive archive during the 2026-05-09 2018 archive sweep.

It also preserves the placement decision requested by #46: the files currently
remain under `legacy/archive-2018/wood-mallet/`, while the natural home is most
likely `woodworking/projects/` or a future `shop-tools-and-jigs/` umbrella.

## Verification commands

Commands run from this `claude-skills` worktree:

```bash
qmd search "Wood mallet CAD recovery"
gh issue view 46 -R tonykoop/claude-skills --json number,title,body,labels
gh repo view tonykoop/woodworking --json nameWithOwner,description,visibility,defaultBranchRef,url
find /mnt/c/Users/Tony/Documents/GitHub -iname '*mallet*'
git -C /mnt/c/Users/Tony/Documents/GitHub/woodworking status --short --branch
git -C /mnt/c/Users/Tony/Documents/GitHub/woodworking log --oneline --decorate --all --grep mallet --max-count 20
git -C /mnt/c/Users/Tony/Documents/GitHub/woodworking ls-tree -r --name-only HEAD legacy/archive-2018/wood-mallet
git -C /mnt/c/Users/Tony/Documents/GitHub/woodworking ls-tree -r --name-only HEAD projects/mallet
```

## Assessment

The asset recovery portion of #46 is satisfied downstream in
`tonykoop/woodworking`. No CAD files should be copied into `claude-skills`.

The remaining product decision is organizational: keep the packet as an archive
recovery under `legacy/archive-2018/wood-mallet/`, promote it into
`woodworking/projects/mallet/`, or move it later into a broader
`shop-tools-and-jigs` structure if that umbrella is created.

No fabrication dimensions, CAD feature details, or build readiness claims are
made here beyond the tracked filenames and the downstream README evidence.
