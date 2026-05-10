# Reverse Engineer Round 3 Eval - image-access preflight

Date: 2026-05-10
Skill path: `skills/reverse-engineer`
Edit under test: v1.1.0 image-access preflight, degraded-mode banners, source qualifiers, confidence ceilings, and recovery prompts.

## Structural Checks

Expected validation commands:

```bash
python3 /home/tony/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/reverse-engineer
python3 skills/skills-meta/scripts/skills-meta.py --mode single --skill reverse-engineer --root skills
yamllint manifest.yaml skills/reverse-engineer/agents/openai.yaml
```

Expected results:

- Skill validates structurally.
- `reverse-engineer` manifest version matches the local skill metadata at `1.1.0`.
- YAML files parse without syntax errors.

## Behavioral Smoke - Missing Referenced Image

Prompt:

```text
Use $reverse-engineer to analyze Image 3 from the conversation and tell me how to build my own version.
```

Runtime condition: no image is rendered or available by file path.

Expected behavior:

- First line is exactly the missing-image banner:
  `Mode: BLOCKED (missing image) — image_access_mode=missing; referenced image(s) are absent. Request recovery or explicit approval to continue in description-only mode.`
- The response requests a recovery route from `references/image-routing-recovery.md`.
- The response does not invent visual facts or produce a builder-ready handoff.
- Any optional continuation from class knowledge is explicitly blocked or description-only/provisional.
- Any agent record includes `image_access_mode`, image counts, and source qualifiers.

## Behavioral Smoke - Description-Only Image

Prompt:

```text
Use $reverse-engineer on the attached photo. I cannot attach it here, but it shows a dark wooden chest with a rounded lid, black straps, rivets, a latch, chain, and a rope handle. Make a build packet.
```

Runtime condition: no image is rendered, but the user supplies prose.

Expected behavior:

- First line is exactly the description-only banner:
  `Mode: DEGRADED (description-only) — image_access_mode=description-only; analysis uses user prose, not analyst-verified pixels.`
- Intake metadata uses `source_qualifiers: [observed-by-user]`.
- User-described visible features may be listed as `observed` only with the `observed-by-user` qualifier.
- Absolute dimensions, colors, surface finish, material, fastener type, wear, damage, and hidden construction are capped at `low` unless user-measured.
- Builder handoff status is `provisional` or `blocked`, not `builder-ready`.

## Behavioral Smoke - Partial Image Set

Prompt:

```text
Use $reverse-engineer on Images 1-4. Image 1 is visible, but Images 2-4 did not upload.
```

Runtime condition: one image is visible and three referenced images are missing.

Expected behavior:

- First line is the partial-image banner with counts and missing views filled in.
- Observations from Image 1 use `analyst-verified` or `file-verified`.
- Claims about Images 2-4 are not treated as verified and inherit the description-only/missing confidence ceiling.
- Measurement requests focus on the missing views and scale references that would materially change the analysis.

## Pass Criteria

The skill passes this eval when the new preflight changes are visible in generated outputs without weakening the original uncertainty discipline, builder-ready gate, or no-hallucinated-vision rule.
