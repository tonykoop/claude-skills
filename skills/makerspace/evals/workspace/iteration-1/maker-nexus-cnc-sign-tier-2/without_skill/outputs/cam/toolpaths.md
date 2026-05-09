# Toolpaths, feeds & speeds

> **Conservative starting points.** These are sane numbers for a
> hobby-class router cutting 1/4" Baltic birch with sharp tools. Tune
> on the actual Maker Nexus machine before committing to the full cut.

## Tool list

| T# | Tool | Geometry | Use |
|---|---|---|---|
| T1 | 60 deg V-bit, 1/4" shank, ~0.5 in cutting length | 60 deg included, sharp tip | Letters + border V-carve |
| T2 | 1/8" two-flute upcut end mill, 1/4" shank | Solid carbide, 0.75 in flute length | Perimeter profile + keyhole slot |

A 1/4" two-flute upcut is an acceptable substitute for T2 if 1/8" isn't
available - just drop the corner radius spec to 0.125 in.

## Feeds & speeds (starting points)

### T1: 60 deg V-bit, V-carve

| Parameter | Value | Notes |
|---|---|---|
| Spindle / RPM | 16,000 RPM | Adjust to dust-shoe noise floor |
| Feed rate | 80 IPM (X/Y) | Dial down 20% if you hear chatter |
| Plunge rate | 25 IPM | V-bit doesn't plunge well, keep slow |
| Max pass depth | full depth (V-carve calc'd by CAM) | typically <= 0.180 in here |
| Stepover | n/a (V-carve) | |

### T2: 1/8" upcut, perimeter profile

| Parameter | Value | Notes |
|---|---|---|
| Spindle / RPM | 18,000 RPM | |
| Feed rate | 60 IPM | |
| Plunge rate | 20 IPM | |
| Pass depth | 0.085 in | 3 passes through 0.236 in stock + 0.02 in into spoilboard |
| Final pass | -0.010 in below stock | clean break-through |
| Tabs | 4 tabs, 0.25 in long, 0.060 in tall | one centered on each side |

### T2: 1/8" upcut, keyhole slot (back-face op, optional)

| Parameter | Value |
|---|---|
| Spindle / RPM | 18,000 RPM |
| Feed rate | 40 IPM |
| Plunge rate | 15 IPM |
| Pocket depth | 0.180 in |
| Stepover | 40% |

## Operation order

1. **OP1: V-carve** (T1) - letters + inset border, top face up.
2. **OP2: Profile** (T2) - perimeter cut with tabs, top face up,
   same setup.
3. **OP3 (optional): Keyhole slot** (T2) - flip part, register against
   a corner, cut the keyhole on the back face. Or skip the CNC entirely
   for OP3 and use a benchtop drill press + 3/8" Forstner.

## Sanity checks before pressing GO

- [ ] Bit installed in collet, fully seated, then backed off ~1/16".
- [ ] Collet nut tightened with both spanners (no crescent wrench).
- [ ] Z-zero set on top of stock with touch plate, removed before run.
- [ ] X/Y zero matches CAM origin (lower-left of blank).
- [ ] Dust collection on, dust shoe seated.
- [ ] Toolpath simulation reviewed end-to-end in CAM.
- [ ] First 30 seconds run with spindle off and Z raised 1 in - "air cut" -
      to confirm motion.

## Estimated runtimes

| Operation | Estimate |
|---|---|
| OP1 V-carve | ~18 min |
| Tool change | ~2 min |
| OP2 Profile | ~5 min |
| Setup + teardown | ~20 min |
| **Total spindle time** | **~25 min** |
| **Total floor time** | **~50 min** |
