# Operation sequence — CNC Welcome Sign
## Space: maker-nexus
## User certs claimed: shop-safety-cert, woodshop-cert, cnc-cert
## Estimated total shop time: 3:30 (CAM prep at home not counted)

## Feasibility summary

- ✅ Project fits Maker Nexus shop. CNC routing area accepts plywood
  (per profile `tools[cnc-area].allowed_materials`).
- ✅ User holds all required certs (shop-safety, woodshop, cnc). No
  cert gap.
- ✅ Material is allowed: baltic birch plywood is in
  `cnc-area.allowed_materials = [hardwood, plywood, mdf, hdpe, foam]`.
- ✅ Laser is NOT in this plan. User isn't cleared on laser; we route
  the keyhole slots on the CNC instead.
- ⚠ Bed size on the Maker Nexus CNC is `TBD` in the profile. The
  18×6 sign easily fits any router with ≥24×24 bed; if the actual
  router is e.g. an Onsrud or Shopbot, the part fits trivially.
  Confirm before reservation.
- ⚠ V-bit and 1/8" endmill are member-supplied per shop convention —
  on the BOM, must be in hand before shop time.

## Operations

1. **Op 1 — Pre-flight and CAM check** [tool: laptop, time: ~0:00 in shop]
   - Done at home before shop time. CAM file ready in
     Vectric VCarve Pro: V-carve toolpath, keyhole pocket toolpath,
     profile toolpath. Save as `welcome-sign.crv` and post-process
     to the Maker Nexus router post.
   - Cleared on this tool: yes (own laptop)
   - Go/no-go check before proceeding: simulation in VCarve shows
     no over-depth cuts on V-carve, profile passes step at 0.10 in,
     6 tabs spaced evenly.

2. **Op 2 — Reserve CNC and arrive** [tool: reservation system, time: ~0:15]
   - Reserve a 4-hour CNC slot. Bring stock, both bits, tape, hex
     keys for collet, vacuum, and a USB stick with the post'd file.
   - Cleared on this tool: yes (cnc-cert)
   - Go/no-go check before proceeding: stock measures 0.245-0.260 in
     thick (within tolerance for V-depth math); face is flat.

3. **Op 3 — Mount stock to spoilboard** [tool: cnc-area, time: ~0:15]
   - Material: 1/4" baltic birch, full sheet OR a pre-trimmed
     ~22×10 in piece. Either is fine; smaller piece is easier to
     handle.
   - Fixture: double-sided carpet tape (b004) on the spoilboard,
     four strips running the long axis. Sweep spoilboard clean,
     press stock down, walk on it for 30 sec to set tape.
   - Tooling: none yet.
   - Cleared on this tool: yes
   - Go/no-go check before proceeding: lift one corner with a
     fingernail — should not budge. Sheet sits flat, no rocking.

4. **Op 4 — Set XY origin and probe Z** [tool: cnc-area, time: ~0:10]
   - Set XY zero at the lower-left corner of the sign body
     (offset 1.0, 1.0 from stock corner per cut-list).
   - Z-zero on top of stock using the touch-off plate.
   - Cleared on this tool: yes
   - Go/no-go check before proceeding: jog to (18, 6) — the cutter
     should be inside the stock with margin. Jog back to (0, 0).

5. **Op 5 — V-carve "WELCOME"** [tool: cnc-area, time: ~0:30]
   - Material: stock from Op 3
   - Fixture: stock taped from Op 3
   - Tooling: 60° V-bit (b002) in a 1/2" collet
   - Feeds & speeds: 18,000 RPM, 60 in/min feed, 30 in/min plunge
     (good baseline for BB at this depth; tune if chatter or burn).
   - Cleared on this tool: yes
   - Go/no-go check before proceeding: first letter looks clean,
     no burning, no chip-out at the top of the carve. Pause and
     inspect after the first letter; resume if good.

6. **Op 6 — Tool change to 1/8" endmill** [tool: cnc-area, time: ~0:05]
   - Tooling: 1/8" upcut spiral endmill (b003) in a 1/4" collet.
   - Re-zero Z (different bit length) using the touch-off plate.
     XY zero stays.
   - Cleared on this tool: yes
   - Go/no-go check before proceeding: collet snug, bit stickout
     ≤ 0.75 in, Z-zero confirmed by jogging to Z=0.005 above stock.

7. **Op 7 — Cut keyhole slot pockets (front face — see note)** [tool: cnc-area, time: ~0:10]
   - NOTE on which face: keyhole slots go on the BACK face of the
     sign (so the sign hangs flush). Two approaches:
     (a) Cut them now on the current face if you flipped the
         design so the V-carve was face-down (not recommended —
         visual surface goes against the spoilboard).
     (b) Skip pockets in this setup; flip the part after Op 9
         and pocket from the back. **This is the recommended
         path.** See Op 10.
   - Decision for this packet: skip Op 7 in this setup. Move to Op 8.
   - Cleared on this tool: yes
   - Go/no-go check before proceeding: confirm the keyhole-pocket
     toolpath is *disabled* in this setup; only profile remains.

8. **Op 8 — Profile cut outline with tabs** [tool: cnc-area, time: ~0:25]
   - Material: stock
   - Fixture: same tape mount
   - Tooling: 1/8" upcut endmill from Op 6
   - Strategy: outside profile, 3 passes × 0.10 in (final pass cuts
     0.05 in into spoilboard), 6 tabs of 0.25 × 0.06 in spaced
     evenly around the perimeter.
   - Feeds & speeds: 18,000 RPM, 80 in/min feed, 30 in/min plunge.
   - Cleared on this tool: yes
   - Go/no-go check before proceeding: after first pass, sign
     outline is visible, edges clean, no burning. Pause if
     anything looks off.

9. **Op 9 — Release part, vacuum, hand-sand tabs** [tool: cnc-area + hand tools, time: ~0:15]
   - Pause spindle, vacuum chips off the part.
   - Slide a putty knife under the sign body to release tape.
   - Snap or chisel through the 6 tabs; hand-sand the tab nubs
     flush with 180 grit.
   - Cleared on this tool: yes (hand tools, no cert)
   - Go/no-go check before proceeding: edges feel smooth, no
     splinters, no tab nubs proud of the perimeter.

10. **Op 10 — Flip and pocket keyhole slots** [tool: cnc-area, time: ~0:25]
    - Flip the sign body face-down (V-carve against the spoilboard).
      Re-tape with new strips of carpet tape. Press to set.
    - Set XY zero on a known point — easiest is to use the
      profile-cut edge: jog the bit to touch the lower-left
      corner edge, then offset by the bit radius (0.0625 in).
    - Set Z-zero on the back face.
    - Run the keyhole pocket toolpath: two pockets, 1.25 in long,
      0.40 in wide at the head, 0.18 in wide at the tail, 0.15 in
      deep, on the W/2 = 3.0 in horizontal centerline, separated
      by x_m = 12.0 in.
    - Feeds & speeds: 18,000 RPM, 60 in/min feed, 25 in/min plunge.
    - Cleared on this tool: yes
    - Go/no-go check before proceeding: pockets visible from the
      front face show no breakthrough (depth 0.15 in into 0.25 in
      stock leaves 0.10 in of substrate); a #8 screw head test-fits
      into the wide end, slides into the narrow end and locks.

11. **Op 11 — Vacuum, release, hand-sand all faces** [tool: hand tools, time: ~0:30]
    - Release sign from spoilboard, vacuum, take to hand bench.
    - Sand front face: 180 → 220. Pay attention to V-carve edges;
      light pass only — don't soften the carve.
    - Sand edges and back: 180 → 220.
    - Tack-cloth before finishing.
    - Cleared on this tool: yes (hand tools)
    - Go/no-go check before proceeding: no fuzz, no burrs, no
      pencil marks; surface is uniformly dull.

12. **Op 12 — Apply finish (offsite or spray bench)** [tool: spray bench, time: ~0:30 active + 24h cure]
    - Apply 1 coat sanding sealer (b005) with foam brush. Wait 2
      hours.
    - Light scuff with 320 grit; tack-cloth.
    - Apply 2 coats spar urethane (b006), 4-hour wait between
      coats, 320-grit scuff between.
    - Final cure: 24 hours before mounting.
    - Cleared on this tool: yes (no shop cert needed; can be done
      at home or at a Maker Nexus finish booth if available).
    - Go/no-go check before proceeding: no bare spots under raking
      light; finish feels smooth, not tacky.

## Prep checklist (before shop time)

- T-7d: Verify Maker Nexus CNC bed size and post-processor; confirm
  reservation system rules.
- T-7d: Order V-bit and 1/8" endmill from Toolstoday (2-day shipping).
- T-5d: Pickup or order baltic birch sheet from MacBeath Berkeley
  (will-call) — confirm sheet thickness is 0.245-0.260 in by caliper
  on arrival.
- T-3d: Build CAM file in VCarve Pro, simulate, post to Maker Nexus
  router post-processor. Save to USB stick.
- T-2d: Buy finish supplies (sanding sealer, spar urethane, foam
  brushes, sandpaper, tack cloths) from Home Depot.
- T-1d: Reserve a 4-hour CNC slot. Charge phone, pack stock + bits +
  tape + USB + hex keys + safety glasses + ear protection + dust mask.
- T-0: Run the build (Ops 2-11). Op 12 finish can happen offsite.

## Open questions

- Maker Nexus CNC bed size and post-processor — confirm at
  reservation time. Profile lists `TBD`.
- Whether the shop has a touch-off plate or whether the user brings
  one — typical for Onsrud/Shopbot is "yes, on a coiled cable."
  Confirm.
- Whether the shop allows finish application on-site or whether it
  must be done at home. Op 12 is offsite-friendly either way.
- Stud locations at the mounting site (12.0 in apart for the keyhole
  slots assumes between two studs at 16" o.c.). User to measure
  before mounting.
