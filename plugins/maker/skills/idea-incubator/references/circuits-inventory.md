# Circuits Inventory - functional primitives across repos + vault

Story #248 of the Cross-Pollination Engine (epic #236). This defines a
portfolio-wide index of reusable **functional primitives** - "circuits" - where
each entry is a solved subassembly with its `functions:` tags, source
repo/issue, maturity, and reuse notes.

The name borrows from electronics: a known-good circuit you drop into a new
board without re-deriving it. A mechanical detent, a tensioning block, a
cable-routing clip - once solved, each becomes a circuit the rest of the
portfolio can reuse. This index is the catalog of those circuits; the
Cross-Pollination Agent (#247) reads it to prefer proven sources, and the
builder script [`scripts/build_circuits_inventory.py`](../scripts/build_circuits_inventory.py)
keeps it current.

## Index schema

Each entry is one row in the table below (human view) and one object in the
generated `circuits-inventory.json` (machine view). Fields:

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable slug, `<domain>-<function>-<variant>` per #245 naming. |
| `name` | yes | Human-readable name of the primitive. |
| `functions` | yes | Canonical `functions:` tokens it provides (#243). |
| `interfaces` | no | `interfaces:` tokens it exposes (#243 / #245). |
| `materials` | no | Coarse material tokens. |
| `source` | yes | `owner/repo#issue` or vault note path where it was solved. |
| `maturity` | yes | `concept | sketch | proto | built | shipped`. |
| `reuse-notes` | yes | One line: how to reuse, gotchas, what to re-tune. |
| `updated` | yes | ISO date the entry was last verified. |

## The inventory

Keep this table sorted by `functions` then `maturity`. The generator can
regenerate it; hand-edits are allowed but should be re-run through the script so
the JSON stays in sync.

| id | name | functions | interfaces | source | maturity | reuse-notes | updated |
|---|---|---|---|---|---|---|---|
| `maker-index-detent-8mm` | Spring-detent telescoping leg | `index-detent`, `slide`, `lock` | `shaft:8mm-round`, `fastener:m5` | `tonykoop/sambuca#88` | built | Reuse detent ball+spring; re-tune spring rate for lighter loads. | 2026-06-16 |
| `instrument-tension-brass` | Removable string-tension anchor block | `tension`, `tune`, `mount` | `mount:hole-pattern-43x43`, `fastener:1/4-20` | `tonykoop/brian-boru-harp-replica#12` | proto | Swap brass pin count per string set; verify pull-through load. | 2026-06-16 |
| `maker-route-cable-clip` | Snap-in strain-relief cable clip | `route-cable` | `mount:t-slot-2020` | `tonykoop/conga#41` | built | Print in PETG; clearance-loose snap; one size per cable OD. | 2026-06-16 |

(The three rows above are seed examples. The generator replaces/extends them
from live tagged ideas.)

## How it is kept current

1. **Source of truth is the tags.** A primitive qualifies for the inventory
   when an idea is tagged `maturity: built` (or `shipped`) and carries a
   `solved-in:` / `source` link. The schema (#243) is upstream of this index.
2. **Generated, then reviewed.** Run
   [`scripts/build_circuits_inventory.py`](../scripts/build_circuits_inventory.py)
   (dry-run by default) to walk the repos + vault, extract qualifying entries,
   and emit `circuits-inventory.json` plus a refreshed markdown table. A human
   reviews `reuse-notes` for accuracy before committing.
3. **Cadence.** Regenerate when a primitive reaches `built`, or on the same
   cadence as the Cross-Pollination Agent run (#247), whichever is sooner.
4. **Stale check.** Entries whose `updated` date is older than the source
   issue's last activity should be re-verified; the generator flags these.
5. **De-dup by id.** Two ideas that solve the same primitive collapse to one
   entry (the most mature source wins); the others become `reuses:` links.

## Relationship to other epic pieces

- Built from the tags defined in #243.
- Entries reference the interface tokens standardized in #245.
- Read by the Cross-Pollination Agent (#247) to prefer proven sources.
- Surfaced for humans by the Shared Subassemblies MOC (#244, query 5).
