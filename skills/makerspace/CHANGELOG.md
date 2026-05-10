# Changelog — makerspace

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
