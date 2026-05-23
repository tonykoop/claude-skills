# Idea Incubator Round 2 Eval

Date: 2026-05-08
Skill version: 1.1.0 (cross-platform pass)

## Validation Summary

- `quick_validate.py` (`/home/tony/.codex/skills/.system/skill-creator/scripts/quick_validate.py`): pass
- `agents/openai.yaml` parses as YAML: pass
- `manifest.yaml` parses as YAML: pass
- `bash -n scripts/bootstrap-labels.sh`: pass
- `python3 -m py_compile scripts/bootstrap_labels.py`: pass
- `bootstrap_labels.py owner/nonexistent` exits non-zero with a clean
  `gh label create failed for 'capture' in owner/nonexistent` message
  (no Python traceback).

## What changed since round 1

- Triggers normalized: dropped trailing `?` from `does this connect to
  anything` in both `SKILL.md` and `agents/openai.yaml`. Codex and Gemini CLI
  do substring matching, and the `?` was dead weight; Claude routes the same.
- Added `scripts/bootstrap_labels.py` Python companion for hosts where bash
  is awkward (native Windows PowerShell, sandboxed Codex Desktop with Python
  but without bash). Same gh-backed behavior as the bash version.
- Added a `gh label create` copy-paste block to `references/label-schema.md`
  for mobile zip-upload and any other no-`gh`/no-shell host. The bash and
  Python helpers cite it as the source of truth so the three stay in sync.
- Added a Platform notes section to `SKILL.md` covering Claude Code,
  Claude Desktop (WSL/mac vs native Windows), Codex CLI/Desktop (with the
  `$idea-incubator` invocation note), Gemini CLI, and mobile zip-upload.

## Behavioral Smoke (3 prompts)

These match the round-1 prompts so we can compare behavior against the
v1.0.0 baseline directly.

### 1) Capture one idea

**Prompt**

> new idea: make a tiny CLI that turns voice memos into issue drafts for the ideas inbox

**Expected**

- One concise mobile-friendly issue draft.
- Capture context, why it matters, next step, suggested labels.
- No invented repo target; no auto-close.

**Observed**

- Single issue draft following `references/issue-template.md`.
- Suggested labels: `capture`, `skills`, `ready-now`.
- Repository target left as a placeholder for Tony to fill in.
- Pass.

### 2) Intake a Telegram dump

**Prompt**

> Telegram dump:
> - maybe a daily photo habit tracker
> - can we use saved messages for inbox?
> - maybe make the running route generator
> - check if yoga sequencing should live with idea-incubator?

**Expected**

- Separate candidate ideas where the split is clear.
- Ambiguity preserved, not guessed.
- Mobile-friendly markdown.

**Observed**

- Three separate candidate issues plus one routing/architecture question
  (the yoga-sequencing item) flagged for clarification rather than split or
  merged.
- The "saved messages for inbox" item surfaced as a meta/inbox question
  rather than a new domain idea.
- Pass.

### 3) Promote idea to a specialist handoff

**Prompt**

> promote idea #18: turn the instrument bore calculator into a maintained helper in instrument-maker-v4

**Expected**

- Copy-pasteable handoff matching `references/promotion-handoff.md`.
- Source linkage; specialist target named.
- `closes #18` only when explicitly requested.

**Observed**

- Handoff drafted with summary, why-now, requested deliverables, source link.
- `closes #18` omitted because Tony did not ask for it.
- Specialist target: `instrument-maker-v4`.
- Pass.

## Cross-platform caveats to flag in the PR

- The Python helper assumes `python3` on PATH. Native Windows installs may
  expose Python as `python` only - call sites in `SKILL.md` and
  `references/label-schema.md` show `python scripts/bootstrap_labels.py`
  which works on both Windows and POSIX.
- Both helpers still require an authenticated `gh`. Mobile zip-upload users
  will need to run the copy-paste block from a machine that has `gh`, or use
  the GitHub web UI.
- `agents/openai.yaml` `default_prompt` uses the Codex `$idea-incubator`
  invocation token. That is correct for the Codex agent file; it should not
  bleed into Claude or Gemini SKILL.md content (it does not).
- `CHANGELOG.md` is intentionally retained at the skill level despite the
  current skill-creator minimal-frontmatter guidance, because the repo
  release workflow expects it.
