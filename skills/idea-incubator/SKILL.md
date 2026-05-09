---
name: idea-incubator
description: Capture, classify, connect, review, and promote speculative ideas through GitHub issues, with Telegram Saved Messages as the capture layer and copy-pasteable issue drafts when automation is unavailable.
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
- `does this connect to anything?`
- `promote idea #N`

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
   skill. Include `closes #N` only when Tony wants the tracked issue closed by
   the downstream work.

## Operating rules

- Default to mobile-friendly, copy-pasteable Markdown.
- Use GitHub issues as the durable incubation layer.
- Treat Telegram Saved Messages as the quick capture layer.
- If `gh` is available, you may create labels or issues directly; otherwise
  print the exact command or issue draft.
- Do not hard-code repository ownership or visibility when the target repo is
  unknown. Use a placeholder or ask Tony first.
- Do not auto-close ideas, and do not invent ideas that Tony did not capture.

## Bundled references

- [`references/label-schema.md`](references/label-schema.md)
- [`references/issue-template.md`](references/issue-template.md)
- [`references/promotion-handoff.md`](references/promotion-handoff.md)

## Optional helper

- [`scripts/bootstrap-labels.sh`](scripts/bootstrap-labels.sh) creates the
  labels in the schema when `gh` is installed.
