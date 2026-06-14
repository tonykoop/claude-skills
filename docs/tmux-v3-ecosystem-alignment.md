# tmux-v3 Ecosystem Alignment

Issue: tonykoop/claude-skills#7

This note scopes how future `tmux-v3` work should align with the canonical
skill ecosystem controls while `tmux-sprint` remains the active packaged skill
at version `2.4.1`.

## Retrieval Gate

- `qmd status` succeeded: 2821 indexed markdown files, 13904 embedded vectors,
  15 collections, last updated about 18 hours before this pass.
- `qmd search` in `sprint-docs` for this lane returned no direct hits.
- `qmd query` was attempted for the lane topic, but the Bun-backed local qmd
  runtime crashed after falling back from Vulkan/no-GPU, so this document uses
  live repo docs, the Round 1 checkpoint draft, and GitHub issue metadata.

## Current State

- `manifest.yaml` lists `tmux-sprint` as `canonical_version: 2.4.1`,
  `status: active`, with source at `plugins/coding/skills/tmux-sprint`.
- `plugins/coding/skills/tmux-sprint/SKILL.md` already has top-level
  `version: 2.4.1` and `last-updated: 2026-06-13` frontmatter.
- The packaged `tmux-sprint` skill is still the production sprint driver:
  dispatch, liveness probing, codex-session revival, TwinGrid, Partner Peek,
  label-aware batching, and smart model-picker routing.
- Do not rename, deprecate, or bump the current `tmux-sprint` package until
  v3 has a real implementation path and clean benchmark evidence.

## Roadmap Cross-Links

The v3 implementation roadmap lives in `tonykoop/tmux-sprint`, not in this
repo. Keep this document as an ecosystem bridge and avoid copying detailed
implementation state into multiple sources of truth.

| Roadmap issue | State | Ecosystem relevance |
| --- | --- | --- |
| [tonykoop/tmux-sprint#1](https://github.com/tonykoop/tmux-sprint/issues/1) | open | Project-neutral routine-driven v3 roadmap |
| [tonykoop/tmux-sprint#2](https://github.com/tonykoop/tmux-sprint/issues/2) | closed | Project-neutral init and doctor onboarding |
| [tonykoop/tmux-sprint#3](https://github.com/tonykoop/tmux-sprint/issues/3) | closed | Saved sprint routines and reusable playbooks |
| [tonykoop/tmux-sprint#4](https://github.com/tonykoop/tmux-sprint/issues/4) | closed | Transactional dispatch and pane state machine |
| [tonykoop/tmux-sprint#5](https://github.com/tonykoop/tmux-sprint/issues/5) | closed | Runtime adapter layer for Codex, Claude, Gemini, and desktop counterparts |
| [tonykoop/tmux-sprint#6](https://github.com/tonykoop/tmux-sprint/issues/6) | open | Benchmark suite, watch-points, and run-log validator |
| [tonykoop/tmux-sprint#7](https://github.com/tonykoop/tmux-sprint/issues/7) | open | Public release readiness and packaging |
| [tonykoop/tmux-sprint#8](https://github.com/tonykoop/tmux-sprint/issues/8) | open | Versioned skill structure, frozen baselines, and release notes |
| [tonykoop/tmux-sprint#9](https://github.com/tonykoop/tmux-sprint/issues/9) | closed | Plugin, connector, and automation extension points |
| [tonykoop/tmux-sprint#23](https://github.com/tonykoop/tmux-sprint/issues/23) | closed | Structured run metrics and pane telemetry |
| [tonykoop/tmux-sprint#24](https://github.com/tonykoop/tmux-sprint/issues/24) | open | Smart model routing and lane classification |
| [tonykoop/tmux-sprint#25](https://github.com/tonykoop/tmux-sprint/issues/25) | closed | Smart batching planner for multi-agent sprint lanes |
| [tonykoop/tmux-sprint#26](https://github.com/tonykoop/tmux-sprint/issues/26) | closed | Persona sub-agent and Claude agent-team support |
| [tonykoop/tmux-sprint#27](https://github.com/tonykoop/tmux-sprint/issues/27) | open | Usage-window and context-budget controller |

## Alignment Contract

`tmux-v3` alignment means the future v3 implementation must fit the existing
skill-control surfaces instead of introducing a parallel governance model.

- Versioning: v2 remains installable and benchmarkable while v3 develops
  beside it. The manifest should not mark v2 deprecated until v3 can install,
  launch, dispatch, and validate a reference routine. Use top-level
  `version` and `last-updated` frontmatter for any shipped v3 skill surface,
  and keep `manifest.yaml` as the canonical registry.
- Activation: v3 should keep the canonical user-facing skill name
  `tmux-sprint` unless a temporary development alias is explicitly marked as
  non-production. Any temporary alias must include a clear `Prefer
  tmux-sprint` or `development only` routing note.
- Runtime adapters: Codex CLI, Claude Code, Gemini CLI, and desktop/bridge
  surfaces must declare capabilities honestly: launch control, prompt staging,
  submit acknowledgement, stop notification, recovery, and limitations.
- Routines: saved sprint routines are the replayable unit. A routine must
  declare worktrees, agents, runtimes, dispatch mode, stop conditions, success
  checks, logging, and whether visible planning is required before edits.
- Hooks and automations: hooks may observe, gate, or notify, but deterministic
  control must stay in the adapter/driver layer. A hook that cannot verify
  prompt submission or stop acknowledgement must be labeled observe-only.
- Plugins and connectors: plugin, connector, GitHub, Slack, Drive, Calendar,
  or browser-backed actions should enter through explicit routine steps with
  named permissions and failure behavior, not hidden side effects.
- Review gates: changes to skills, adapters, hooks, commands, or benchmark
  fixtures must use the agentic-skill review gate and PR evidence contract.
- Public release: defaults must be project-neutral. Personal paths, private
  repo names, and WRFCoin/instrument-specific details are acceptable only when
  labeled as illustrative examples or preserved as private provenance.

## Required Ecosystem References

Any v3 work in this repo should link back to:

- [docs/skill-controls.md](skill-controls.md)
- [docs/skill-versioning.md](skill-versioning.md)
- [docs/public-release-checklist.md](public-release-checklist.md)
- [docs/review-gates/agentic-skill.md](review-gates/agentic-skill.md)
- [docs/review-gates/pr-evidence-contract.md](review-gates/pr-evidence-contract.md)

## Runtime Adapter Expectations

Each adapter should publish a small manifest or fixture that answers:

| Field | Required answer |
| --- | --- |
| Runtime id | Stable id such as `codex-cli`, `claude-code`, `gemini-cli`, `claude-desktop`, or `codex-desktop` |
| Launch mode | Can launch, can attach, prompt-staging only, or observe-only |
| Prompt submission evidence | How the adapter knows the prompt was accepted |
| Working-state probe | How the adapter distinguishes idle, working, blocked, dead, and update-required states |
| Stop signal | Supported stop command or explicit unsupported state |
| Recovery path | Same-pane resume, new-pane relaunch, or manager handoff |
| Permission needs | Shell, tmux, network, connector, browser, filesystem, or none |
| Known divergence | Any runtime behavior that is intentionally not portable |

The first validator should fail early on unknown runtime ids, observe-only
adapters used for full dispatch, missing stop signals, and missing
prompt-submission evidence.

## Routine Fixture Expectations

Saved sprint routines should be concrete enough to replay and strict enough to
review:

- worktree roots and branch policy;
- agent roster and pane targets;
- runtime adapter per pane;
- assignment-file or prompt source;
- dispatch ordering and batching policy;
- label preservation and issue-routing notes;
- stop conditions and escalation rules;
- run-log and evidence paths;
- required visible planning or no-planning edit mode;
- validation commands and expected artifacts.

The first routine validator should check worktree isolation, assignment-file
dispatch requirements, label preservation, model-routing notes, stop
conditions, and run-log paths.

## Benchmark Cases

Add benchmark cases before any release-candidate label:

1. Dispatch reliability: assignment file reaches every target pane or fails
   with a named pane and reason.
2. Prompt submission: adapter records evidence that the runtime accepted the
   submitted prompt.
3. Pane recovery: dead, exited, update-required, and budget-exhausted panes
   follow deterministic recovery or manager handoff.
4. Stop hooks: stop notification fires once, names the pane/run, and does not
   imply control when the adapter can only observe.
5. Generic-project onboarding: a non-WRFCoin, non-instrument sample project can
   init, doctor, dispatch, and validate without private path assumptions.

## Acceptance Checks

- `manifest.yaml` still reports `tmux-sprint` as active `2.4.1`.
- `plugins/coding/skills/tmux-sprint/SKILL.md` still describes current
  production behavior without v3-only promises.
- No install roots, tags, or package names change until v3 passes a clean
  install/doctor/launch benchmark on a generic sample project.
- PRs touching v3 surfaces include the review evidence contract and link to
  the relevant `tonykoop/tmux-sprint` roadmap issue.
