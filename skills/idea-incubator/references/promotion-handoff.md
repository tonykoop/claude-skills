# Promotion Handoff

Promotion means moving an incubated idea into a target repo, project board, or
specialist skill without losing the original issue trail.

## Handoff pattern

1. Restate the idea in one sentence.
2. Name the target repo or specialist skill.
3. Say what should exist when the handoff is done.
4. Link the source issue.
5. Include `closes #N` only when the downstream issue should close the source.

## Copy-pasteable handoff

```markdown
Promoting idea #<N> into <target>.

Source: #<N>
Summary: <one sentence>
Why now: <one sentence>
Related links: <issue links or URLs>

Requested output:
- <deliverable 1>
- <deliverable 2>

If the target work should close the source issue, use `closes #<N>` in the
downstream issue or PR body.
```

## Specialist pairings

- `maker-engineering` for fabrication and shop ideas.
- `instrument-maker-v4` for instrument concepts and acoustics.
- `yoga-sequencer` for class and sequence ideas.
- `skills-meta` for skill ecosystem or routing ideas.

## Ownership note

Do not hard-code future repo ownership or visibility in the handoff. Keep the
target repo as an explicit input unless the user has already chosen it.
