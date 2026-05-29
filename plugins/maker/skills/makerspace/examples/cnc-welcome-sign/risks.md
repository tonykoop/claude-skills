# Risks — CNC Welcome Sign

For each risk: severity (low/med/high), description, root cause,
mitigation, *test* (how you verify the mitigation worked).

## High severity

(none — this is a straightforward sign-fabrication project)

## Medium severity

### Outdoor humidity warpage
- **Severity:** medium
- **Description:** Baltic birch ¼" plywood can cup or warp when
  installed outdoors with one face exposed.
- **Root cause:** Differential moisture absorption between front
  (sealed) and back (raw) faces.
- **Mitigation:** Apply finish to *both* faces, not just the front.
  Add at least one cleat on the back to add stiffness and let the
  back dry.
- **Test:** After 30 days of installation, sight along the long edge.
  Pass: deflection ≤ 1/16" over 18". Fail: anything visible at arm's
  length.

### Insufficient depth-of-cut on V-carve
- **Severity:** medium
- **Description:** V-bit doesn't reach the design depth and letters
  look shallow / illegible.
- **Root cause:** Bit dulled or Z-zero set too high.
- **Mitigation:** Cut the test coupon (p004) first with full-depth
  toolpath; measure relief depth before running the main piece.
- **Test:** Depth gauge across deepest letter. Pass: 0.125 ± 0.005 in.
  Fail: anything outside that range.

## Low severity

### CNC vacuum table loses hold mid-cut
- **Severity:** low
- **Description:** Small parts can lift off the spoilboard if vacuum
  cycles down during a profile cut.
- **Root cause:** The Maker Nexus CNC's vacuum pump cycles every
  ~60 seconds.
- **Mitigation:** Use onion-skin tabs in the profile-cut toolpath
  (already specified in Op 4).
- **Test:** Tabs visible in the toolpath preview before running.

### Tearout on profile-cut edges
- **Severity:** low
- **Description:** Plywood face can tear out on the climb side.
- **Root cause:** Compression bit's geometry is good but not perfect
  on softer baltic birch.
- **Mitigation:** Use the recommended ¼" compression spiral (already
  specified). Run a finish pass at lighter depth-of-cut if the first
  pass shows tearout on the test coupon.
- **Test:** Inspect test coupon edge under raking light; no fuzz
  longer than 1mm.

### Dust extraction overwhelmed
- **Severity:** low
- **Description:** Heavy dust load during a long profile cut can
  reduce extraction efficiency, especially on a busy shop day.
- **Root cause:** Shared dust collection across multiple machines.
- **Mitigation:** Run during off-peak hours; verify dust shoe is
  attached and sealed.
- **Test:** Check dust collection bag fill level halfway through the
  cut.

## Risks considered and dismissed

- **Aluminum chip contamination of CNC:** dismissed — project is wood
  only, no metal in the build.
- **Laser-cut alternative:** dismissed — V-carved relief is what the
  user wants; laser engraving wouldn't produce the same effect.
- **Solid hardwood instead of plywood:** considered — plywood is
  fine for a small outdoor sign and tolerates seasonal movement
  better than a flatsawn hardwood panel of this size.
