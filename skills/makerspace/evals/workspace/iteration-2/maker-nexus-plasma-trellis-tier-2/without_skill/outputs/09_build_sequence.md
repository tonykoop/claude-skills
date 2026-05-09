# 09 - Build Sequence

A realistic schedule for one maker, working alone. Plan two shop sessions, not one - heat handling and powder cure don't compress.

## Session 1: cut + deburr (6-7 hours)

| Time | Task |
|---|---|
| 0:00-0:20 | Material check: confirm plate flat, clean, scaled or not. Sweep slat bed. |
| 0:20-0:40 | CAM final review: load DXF, verify lead-ins, tabs, pierce sequence, kerf compensation, post G-code. |
| 0:40-1:00 | Consumable change: fresh tip + electrode. Air pressure check under load. |
| 1:00-1:20 | **Test cut**: 6" x 6" coupon with 1" inner circles. Inspect, adjust feedrate/pierce delay. |
| 1:20-1:30 | Load full plate, jog to start point, dry run perimeter at Z+0.5 with torch off. |
| 1:30-1:50 | **Stage 2**: internal pierces - 18 small/medium/large vein slots + 2 tendril holes. Pause and verify all clear. |
| 1:50-2:30 | **Stage 3**: outer profile cut, ~25-35 min run time on a 6 ft path. Stay in booth, monitor. |
| 2:30-2:50 | Cool down. Lift part with leather gloves to a clear bench. |
| 2:50-3:20 | Cut 2 bracket plates from offcut. |
| 3:20-4:30 | Tab break-out and edge deburr - flap disc both faces, all edges, all interior cuts. |
| 4:30-6:00 | Mill scale removal - blast or wire wheel. |
| 6:00-6:30 | Acetone wipe, package for transport to powder booth (or store flat, indoors, NOT outside overnight - flash rust within 12 hr). |

## Session 2: powder coat + install (4-5 hours, on a separate day)

| Time | Task |
|---|---|
| 0:00-0:20 | Confirm part still clean. Re-acetone if any handling marks. |
| 0:20-0:50 | Pre-bake at 400 F to outgas. Cool to 150 F. |
| 0:50-1:20 | Hang on hooks, ground, apply powder (two light passes). |
| 1:20-1:50 | Cure at 400 F part-temp for 20 min. |
| 1:50-2:30 | Cool to ambient. Inspect. Touch up if needed (re-shoot, re-cure spot). |
| 2:30-end | Transport home. Install per `07_install_plan.md`. |

## Critical checkpoints

- **Before pierce 1**: test cut acceptable? If no - STOP, fix settings.
- **After Stage 2**: every interior slug cleared? If no - STOP, re-pierce manually before Stage 3.
- **Before powder coat**: surface clean enough to lick (don't actually)? Mill scale gone? Edges deburred? If no - STOP, re-prep.
- **After cure**: any pinholes or coverage gaps? Address now, not after install.
