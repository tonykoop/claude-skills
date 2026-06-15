# Optional task source registry

Where candidate tasks may be read from when the user does not list them inline.
All sources are **read-only** for this skill. It never edits issues, calendars,
or repos.

## Sources

| Source | How to read | Notes |
|---|---|---|
| Inline (default) | the user's message | always available, fully offline |
| idea-incubator issue inbox | `gh issue list` filtered by `ready-now` / domain labels | preferred backlog source; honors the shared label schema |
| Active project repos | `gh issue list -R <repo>` open issues | only repos the user names |
| Google Calendar | calendar connector, read events | for teaching blocks and committed time in weekly mode |

## Reading idea-incubator candidates

When the user says "use my inbox" or similar:

```bash
# read-only; ready-now tasks are the cheap-energy candidates
gh issue list -R <inbox-repo> --label ready-now --state open --json number,title,labels
```

Treat labels as the effort/energy signal (see `energy-label-schema.md`). Do not
re-rate a `ready-now` task as expensive.

## Rules

- Never write to any source from this skill.
- If no source is reachable, fall back to asking the user for an inline list.
- Do not cache or persist anything read from a source — read fresh each plan.
