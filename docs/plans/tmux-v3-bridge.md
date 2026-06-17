# tmux-v3 Bridge & Design Doc

Issue: https://github.com/tonykoop/claude-skills/issues/7

This is the **bridge** between the working tmux sprint skill and this repo's
skill-ecosystem controls. It is a design doc, not an implementation. Per #7,
**do not rename or bump the working `tmux-sprint` skill until v3 has a real
implementation path** — today that skill ships as `tmux-sprint`
`canonical_version: 2.7.0`, `runtime: claude`, `status: active`
(`plugins/coding/skills/tmux-sprint`).

Goal of v3: evolve the WRFCoin-specific persona sprint driver into a
**project-neutral, routine-driven, runtime-adapter-based** sprint
orchestration skill that obeys the same canonical controls as every other
skill in this repo.

---

## AC1 — Cross-link the existing v3 roadmap

v3 roadmap lives partly here and partly in the external `tonykoop/tmux-sprint`
repo. Link both when issues are enumerated:

- **This repo (landed v2.x increments that shape v3):**
  - #225 — recursive fan-out (persona panes as sub-managers) — `tmux-sprint` v2.7.0
  - #222 / #117 — Codex `/goal` lane integration — v2.6.0
  - #195, #193/#194 — bash 3.2-compatible `launch-grid.sh`, preflight/dispatch/restart scripts
- **External roadmap:** enumerate the open `tmux-sprint` v3 issues in
  `tonykoop/tmux-sprint` and back-link them here (left as a TODO — issue
  numbers to be filled in by Tony to avoid guessing).
- **Adjacent skills that must stay coordinated:** `sprint-supervisor`
  (#164 staged extraction), `sprint-update`, `run-swarm`, `sprint-manager`.

## AC2 — Canonical skill version metadata

v3 must be a first-class `manifest.yaml` citizen, not a sideloaded copy:

- Add a manifest entry with `canonical_version`, `runtime`, `repo_path`,
  `last_updated`, and `status` (see `docs/skill-versioning.md`).
- Keep `SKILL.md` frontmatter `version` in lockstep with the manifest
  `canonical_version`; the drift checker
  (`skills-meta --mode drift --strict`) must pass.
- Ship a per-skill `CHANGELOG.md` per `docs/packaging.md`.
- **Naming/transition:** introduce v3 under a new `repo_path` (e.g.
  `plugins/coding/skills/tmux-sprint-v3` or a renamed package) and mark the
  v2 entry `superseded_by` **only at cutover** — never bump v2 in place
  before v3 is real (#7 constraint). Until then v3 lives as a design doc +
  optional `status: draft` manifest stub that ships nothing.

## AC3 — Routines, hooks, plugins, connectors, automations

How each control surface maps into sprint orchestration:

| Surface | Role in v3 |
|---|---|
| **Routines** | Dispatch/poll cadence and round structure become declared routines rather than hardcoded loops, so a sprint is configured, not coded. Pairs with `sprint-supervisor`'s routines-integration design. |
| **Hooks** | Pre-dispatch verification and stop hooks gate a round (preflight pane liveness, post-round commit/merge). The mechanical watchdog stays a hook; judgment stays in-skill. |
| **Plugins** | v3 ships inside the `coding` plugin; persona/grid topology is plugin config, not skill-baked. |
| **Connectors** | GitHub (issue/PR queue), and optionally chat/notify connectors for escalation, declared as optional connectors the skill suggests when needed. |
| **Automations** | Scheduled sprint kickoff / morning-summary become automations that invoke the skill, decoupling "when" from "how". |

Design rule: **project-specific topology (grids, pane IDs, refusal classes)
is configuration**; the skill is the engine.

## AC4 — Runtime adapters

v3 is portable across runtimes via thin adapters over one canonical core:

- **Claude** (Claude Code / Desktop) — canonical reference adapter.
- **Codex** (CLI / Desktop) — `/goal` lane already integrated in v2.6.0;
  formalize as the Codex adapter.
- **Gemini CLI** — adapter for dispatch + submission verification; document
  any divergence per the checklist's runtime-adapter gate.
- **Desktop counterparts** — note tmux-availability assumptions and degrade
  gracefully where a desktop runtime lacks a real tmux backend.

Each adapter references the **portable canonical name** and documents
divergences (per `docs/public-release-checklist.md`).

## AC5 — Benchmark cases

Add fixtures under the repo's benchmarking harness
(`docs/operational-skill-benchmarking.md`) covering:

1. **Dispatch reliability** — N assignments dispatched to N panes; verify each
   landed in the right pane.
2. **Prompt submission** — submitted text actually entered (not stuck in a
   draft buffer); verify the submit keystroke registered.
3. **Pane recovery** — a dead/stuck codex pane is detected and revived;
   verify round resumes.
4. **Stop hooks** — a stop/refusal condition halts dispatch and escalates;
   verify no further work is sent.

Each case needs trigger + expected-observable assertions so it can run in the
operational-skill benchmark suite.

---

## Cutover gate (definition of done for v3)

v3 replaces v2 only when: manifest entry + changelog exist; drift checker
passes; all four benchmark cases pass on at least the Claude adapter; no
unlabelled private paths / WRFCoin topology in the generic core (coordinate
with #10 and #164); and the v2 entry is flipped to `superseded_by` in the
same cutover PR.
