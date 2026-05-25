# Build Plan — Order of Operations for the Niece Team

Total estimated build time: **12-16 hours** spread over 3-4 weekend sessions. Plan for the team to do the work; the mentor's job is to ensure safety and to handle the laser order / press brake.

## Session 1 — Plan & Order (1 hour)
1. Review weight class rules for target tournament (NHRL, RoboGames, regional).
2. Confirm wedge front-edge radius rules for your event.
3. Place laser-cut order for both 5052 shells and the 6061 frame plate.
4. Order all hardware and motors (see BOM).
5. While waiting for parts: print full-scale paper template of flat pattern, fold it up, verify fit of the cardboard mock-up motor and battery.

## Session 2 — Receive Parts & Bend (3 hours)
**Adults/mentor work:**
- Inspect laser-cut parts for relief cuts at corners.
- Check edges are deburred. Run a flat file along any sharp edge.

**Team work:**
- Match parts to flat pattern drawing.
- Mark bend lines and bend direction on the OUTSIDE of the blank with a Sharpie.
- Practice the bend sequence on the SECOND blank first (scrap on purpose).

**Mentor with press brake (or local maker space):**
- Bend in this exact order: front wedge (15 deg), rear (90 deg), left side (90 deg), right side (90 deg), bottom flanges (90 deg in).
- After each bend, check fit against the cardboard mock-up.
- DO NOT FORCE A BEND that does not want to happen. If the brake is fighting you, the relief cut is too small.

## Session 3 — Drive Assembly (4 hours)
1. Mount motors to internal frame plate. Two M3x8 bolts per motor through 6061 plate into the motor's threaded mount holes. Loctite 243.
2. Install wheels onto motor shafts. Set screw onto flat of D-shaft. Loctite 243 on set screw.
3. Test fit internal frame inside folded shell. Mark and drill M3 clearance holes for top-deck bolts if not already laser-cut.
4. Install wheel guards. Two M3x10 bolts per guard through shell side wall into M3 locknuts.
5. Bench test drive: power motors directly from battery (one second each direction) to confirm wheels spin freely and don't rub on guards.

## Session 4 — Electronics & Final Assembly (3 hours)
1. Solder XT30 to battery pigtail. **Mentor only or supervised.** Use helping hands and a fume extractor or open window.
2. Solder ESC power input to arming link lugs. Then arming link to battery XT30.
3. Solder ESC motor outputs to motor leads. Match polarity to drive direction; if a wheel spins backwards, swap two motor wires.
4. Plug receiver into ESC, bind to nieces' transmitter.
5. Install all electronics into the shell. Velcro the battery into its pocket. Route wires through interior frame channels.
6. Bolt top deck on with 6x M3 bolts. Loctite 243 (mentor applies).
7. Insert arming link, verify status LED.
8. Drive test on the floor. Calibrate trim. Practice driving for an hour.

## Session 5 — Pre-Tournament Shakedown (2 hours)
1. Weigh the bot. If over 1361 g, **stop and redesign** — do not shave material from the shell.
2. Drive against cardboard boxes for impact testing.
3. Spin tires against a piece of wood to simulate friction loading.
4. Run a full battery from full charge to ESC low-voltage cutoff to confirm match endurance.
5. Practice the 60-second teardown drill three times.
6. Sharpie the team name on the top deck.
7. Charge all batteries. Pack pit kit.

## Safety Notes for the Mentor
- Eye protection during all bending, drilling, and driving.
- LiPo charging on a non-flammable surface, never unattended, always in the LiPo bag.
- Arming link OUT any time the bot is in human hands. This is a hard rule. No "just one quick test."
- Hot solder iron lives in its stand. Always.
- When testing drive on the floor, drive AT a wall, never AT a person.
