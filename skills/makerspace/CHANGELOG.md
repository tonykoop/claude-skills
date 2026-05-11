# Changelog — makerspace

## v1.1.2 — 2026-05-11

- Add repo-to-shop-packet routing guidance for woodworking and mechanism
  projects such as chessboard-table and cryptex.
- Add a smoke eval covering fabrication handoff from an existing project repo.
- Add minimum readiness gates for revision authority, dimensions, materials,
  workholding, safety, and publication scrub.
- Clarify generated DXF/CNC handoff checklists as blocker lists, not pass
  certificates, and add coverage for the generated checklist role.

## v1.1.1 — 2026-05-10

- Add generator-backed `references/examples/cnc-laser-fabrication-handoff/`
  checklist for DXF/CAD/CAM/fabrication-repo readiness reviews.
- Add `scripts/generate_cnc_handoff_checklist.py` to emit deterministic
  `handoff_checklist.json` and schema-compatible `validation.csv` from one
  `design_params.json` source.
- Route DXF/CNC handoff prompts to the checklist while preserving CAD/DXF as
  fabrication authority over generated images or prose summaries.
- Add repo-backed woodworking/mechanism handoff routing and eval coverage,
  adopting the Partner Peek cue to extract fabrication facts while leaving
  private/story context out of shop docs.
- Normalize `SKILL.md` frontmatter to top-level `version` and `last-updated`
  for skills-meta compatibility.

## v1.1.0 — 2026-05-10

- Add `references/structured-shop-artifacts.md` defining CSV schemas for `cut-list.csv`, `validation.csv`, and `process-schedule.csv` (renameable to `bending-schedule.csv` etc.).
- Document parametric SVG sanity-check workflow (`rsvg-convert` / Inkscape) for packets with curved primary features.
- Add steam-bending gate table: 8 required validation checks (moisture, grain, box temp, strap, working window, breakage threshold, cooling, oil-rag fire).
- Extend `scripts/validate_packet.py` with `check_csv_schemas()` and `check_steam_bending_gates()` plus `--schemas-only` mode.
- Update `references/repeatable-shop-packets.md` and `SKILL.md` to point at the new structured-artifact threshold rule (>5 parts or >5 gates).
- Refs Round 7 TwinGrid Lane Cindy artifacts as the worked example.

## v1.0.0 — 2026-05-09

- Initial skill: home-shop fabrication specialist (jigs, fixtures, shop layout, tooling).
- Cross-platform snapshot: lazy-load pattern, portable path handling.
- Public-scrub pass: private names and contact info removed.
