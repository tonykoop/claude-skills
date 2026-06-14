# Round 8 Heated-Room Safety Eval

Issue: `tonykoop/claude-skills#95`

## Evidence Used

- `/tmp/twingrid-r8-gpt54-bob-flow-state-c3/v2-class-plan.md`
- `/tmp/twingrid-r8-gpt54-bob-flow-state-c3/partner-peek-improvements.md`
- `/tmp/twingrid-r8-gpt54-bob-flow-state-c3/validation_notes.md`

## Fixture

Prompt:

> Use `$yoga-sequencer` to build a 60-minute advanced hot power vinyasa class themed on flow state. Include heated-room safety, cue density, a crow peak, pregnancy-aware options, and playlist-ready phase timing.

Expected behavior:

- Open `references/heated-room-safety.md`.
- Include hydration, breath-quality gating, heat-distress signs, and downshift options.
- Include pregnancy / non-heated substitutions.
- Make the cue arc quieter as repetition and heat rise.
- Keep teacher language practical, not legalistic.

## Worked Example Excerpt

```markdown
## Heated-Room Safety

- Start at 70-75% effort; downshifting early is advanced practice.
- Sip water when needed and rejoin without rushing.
- If breath becomes ragged, reduce range, skip the next vinyasa, or rest.
- Rest or leave the room calmly for dizziness, tunnel vision, nausea, chills,
  goosebumps, confusion, unusual shortness of breath, glassy eyes, loss of
  coordination, or the feeling that the room suddenly got hotter.
- Pregnancy / non-heated path: open twists, supported balance, boat-pose
  compression instead of crow, and side-lying or bolstered rest.

| Time | Phase | Cue density | Teacher voice |
|---:|---|---|---|
| 0-5 | Arrival / heat contract | sparse | one safety line, one breath cue |
| 5-12 | Warm-up | moderate | wrists, shoulders, spine, pacing |
| 12-20 | Sun A | rhythmic | breath-to-movement patterning |
| 20-34 | Standing repetition | rhythmic -> focused | teach first pass, quiet second pass |
| 34-44 | Crow focus | focused | setup, exit, quiet attempts |
| 44-56 | Cooldown | sparse | unload wrists, slow breath |
| 56-60 | Savasana | minimal | quiet landing |
```

## Manual Result

Pass. The new reference gives the skill a reusable hot-room safety checklist and a concrete cue-volume arc that can be inserted into full hot power class outputs without turning the response into legal language.
