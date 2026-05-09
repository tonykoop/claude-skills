# claude-skills

Canonical source for Tony Koop's agentic skills, routines, hooks, commands, and
cross-runtime orchestration patterns.

This repo started as `agent-orchestration`, the WRFCoin sprint infrastructure
repo. It is now being evolved into a broader skill ecosystem repo: still grounded
in the tmux/persona sprint work that proved the pattern, but organized so skills
can be versioned, packaged, audited, installed across devices, and eventually
released publicly.

## What Lives Here

- `claude/` - Claude Code skills, commands, hooks, and routines.
- `codex/` - Codex skills and runtime-specific workflow ports.
- `gemini/` - Gemini CLI/runtime parity work, when added.
- `skills/` - Portable user skills that are not tied to one runtime.
- `docs/` - Architecture, versioning, controls, benchmarks, and release notes.
- `manifest.yaml` - Canonical version registry for every tracked skill.

## Operating Model

The repository treats a skill as a versioned product, not a pasted prompt. Every
shippable skill should have:

- a `SKILL.md` with structured frontmatter;
- a per-skill changelog;
- a manifest entry;
- a tagged release before zipping or upload;
- a lightweight validation or benchmark story.

Runtime-specific pieces stay under their runtime folders. Shared skills that
should work across Claude Desktop, Claude Code, Codex, Codex Desktop, Gemini CLI,
and future runtimes live under `skills/`.

## Versioning

Every `SKILL.md` should include:

```yaml
---
name: skill-name
version: 1.0.0
last-updated: 2026-05-08
description: ...
---
```

Each skill is independently versioned with semver. Tags are namespaced:

```text
instrument-maker-v4/v4.3.1
tmux-v2/v2.0.0
idea-incubator/v1.0.0
```

See [docs/skill-versioning.md](docs/skill-versioning.md).

## Controls

The next phase of this repo is about controls: trigger accuracy, routing,
runtime adapters, issue-backed handoffs, routine support, and version drift
detection. The guiding principle is simple: skills should be easy to install and
portable, but hard to silently drift.

See [docs/skill-controls.md](docs/skill-controls.md).

## Provenance

The first production use case was WRFCoin: a multi-repo blockchain sprint system
using named tmux personas, handoff files, GitHub issues, PR review gates, and
Claude/Codex/Gemini runtime parity. That history remains in `claude/`, `codex/`,
and the architecture docs because it is valuable field evidence.

The current expansion generalizes that system for musical instrument design,
maker workflows, yoga/class-planning skills, idea incubation, and public skill
release.

## Status

Private-first while the repo is being scrubbed, reorganized, and benchmarked for
public release.
