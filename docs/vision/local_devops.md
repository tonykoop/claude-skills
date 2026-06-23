> **Status: Speculative / Far-Future** — vision capture only, not a build plan.

# Local Version Control + Shadow Testing + Passive A/B

A personal app that can be reshaped by conversation is a personal app that can be broken by conversation. The platform's safety layer is a set of local devops mechanisms that make self-modification safe: immutable rollback checkpoints, a personal regression guard, and a passive A/B framework that lets changes prove themselves before being promoted.

## Local Time Machine: NL-Rollback Checkpoints

Every structural change to a blueprint creates a named, immutable checkpoint in the local version history. The user can roll back to any checkpoint by name, time, or description — without understanding git, diffs, or version numbers.

### What triggers a checkpoint

| Action | Checkpoint name (auto-generated) |
|---|---|
| Blueprint deep-edit via conversation | `"Before: removed audio feedback"` |
| Upstream blueprint update rebase | `"Before: upstream v1.3.0 rebase"` |
| Module substitution (OS-triggered) | `"Before: pitch-detection module swapped on macOS 17.0"` |
| User-initiated snapshot | `"Practice session 42 — milestone"` (user supplies name) |
| Blueprint publish | `"Before: published to marketplace as v2.0.0"` |

Checkpoints are stored as immutable snapshots of the blueprint YAML in a local `.versions/` directory alongside each blueprint file:

```
~/.local/share/personal-apps/blueprints/
├── ear-training-minor-intervals@1.2.0+tony.3.yaml     ← current
└── .versions/
    ├── ear-training-minor-intervals/
    │   ├── 2026-06-20T14:30_before-removed-audio.yaml
    │   ├── 2026-06-21T09:15_before-upstream-v1.3.0.yaml
    │   └── 2026-06-22T19:00_milestone-session-42.yaml
```

### Rollback UX

The user never types a SHA. They say: "Go back to before I removed audio feedback." The agent:
1. Searches checkpoint names for the closest match
2. Presents the checkpoint and a diff summary in plain language: "This will restore the `feedback_mode: immediate` setting and re-add the audio playback module. 3 sessions were run after this point and will still be in your history."
3. On confirmation, replaces the current blueprint with the checkpoint and creates a new checkpoint named `"After: rolled back to 'before-removed-audio'"`

Rollback is itself a checkpointed operation — it is never destructive.

### Retention policy

Checkpoints are retained by default for 90 days. The user can adjust this in preferences. Milestone checkpoints (user-named) are retained indefinitely. The total storage footprint is small: blueprints are text, so even 1,000 checkpoints rarely exceed a few megabytes.

## Personal Eval Dataset: Regression Guard

When a user reshapes a blueprint, the platform runs the new version against a personal eval dataset before promoting it to active use. This catches silent regressions — changes that feel right in conversation but break something the user cared about.

### Building the eval dataset

The personal eval dataset accumulates automatically from the user's session history:

- Each session produces a set of `(input, expected_output)` pairs: the questions asked, the answers given, the user's feedback signals (accepted, rejected, skipped)
- Pairs where the user gave a strong feedback signal (explicit correction, repeated error) are promoted to "regression-critical" status
- The dataset is stored locally in the context graph under `eval:personal/<blueprint-id>`

### Regression check flow

```
User requests deep-edit
        │
        ▼
Agent updates blueprint (not yet active)
        │
        ▼
Agent runs new blueprint against personal eval dataset (silent, background)
        │
        ▼
Compare outputs to expected (using same `low-latency` inference profile)
        │
        ├── All regression-critical cases pass → promote blueprint to active
        │
        └── One or more cases fail →
              Present failure in plain language:
              "The new version answered 'major third' for the interval
               you usually get right (D→F). The old version answered
               'minor third'. Do you want to keep the change anyway?"
```

The regression check runs silently in under 5 seconds for most blueprints (small eval datasets, fast inference). It does not block the user interaction; it runs after the blueprint is staged but before it replaces the active version.

### Eval dataset management

The user can:
- View the eval dataset for any blueprint ("show me what I'm being tested against")
- Promote specific session outputs to regression-critical status ("always check this one")
- Delete eval pairs that are no longer relevant ("I've moved past that; stop testing it")
- Export the dataset for sharing or external analysis

## Passive Behavioral A/B Testing

When the platform is uncertain about a blueprint change (e.g., the change affects a core flow where the user has mixed historical feedback), it can run both versions in parallel — the old and the new — and observe which produces better outcomes without asking the user to compare them explicitly.

### How it works

```
Two variants run in alternating sessions:
  Session N:    Active blueprint (control)   → log outcomes
  Session N+1:  New blueprint (treatment)    → log outcomes
  Session N+2:  Active (control)             → log outcomes
  ...

After K sessions per variant (default K=5):
  Agent compares outcomes on key metrics:
    - accuracy rate
    - session completion rate
    - user-initiated skips / overrides
    - time per question

If treatment is better on ≥2 metrics and not worse on any: promote treatment
If control is better: discard treatment, restore control, notify user
If inconclusive: ask user to choose ("Here's what I observed in each...")
```

### What "better" means

The platform does not define "better" globally. It infers it from the user's established feedback patterns in the context graph:

- If the user historically quits sessions that run long, "session completion rate" is a strong signal
- If the user historically accepts corrections without complaint, "accuracy rate" is the dominant signal
- The weighting is personalized and recalibrated every 30 days

### Transparency

Passive A/B is never hidden from the user. A small indicator in the HUD signals "I'm comparing two versions of this app." The user can disable A/B testing globally or per-blueprint.

## Integration with Per-Tenant Branching

The three mechanisms interact cleanly with the per-tenant branching model:

| Event | Checkpoint | Eval check | A/B |
|---|---|---|---|
| Deep-edit by user | ✓ before edit | ✓ on staged version | Optional (if high-risk edit) |
| Upstream rebase | ✓ before rebase | ✓ on rebased version | Optional (if upstream changed core behavior) |
| Module substitution | ✓ before substitution | ✓ on new module | Automatic (module swaps always A/B'd) |
| Rollback | ✓ before rollback | — (rolling back to known-good; no check needed) | — |

## Related Captures

- [malleable_software.md](malleable_software.md) — deep-edit and per-tenant branching that create the events this layer guards
- [blind_spot_engine.md](blind_spot_engine.md) — overnight Shadow Worker that also uses the eval dataset to validate synthesized apps
- [personal_apps.md](personal_apps.md) — the context graph that stores the personal eval dataset
