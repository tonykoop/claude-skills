# Sourcing And Production Readiness

Use this reference when a project needs to move from design package to real purchasing, stock prep, assembly, and validation.

## Sourcing Workflow

- Start with required specs, not supplier names: dimension, material, grade, finish, quantity, tolerance, safety/contact requirement, compatibility.
- Add search terms and supplier candidates, but leave live price/availability blank until browsing or supplier contact happens.
- Browse or otherwise verify current prices, stock, lead time, shipping limits, substitutions when the user asks for sourcing or purchasing recommendations. Do not rely on remembered availability.
- Record `date_checked`, URL/source, unit price, minimum order, lead time, substitute risk.
- Separate `must match exactly` features from `acceptable substitute` features.

## Common Components Users Will Ask For

### Strings and string hardware

- Harp/kora/ngoni strings, nylon monofilament, fluorocarbon, gut, wound bass strings.
- Guitar/ukulele/violin strings, tuning machines, zither pins, bridge pins, tailpieces, fine tuners, nuts/saddles, fretwire.
- Piezo pickups, output jacks, pots, switches, shielding, strap buttons, neck screws, ferrules.

### Drums and shell hardware

- Goatskins, calfskin, synthetic heads, flesh hoops, steel rings, tension hoops, bearing-edge protectors.
- Drum rope, polyester cord, rawhide lace, tuning rings, pullers, decorative fabric wrap.
- Conga/bongo/djembe lugs, tension rods, side plates, rim/hoop hardware, rubber feet, stands.
- Hardwood staves, segmented-ring stock, plywood forms, adhesives, finishes, abrasives.

### Metal percussion

- Handpan/steelpan steel blanks, DC04 or stainless sheet/shells, nitrided shells, forming services.
- Steel tongue drum blanks, sheet metal thicknesses, laser/CNC cutting services, deburring supplies.
- Tuning hammers, stands, rubber feet, edge trim, corrosion protection.

### Woodwinds and reeds

- Bore stock, hardwood/cedar blanks, bamboo/cane, cork, thread wrap, leather, blocks/fetishes.
- Reed cane, bagpipe reeds, drone reeds, bags, stocks, ferrules, mounts, waxed hemp.
- Key/pad hardware for keyed instruments where applicable.

### Shop and fixture supplies

- CNC bits, laser-safe plywood/acrylic, MDF fixture stock, dowel/register pins, threaded inserts, clamps.
- Steam-bending forms, straps, cauls, molds, spoilboards, measuring tools, tuners, microphones, hygrometers.

## Production Deliverables

- `sourcing.csv` — component specs, suppliers/search terms, price/date checked, lead time, substitutes, sourcing risks.
- `cut-list.csv` — rough/final dimensions, material, quantity, grain direction, operation, yield, offcuts.
- `validation.csv` — target/measured values, tolerance, cents error or dimensional error, environment, result, action.
- `assembly-manual.md` — phased build steps, tools, safety, setup, tuning, finishing, maintenance, photo placeholders.
- `supplier-rfq.md` — clear supplier email/request-for-quote draft.
- `visual-bom-brief.md` — art direction and layout notes for a visual BOM plate.

## Visual BOM Pattern

Use Tony's Ashiko visual BOM as a reference:

```text
C:\Users\Tony\Documents\GitHub\ashiko-drum-workshop\images\figure-bom-v2.png
```

What makes it work:

- Header with assembly name, quote date, estimated cost.
- Large product/reference image near the top.
- Spreadsheet-style table with alternating row fills and strong column headers.
- Columns for part number, part name, description, quantity, units, picture, cost each, total.
- Small part images embedded directly in each row.
- Notes at the bottom for lumber species, sourcing assumptions, bulk pricing assumptions.

For generated visual BOMs, use actual photos/renders where available. If generated images are used, mark them as visual placeholders until replaced by real part photos or supplier images.

## RFQ Guidance

Good supplier requests include:

- Short project context.
- Exact quantity and acceptable range.
- Dimensions, material/spec, finish, tolerances, use case.
- Whether substitutions are acceptable.
- Request for unit price, volume price, lead time, shipping estimate, data sheet/drawing.
- Deadline and contact information.
