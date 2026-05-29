# Structured Shop Artifacts

Markdown narratives carry the craft reasoning. Structured artifacts
(CSV) carry the audit trail. A shop packet above a small complexity
threshold should produce both.

## When structured artifacts are required

Add structured CSV artifacts whenever **either** holds:

- The packet has more than five distinct parts (chair frame parts,
  laser tiles, machined components, etc.).
- The packet has more than five distinct go/no-go gates (stock
  receipt, dry-fit, bend, glue, load test, finish, etc.).

Below this threshold, the markdown narratives in the default packet
remain sufficient.

## Required structured files

| File | Purpose | Schema |
|---|---|---|
| `cut-list.csv` | Per-part stock list with rough and finished dimensions | `part_id,part_name,qty,rough_dimensions,finished_dimensions,material,operation_notes` |
| `validation.csv` | Auditable per-check log with target/tolerance/method | `check_id,check_name,target,tolerance,method,when_to_check,pass_fail,notes` |
| `cad-index.csv` | Recovered CAD/drawing archive triage before shop claims | `path,file_type,role,authority_status,revision_status,units_scale_status,stale_risk,next_review_action,notes` |
| `process-schedule.csv` | Step-by-step process timing and gates (rename to `bending-schedule.csv`, `welding-schedule.csv`, etc., as the work warrants) | `step_id,part,option,stock,prep,heat_or_glue_time,bend_or_clamp_window,fixture,release_time,go_no_go` |

Existing `bom.csv` retains its schema:
`item_id,category,description,qty,unit,unit_cost_usd,extended_usd,vendor_class,lead_time,notes`.

### Schema rules

- Header row must use exactly the documented column names, in order.
- Use `TBD` for unknown values; never invent.
- Quote any cell containing a comma.
- One row per part / per check / per step. No multi-row records.
- IDs (`part_id`, `check_id`, `step_id`) are strings; prefer
  `CHAIR-001`, `VAL-001`, `BEND-001` style so they sort and grep
  cleanly.
- For `cad-index.csv`, use `TBD` for unchecked units/scale or revision
  status. Use authority statuses such as `current`, `stale`, `visual_only`,
  `requires_export`, and `unknown`; do not promote `unknown` or
  `visual_only` rows into shop instructions.

## Optional sanity-check drawing

For any packet whose primary feature is curved (rocker arc, kayak
hull, bent rim, vault arch) include a parametric SVG side-elevation
or top-view that **visually proves** the dimensions in the narrative
are mutually consistent. The drawing does not need to be production
quality; it needs to catch dimension contradictions before stock is
cut.

Recommended toolchain (all WSL/Linux, no extra cost):

- Python 3 with stdlib only — generate `*.svg` from the dimension
  table.
- `rsvg-convert` (librsvg2-bin) — rasterize to PNG for clipboard
  use:

  ```bash
  rsvg-convert -w 1200 side-elevation.svg -o side-elevation.png
  ```

- `inkscape --export-type=png --export-filename=...` — alternative
  rasterizer with better text rendering.

Round 7 lane Cindy generated a side-elevation that surfaced a real
math bug in the generator on first render — proof of value.

## Validation gates

Two cheap checks the author should run before declaring the packet
ready.

### CSV column-count check

```bash
python3 - <<'EOF'
import csv, sys
schemas = {
  "cut-list.csv": ["part_id","part_name","qty","rough_dimensions",
                   "finished_dimensions","material","operation_notes"],
  "validation.csv": ["check_id","check_name","target","tolerance",
                     "method","when_to_check","pass_fail","notes"],
  "cad-index.csv": ["path","file_type","role","authority_status",
                    "revision_status","units_scale_status","stale_risk",
                    "next_review_action","notes"],
  "process-schedule.csv": ["step_id","part","option","stock","prep",
                           "heat_or_glue_time","bend_or_clamp_window",
                           "fixture","release_time","go_no_go"],
  "bom.csv": ["item_id","category","description","qty","unit",
              "unit_cost_usd","extended_usd","vendor_class",
              "lead_time","notes"],
}
ok = True
for name, cols in schemas.items():
    try:
        with open(name, newline="") as f:
            rows = list(csv.reader(f))
    except FileNotFoundError:
        continue
    if not rows:
        print(f"{name}: EMPTY"); ok = False; continue
    if rows[0] != cols:
        print(f"{name}: HEADER MISMATCH"); ok = False; continue
    bad = [(i+1, len(r)) for i,r in enumerate(rows[1:],1) if len(r) != len(cols)]
    if bad:
        print(f"{name}: COLUMN COUNT MISMATCH {bad[:3]}"); ok = False
    else:
        print(f"{name}: OK rows={len(rows)} cols={len(cols)}")
sys.exit(0 if ok else 1)
EOF
```

The repo provides this as `scripts/validate_packet.py --schemas-only
--packet <packet-dir>`.

### SVG render check

```bash
rsvg-convert -w 1200 side-elevation.svg -o side-elevation.png \
    && file side-elevation.png | grep -q PNG \
    && echo "OK"
```

If `rsvg-convert` rejects the SVG, the SVG has invalid markup and
will not display in browsers either.

## Steam-bending packet — required gate table

Steam bending is high-energy and failure-sensitive. Any
steam-bending packet must include the following checks in
`validation.csv`. This list is the floor, not the ceiling.

| check_id | check_name | target | when |
|---|---|---|---|
| VAL-MOIST | stock-moisture | 18–25% MC for solid bend | on stock arrival |
| VAL-GRAIN | stock-grain-runout | < 1:15 in bend zone, no knots | before milling |
| VAL-BOX-T | steam-box-temperature | ≥ 200 °F continuous through soak | every soak |
| VAL-STRAP | compression-strap-fit | strap end-blocks seated, stop-pins engaged | before each bend |
| VAL-WIN | working-window | blank in form within 60 sec of box opening | every bend |
| VAL-CRACK | breakage-threshold | no audible crack; no tension-face tear-out | during/after each bend |
| VAL-COOL | cooling-time | ≥ 24 h clamped (72 h preferred) at 65–75 °F, 35–55% RH | after each bend |
| VAL-OIL | oil-rag-disposal | rags spread flat outdoors or submerged in water in a metal can with lid | every finish session |

Rationale per check:

- **Moisture:** Kiln-dried oak below ~12% MC fractures on tight bends.
  Reject KD stock if the project spec is solid steam-bend.
- **Grain runout:** Cross-grain in a bend zone tears on the tension
  face within the first 5° of bend.
- **Steam-box temp:** Below 200 °F the lignin does not soften enough;
  the wood acts brittle.
- **Strap fit:** A compression strap reverses the neutral axis. End-
  block slip during clamp-up sends the blank as a projectile.
- **Working window:** Wood cools fast outside the box; past ~60 sec
  the working stress climbs sharply and fracture risk spikes.
- **Breakage threshold:** Audible crack means fibers parted; the
  blank is scrap. Use a spare; do not re-bend a cracked blank.
- **Cooling time:** Set takes hours; releasing warm guarantees
  springback past tolerance.
- **Oil rag disposal:** Boiled-linseed-oil rags self-heat and
  ignite. This is a genuine shop-fire vector; gate on it explicitly.

## Example — Round 7 steam-bent rocking chair

Reference artifacts that meet this schema (TwinGrid Round 7 lane
Cindy):

- `/tmp/twingrid-r7-claude-cindy-rocking-chair/v2-cut-list.csv`
  (28 rows; chair + jigs + test pieces)
- `/tmp/twingrid-r7-claude-cindy-rocking-chair/v2-bending-schedule.csv`
  (10 steps; test slats, three final bends, joinery coupon, three
  lamination fallbacks)
- `/tmp/twingrid-r7-claude-cindy-rocking-chair/v2-validation.csv`
  (27 checks; covers stock receipt through finish handoff, includes
  all eight steam-bending gates above plus 250 lb static load test)
- `/tmp/twingrid-r7-claude-cindy-rocking-chair/v2-side-elevation.py`
  + `.svg` + `.png` — parametric sanity check that caught a real
  geometry bug during rendering
- `/tmp/twingrid-r7-codex-cindy-steam-bent-rocking-chair/v2-validation.csv`
  — Codex side B's complementary view

Use these as the worked example when authoring a new steam-bending
packet.

## Cross-references

- `references/repeatable-shop-packets.md` — when to add structured
  artifacts to the default packet.
- `references/recovered-cad-archive-index.md` — how to use `cad-index.csv`
  before treating recovered CAD/drawings as fabrication authority.
- `references/safety-checklist.md` — broader safety sweep; the
  steam-bending gate table above is a focused subset.
- `scripts/validate_packet.py` — runs the CSV header-and-column check
  against a packet directory. Pass `--schemas-only --packet <dir>` for the
  CSV-only check, or include `validation.csv` / `cut-list.csv` in a
  full tier-2 packet to have them validated as part of completeness.
