# Maker Engineering Round 1 Eval

Date: 2026-05-08
Skill under test: `maker-engineering`
Evaluator: Codex

## Validation

| Check | Result | Notes |
| --- | --- | --- |
| Re-read `skill-creator` | pass | Re-read `/home/tony/.codex/skills/.system/skill-creator/SKILL.md` before making quality-gate changes. |
| `quick_validate.py` | pass | `python3 /home/tony/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/maker-engineering` returned `Skill is valid!`. |
| YAML/frontmatter parse | pass | Parsed `SKILL.md`, `agents/openai.yaml`, and `manifest.yaml`; confirmed validator-compatible frontmatter and manifest version entry. |
| OpenAI metadata | pass | Added generated `agents/openai.yaml`; `default_prompt` includes literal `$maker-engineering`. |
| Benchmark assertions | pass | Ran a lightweight local benchmark assertion script for hybrid routing, jig/fixture routing, and DoE routing terms. |

## Benchmark 1

Prompt fixture:

> I want to make a ceramic ocarina and need to figure out the slip-cast mold, tuning approach, and a small experiment for shrinkage.

Expected behavior:

- Keep `maker-engineering` in umbrella orchestration mode.
- Split the project into `instrument-maker-v4` for acoustic/tuning work and `makerspace` for mold/shop workflow.
- Keep the DoE scaffold in `maker-engineering`.
- Avoid producing a full instrument packet or fabrication packet directly.

Observed behavior:

- The routing decision tree includes this hybrid case directly.
- It calls for separate `instrument-maker-v4`, `makerspace`, and `maker-engineering` DoE outputs.
- The main skill tells the agent to produce one handoff per specialist and avoid full instrument packets, CNC toolpaths, BOMs, shop drawings, or acoustic calculations.

Result: pass

## Benchmark 2

Prompt fixture:

> Design a jig or fixture for repeated tone-hole drilling. Is this instrument-maker or makerspace?

Expected behavior:

- Route the shop implementation to `makerspace`.
- Preserve `instrument-maker-v4` only for tone-hole datum or acoustic requirements.
- Avoid collapsing jig design and acoustic design into one output.

Observed behavior:

- The frontmatter explicitly triggers on "design a jig or fixture" and "is this instrument-maker or makerspace?"
- The scope check routes jig, fixture, toolpath, machine setup, and shop-process-only work to `makerspace` when available.
- The routing reference gives a tone-hole drilling jig split with `instrument-maker-v4` owning datum requirements and `makerspace` owning jig/workholding/toolpath implementation.

Result: pass

## Benchmark 3

Prompt fixture:

> Set up an experiment comparing wall thickness and firing schedule against pitch error and cracking rate.

Expected behavior:

- Stay in standalone DoE mode.
- Produce factors, levels, response metrics, controls, trial matrix, logging fields, analysis plan, and stop condition.
- Route specialist calculations only if they dominate the task.

Observed behavior:

- The main skill states that DoE mode can stand alone.
- `references/doe-template.md` includes the required intake fields, factor table, trial matrix, measurement discipline, analysis plan, and stop condition.
- Specialist boundaries are explicit for acoustic target, fixture/toolpath, existing-object measurement, and early concept selection.

Result: pass

## Deviations Fixed During Quality Gate

- Removed unsupported `version` and `last-updated` keys from `SKILL.md` frontmatter so the bundled validator passes.
- Kept canonical versioning in `manifest.yaml`, where this repo tracks active skill versions.
- Added `agents/openai.yaml` using the bundled generator and verified it parses.
- Removed the per-skill `CHANGELOG.md`; `skill-creator` treats changelogs as auxiliary files, and the quality gate asked to fix creator deviations.
- Tightened the body from broad "when to use" prose into a post-trigger scope check, since trigger-critical wording belongs in frontmatter.

## Remaining Risks

- `makerspace` and `reverse-engineer` are planned specialists in this repo, so the skill currently routes to them "when available."
- The benchmarks are contract-level checks plus manual behavior review, not an automated model-in-the-loop harness.
- The repo's versioning docs prefer version fields in `SKILL.md`, but the current bundled `quick_validate.py` rejects them; this eval follows the validator for quality-gate pass/fail.
