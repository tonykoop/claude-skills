# CNC Welcome Sign — Baltic Birch, V-Carved

A V-carved "WELCOME" sign in 1/4" baltic birch ply, 18" × 6", routed at
Maker Nexus on the CNC and finished with exterior satin polyurethane.
Single-sheet build, single setup, two-toolpath job (V-carve + profile),
one afternoon of shop time once CAM is prepped.

![hero placeholder — replace with images/hero.jpg](images/hero.jpg)

## What this is

- Substrate: 1/4" Baltic birch plywood (BB/BB grade), 18.0 × 6.0 in
- Lettering: V-carved "WELCOME", 3.0 in cap height, centered
- Edges: 0.25 in radius corners, profile-cut on the same setup
- Mounting: two keyhole slots routed on the back face for screw hangers
- Finish: 1 coat sanding sealer + 2 coats satin exterior polyurethane

## File map

| File | Purpose |
|------|---------|
| `design.md` | Parametric design, every dimension lives here |
| `bom.csv` | Bill of materials, line costs, vendors |
| `cut-list.csv` | Stock plan, parts laid out on a 60×60 sheet |
| `op-sequence.md` | Operation-by-operation shop plan, cleared tools only |
| `safety-notes.md` | PPE, dust, fume, pinch-point notes for this build |
| `sourcing.csv` | Primary + alternate vendors, URLs, lead times |
| `validation.csv` | Acceptance checks with tolerances and methods |
| `assembly-manual.md` | Step-by-step build, photos to capture along the way |
| `risks.md` | Failure modes from the red-team pass, each with a test |
| `drawing-brief.md` | What the drawings should show; SVG stubs in drawings/ |
| `drawings/` | SVG drawing placeholders (plan, front, section A) |
| `images/` | Hero, process, detail photos (placeholders for now) |

## Status

- Design: complete, parametric in `design.md`
- BOM/sourcing: priced against MacBeath Berkeley + Amazon as of 2026-05-07
- CAM: outlined in `op-sequence.md`, file-prep step is on the maker
- Build: not yet started

## Shop & certs

- Space: Maker Nexus, Sunnyvale CA (`spaces/maker-nexus/profile.yaml`)
- Required certs: shop-safety-cert, woodshop-cert, cnc-cert — all held
- Laser is not used for this build (user not cleared on laser, by design)

## License

Project files: CC-BY-4.0. Use, fork, remix, mount above your own door.

## One-line pitch

A weekend CNC project that proves out V-carve workflow on the Maker
Nexus router and produces a finished, mountable sign you can put on a
front porch the same day.
