---
name: idea-incubator
version: 0.1.0
last-updated: 2026-05-09
description: >-
  Capture, classify, connect, review, and promote speculative ideas into a
  searchable GitHub issue inbox. Use when the user says "new idea", "incubate
  this", "add this to my inbox", "process my Telegram dump", "review my
  ideas", "does this connect to anything?", "promote idea #N", or wants to
  turn a rough note, voice fragment, or URL into a tracked issue. Telegram
  Saved Messages is the quick-capture layer; GitHub issues are the durable
  layer. Do not use for ideas that are already scoped and ready to build —
  route those directly to maker-engineering or the relevant specialist.
---

# Idea Incubator

Use this skill to turn rough ideas into a searchable GitHub issue inbox,
connect them to related work, review the backlog, and promote ready ideas
into specialist handoffs.

## Trigger phrases

- `new idea`
- `incubate this`
- `add this to the inbox`
- `process my Telegram dump`
- `review my ideas`
- `does this connect to anything`
- `promote idea #N`

The phrases are kept punctuation-free so substring-matching agents (Codex,
Gemini CLI) hit them as reliably as Claude does.

## Do not trigger for

- Ideas that already have a clear build plan — route to `maker-engineering` instead.
- Feature requests for active code projects — open a GitHub issue directly.
- Tasks the user wants done immediately rather than tracked.

## Modes

1. **Capture** - turn one idea into one issue draft. If the input is a note,
   URL, or voice-to-text fragment, keep the draft short and actionable.
2. **Intake** - split a pasted Telegram dump into candidate ideas. Keep
   uncertain splits visible instead of guessing.
3. **Connect** - search for related ideas, prerequisites, duplicates, and
   cross-pollination candidates. Link them; do not auto-close.
4. **Review** - surface stale ideas, best-fit-for-now ideas, and clusters
   worth revisiting. Summarize; do not score emotional resonance numerically.
5. **Promote** - draft the handoff text for the downstream repo or specialist
   skill. Include `closes #N` only when the user wants the tracked issue closed
   by the downstream work. Route to `maker-engineering` for physical builds,
   to a domain specialist (`instrument-maker`, `makerspace`, `reverse-engineer`)
   when the scope is clear, or to a project repo when the idea belongs in an
   existing backlog.

## Operating rules

- Default to mobile-friendly, copy-pasteable Markdown.
- Use GitHub issues as the durable incubation layer.
- Treat Telegram Saved Messages as the quick capture layer.
- If `gh` is available, you may create labels or issues directly; otherwise
  print the exact command or issue draft.
- Do not hard-code repository ownership or visibility when the target repo is
  unknown. Use a placeholder or ask the user first.
- Do not auto-close ideas, and do not invent ideas that the user did not capture.

## Bundled references

- [`references/label-schema.md`](references/label-schema.md)
- [`references/issue-template.md`](references/issue-template.md)
- [`references/promotion-handoff.md`](references/promotion-handoff.md)

## Optional helpers

Both helpers create the same labels and need an authenticated `gh`. Pick the
one that matches the host shell:

- [`scripts/bootstrap-labels.sh`](scripts/bootstrap-labels.sh) - bash, for
  WSL, macOS, Linux, and Git Bash on Windows.
- [`scripts/bootstrap_labels.py`](scripts/bootstrap_labels.py) - Python 3,
  for native PowerShell on Claude Desktop (Windows) or any environment where
  bash is awkward but Python is available.

If neither works (mobile zip-upload, sandboxed Codex Desktop, no `gh`), fall
back to the copy-pasteable `gh label create` block in
[`references/label-schema.md`](references/label-schema.md), or apply the
labels by hand from the GitHub web UI.

## Platform notes

This skill is intentionally portable. Behavior shifts a little by host:

- **Claude Code / Claude Desktop on WSL or macOS** - full path; `gh` and bash
  scripts work as written.
- **Claude Desktop on native Windows** - prefer the Python bootstrap helper;
  paths in this skill are POSIX-relative and resolve correctly.
- **Codex CLI / Codex Desktop** - invoke explicitly with `$idea-incubator`
  when you want guaranteed routing. The `$skill-name` syntax is a Codex
  convention; do not paste it into other clients.
- **Gemini CLI** - triggers match by substring, so the phrases above work;
  bundled scripts run via the host shell as usual.
- **Mobile zip-upload (Claude.ai)** - assume no `gh`, no shell. Stay in
  copy-pasteable Markdown mode and emit the issue draft and `gh label create`
  commands as text blocks for the user to run later.
