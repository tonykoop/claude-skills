# Observation Template

Use this template for reverse-engineering notes. Keep facts and inferences apart even when the answer is obvious to a human.

## Intake (required)

Fill this YAML block before any other section. Downstream tooling parses it.

```yaml
intake:
  image_access_mode: direct      # one of: direct | file-path | description-only | missing | partial | named-object
  images_referenced: 0           # count of images the user pointed at
  images_viewable: 0             # count the runtime actually rendered
  recovery_path: not-needed      # one of: not-needed | requested-and-supplied | requested-and-declined | not-applicable
  source_qualifiers: []          # e.g. [user-prose, named-class, dictated, sketch, video-still]
  confidence_ceiling: full       # one of: full | provisional | speculative
  notes: ""                      # free-form: link to recovery transcript, runtime, etc.
```

When `image_access_mode` is anything other than `direct`, the analysis must also lead with the standardized degraded-mode banner from `SKILL.md`.

## Input Inventory

| Input | Source | Reliability | Notes |
| --- | --- | --- | --- |
| Photo / sketch / link / user statement | filename, URL, or user | high / medium / low | Viewpoint, scale reference, date, access limits |

## Observed Facts

Only list what is directly visible or explicitly supplied by the user.

| ID | Fact | Evidence | Claim type | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
| O-001 |  | image/file/user statement | observed | high |  |

## Measured Values

Use measured values when the user supplies dimensions or a reliable scale reference makes a measurement defensible.

| ID | Feature | Value | Units | Method | Tolerance | Confidence | Verification needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M-001 |  |  |  | caliper / ruler / image scale / user stated |  | high / medium / low |  |

## Inferred Facts

Every inference needs a basis and a way to verify it.

| ID | Inference | Basis | Claim type | Confidence | Verification |
| --- | --- | --- | --- | --- | --- |
| I-001 |  | visible feature, comparable part, physics, common construction | inferred | medium | Measure / inspect / test |

## Assumptions

Assumptions are temporary choices made to keep analysis moving. Do not let them enter a build handoff as facts.

| ID | Assumption | Why it is being used | Risk if wrong | How to retire it |
| --- | --- | --- | --- | --- |
| A-001 |  |  |  |  |

## Unknowns

| ID | Unknown | Why it matters | Blocking? | Best next evidence |
| --- | --- | --- | --- | --- |
| U-001 |  |  | yes / no | photo / measurement / teardown / test |

## Dimension Table

| Feature | Observed geometry | Estimated range | Measured value | Units | Source | Confidence | Builder critical? |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  | yes / no |

## Mechanism or Construction Hypothesis

- **Working model:** One or two sentences explaining how the object likely works or is assembled.
- **Evidence for:** Visible features that support the model.
- **Evidence against / weak spots:** Missing views, alternative mechanisms, contradiction risks.
- **Tests:** Manual movement, teardown, probe, measurement, acoustic test, electrical continuity, or material test.

## Builder Readiness

| Gate | Status | Notes |
| --- | --- | --- |
| Functional goal is clear | pass / partial / fail |  |
| Critical dimensions are measured or bounded | pass / partial / fail |  |
| Materials/processes are known or substitutable | pass / partial / fail |  |
| Interfaces and tolerances are documented | pass / partial / fail |  |
| Safety/legal/product risks are surfaced | pass / partial / fail |  |
| Unknowns are non-critical or test-assigned | pass / partial / fail |  |
