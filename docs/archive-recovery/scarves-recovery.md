# Scarves Archive Recovery

## Contract

- Issue: `tonykoop/claude-skills#56`
- Capture: commercial textile portfolio recovery for scarf inventories
- Scope: document the recovered archive evidence and recommend the repo home
- Asset policy: do not copy the 583 MB photo packet into `claude-skills`

## Archive Evidence

The archive inventory records the scarf collection under:

```text
D:\External Hard Drive Consolidation\Lacie Share with photos from 2014\Document Archive 3-3-18\Scarves
```

Relevant inventory rows from `archive/archive-inventory-2026-05-09.csv`:

| archive path | files | size MB | extensions |
| --- | ---: | ---: | --- |
| `Scarves` | 2 | 9.39 | `.jpg` |
| `Scarves\Christmas Scarves 2017` | 6 | 20.99 | `.jpg,.xlsx` |
| `Scarves\Christmas Scarves 2017\edited` | 5 | 19.38 | `.jpg` |
| `Scarves\For Sale` | 48 | 264.15 | `.jpg` |
| `Scarves\No Pocket - For Sale` | 12 | 64.28 | `.jpg` |
| `Scarves\Not FS` | 6 | 31.23 | `.jpg` |
| `Scarves\Not Yet Ready` | 33 | 172.55 | `.jpg` |

The copy plan entry is:

```text
id: scarves
priority: P2
source: D:\External Hard Drive Consolidation\Lacie Share with photos from 2014\Document Archive 3-3-18\Scarves
dest: C:\Users\Tony\Documents\GitHub\sewing\legacy\archive-2018\scarves
rationale: Commercial scarf portfolio folders and spreadsheets.
notes: 582MB dry-run result; could become textile/apparel repo after review.
```

The robocopy log at
`/mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools/logs/scarves.robocopy.log`
shows a successful copy on Saturday, May 9, 2026:

| metric | value |
| --- | ---: |
| directories copied | 7 |
| files copied | 112 |
| bytes copied | 581.98 MB |
| failures | 0 |

## Local Destination

The local checkout for `tonykoop/sewing` is:

```text
/mnt/c/Users/Tony/Documents/GitHub/fabrication/sewing
```

The recovered scarf packet is present at:

```text
/mnt/c/Users/Tony/Documents/GitHub/fabrication/sewing/legacy/archive-2018/scarves
```

Local inventory:

| metric | value |
| --- | ---: |
| files | 112 |
| disk usage | 583 MB |
| `.jpg` files | 111 |
| `.xlsx` files | 1 |

Top-level recovered folders:

- `Christmas Scarves 2017`
- `For Sale`
- `No Pocket - For Sale`
- `Not FS`
- `Not Yet Ready`

Representative files:

- `AAK_9810.JPG`
- `AAK_9814.JPG`
- `Christmas Scarves 2017/ADK_0192.JPG`
- `Christmas Scarves 2017/receipients.xlsx`
- `For Sale/Scarf-001-a.JPG`
- `For Sale/Scarf-001-b.JPG`
- `No Pocket - For Sale/Scarf-019-a.JPG`
- `Not FS/Scarf-017-a.JPG`
- `Not Yet Ready/Scarf-023-a.JPG`

## Repo State

`tonykoop/sewing` exists and is private. GitHub describes it as:

> Soft-goods craft archive focused on reversible scarves, practical sewing, and textile design process.

The local `sewing` checkout is clean on `main`. Its README already names
reversible scarves as the signature project and describes the design rule as
"party fabric on one side, business fabric on the other." The repo also has:

- `projects/pattern-index.md`, with `reversible-scarf-series` and
  `christmas-scarves-2017` entries.
- `projects/hero-photo-plan.md`, with archived scarf photo candidates and
  planned public-safe hero shots.
- `legacy/archive-2018/scarves/`, which now holds the recovered source packet.

`tonykoop/apparel` does not currently exist.

## Recommendation

Extend the existing private `sewing` repo rather than creating an `apparel`
umbrella now.

Reasons:

- The recovered packet is already copied into the `sewing` repo's legacy archive.
- The `sewing` README already frames scarves as the core through-line of the
  repo, not as a side project.
- `sewing/projects/pattern-index.md` already has scarf-specific entries that can
  be deepened from this packet.
- The branch would avoid creating a new umbrella repo around one already-homed
  textile collection.

Suggested follow-up inside `sewing`:

```text
sewing/
  legacy/
    archive-2018/
      scarves/
  projects/
    scarves/
      recovery-inventory.md
      commercial-categories.md
      public-gallery-selection.md
```

Keep `legacy/archive-2018/scarves/` as the lossless source archive. Add curated
metadata and public-safe selections under `projects/scarves/` rather than
renaming or flattening the original category folders.

## Public Release Review

Before any public gallery or generated showcase uses this packet, review:

- Whether `receipients.xlsx` contains private recipient information.
- Whether the sale-category labels (`For Sale`, `Not FS`, `Not Yet Ready`) should
  remain internal metadata or become public portfolio language.
- Whether all scarf images are Tony-owned photographs and free of identifiable
  people, private addresses, receipts, or unrelated background details.
- Whether the 583 MB archive should stay out of Git history or move through LFS
  before any future remote push.

## Verification Commands

Commands run for this recovery note:

```bash
qmd status
qmd search "Scarves commercial textile portfolio sewing apparel"
qmd search "Betabrand shacket sewing apparel umbrella scarves"
gh issue view 56 -R tonykoop/claude-skills --json number,title,body,labels
rg -n "Scarves|scarves" /mnt/c/Users/Tony/Documents/GitHub/_meta/archive-inventory-tools /mnt/c/Users/Tony/Documents/GitHub/archive
gh repo view tonykoop/sewing --json name,visibility,description,url
gh repo view tonykoop/apparel --json name,visibility,description,url
find /mnt/c/Users/Tony/Documents/GitHub/fabrication/sewing/legacy/archive-2018/scarves -type f | wc -l
du -sh /mnt/c/Users/Tony/Documents/GitHub/fabrication/sewing/legacy/archive-2018/scarves
git -C /mnt/c/Users/Tony/Documents/GitHub/fabrication/sewing status --short --branch
```

## Assessment

Issue #56 is archive-backed and already has a concrete private-repo home. Treat
the recovered scarf portfolio as a `sewing` project-deepening task, with the
commercial categories preserved as source evidence and only curated,
privacy-reviewed subsets promoted to public portfolio materials.
