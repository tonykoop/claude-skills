# houseplant

A Claude skill for managing houseplant and bonsai collection digital twins plus care workflows. First-class Blender MCP support: simulate prunes and wire-coil bends in a parametric twin before you take shears to the live plant. Built by Tony Koop on a multi-year *Ficus benjamina* bonsai-in-training and a brainstorm with two collaborator agents.

This is **v0.2.0** — the first skill-creator iteration on top of an initial Codex-authored draft. The scope of v0.2.0 is the killer-app workflow: phone capture → Blender twin → structural prune + wire-coil training simulation. Six additional modules (chrono-horticultural calendar, bud/bloom tracker, aerial-root tracker, health diagnostics, grafting sandbox, propagation tracker) are filed as GitHub issues for later iterations.

## What this skill does

When loaded into a Claude session that has access to Blender MCP and the user's plant records, this skill turns prompts like:

- *"Plan a structural prune on my ficus and preview wire-coil training on the front-right primary"*
- *"I just exported a .glb from Polycam — build me a digital twin with proper scale from the ruler in the photo"*
- *"Simulate removing branch L03 and bringing R02 down 25° with wire before I cut anything"*
- *"Log that I removed wire from R02 today and tell me what to check next"*

into real artifacts: an editable parametric Blender twin under `Plant_<plant_id>/`, a pruning plan in the bonsai-module table format with risk levels, a helical wire-coil simulation in `05_simulations/`, annotated photos with consistent color semantics, plant-record event log entries, and calendar-ready reminders for wire-bite-in inspection windows.

The skill is heavily progressive-disclosure — `SKILL.md` is the orchestrator; everything else loads on demand from `references/`, `scripts/`, and `assets/`.

## Folder layout

```
houseplant/
├── SKILL.md                              # the orchestrator
├── manifest.yaml                         # structured discoverability
├── CHANGELOG.md                          # semver history
├── README.md                             # this file
├── agents/
│   └── openai.yaml                       # interface metadata
├── references/                           # progressive-disclosure docs
│   ├── capture-pipeline.md               # phone capture modes + ruler scale calibration
│   ├── blender-digital-twin.md           # MCP tool order, bpy patterns, hybrid recipe
│   ├── bonsai-module.md                  # pruning, wiring, aerial roots, ficus notes
│   └── collection-records-and-care.md    # plant record schema, event log types
├── scripts/                              # bundled bpy patterns
│   ├── scene_scaffold.py                 # Plant_<plant_id>/ collection hierarchy
│   ├── scale_from_ruler.py               # ruler-based scale calibration
│   ├── wire_coil.py                      # helical wire-coil generator
│   ├── cut_marker.py                     # colored marker placement
│   └── sim_collection.py                 # non-destructive simulation collections
├── assets/
│   └── ficus-benjamina-starter.md        # starter plant profile
├── evals/
│   └── evals.json                        # test prompts for the skill-creator loop
└── tests/                                # smoke tests on bundled scripts
    └── test_houseplant_scripts.py
```

The iteration benchmarks live alongside the skill at `skills/houseplant-workspace/iteration-N/`. Each iteration directory contains the eval outputs, grading, timing, and a static `review.html` for human qualitative review.

## Required tools

Run-time:

- **Claude with Blender MCP installed** — see [Blender MCP setup](https://github.com/ahujasid/blender-mcp). The skill expects `mcp__Blender__*` tools to be available.
- **Blender 3.x or 4.x** — the bundled scripts target the standard `bpy` API in those versions.
- **A phone with a photogrammetry app** (Polycam, Luma AI, RealityScan, or equivalent) if you want a real 3D twin. Multi-angle photos with a ruler in frame also work for a stylized twin.

Test-time:

```
python3 -m pytest skills/houseplant/tests/
```

The tests are pure-Python — they don't require Blender — and verify that script files parse correctly and that the helper math (helix geometry, scale-factor computation) is correct.

## Installing the skill

The skill installs by being copied into the Claude Desktop skills folder, then re-discovered. For Tony's environment:

```
C:\Users\<you>\AppData\Roaming\Claude\local-agent-mode-sessions\
  skills-plugin\<plugin-id>\<install-id>\skills\houseplant\
```

If `skills-meta` is installed, run an inventory afterward to confirm the canonical version matches the installed copy:

```bash
python3 skills/skills-meta/scripts/skills-meta.py --skill houseplant
```

## Iteration roadmap

Tracked in [GitHub issues](https://github.com/tonykoop/claude-skills/issues?q=is%3Aissue+label%3Ahouseplant):

- **v0.3** target: aerial-root and nebari guidance tracker (#174). This module pairs with the maintainer's Ficus benjamina specimen, which is actively training aerial roots.
- **v0.4** target: chrono-horticultural calendar engine (#172) with wire-removal inspection-window scheduling.
- **v0.5** target: bud/bloom chrono-tracker (#173) for non-Ficus specimens that have visible blooms.
- Other deferred: health diagnostics (#175), virtual grafting sandbox (#176), propagation tracker (#177).

## License

Same as the parent `claude-skills` repo (MIT). Grow something beautiful with it.
