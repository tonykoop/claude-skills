# Maker Engineering Round 1 Eval

Date: 2026-05-08
Skill under test: `maker-engineering`
Evaluator: Codex

## Validation

| Check | Result | Notes |
| --- | --- | --- |
| Re-read `skill-creator` | pass | Re-read `skill-creator/SKILL.md` before making quality-gate changes. |
| `quick_validate.py` | pass | `python3 <skill-creator>/scripts/quick_validate.py skills/maker-engineering` returned `Skill is valid!`. |
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

## Round 1.1 Addendum — Cross-Runtime Routing Pass (2026-05-08)

Followup to the cross-platform review handoff `02-maker-engineering.md`.

Changes:

- Switched the routed-to instrument specialist from the literal versioned name `instrument-maker-v4` to the canonical unversioned name `instrument-maker` across `SKILL.md`, `references/routing-decision-tree.md`, `references/specialist-registry.md`, and `references/doe-template.md`. The benchmarks above were authored against `instrument-maker-v4`; their intent is preserved (route to the instrument specialist), and the canonical name resolves to whichever compatible version is installed in the current runtime.
- Added a "Naming Convention" section to `references/specialist-registry.md` explaining when to add a minimum-version hint (e.g., "prefer v4+") instead of baking a version into the routed name.
- Added a runtime-agnostic-handoffs rule to `SKILL.md` and the registry's handoff prompt section: do not embed `$skill`, slash-command markers, or runtime-specific invocation syntax in the prompt body, since the user may paste the handoff into Claude Code, Claude Desktop, Codex CLI, Codex Desktop, Gemini CLI, or a mobile zip upload.

Cross-runtime routing smoke (3 prompts, contract-level):

1. "I want to make a ceramic ocarina and need to figure out the slip-cast mold, tuning approach, and a small experiment for shrinkage." → routing tree splits to `instrument-maker` (acoustics/tuning), `makerspace` (mold/shop), and stays in `maker-engineering` DoE for the shrinkage matrix. Pass.
2. "Design a jig or fixture for repeated tone-hole drilling. Is this instrument-maker or makerspace?" → routes shop implementation to `makerspace` and reserves `instrument-maker` for tone-hole datum requirements only. Pass.
3. "I'm on Claude Desktop and only have `instrument-maker` (no v4). Route a slip-cast ocarina build." → canonical name resolves correctly; the registry's naming convention covers the case and the handoff prompt template stays runtime-agnostic. Pass.

Validator: `python3 <skill-creator>/scripts/quick_validate.py skills/maker-engineering` returns `Skill is valid!` after the rename.
