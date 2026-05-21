# Design Brief: 3 lb Beetleweight Wedge Chassis (Family Build)

Authority: design planning only. Not fabrication-ready. No structural,
weapon, or arena-safety claims. Combat robotics is impact-loaded — final
material, fasteners, wheel guards, and weight budget must be confirmed
on the team's measured stock and event rules before any cutting.

## Object And Use Case

- Object: folded sheet aluminum wedge chassis for a 3 lb (1360 g) beetleweight
  combat robot, built and driven by middle-school nieces.
- Use case: middle-school combat-robotics event with a short bench window
  between matches; design must reward fast service access more than absolute
  weight optimization.
- Skill posture: forgiving alloy, conservative bend radius, mechanical
  fasteners (no welding required), guarded wheels, and a single removable top
  panel for fast service.

## Envelope And Form

- Class: beetleweight, 3 lb / 1360 g hard limit.
- Form: low classic wedge — short, wide front edge low to the floor, sloped
  top deck rising rearward to a vertical back wall.
- Planning envelope (outside): 7.0 in long x 6.0 in wide x 2.5 in tall at
  the rear wall. Front lip target around 0.20 in off floor; sloped top deck
  at roughly 18 to 22 degrees.
- Layout intent: two drive motors mounted across the rear, battery and
  electronics tray ahead of the motors, removable top panel that exposes the
  whole interior in under 60 seconds.

## Material Choice (Forgiving Alloy)

- Selected: 5052-H32 aluminum, 0.063 in (1.6 mm) nominal thickness.
- Rationale: 5052 is the forgiving sheet alloy. It cold-bends without
  cracking at `R >= T`, takes mechanical fasteners cleanly, and is easy to
  deburr safely. The skill's combat-bot reference explicitly flags 6061-T6
  as crack-prone in bends and 7075-T6 as outright crack-prone. For a kid-
  facing build, fracture-tolerance beats stiffness-per-gram.
- Tradeoff: 5052 is softer than 6061-T6, so the design must rely on folded
  geometry (closed corners, return flanges, sloped top deck acting as a
  diaphragm) for stiffness instead of plate strength.

## Hard Constraints

- Total robot weight at or under 1360 g, with chassis budget targeted in the
  skill's stated beetleweight range of 300 to 400 g.
- No welding required. Build must be completable with a brake, drill, files,
  deburring tools, and a screwdriver/hex driver.
- Wheels must be guarded on both sides — exposed wheel hubs are a known
  beetleweight failure mode.
- Service access target: top panel off and battery swappable in under
  60 seconds with a single tool.
- All accessible exterior edges deburred plus either hemmed, radiused, or
  protected by a flange. No raw plasma/laser edges left where hands touch.

## Soft Constraints (Family / Middle-School Context)

- Hardware standard: M3 stainless socket-head cap screws plus nylock nuts.
  M3 hex key is universally available and forgiving of misalignment;
  nylocks tolerate the vibration of a combat event without thread locker.
- Spares plan: parts that take hits (wheel guards, front wedge lip,
  top-panel screws) should be cheap to refabricate from the same DXF.
- All edges accessible to a child's hand should be deburred and either
  hemmed, return-flanged, or fully radiused.

## Open Questions (Three Blocking)

1. What drive motors, ESC, receiver, and battery are the team committed to?
   Their footprint, mounting pattern, and combined mass set the interior
   tray and remaining chassis budget.
2. What event class is this — pushers-only, or are active weapons allowed?
   A pusher rules set tolerates this forgiving design; a horizontal-spinner
   event would push us toward sloped 6061 or Ti armor over a 5052 inner
   shell.
3. What wheel diameter and hub width are planned? Wheel guards and the
   front-lip ground clearance both key off that number.

## Assumptions Used For Planning

- 5052-H32, 0.063 in nominal thickness (measure before cutting).
- Inside bend radius equal to thickness (R = T = 0.063 in) as a conservative
  starting tool radius on a finger brake.
- K-factor 0.45 (mid-range planning value for common aluminum).
- M3 fasteners, eight to twelve total on the chassis.
- Skill-supplied combat-bot guidance: mechanical interlocks plus screws for
  thin micro-bot work, sloped armor 30 to 45 degrees off the floor for the
  wedge face, dogbone or circular reliefs at internal corners, wheels
  guarded by side flanges or loops.

## Out Of Scope

- Weapon design, weapon motor selection, weapon armor.
- Welded or riveted permanent joints (kept out so the nieces can re-build).
- Road, vehicle, overhead, or human-load use. This is an arena-only build
  within a small enclosed combat box.
