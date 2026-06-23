# maker plugin — Changelog

## 2.1.0 — 2026-06-22

Add the `music-teacher` skill to the maker set (now 15 skills). Agentic learner
profiling, per-skill mastery tracking on a 0.0–1.0 competency scale, and
personalized multi-month practice plans via the closed Coach loop
(Profile → Curate → Calibrate → Mutate), plus Curator (graded repertoire + drill
catalog) and Translator (cross-instrument/notation conversion) sub-roles.
Kora-first, extensible to wind/percussion/dulcimer. Canonical source is the
`tonykoop/music-teacher` repo; wired in via `SKILL.md` (frontmatter) + `skill.yaml`.
Pairs with `sheet-music` and `instrument-maker`.

## 2.0.0 — 2026-06-19

First-class v2.0.0 release. The maker skill set is mature and stable across 14 skills:

| Skill | Description |
|---|---|
| `instrument-maker` | Acoustic instrument design (v4.5.0): reed/free-reed boundary conditions, khaen/sheng/hulusi/chalumeau, prototype validation-loop, DXF/image-gen-2 visual authority, design-book chapter contract, experimental acoustic rig templates |
| `sheet-metal` | Sheet-metal CAD, SolidWorks flat-pattern, DXF/plasma, brake/slip-roll, welding, lofted bends, enclosures, kinetic objects, mixed-material shop packets |
| `makerspace` | Shop-floor planning, structured fabrication artifacts, DXF/CNC handoff checklists, woodworking/mechanism routing, Alpha tool-matrix schema (v1.2.0) |
| `maker-engineering` | Umbrella routing for physical projects and specialist handoffs; human-carrying/floatable-object safety gate |
| `laser-art` | Laser-cut/engraved/scored decorative art routing with generated-image vs. fabrication-authority boundaries |
| `habitat-maker` | Wildlife habitat (bat/bee/bird-bath/observation-hive) with welfare gates, camera/electronics caveats, laser packet support, Tillandsia-on-bark sculpture micro-line |
| `reverse-engineer` | Reverse-engineering routing with image-access preflight and degraded-mode banner |
| `sheet-music` | Sheet-music reading, transcription, and notation workflows |
| `idea-incubator` | Idea capture, promote-batch mode, readiness matrix, evidence-ledger, media/family archive promotion, yearbook/design-book chapter contracts (v1.4.4) |
| `file-a-patent` | Private invention packet and provisional-patent preparation (attorney-ready; does not file or provide legal advice) |
| `houseplant` | Houseplant/bonsai digital twins, Blender MCP support, chrono-horticultural engine, wire-removal windows, bud/bloom tracker, aerial-root tracker, CV health check, grafting sandbox, propagation tracker (v0.3.0) |
| `energy-management` | Capacity-to-task matching for making/teaching/sprint work; two-input model (time window + energy state), five modes |
| `yoga-sequencer` | Vinyasa class sequencing with playlist-builder handoff; heated-room safety checklist |
| `playlist-builder` | Music playlist curation with catalog/auth-state preflight |

**Maturity note:** `plugins/maker/skills/houseplant-workspace/` is a scratch evaluation workspace (benchmarking artifacts, iteration data for the `houseplant` skill) — it is not a standalone skill and carries no SKILL.md at its root. All 14 real skill directories have a `SKILL.md`.

**No breaking changes.** This is a promotion milestone — all skills were stable in the 1.x line; v2.0.0 marks collective maturity.
