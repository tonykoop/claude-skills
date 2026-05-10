# New Instruments — v4 additions

This reference covers the instrument families that exist in
`Musical Instruments V2.xlsx` but were not enumerated in v3's
`acoustic-models.md` or `queued-instruments.md`. Each entry has the
governing acoustic model, the workbook sheet to consult, key formulas,
and the family-specific empirical corrections (where Tony has
measurements).

## Quick index

| Instrument | Workbook sheet | Governing model | Status |
|---|---|---|---|
| Handpan | `Handpan` | Coupled membrane + Helmholtz | Designed |
| Steel Pan | `Steel Pan` | Plate (vibrating area) | Designed |
| Tubular Bells | `Tubular Bells` | Free-free beam (tube) | Designed |
| Cajón | `Cajón` | Helmholtz + plate front | Designed |
| Glockenspiel | `Glockenspiel` | Free-free beam (metal) | Designed |
| Rainstick | `Rainstick` | Friction noise (cascade) | Designed |
| Steel Tongue Drum | `Steel Tongue Drum` | Cantilever beam (steel) | Designed |
| Wood Shell Tongue Drum | `Wood Shell Tongue Drum` | Cantilever + Helmholtz coupling | Designed |
| Ceramic Tongue Drum | `Ceramic Tongue Drum` | Cantilever (ceramic) + Helmholtz | Research |
| Ceramic Electric Violin | `Ceramic Electric Violin` | Solid body + pickup | Research |
| Great Highland Bagpipe | `Great Highland Bagpipe` | Coupled reed + drone pipe | Research |
| Khaen | TBD | Side-branch free reed + open-open pipe | Research |
| Duntong | `Duntong` | Cantilever beam (hybrid stave) | Research |

## Handpan

**Governing model:** Coupled membrane + Helmholtz. Each tone field on
the upper shell behaves as a vibrating plate with a defined area; the
shell-and-port system underneath couples Helmholtz-style. The
fundamental of each tone field is dominated by plate dynamics; the
warmth/sustain comes from the Helmholtz coupling.

**Key formulas (first-order):**

- Plate fundamental: `f₁ ≈ (κ / (2π)) · (h / a²) · √(E / (ρ · (1 - ν²)))`
  where `h` is plate thickness, `a` is the effective radius of the tone
  field, `E`/`ρ`/`ν` are steel properties, `κ` is a clamped/free-edge
  coefficient (~10.2 for free-free disk first mode).
- Helmholtz of the body: `f_H = (c / 2π) · √(A / (V · L_eff))` for the
  shell port at the bottom — A is port area, V is enclosed volume,
  L_eff is the corrected port length.

**Workbook sheet:** `Handpan`. 50+ formula cells, 39 blue input cells.
Tony's input convention is "blue = your knob, formula = derived" —
honor it.

**Empirical corrections:** None yet. Handpan tuning is dominated by
hammered tone-field shape; the formulas above are coarse first-order
sanity checks, not predictions accurate to <30 cents.

**Reference repo:** No done-bar repo yet for handpans. The closest
analog is `tonykoop/tongue-drum` for the cantilever-beam vs Helmholtz
coupling pattern.

## Steel Pan

**Governing model:** Plate. Each note region on the steel pan is a
hammered/tempered area whose vibration is dominated by plate bending
modes. The pan's curvature defines per-note effective area and tension.

**Key formulas:** Use the same plate formula as Handpan. The steel-pan
tradition relies heavily on tuning by ear — use formulas as a
sanity-check on tone-region area, not as primary tuning input.

**Workbook sheet:** `Steel Pan`. 89 formulas, 73 blue cells.

**Empirical corrections:** None. Tony's steel pan work is in the
research stage.

## Tubular Bells

**Governing model:** Free-free beam, but a tube — the wave equation is
the same as a marimba bar (`λ₁ = 4.730`) with the moment of inertia
calculated for a hollow cylinder. The tube is suspended at the antinode
points (~22.4% from each end) for a free-free condition.

**Key formulas:**

- `f₁ = (4.730² / (2π · L²)) · √(E · I / (ρ · A))`
- For a thin-walled tube: `I = π · (OD⁴ - ID⁴) / 64`; `A = π · (OD² - ID²) / 4`
- Simplified: `f₁ ∝ √(OD² + ID²) / L²` for a fixed material.

**Workbook sheet:** `Tubular Bells`. 99 formulas, 20 blue cells.

**Suspension:** The chime tube is suspended at the antinode points
(0.224 · L from each end). Top antinode is the first node; the lower
antinode is where the striker hits.

## Cajón

**Governing model:** Helmholtz + front plate. The cajón is a box with a
back-port. The front plate (tapa) is thin plywood; striking it excites
plate modes that couple to the box volume via Helmholtz. The thump is
the Helmholtz fundamental; the snap is the plate.

**Key formulas:**

- Helmholtz: `f_H = (c / 2π) · √(A / (V · L_eff))`. For typical
  full-size cajón (V ≈ 18 L, A ≈ port hole area, L_eff ≈ wall thickness +
  end correction), f_H ≈ 80–110 Hz.
- Front plate plate modes: Use the plate formula above; tapa thickness
  3–4 mm, area ~0.16 m², gives plate first mode ~150–200 Hz.

**Workbook sheet:** `Cajón`. 8 formulas, 23 blue cells.

## Glockenspiel

**Governing model:** Free-free beam, metal (typically steel or
aluminum). Same equation as marimba bars; metal K-constant table below.

**Key formulas:** `f₁ = K · t / L²` where K is the metal K-constant.

**Metal K-constants (imperial, t in inches, L in inches, f in Hz):**

| Metal | E (GPa) | ρ (kg/m³) | K (approx) |
|---|---|---|---|
| Aluminum 6061 | 69 | 2700 | 35,500 |
| Steel 1018 | 200 | 7870 | 35,400 |
| Brass | 100 | 8500 | 24,200 |

Note: K values are similar between aluminum and steel because the
density-stiffness ratio is similar; the practical difference is mass and
sustain. Aluminum is lighter and rings longer; steel is heavier with a
sharper attack.

**Workbook sheet:** `Glockenspiel`. 94 formulas, 16 blue cells.

## Rainstick

**Governing model:** Friction-noise cascade. Not tonal — the rainstick
produces a noise spectrum dominated by impact statistics of seeds/beans
hitting internal pegs as the tube is rotated. Useful design parameters
are tube length, seed/peg density, and tube material (wood vs cardboard
vs cactus).

**Key formulas:** None traditional. Design instead targets:

- *Sound duration:* L / (g · sin θ)^0.5 where θ is tilt angle ~30°,
  giving full-rotation sound for 6–12 s.
- *Frequency content:* Higher peg density → finer "rain" sound; coarser
  peg density → more distinct "drops."

**Workbook sheet:** `Rainstick`. 13 formulas, 15 blue cells. Most cells
are empirical (peg count, seed mass, tube length).

## Steel Tongue Drum

**Governing model:** Cantilever beam, steel. Same equation as wood
tongue drum; substitute the steel modulus and density.

**Key formulas:**

- `f = K_steel · t / L²` where K_steel ≈ 35,400 (see Glockenspiel
  table).
- For a steel tongue with a cut isolating it from the surrounding plate,
  treat as a fixed-free cantilever.

**Workbook sheet:** `Steel Tongue Drum`. 71 formulas, 40 blue cells.

**Reference repo:** `tonykoop/tongue-drum` — the wood version. The
physics is the same family; just swap the K-constant.

## Wood Shell Tongue Drum

**Governing model:** Cantilever beam (top tongue) + Helmholtz (shell
chamber). The tongue drives a fundamental; the Helmholtz chamber
underneath provides sustain and warmth at a tuned frequency near the
tongue fundamental (typically -20% to +20% of tongue fundamental for
the strongest coupling).

**Key formulas:**

- Tongue: `f = K · t / L²` (use wood K-constants from
  `acoustic-models.md`).
- Shell Helmholtz: `f_H = (c / 2π) · √(A / (V · L_eff))`.

**Sweet spot:** Helmholtz tuning at 0.85 to 1.15 of the tongue
fundamental gives the strongest coupling. Tony's empirical observation:
tuning the chamber to ~0.95 · f_tongue gives the warmest sustain
without overwhelming the tongue's fundamental.

**Workbook sheet:** `Wood Shell Tongue Drum`. 70 formulas, 46 blue
cells.

**Reference repo:** `tonykoop/tongue-drum` is the canonical example.

## Ceramic Tongue Drum

**Governing model:** Cantilever beam (ceramic) + Helmholtz (chamber).

**Notes:** Ceramic K-constants vary widely with formulation and firing
temperature. Use as a *first-order estimate*, not a precise prediction.
Slip-cast earthenware fired to cone 6 typically gives K ≈ 15,000–18,000
(rough estimate, mark as `derived estimate` in the design sheet).

**Workbook sheet:** `Ceramic Tongue Drum`. 66 formulas, 23 blue cells.

**Reference repo:** None yet. Closest done-bar is `tonykoop/udu` for the
slip-cast process and `tonykoop/tongue-drum` for the cantilever physics.

## Ceramic Electric Violin

**Governing model:** Solid body + pickup. Body shape determines mass
and damping; pickup converts string vibration to electrical signal.
No acoustic chamber — the body is solid (or near-solid) ceramic.

**Notes:** Tuning is dominated by the strings (Mersenne-Taylor). The
body's job is mechanical: hold the strings at fixed scale length, allow
ergonomic playing position, transmit vibration to the pickup.

**Workbook sheet:** `Ceramic Electric Violin`. 0 formulas (purely
geometry); 20 blue cells.

## Great Highland Bagpipe

**Governing model:** Coupled reed + drone pipe (cylindrical or conical
bore). The reed sets a fundamental driving frequency; the bore length
and bore profile determine the drone's stable note.

**Key formulas:**

- Drone (cylindrical bore, closed at reed end, open at far end —
  effectively a stopped pipe): `f = c / (4 · L_eff)`.
- Chanter (conical bore with reed): More complex; the conical bore
  makes the chanter behave like an open-open pipe (`f = c / 2L_eff`)
  to first approximation.

**Workbook sheet:** `Great Highland Bagpipe`. 36 formulas, 78 blue
cells.

## Duntong

**Governing model:** Cantilever beam (hybrid wood-stave construction).
The duntong is Tony's hybrid — a stave-walled tongue drum where the
shell is segmented and the top plate is solid. Tongue physics same as
wood shell tongue drum; shell construction is segmented like a djembe
or conga.

**Workbook sheet:** `Duntong`. 90 formulas, 35 blue cells.

**Reference repos:** `tonykoop/tongue-drum` for the tongue physics,
`tonykoop/djembe` or `tonykoop/conga` for the segmented construction.

## Khaen

**Governing model:** Side-branch free reed exciting an open-open pipe for a
tradition-faithful khaen. Use `acoustic_law=side_branch_reed`, document
`end_condition=both_pipe_ends_open`, and set `reed_source_role=exciter` unless
measurements show stronger reed-pipe coupling.

**Key formulas:**

- Traditional long pipe: `f = c / (2 * L_eff)`, with open-end correction at
  both pipe ends. The reed window is a side branch near the windchest; it does
  not make the pipe a closed-open reed-at-end tube.
- Compact study module: a reed-at-end or blocked-channel proof of concept may
  use `closed_open` or `free_reed_coupled_pipe`, but label it as a compact
  experiment and keep it separate from the traditional khaen family rows.

**Workbook sheet:** TBD. No canonical workbook sheet exists yet.

**Cultural note:** Frame CNC work as an adaptation and measurement study, not
as an improvement over Lao/Isan craft practice. Preserve traditional model
language separately from compact shop experiments.

**Reference repo:** TBD. Round 7 Irene khaen packets are the current seed
artifacts for this entry.

## How to use this reference

When the orchestrator dispatches you (the acoustician) to size a Steel
Pan or scale a Handpan family, this is your starting point — read the
relevant section, then go to the workbook sheet to see Tony's existing
input/formula structure. Don't override his blue-cell convention; the
v4 priorities include "stronger workbook + spreadsheet integration,"
and that means honoring the existing structure.

If the user asks for an instrument *not* in this list and *not* in v3's
`acoustic-models.md` or `queued-instruments.md`, escalate: ask Tony
which family it should belong to before guessing.
