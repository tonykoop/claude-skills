---
name: movement-arts
version: 0.1.0
last-updated: 2026-06-22
description: Design movement sequences across yoga, dance (hip-hop, salsa, ballet), martial arts (tai chi, capoeira, kata), and physical therapy by swapping the domain library while keeping the core arc engine intact. Use when planning a multi-discipline movement class, creating a cross-training routine, sequencing a hip-hop dance class, building a tai chi or capoeira session, generating movement cues for an instructor or audio pipeline, or when the user wants a universal movement sequence that spans more than one discipline. Also use when the user asks for a "movement class", "flow for any style", "dance sequence", "martial arts routine", "PT exercise sequence", or "cross-training flow". Do not use for pure yoga sequencing (use yoga-sequencer for that), live movement coaching, medical rehabilitation prescription, clinical physical therapy treatment plans, or any movement involving partner safety not covered by the domain safety gates.
---

# Movement Arts — Universal Movement Sequencer

Build movement class arcs that work across disciplines — yoga, dance, martial arts, and physical therapy — by swapping the domain library while keeping the sequencing engine intact.

## Core concept

The same mechanics drive every great class: a pacing arc, valid state transitions, an intensity curve, and mechanical safety gates. This skill separates:

- **Core engine** (`scripts/sequencer.py`, `scripts/tracker.py`) — domain-agnostic arc, intensity curve, and state tracker
- **Domain library** (`domains/*.json`) — style-specific primitives, clock type, and objective function
- **Objective function** (`scripts/objective.py`) — what "good" means per discipline (style expression, force output, joint safety, breath alignment)
- **State machine** (`scripts/state_machine.py`) — mechanically valid transitions regardless of domain

Load a different domain and the engine produces a hip-hop class; load another and it produces tai chi. The core never changes.

## Connectors

- **Spotify** — for audio-energy handoff after cue formatting; the playlist-builder can consume the `audio_energy` output format from this skill

## Supported domains

| Domain | Clock | Objective | File |
|---|---|---|---|
| vinyasa | breath-cycle | breath_alignment | `domains/vinyasa.json` |
| hip_hop | 8-count beat | style_expression | `domains/hip_hop.json` |
| salsa | on1/on2 musical phrase | style_expression | `domains/salsa.json` |
| ballet | musical phrase | style_expression | `domains/ballet.json` |
| tai_chi | slow-breath-arc | breath_alignment | `domains/tai_chi.json` |
| capoeira | 3-count ginga | style_expression | `domains/capoeira.json` |
| kata | embusen arc | force_output | `domains/kata.json` |
| physical_therapy | breath-cycle | joint_safety | `domains/physical_therapy.json` |

## Safety gates

**Physical therapy domain**: the sequencer refuses to emit a PT routine unless `safety_acknowledged=True` is passed by the caller. Always surface this gate to the user. PT libraries are informational movement patterns, not clinical rehabilitation protocols. Never substitute for licensed physical therapist guidance.

**General**: velocity caps, weight-shift feasibility, and unilateral-load limits are enforced by the state machine for all domains. The engine will not emit a physically impossible transition.

## Motion-primitives import seam

This skill is designed to accept an external primitives ontology from `tonykoop/offtheshelf#35` when it publishes. Until then, domain JSON files contain inline primitives following the same schema. The seam is documented in `references/motion-primitives-import.md`.

## Using the core engine

```bash
# Compile a 60-minute hip-hop sequence (demo mode, no domain file needed)
python3 plugins/maker/skills/movement-arts/scripts/sequencer.py --demo --json

# Compile from a domain file
python3 plugins/maker/skills/movement-arts/scripts/sequencer.py \
  --domain plugins/maker/skills/movement-arts/domains/vinyasa.json \
  --duration 60 --json

# Inspect tracker state after applying a primitive
python3 plugins/maker/skills/movement-arts/scripts/tracker.py --demo
```

## Using the state machine

```bash
# Get valid next maneuvers from a tracker state snapshot
python3 plugins/maker/skills/movement-arts/scripts/state_machine.py \
  --domain domains/hip_hop.json --state '{"weight_distribution":{"left":0.0,"right":1.0},"facing_direction":"north"}' 
```

## Using the cue formatter

```bash
# Verbal instructor script from a compiled routine JSON
python3 plugins/maker/skills/movement-arts/scripts/cue_output.py \
  --routine routine.json --domain vinyasa --format verbal

# Audio-energy handoff for playlist-builder
python3 plugins/maker/skills/movement-arts/scripts/cue_output.py \
  --routine routine.json --domain hip_hop --format audio_energy
```

## Using the cross-training generator

```bash
# Generate a vinyasa-capoeira hybrid class
python3 plugins/maker/skills/movement-arts/scripts/cross_training.py \
  --preset vinyasa-capoeira --duration 60 --json

# Custom 2-domain blend
python3 plugins/maker/skills/movement-arts/scripts/cross_training.py \
  --domains hip_hop kata --weights '{"hip_hop":0.6,"kata":0.4}' --duration 45 --json
```

## Default posture

- Default to vinyasa if no domain is specified and the request is yoga-adjacent.
- Default to 60-minute class if duration is not specified.
- Default to verbal cue output format unless the user requests audio or PT biomechanical cues.
- Treat PT domain as gated: always confirm `safety_acknowledged` before emitting any PT routine.

## Gather inputs

- Movement style or domain (yoga, hip-hop, dance, martial arts, PT, or cross-training blend)
- Duration in minutes
- Student or participant level
- Teaching format (class, personal practice, audio-driven, instructor-led)
- Any known constraints or injuries (for safety gate routing)

## Core workflow

1. Identify the domain (or cross-training blend).
2. Compile the routine arc using the sequencer.
3. Validate transitions with the state machine.
4. Format output for the target consumer (verbal / audio_energy / pt_biomechanical).
5. For cross-training, interleave domain blocks and run the shared state machine across domain boundaries.

## Sequencing rules

- Open simple, layer complexity — same arc principle as yoga.
- Intensity follows a sigmoid ramp unless the objective function overrides it.
- Valid transitions are enforced; the engine will not emit weight-shift violations or impossible facing changes.
- PT routines track velocity caps and unilateral load accumulation per block.
- Cross-training routines respect each domain's state machine at transition points.

## Output shape

For a full routine plan:
1. Routine summary: domain(s), duration, objective, clock type
2. Block-by-block sequence: primitive name, duration, energy level, cue density
3. Verbal cue script or audio-energy phase map (per format)
4. For cross-training: domain attribution per block

For lookup requests (valid transitions, objective comparison), return only the relevant subset.

## Pairings

- `yoga-sequencer` — for pure vinyasa flows with DJI Mic ingest, shorthand protocol, and Rosetta trainer
- `playlist-builder` — consumes the `audio_energy` output format for music matching
- `energy-management` — for scheduling movement sessions against available energy

## Final check before replying

- Is the arc coherent and does intensity ramp correctly?
- Are all transitions mechanically valid?
- Is the PT safety gate surfaced if the domain is `physical_therapy`?
- Is the output format matched to what the user asked for?
- For cross-training: do domain-boundary transitions respect both domains' state machines?
