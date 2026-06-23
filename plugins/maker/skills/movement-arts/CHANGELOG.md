# Changelog — movement-arts

## 0.1.0 — 2026-06-22 (Refs #464)

Initial scaffold: domain-agnostic core sequencer + state tracker.

- `scripts/sequencer.py` — `MovementSequencer`, `BreathClock`, `BeatClock`, `CompiledRoutine`, `Block`
- `scripts/tracker.py` — `MovementTracker` with weight distribution, facing direction, clock beat, intensity
- `references/motion-primitives-import.md` — import seam for offtheshelf#35 (stubbed, clearly marked TODO)
- `evals/evals.json` — 5 machine-runnable evals
- `SKILL.md` — trigger-oriented skill contract

Builds on yoga-sequencer (epic #368) but is domain-agnostic from the ground up.
