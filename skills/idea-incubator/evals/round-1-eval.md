# Idea Incubator Round 1 Eval

Date: 2026-05-08

## Validation Summary

- `quick_validate.py`: pass
- YAML parse check: pass
- Frontmatter check: pass
- `agents/openai.yaml` length/spec check: pass

## Notes on skill-creator alignment

- I re-read `/home/tony/.codex/skills/.system/skill-creator/SKILL.md` before this pass.
- The skill now follows the validator-friendly frontmatter shape used by the current skill-creator toolchain: `name` and `description` only.
- The repo-required `CHANGELOG.md` remains present because the repository release workflow expects it.

## Behavioral Benchmark

### 1) Capture one idea

**Prompt**

> new idea: make a tiny CLI that turns voice memos into issue drafts for the ideas inbox

**Expected behavior**

- Produce one concise GitHub issue draft.
- Keep it mobile-friendly.
- Include capture context, why it matters, next step, and suggested labels.
- Do not invent a repository target or auto-close anything.

**Observed behavior**

- Produced a single issue draft with a short title.
- Included capture/source context, a concise summary, why it matters, a next step, and labels.
- Kept the output copy-pasteable and avoided hard-coding repo ownership.

**Pass/fail**

- Pass

**Timing**

- Not formally measured; drafted in a single pass.

### 2) Intake a Telegram-style batch

**Prompt**

> Telegram dump:
> - maybe a daily photo habit tracker
> - can we use saved messages for inbox?
> - maybe make the running route generator
> - check if yoga sequencing should live with idea-incubator?

**Expected behavior**

- Split clearly separate ideas into separate candidates.
- Preserve ambiguity when a split is uncertain.
- Surface related ideas instead of collapsing them.
- Keep the result readable on mobile.

**Observed behavior**

- Split the batch into separate candidate ideas.
- Preserved the uncertain yoga-sequencing question as a related/ambiguous item rather than guessing.
- Surfaced the saved-messages capture idea as a routing/inbox question.
- Kept the output compact and copy-pasteable.

**Pass/fail**

- Pass

**Timing**

- Not formally measured; drafted in a single pass.

### 3) Promote an idea to a specialist handoff

**Prompt**

> promote idea #18: turn the instrument bore calculator into a maintained helper in instrument-maker-v4

**Expected behavior**

- Produce a copy-pasteable promotion handoff.
- Name the target specialist skill or repo.
- Restate the idea in one sentence.
- Include source issue linkage.
- Only include `closes #18` if the user explicitly wants the downstream work to close the source.

**Observed behavior**

- Produced a promotion handoff referencing the source idea and target specialist area.
- Included summary, why-now context, and requested outputs.
- Omitted `closes #18` because it was not explicitly requested.

**Pass/fail**

- Pass

**Timing**

- Not formally measured; drafted in a single pass.

## Remaining Risks

- Repo ownership and visibility are intentionally not hard-coded, so some promotion prompts still need Tony to name the target repo.
- The label bootstrap helper depends on authenticated `gh` access.
- `CHANGELOG.md` is a deliberate repo-level exception to the minimal skill-creator guidance.
