# Reverse Sequence Engine

Use this reference when expanding compact yoga shorthand into a full 60-minute class scaffold. This public engine is deterministic and review-gated. It does not contain Tony's private voice model or class corpus.

## Input

One macro or sequence per line:

```text
Viny = PL>CH+UD>DD
DD // 5B
RLH_r > CL_r // 5B > PT_r
RLH_l > CL_l // 5B > PT_l
FF > HL + FF > Viny
```

Optional metadata:

- `theme`
- `level`
- `energy`
- `reviewer`

## Output

The engine emits:

- `class_summary`
- `expanded_tokens`
- `transition_handoffs`
- `phases` totaling 60 minutes
- `script_lines`
- `playlist_phase_map`
- `quality_gate`

## Review Gate

Public generation is never autopilot. `trusted_for_teaching` is false until:

- shorthand parses without draft tokens
- the output totals exactly 60 minutes
- transition handoffs are present
- thematic infusion slots are present
- a named human reviewer approves the draft
- private voice/corpus review, if required, happens outside this public repo

Use this output as a class-script scaffold for review, not as a final claim that the private voice model has been trained.
