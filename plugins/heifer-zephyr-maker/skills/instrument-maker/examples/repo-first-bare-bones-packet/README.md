# Instrument Project Starter

Status: bare-bones readiness packet.

This repo is a first public scaffold for an instrument project. It records the
intent, current assumptions, unknowns, validation gates, and starter sourcing
surface before the project has enough evidence for a full build packet.

## Current Authority

- Build readiness: not build-ready.
- Fabrication authority: future CAD/DXF or measured drawing, not this README.
- Acoustic authority: measurement-required unless `design.md` names a measured
  model and validation data.
- Sourcing authority: unverified until checked at purchase time.
- Concept images: allowed for story or visual direction only.

## File Map

| File | Purpose |
| --- | --- |
| `design.md` | Intent, assumptions, unknowns, and next design decisions. |
| `bom.csv` | Starter materials/components with status fields. |
| `sourcing.csv` | Supplier/search/provenance notes without current purchase claims. |
| `cut-list.csv` | Candidate parts, coupons, or blanks; dimensions may be `TBD`. |
| `validation.csv` | Gates, next actions, and evidence required before a full packet or CAD release. |
| `risks.md` | Failure modes and mitigations. |
| `drawing-brief.md` | Future drawing set and authority expectations. |
| `photo-shotlist.md` | Public-safe documentation shot plan. |

## Next Gates

1. Replace placeholder project name, instrument family, and intended build
   method in `design.md`.
2. Record measurements that affect tuning, fit, machining, structure, or
   ergonomics.
3. Promote the authoritative drawing/CAD source in `drawing-brief.md`.
4. Update BOM and sourcing rows after current supplier verification.
5. Run the relevant instrument-maker validators before claiming full packet
   readiness.

## License

Add the project license before publishing derived drawings, CAD, images, or
build documentation.
