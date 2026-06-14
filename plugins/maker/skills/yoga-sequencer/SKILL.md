---
name: yoga-sequencer
version: 1.2.2
last-updated: 2026-06-13
description: Design vinyasa-first yoga class sequences, peak-pose progressions, anatomical prep, counter-poses, heated-room safety adjustments, and full class plans with phase timing plus playlist-builder handoff data. Use when planning a yoga class, sequencing for hips, shoulders, twists, or backbends, choosing prep for a peak pose, adapting a hot-room class, or turning a class arc into music-ready phases.
---

# Yoga Sequencer

Build teachable yoga class arcs that work in a real room, not just as a pose list.

## Connectors

This skill works best with these MCP connectors. Claude will suggest connecting any that aren't already linked at the point they're needed (via `mcp__mcp-registry__suggest_connectors`).

- **Spotify** (`86925244-b3bb-415b-b7e8-6e3cd1392247`) — optional for the playlist-builder handoff. When the user wants a generated class to flow into a playlist, the sequencer hands phases to `playlist-builder`, which uses Spotify to materialize the tracks.

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

## Load references on demand

These references are bundled but not all are needed every time. Pull only what the current request actually uses, so the skill stays lean on context-constrained platforms (mobile, zip-uploaded skills, smaller runtimes).

- `references/poses.yaml`
  Query for specific lookups: prep ladder for a peak pose, counter-pose ideas, or constraint-aware substitutions. For a routine class plan that only uses the staple poses listed below, you usually do not need to open this file at all.
- `references/sequencing-principles.md`
  Open when you need the default arc by class length, peak-pose ladders, or the bilateral symmetry checklist.
- `references/heated-room-safety.md`
  Open for any heated-room, hot power, sculpt, C3-style, or sweaty public-class request. Use it for the standard safety checklist, heat-distress signs, hydration and breath-quality gates, pregnancy/non-heated substitutions, and cue-volume guidance as heat rises.
- `references/playlist-builder-handoff.md`
  Open when the user wants music or a phase-timing export.

### Staple pose cheat-sheet (two tiers)

The staple list is split by risk profile. Tier 1 covers everyday vinyasa shapes whose default cues and modifications are common knowledge — fine to sequence without opening `poses.yaml`. Tier 2 flags shapes that look routine but have failure modes the bundled library tracks explicitly (knees, low back, neck, wrists, SI joint, pregnancy). Use them, but always cross-reference `poses.yaml` first so the modifications and contraindications you cue are the ones the library actually documents.

**Tier 1 — safe-default staples (no `poses.yaml` lookup required):**

- arrival and breath: sukhasana, child's pose
- spinal warm-up: cat-cow, thread the needle
- sun salutation core: downward dog, plank, cobra, mountain
- standing build: warrior II, side angle, triangle, crescent lunge, chair, tree, low lunge
- cooldown: seated twist, supine twist, happy baby, legs up the wall, savasana

**Tier 2 — constraint-sensitive staples (always cross-reference `poses.yaml`):**

These shapes are still common in mixed-level vinyasa — keep using them — but their typical contraindications come up often enough that a quick lookup is cheap insurance and the right thing for student safety:

- hip openers: malasana, lizard, pigeon, reclined figure four
- backbends: bridge, locust, camel
- arm balances and inversions: crow, any inverted peak
- deep twists: revolved triangle, revolved crescent

Always open `poses.yaml` (regardless of which tier the pose lives in) when:

- the user names a constraint (wrists, knees, shoulders, low back, SI joint, neck, pregnancy, balance instability)
- the request is a counter-pose lookup — `counterposes_for` and `contraindications` are how the library encodes the right neutralizers
- a peak-pose-first sequence centers on a Tier 2 shape or any pose outside Tier 1
- the requested pose is not on either staple list

If `poses.yaml` is unavailable on the current platform (rare), say so explicitly, reason from general teaching knowledge, and bias toward more conservative modifications.

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
6. End any full class plan with the playlist phase-map YAML block. Skip it for pure lookup requests. See "When to include the playlist phase-map YAML" under Output shape.

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
- If the default peak is **constraint-heavy** — binds, deep twists, deep backbends, heavy wrist load, balance peaks, or anything contraindicated for pregnancy — also include a **teacher-discretion alternate peak**: a wholly different, gentler shape that lands the same theme. This is more than a regression. It is the peak you teach when the room reads tired, brand-new, or pregnancy-heavy. See `references/sequencing-principles.md` for the alternate-peak pattern and worked examples.

### Anatomical prep lookup

When the user wants prep for an area or action, return:

- key joint or muscle actions
- 4 to 8 useful prep poses
- 1 or 2 "do less" options
- the point at which to stop adding intensity

### Counter-pose lookup

Always open `poses.yaml` for this mode, even when the target pose is one you think you know cold. The bundled library encodes the right neutralizers in the `counterposes_for` field, and the `contraindications` field tells you which "obvious" counter-shapes are actually wrong for a mixed-level room. Skipping the lookup is how you end up recommending a deep forward fold straight after camel, or supine twist for a student whose SI joint is the reason they came to class.

When the user gives a pose or family, return:

- what the pose loaded most heavily — cross-reference `focus`, `intensity`, and `family` in `poses.yaml`
- 2 to 5 reasonable counter-shapes — start from poses whose `counterposes_for` lists the target, then add common-sense neighbors
- whether the best follow-up is a full counterpose, a neutral reset, or rest
- contraindications worth naming briefly if the room is mixed-level

Do not force dramatic opposites. After deep backbends, twists, balances, or arm loads, a neutralizing transition is often better than a hard reversal.

### Full-class generation

Produce a phase-by-phase plan with:

- phase name
- approximate minutes or breath counts
- intent
- pose order
- notable cues, modifications, or cautions
- **cue density** — how much teacher voice belongs in the phase: `sparse`, `moderate`, `rhythmic`, `focused`, or `minimal`. See `references/sequencing-principles.md` for default arcs by class length and style.

Always include warm-up, standing build, peak or focal work, counterpose, cooldown, and savasana.

For heated-room or hot power requests, also include a short teacher-usable safety checklist:

- hydration and permission to downshift without rushing to rejoin
- breath-quality gate: if breath gets ragged, the advanced option is to reduce intensity
- heat-distress signs such as dizziness, tunnel vision, nausea, chills, goosebumps, confusion, unusual shortness of breath, glassy eyes, loss of coordination, or the sense that the room suddenly got hotter
- pregnancy, heat-avoidance, and non-heated substitution path: open twists, supported balance, less compression, and rest options
- cue-volume arc: teacher voice gets quieter as repetition and heat rise; the peak is focused, not loud

### Playlist handoff

Do not generate songs. Emit the phase-map YAML block described in `references/playlist-builder-handoff.md` directly in your reply, as portable data the user can paste into `yoga-playlist-builder`, another Claude session, or any other tool. Do not assume the companion skill is installed on the current platform.

The YAML is part of the contract for any full class plan — see "When to include the playlist phase-map YAML" under Output shape for the exact rule.

## Sequencing rules

- Open simple, then layer complexity.
- Avoid advanced poses without prep, modification guidance, and a clear reason they belong.
- Do not let one joint action dominate too long without relief.
- Keep floor-to-stand and stand-to-floor transitions intentional instead of fussy.
- If crow, inversion, deep twist, or deep backbend appears, give it runway and recovery.
- Match breath cadence to the class goal: steadier for grounding, quicker only when the user clearly wants heat.
- If one side gets extra rounds, state why and re-balance later when possible.
- Manage teacher voice across the arc. Cue density rises into the peak (focused) and falls into savasana (minimal). Avoid lyric-dense or wordy cueing during focused phases — students need silence for proprioception.
- In heated rooms, protect breath and attention by lowering cue volume as repetition and heat rise: teach landmarks early, then use fewer words, repeated anchor cues, and longer quiet stretches.
- When the default peak is constraint-heavy (binds, deep twists, deep backbends, balance peaks, heavy wrist load, pregnancy-contraindicated), include a teacher-discretion alternate peak — a wholly different gentler shape that still lands the theme. This is the peak you teach when the room reads tired, brand-new, or pregnancy-heavy. A regression of the default is not a substitute.

## Safety and scope

- Stay in teaching-planning language, not medical advice.
- If a request centers on injury treatment, rehab, or guaranteed safety, say that this skill can only offer general class-planning adjustments.
- Prefer accessible regressions for mixed-level rooms.
- Name obvious caution zones for advanced poses or strong ranges of motion.
- For hot-room classes, use calm teacher language instead of legal disclaimers: name downshift options, breath-quality gates, hydration reminders, heat-distress signs, and non-heated or pregnancy-aware substitutions.

## Output shape

For a full sequence, use this structure unless the user asks for something shorter:

1. Class summary: length, level, theme, peak pose, energy. If the default peak is constraint-heavy, also name the teacher-discretion alternate peak.
2. Sequence by phase: timing, intent, pose order, brief cues, **cue density** (sparse / moderate / rhythmic / focused / minimal).
3. Modifications and cautions.
4. Playlist phase-map YAML block (see rule below). Each phase should carry both `energy` and `cue_density`.

For lookup requests (counter-pose, anatomical prep, single-pose modifications), return only the smallest useful subset and skip the playlist YAML.

### When to include the playlist phase-map YAML

The phase-map block is part of the contract for a complete class plan, not an optional add-on. This rule exists so a teacher who asks for a class never gets handed back a sequence without the timing block they need to plan music, watch the clock, or hand off to `yoga-playlist-builder`.

**Always include the YAML when any of these are true:**

- the user asked for a full class, full sequence, or any output containing phase-by-phase timing
- the user mentioned music, playlists, or `yoga-playlist-builder`
- the user said "playlist-ready" or "playlist-builder handoff"

**Skip the YAML only when:**

- the user asked for a pure lookup — counter-poses for X, prep for Y, modifications for Z
- the user explicitly requested no music or no handoff
- the output is a fragment such as "just give me a warm-up" with no full arc to map

If you are unsure whether the request is full-class or lookup, default to including the YAML. It is cheap to produce and ignorable if unused, and the failure mode of omitting it (a teacher missing the timing block they expected) is worse than the failure mode of including it.

## Pairings

These are optional collaborators, not requirements. The skill should produce a complete, self-contained class plan even if none of them are installed on the current platform.

- `yoga-playlist-builder` for music selection and phase-matched track planning, when available
- `energy-management` when class design must fit the user's week, energy, or teaching schedule
- `idea-incubator` when the user wants class themes, workshop angles, or retreat concepts

## Final check before replying

- Is the class arc coherent?
- Is unilateral work balanced?
- Is the peak earned rather than dropped in?
- Is there a believable cooldown?
- Did you include playlist-ready timing when relevant?
- Did you map cue density across the arc, and does it ease toward `minimal` for savasana?
- For heated-room classes, did you include the safety checklist and make the teacher voice quieter as repetition and heat rise?
- If the peak is constraint-heavy, did you offer a teacher-discretion alternate peak (not just a regression)?
