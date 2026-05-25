# Operation sequence — CNC Welcome Sign

## Space: maker-nexus
## Tier: 2
## User certs claimed: shop-safety-cert, woodshop-cert, cnc-cert
## Estimated total shop time: ~3.5 hours

## Feasibility summary

- ✅ Feasible at Maker Nexus with claimed certs.
- ✅ Material (baltic birch plywood ¼") is allowed on the woodshop CNC.
- ✅ V-carving at 0.125" depth is well within the CNC's range.
- ⚠ Verify on-site that the shop has a ¼" compression bit and a 60°
  V-bit. Bring backups if not.

## Operations

1. **Op 1 — Stock breakdown to sub-sheet** [tool: tablesaw, time: ~0:15]
   - Material: 60×60 baltic birch ¼" sheet (full)
   - Fixture: rip fence + crosscut sled
   - Tooling: 60-tooth fine-cut blade
   - Cleared: yes (woodshop-cert)
   - Go/no-go: cut a ~22×8 rectangle to fit the CNC bed setup; check
     squareness within ±1/32".

2. **Op 2 — Mount sub-sheet on CNC** [tool: cnc-area, time: ~0:15]
   - Material: 22×8 sub-sheet from Op 1
   - Fixture: vacuum table + corner alignment fence
   - Tooling: n/a (setup only)
   - Cleared: yes (cnc-cert)
   - Go/no-go: vacuum holds when partially loaded; corners square to
     X/Y; Z-zero set on top face.

3. **Op 3 — V-carve letters** [tool: cnc-area, time: ~0:30]
   - Material: 22×8 sub-sheet
   - Fixture: same as Op 2
   - Tooling: 60° V-bit, ¼" shank
   - Cleared: yes
   - Go/no-go: dry-run the toolpath in CAM software; verify deepest
     pass is 0.125" (= half stock); first cut on test coupon (p004)
     before main piece.

4. **Op 4 — Profile-cut sign body and cleats** [tool: cnc-area, time: ~0:30]
   - Material: 22×8 sub-sheet
   - Fixture: same as Op 2; add onion-skin tabs
   - Tooling: ¼" compression spiral, 2-flute
   - Cleared: yes
   - Go/no-go: tabs visible in toolpath preview; chip clearing OK
     mid-cut; verify zero is still set after V-carve.

5. **Op 5 — Knife-cut tabs** [tool: hand tools, time: ~0:10]
   - Material: cut parts from Op 4
   - Fixture: bench vise + mat
   - Tooling: utility knife
   - Cleared: n/a (hand tools)
   - Go/no-go: parts release without splintering the show face.

6. **Op 6 — Sand to 220** [tool: orbital sander + hand, time: ~0:30]
   - Material: sign body, cleats, spacers
   - Fixture: bench
   - Tooling: orbital sander, 150 → 220 grit
   - Cleared: yes
   - Go/no-go: V-carved letter edges crisp, not rounded over.

7. **Op 7 — Drill mounting holes** [tool: drill press, time: ~0:10]
   - Material: sign body + cleats stacked
   - Fixture: drill-press fence + sacrificial backer
   - Tooling: ¼" brad-point bit
   - Cleared: yes (woodshop-cert)
   - Go/no-go: holes aligned through both pieces; no tearout on exit.

8. **Op 8 — Apply finish (3 coats)** [tool: hand, time: ~1:30 elapsed
   incl. dry time, ~0:15 active]
   - Material: assembled sign
   - Fixture: drying rack
   - Tooling: spray can or wipe-on poly
   - Cleared: n/a (no cert)
   - Go/no-go: each coat dry to touch (light sand 320 between coats).

## Prep checklist (before shop time)

- T-7d: Verify CNC and drill-press reservations on the Maker Nexus
  schedule.
- T-3d: Order baltic birch from MacBeath (or pick up day-of if local).
- T-2d: CAM the V-carve and profile-cut in Vectric or Fusion;
  sanity-check feeds and speeds against the CNC's posted chart.
- T-1d: Print the drawing brief (`drawing-brief.md`) for shop-floor
  reference.

## Open questions

- Final font choice for the letters (default: Inter Bold — confirm
  with user).
- Mounting hole spacing — depends on the post or wall this attaches
  to. Set during Op 7; user should bring measurements.
