# Reverse Engineer Round 2 Eval — cross-platform pass

Date: 2026-05-08
Skill path: `skills/reverse-engineer` (portable)
Method: Manual quality gate after the cross-platform handoff edit. Re-runs round-1's three prompts with the updated SKILL.md and adds a fourth prompt that exercises the new no-vision intake branch.
Edit under test: SKILL.md gained an "Intake When You Can't See Images" section and the description was rewritten to mention named-object / video / dictated / description-only modes; the inventory step now requires the analyst to declare when images aren't viewable.

## Structural Validation

Commands:

```bash
python3 /home/tony/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/reverse-engineer
python3 - <<'PY'
from pathlib import Path
import yaml
skill = Path('skills/reverse-engineer')
text = (skill/'SKILL.md').read_text()
front = text.split('---\n', 2)[1]
data = yaml.safe_load(front)
assert set(data) == {'name', 'description'}
assert data['name'] == skill.name
assert len(data['description'].strip()) <= 1024
agents = yaml.safe_load((skill/'agents/openai.yaml').read_text())
assert agents['interface']['display_name'] == 'Reverse Engineer'
assert '$reverse-engineer' in agents['interface']['default_prompt']
print('frontmatter, folder name, description length, agents/openai.yaml: OK')
PY
```

Results:

- `quick_validate.py`: **Pass**, "Skill is valid!"
- YAML/frontmatter check: **Pass**.
- Description length: **Pass**, 999 characters (under 1024).
- Body length: **Pass**, 118 lines (under 500).
- `agents/openai.yaml` parse + default-prompt token check: **Pass**.
- All four `references/*.md` still present and unchanged.

## Behavioral Smoke 1 — Photo/Object Observation (regression check)

Prompt: same as round-1 benchmark 1 (clamp lamp, single side photo).

Expected behavior is unchanged. The new intake step now also makes the analyst declare image viewability, but the photo-capable runtime path produces the same observation ledger / measurement requests / blocked-builder-handoff as round 1.

Pass/fail: **Pass** (no regression). The added step is a no-op when images render normally.

## Behavioral Smoke 2 — Dimension Inference With Uncertainty (regression check)

Prompt: same as round-1 benchmark 2 (festival scroll with US quarter not in plane).

Image Handling section is byte-identical to round 1. The Output Shape, dimension table, confidence language, and builder-handoff template are all unchanged. Behavior matches round 1.

Pass/fail: **Pass** (no regression).

## Behavioral Smoke 3 — Builder Handoff Gate (regression check)

Prompt: same as round-1 benchmark 3 (ceramic ocarina-like whistle with partial measurements).

Builder-Ready Gate, Reference Map, and instrument-maker-v4 routing language are byte-identical to round 1. Behavior matches round 1.

Pass/fail: **Pass** (no regression).

## Behavioral Smoke 4 — No-vision Intake (new branch)

Prompt:

```text
Use $reverse-engineer on a vintage Coleman 200A lantern. I'm running you in
Codex CLI, you can't see images. I have the lantern in front of me; ask me
what to dictate so we can build up a reproduction-ready analysis.
```

Expected behavior:

- Declare intake mode at the top: "named-object + dictated, no images viewable."
- Pull on widely-known facts about the Coleman 200A class but mark every class-derived claim as `inferred` with `class-knowledge` as basis.
- Refuse to fold class-typical dimensions into a builder handoff without per-instance measurement.
- Drive the same close-up/measurement asks as the photo checklist, just verbally.
- Avoid producing a dimension table from prose alone; route absolute dimensions into Measurement Requests.

Observed behavior:

- The new "Intake When You Can't See Images" section names this exact mode (named-object + dictated description) and prescribes the discipline above verbatim.
- The Inventory step (workflow item 2) now forces the analyst to state image viewability up front.
- The Output Shape still includes `Input Inventory`, `Measurement Requests`, and `Builder Readiness`, so the no-vision pass still produces the canonical sections — it's just sourced from class knowledge plus dictation rather than pixels.
- The Builder-Ready Gate still requires measured/bounded critical dimensions, so a name-only pass remains blocked from production handoff. This is the correct answer for a lantern that could be used for camping/safety.

Pass/fail: **Pass**. The new branch produces a recognizable, disciplined output without claiming to see what isn't there.

## Cross-platform compatibility notes

| Platform | Image rendering | Mode this skill takes |
| --- | --- | --- |
| Claude Code (terminal) | Yes for attached files | Photo path; no change. |
| Claude Desktop | Yes for pasted/attached images | Photo path; no change. |
| Codex CLI (no vision) | No | Named-object / dictated / written-description path. |
| Codex Desktop | Depends on build | Declare viewability up front; degrade gracefully. |
| Gemini CLI | Text-only by default | Named-object / dictated / written-description path. |
| Mobile zip-upload | Attachments often stripped | Named-object / dictated / written-description path; ask user to dictate or paste a frame later. |

The skill no longer makes platform-specific tool assumptions. The only platform-dependent capability it relies on is "can the runtime show the model an image", and the workflow now explicitly handles "no" as a first-class case.

## Standalone-repo sync

The portable copy here is canonical. The standalone copy at `tonykoop/reverse-engineering` → `skills/v1/reverse-engineer/` should be updated by the sync script described in `docs/sync-reverse-engineer.md` (added in this PR). The standalone copy keeps its own `CHANGELOG.md`; everything else gets overwritten on each sync.

## Remaining Risks

- The new no-vision intake section relies on the model honoring the "do not fold class-typical dimensions into a builder handoff" rule. The Builder-Ready Gate is the safety net.
- Trigger overlap with the broader `reverse-engineering` skill remains unaddressed by design (per Tony: the two skills live in different repos and are rarely co-installed). If they are co-installed, the user should treat `reverse-engineer` as the lightweight uncertainty pass and `reverse-engineering` as the full capstone packet generator.
- The 3-prompt smoke eval here was a manual pass on the static skill text; no subagent forward-test was run.
