# Boxes, Storage, Stacking, Decor, And Hybrid Cases

Use this file for modular toolboxes, storage trays, shelves, plant stands,
STAS/gallery items, cat furniture, rolling stack systems, and wood-metal
attache cases.

## Contents

- Modular toolbox platform
- Storage archetypes
- Stackable and rolling systems
- Shelves, plant stands, STAS, and cat furniture
- Hybrid heritage attache cases
- Output checklist

## Modular Toolbox Platform

The seed platform from the brainstorming session is a 20 x 10 x 8 inch
tackle-box-style sheet metal case.

Recommended master variables:

| Variable | Default | Notes |
| --- | ---: | --- |
| `Box_Length` | 20.00 in | outside planning length |
| `Box_Width` | 10.00 in | outside planning width |
| `Box_Height` | 8.00 in | outside planning height |
| `Material_Thickness` | 0.060 in | 16 ga mild steel starting point |
| `Inside_Bend_Radius` | 0.060 in | match `T` unless tooling differs |
| `Clearance_Gap` | 0.030 in | lid, insert, and tray clearance |
| `Lid_Drop` | 1.50 in | clamshell dust/weather overlap |
| `Tray_Clearance` | 0.50 in | clearance below closed lid |

SolidWorks strategy:

1. Create a master layout part or skeleton sketch with the controlling
   envelope.
2. Derive tub, lid, trays, dividers, hinges, and latch interfaces from the
   same layout.
3. Keep the tub and lid as sheet metal bodies or separate parts that flatten
   cleanly.
4. Use a closed hem or inward return flange at the tub rim for safe handling
   and tray support.
5. Integrate piano hinge or latch mounting flats before detailing the exterior.
6. Keep hardware holes at a consistent visual pitch, such as 1.5 or 2.0 inches
   on center, unless the purchased hardware dictates otherwise.

Main tub options:

- Single U-fold body with welded or riveted end caps for high rigidity.
- Four-sided tray with relieved corners for lighter storage.
- Tab-and-slot self-fixturing when welding or riveting will follow.

Modular insert options:

- Stepped hanger lip: drop-in trays hook over the tub rim.
- Slot-grid walls: plasma-cut vertical slots accept movable dividers.
- Lift-out tote: center divider extends upward and includes a handle slot.
- Foam-offset precision tray: add 0.25 or 0.50 inch clearance for foam liners.

## Storage Archetypes

### Liquids, Creams, And Sprays

Use for shoe-care supplies, bike grease, lube, leather oil, aerosols, and jars.

- Minimum tray wall height: 3.5 inches.
- Prefer solid-bottom trays with folded or sealed corners for spill capture.
- Use drop-in secondary plates for circular or oval pockets when useful.
- Keep tall containers low in the box for center of gravity.

Starting pocket sizes from the brainstorm:

- Cream or polish jars: about 2.75 inch diameter
- Standard aerosol or powder cans: about 2.65 inch diameter
- Conditioner or oil bottles: about 2.25 x 1.5 inch oval/rectangular pockets

Verify actual container dimensions before cutting.

### Rolling Stock And Soft Goods

Use for rim tape, tubes, valve stems, shoelaces, insoles, small lights, and
brushes.

- Use shallow trays around 2.0 inches deep for visibility.
- Add tab-and-slot divider pitch around 2.0 inches when adjustability matters.
- Add folded anti-roll posts or removable pegs for tape and rolls.
- Keep brush slots and lace channels long and easy to clean.

### Precision Gear

Use for rimfire competition gadgets, optics, electronics, match accessories, or
delicate gear.

- Add lidded sub-compartments or covered dividers.
- Add foam clearance offset where protective foam will be inserted.
- Prevent rattle with dividers, straps, or removable padded inserts.
- Keep heavy precision items low and isolate them from liquids.

### Makerspace Commute Tote

Use for hand tools, calipers, safety glasses, bits, and fasteners.

- Split the box length into removable carry zones.
- Use a center handle around 1.25 x 4.0 inches as a starting ergonomic slot,
  then verify hand clearance.
- Radius and deburr the handle, or add a folded/rolled grip edge.
- Add slight draft or clearance so the tote drops into the chassis without
  binding.

## Stackable And Rolling Systems

Nesting prevents sliding. Latching prevents separation. The bottom unit carries
dynamic loads.

Stacking interfaces:

- Perimeter clocking rim: lower lid has an upward rim; upper base has an inset
  shoulder.
- Corner cleats: welded or riveted L-shaped pockets capture the upper box feet.
- Slide-and-lock cleats: keyhole slots and hook tabs lock after a short slide.
- Draw latches: purchased over-center latches compress upper and lower boxes.

Rules:

- Keep latch hardware clear of removable trays by at least 0.25 inch.
- Use consistent latch and foot geometry across the whole box family.
- If stack height exceeds 3 x base width, place heavy boxes at the bottom and
  include a center-of-gravity warning.
- Design all stack interfaces with deburring and pinch-point awareness.

Dolly chassis:

- Use thicker base material than normal boxes: 12 ga mild steel or 1/8 inch
  aluminum as planning starting points.
- Add down-turned 2 inch structural flanges on all sides where practical.
- Use front swivel casters with brakes and rear large wheels/axle tabs for a
  hand-truck style.
- Reinforce caster bolt patterns with doubler plates when loads are high.
- Add rear handle receiver brackets for square tube handles or a detachable
  hand-truck spine.

## Shelves, Plant Stands, STAS, And Cat Furniture

Shelves and plant stands:

- Reject long flat shelf edges as a default. Add return flanges, hems, ribs, or
  folded trays for stiffness.
- For shelf spans over 12 inches, propose a 90 degree return flange, hat
  channel, or teardrop hem.
- For plant trays, consider drainage slots, removable drip pans, corrosion
  resistant materials, and cleanable corners.
- Keep water and soil away from unsealed mild steel unless patina/rust is
  intentional and isolated.

STAS/gallery hanging:

- Treat the rail/hook interface as a measured interface, not a guessed profile.
- Ask for the exact hanger model, hook, cable, wall clearance, and load.
- Add anti-slip geometry and a secondary retention option for heavy mirrors or
  sconces.
- Keep visible fasteners and slots symmetrical when the bracket is decorative.

Cat furniture:

- Apply at least 4x dynamic factor over the animal's static weight as a
  planning minimum.
- No exposed raw sheet metal edges where paws, tails, fur, or people can
  contact.
- Prefer hems, guards, rubber edge trim, rolled lips, or wood caps.
- Route wall anchoring, dynamic loads, and overhead failure concerns through a
  safety gate before fabrication-ready output.

## Hybrid Heritage Attache Cases

Use this mode for old-world briefcases, wood-metal art cases, and refined
objects where metal is the exoskeleton and wood is the skin or inlay.

Architecture:

- Drive metal and wood from a shared SolidWorks skeleton.
- Use metal U-channels, miter flanges, hems, or folded frames to capture wood
  panels.
- Allow seasonal wood movement. Add at least 0.040 inch cross-grain clearance
  in metal channels unless measured wood movement analysis specifies more.
- Avoid depending entirely on glue between wood and metal. Add mechanical
  capture, screws, rivets, tongues, grooves, or slots.

Material pairings:

| Metal | Wood | Fastener feel |
| --- | --- | --- |
| Brass or copper | walnut or mahogany | brass rivets or pins |
| Anodized aluminum | teak, zebrawood, maple | stainless machine screws |
| Blued mild steel | oak or cherry | copper-washed rivets |

Design details:

- Use custom folded corner caps for a flight-case/steamer-trunk feel.
- Keep visible fastener pitch symmetrical and intentional.
- Add sculpted handle mounts that bridge sheet metal tabs and a wood handle.
- Check empty weight. If the case exceeds about 8 lb empty, suggest thinner
  metal, aluminum, pocketed wood panels, or fewer solid hardwood parts.

## Output Checklist

For this reference family, include:

- box or object envelope
- material/thickness and finish
- rim, hem, or edge protection plan
- insert/tray/hardware interface dimensions
- flat pattern risk notes
- bend order
- fastening or welding method
- load, spill, transport, or dynamic safety notes
- verification measurements before cutting

