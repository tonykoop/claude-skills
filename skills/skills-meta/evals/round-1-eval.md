# skills-meta Round 1 Eval

Date: 2026-05-08

## Scope

Validate the `skills-meta` skill package against skill-creator guidance, then
exercise three realistic prompts against the bundled helper.

## Structural Validation

| Check | Result | Notes |
|-------|--------|-------|
| `quick_validate.py` | pass | `quick_validate.py` accepts the skill now that `SKILL.md` frontmatter only includes `name` and `description`. Runtime: `0.035s`. |
| YAML/frontmatter parse | pass | `SKILL.md` frontmatter parsed cleanly; `name` and `description` are present. Canonical version lives in `manifest.yaml`. |
| `agents/openai.yaml` parse | pass | `interface.display_name`, `interface.short_description`, `interface.default_prompt`, and `policy.allow_implicit_invocation` parsed cleanly. |
| manifest presence | pass | `manifest.yaml` contains an active `skills-meta` entry with `runtime: portable`. |

## Behavioral Benchmark

| Prompt | Expected behavior | Observed behavior | Result | Timing |
|--------|-------------------|-------------------|--------|--------|
| `inventory all skills` | List installed skills, show versions, flag drift, and summarize counts in a phone-friendly format. | Reported 12 scanned skills, 12 drifted, and listed active skills plus manifest-missing locals. `skills-meta` itself is now drifted because its frontmatter intentionally omits `version` and `last-updated`. | pass | `0.279s` |
| `single-skill version check` | Focus on one skill and show installed version vs canonical version with drift notes. | Reported `gh-fix-ci` as `vmissing`, canonical `v1.0.0`, runtime `codex`, and issues `missing-version` and `missing-last-updated`. | pass | `0.255s` |
| `frontmatter-fix suggestion` | Print a copy-pasteable frontmatter block only, without rewriting files. | Returned a suggested frontmatter block for `skills-meta` with `name`, `version`, `last-updated`, and `description`. This is a suggestion only; the actual skill frontmatter remains `name` + `description`. | pass | `0.256s` |

## Skill-Creator Compliance

| Guidance | Status | Notes |
|----------|--------|-------|
| Keep the skill lean | pass | Core logic lives in `scripts/skills-meta.py`; reference files hold schema, examples, and runtime roots. |
| Avoid extraneous docs | pass | No `README.md` or `CHANGELOG.md` was added under the skill. |
| Use bundled references for detail | pass | Detailed schema and output examples are split into references. |
| Validate agents metadata on update | pass | Added `agents/openai.yaml` with UI metadata and default prompt. |
| Follow current skill-creator frontmatter rules | pass | `SKILL.md` now uses only `name` and `description`; canonical version is tracked in `manifest.yaml`. |

## Remaining Risks

- The helper intentionally treats non-ISO or unparseable dates as drift, which is safe but may surface false positives for legacy skills.
- The inventory output reflects existing repo drift: all scanned skills currently lack version frontmatter, including `skills-meta` by design.
- `skills-meta` currently suggests fixes but does not apply them, by design.
