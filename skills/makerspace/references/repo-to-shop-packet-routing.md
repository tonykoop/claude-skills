# Repo to Shop Packet Routing

Use this reference when a user points at an existing project repo and asks
for a fabrication handoff, shop packet, fixture plan, or build-ready route.
Typical examples include woodworking and mechanism projects such as a
chessboard table, cryptex, puzzle box, furniture piece, jig, fixture, or
small mechanical prop.

## Route here when

- The repo already has a concrete object, mechanism, or furniture concept.
- The next decision is how to build, hold, cut, fixture, source, inspect, or
  safely run the work in a shop.
- The user needs a repeatable packet, not brainstorming, storytelling, or
  portfolio polish.
- The project has enough geometry, materials, sketches, CAD, BOM notes, or
  prior build notes to state design intent with explicit `TBD` gaps.

## Route elsewhere first when

- The project is still an idea or broad concept: use `maker-engineering`.
- The user wants to identify how an existing object works from photos or
  sparse measurements: use `reverse-engineer`.
- The user is asking for instrument acoustics, voicing, bore design, reed
  behavior, or tuning: use `instrument-maker`.
- The request is about public narrative, family photos, private media, or
  portfolio copy rather than fabrication decisions.

## Repo facts to extract

Keep extraction narrow and fabrication-focused:

- Object purpose and the specific assembly or part to build.
- Dimensions, tolerances, fit classes, datums, and derived geometry.
- Materials, stock form, purchased hardware, adhesives, finishes, and
  fasteners.
- Existing CAD, DXF, SVG, CAM, drawings, cut lists, BOMs, or sketches.
- For recovered CAD archives: file path, file type, suspected role,
  authority status, revision status, units/scale status, stale-file risk,
  and next review action.
- Tools or shop assumptions already stated in the repo.
- Risk notes, failed attempts, calibration data, and open TODOs.

Do not publish personal names, private family/media context, unpublished
photos, or story details into public-facing packet text unless the user
explicitly asks and the repo is already intended for that publication.

## Output shape

Start with the default repeatable shop packet:

- `fabrication-plan.md`
- `jig-decision.md`
- `workholding-checklist.md`
- `safety-checklist.md`
- `make-order-buy-borrow.md`

Add `drawing-brief.md` when the repo lacks authoritative shop drawings or
when another person needs to produce CAD/CAM from the packet. Add `bom.csv`
or `sourcing.csv` only when the repo contains or needs hardware and stock
decisions. Add `cad-index.csv` first when the repo has a recovered or mixed
CAD archive and no reviewed fabrication revision. Add structured CSV
artifacts under the thresholds in `structured-shop-artifacts.md`.

## Minimum readiness gates

When a repo-backed handoff needs explicit validation, add these checks to
`validation.csv` or mirror them in the chat response:

| check_id | check_name | target |
| --- | --- | --- |
| REPO-REV | revision authority | CAD, DXF, drawing, and packet all name the same fabrication revision |
| REPO-DIMS | critical dimensions | every cut, bore, slot, clearance, and datum has a source or `TBD` |
| REPO-MAT | material and stock | stock species/material, thickness, grain/face direction, hardware, adhesive, and finish are explicit |
| REPO-WORKHOLD | workholding and access | clamps, fixtures, tool clearance, registration, and safe order of operations are stated |
| REPO-SAFE | safety gate | machine, material, dust/fume/fire, stored-energy, and stop-work hazards are checked |
| REPO-PUBLIC | publication scrub | private family/media/story details are excluded from public shop docs unless approved |

For recovered CAD archives, add these before shop claims:

| check_id | check_name | target |
| --- | --- | --- |
| CAD-IDX | CAD archive index | every CAD, drawing, export, layout, render, and sketch has a row in `cad-index.csv` or is explicitly excluded |
| CAD-AUTH | authority status | each file is marked `current`, `stale`, `visual_only`, `requires_export`, or `unknown` |
| CAD-UNITS | units and scale | every fabrication-authority candidate has units, scale, origin/datum, and at least one known dimension checked or marked `TBD` |
| CAD-STALE | stale-file handling | duplicate, old/new, V1/V2, and unreviewed export files are blocked from shop use until reviewed |

## Handoff rules

- Treat CAD, DXF, dimensioned drawings, and measured geometry as fabrication
  authority. Generated images can support concept/story work, but they do not
  replace CAD/DXF authority for shop operations.
- For recovered archives, do not let file names or screenshots imply
  authority. Build `cad-index.csv` first, then a drawing brief from the rows
  that survive review.
- Separate design intent from machine operations. Quote the required outcome
  first, then choose a shop route.
- Preserve unknowns as `TBD` instead of inventing dimensions, machine limits,
  or tolerances that affect safety or fit.
- Include a primary route and at least one fallback when access to a machine,
  certification, cutter, fixture, or purchased component may be blocked.
- End with go/no-go checks that a maker can run before cutting material.

## Prompt smoke examples

- "Use my chessboard-table repo to make a shop packet for cutting and
  assembling the board, drawer frame, and leg joinery. I have design notes
  and a rough BOM, but I need the fabrication handoff."
- "Turn the cryptex repo into a shop-ready packet. Focus on indexing,
  tolerances, pin alignment, workholding, and what should be CAD authority
  versus a drawing brief."
