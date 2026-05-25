# Build packet structure

A build packet is the folder that holds everything about one project.
This doc is the canonical spec for what's in it, file by file.

## Folder layout

```
<project-slug>/
├── README.md              # Project front door (Tier 2+)
├── design.md              # Parametric design (Tier 1+)
├── bom.csv                # Bill of materials (Tier 1+)
├── cut-list.csv           # Stock plan (Tier 1+)
├── op-sequence.md         # Manufacturing sequence (Tier 1+)
├── safety-notes.md        # Material/tool/cert risks (Tier 1+)
├── sourcing.csv           # Vendors, SKUs, lead times (Tier 2+)
├── validation.csv         # How to verify (Tier 2+)
├── assembly-manual.md     # Step-by-step build (Tier 2+)
├── risks.md               # Failure modes + tests (Tier 2+)
├── photo-shotlist.md      # Photos to take (Tier 3+)
├── drawings/              # Dimensioned drawings (Tier 2+)
│   ├── plan-view.svg
│   ├── front-view.svg
│   └── section-A.svg
├── images/                # Process and finished photos
│   └── hero.jpg           # Placeholder OK at first
├── cad/                   # Native CAD files (optional)
├── cnc/                   # G-code, CAM files (optional)
├── data/                  # Measurements, test data, calibrations
├── deck.pptx              # Capstone deck (Tier 3)
├── print-packet.pdf       # Printable shop packet (Tier 3)
└── site/                  # Build-log site (Tier 3)
    └── index.html
```

`drawings/`, `images/`, `cad/`, `cnc/`, `data/` exist as placeholders
even when empty so the user has somewhere to drop files later.

## File-by-file spec

### `design.md` (parametric)

The source of truth for *what we're making*. Every dimension cited
elsewhere in the packet traces back here.

Required structure:

```markdown
# <project name>

## Parameters
| Name | Symbol | Value | Unit | Source |
|------|--------|-------|------|--------|
| Length | L | 18 | in | input |
| Width | W | 6 | in | input |
| Stock thickness | t | 0.25 | in | input |
| Letter height | h | L * 0.4 | in | derived |

## Critical dimensions
- L = 18 in (input)
- W = 6 in (input)
- Outer radius (corner) = 0.25 in (input)

## Derived dimensions
- Letter height h = 0.4 × L = 7.2 in
- Border = (W - h) / 2 = -0.6 in   ← FAIL: see Open questions

## Open questions
- Border calculation comes out negative — need to revisit letter
  height or stock width.

## Notes
- Sized to fit a 4"×4" mailbox post above the door.
```

Use *formulas* not values where dimensions derive from inputs.
"Derived = 0.4 × L" beats "Derived = 7.2" because changing L
auto-updates the design.

If the project naturally lives in a spreadsheet (lots of derived
dimensions, families of sizes, parameter sweeps), use a `design.xlsx`
instead and let `design.md` summarize. The verifier accepts either.

### `bom.csv`

```
item_id, item_name, qty, unit, vendor, sku, unit_cost_usd, line_cost_usd, lead_time_days, notes
b001, "Baltic birch plywood, ¼\" 60×60 sheet", 1, sheet, MacBeath, BB14-6060, 35.00, 35.00, 0, "stock for sign + scrap"
b002, Titebond III wood glue, 1, 8oz bottle, Amazon, B000A11LSA, 9.50, 9.50, 2, ""
b003, Polyurethane satin spray, 1, can, Home Depot, 100133012, 8.00, 8.00, 0, "exterior"
b004, "#8 × 1¼\" wood screws, 100ct", 1, box, Home Depot, 204321712, 12.00, 12.00, 0, "for mounting"
```

Computed columns: `line_cost_usd = qty × unit_cost_usd`. The verifier
recomputes and flags mismatches.

`unit_cost_usd = TBD` is acceptable when the price hasn't been
verified — better than a guess.

### `cut-list.csv`

```
part_id, part_name, qty, material, stock_id, length_in, width_in, thickness_in, grain_dir, kerf_in, notes
p001, sign body, 1, baltic-birch-quarter, b001, 18, 6, 0.25, length, 0.0625, "leave 0.25 trim each edge"
p002, mounting cleat, 2, baltic-birch-quarter, b001, 6, 0.75, 0.25, length, 0.0625, "from sign body offcut"
p003, spacer block, 4, baltic-birch-quarter, b001, 1, 1, 0.25, length, 0.0625, "from offcut"
```

Group rows by `stock_id` to verify they fit. Include kerf in the
math.

### `op-sequence.md`

See `agents/specialists/shop-planner.md` for the format. Briefly:
ordered ops, each with tool, fixture, tooling, time estimate, and a
go/no-go check.

### `safety-notes.md` (Tier 1)

Short doc — the safety stuff a maker actually needs *for this build*,
not the generic shop policy. Section headings:

```markdown
# Safety notes — <project>
## PPE for this build
## Tool-specific risks
## Material-specific risks
## Process-specific risks
## Emergency / fire / fume notes
```

Three-to-five bullets per section is plenty. If you find yourself
writing a wall of text, it belongs in `risks.md` (Tier 2) instead.

### `sourcing.csv` (Tier 2)

Detailed vendor list — extends `bom.csv` with vendor URL, RFQ status,
shipping cost, alternate vendors.

```
item_id, primary_vendor, primary_url, primary_unit_cost_usd, alt_vendor, alt_url, alt_unit_cost_usd, lead_time_days, shipping_usd, rfq_sent, rfq_quoted, notes
b001, MacBeath, https://macbeath.com/baltic-birch, 35.00, Rockler, https://rockler.com/...60-60, 42.00, 0, 0, false, false, ""
```

### `validation.csv` (Tier 2)

How to verify the build matches the design.

```
check_id, check_name, target, tolerance, method, when_to_check, pass_fail, notes
v001, overall length, 18 in, ±1/32 in, "tape measure across longest face", after CNC, pending, ""
v002, letter relief depth, 0.125 in, ±0.005 in, "depth gauge", after CNC, pending, ""
v003, finish coverage, "no bare spots", n/a, "raking light inspection", after final coat, pending, ""
```

`pass_fail` starts at `pending` and the maker fills in `pass`/`fail`
during/after the build. Old runs become a maintenance log.

### `assembly-manual.md` (Tier 2)

Step-by-step build. One step per heading. Photos as placeholders are
fine; the photo-shotlist tells the user what to capture.

```markdown
# Assembly manual — <project>

## Estimated total time: <hh:mm>
## Tools needed: <list>

### Step 1 — <verb> <part>
- What you're doing: <one sentence>
- Tool: <tool>
- Time: <minutes>
- Photo placeholder: `images/step-01-<slug>.jpg`
- Notes / gotchas: <anything to watch for>

### Step 2 — ...
```

### `risks.md` (Tier 2)

See `agents/specialists/red-team.md`. Severity-grouped, every risk
has a *test*.

### `photo-shotlist.md` (Tier 3)

A list of photos the maker should capture, with composition notes.
Saves the "wait, I forgot to photograph that step" failure mode.

```markdown
# Photo shotlist — <project>

## Hero (one)
- Finished piece in context, raking light, golden hour OK.
- Filename target: `images/hero.jpg`

## Process (5-10)
- Stock laid out before first cut: `images/process-01-stock.jpg`
- First cut on the CNC, mid-cut: `images/process-02-cnc.jpg`
- Glue-up clamps in place: `images/process-03-glueup.jpg`
- ...

## Detail (3-5)
- Joinery close-up: `images/detail-01-joinery.jpg`
- Finish texture: `images/detail-02-finish.jpg`

## Maker (1, optional)
- Maker holding finished piece: `images/maker-portrait.jpg`
```

### `README.md` (Tier 2+)

See `agents/specialists/documentarian.md` for the format.

## Folder shape — single-project repo vs multi-project workspace

A user might want one of two folder shapes:

**Mode A — Project repo at root.** When the project lives in its own
GitHub repo, the build-packet files go at the root (e.g.,
`cnc-welcome-sign/README.md`, `cnc-welcome-sign/design.md`, etc.).

**Mode B — Workspace with multiple packets.** When the user has a
working directory with several projects, files go under
`projects/<project-slug>/`.

The orchestrator picks based on the user's prompt. When ambiguous,
default to Mode A (single-project repo) unless the user is clearly
inside a multi-project workspace already.

## Naming conventions

- Project slug: kebab-case, no spaces (`cnc-welcome-sign`)
- File names: lowercase, hyphens, no spaces
- Part ids in `bom.csv`/`cut-list.csv`: short prefixes (`b001`,
  `p001`)
- Image filenames: `<role>-<slug>.jpg` where role ∈ {hero, process,
  detail, maker}
