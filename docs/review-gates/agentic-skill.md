# Agentic Skill Review Gate

Use this gate for PRs that add or change a skill, runtime adapter, command,
hook, benchmark, or skill-routing policy. The reviewer should be able to decide
merge/readiness from evidence in the PR body without reconstructing the whole
handoff.

## Required Evidence Contract

Every agentic-skill PR must include:

```markdown
## Review Evidence

Type: skill | runtime-adapter | command | hook | benchmark | docs | mixed

Changed behavior:
- ...

Validation run:
- ...

Known gaps:
- ...

Reviewer should check:
- ...

Do not merge until:
- ...
```

`Known gaps` can say `none`, but it must not be omitted. `Do not merge until`
is the agent's own merge bar; reviewers may add stricter requirements.

## Stage 1 - Static Gate

- `SKILL.md` frontmatter has the canonical `name` and a trigger-oriented
  `description`.
- The description names the target user intent and includes a `Do not use for`
  or `Prefer <skill>` clause when adjacent skills exist.
- Scope boundaries are explicit: what the skill owns, hands off, or refuses.
- Long reference material lives in `references/`, not the activation-critical
  `SKILL.md` body.
- Scripts, assets, evals, and references named by the skill exist in the PR.
- `manifest.yaml`, per-skill changelog, and docs agree on the current status.
- Private paths, credentials, personal contact data, and repo-specific
  assumptions are absent unless intentionally labeled as project-specific.

## Stage 2 - Behavior Gate

The PR should include or reference 3-5 fixture prompts:

- should trigger the skill;
- should not trigger the skill;
- ambiguous request that should clarify or hand off;
- conflict with an adjacent skill or runtime adapter;
- safety, refusal, or deprecation boundary where relevant.

For each prompt, record the expected routing or observable output. For
file-producing skills, include before/after fixture artifacts or a small checked
sample showing the generated shape.

## Stage 3 - Runtime Gate

- The PR states which runtime was exercised: Claude Code/Desktop, Codex
  CLI/Desktop, Gemini, tmux, or another adapter.
- Runtime-specific behavior is marked as either parity, intentional divergence,
  or untested.
- Hooks, permissions, settings, and external commands are validated when the
  skill depends on them.
- Desktop/bridge-backed runtimes are labeled as deterministic, prompt-staging,
  or observe-only. Do not imply deterministic control where none exists.

## Stage 4 - Regression Gate

- New trigger language does not shadow a narrower specialist skill.
- New routing does not duplicate an existing umbrella/specialist boundary.
- Deprecated or archived skills keep their migration path.
- Public examples remain portable and do not reintroduce private assumptions.
- Benchmark or smoke coverage is added for any previously fragile behavior.

## Merge Decisions

| Decision | Use when |
| --- | --- |
| Merge | All required evidence is present and the changed behavior is verified. |
| Hold draft | The direction is right, but manager acceptance, live smoke, or policy alignment is still needed. |
| Changes requested | Evidence is missing, stale-base diffs pollute review, behavior is untested, or the change introduces trigger/routing ambiguity. |

## Reviewer Short Form

Copy this into a PR comment when a full review is not necessary:

```markdown
## Agentic skill gate

- Static gate:
- Behavior gate:
- Runtime gate:
- Regression gate:
- Decision:
```
