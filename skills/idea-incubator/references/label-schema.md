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

Pick the helper that matches the host shell. Both require an authenticated
`gh` and produce the same labels.

```bash
# bash, WSL/macOS/Linux/Git Bash
scripts/bootstrap-labels.sh owner/repo
```

```powershell
# Python, native Windows or sandboxed Codex Desktop
python scripts/bootstrap_labels.py owner/repo
```

If neither helper can run (mobile zip-upload, no `gh`), use the raw
`gh label create` commands below from any machine that does have `gh`. The
list is the source of truth for both helpers above; keep them in sync if you
edit it.

```bash
gh label create capture --color 1d76db --description "Fresh idea captured from Telegram, chat, or a quick note." --force
gh label create intake --color 0e8a16 --description "A pasted dump that still needs parsing into separate ideas." --force
gh label create connect --color 5319e7 --description "Link this idea to related issues or duplicates." --force
gh label create review --color fbca04 --description "Backlog review or triage pass." --force
gh label create promote --color b60205 --description "Ready for downstream handoff." --force
gh label create needs-clarification --color d93f0b --description "Key detail is missing before the idea can move." --force
gh label create duplicate-candidate --color e11d21 --description "This idea may overlap with an existing issue." --force
gh label create stale --color c2c2c2 --description "The idea has sat long enough to deserve a review." --force
gh label create ready-now --color 0052cc --description "Low-friction idea that can be executed quickly." --force
gh label create maker --color bfdadc --description "Fabrication, shop, or hardware ideas." --force
gh label create instrument --color c5def5 --description "Musical instrument ideas and acoustics work." --force
gh label create yoga --color f9d0c4 --description "Class, sequence, or movement ideas." --force
gh label create skills --color d4c5f9 --description "Skill ecosystem, tooling, or orchestration ideas." --force
gh label create general --color ededed --description "Idea does not fit a narrower domain." --force
```

If the repo is not known yet, keep the label names in the issue draft and
apply them later.
