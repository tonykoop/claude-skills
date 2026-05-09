# Machine, post-processor, fixturing

## Machine assumptions

This packet assumes Maker Nexus has a hobby-to-prosumer 3-axis CNC
router with the following baseline capability. **Verify on site.**

| Spec | Assumed value | Verify? |
|---|---|---|
| Make / model | TBD (e.g. ShopBot Desktop, Onefinity, Avid Pro) | [verify] |
| Work envelope | >= 24 x 18 in | [verify] |
| Z clearance | >= 3 in | [verify] |
| Spindle | Variable-speed router or VFD spindle, 1.5-2.2 kW | [verify] |
| Collet | 1/4 in or ER-11 / ER-20 | [verify] |
| Touch plate | Yes | [verify] |
| Dust shoe | Yes | [verify] |
| Dust collection | Yes (HEPA or cyclone) | [verify] |
| Spoilboard | MDF, replaceable | [verify] |
| Software / sender | TBD (VCarve, Mach3, UCCNC, gSender, Carbide Motion) | [verify] |

## Recommended CAM software (in order of fit)

1. **VCarve Pro / VCarve Desktop** (Vectric) - purpose-built for V-carving;
   the "carve toolpath" handles serif fonts beautifully.
2. **Carbide Create Pro** - free with Carbide-machine ownership; has a
   competent V-carve toolpath.
3. **Fusion 360** - works but V-carving in Fusion is more setup-heavy
   than in VCarve.

## Post-processor

The post must match the sender Maker Nexus uses. Common pairings:

| Sender | Post |
|---|---|
| ShopBot | ShopBot.pp |
| Mach3 / Mach4 | Mach3 mm or in |
| UCCNC | UCCNC |
| gSender / Grbl | grbl mm or grbl inches |
| Carbide Motion | Carbide 3D |

Export G-code as the appropriate flavor and confirm the first few lines
are sane (`G20` for inches, `G21` for mm, `G90` absolute).

## Fixturing

### Plan A: double-sided carpet tape (recommended)

- 4-6 strips of 2 in carpet tape on the spoilboard, footprint of the
  blank.
- Press blank down hard. Walk on it.
- Pros: zero hold-down hardware in the toolpath; flat under the cut.
- Cons: tape under V-carve sometimes loads up and gunks the bit.
  Solution: keep tape strips outside the carve area.

### Plan B: clamps + cleats

- Two t-track clamps top and bottom edge, gripping the 1 in margin
  outside the perimeter profile.
- Pros: no tape residue.
- Cons: need to plan toolpath to avoid clamps.

### Plan C: vacuum table

- If Maker Nexus has a vacuum bed, use it.
- Confirm the porous spoilboard is not too clogged.

## Stock alignment

- Lower-left corner of blank = X0 Y0.
- One long edge against a fence cleat (jointed edge from stock prep).
- Pencil arrow on back of blank pointing to the back of the machine.

## Tool change protocol (mid-job)

1. Pause / "tool change" command in the sender.
2. Spindle off. Wait for full stop.
3. Loosen collet, swap bit, retighten.
4. Re-zero Z on top of stock with touch plate (X/Y stays).
5. Resume.
