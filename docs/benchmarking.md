# Skill Benchmarking

The benchmark model is inspired by the instrument-maker benchmark suite:
fixed prompts, explicit watch-points, and run logs that make regressions visible.

## Benchmark Shape

Each benchmark should define:

- skill under test;
- runtime under test;
- prompt fixture;
- expected mode or route;
- expected artifacts;
- watch-points;
- pass/fail notes;
- manual interventions.

## Initial Watch-Points

- Trigger accuracy: the right skill activates.
- Routing accuracy: umbrella skills delegate rather than doing specialist work.
- Context discipline: the skill loads only needed references.
- Version awareness: the skill reports its own version when asked.
- Portability: output is not hard-coded to one project base.
- Handoff quality: generated issues/prompts are enough for another agent to act.

