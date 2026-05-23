# Queued Instruments

Research dimensions and design constraints for instruments on Tony's roadmap. Use these as starting points; verify against measured prototypes before committing to CNC.

## Kora (21-string West African harp-lute)

Physics: Mersenne–Taylor (`references/acoustic-models.md` §Strings).

### Reference Dimensions

- **Bowl** (segmented, replacing calabash gourd):
  - Havlena builder: 16" diameter head, 10.25" deep.
  - Full-size traditional: 51.5 cm Ø × 25 cm deep.
  - Goatskin head, notched bridge.
- **Neck**:
  - Havlena: 49" × 3/4" × 2".
  - Traditional: 120–130 cm.
- **Strings**:
  - Havlena: shortest 12.5" / longest 33.25".
  - Full-size: 22–79 cm vibrating length.
- **Tuning**: F3–D6 diatonic, 11 strings left + 10 right.

### Build Notes

- Electric version planned with piezo pickup.
- String schedule from Mersenne–Taylor, nylon + wound bass strings.
- Segmented bowl uses miter sled technique (`references/manufacturing-and-cnc.md`); adapt ring count for hemispherical profile.
- Bridge geometry is critical for tone separation between left/right hand string banks.

## Ngoni (Kamele N'goni)

Physics: Mersenne–Taylor.

### Variants

- **Donso**: 6-string hunter's ngoni.
- **Kamele**: 10–12 modern strings.

### Reference Dimensions

- Bowl: 10–18" diameter.
- Kaypacha model: 32 cm (small) or 45 cm (large).
- Goatskin head.
- Strings: nylon, 0.5–1.6 mm gauges.
- Tuning: pentatonic D-F-G-A-C pattern, repeating.

## Stave Lute / Oud

Physics: Mersenne–Taylor strings + bowl-back acoustic body.

### Reference Dimensions

- **Bowl-back**: 14–21 thin ribs bent over CNC mold.
- **Rib dimensions**: 70–75 cm × 2.5–4 cm × 2.8 mm each.
- **Oud**: fretless, 11 strings.
- **Lute**: fretted, 6–13 courses.

### Build Notes

- Requires steam bending reference data (`references/manufacturing-and-cnc.md`).
- Steam time: ~1 hour per inch of rib thickness at 212°F. Thin ribs (2.8 mm) need careful timing to avoid scorching.
- CNC-routed mold form for bowl shape; springback allowance needed.

## Tongue Drums (TNG family)

Already covered in detail in `references/acoustic-models.md` §Cantilever Beams and §Helmholtz Resonators. Three variants in Master Catalog:

- **TNG-001**: Small, magazine baseline, D minor / A minor.
- **TNG-002**: Medium, bilateral original, extended scale.
- **TNG-003**: Large, extended range, widest tonal range.

## Marimba / Xylophone Bar Sets

Physics: Free-free beam (`references/acoustic-models.md` §Free-Free Beams).

Key constraints:

- Suspension nodes: 22.4% and 77.6% of bar length.
- Marimba arch undercut: parabolic CNC cut, minimum center thickness 0.25" for structural integrity.
- Resonator tubes (quarter-wave closed pipe): one per bar.

## Workflow For New Instruments On The Roadmap

1. Add a row in `Master Catalog` of `Instrument Workshop Master v3.xlsx` with at minimum: Instrument ID, Family, Instrument Type, Variant/Size, Key/Scale, Design Stage = "Research".
2. Choose the governing physics model from `references/acoustic-models.md`.
3. Create a design sheet in `Flutes-AI.xlsx` (or other workbook) using the patterns in `references/workbook-integration.md`.
4. Update the `Index` sheet.
5. When ready, run `scripts/generate_build_packet.py` to produce the build packet folder.
6. Iterate on the packet, then run `scripts/generate_capstone_docs.py` to produce the capstone deck (.pptx) and printable shop packet (.pdf).
