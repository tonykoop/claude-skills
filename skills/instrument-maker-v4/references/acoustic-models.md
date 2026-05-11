# Acoustic Models

Use these models as design starting points. Put formulas in spreadsheet cells or Wolfram variables so a future builder can change key, material, temperature, or scale length without rebuilding the sheet.

## Reed boundary-condition decision tree (READ FIRST for any free-reed instrument)

> Added in v4.4 to close [#73](https://github.com/tonykoop/claude-skills/issues/73). Round 7 TwinGrid lane Irene showed two specialists confidently picking *different* governing acoustic models for the same instrument (khaen) — one quarter-wave, one half-wave — both internally consistent, both passing self-review. The fix is to make the model choice an explicit, machine-checkable field rather than an implicit specialist judgment.

Before computing any pipe length for a free-reed or reed-coupled pipe
instrument (khaen, sheng, sho, harmonica, melodica, accordion, bawu,
harmonium, reed organ, hulusi, chalumeau-style reed pipes, hybrid reed
adaptations), the acoustician specialist **must** answer the questions in this
tree and record the answer as `acoustic_law` in the packet's
`family-spec.csv`. The validator (`scripts/validate_acoustic_law.py`) refuses
to ship a packet that omits or invents the value.

```
Is this a free-reed instrument? ─── NO ───────► follow the standard
                                                flute/edge/string trees
                                                below
                                  └── YES
                                       ▼
Where does the reed sit relative to the pipe?

  (a) Reed is the closed end of the pipe — pipe extends in one
      direction from the reed plate; the windchest seats behind the
      reed.
        → acoustic_law = closed_open
        → f = c / (4 * L_eff)
        → end correction at the open end only (≈ 0.6 * r_eff)
        → examples: melodica with single-direction channel, sheng-style
          upright pipes with reed at base, single-pipe accordion blocks,
          compact chalumeau-style control pipes where the reed end is
          acoustically closed

  (b) Reed sits in the SIDE WALL of the pipe near its mid-point;
      both pipe ends are open to room air. Reed acts as a side branch.
        → acoustic_law = side_branch_reed (also accept: free_reed_coupled_pipe)
        → f = c / (2 * L_eff)
        → end correction at BOTH open ends (≈ 0.6 * r_eff each)
        → examples: TRADITIONAL LAO KHAEN, sheng (with both pipe ends open),
          traditional bawu, hulusi mid-pipe free-reed configurations

  (c) Reed at the closed end with a vent/fingerhole that controls
      whether the pipe couples to the reed (vent open = silent; vent
      closed = pipe speaks at quarter-wave).
        → acoustic_law = closed_open  (with vent-controlled effective length)
        → f = c / (4 * L_eff_vented)  where L_eff_vented depends on
          whether the vent is closed
        → examples: harmonica chambers, vented-reed adaptations

  (d) Reed in a Helmholtz resonator with no significant pipe length
      (chamber dimension dominates over any tubular extent).
        → mark as Helmholtz; do not use the free-reed pipe tree.
        → examples: kazoos, mirlitons, some accordion reed banks

  (e) The instrument is being designed empirically (from measurements
      of a built prototype) without a clean closed-form model.
        → acoustic_law = empirical_only
        → mark every dimension in family-spec.csv as
          dimension_provenance = empirically_seeded or
          measurement_required

  (f) The acoustician has not yet decided OR a measurement of the
      donor reed's free pitch is required before pipe length can be
      computed.
        → acoustic_law = unknown_requires_measurement
        → packet ships with a measurement plan (see
          references/family-aware-design.md)
        → validator emits a WARN (not a hard fail) so the maker can
          ship the planning packet, then re-run after measuring.

  (g) Reed at a stopped end (traditional reed-cap and reed-pipe ranks
      where the reed itself is the stop).
        → acoustic_law = stopped_pipe
        → f = c / (4 L_eff)  (sounds an octave below open-open of same length)
        → examples: traditional reed organ ranks, some accordion bass,
          chalumeau-style beating-reed pipes with a stopped reed end
```

### Controlled vocabulary

The `acoustic_law` field accepts exactly these values; the validator rejects any other:

| Value                              | Meaning                                                  | Pipe-length formula              |
|------------------------------------|----------------------------------------------------------|----------------------------------|
| `open_open`                        | Open both ends, edge or air-jet excitation               | `f = c / (2 L_eff)`              |
| `closed_open`                      | One closed end (reed-stop, lip-buzz, or stopped flue)    | `f = c / (4 L_eff)`              |
| `stopped_pipe`                     | Stopped at one end, reed/lip excitation                  | `f = c / (4 L_eff)` (octave low) |
| `side_branch_reed`                 | Reed in pipe side wall, both ends open                   | `f = c / (2 L_eff)`              |
| `free_reed_coupled_pipe`           | Synonym for `side_branch_reed`; explicit physical model  | `f = c / (2 L_eff)`              |
| `empirical_only`                   | No closed-form model; dimensions from measurement        | n/a — measurement required       |
| `unknown_requires_measurement`     | Decision deferred until a reed/cavity is measured        | n/a — emits validator WARN       |

`open_open` is for edge-tone flutes (NAF, transverse, shakuhachi) and remains the default for that family. `closed_open`, `stopped_pipe`, `side_branch_reed`, and `free_reed_coupled_pipe` cover the reed and free-reed cases. `empirical_only` and `unknown_requires_measurement` are honest-uncertainty escape hatches; both must come with a justifying note in the packet's `design.md`.

### Reed-family routing notes

- **Sheng/khaen side-branch families:** use `side_branch_reed` or
  `free_reed_coupled_pipe` only when the reed sits in the side wall and both
  pipe ends remain open. DXF notes must identify the reed window, socket pitch
  map, and both open pipe ends.
- **Hulusi/bawu donor-reed or uncertain-coupling families:** use
  `unknown_requires_measurement` until the packet records reed-alone pitch,
  pull-down, onset pressure, blow/draw behavior, leak status, and the measured
  pipe coupling. Do not promote supplier reed labels or concept images into
  build dimensions.
- **Chalumeau-style beating-reed pipes:** use `closed_open` when the reed end
  acts as the closed end of a quarter-wave pipe, or `stopped_pipe` when the
  design is intentionally modeled as a stopped reed pipe. These are reed-pipe
  validation cases even though they are not free-reed mouth organs.

### Exploration packet guard

For khaen/khen, sheng, sho, hulusi, bawu, chalumeau-style reed pipes, and
donor-reed experiments, read
`references/free-reed-khaen-exploration.md` before creating CAD. A planning
packet may ship with `acoustic_law=unknown_requires_measurement`, but a
family-true packet must measure a P0 reed coupon, choose `side_branch_reed` or
`closed_open`/`stopped_pipe` as appropriate, and pass
`scripts/validate_acoustic_law.py` before pipe lengths are treated as build
dimensions.

Unsupported pipe-law claims must be caught in one of two places:

- `family-spec.csv` uses the controlled `acoustic_law` values above, and the
  validator rejects invented values such as `quarter_wave_closed_open`.
- Prose, DXF notes, and drawing briefs must use the same vocabulary so a
  mouth-organ drawing cannot quietly claim a different law than the CSV.

### Why this exists

Round 7 TwinGrid lane Irene blind A/B run produced two khaen packets with different governing models. Both passed self-review. Without a machine-checkable invariant, the divergence was undetectable from the deliverables alone. By forcing the model choice into a typed field that the validator checks against the actual computed dimensions (see `scripts/validate_acoustic_law.py`), this class of "silent wrong physics" error is caught at packet generation time instead of at first-build time.

## Empirical-correction guard rules (READ FIRST)

The corrections in this file (Tony's NAF K2 bore corrections, scale offsets, K-constant tables) are **physics-model-specific**. Misapplying them produces wrong predictions and undermines the whole packet's credibility. Before applying any empirical correction, check the model:

- **NAF K2 bore corrections** (the `0.875 in → +0.4%`, `≥1.125 in → +1.0% to +1.6%`, `≤0.75 in → −0.7% to −6.0%` table below) apply **ONLY to open-open pipe NAFs in Tony's bore-diameter range (0.5–1.25 in)**. They are derived from 150+ empirically tuned NAFs. They do **NOT** apply to:
  - Vessel resonators (ocarina, udu, gemshorn, ceramic-tongue-drum) — the governing model is Helmholtz, not open-pipe, and bore diameter is not a parameter.
  - Cantilever-beam idiophones (wooden tongue drums, marimba, kalimba, glockenspiel) — the governing model is `f₁ ≈ 0.162·(h/L²)·√(E/ρ)`, K2 is irrelevant.
  - Stopped pipes with non-NAF embouchure (didgeridoo, panpipes, duduk) — different end-correction regime.
  - Coupled-mode resonators (udu mouth+side, dual-tongue tongue drums) — coupling term dominates the single-mode correction.
- **Scale-offset tables** (centsoffsets-by-key, hole-area-curves) are NAF-family-specific and should not be ported across families without validation.
- **Material K-constants for cantilever beams** (the wood-species table in the cantilever section) are species-specific and only apply to free-free / fixed-free beam excitation. They are not relevant to open-pipe woodwinds or vessel resonators.

When in doubt, apply the model formula *without* corrections, mark the result as a "first-order estimate," and add a row to `validation.csv` for empirical correction post-prototype. **Do not invent corrections that aren't in this file.** If a future instrument needs a new empirical correction, add it here with the bore/length/material range it was measured over and the count of prototypes used to derive it.

The capstone deck's Physics Model slide should surface the governing model in plain text. If the user/agent goes to apply a K-constant or K2 correction on that slide, this guard rule should be the first thing they check.

## Tuning

- Equal temperament: `f = 440 * 2^((MIDI - 69)/12)`, with A4 = MIDI 69.
- Speed of sound: `c = 331.3 * sqrt(1 + T_C/273.15)` m/s, about `343 m/s` or `13552 in/s` at 68 F.
- Cents error: `cents = 1200 * log2(measured_freq / target_freq)`.
- Treat temperature and humidity as validation inputs for wind and wood instruments when tuning precision matters.

## Open-Open Pipes

Use for most transverse/end-blown flutes: Native American style flutes (NAF), Irish flute, shakuhachi, tin whistle, fujara, quena/kena, moseno, pinkullo, tarka, xiao.

```text
f = c / (2 * L_eff)
L_eff = c / (2 * f)
```

- End correction: about `0.6 * radius` at each open end.
- Tone-hole first pass: `distance_from_foot = acoustic_length * (fund_freq / hole_freq)`.
- Larger holes move the effective open point toward the hole center; smaller holes require empirical correction.
- For Tony's NAF sheets, preserve K2 correction columns and compare against built flute data before trusting new bore/key combinations.
- NAF chamber-to-bore ratio target: about `17:1` to `21:1` acoustic length / bore ID.

### Tony's K2 Empirical Corrections (NAF-Specific)

Apply these corrections to the model-predicted hole positions, indexed by bore diameter:

| Bore (in) | Correction | Notes |
| --- | ---: | --- |
| ≥ 1.125 | +1.0% to +1.6% | Model underestimates; lengthen distances |
| 0.875 | +0.4% | Neutral crossover |
| ≤ 0.75 | −0.7% to −6.0% | Model overestimates; shorten distances |

Sweet spot for NAF chamber-to-bore ratio: 17:1 to 21:1 across all keys.

## Stopped Pipes

Use for closed-one-end tubes: didgeridoo, pan flute / siku / zampona tubes, duduk family, some drone concepts.

```text
f = c / (4 * L_eff)
```

- Sounds one octave lower than an open-open pipe of the same length.
- Harmonics are mostly odd: `f`, `3f`, `5f` → hollow tone color.
- End correction applies at the open end only.
- Pan flute first pass: `L = c/(4f) - 0.82 * bore_diameter`.
- Didgeridoo: 2nd resonance at 3f ("toot"), 3rd at 5f; blank length = theoretical + 6" overshoot for tuning trim.
- Duduk: root note = key_name − 3 semitones; body_length ≈ 2412 / freq (inches).
- Document target fundamental and expected higher resonances on the design sheet.

## Conical And Reed Bores

Use caution for bagpipe chanters, shawms, oboes, and tapered folk winds.

- A conical bore behaves closer to an open-open pipe even when reed-excited, but tone holes, reed compliance, and taper dominate intonation.
- Start with measured or traditional bore stations, then fit a spline or station table.
- For Great Highland Bagpipe work, preserve the distinction between modern pitch (often near A = 480 Hz), drone tuning, and equal-temperament convenience tables.

## Cantilever Beams

Use for tongue drums, lamellophones, slit tongues where one end behaves fixed.

```text
f = K * t / L^2
L = sqrt(K * t / f)
```

- Length is the dominant pitch lever (L² in denominator); thickness is linear; width mainly affects volume, stiffness distribution, and sustain — **width does NOT affect frequency**.
- `K = (1.875²)/(2π) × √(E/(12ρ)) / 0.0254` (imperial: t in inches, L in inches → Hz).

### Material K Values (Imperial Cantilever)

| Material | E (GPa) | ρ (kg/m³) | K | Tonewood Rating |
| --- | --- | --- | ---: | --- |
| Padauk | 11 | 745 | 24,438 | ★★★★★ |
| Wenge | 15.8 | 870 | 27,103 | ★★★★★ |
| Hard Maple | 12.6 | 705 | 26,887 | ★★★★ |
| Cherry | 10.3 | 560 | 27,275 | ★★★★ |
| Black Walnut | 11.6 | 610 | 27,734 | ★★★★ |
| White Oak | 12.3 | 770 | 25,419 | ★★★ |
| Baltic Birch Ply | 10.0 | 680 | 24,389 | ★★★ |
| Mahogany | 10.1 | 590 | 26,314 | ★★★★ |
| Western Red Cedar | 7.7 | 370 | 29,013 | ★★★ |

Validate with measured strike data. Slot kerf, bridge geometry, cavity coupling, and grain direction can shift pitch.

## Free-Free Beams

Use for marimba, xylophone, glockenspiel, tubular bar-like idiophones.

- First mode uses `λ_1 = 4.730`; cantilever uses `1.875`.
- Approximate relation: `K_free_free = K_cantilever × (4.730/1.875)² ≈ 6.36 × K_cantilever`.
- Suspension nodes at `22.4%` and `77.6%` of bar length — drill cord/mounting holes here.
- **Marimba arch undercut** (parabolic CNC cut on underside) lowers pitch without shortening:
  `center_thickness = edge_thickness × (target_freq / flat_bar_freq)²`
  Minimum center: 0.25" for structural integrity.
- **Xylophone**: NO arch, shorter/harder bars, tuned to 12th overtone (3:1 ratio).
- **Resonator tubes** (quarter-wave closed pipe): `L_tube = c/(4f) − 0.82 × bore`.

## Helmholtz Resonators

Use for ocarina, udu, cajon ports, handpan gu, resonant boxes, coupled tongue cavities.

```text
f = (c / (2π)) × sqrt(A_neck / (V_chamber × L_eff_neck))
```

- Rectangular neck: `A_neck = slit_width × tongue_width`.
- Cylindrical port: `A_neck = π × (port_diameter/2)²`.
- For a coupled tongue + chamber (resonant box): `V_chamber = π × (pocket_Ø/2)² × pocket_depth`; `L_neck = soundboard thickness`.
- Effective neck length often needs an end correction; document the assumption.
- Coupled tongue/chamber target: Helmholtz frequency within about `±20%` of tongue fundamental for strong coupling — mark "✓ Coupled" or "✗ Detuned" on the design sheet.
- Pocket Ø for coupling: `Ø = 2 × √(V_needed / (π × depth))`.

## Strings (Mersenne–Taylor)

Use for guitar, violin, kora, ngoni, harp, ukulele, whamola, monochords.

```text
f = (1 / (2L)) × sqrt(T / μ)
μ = density × π × (diameter/2)²
diameter = 2 × sqrt(T × g / (density × π × 4 × L² × f²))
```

- In imperial sheets, use `g = 386.4 in/s²`.
- Nylon density reference: `0.04155 lb/in³`; breaking stress reference: about `44,600 psi`.
- **Percent breaking is INDEPENDENT of diameter** in the ideal round-string model:
  `%break = density × 4 × L² × f² / (σ_break × g) × 100`.
- Practical targets: treble nylon often `50–70%` of breaking; bass strings often `10–30%`; wound strings need an effective density factor (typically `2.5×`).

## Membranes And Plates

Use for drums, handpans, steel pans, and ceramic/metal idiophones.

- Treat simple formulas as concept tools only; membrane/plate instruments usually need empirical tuning or FEM for final pitch.
- Drumheads follow Bessel-mode behavior rather than harmonic string ratios.
- Handpan/steel pan tone fields are shaped/tuned zones with multiple partials; document target partials, field geometry, steel thickness, forming method, and post-form tuning process.
- Ceramic/metal tongue drums need material-specific measurement loops; do not transfer wood K constants blindly.

## Scale & Hole Patterns

### Semitone offset tables (from fundamental)

| Scale | Offsets | Instruments |
| --- | --- | --- |
| Pentatonic Minor | +3, +5, +7, +8, +10, +12 | NAF (6 holes) |
| Double Harmonic (Arabic) | +1, +4, +5, +7, +8, +11, +12 | NAF Arabic mode (7 holes) |
| Diatonic Major | +2, +4, +5, +7, +9, +11, +12 | Irish Flute, Quena, Tin Whistle, Moseño, Pinkullo, Tarka (6–7 holes) |
| Shakuhachi Pentatonic | +3, +5, +7, +10, +12 | Shakuhachi (5 holes) |
| Xiao 8-Hole Chromatic | +2, +3, +4, +5, +7, +9, +10, +11 | All 3 Xiao variants (8 holes) |
| Duduk Natural Minor | +2, +3, +5, +7, +8, +10, +12, +14, +15 | Duduk family (9 holes) |
| Fujara Pentatonic | +3, +5, +7 | Fujara (3 holes + overtones) |
| Siku Diatonic (split) | Arka: 0,4,7,10,14,17,21 / Ira: 2,5,9,12,16,19 | Siku/Zampoña (13 tubes) |

### Naming conventions

- NAF and most flutes: Key = fundamental (all holes closed).
- Xiao: Key = 4th hole note (root + 5 semitones). "G xiao" has root D.
- Duduk: Key = root + 3 semitones. "A duduk" has root F#.
- Siku: Key = 4th note of combined scale (usually the major key name).

## Sanity Checks

- Verify `f = 440 * 2^((69 - 69)/12)` returns 440 Hz.
- Compare a known reference: D4 Irish flute roughly 23 inches (depending on bore/headjoint); A4 tongue in 3/8 inch hardwood often lands near a few inches, not tens of inches.
- Check whether the selected model predicts the observed harmonic behavior.
- Add validation rows for frequency error, cents error, trim allowance, and structural minimums.
