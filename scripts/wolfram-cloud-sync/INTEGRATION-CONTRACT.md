# Integration contract: wolfram-cloud-sync ↔ explorer.html

This file is the schema and ordering contract between `wolfram-cloud-sync`
(writer) and the explorer.html generator inside `instrument-maker-v4`
(reader). If you change names or shapes here, change them on both sides.

## The bridge

`wolfram-cloud-sync` uploads `.wl` and `.nb` files to Wolfram Cloud, makes
them public-execute, captures their public URLs, and writes those URLs into
each per-instrument `capstone-manifest.json` under `engineering.wolfram[]`.
The explorer generator reads that block and emits one
`<div class="wolfram-embed-wrap">` per entry.

## Pipeline (run in order)

1. `python3 wolfram_inventory.py` — scan repos, write `manifest/wolfram_manifest.json`
2. `wolframscript -file wolfram_sync.wls -- manifest/wolfram_manifest.json` — upload
3. `wolframscript -file wolfram_publish.wls -- manifest/wolfram_manifest.json` — set permissions, capture URLs into `manifest/wolfram_embed_urls.json`
4. `python3 wolfram_emit_engineering_manifest.py --manifest manifest/wolfram_manifest.json --embed-urls manifest/wolfram_embed_urls.json --apply` — writeback to each `capstone-manifest.json`

Optional cleanup after a rename:

5. `wolframscript -file wolfram_orphans.wls -- manifest/wolfram_manifest.json --delete` — remove cloud objects whose names no longer match the manifest

## `engineering.wolfram[]` schema

A list of objects at `engineering.wolfram` in `capstone-manifest.json`. One
entry per uploaded Wolfram file in that repo.

```json
{
  "engineering": {
    "wolfram": [
      {
        "source_file": "wolfram/sambuca-acoustics-starter.wl",
        "cloud_path":  "GitHub-Inbox/sambuca__wolfram__sambuca-acoustics-starter.wl",
        "cloud_url":   "https://www.wolframcloud.com/obj/.../sambuca__wolfram__sambuca-acoustics-starter.wl",
        "permission":  "Public-Execute",
        "kind":        "acoustics-starter"
      }
    ]
  }
}
```

### Field meanings

| Field | Type | Description |
|---|---|---|
| `source_file` | string | Path within the repo, e.g. `wolfram/sambuca-acoustics-starter.wl`. Repo prefix stripped. |
| `cloud_path`  | string | The full path on Wolfram Cloud, e.g. `Musical_Instruments/strings/sambuca/sambuca-acoustics-starter.wl`. In categories mode (current default) the inventory's `cloud_prefix` is empty and `cloud_name` is the full path. |
| `cloud_url`   | string \| null | Public-executable URL. `null` when the file is `Private` (uploaded but not yet shared) or when publish has not run for that repo. |
| `permission`  | string | `Private` (uploaded, not publicly visible), `Public-Execute` (publish has run for this repo), `failed` (SetPermissions raised), `missing` (cloud object not found — sync didn't run or was interrupted), `would-publish` (dry-run output). The explorer should render `Private` entries as **grey-dot "Owner-only — not yet published"** so the user sees what exists without trying to embed a URL that doesn't exist. |
| `kind`        | string | `acoustics-starter` (any `*-starter.wl`), `geometry-model` (any `*-model.wl`), or `other`. |

### Other guarantees

- The list is in stable sort order (same as the manifest's row order).
- If a repo's existing `engineering` key is not an object, the script
  writes to `engineering_wolfram` at the root instead of clobbering.
- Existing keys under `engineering` are preserved; only `wolfram` is overwritten.
- Repos without a `capstone-manifest.json` (skill-source repos like
  `instrument-maker`, `claude-skills`, `WSS-2019`) are logged and skipped.

## Explorer wrapper-div contract

The explorer.html generator emits one `<div>` per entry with these data
attributes (which the JS handler reads to mount the iframe):

```html
<div class="wolfram-embed-wrap"
     data-cloud-url="https://www.wolframcloud.com/obj/.../sambuca__..."
     data-cloud-path="GitHub-Inbox/sambuca__wolfram__sambuca-acoustics-starter.wl"
     data-notebook-name="sambuca-acoustics-starter.wl"
     data-kind="acoustics-starter">
  ...
</div>
```

Don't rename these attributes without updating both the generator (in
`claude-skills/skills/instrument-maker/scripts/generate_site.py` or wherever
the explorer template lives) and any explorer JS that reads them.

## Naming convention edge case (post v4.4.5 rename)

Most starter files follow `{slug}-starter.wl` (e.g. `cajon-starter.wl`).
Files with a domain descriptor follow `{slug}-{descriptor}-starter.wl`
(e.g. `sambuca-acoustics-starter.wl`). Both are accepted by
`validate_packet.py`'s `*-starter.wl` glob. The cloud-name generator in
`wolfram_inventory.py` just walks the filesystem, so descriptor-bearing
names carry through to the flat-inbox cloud name unchanged:
`sambuca__wolfram__sambuca-acoustics-starter.wl`.

## What changed when (provenance)

- **v4.4.5 rename (2026-05-17):** `wolfram-starter.wl` → `{slug}-starter.wl`
  across 55 repos; `instrument-model.wl` → `{slug}-model.wl` across 9.
  Within-repo collisions resolved with subpath suffix.
- **2026-05-17 integration pieces:** Added `wolfram_publish.wls`,
  `wolfram_emit_engineering_manifest.py`, `wolfram_orphans.wls`,
  and this contract document.
