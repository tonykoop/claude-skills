# wolfram-cloud-sync

Scan a folder of Git repos for Wolfram Language files (`.nb`, `.wl`, `.wls`,
`.cdf`, `.wxf`, and Wolfram-flavoured `.m` files), then push them to a flat
Wolfram Cloud inbox so you can open and interact with them in
[wolframcloud.com](https://www.wolframcloud.com/).

Built for the case where you have many repos (here: ~110 instrument-maker repos
under `C:\Users\Tony\Documents\GitHub`), most carrying a small `wolfram-starter.wl`
or `wolfram/instrument-model.wl`, and you want them all visible in the cloud
without installing desktop Mathematica.

## What you get

A four-step pipeline (plus an optional cleanup step), deliberately
separated so each can be reviewed before the next runs:

| Step | Script | Runtime | Output |
|---|---|---|---|
| 1. Inventory | `wolfram_inventory.py` | Python 3 | `manifest/wolfram_manifest.{csv,json}` (category-aware cloud paths via `categories.yaml`) |
| 2. Sync (upload) | `wolfram_sync.wls` | wolframscript | CloudObjects under the manifest's `cloud_prefix` (or the prefix encoded in each `cloud_name`) |
| 3. Publish | `wolfram_publish.wls` | wolframscript | opt-in via `--repos`; sets `Public→Execute` and captures URLs only for the listed repos → `manifest/wolfram_embed_urls.json`. Default (no `--repos`): everything stays Private. |
| 4. Emit | `wolfram_emit_engineering_manifest.py` | Python 3 | writes `engineering.wolfram[]` into each repo's `capstone-manifest.json`; entries carry one of `Private` / `Public-Execute` / `failed` / `missing` |
| optional. Orphans | `wolfram_orphans.wls` | wolframscript | lists/deletes cloud objects no longer in the manifest |

## Cloud layout (since 2026-05-17)

`categories.yaml` defines the cloud folder structure. Each repo is
assigned a Hornbostel-Sachs-ish category (`strings`, `woodwinds`,
`percussion`, `idiophones`), and `wolfram_inventory.py` emits cloud paths
in the shape:

```
Musical_Instruments/<category>/<repo>/<filename>
```

For example:

| Local path | Cloud path |
|---|---|
| `cajon/cajon-starter.wl` | `Musical_Instruments/percussion/cajon/cajon-starter.wl` |
| `sambuca/wolfram/sambuca-acoustics-starter.wl` | `Musical_Instruments/strings/sambuca/sambuca-acoustics-starter.wl` |
| `WSS-2019/Final Project/Drafts/FinalProjectDraft1.nb` | `WSS-2019/Final Project/Drafts/FinalProjectDraft1.nb` (preserved as-is) |

Repos not listed in `categories.yaml` go to `Musical_Instruments/unsorted/<repo>/`.
Repos listed under `skip:` (currently `claude-skills`, `wolfram-cloud-sync`)
are dropped from the manifest entirely.

To force the old flat-inbox layout (`<repo>__<path>__<filename>` under
`GitHub-Inbox/`), pass `--no-categories` to `wolfram_inventory.py`.

The post-upload steps (publish + emit) close the loop with the
`explorer.html` generator inside `instrument-maker-v4` — see
`INTEGRATION-CONTRACT.md` for the schema and the wrapper-div attributes.

Also in this folder:

- `rename_starters.py` — one-shot tool used in the v4.4.5
  `wolfram-starter.wl` → `{slug}-starter.wl` rename pass.
- `fix_starter_refs.py` — second-pass path-aware reference fixer that
  rewrites pointers to renamed files inside `README.md`, `design.md`,
  `capstone-manifest.json`, etc.

## Setup (one-time)

1. Install the free [Wolfram Engine for Linux](https://www.wolfram.com/engine/)
   or any wolframscript-bearing distribution. You already have this.
2. Authenticate wolframscript against your Wolfram Cloud account:
   ```
   wolframscript -authenticate
   ```
   (Opens a browser. Once done, future scripts are silent.)

## Workflow

### Step 1 — inventory

From this folder:

```
python3 wolfram_inventory.py --root "C:\Users\Tony\Documents\GitHub" --out manifest
```

This walks the tree, skipping `.git`, `node_modules`, `_archive*`,
`_twingrid_archives`, `_worktrees`, and `_ip-triage`. For `.m` files it
sniffs the first 8 KB and only keeps the ones that look like Wolfram
(`BeginPackage[`, `(* :Title:`, etc.) — your repos currently contain zero
`.m` files, so this is just future-proofing.

Output:

```
manifest/wolfram_manifest.csv   <- spreadsheet-friendly
manifest/wolfram_manifest.json  <- consumed by wolfram_sync.wls
```

Each row has `repo`, `rel_path`, `abs_path`, `ext`, `size_bytes`, `mtime_iso`,
`sha256_16`, and a precomputed `cloud_name`. Open the CSV in Excel, prune
rows you don't want synced, save back over the JSON if you like — or just
keep everything.

### Step 2 — review

Open the CSV. You'll see entries like:

```
cajon,cajon/wolfram-starter.wl,wl,...,cajon__wolfram-starter.wl
WSS-2019,WSS-2019/Final Project/Drafts/FinalProjectDraft1.nb,nb,...,WSS-2019__Final Project__Drafts__FinalProjectDraft1.nb
```

The `cloud_name` is the flat-inbox name. Path separators become `__` so the
mapping is reversible:

```
WSS-2019__Final Project__Drafts__FinalProjectDraft1.nb
   ^^^^^^^^                                  ^^^^^^^^^^^^^^^^^^^^
   repo               subfolders            filename
```

Splitting any cloud filename on `__` recovers the original path.

### Step 3 — sync

```
wolframscript -file wolfram_sync.wls -- manifest/wolfram_manifest.json
```

Optional positional arg: a different cloud prefix (defaults to `GitHub-Inbox`,
or whatever the manifest specifies).

```
wolframscript -file wolfram_sync.wls -- manifest/wolfram_manifest.json My-Inbox
```

Optional flag:

```
wolframscript -file wolfram_sync.wls -- manifest/wolfram_manifest.json --dry-run
```

The sync is idempotent on byte count: re-running it skips files whose cloud
copy is already the same size as the local one. Edited files get re-uploaded.

When it finishes you'll see your files in Wolfram Cloud under
`Home / GitHub-Inbox / *`. `.nb` files open as interactive notebooks; `.wl`
files open in the text editor and can be evaluated with `Get` or by opening
them as a notebook.

### Step 4 — publish (permissions + embed URLs)

**Safer default: this script publishes nothing unless you opt in with
`--repos`.** Without a `--repos` flag, every manifest entry is written as
`"permission": "Private", "cloud_url": null`. With `--repos`, only the
listed repos get `SetPermissions[obj, "Public" -> "Execute"]` (so anonymous
viewers can interact with `Manipulate[]`) and have their public URLs
captured. Everything else stays private.

```
# Publish nothing publicly yet — just record the upload state:
wolframscript -file wolfram_publish.wls -- manifest/wolfram_manifest.json

# Publish a controlled subset:
wolframscript -file wolfram_publish.wls -- manifest/wolfram_manifest.json --repos sambuca,kora

# Preview without making any changes:
wolframscript -file wolfram_publish.wls -- manifest/wolfram_manifest.json --repos sambuca --dry-run
```

Writes `manifest/wolfram_embed_urls.json` either way.

### Step 5 — write the engineering contract into each repo

```
python3 wolfram_emit_engineering_manifest.py \
  --manifest manifest/wolfram_manifest.json \
  --embed-urls manifest/wolfram_embed_urls.json \
  --apply
```

Reads the embed-URL map and writes the `engineering.wolfram[]` block into
each per-instrument `capstone-manifest.json`. This is the contract the
`explorer.html` generator (inside `instrument-maker-v4`) reads to emit one
live embed per Wolfram notebook. Schema in
[`INTEGRATION-CONTRACT.md`](INTEGRATION-CONTRACT.md).

### Cleanup (optional) — delete orphan cloud objects

After a rename pass, the old cloud-object names are dangling. List them
or delete them:

```
wolframscript -file wolfram_orphans.wls -- manifest/wolfram_manifest.json          # list
wolframscript -file wolfram_orphans.wls -- manifest/wolfram_manifest.json --delete # delete
```

## What was found on the current scan (2026-05-17)

```
Total: 105 files, ~79 MB
By extension: .wl 90, .nb 15
Top sources:
  29  instrument-maker (build-packets/* and skill templates)
  14  WSS-2019         (your 2019 Wolfram Summer School work — ~75 MB of it)
  62  per-instrument repos
```

**v4.4.5 rename (2026-05-17):** the per-instrument starter scaffolds were
renamed from the shared basename `wolfram-starter.wl` to a unique
`{instrument}-starter.wl` (e.g. `cajon-starter.wl`, `marimba-starter.wl`).
The `instrument-model.wl` files were similarly renamed to
`{slug}-model.wl`. The `claude-skills/skills/instrument-maker/` v4.4.5 skill
emits the new names going forward; its validators accept either form for
backward-compat with older packets. See `rename_starters.py` and
`fix_starter_refs.py` in this folder for the tooling.

**Naming edge case** — files with a domain descriptor follow
`{slug}-{descriptor}-starter.wl` (e.g. `sambuca/wolfram/sambuca-acoustics-starter.wl`).
The v4.4.5 rename only matched literal `wolfram-starter.wl` and
`instrument-model.wl`, so descriptor-bearing files were correctly left
alone. The validator's `*-starter.wl` glob accepts both patterns, and the
cloud-name generator just walks the filesystem so descriptor names carry
through unchanged.

The big files are the WSS-2019 notebooks with embedded data (the 49 MB
`ATripToWork-new.nb` is the biggest). They'll upload, just slowly the first
time. If you'd rather skip them, prune those rows from the CSV before sync.

## Reversing the flat naming

Once a notebook is open in Wolfram Cloud, the file name encodes its origin.
If you want to script the reverse:

```wolfram
parts = StringSplit["WSS-2019__Final Project__Drafts__FinalProjectDraft1.nb", "__"];
repo = First[parts];
relPath = FileNameJoin[Rest[parts]];
```

## Why not mirror the folder tree?

You picked flat-inbox-with-tags during setup. Trade-off: easier to search
("show me everything with `wolfram-starter`"), harder to browse hierarchically.
If you change your mind later, regenerate `cloud_name` in
`wolfram_inventory.py` — there's a single `cloud_name(rel_path)` function to
edit; mirroring the tree is just `rel_path.as_posix()`.

---

## 2026-05-30 — reorg-aware update

The 2026-05-25 GitHub folder reorg moved every instrument repo under
`instruments/<family>/<repo>/` (plus `habitat/`, `fabrication/`, `_meta/`).
The pipeline was updated so `repo` and cloud `category` derive correctly from
the nested layout instead of the old flat `<repo>/` assumption:

- **`wolfram_inventory.py`** — new `path_repo_family()` + `FAMILY_TO_CATEGORY`
  map (`woodwind→woodwinds`, new `brass` category, etc.); derives `repo` from
  `instruments/<family>/<repo>/`; auto-categorizes by family dir when a repo
  isn't explicitly listed in `categories.yaml`; skips the reorg `archive/` dir
  (WSS-2019 lives there now) and this tooling folder; prints a per-category
  breakdown. Result: all ~110 instruments categorize without hand-listing each.
- **`rename_starters.py`** — same reorg-aware slug derivation (was producing
  `instruments-…` collisions).
- **`fix_starter_refs.py`** — unchanged (already path-relative / reorg-safe);
  run it **per-repo** (`--root <repo>`) to avoid walking up into `/mnt/c`.

Run order to refresh after adding/renaming instruments:
`inventory → (optional rename + per-repo fix_starter_refs) → sync → publish → emit`.
