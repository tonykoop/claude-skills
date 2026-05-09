# DoE Template

Use this reference when the user wants an experiment, validation plan,
prototype comparison, parameter sweep, or tuning loop for a physical project.

## DoE Intake

Capture:

- experiment question;
- hypothesis;
- response metrics;
- factors and levels;
- constants/controls;
- nuisance variables;
- available instruments and measurement method;
- sample count or build budget;
- success threshold and stop condition.

## Minimal Output Structure

```text
Experiment question:
Hypothesis:
Primary response metric:
Secondary metrics:
Factors:
Constants:
Trial matrix:
Measurement method:
Logging fields:
Analysis plan:
Stop condition:
Specialist handoffs:
```

## Factor Table

| Factor | Level A | Level B | Level C | Notes |
| --- | --- | --- | --- | --- |
| <factor> | <value> | <value> | <optional> | <measurement or build note> |

Use two levels for fast screening. Use three levels when curvature or tuning
nonlinearity is likely and the build budget can support it.

## Trial Matrix

For two or three factors, prefer a full factorial if feasible. For four or more
factors, propose a screening matrix first and explicitly mark follow-up trials.

| Trial | Factor 1 | Factor 2 | Factor 3 | Replicate? | Response metric | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Low | Low | Low | No |  |  |
| 2 | High | Low | Low | No |  |  |
| 3 | Low | High | Low | No |  |  |
| 4 | High | High | Low | No |  |  |

Add randomization when order effects matter, such as tool wear, temperature,
humidity, curing time, operator fatigue, or instrument warm-up.

## Measurement Discipline

- Define units before the trial starts.
- Record raw measurements, not only pass/fail decisions.
- Keep one photo or sketch field for physical builds.
- Note tool setup, material batch, operator, date/time, and environment.
- Include at least one repeated baseline when practical.

## Specialist Boundaries

If the DoE needs a specialist deliverable, route that part separately:

- Acoustic target, tuning model, or playable geometry: `instrument-maker`.
- Fixture, toolpath, workholding, or shop operation: `makerspace`.
- Measurement extraction from an existing object: `reverse-engineer`.
- Early concept selection before experiments: `idea-incubator`.
