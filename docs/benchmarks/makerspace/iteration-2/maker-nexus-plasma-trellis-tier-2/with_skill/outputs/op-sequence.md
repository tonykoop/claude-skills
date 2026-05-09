# Operation Sequence — Climbing-Vine Plasma Trellis

All shop operations cite **Maker Nexus' metalshop-area** (per the
seed profile, plasma lives under metalshop-area until per-machine
entries are added). Tony is cleared on `metalshop-cert`, which
grants access to metalshop-area.

| # | Op | Area / Tool | Fixturing | Time | Notes |
|---|---|---|---|---|---|
| 0 | Pre-shop prep: confirm CAM file, check kerf-test plan, gather PPE, confirm sheet on order | Home / shop bench | — | 1 hr | See `cut-path-strategy.md`. |
| 1 | Receive & inspect 1/4" sheet; check flatness with straightedge across diagonals | metalshop-area | Steel cart | 0.25 hr | Reject if bow exceeds 1/16 in over 8 ft; ask vendor for replacement. |
| 2 | Wipe sheet with acetone, remove rust-preventive oil from cut zone | metalshop-area | Bench | 0.25 hr | Plasma cuts through P&O fine, but oil under the torch can flare. |
| 3 | Load sheet onto plasma table; secure with magnetic hold-downs at four corners + two midpoints | metalshop-area (plasma table) | Magnetic hold-downs, table slats | 0.5 hr | Square the long edge to the X-axis with a machinist's square. |
| 4 | **Kerf-test cut**: run KT1 coupon program, measure actual kerf, update CAM if delta > 0.010 in, re-export | metalshop-area (plasma table + caliper) | — | 0.5 hr | Do NOT skip. See `cut-path-strategy.md` §kerf compensation. |
| 5 | **Pierce-test cut**: run P1 program with three test pierces using planned lead-in geometry | metalshop-area (plasma table) | — | 0.25 hr | Verify pierces are inside the scrap, not on the part edge. |
| 6 | **Production cut**: run trellis program. Internal cutouts first, perimeter last. | metalshop-area (plasma table) | Magnetic hold-downs | 1.5 hr | Stay at the table. Pause after every leaf finishes to confirm the part hasn't shifted. |
| 7 | Let the part cool on the table (5 min minimum) before lifting | metalshop-area | — | 0.1 hr | Edges will be 400-600 deg F immediately after cut. Welder gloves. |
| 8 | Knock dross off bottom edge with a chipping hammer, then flap-disc the top edge | metalshop-area (angle grinder, chipping hammer) | Welding table + clamps | 1 hr | See `cut-path-strategy.md` §dross management. |
| 9 | Wire-wheel mill scale off both faces | metalshop-area (angle grinder + knot-wire wheel) | Welding table | 1 hr | Required for powder-coat adhesion (sandblaster at coater finishes). |
| 10 | MIG-tack the two spikes to the back face of the bottom rail | metalshop-area (MIG welder) | C-clamps, square | 0.5 hr | Spikes are integral to the silhouette in the cut plan; this op is only needed if the cut produced separate spike pieces. With the vine-trellis-as-one-piece design, spikes are already attached — verify before welding. |
| 11 | Final dimension check & flatness check | metalshop-area | Tape, framing square, flat reference | 0.25 hr | Document deltas in `validation.csv`. |
| 12 | Acetone wipe again; bag the part for transport | metalshop-area | Plastic sheet, blue tape | 0.25 hr | Don't touch bare metal with bare hands after the wipe — body oil resists powder coat. |
| 13 | Drop off at powder coater (sandblast prep + RAL 9005 texture matte black) | Off-site | Vehicle | 1 hr round trip | See `sourcing.csv` for vendor. |
| 14 | Pick up coated part; inspect for runs, voids, contamination | Off-site → home | — | 1 hr round trip | If defects > spec, request rework before paying. |
| 15 | Install: drive spikes into prepared garden bed, plumb with a level | On-site | Sledge or post pounder, level | 0.5 hr | Don't strike the powder-coated rail directly — use a wood buffer. |

**Total in-shop time:** ~7 hours (one weekend day).
**Total project clock time:** ~10 days including powder-coat turnaround.

## Required certifications

- **shop-safety-cert** — prerequisite (Shop Safety Orientation).
- **metalshop-cert** — required for metalshop-area, which covers
  the plasma table on the seed profile. Tony has this. (cleared)

If a future profile update splits plasma into its own
`plasma-area` with a `plasma-cert`, this op-sequence should be
re-checked.
