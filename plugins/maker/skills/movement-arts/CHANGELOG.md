# Changelog — movement-arts

## 0.1.0 — 2026-06-22 (Refs #464)

Initial scaffold: domain-agnostic core sequencer + state tracker.

- `scripts/sequencer.py` — `MovementSequencer`, `BreathClock`, `BeatClock`, `CompiledRoutine`, `Block`
- `scripts/tracker.py` — `MovementTracker` with weight distribution, facing direction, clock beat, intensity
- `references/motion-primitives-import.md` — import seam for offtheshelf#35 (stubbed, clearly marked TODO)
- `evals/evals.json` — 5 machine-runnable evals
- `SKILL.md` — trigger-oriented skill contract

Builds on yoga-sequencer (epic #368) but is domain-agnostic from the ground up.

## 0.2.0 — 2026-06-22 (Refs #465)

Valid-transition state machine.

- `scripts/state_machine.py` — `ValidTransitionMachine`, `ImpossibleTransitionError`
- Rule-based weight-shift and facing-continuity constraints (not hand-enumerated per style)
- 180° pivot gated behind bilateral or unweighted base
- Jump/unweighted transitions require bilateral base
