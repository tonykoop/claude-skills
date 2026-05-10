# Golden Example Packets

These public-safe examples show what "done" looks like for
`instrument-maker-v4` without requiring Tony's full local workspace. Use them
as reference shapes, not as files to copy blindly.

Do not use `wooden-hang` as a public example until its IP/private-public status
is explicitly cleared.

## Ocarina

- Repo: https://github.com/tonykoop/ocarina
- Governing model: Helmholtz vessel resonator.
- Manufacturing path: slip-cast or formed vessel body with tuned voicing and
  finger-hole placement.
- What to copy: compact vessel-instrument packet structure, validation rows,
  drawing expectations, and honest first-order acoustic assumptions.
- Validator role: root-mode packet baseline for public validation checks.

## Udu

- Repo: https://github.com/tonykoop/udu
- Governing model: coupled Helmholtz / vessel-drum behavior.
- Manufacturing path: ceramic vessel forming, port sizing, firing-shrinkage
  tracking, and post-fire pitch validation.
- What to copy: family-aware vessel logic, risk notes around clay/firing,
  validation deltas, and public-safe cultural/source context.
- Validator role: root-mode or migrated packet baseline for vessel-drum checks.

## Gemshorn Slip-Cast Family

- Repo: https://github.com/tonykoop/gemshorn
- Local reference packet: `docs/build-packets/gemshorn-slip-cast-family/`
- Governing model: stopped/open vessel-flute family behavior with shrinkage
  and hole schedule tracking.
- Manufacturing path: slip-cast family workflow with mold plan, drawings, CAD
  starter, RFQ, and validation matrix.
- What to copy: family-spec-driven deliverables, drawing set organization,
  source notes, mold workflow, cut list, and capstone/print packet packaging.

## Transverse Flute Slip-Cast Family

- Repo: https://github.com/tonykoop/transverse-flute
- Local reference packet: `docs/build-packets/slip-cast-transverse-flute-family/`
- Governing model: open-open pipe with tone-hole schedule and fired-dimension
  compensation.
- Manufacturing path: slip-cast ceramic flute body with CAD/OpenSCAD starter,
  mold stack, DoE matrix, and validation logs.
- What to copy: nested `build/packet`-style organization, sibling drawings/CAD
  folders, and explicit manufacturing assumptions.

## Agent Guidance

When creating a new packet:

- Pick the closest example by acoustic family and manufacturing path.
- Preserve the public-safety rule: no private repo links, no local absolute
  paths, no supplier prices frozen as facts, and no unlicensed images.
- Run `scripts/validate_packet.py <repo> --mode auto --json` and explain any
  remaining findings before calling a packet complete.
