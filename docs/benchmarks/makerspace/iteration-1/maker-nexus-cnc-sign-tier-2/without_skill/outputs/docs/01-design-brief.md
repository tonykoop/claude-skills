# Design brief

## Goal

A small, durable interior welcome sign with crisp V-carved letterforms,
suitable for hanging by the front door or in an entryway. The piece should
read as "handmade but precise" - the kind of object that demonstrates
competence with the CNC without being fussy or over-decorated.

## Constraints

| Constraint | Source | Value |
|---|---|---|
| Stock | Project requirement | 1/4" Baltic birch plywood |
| Outside size | Project requirement | ~18 x 6 in |
| Lettering | Project requirement | "WELCOME", V-carved |
| Tool process | Project requirement | CNC router only (no laser) |
| Shop access | User clearance | Maker Nexus Woodshop + CNC |
| Time budget | Self-imposed | One half-day shop session |

## Design decisions and rationale

### 1. Final sign size: 18.000 x 6.000 in
The stated brief is "about 18 by 6 inches." Locking it to 18 x 6 in even
gives a 3:1 aspect ratio that frames "WELCOME" (7 letters) comfortably
without wasted negative space, and falls under common 24 x 30 in Baltic birch
half-sheet sizes with plenty of clamping margin.

### 2. Stock blank: 20 x 8 in
Adds 1 in of margin on every side of the finished part for hold-down,
spoilboard tape, and the perimeter cut to live in. This is the *blank*
clamped to the spoilboard - not the finished outside dimension.

### 3. Material: Baltic birch (B/BB or BB/BB grade)
- 1/4" Baltic birch is genuinely 5-6 mm and 5-ply, so V-carving across grain
  doesn't blow out the way fir or sande ply does.
- Small, tight knots and a clean light face take oil finish beautifully.
- A B/BB sheet has one near-perfect face; orient that face up.

### 4. Letterform: V-carve friendly serif, ~3 in cap height
- A serif (Trajan, Cinzel, EB Garamond Caps) gives the V-carve more
  variation in line width, which is the whole reason to V-carve instead of
  pocket - the bit naturally cuts wider where the letter is thicker.
- ~3 in caps at 6 in sign height = 50% of vertical space for letters,
  with ~1.5 in margin top and bottom. Reads cleanly from across a room.
- Letter spacing tracked +25 to +50 units to open the word up; "WELCOME"
  set tight looks cramped.

### 5. V-bit angle: 60 degrees
- 60 deg is the most common V-carve angle and gives a good balance of
  depth-for-width. A 90 deg bit would be shallower and less dramatic; a
  30 deg would dive too deep into 1/4" stock for the larger letter
  thicknesses.
- Max V-carve depth set to 0.18 in (leaving ~0.07 in of stock under the
  deepest cut so the part doesn't get fragile).

### 6. Border: 0.125" inset rectangle, V-carved
- Frames the word and gives the eye somewhere to rest.
- Same V-bit, same toolpath logic - no extra tool change.
- Inset 0.5 in from the perimeter on all sides.

### 7. Perimeter: square corners with 1/8" radius
- A 1/8" corner radius is the smallest a 1/8" end mill can cut cleanly
  (it's literally the tool radius).
- Square-ish corners read as "intentional sign" rather than "cookie."

### 8. Hanging: keyhole slot on the back, off the CNC
- One keyhole slot routed in a second op (flip the part) at the top
  center, sized for a #8 panhead screw.
- Alternative: two small holes for sawtooth hanger hardware. Keyhole is
  cleaner and uses no extra parts.

## Out of scope

- No paint-fill in the V-carves (kept natural; could be added later with
  acrylic + sanding).
- No laser-engraved details (laser clearance not held).
- No edge profiling beyond a hand-sanded eased edge.
- No mounting hardware shipped with the sign - one screw in the wall.
