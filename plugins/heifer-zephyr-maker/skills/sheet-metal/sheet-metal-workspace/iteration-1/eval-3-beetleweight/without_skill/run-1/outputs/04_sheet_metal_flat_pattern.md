# Flat Pattern — Folded Armor Shell

**Material:** 5052-H32 aluminum, 1.6 mm (0.063") thick
**Stock size needed:** ~330 mm x 280 mm sheet
**K-factor (5052 air bend at 1.5T inside radius):** 0.40
**Bend radius (inside):** 3.0 mm
**Bend allowance per 90 deg bend:** BA = (pi/2) * (R + K*T) = 1.5708 * (3.0 + 0.40 * 1.6) = 1.5708 * 3.64 = 5.72 mm

## Shell Topology
Single blank, six bends. Imagine an upside-down boat:
- Flat top deck (with service-hole patterns)
- Two side walls bent down 90 deg
- Front wedge face bent down 15 deg (this is the leading edge)
- Rear face bent down 90 deg
- Two small return flanges along bottom edges of sides (for bolting to internal frame)

## Bend Sequence (CRITICAL — wrong order = press brake collision)
| Step | Bend | Angle | Inside Radius | Direction | Notes |
|---|---|---|---|---|---|
| 1 | Wedge face (front) | 15 deg down | 3.0 mm | Down | Bend first while blank is flat — easy access |
| 2 | Rear face | 90 deg down | 3.0 mm | Down | Press brake clears - no interference |
| 3 | Left side wall | 90 deg down | 3.0 mm | Down | Now we have an open box |
| 4 | Right side wall | 90 deg down | 3.0 mm | Down | Mirror of step 3 |
| 5 | Left bottom return flange | 90 deg in | 3.0 mm | In | Tab folds inward 10 mm for bolting |
| 6 | Right bottom return flange | 90 deg in | 3.0 mm | In | Mirror |

## Flat Blank Layout (approximate, mm)

```
                  330 mm overall
        +----------------------------+
        |                            |
   45mm | <-- front wedge face -->   |  bend line @ 15deg
        +----------------------------+
   95mm |                            |
        |        TOP DECK            |
        |   (service holes here)     |
        +----------------------------+
   45mm |                            |
        |       REAR FACE            |
        +----------------------------+   bend line @ 90deg
   10mm |    REAR BOTTOM LIP         |
        +----------------------------+

   ^                                  ^
   |  side wall flaps stick out left  |
   |  and right of TOP DECK band:     |
   |  each is 50mm tall + 10mm        |
   |  return flange = 60mm flap.      |
```

## Bend Deduction Math (per bend)
For each 90 deg bend:
- BD (Bend Deduction) = 2 * (R + T) - BA = 2 * (3.0 + 1.6) - 5.72 = 9.2 - 5.72 = 3.48 mm
- So for every 90 deg bend, the flat blank is 3.48 mm SHORTER than the sum of the outside dimensions.

For the 15 deg wedge bend:
- BA = (15 * pi/180) * (R + K*T) = 0.2618 * 3.64 = 0.95 mm
- BD = 2 * (R + T) * tan(15/2) - BA = 2 * 4.6 * 0.1317 - 0.95 = 1.21 - 0.95 = 0.26 mm
- Negligible for layout purposes.

## Relief Cuts (REQUIRED at intersecting bends)
At each corner where the side wall meets the rear face, cut a **relief notch** before bending:
- Notch type: round-bottom slot
- Notch width: 3.2 mm (2 x material thickness)
- Notch depth: 5.0 mm (into the corner past the bend tangent line)
- Purpose: prevents tearing and puckering where two bends meet

Without these reliefs the corner will crack on the first bend and look terrible — middle school robotics judges notice.

## Service-Access Hole Pattern on Top Deck
- 6x M3 clearance holes (3.3 mm) for top deck-to-frame bolts (perimeter, 30 mm in from edges)
- 1x rectangular pocket: 30 mm x 50 mm centered, for battery access (use a removable cover plate)
- 1x 8 mm hole for arming-link bolt access
- 1x 4 mm hole for LED status / charge port

## Edge Break / Deburr
ALL edges after laser cut: 0.3 mm chamfer minimum. The leading wedge edge stays sharp (rules-legal up to 1.0 mm radius for most beetle organizations — check NHRL/RoboGames rules for your event).
