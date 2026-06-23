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

## 0.4.0 — 2026-06-22 (Refs #467)

Domain registry: tai chi / capoeira / kata / physical therapy.

- `domains/tai_chi.json` — 24 primitives, legato breath clock 6bpm, breath_alignment objective; Yang-style 24-form moves (ward-off, rollback, press, push, single-whip, cloud-hands, closing form)
- `domains/capoeira.json` — 18 primitives, 3-count beat clock, style_expression objective; ginga loop, esquivas, aú, meia-lua de frente/compasso, armada, macaco, rasteira
- `domains/kata.json` — 18 primitives, kime-burst breath clock, force_output objective; per-primitive `acceleration_curve` and `embusen_direction` fields
- `domains/physical_therapy.json` — 21 primitives, controlled breath clock, joint_safety objective; `requires_clinical_review: true` safety gate; per-primitive `velocity_cap_m_per_s`, `unilateral_load`, `ROM_target_deg`

## 0.3.0 — 2026-06-22 (Refs #466)

Domain registry: vinyasa / hip-hop / salsa / ballet.

- `domains/vinyasa.json` — 31 primitives, breath clock, breath_alignment objective; reuses yoga flow structure
- `domains/hip_hop.json` — 19 primitives, 8-count beat clock, tutting/isolation/cypher-step
- `domains/salsa.json` — 14 primitives, linear-slot geometry, on1/on2 timing
- `domains/ballet.json` — 23 primitives, musical-phrase clock, plié/tendu/pirouette/jeté
- `references/domain-registry.md` — how domains load; schema reference
