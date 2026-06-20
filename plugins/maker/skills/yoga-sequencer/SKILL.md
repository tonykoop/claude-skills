---
name: yoga-sequencer
version: 2.1.0
last-updated: 2026-06-20
description: Design vinyasa-first yoga class sequences, peak-pose progressions, anatomical prep, counter-poses, heated-room safety adjustments, shorthand protocol parsing, transition-matrix lookup, Rosetta shorthand-transcript alignment, phase-gated class ingest, Reverse Sequence Engine scaffolds, DJI Mic capture QA, full class plans with phase timing plus playlist-builder handoff data, transitions-only classes where poses are never named and the connective tissue between shapes is the unit of instruction, and savasana-backward classes designed from final rest toward the minimum disturbance required to earn it. Use when planning a yoga class, sequencing for hips, shoulders, twists, or backbends, choosing prep for a peak pose, adapting a hot-room class, defining shorthand tokens or macros, parsing a five-line shorthand class, inspecting transitions between poses, aligning shorthand to transcript spans, phase-gating captured class JSON, splitting DJI Mic captures into transcript/audio paths, expanding shorthand into a 60-minute reviewed script scaffold, turning a class arc into music-ready phases, teaching movement without ever naming a pose, or designing stillness-first classes from a SavasanaSpec.
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
- `references/pose_thesaurus.json`, `config.toml`, and `scripts/engine_config.py`
  Use when the user asks about shorthand tokens, starter vocabulary, parser configuration, or audio-sync settings. The thesaurus maps public shorthand tokens to pose names and metadata; `config.toml` exposes `current_phase`, `syntax_strictness`, and audio LUFS; the script loads both at runtime.
- `references/shorthand-protocol.md`
  Open when the user asks how to write shorthand, define macros, use breath operators, or check whether a compact class sketch is parseable.
- `references/transition-matrix.json` and `scripts/transition_matrix.py`
  Use when the user asks about the "space between" poses, pathways into a target pose, transcript cue text for a transition, or pacing-to-crossfade handoff.
- `references/rosetta-trainer.md` and `scripts/rosetta_trainer.py`
  Use when the user asks to pair shorthand with transcript spans, extract somatic spacing, label structural transitions, find thematic-infusion points, or check whether paired data is trusted for training.
- `references/phase-gate-ingest.md` and `scripts/phase_gate_ingest.py`
  Use when the user asks to ingest one or more captured classes, produce the four-array parse target, or run anchor / triangulation / micro-batch / bulk go/no-go gates.
- `references/reverse-sequence-engine.md` and `scripts/reverse_sequence_engine.py`
  Use when the user asks to expand compact shorthand into a 60-minute class script scaffold with transitions, phases, thematic slots, playlist timing, and human-review gating.
- `references/savasana-backward.md` and `scripts/savasana_backward.py`
  Use when the user wants to design a class backward from final rest — define the somatic quality of savasana first, then derive the minimum disturbance required to earn it. See "Savasana-backward" under Mode guide.
- `references/dji-mic-capture.md` and `scripts/dji_mic_ingest.py`
  Use when the user asks to validate a DJI Mic class capture, split it into transcript/thematic and audio/playlist paths, or check whether capture quality is safe for Rosetta ingest.

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

## Transitions-only mode

Transitions-only is an inverted teaching mode where the unit of instruction is the **transition** — the connective tissue between shapes — and poses are never named. The "shapes" are merely where a transition momentarily slows down; they are incidental waypoints, not the thing being taught.

Use this mode when the user asks for:
- "teach the space between the poses"
- "never name the poses"
- "transitions-only class"
- a class framed around movement, unfolding, or breath-led travel rather than pose lists

### Constraint
Every cue must describe **how the body moves**, not **where it arrives**. Pose names (Sanskrit, English, or shorthand tokens) must not appear in any cue text. The `TransitionCue` dataclass enforces this at construction time — it raises `TransitionsClassError` if a forbidden token is detected.

### Reference template
`references/transitions-class-template.json` is a 60-minute starter template. Load it with:

```bash
python3 plugins/maker/skills/yoga-sequencer/scripts/transitions_class.py --template references/transitions-class-template.json
python3 plugins/maker/skills/yoga-sequencer/scripts/transitions_class.py --template references/transitions-class-template.json --json
```

### Arc
The 60-minute arc uses six phases: `arrival`, `warm_up`, `standing_flow`, `peak_work`, `cooldown`, `stillness`. Each phase label avoids Sanskrit so no pose vocabulary bleeds through even in section headers.

### Extending the template
To build a custom transitions-only class, load `TransitionsOnlyClass.from_template()` or construct one directly via `TransitionsOnlyClass.add_cue()`. Call `.validate()` before emitting — it checks total duration (±90 s), bilateral symmetry, and non-empty arc.

## Shorthand engine support

Treat shorthand support as a public interface layer, not a promise that the private corpus or voice model is installed. For shorthand-token setup, use `references/pose_thesaurus.json` as the starter token source of truth and `config.toml` as the operator-tunable dashboard.

- Starter pose tokens include `DD`, `HL`, `FF`, `RLH`, `CL`, and `PT`.
- The starter `Viny` macro expands to `PL > CH + UD > DD`.
- Directional and placement suffixes use `_r`, `_l`, `_f`, `_b`, `_open`, and `_cl`.
- Breath and pacing operators include `+`, `>`, `//`, and integer breath counts such as `5B`.
- Macro definitions use `Name = expression`, for example `Viny = PL>CH+UD>DD`.
- `syntax_strictness = "strict"` rejects unknown pose tokens; `syntax_strictness = "draft"` allows placeholder tokens for authoring experiments; `starter` is the packaged default.
- `audio_sync.lufs_target` is the public audio handoff target for downstream playlist or DJ tooling. Do not infer private mastering, sampler, or corpus logic from this value.

When a task needs deterministic token inspection, run:

```bash
python3 plugins/maker/skills/yoga-sequencer/scripts/engine_config.py "Viny // 5B" --json
```

For a multiline shorthand sketch, put one macro or sequence per line and run:

```bash
python3 plugins/maker/skills/yoga-sequencer/scripts/engine_config.py --program-file shorthand.txt --json
```

## Transition matrix support

Treat transitions as vectors: `origin shape -> pathway modifier -> target shape`. Use `references/transition-matrix.json` for the public starter matrix and `scripts/transition_matrix.py` for deterministic lookup.

- Crescent Lunge (`CL`) is the first documented multi-entry target.
- Each transition carries `origin`, `pathway`, `target`, `pacing`, `transcript_cue`, and `shorthand`.
- `pacing` maps to playlist/DJ handoff crossfade seconds: `fast`, `medium`, or `slow`.
- The public `transcript_cue` field is a teacher-facing cue template, not private live-class transcript data.

To inspect pathways into Crescent Lunge:

```bash
python3 plugins/maker/skills/yoga-sequencer/scripts/transition_matrix.py --target CL
```

## Rosetta trainer support

Treat the Rosetta trainer as a deterministic labeling and quality-gate layer, not a private voice model. It aligns shorthand rows to transcript spans and returns labels that a future private trainer can consume after human review.

- Input is JSON with `pairs[]`, where each pair has `shorthand`, `transcript.start_sec`, `transcript.end_sec`, `transcript.text`, and `human_review.status`.
- The trainer extracts somatic spacing, structural transitions, thematic-infusion terms, draft token flags, and a quality gate.
- Output is trusted only when every pair has positive transcript duration, no draft tokens, at least one structural transition, at least one thematic-infusion point, and approved human review.
- Keep private class transcripts and learned voice data out of this public repo.

Run:

```bash
python3 plugins/maker/skills/yoga-sequencer/scripts/rosetta_trainer.py rosetta-class.json
```

## Phase-gate ingest support

Use the phase-gate ingest layer before feeding class captures into Rosetta training.

- Input is class JSON with `metadata` fields and timed `segments`.
- Output always uses the four-array target: `metadata`, `audio_timeline`, `choreography_raw`, and `thematic_drops`.
- Gates are `anchor` (1 class), `triangulation` (3+ classes), `micro_batch` (3-5 classes), and `bulk` (35+ classes).
- Gates fail closed on malformed timing, missing segments, missing shorthand, or an absent output array.
- Keep private corpus files outside this repo; pass local/private JSON paths at runtime.

Run:

```bash
python3 plugins/maker/skills/yoga-sequencer/scripts/phase_gate_ingest.py anchor class.json
```

## Reverse sequence engine support

Use the Reverse Sequence Engine to expand shorthand into a reviewed 60-minute class scaffold.

- Input is one macro or shorthand sequence per line.
- Output includes expanded tokens, transition handoffs, six timed phases, script lines, and playlist phase-map data.
- The public engine emits `voice_mode: public_teacher_style_scaffold`; it does not claim the private Tony voice model is present.
- `trusted_for_teaching` stays false until a named human reviewer approves the draft.

Run:

```bash
python3 plugins/maker/skills/yoga-sequencer/scripts/reverse_sequence_engine.py shorthand.txt --reviewer tk
```

## DJI Mic capture support

Use the DJI Mic ingest layer when a live class capture needs to feed both Rosetta and playlist/DJ tooling.

- Input is a capture manifest, not raw audio.
- Path A emits transcript spans, thematic script extraction, and `rosetta_ready`.
- Path B emits an audio timeline handoff with phase, energy, and cue-density fields.
- Capture quality fails closed for loud music beds, high movement noise, dropouts, clipping, empty transcript text, or malformed timing.
- Keep raw audio and private ASR output outside this repo.

Run:

```bash
python3 plugins/maker/skills/yoga-sequencer/scripts/dji_mic_ingest.py capture.json
```

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

### Savasana-backward

Start from the somatic quality of rest you want students to land in, then
derive the minimum disturbance — the fewest movements whose absence would
leave the stillness unearned.

1. Elicit the **SavasanaSpec**: what does the rest need to feel like? Name at
   least one `target_release` (body area that must have worked and released)
   and one `rest_quality` descriptor (e.g. `"symmetric_weight"`), plus an
   `emotional_landing` phrase (e.g. `"earned ease"`).
2. Derive the **minimum disturbance set** using the economy pass in
   `scripts/savasana_backward.py`: prefer movements that address multiple
   releases in a single shape.
3. Apply the **justification filter**: for every movement, confirm that its
   absence would leave the rest unearned. If you cannot write that sentence,
   remove the movement.
4. Assign to the four-phase arc: `arrival_warm_up → release_work →
   integration_cooldown → savasana`. Cue density eases to `minimal` well
   before the floor.
5. Output the disturbance set with justifications, phases, and playlist
   phase-map YAML.

Run deterministically:

```bash
python3 plugins/maker/skills/yoga-sequencer/scripts/savasana_backward.py spec.json --reviewer tk
```

See `references/savasana-backward.md` for the SavasanaSpec contract,
available release keys, and the comparison with peak-pose-first.

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
