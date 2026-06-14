# Family-Aware Design — v4 (Tier 3 #9)

v3 produced family-aware *packets* (one packet describing S/M/L/XL
members of a family). v4 introduces *family-aware design* — when a user
asks for a new family, the skill proposes the family scaling law,
generates members at acoustically-reasonable size ratios, and emits a
`family-spec.csv` that drives N packet generations in one shot.

This is the brainstorm's "70 repos becomes 200 without 200x the work"
move.

## The general flow

1. User: "Design a vessel-flute family in C major: tonic, dominant,
   octave."
2. The acoustician picks the model (Helmholtz for vessel flutes), reads
   `references/family-aware-design.md` (this file) for the scaling law,
   and proposes member fundamentals.
3. The orchestrator emits `family-spec.csv` — one row per family
   member with target frequency, predicted dimensions, scale offset
   table.
4. `scripts/generate_build_packet.py` is invoked once per row to emit
   N packets (typically 3–5 for a family).
5. `scripts/generate_drawings.py` and `scripts/generate_capstone_docs.py`
   are run on each packet.
6. Optionally, `scripts/generate_site.py` produces a family-overview
   page with each member linked.

## Scaling laws

### Vessel flutes — Helmholtz scaling

For a Helmholtz resonator, `f ∝ √(A / (V · L_eff))`. Holding port area
A constant and scaling chamber volume V uniformly (L³ scaling), the
fundamental drops as V^(-1/2) → L^(-3/2). To go from f₀ to f₁, scale
linear chamber dimensions by `(f₀ / f₁)^(2/3)`.

Practical implication: a vessel flute family with members at C5, F5, A5
needs chamber volumes in ratios `1 : (262/349)^2 : (262/440)^2 ≈
1 : 0.563 : 0.355` and linear scales `1 : 0.825 : 0.706`.

If holding port-to-chamber proportions constant (more typical for
ergonomic playability), simply linear-scale all dimensions by
`(f₀ / f₁)^(2/3)`.

### Marimba bars — cantilever / free-free beam scaling

For a free-free beam, `f₁ = K · t / L²`. Holding `t` (bar thickness)
constant — typical for a marimba where bar thickness is set by the
chosen wood species and undercut depth — `L ∝ √(t · K / f)`. To go
from f₀ to f₁, scale L by `√(f₀ / f₁)`.

Practical implication: a 1-octave run from C4 (262 Hz) to C5 (524 Hz)
needs the C5 bar at `√(262/524) = 0.707` × the C4 bar length.

For a *family* of marimbas at different keys (e.g., a soprano marimba
in C and a tenor marimba in F), all bars in each instrument shrink by
the same ratio when changing key.

### Stave drums — segmented scaling

For a segmented stave drum at fixed segment count N, the miter angle θ
is fixed (`180°/N`); the stave edge-length scales linearly with the
outer diameter (`edge = π · OD / N`). Family members are typically
defined by:

- Same OD, different shell heights (different fundamental Helmholtz
  modes).
- Same height, different OD (proportionally different note based on
  combined membrane + Helmholtz coupling).
- Both (true family scaling).

Acoustically, a segmented drum's fundamental is dominated by the
membrane (head) tension and OD; the stave construction is a structural
choice, not an acoustic one. Family scaling is therefore by head
diameter — same membrane tension, different OD → fundamental ∝ 1/OD.

### Tongue drums — cantilever beam scaling

Same as marimba bars, but applied to tongues cut into a top plate. For
a family of tongue drums where the *plate* scales but each tongue's
length and thickness are individually tuned, the family scaling is
implicit in the per-tongue cantilever formula.

For a family where the *whole drum* scales (S/M/L sizes of the same
scale), tongue lengths within each drum scale by `√(f₀ / f₁)` between
the smallest and largest drum in the family, holding wood species and
plate thickness constant.

### Folded stopped-pipe drones — quarter-wave centerline scaling

For a folded stopped-pipe drone, the acoustic path is still a
quarter-wave stopped pipe. The fold pattern changes packaging,
serviceability, wall friction, and bend losses; it does not remove the
need for a straight reference tube.

Use:

```text
c = 331.3 * sqrt(1 + T_C / 273.15)
L_eff = c / (4f)
area_rect = duct_width_mm * duct_height_mm
d_eq = 2 * sqrt(area_rect / pi)
L_geom_first_pass = L_eff - 0.82 * d_eq
```

Family scaling is by target frequency (`L ∝ 1/f`) at the chosen warm
playing temperature. Generate a folded centerline station CSV for each
member, then run `scripts/generate_folded_drone_dxf.py` to produce a
DXF starter. Keep `tuning_tail_mm` explicit so low drones can be trimmed
or sleeve-tuned after leak testing.

## family-spec.csv format

Every family-aware packet has a `family-spec.csv` that drives the
auto-generators. The format is one row per family member.

### Required columns (v4.4+)

As of v4.4 (issue [#73](https://github.com/tonykoop/claude-skills/issues/73)),
every `family-spec.csv` must include three columns that record the model
choice and dimension provenance up front, so a downstream reader can
verify the physics without re-deriving it from prose:

| Column                  | Required | Type / values                                                                 | Purpose                                                                  |
|-------------------------|----------|-------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| `acoustic_law`          | yes      | One of: `open_open`, `closed_open`, `stopped_pipe`, `side_branch_reed`, `free_reed_coupled_pipe`, `empirical_only`, `unknown_requires_measurement` | Declares the governing physics. See `references/acoustic-models.md` § *Reed boundary-condition decision tree*. |
| `end_condition`         | yes      | Free text but typed: `both_ends_open`, `one_end_closed_reed`, `one_end_closed_stopped`, `vented_chamber`, `closed_cavity_helmholtz`, `n_a_empirical` | Boundary condition at the pipe ends. Cross-checked against `acoustic_law` by the validator. |
| `dimension_provenance`  | yes      | One of: `physics_derived`, `empirically_seeded`, `measurement_required`       | Whether predicted dimensions came from the formula, were seeded from prior measurements, or still need a measurement before CAD/CAM. |

Other historical columns remain valid (member_id, target_hz, target_note,
wood_species, etc.).  The validator only adds *requirements* — it does
not remove or rename pre-v4.4 columns.

### Example (free-reed instrument — khaen family)

```csv
member_id,target_hz,target_note,acoustic_law,end_condition,dimension_provenance,predicted_L_geom_mm,wood_species,notes
KHN-007-G3,196.00,G3,side_branch_reed,both_ends_open,physics_derived,866.9,Hard Maple,Traditional Lao khaen architecture; reed in pipe side wall at central tao
KHN-007-A3,220.00,A3,side_branch_reed,both_ends_open,physics_derived,771.4,Hard Maple,
KHN-Q-007-G3,196.00,G3,closed_open,one_end_closed_reed,physics_derived,427.0,Hard Maple,Quarter-wave sister variant; reed at windchest end (adapted melodica architecture)
KHN-POC-2-C4,261.63,C4,unknown_requires_measurement,n_a_empirical,measurement_required,,Cherry,Donor melodica reed must be measured before pipe length is finalized
```

This example distinguishes the *traditional long-pipe side-branch* khaen
from the *compact quarter-wave experimental* sister build — exactly the
pair Round 7 lane Irene exposed.

For a new sheng, hulusi, bawu, khaen, or chalumeau-style reed exploration,
start with `references/free-reed-khaen-exploration.md`. Use
`acoustic_law=unknown_requires_measurement` for donor reeds or uncertain
coupling until the P0 reed coupon records reed-alone pitch, pull-down cents,
onset pressure, leak status, and blow/draw behavior. For chalumeau-style
beating-reed pipes, use `closed_open` or `stopped_pipe` only when the packet
can state which end condition the reed geometry creates.

### Example (folded stopped-pipe drone family)

```csv
member_id,target_hz,target_note,acoustic_law,end_condition,dimension_provenance,bore_shape,duct_width_mm,duct_height_mm,equivalent_diameter_mm,centerline_length_mm,tuning_tail_mm,straight_reference_length_mm,notes
FDR-E2,82.41,E2,stopped_pipe,one_end_closed_stopped,physics_derived,rectangular_folded_duct,52,42,52.7,1200,180,1021,Compact E2 proof mule; untrimmed centerline includes removable tail allowance
FDR-G2,98.00,G2,stopped_pipe,one_end_closed_stopped,physics_derived,rectangular_folded_duct,48,40,49.4,1020,160,860,Same fold grammar scaled upward with removable tail allowance
```

Pair each folded-drone family row with a centerline station CSV:

```csv
station_id,x_mm,y_mm,width_mm,height_mm,bend_radius_mm,role,note
S0,0,0,52,42,0,mouthpiece,removable mouthpiece
S1,360,0,52,42,75,fold,first run
S2,360,160,54,42,75,fold,return turn
S3,20,160,54,42,75,fold,return run
S4,20,320,56,42,75,tuning_tail,tail sleeve starts near warm E2 length
S5,200,320,56,42,0,closed_end,temporary tail cap
```

The station CSV is the source for `generate_folded_drone_dxf.py`; it is
not a substitute for `family-spec.csv`, which remains the acoustic and
validation summary.

### Example (idiophone family — tongue drum, no `acoustic_law` requirement)

For non-pipe instruments (idiophones, membranes, strings), `acoustic_law`
is not required because the validator only enforces it on free-reed and
wind-instrument families.  Idiophones can leave the column out or fill
`empirical_only` if they need to.

```csv
member_id,target_hz,target_note,scale_label,predicted_length_in,wood_species,k_constant,k2_correction,notes
TNG-S-D4,294.0,D4,Pentatonic D minor,8.0,Padauk,24438,0,Small drum (magazine baseline)
TNG-M-A3,220.0,A3,Pentatonic D minor,12.0,Padauk,24438,0,Medium drum
TNG-L-D3,147.0,D3,Pentatonic D minor,16.0,Padauk,24438,0,Large drum
```

### Validator behavior

`scripts/validate_acoustic_law.py` checks every `family-spec.csv` it is
pointed at:

- **Hard fail** (`exit 1`) if the family is wind/free-reed and the row
  is missing `acoustic_law`, `end_condition`, or `dimension_provenance`,
  or if `acoustic_law` is not in the controlled vocabulary.
- **Hard fail** if `acoustic_law` ↔ `end_condition` are inconsistent
  (e.g. `acoustic_law=side_branch_reed` paired with
  `end_condition=one_end_closed_reed`).
- **Hard fail** if `dimension_provenance=physics_derived` but the
  declared formula's predicted length disagrees with the stored
  `predicted_L_geom_mm` by more than 1 mm or 0.5 % at room temp.
- **Warn** (`exit 0`, finding emitted) if `acoustic_law=
  unknown_requires_measurement` so the maker can ship the planning
  packet, then re-run after measuring.
- **Skip** rows for non-wind families (idiophones, strings, membranes).

The columns are always: `member_id` (a stable per-member identifier),
`target_hz`, `target_note`, plus the v4.4 required columns above (when
applicable), plus family-specific dimension columns, plus material and
correction columns, plus `notes`.

## How generators read family-spec.csv

- `generate_build_packet.py` — generates one packet per row when given
  `--family-spec /path/to/family-spec.csv` instead of `--instrument-id`.
- `generate_drawings.py` — emits one SVG per row.
- `generate_openscad_starter.py` — emits one parametric OpenSCAD master
  for the family, with the row data pre-loaded as configurations.
- `generate_capstone_docs.py` — auto-fills the *Family Spec* slide in
  the deck and the *Family Overview* section in the print packet.
- `generate_site.py` — emits a family-overview page that links to each
  member's page.

## Quality gates for family design

- [ ] All members within the family share a *consistent* scaling law
      — don't mix Helmholtz scaling for one member and cantilever
      scaling for another.
- [ ] The acoustically-reasonable size range is bounded:
  - Vessel flutes — chamber volume from 50 mL (small ocarina) to 5 L
    (large gemshorn). Beyond that, plate vibration dominates.
  - Marimba bars — bar length from 4" (high-pitched) to ~28" (low,
    edge of practical CNC stock).
  - Stave drums — OD from 8" (small ashiko) to ~24" (large djembe);
    larger gets tone but adds stave count and weight quickly.
- [ ] Material choice is consistent across the family (avoid mixing
      Padauk and cedar in one family unless the user explicitly asks
      for a species sweep).
- [ ] Each member's predicted fundamental is within the playable range
      for the chosen scale (no D9 piccolos by accident, no C0
      sub-bass).
- [ ] The done-bar reference repo for the family is named in the
      family-spec's `notes` column.

## When to dispatch family-aware design

Dispatch family-aware design (vs single-instrument design) when the
user says any of:

- "Family of [instrument]"
- "S/M/L of [instrument]"
- "[Instrument] in three keys"
- "Scale this [instrument] up/down"
- "Make a [instrument] in different sizes"
- "[Instrument] family in [scale]"

When the prompt is ambiguous, ask before generating: a single packet is
much cheaper than three packets the user didn't want.
