# Flat Roof Rack — Design Brief
**Vehicle:** 2024 Toyota RAV4 Prime (XSE trim assumed; raised side rails standard)
**Use cases:** Carry ShiftPod tent (in bag), carry lumber to/from makerspace
**Date:** 2026-05-18

---

## 1. Vehicle Reference Data (2024 RAV4 Prime)

| Parameter | Value | Source / Notes |
|---|---|---|
| Roof length (front to rear of rails) | ~58 in (1473 mm) | Measured per Toyota factory rail spec |
| Roof width (outside of rails) | ~44 in (1118 mm) | Side rails are integrated, raised |
| Roof width (between rails, usable) | ~38 in (965 mm) | Center-of-rail to center-of-rail |
| Factory roof distributed load limit (dynamic) | **176 lb (80 kg)** | Toyota owner's manual — **INCLUDES** rack hardware weight |
| Factory roof static load (parked, tent on top) | ~660 lb (300 kg) | Typical Toyota spec; verify in manual |
| Side rail type | Raised / flush combo — accepts most clamp-on towers | Yakima/Thule "raised rail" foot pads fit |
| Sunroof present? | YES on XSE/SE trims | Avoid clamping or drilling over sunroof glass |

**HARD CONSTRAINT:** Dynamic load = 176 lb total (rack + cargo). This drives every decision below.

---

## 2. Cargo Requirements

### ShiftPod (Original / ShiftPod 2 / Mini)
- Packed bag: ~50 x 14 x 14 in (127 x 36 x 36 cm)
- Weight: 55–75 lb depending on model (assume **70 lb** worst case)
- Soft-sided duffel — needs **flat, continuous surface** OR closely-spaced crossbars (no gaps > 10 in) to avoid sag
- Strap-down via cam straps through bag handles

### Lumber loads (makerspace trips)
- Typical sheet goods: 4x8 ft plywood/MDF, ~50–80 lb per sheet
  - **4 ft (48 in) overhangs the 44 in roof width by 2 in per side — OK**
  - **8 ft length sticks out ~24 in past front and ~16 in past rear** — need red flag on rear, ideally limit to 1–2 sheets at a time given weight cap
- Dimensional lumber: 2x4s, 1x4s up to 10 ft
  - 10 ft = 120 in. Roof is 58 in. Overhang front+rear ~62 in total. Limit rear overhang to 4 ft (48 in) per DOT rule of thumb; flag with red cloth.
- Long stock loading benefits from **bars that extend slightly beyond roof width** so cargo can hang past the vehicle if needed laterally

**Worst-case payload check:**
- 2 sheets 3/4" plywood (75 lb each) = 150 lb
- Add rack weight (~25 lb target) = 175 lb → at the 176 lb limit
- **Decision: Plan for 1 sheet + tent OR 2 sheets alone, never both.**

---

## 3. Design Goals

1. **Flat deck** — single planar surface so ShiftPod bag and sheet goods both sit flat without point loads
2. **Lightweight** — target rack tare ≤ 25 lb so payload budget is preserved
3. **Removable / no drilling** — clamp to factory raised rails using third-party feet (Yakima SkyLine + LandingPad, or Thule Evo Raised Rail), NOT direct-to-roof
4. **Tie-down friendly** — perimeter rail and/or T-slot for cam straps every ~6 in along the sides
5. **Sunroof-clear** — no fasteners or supports in the center 24 in (sunroof glass zone)
6. **Wind-noise reasonable** — leading edge airfoil or fairing
7. **Build-to-order in a makerspace** — uses CNC plasma/router + bender + TIG/MIG; no exotic processes

---

## 4. Top-Level Architecture Decision

**Chosen approach: Aluminum platform on commercial crossbar foundation.**

- **Foundation:** 2x Yakima JetStream bars (60 in) + SkyLine towers + LandingPad 22 (or equivalent Thule WingBar Evo + Evo Raised Rail). These are load-rated, weatherproof, and certified to the vehicle.
  - Foundation weight: ~17 lb
  - Foundation load rating: 165 lb (Yakima) — matches vehicle limit closely
- **Platform deck:** Custom-built flat platform that **bolts to the crossbars** via T-slot channel nuts.
  - Material: 6061-T6 aluminum extrusion frame + perforated 5052 aluminum sheet deck (or aluminum slats)
  - Platform weight target: ≤ 8 lb (so total rack ~25 lb)

This split-architecture is **safer and cheaper** than building towers from scratch — the certified clamps handle the critical interface with the car.

---

## 5. Parameter Table (drives the build files)

| Symbol | Param | Value | Notes |
|---|---|---|---|
| L_deck | Platform length | 52 in | Fits between/over crossbars, ~3 in shy of rail ends |
| W_deck | Platform width | 42 in | 1 in inboard of outside-of-rail line each side |
| H_deck | Deck thickness (frame + skin) | 1.25 in | Low profile, low drag |
| t_skin | Deck skin thickness | 0.063 in (16 ga) | 5052-H32 aluminum, perforated 3/8" holes on 1/2" centers |
| Frame_ext | Perimeter & cross member | 1 in x 1 in T-slot 8020-style aluminum extrusion | 10-series, ~0.45 lb/ft |
| N_xmbr | # internal crossmembers | 3 | Spaced 13 in on center; gap between supports < 14 in for tent bag |
| Tie_pitch | Tie-down slot pitch | 6 in along long sides | Open T-slot in perimeter extrusion already provides this |
| Fairing | Front wind fairing | 6 in tall, 30° rake, ABS or aluminum | Reduces noise above 50 mph |
| Mount | Platform to crossbar | 4x M8 channel nuts + cap screws + neoprene isolator | Two per crossbar |
| Margin_to_glass | Min clearance to sunroof | ≥ 2 in | Cross-section avoid zone Y = 12–34 in from front of roof |

---

## 6. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Exceeding 176 lb dynamic limit | Painted load-rating decal on platform: "MAX CARGO 150 LB" (leaves 25 lb for rack itself) |
| Galvanic corrosion (Al deck on steel fasteners) | Use stainless 18-8 fasteners with nylon isolator washers |
| Sunroof damage from drilling/clamping | Use rail clamp foundation only; no center penetrations |
| Lumber sliding forward under braking | Front strap to factory tow hook eyelet + rear strap to tow point; tent bag uses 4 perimeter cam straps |
| Wind noise / whistle | Front fairing + rubber T-slot fillers in unused channel |
| Snow/ice load (static) when parked under tent | Snow load << 660 lb static limit; remove rack in winter if not used |
| Lumber overhang exceeds DOT limit | Rule: max 4 ft rear overhang, red flag required; daytime only for >3 ft front overhang |

---

## 7. Build Sequence (high level)

1. Order Yakima JetStream 60" bars + SkyLine towers + LandingPad 22 (vehicle-specific fit kit)
2. Cut extrusion to length on miter saw with carbide non-ferrous blade
3. Plasma/laser cut perforated deck skin from 4x8 sheet of 5052-H32 (one nest)
4. Drill/tap or use corner brackets to assemble extrusion frame
5. Rivet or screw skin to frame perimeter
6. CNC or hand-form aluminum fairing; rivet to leading crossmember
7. Apply decals (load rating, tie-down points)
8. Test fit on car; torque check crossbar clamps to 9 N·m (Yakima spec)
9. Road test: 30 mph → 50 mph → 70 mph progression, listening for whistle, watching for vibration

---

## 8. Files in this package

- `01_design_brief.md` — this file
- `02_parameters.csv` — machine-readable param table
- `03_bom.csv` — bill of materials with sources and costs
- `04_cut_list.csv` — every part to cut with dims and qty
- `05_load_calculations.md` — load math for tent and lumber scenarios
- `06_assembly_checklist.md` — step-by-step build & install
- `07_tiedown_loading_guide.md` — how to load tent vs lumber, knot/strap guide
