# Manufacturing and tools

## Table of contents

- CNC Routers
- Laser Cutters
- 3D Printers (FDM)
- 3D Printers (SLA / Resin)
- Lathes (Wood)
- Lathes (Metal)
- Mills (Vertical, Manual or CNC)
- Welding (MIG, TIG, Stick)
- Tablesaw, Bandsaw, Jointer, Planer (Woodworking)
- Drill Press
- Sewing / Textile / Embroidery
- Electronics Bench
- Pottery / Ceramics

Tool-by-tool guidance for planning operations. This is the omnibus
reference — when it grows past ~500 lines, split into per-domain files
under `references/domains/` (woodworking.md, metalworking.md,
electronics.md, textiles.md, ceramics.md, etc.).

For each tool family: typical capabilities, common pitfalls, fixturing
patterns, material limits, and what to ask the user about *their*
specific machine.

## CNC Routers

**What it does well:** sheet-good shaping (plywood, MDF, HDPE), 2.5D
relief, pocketing, drilling, profile cuts, V-carving, light 3D
roughing/finishing on softer materials.

**Capability questions to ask:**
- Bed size and Z travel?
- Max spindle RPM and HP?
- Tool holder type (ER collets, ISO, BT)?
- Vacuum table or T-track / fixture only?
- What bits are in the shop tool inventory vs bring-your-own?

**Material limits:**
- Hardwood, plywood, MDF, HDPE, foam, soft metals if cleared.
- Many shops ban ferrous metals on woodworking CNCs (chips destroy
  bearings).
- Aluminum varies by shop — some allow with proper fixturing/feeds,
  others ban entirely. Check the policy.

**Common pitfalls:**
- Workholding fails on small parts → onion-skin tabs, then knife-cut
  free.
- Climb-cut on plywood with cheap bits → tearout. Conventional cut
  the final pass.
- Insufficient depth-of-cut steps on hardwood → bit deflection.
- Forgetting to add an offset for compression bits' upcut at bottom.

**Fixturing patterns:**
- Vacuum table + spoilboard for sheet goods.
- Brad-nailed spoilboard for one-off fixturing.
- Threaded inserts in spoilboard for repeat fixtures.

**Defaults for unclear feeds/speeds:**
Don't guess feeds and speeds — ask the user or note "TBD: confirm
from machine's posted feed chart." Bad feeds break bits and ruin
stock.

## Laser Cutters

**What it does well:** thin-stock cutting, raster engraving, vector
scoring, precision shapes, repeatable production runs.

**Capability questions to ask:**
- CO₂ or fiber laser? Wattage?
- Bed size? Auto focus?
- Air assist? Fume extraction routed where?

**Material limits — universal bans (every shop):**
- Chlorinated plastics (PVC, vinyl) → produces hydrochloric acid +
  damage to optics.
- ABS → cyanide-bearing fumes.
- Polycarbonate → toxic, also doesn't cut cleanly with CO₂.
- Anything fluoride-bearing (PTFE).

**Material limits — typically allowed:**
- Acrylic (cuts and engraves well; ¼" max for many CO₂ machines).
- Plywood and hardwood (under 1/4" reliable; 1/2" iffy).
- MDF (engraves well; cutting smells terrible).
- Cardboard, paper, leather.
- Anodized aluminum for marking only (not cutting on CO₂).

**Common pitfalls:**
- Material thickness exceeds laser's reliable range → multiple passes
  with re-focus, or split job to a CNC.
- Adhesive-backed materials (vinyl) → adhesive contaminates lens.
- Engraving on knot-rich wood → uneven depth, fire risk on resin
  pockets.

## 3D Printers (FDM)

**Capability questions:**
- Build volume?
- Nozzle diameter and how easily swappable?
- Heated bed / chamber?
- Material list the printer can handle (PLA only? PETG? ABS? Nylon?
  TPU?).

**Common pitfalls:**
- Overhangs without supports.
- Bridge spans beyond the printer's bridging ability.
- Bed adhesion on first layer (PETG vs glass vs PEI sheet).
- ABS warping on un-enclosed printers.
- Ignoring print orientation for strength (layer adhesion is the
  weak axis).

## 3D Printers (SLA / Resin)

**Common pitfalls:**
- Forgetting drain holes in hollow parts.
- Insufficient supports on overhangs.
- Post-cure schedule (UV duration matters).
- Resin handling PPE — gloves, ventilation, isopropyl wash.

## Lathes (Wood)

**Capability questions:**
- Swing over bed and between centers?
- Variable speed?
- Outboard turning capability?
- Tool inventory (bowl gouge, spindle gouge, parting tool, skew)?

**Common pitfalls:**
- Mounting strategy mismatch (faceplate vs chuck vs centers).
- Stock balance — out-of-balance blanks at speed.
- Catch-prone tool angles for the user's experience level.
- Drying schedule for green wood (won't dry uniformly mounted on a
  faceplate).

## Lathes (Metal)

**Capability questions:**
- Swing, between-centers, spindle bore?
- Threading capability and pitch range?
- Tool post (QCTP, four-way, lantern)?
- Coolant?

**Common pitfalls:**
- Stock chucking — three-jaw vs four-jaw vs collet.
- Tool height relative to centerline (off-center cuts ruin finish
  and tool life).
- Forgetting to recompute SFM for different materials.
- Long stock without a tailstock or steady rest.

## Mills (Vertical, Manual or CNC)

**Capability questions:**
- Travel (X/Y/Z)?
- Spindle taper and tooling?
- Power feed on which axes?
- DRO present?

**Common pitfalls:**
- Workholding (vise vs fixture vs T-slots).
- Tramming the head (not square = tapered cuts).
- Climb milling on a manual mill without ballscrews → backlash
  catches.
- Tool stick-out vs rigidity.

## Welding (MIG, TIG, Stick)

**Capability questions:**
- Process available?
- Material thickness range?
- Gas type for MIG/TIG (75/25, pure argon, etc.)?
- Welding curtains / dedicated booth?

**Common pitfalls:**
- Cleaning prep — mill scale, paint, galvanizing.
- Galvanic corrosion in mixed-metal welds.
- Hexavalent chromium in stainless welding without proper exhaust.
- Distortion control — tack pattern, cooling sequence.

## Tablesaw, Bandsaw, Jointer, Planer (Woodworking)

**Common pitfalls:**
- Feeding direction relative to grain.
- Push-stick discipline (especially on tablesaw rip).
- Snipe on the planer (lift the trailing end on long stock).
- Riving knife / blade guard on tablesaw — many makerspaces require
  these be in place.
- Bandsaw blade tension and tracking.
- Jointer relief on quarter-sawn / heavily-figured stock.

## Drill Press

**Common pitfalls:**
- Workpiece pinch — clamp it, don't hand-hold.
- Drilling steel with wood-shop drill press at woodworking RPMs.
- Forster bits at high RPM → burning.
- Insufficient stock support for through-drilling.

## Sewing / Textile / Embroidery

**Capability questions:**
- Domestic vs industrial sewing machine?
- Walking-foot capability for thick layers?
- Embroidery machine hoop size?
- Serger / coverstitch availability?

**Common pitfalls:**
- Needle size mismatched to material (too small breaks, too big
  leaves holes in thin fabric).
- Ignoring grain direction on woven fabric.
- Stretch-stitch vs straight-stitch on knit fabrics.
- Not pre-washing fabric for shrinkage.

## Electronics Bench

**Capability questions:**
- Soldering iron type and temperature control?
- Hot-air rework station?
- Microscope?
- Power supplies (variable, programmable)?
- Oscilloscope bandwidth?

**Common pitfalls:**
- ESD — wrist strap, mat, grounded iron tip.
- Cold solder joints — temperature too low.
- Lead-free vs leaded solder mixing.
- Reading capacitor polarity backward.

## Pottery / Ceramics

**Capability questions:**
- Wheel(s)?
- Kiln type and max temp (cone)?
- Slip-casting bench / mold storage?
- Clay studio's own clay vs bring-your-own?

**Common pitfalls:**
- Drying schedule — uneven thickness cracks during drying.
- Bisque firing schedule mismatched to clay body.
- Glaze firing temperature mismatched to glaze and clay.
- Kiln-shelf prep (kiln wash, cones).

## Hand-tools-only fallback

When the user has no power tools, plan around hand tools:
- Hand saws (rip, crosscut, dovetail, coping)
- Hand planes (jack, smoother, block, router plane)
- Chisels and mallet
- Hand drill / brace and bit
- Marking tools (combination square, marking gauge, knife)
- Clamps (F-clamps, parallel jaws)

Hand-tools-only builds take longer but are completely viable for
small joinery projects, boxes, frames, and finish work. Adjust time
estimates accordingly (4-8x slower than power tools for most cuts).

## Asking about unknown shops

When the user is at a makerspace not in `spaces/`, ask three
questions before assuming any tool:

1. What machines do you have access to?
2. What are you cleared to use right now?
3. What materials are banned in this shop?

Three answers, and the skill can plan responsibly.
