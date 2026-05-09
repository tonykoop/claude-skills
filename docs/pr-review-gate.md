# PR Review Gate

Sprint-manager checklist for merging PRs and closing issues in the claude-skills ecosystem.
Apply the section that matches the PR type. All PRs must pass the **Universal** section first.

---

## Universal (all PR types)

- [ ] PR targets the correct base branch (not `main` unless it is a release merge).
- [ ] PR title is ≤ 72 characters and describes the change, not the ticket.
- [ ] PR body links the issue it closes (`Closes #N`).
- [ ] PR is small: a single coherent unit of change. If it touches ≥ 3 unrelated areas, ask to split.
- [ ] CI / GitHub Actions checks have run and are green (or failures are explained in the PR body).
- [ ] No merge conflicts with base branch.
- [ ] Author is not merging their own PR without review (sprint manager counts as reviewer).

---

## Documentation-only PRs

*Applies when the diff contains only `*.md`, `*.txt`, or other non-executable files.*

- [ ] Prose is accurate against current code/manifest state (no stale file paths or version numbers).
- [ ] No private paths, credentials, or WRFCoin-only assumptions exposed.
- [ ] If a checklist or procedure was updated, the change does not contradict `skill-versioning.md` or `skill-controls.md`.
- [ ] CHANGELOG.md updated with the date and a one-line summary.

---

## Script PRs

*Applies when the diff includes `.py`, `.sh`, `.js`, or similar executable files.*

- [ ] Script has a usage comment or `--help` output.
- [ ] No hard-coded private paths; paths are parameterized or read from env/config.
- [ ] If the script references `manifest.yaml`, it handles missing keys gracefully.
- [ ] Script was smoke-tested locally; output is shown in the PR body or a linked artifact.
- [ ] CHANGELOG.md updated.
- [ ] `manifest.yaml` updated if the script is a bundled skill resource.

---

## Skill-content PRs

*Applies when the diff includes a `SKILL.md` or any file under `skills/`, `claude/skills/`, `codex/skills/`, or `gemini/skills/`.*

### Frontmatter and versioning

- [ ] `name` and `description` fields are present and trigger-accurate.
- [ ] Version is bumped in `manifest.yaml` following semver:
  - patch — trigger wording, clarifications, small fixes
  - minor — new modes, new runtime support, additive resources
  - major — breaking schema, output, or workflow changes
- [ ] `last_updated` in `manifest.yaml` reflects today's date.
- [ ] A per-skill changelog entry is added (date + summary).
- [ ] CHANGELOG.md has a repo-level entry.

### Portability review

- [ ] Runtime-specific logic lives under the correct runtime directory (`claude/`, `codex/`, `gemini/`).
- [ ] Shared/portable logic lives under `skills/`.
- [ ] Any runtime assumptions are explicitly labeled (e.g., "Claude Code only", "requires tmux").
- [ ] Bundled scripts, templates, or resources referenced in `SKILL.md` are present in the PR.
- [ ] Example prompts do not contain private credentials, repo names, or environment-specific paths.

### Routing (umbrella skills only)

- [ ] Specialist names match the canonical names in `manifest.yaml`.
- [ ] Routing conditions are mutually exclusive (no ambiguous trigger overlap with sibling skills).
- [ ] Fallback behavior is documented if no specialist matches.

### Smoke test

- [ ] At least one trigger prompt is listed in the PR body and the expected routing or output is described.
- [ ] For high-risk or fragile skills, a benchmark prompt set exists in `docs/benchmarking.md` or linked.

---

## Issue Closure Checklist

Before closing an issue, confirm:

- [ ] The linked PR is merged (not just opened).
- [ ] The issue acceptance criteria are met — re-read the original issue, not just the PR title.
- [ ] If the issue was "add X to manifest", verify `manifest.yaml` actually contains X.
- [ ] If the issue was a bug, a regression note is added to `docs/benchmarking.md` or a smoke test covers it.
- [ ] If the issue spawned follow-on work, those follow-on issues are filed before closing this one.
- [ ] The issue milestone or sprint label reflects the correct round.

---

## Portability Quick-Reference

| Location | When to use |
|---|---|
| `skills/<name>/` | Portable — works on Claude, Codex, Gemini, mobile zip |
| `claude/skills/<name>/` | Claude Code / Claude Desktop only |
| `codex/skills/<name>/` | Codex CLI / Codex Desktop only |
| `gemini/skills/<name>/` | Gemini CLI only |

A PR that moves a skill from a runtime directory to `skills/` must pass the full portability review above and update `manifest.yaml` `runtime` field to `portable` or `shared`.

---

## Instrument Packet Work

This gate is designed to be compatible with PRs from the **instrument-maker** and **maker-engineering** specialist pipeline. When reviewing instrument packet PRs:

- Treat each instrument packet (BOM, CAD, cut plan, SKILL.md) as a **skill-content PR** plus a **script PR** if CNC or export scripts are included.
- Portability matters: instrument packets are intended to run on Claude Desktop, Codex, and future mobile runtimes — do not let runtime-specific paths land in `skills/maker-engineering` or sub-specialists.
- Routing review is required: verify that `maker-engineering` umbrella trigger conditions correctly hand off to the new instrument specialist without overlapping existing specialists.
- Smoke test for instrument PRs: at minimum, one prompt like *"design a pentatonic PVC flute"* should route through `maker-engineering` to the correct specialist without falling through to a catch-all.
