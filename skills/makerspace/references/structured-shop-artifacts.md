# Structured Shop Artifacts

Use this reference when a makerspace packet needs auditable shop-floor
files rather than prose-only instructions. It grew out of the Round 7
Cindy steam-bent rocking-chair A/B pass, where the best combined result
paired craft judgment with machine-checkable CSVs and a visual sanity
check.

## When to Add These Files

Add structured artifacts when the project has any of these traits:

- repeated parts, paired parts, or stock optimization;
- steam bending, laminations, cure schedules, heat schedules, or other
  timing-sensitive processes;
- human-load objects such as chairs, stools, ladders, swings, and benches;
- safety-critical fixtures, jigs, or workholding;
- a packet that another maker must validate without the original author.

## Minimum Schemas

These are minimum columns. Add project-specific columns after them, but do
not rename the required columns unless you also explain the mapping in the
packet README.

### `cut-list.csv`

```csv
part_id,part_name,qty,material,stock_id,length_in,width_in,thickness_in,grain_dir,kerf_in,notes
p001,runner blank,2,white oak,b001,48,1.75,1.25,length,0.0625,leave long for springback trim
```

Use for stock planning and repeated parts. Include kerf even when cutting
by hand; write `0` only when kerf is genuinely irrelevant.

### `validation.csv`

```csv
check_id,check_name,target,tolerance,method,when_to_check,pass_fail,notes
v001,runner pair symmetry,left/right runners match template,+/- 1/16 in,nest both on form,before trimming,pending,
```

Every row needs a measurable method and a clear `when_to_check`.
`pass_fail` starts as `pending`; the maker fills in `pass` or `fail`.

### `process-schedule.csv`

```csv
step_id,part,process,stock,prep,process_time,working_window,fixture,release_time,go_no_go
p001,runner,steam bend,1.25 x 1.75 x 48 in oak,compression strap fitted,75-90 min steam,clamp within 60 sec,rocker form,24-72 hr clamped,no split/check/twist
```

Use this generic schedule for heat, glue, cure, soak, pressing, casting,
or other time-sensitive work.

### `bending-schedule.csv`

```csv
step_id,part,option,stock,prep,heat_or_glue_time,bend_or_clamp_window,fixture,release_time,go_no_go
BEND-001,runner coupon,solid steam,1.25 x 1.75 x 24 in straight-grain oak,round arrises and fit strap,75-90 min steam,transfer and clamp within 60 sec,rocker form with compression strap,inspect after 24 hr,no split/check; twist <= 1/8 in
```

Use `bending-schedule.csv` instead of the generic schedule when bending
is central to the packet. It should include test coupons before final
parts whenever stock, radius, moisture, or operator speed is uncertain.

## Go/No-Go Gate Table

Every packet with a custom jig, bending form, or safety-sensitive process
should include a go/no-go gate table in `fabrication-plan.md` or
`op-sequence.md`:

| Stage | Check | Pass criteria | If fail |
| --- | --- | --- | --- |
| Stock arrival | Moisture and grain | 18-25% MC for solid bends; runout acceptable | Reject, reorder, or switch to lamination |
| Steam box | Temperature | Holds >= 200 F through soak | Add insulation or increase boiler output |
| Bend | Visual and sound | No crack, split, strap slip, or twist beyond tolerance | Scrap part and use spare/test new schedule |

## Validation Commands

Run the repo-local verifier when the packet follows the tiered build
packet shape:

```bash
python3 skills/makerspace/scripts/validate_packet.py --packet <packet> --tier 2 --space home-shop-default
```

For ad hoc packets that are not in the tiered shape, at minimum parse the
CSV files:

```bash
python3 -c "import csv,pathlib; [list(csv.reader(p.open(newline=''))) for p in pathlib.Path('<packet>').glob('*.csv')]"
```

When a packet includes SVG sanity drawings, rasterize at least one view:

```bash
rsvg-convert <packet>/v2-side-elevation.svg -o <packet>/v2-side-elevation.png
convert <packet>/v2-side-elevation.png -format '%m %wx%h' info:
```

If `rsvg-convert` is unavailable, use Inkscape:

```bash
inkscape <packet>/v2-side-elevation.svg --export-type=png --export-filename=<packet>/v2-side-elevation.png
```

## Steam-Bending Required Gates

Steam-bending packets must explicitly cover:

- stock moisture content and grain-runout acceptance;
- compression strap or equivalent anti-fracture strategy;
- transfer/working window from steam box to form;
- breakage threshold such as crack, split, tear-out, twist, strap slip, or
  springback mismatch;
- oil-rag/fire checks when the finish plan uses oil, wax, solvent, or
  other combustible finishing materials.

## Human-Load Objects

For chairs, stools, ladders, swings, benches, and similar body-supporting
projects, add validation rows for:

- intended sitter/load range;
- ergonomic or stance mockup;
- static load test;
- dynamic/use-cycle test;
- joint movement check;
- finish and touch-point safety.

## Round 7 Rocking-Chair Evidence

Use these local artifacts as examples when available:

- `/tmp/twingrid-r7-claude-cindy-rocking-chair/v2-cut-list.csv`
- `/tmp/twingrid-r7-claude-cindy-rocking-chair/v2-bending-schedule.csv`
- `/tmp/twingrid-r7-claude-cindy-rocking-chair/v2-validation.csv`
- `/tmp/twingrid-r7-codex-cindy-steam-bent-rocking-chair/v2-validation.csv`
- `/tmp/twingrid-r7-codex-cindy-steam-bent-rocking-chair/v2-side-elevation.svg`

