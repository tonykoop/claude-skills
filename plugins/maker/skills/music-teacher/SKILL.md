---
name: music-teacher
version: 0.1.0
last-updated: 2026-06-22
description: Profile music learners, track per-skill mastery on a 0.0–1.0 competency scale, and emit personalized multi-month practice plans of interleaved daily micro-drills. Use when the user says "help me practice [instrument]", "make me a practice plan", "what should I work on today", "assess my playing", "I want to learn [piece/technique]", "track my progress", "give me a drill for [skill]", or "how do I improve my [competency]". Three sub-roles, invoke one per session — Coach (the closed Profile→Curate→Calibrate→Mutate learning loop), Curator (graded repertoire + drill catalog + theory references), Translator (convert musical material across instruments, theory systems, and notation formats). Kora-first, extensible to wind, percussion, and dulcimer. Pairs with `sheet-music` and `instrument-maker`; canonical source is the tonykoop/music-teacher repo.
---

Agentic skill for profiling learners, tracking per-skill mastery, and emitting personalized multi-month practice plans.

## Trigger Phrases

- "help me practice [instrument]"
- "make me a practice plan"
- "what should I work on today"
- "assess my playing"
- "I want to learn [piece/technique]"
- "track my progress"
- "give me a drill for [skill]"
- "how do I improve my [competency]"

## Modes

| Mode | Description |
|------|-------------|
| **Coach** | Runs the closed learning loop: profiles the learner, curates drills, calibrates performance, mutates the syllabus. |
| **Curator** | Browses and recommends repertoire, drill catalogs, and method references without running the full loop. |
| **Translator** | Converts musical ideas across instruments, theory systems, or notation formats. |

## Capabilities

- Initial-state profiling: maps intake answers to a 0.0–1.0 competency baseline
- Mastery tracking: per-tag competency scores updated from drill results
- Closed-loop engine: Profile → Curate → Calibrate → Mutate Syllabus
- Multi-month plan generation: week-by-week interleaved micro-drills (5 min/day)
- Method library: Variable Tempo Training, Micro-Chunking, Interleaved Practice, Audiation
- Instrument adapters: Kora (primary), extensible to wind, percussion, dulcimer
- Human override: any auto-set competency value can be corrected by the learner

## Skill Boundaries

This skill covers **three distinct sub-roles**. Invoke one per session:

### Translator
Converts musical material across representations (e.g. kora fingering → guitar tab, West African rhythmic notation → standard notation). Does not track mastery or emit plans.

### Coach
The closed-loop tutor. Takes a learner profile, runs the four-stage learning loop, and emits a personalized syllabus. Does not generate new content — pulls from the Curator's catalog.

### Curator
Maintains and searches the content graph: graded repertoire, drill catalog, theory references, instrument-pairing knowledge. Does not adapt to individual learners — outputs are general.

## Architecture

```
SKILL.md          ← this file (trigger/mode/boundary spec)
engine/           ← LearningLoop state machine, profile CRUD
schemas/          ← JSON Schema + competency tag registry
planner/          ← roadmap generator (week-by-week plan)
methods/          ← deliberate-practice method library
intake/           ← profiling questionnaire
adapters/         ← per-instrument input adapters
data/             ← drills, repertoire, instruments, pairings, theory
docs/             ← design docs (engine loop spec, etc.)
game/             ← gamification layer (XP, quests, Kora Hero)
social/           ← recital hall, async jam, duo companion
improv/           ← improv evaluation + curriculum
production/       ← sampling pipeline, album assembly
sampling/         ← acoustic sample library + capture pipeline
```
