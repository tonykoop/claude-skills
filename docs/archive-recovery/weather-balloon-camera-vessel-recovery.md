# Weather Balloon Camera Vessel Recovery

Issue: #55

## Contract

Issue #55 asks to recover and scaffold a new `weather-balloon-camera-vessel`
repo from a substantial CAD packet for a high-altitude camera rig.

## Archive Evidence

The archive recovery copy plan identifies the source as:

`D:\External Hard Drive Consolidation\Lacie Share with photos from 2014\Document Archive 3-3-18\CAD\Weather Balloon Camera Vessel`

The staged local packet was found at:

`/mnt/c/Users/Tony/Documents/GitHub/archive/_archive-recovery-staging/weather-balloon-camera-vessel/cad`

Robocopy log inspected:

`/mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools/logs/weather-balloon-camera-vessel.robocopy.log`

Robocopy result:

- Files copied: 46
- Bytes copied: 816.81 MB
- Failed: 0

Current staged packet inventory:

- Total files: 46
- Disk usage: 817M
- Extensions:
  - `SLDPRT`: 22
  - `stl`: 11
  - `jpg`: 11
  - `eprt`: 2

Representative files:

- `Weather Ballon Camera Ship.stl`
- `Innards Alpha.SLDPRT`
- `Innards Beta.SLDPRT`
- `Innards Gamma.SLDPRT`
- `Spaceship Iota.SLDPRT`
- `Spaceship Iota.stl`
- `Spaceship Lambda.SLDPRT`
- `Spaceship Lambda.stl`
- `Spaceship Nu.eprt`
- `Wire Mesh for Vessle Construction.jpg`

The spelling in filenames is preserved from the archive, including `Ballon` and
`Vessle`.

## Repo State

No GitHub repo currently exists at:

- `tonykoop/weather-balloon-camera-vessel`

## Recommendation

Create a new private `weather-balloon-camera-vessel` repo for this packet.

Recommended initial structure:

```text
weather-balloon-camera-vessel/
  README.md
  cad/
    source-solidworks/
    stl/
    previews/
  docs/
    provenance.md
    recovery-inventory.md
```

Do not copy the 817MB asset packet into `claude-skills`. The correct next move
is a dedicated repo or Git LFS-aware staging decision.

Before public release, review the CAD and previews for:

- actual build/flight evidence versus concept-only CAD
- third-party camera payload assumptions
- safety/regulatory claims for high-altitude balloon launches
- whether the project connects to the drone/aerial-photography and Kickstarter
  archives as a separate portfolio story

## Verification Commands

```bash
gh issue view 55 -R tonykoop/claude-skills --json number,title,body,labels
qmd search "Weather Balloon Camera Vessel recover scaffold repo"
qmd search "weather balloon camera vessel"
rg -n "weather-balloon|Weather Balloon|camera vessel" /mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools/archive-recovery-copy-plan-2026-05-09.csv /mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools/logs/weather-balloon-camera-vessel.robocopy.log
sed -n '1,180p' /mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools/logs/weather-balloon-camera-vessel.robocopy.log
find /mnt/c/Users/Tony/Documents/GitHub -maxdepth 5 -type d -iname '*weather*balloon*'
find /mnt/c/Users/Tony/Documents/GitHub -maxdepth 6 -type f -iname '*Spaceship*Iota*'
find /mnt/c/Users/Tony/Documents/GitHub -maxdepth 6 -type f -iname '*Weather*Ballon*Camera*Ship*'
find /mnt/c/Users/Tony/Documents/GitHub/archive/_archive-recovery-staging/weather-balloon-camera-vessel/cad -maxdepth 1 -type f -printf '%f\n' | sort
find /mnt/c/Users/Tony/Documents/GitHub/archive/_archive-recovery-staging/weather-balloon-camera-vessel/cad -type f | wc -l
du -sh /mnt/c/Users/Tony/Documents/GitHub/archive/_archive-recovery-staging/weather-balloon-camera-vessel/cad
gh repo view tonykoop/weather-balloon-camera-vessel --json nameWithOwner,visibility,url,defaultBranchRef,description
```

## Assessment

#55 has a strong standalone asset packet and should graduate to its own repo,
but only through a deliberate large-asset workflow. This note records the
recovered CAD inventory and keeps `claude-skills` as metadata-only evidence.
