# Changelog

## 1.2.0 - 2026-06-15

- S8 decision (issue #219): **promoted** the Alpha tool-matrix schema into
  makerspace as the single source of truth; the Evolution Pipeline Alpha
  Workspace Compiler consumes it rather than defining its own (Refs #206).
- Added `references/tool-matrix-schema.md` — the promoted schema, expressed
  as a derived capability view over the space profile, with a normalized
  `process` enum mapping onto the existing tool `category` enum.
- Added `references/tool-matrix-promotion-decision.md` — the S8 decision
  record and rationale.
- Registered both references in the on-demand reference list.

## 1.1.4 - 2026-06-15

- Recorded that issue #15 (epic #211, "Build makerspace fabrication specialist
  skill") is satisfied by this existing skill — no sibling skill or new plugin
  created.
- Added `references/fabrication-specialist-charter.md` mapping #15's requested
  modes, bundled resources, and acceptance criteria to existing deliverables.
- Registered the charter in the on-demand reference list.

## 1.1.3 - 2026-05-11

- Portable snapshot from the standalone makerspace repo. (Pre-existing release;
  changelog backfilled.)

## 1.1.2 - 2026-05-11

- Added repo-to-shop-packet routing for woodworking/mechanism fabrication
  handoffs.

## 1.1.1 - 2026-05-11

- Added a generator-backed DXF/CNC fabrication handoff checklist on top of the
  structured-shop-artifacts validator.
