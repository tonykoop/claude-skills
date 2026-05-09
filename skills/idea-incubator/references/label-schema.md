# Label Schema

Use a small, predictable label set so ideas stay easy to sort from a phone.
The schema is split into workflow, state, and domain labels.

## Workflow labels

| Label | Use |
|---|---|
| `capture` | A fresh idea captured from Telegram, chat, or a quick note. |
| `intake` | A pasted dump that still needs parsing into separate ideas. |
| `connect` | An idea that should be linked to related issues or duplicates. |
| `review` | A backlog review or triage pass. |
| `promote` | An idea that is ready for a downstream handoff. |

## State labels

| Label | Use |
|---|---|
| `needs-clarification` | Key detail is missing before the idea can move. |
| `duplicate-candidate` | The idea may overlap with an existing issue. |
| `stale` | The idea has sat long enough to deserve a review. |
| `ready-now` | Low-friction idea that can be executed without much setup. |

## Domain labels

| Label | Use |
|---|---|
| `maker` | Fabrication, shop, or hardware ideas. |
| `instrument` | Musical instrument ideas and acoustics work. |
| `yoga` | Class, sequence, or movement ideas. |
| `skills` | Skill ecosystem, tooling, or orchestration ideas. |
| `general` | Idea does not fit a narrower domain. |

## Optional bootstrap

If GitHub CLI is available, create the labels in the current repo:

```bash
scripts/bootstrap-labels.sh owner/repo
```

If the repo is not known yet, keep the label names in the issue draft and
apply them later.
