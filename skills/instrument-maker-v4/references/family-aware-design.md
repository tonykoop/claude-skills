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

## family-spec.csv format

Every family-aware packet has a `family-spec.csv` that drives the
auto-generators. The format is one row per family member:

```csv
member_id,target_hz,target_note,scale_label,acoustic_law,end_condition,reed_source_role,cad_dimension_basis,predicted_length_in,predicted_width_in,predicted_height_in,predicted_volume_cuin,wood_species,k_constant,k2_correction,notes
TNG-S-D4,294.0,D4,Pentatonic D minor,cantilever_beam,plate_tongue_fixed_free,none,physics_derived,8.0,8.0,3.5,224.0,Padauk,24438,0,Small drum (magazine baseline)
TNG-M-A3,220.0,A3,Pentatonic D minor,cantilever_beam,plate_tongue_fixed_free,none,physics_derived,12.0,12.0,5.0,720.0,Padauk,24438,0,Medium drum
TNG-L-D3,147.0,D3,Pentatonic D minor,cantilever_beam,plate_tongue_fixed_free,none,physics_derived,16.0,16.0,7.0,1792.0,Padauk,24438,0,Large drum (max practical for shop CNC bed)
```

The columns are always: `member_id` (a stable per-member identifier),
`target_hz`, `target_note`, `acoustic_law`, `end_condition`,
`reed_source_role`, `cad_dimension_basis`, plus family-specific dimension
columns, plus material and correction columns, plus `notes`.

`acoustic_law` is a required controlled value. Use the vocabulary from
`references/acoustic-models.md`: `open_open`, `closed_open`, `stopped_pipe`,
`side_branch_reed`, `free_reed_coupled_pipe`, `empirical_only`, or
`unknown_requires_measurement`. When a family uses a non-pipe model, use the
same explicit law names used by the acoustic reference and validator:
`helmholtz`, `helmholtz_dual`, `cantilever_beam`, `free_free_beam`,
`membrane`, `mersenne_taylor_string`, or `hybrid_compound`.

`cad_dimension_basis` records whether CAD dimensions are `physics_derived`,
`empirically_seeded`, or `measurement_required`. If it is
`physics_derived`, the CAD/OpenSCAD/SolidWorks table must use the same law
declared in `acoustic_law`. If the row uses `empirical_only` or
`unknown_requires_measurement`, set `cad_dimension_basis` to
`measurement_required` unless the packet includes measured source dimensions.

For reed instruments, keep `reed_source_role` explicit:

- `none` for edge-blown pipes, strings, beams, membranes, and pure Helmholtz
  vessels.
- `exciter` when the reed drives a pipe but pipe boundary conditions set the
  length law.
- `pitch_source` when the reed itself primarily sets pitch.
- `coupler` when the reed, chamber, and pipe must be validated as a coupled
  system.
- `unknown_requires_measurement` when the role is not yet known.

### Khaen family example

Use separate rows or separate packets for a traditional khaen model and a
compact study model. Do not let the compact quarter-wave study silently stand
in for the traditional instrument.

```csv
member_id,target_hz,target_note,scale_label,acoustic_law,end_condition,reed_source_role,cad_dimension_basis,predicted_length_mm,reed_window_position,notes
KHN-HW-G3,196.0,G3,Lao/Isan khaen pipe,side_branch_reed,both_pipe_ends_open,exciter,physics_derived,866.9,near_windchest_midline,Traditional long pipe: open-open resonator with side-wall reed
KHN-QW-G3,196.0,G3,Compact reed study,closed_open,reed_block_closed_end,exciter,empirically_seeded,433.4,reed_at_end,Quarter-wave experiment; not a traditional khaen pipe
```

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
