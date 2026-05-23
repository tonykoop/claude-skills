# Reverse Engineer Round 1 Eval

Date: 2026-05-08
Skill path: `skills/v1/reverse-engineer`
Method: Manual quality gate using the skill instructions and bundled references, plus structural validators. Timing is approximate wall-clock time for each manual behavioral pass.

## Skill-Creator Compliance Check

Reread: `skill-creator/SKILL.md`

Pass:
- Skill folder name matches skill name: `reverse-engineer`.
- `SKILL.md` has valid YAML frontmatter with only `name` and `description`.
- Frontmatter description carries the trigger/use-context text instead of relying on a body-only "when to use" section.
- Body is concise at 102 lines, under the 500-line guidance.
- Detailed reusable material is split into one-level `references/` files.
- No scripts or assets were added because the workflow is judgment/template driven, not deterministic code.
- Added recommended `agents/openai.yaml` using the bundled generator.

Exception:
- `CHANGELOG.md` remains even though the general skill-creator guidance discourages changelogs inside skills. It is retained because GitHub issue #17 and Dan's handoff explicitly required a changelog stub.

Fix made during gate:
- Moved `version: 1.0.0` out of YAML frontmatter and into the body/changelog because skill-creator says frontmatter should contain only `name` and `description`.

## Structural Validation

Commands run:

```bash
python3 <skill-creator>/scripts/quick_validate.py skills/v1/reverse-engineer
python3 - <<'PY'
from pathlib import Path
import yaml
skill=Path('skills/v1/reverse-engineer')
text=(skill/'SKILL.md').read_text()
front=text.split('---\n',2)[1]
data=yaml.safe_load(front)
assert set(data)=={'name','description'}, data
assert data['name']==skill.name
assert len(data['description'].strip()) <= 1024
agents=yaml.safe_load((skill/'agents/openai.yaml').read_text())
assert agents['interface']['display_name']=='Reverse Engineer'
assert '$reverse-engineer' in agents['interface']['default_prompt']
print('frontmatter, folder name, description length, and agents/openai.yaml OK')
PY
```

Results:
- `quick_validate.py`: Pass, `Skill is valid!`
- YAML/frontmatter check: Pass.
- Folder/name match: Pass.
- Description length: Pass, 735 characters.
- `agents/openai.yaml` parse/default prompt check: Pass.
- Reference files present: Pass.

## Behavioral Benchmark 1: Photo/Object Observation

Prompt:
```text
Use $reverse-engineer on this single side photo of a vintage clamp lamp. I can see a round shade, a bent gooseneck, a spring clamp base, and one screw at the hinge. Tell me how it is constructed and what photos or measurements you need next.
```

Expected behavior:
- Select photo/object observation mode with possible mechanism/material inference.
- Separate visible facts from inferred construction.
- Avoid claiming hidden hinge geometry, spring rate, material, thread size, or exact dimensions.
- Ask for scale reference, orthogonal views, close-ups of hinge/clamp/screw, and motion video if mechanism matters.
- Mark builder readiness as blocked or partial, not builder-ready.

Observed behavior:
- The skill's normal output sections force `Input Inventory`, `Observed Facts`, `Inferred Facts`, `Unknowns`, `Material and Process Notes`, `Measurement Requests`, and `Builder Readiness`.
- `Image Handling` explicitly says to report viewpoint limits and occlusions separately, and to avoid absolute dimensions without a same-plane scale reference.
- The measurement checklist includes whole-object and critical-interface photos, fastener/joint close-ups, and mechanism travel video.
- Builder-ready gate prevents handoff because critical dimensions, interfaces, and materials are not documented from one side photo.

Pass/fail: Pass.
Timing: ~2 minutes.

## Behavioral Benchmark 2: Dimension Inference With Uncertainty

Prompt:
```text
Use $reverse-engineer to extract dimensions from one angled photo of a small wooden festival scroll lying next to a US quarter. The quarter is near the left rod but slightly closer to the camera than the paper. Estimate rod diameter, paper width, and finial length, and tell me what I can safely build from this.
```

Expected behavior:
- Select dimension inference mode.
- Use ranges or proportions, not exact dimensions, because the scale reference is not in the same plane.
- Mark any absolute dimensions as low confidence unless directly measured.
- Identify perspective error as a risk.
- Ask for same-plane ruler/coin, centered front view, side view, and close-up of paper-to-rod attachment.
- Refuse or block full builder handoff while allowing a rough concept sketch/prototype envelope.

Observed behavior:
- `Image Handling` directly covers this case: no same-plane scale reference means estimate only proportions, ratios, counts, and qualitative geometry.
- `confidence-language.md` says image-derived dimensions should be ranges unless a reliable scale reference exists and should state plane/perspective error.
- `observation-template.md` includes separate `Estimated range`, `Measured value`, `Source`, `Confidence`, and `Builder critical?` columns.
- `builder-handoff-template.md` supports `provisional` and `blocked` status, so the safe output is a provisional concept envelope or blocked production handoff.

Pass/fail: Pass.
Timing: ~3 minutes.

## Behavioral Benchmark 3: Builder Handoff Gate

Prompt:
```text
Use $reverse-engineer on this described ocarina-like ceramic whistle. I measured overall length 145 mm, width 72 mm, mouthpiece slot 1.8 mm, and four tone holes at 8, 9, 10, and 11 mm. I do not know the internal chamber volume, wall thickness, firing shrinkage, or tuning. Please hand this to instrument-maker-v4 to build a playable version.
```

Expected behavior:
- Select handoff-to-builder plus instrument/acoustic artifact handling.
- Treat supplied dimensions as measured.
- Mark chamber volume, wall thickness, shrinkage, and tuning as builder-critical unknowns.
- Do not emit a builder-ready instrument-maker-v4 handoff.
- Emit blocked or provisional handoff with minimum measurements/tests: chamber volume, wall thickness, clay body/shrink rate, voicing geometry, pitch/tuning data, photos/sections.

Observed behavior:
- The workflow routes instruments to `instrument-maker-v4` only "after critical acoustic and dimensional data is validated."
- Builder-ready gate requires critical dimensions, material/process, acoustic/contact surfaces, and unknowns to be non-critical or test-assigned.
- Measurement checklist has an `Instruments and Acoustic Artifacts` section requesting cavity dimensions, material thickness, tuning references, reed/air path/openings, and environmental notes.
- The blocked handoff template gives the exact shape needed: reason, builder-critical unknowns, minimum measurements/tests, and what can be done now.

Pass/fail: Pass.
Timing: ~3 minutes.

## Remaining Risks

- The skill depends on the model following references rather than deterministic scripts; this is appropriate for analysis but still requires discipline from the caller.
- No independent subagent forward-test was run in this gate because this pass stayed within the local validation request and avoided extra parallel agents.
- The existing broader `reverse-engineering` skill could overlap trigger space with `reverse-engineer`; routing should prefer `reverse-engineer` for compact uncertainty-first analysis and `reverse-engineering` for full capstone packet generation.
- `CHANGELOG.md` is a deliberate issue-specific exception to the generic skill-creator guidance.
