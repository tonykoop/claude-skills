# Sourcing and production

## Table of contents

- Sourcing.csv (Tier 2+)
- Supplier RFQ — `supplier-rfq.md` (Tier 2 optional)
- Cut-list optimization
- Validation sheet — `validation.csv`
- Assembly manual — `assembly-manual.md`
- Visual BOM brief — `visual-bom-brief.md`
- Notes on stock-buying conventions
- Lead-time defaults to budget for

The "where do I buy this and how much will it cost" reference. Used
by the manufacturing-planner specialist when extending `bom.csv` into
`sourcing.csv` (Tier 2+).

## Sourcing.csv (Tier 2+)

Extends `bom.csv` with vendor details:

```
item_id, primary_vendor, primary_url, primary_unit_cost_usd,
alt_vendor, alt_url, alt_unit_cost_usd, lead_time_days,
shipping_usd, rfq_sent, rfq_quoted, notes
```

### Filling the rows

- **`primary_vendor`** — the user's preferred source. If the user
  hasn't said, default to:
  - Sheet goods: a regional hardwood/plywood dealer (MacBeath in CA,
    Forest Products in MN, etc.)
  - Hardware: McMaster-Carr (fast, expensive) or Bolt Depot (slower,
    cheaper)
  - Electronics: DigiKey or Mouser
  - Generic shop supplies: the user's local big-box (Home Depot,
    Lowe's, Menard's)
- **`alt_vendor`** — a second source for risk mitigation. Useful when
  the primary is out-of-stock or has a long lead time.
- **`lead_time_days`** — from order to door. Be conservative.
- **`shipping_usd`** — only when the vendor charges separately. If
  shipping is included in the unit cost, write `0` and note in
  `notes`.

### What to verify before declaring done

- Every primary URL resolves (not 404).
- Lead times don't exceed the user's build deadline.
- Shipping costs are accounted for in the total.
- Tax estimation noted (default ~10% for US makers; varies).

## Supplier RFQ — `supplier-rfq.md` (Tier 2 optional)

Useful when the user needs custom-cut stock, custom-machined parts,
or wholesale quantities. Standard structure:

```markdown
# Supplier RFQ — <project name>
## Maker contact
- Name, email, phone
## Project summary
- What's being made, how many, by when

## Items to quote

### Item 1 — <description>
- Material: <material>
- Quantity: <qty>
- Specifications: <dims, tolerances, finish>
- Drawing: see `drawings/dwg-001.pdf` (attach)
- Required by: <date>
- Shipping address: <address>

### Item 2 — ...

## Quote response template

Vendor please return:
- Per-item unit price
- Setup / NRE charges if any
- Lead time
- Payment terms
- Shipping cost / method
```

## Cut-list optimization

For sheet goods, the manufacturing-planner should produce a cut layout
that minimizes waste. Two patterns:

**Pattern A — Single-sheet manual layout.** For projects under ~10
parts, hand-arrange the cuts on a sketch and verify they fit. Note
remaining usable scrap in `notes`.

**Pattern B — Programmatic optimization.** For families of sizes or
larger projects, run a bin-packing algorithm. The result goes in the
cut-list as a `stock_id`-grouped layout.

In v0.1, prefer pattern A. Add a programmatic optimizer in v0.2 if
real users hit projects where it matters.

## Validation sheet — `validation.csv`

```
check_id, check_name, target, tolerance, method, when_to_check, pass_fail, notes
```

Rules of thumb:
- **`when_to_check`** — be specific. "After CNC" is bad; "After CNC,
  before glue-up" is good.
- **`method`** — measurable, not vague. "Caliper across A-A" beats
  "looks square."
- **`target`** + **`tolerance`** — numbers, not adjectives.
- **`pass_fail`** — starts as `pending`. The maker fills in `pass`
  or `fail` during the build.

## Assembly manual — `assembly-manual.md`

Step-by-step. Format:

```markdown
# Assembly manual — <project>

## Estimated total time: <hh:mm>
## Tools needed: <list>
## Materials at this stage: <list>

### Step 1 — <verb> <part>
- **What you're doing:** <one sentence>
- **Tool:** <tool>
- **Time:** <minutes>
- **Photo placeholder:** `images/step-01-<slug>.jpg`
- **Watch for:** <gotchas>

### Step 2 — ...
```

Rules of thumb:
- One step per page-break worthy chunk. Short steps are fine.
- Photo placeholders even if photos don't exist yet — the photo-
  shotlist references these filenames.
- Each step has a "watch for" line. If you can't think of one,
  the step is probably trivial enough to combine with the next.

## Visual BOM brief — `visual-bom-brief.md`

One page describing what the visual BOM (Tier 3) should show:

```markdown
# Visual BOM brief — <project>

## Hero image position: top-left, 50% page width
## Parts grid: 3 columns, 4 rows
## Callout numbers: 01-12

## Parts to call out
01 — Sign body (qty 1) — see `drawings/dwg-001`
02 — Mounting cleat (qty 2) — see `drawings/dwg-002`
03 — ...
```

The documentarian uses this brief to compose the actual visual BOM
slide / page in Tier 3.

## Notes on stock-buying conventions

- **Plywood** sold in 4×8 sheets in the US, in mm-thick metric
  elsewhere. Always note both.
- **Hardwood** sold in board-feet (rough) or by the linear foot
  (S2S/S4S — surfaced two/four sides). Note which.
- **Steel** sold by linear foot for sticks, by sheet for plate.
- **Aluminum** similar to steel; alloy matters (6061 vs 2024 vs etc.).
- **Filament** by kg; resin by liter.

## Lead-time defaults to budget for

When the user hasn't asked, assume:
- Local pickup: 1 day
- Big-box / Amazon Prime: 2-3 days
- Specialty hardware (McMaster, Bolt Depot): 3-5 days
- Wood / metal supplier: 1-2 weeks if cutting to size
- Custom services (laser-cut metal, anodizing): 2-4 weeks
- Overseas / drop-ship from manufacturer: 4-8 weeks

If the user has a deadline, work backward and flag any item that
won't arrive in time.
