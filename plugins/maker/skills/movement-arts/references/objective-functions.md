# Objective Functions

Objective functions control *which* primitive the sequencer emits next, given the list of transition-valid candidates and the live tracker state.

## Contract

```python
class ObjectiveFn(ABC):
    def select_next(self, valid_primitives: list[dict], tracker: MovementTracker) -> dict | None:
        ...

    def __call__(self, valid_primitives, tracker) -> dict | None:
        return self.select_next(valid_primitives, tracker)

    def score(self, sequence: list[dict], tracker_history: list[dict]) -> float:
        return 0.0  # optional post-compilation evaluator
```

`select_next` is called for every block. It receives:
- `valid_primitives` — filtered by `ValidTransitionMachine` (weight + facing rules applied)
- `tracker` — live `MovementTracker` with `.current_state` (intensity, weight_distribution, facing_direction, clock_beat)

Return one dict from `valid_primitives`, or `None` to stop the sequence early.

## Auto-loading

The sequencer loads the right objective automatically from `domain["objective"]`:

```python
# No explicit objective_fn needed — loaded from domain JSON
seq = MovementSequencer(domain=hip_hop_domain)
```

To override:

```python
from scripts.objective import ForceObjective
seq = MovementSequencer(domain=kata_domain, objective_fn=ForceObjective())
```

## Available objectives

| Name | Class | Used by | Selection strategy |
|---|---|---|---|
| `style_expression` | `StyleObjective` | hip_hop, salsa, ballet, capoeira | Avoids immediate repetition; tracks sigmoid energy curve |
| `force_output` | `ForceObjective` | kata | Weights `acceleration_curve` (explosive/snap/impact) by current intensity |
| `joint_safety` | `JointSafetyObjective` | physical_therapy | Prefers low `velocity_cap_m_per_s`; penalises `unilateral_load` when imbalanced |
| `breath_alignment` | `BreathAlignmentObjective` | vinyasa, tai_chi | Minimises per-block intensity variance; follows the breath arc smoothly |

## score() — post-compilation evaluation

```python
seq = MovementSequencer(domain=vinyasa)
routine = seq.compile(60)
objective = seq._objective_fn
score = objective.score(
    [b.__dict__ for b in routine.blocks],
    routine.tracker_final_state.get("history", [])
)
```

`score()` returns a float (higher is better); interpretation is objective-specific:
- `StyleObjective.score` → variety ratio (unique IDs / total blocks)
- `ForceObjective.score` → fraction of explosive/snap/impact blocks
- `JointSafetyObjective.score` → 1 − (max velocity_cap in sequence)
- `BreathAlignmentObjective.score` → smoothness of intensity arc (1 = perfectly smooth)

## Adding a new objective

1. Subclass `ObjectiveFn` in `scripts/objective.py`.
2. Implement `select_next`.
3. Register in `_OBJECTIVE_REGISTRY`.
4. Set `"objective": "<your_name>"` in the domain JSON.
5. Add tests in `tests/test_movement_arts_objective.py`.
