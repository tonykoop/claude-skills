# Load Calculations — RAV4 Prime Flat Roof Rack

## A. Static weight budget (dynamic driving limit = 176 lb)

| Item | Weight (lb) | Cumulative (lb) | Margin to 176 |
|---|---:|---:|---:|
| Yakima crossbars + towers (foundation) | 17 | 17 | 159 |
| Custom platform (frame + skin + fairing + fasteners) | 8 | 25 | 151 |
| **Rack tare total** | **25** | **25** | **151 lb available for cargo** |

Cargo scenarios:

### Scenario 1 — ShiftPod only (camping trip)
- ShiftPod packed bag: 70 lb
- 4x cam straps: 1 lb
- **Cargo total: 71 lb** → 80 lb margin remaining. OK.

### Scenario 2 — One 4x8 sheet of 3/4" plywood
- 3/4" ply 4x8: 75 lb
- Straps + 2x4 spreaders underneath: 5 lb
- **Cargo total: 80 lb** → 71 lb margin. OK.

### Scenario 3 — Two sheets 3/4" plywood (limit case)
- 2x 75 = 150 lb
- Straps + spreaders: 5 lb
- **Cargo total: 155 lb** → -4 lb. **OVER LIMIT by 4 lb.**
- Decision: cap at 1.5 sheets of 3/4" OR 2 sheets of 1/2" (50 lb each = 100 lb cargo).

### Scenario 4 — ShiftPod + 1 sheet plywood (mixed)
- Tent 70 + ply 75 + straps 5 = 150 lb
- **Cargo total: 150 lb** → 1 lb margin. **TIGHT — not recommended.**

### Scenario 5 — Dimensional lumber bundle (8x 2x4 @ 8 ft)
- 2x4x8 SPF kiln-dried: ~10 lb each x 8 = 80 lb
- Straps: 2 lb
- **Cargo total: 82 lb** → 69 lb margin. OK.

---

## B. Aerodynamic and inertial load checks

### Wind drag on flat platform (empty, 70 mph)
- Frontal area approx: 42 in x 1.25 in = 52.5 in² = 0.36 ft²
- Without fairing, Cd ≈ 1.1 (flat plate normal); with fairing Cd ≈ 0.4
- Dynamic pressure at 70 mph: q = 0.5 * 0.00238 slug/ft³ * (102.7 ft/s)² ≈ 12.6 lb/ft²
- Drag force (no fairing): F = Cd * q * A = 1.1 * 12.6 * 0.36 ≈ **5.0 lb**
- Drag force (with fairing): 0.4 * 12.6 * 0.36 ≈ **1.8 lb**
- Fuel economy hit estimate: 1–2 mpg highway with empty rack; up to 4 mpg with tent loaded

### Braking deceleration → tie-down force
- Hard brake = 1 g (32.2 ft/s²); typical panic stop ~0.7 g
- Worst-case 150 lb cargo at 1 g forward = **150 lbf forward**
- 1 in cam strap rated 500 lb each → 1 strap is sufficient; **use 2 forward + 2 rear** as redundancy
- Tie to factory tow hook eyelet (front bumper has a screw-in eye) for forward strap; D-ring or hitch loop for rear

### Lateral cornering (0.7 g lateral)
- 150 lb x 0.7 = 105 lbf sideways
- T-slot perimeter provides continuous tie-down; 2x side straps handle this easily
- Verify cargo CG stays below 4 in above deck → roll moment manageable

---

## C. Crossbar span and platform deflection

### Crossbar span between towers
- Yakima JetStream 60 in bar, towers ~38 in apart (rail spacing)
- Yakima rated for 165 lb distributed → platform load of 150 lb is within rating
- Recommend distributing load so center of mass is between the two crossbars, not cantilevered

### Platform deck — bending check (worst case: 150 lb point load mid-span)
- Treat as simply supported beam between the 2 crossbars (spaced ~24 in apart along platform length)
- Effective beam: 6061-T6 1x1 extrusion array, 3 longitudinal members carry load
- Each member: I ≈ 0.04 in⁴, S ≈ 0.08 in³ for 1x1 T-slot (approximate, conservative)
- Bending moment at center for 50 lb on one rail: M = 50 * 24 / 4 = 300 lb·in
- Bending stress: σ = M/S = 300 / 0.08 = 3,750 psi
- 6061-T6 yield = 40,000 psi → **safety factor 10.7. Comfortable.**

Deck deflection at center under 150 lb distributed: < 0.1 in. Tent and plywood will not feel any sag.

---

## D. Overhang and DOT rules

| Overhang | Rule | Action |
|---|---|---|
| Front | Driver visibility; most states max 3 ft | Limit to 36 in; never block hood line of sight |
| Rear (3–4 ft) | Red/orange flag 18x18 required daytime | Flag from kit, item 13 in BOM |
| Rear (>4 ft) | Many states require lights at night | Don't drive at night with this overhang |
| Sides | Cannot exceed vehicle width or 6 in past, varies by state | 4 ft sheet is 2 in past each side; OK |

---

## E. Sunroof protection

- 2024 RAV4 XSE sunroof glass spans roughly 12–34 in from front of roof, centered laterally
- Crossbar 1 placed at ~8 in from front (in front of sunroof)
- Crossbar 2 placed at ~46 in from front (behind sunroof)
- Platform spans both; deck stiffness keeps point loads off glass center

**Rule:** Never sit or stand on the platform when stationary unless directly over a crossbar.
