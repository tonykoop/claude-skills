---
name: yoga-sequencer
description: Design vinyasa-first yoga class sequences, peak-pose progressions, anatomical prep, counter-poses, and full class plans with phase timing plus playlist-builder handoff data. Use when planning a yoga class, sequencing for hips, shoulders, twists, or backbends, choosing prep for a peak pose, or turning a class arc into music-ready phases.
---

# Yoga Sequencer

Build teachable yoga class arcs that work in a real room, not just as a pose list.

## Default posture

- Default to vinyasa unless the user explicitly asks for another style.
- Default to a 60-minute mixed-level public class if length or level is missing.
- Keep bilateral symmetry unless the user wants an intentionally asymmetric workshop or drill.
- Treat injuries, pain, and health conditions as constraints to respect, not diagnoses to solve.

If the request is clearly for yin, restorative, hot power, prenatal, or therapy-adjacent work, pause and ask before improvising a non-vinyasa approach.

## Use this skill for

- theme-first class planning
- peak-pose-first sequencing
- anatomical prep lookup
- counter-pose lookup
- full class generation
- playlist-builder handoff

## Load these references

- `references/poses.yaml`
  Use for starter pose metadata, prep relationships, counter-pose ideas, and constraint-aware substitutions.
- `references/sequencing-principles.md`
  Use for arc design, timing heuristics, symmetry checks, and intensity management.
- `references/playlist-builder-handoff.md`
  Use when the user wants music, phase timing export, or a clean handoff to `yoga-playlist-builder`.

## Gather inputs

Collect what matters, but do not over-interview. If details are missing, choose reasonable defaults and state them.

- class length
- student level
- theme or teaching focus
- peak pose, if any
- energy goal
- constraints, including wrists, knees, shoulders, low back, pregnancy, or "keep it simple"

## Core workflow

1. Pick the mode.
2. Define the class arc before choosing every pose.
3. Build a preparation ladder that earns the most demanding shape.
4. Mirror unilateral work or explain a deliberate asymmetry.
5. Include a downshift: counterpose, cooldown, and savasana.
6. Output phase timing that can be handed to `yoga-playlist-builder`.

## Mode guide

### Theme-first

Start with the felt or anatomical theme, then choose pose families that express it.

- Theme examples: grounding, shoulder opening, twisting, heart opening, hips, balance.
- Let the theme shape repetition, cueing, and pace.
- Add a peak pose only if it clarifies the class rather than hijacking it.

### Peak-pose-first

Start from the most demanding shape and work backward.

- Use `poses.yaml` to identify required actions, likely prep poses, and safer regressions.
- Build heat, mobility, strength, and pattern recognition before the peak.
- Include at least one simpler version or exit ramp.

### Anatomical prep lookup

When the user wants prep for an area or action, return:

- key joint or muscle actions
- 4 to 8 useful prep poses
- 1 or 2 "do less" options
- the point at which to stop adding intensity

### Counter-pose lookup

When the user gives a pose or family, return:

- what the pose loaded most heavily
- 2 to 5 reasonable counter-shapes
- whether the best follow-up is a full counterpose, neutral reset, or rest

Do not force dramatic opposites. After deep backbends, twists, balances, or arm loads, a neutralizing transition is often better than a hard reversal.

### Full-class generation

Produce a phase-by-phase plan with:

- phase name
- approximate minutes or breath counts
- intent
- pose order
- notable cues, modifications, or cautions

Always include warm-up, standing build, peak or focal work, counterpose, cooldown, and savasana.

### Playlist handoff

Do not generate songs. Export the phase structure and energy map described in `references/playlist-builder-handoff.md`, then hand off to `yoga-playlist-builder`.

## Sequencing rules

- Open simple, then layer complexity.
- Avoid advanced poses without prep, modification guidance, and a clear reason they belong.
- Do not let one joint action dominate too long without relief.
- Keep floor-to-stand and stand-to-floor transitions intentional instead of fussy.
- If crow, inversion, deep twist, or deep backbend appears, give it runway and recovery.
- Match breath cadence to the class goal: steadier for grounding, quicker only when the user clearly wants heat.
- If one side gets extra rounds, state why and re-balance later when possible.

## Safety and scope

- Stay in teaching-planning language, not medical advice.
- If a request centers on injury treatment, rehab, or guaranteed safety, say that this skill can only offer general class-planning adjustments.
- Prefer accessible regressions for mixed-level rooms.
- Name obvious caution zones for advanced poses or strong ranges of motion.

## Output shape

For a full sequence, use this structure unless the user asks for something shorter:

1. Class summary: length, level, theme, peak pose, energy.
2. Sequence by phase: timing, intent, pose order, brief cues.
3. Modifications and cautions.
4. Playlist-builder handoff block.

For lookup requests, return only the smallest useful subset.

## Pairings

- `yoga-playlist-builder` for music selection and phase-matched track planning
- `energy-management` when class design must fit Tony's week, energy, or teaching schedule
- `idea-incubator` when the user wants class themes, workshop angles, or retreat concepts

## Final check before replying

- Is the class arc coherent?
- Is unilateral work balanced?
- Is the peak earned rather than dropped in?
- Is there a believable cooldown?
- Did you include playlist-ready timing when relevant?
