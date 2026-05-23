# NotebookLM integration (optional layer)

NotebookLM is an optional retrieval layer on top of the markdown
source-of-truth. The skill works fine without it. Use NotebookLM
when:

- The space's documentation is large (multi-hundred-page safety
  manuals, decades of class history).
- The user wants conversational Q&A grounded in the docs ("what
  does the safety manual say about glue-up time on the spray booth?").
- You want the docs accessible via Gemini app on the user's phone
  while they're in the shop.

Skip NotebookLM when:

- The user is air-gapped or doesn't have a Google account.
- The docs are short enough to read directly each session.
- Privacy / member-only content shouldn't be uploaded to a third
  party.

## Source-of-truth model

Markdown files in `spaces/<slug>/` remain canonical. NotebookLM is a
*read replica* — you populate it from the markdown, not the other
way around.

If you change something in NotebookLM but not in the markdown, the
next sync overwrites your NotebookLM change. Always edit the
markdown.

## Wiring NotebookLM to a space profile

In the space's `profile.yaml`:

```yaml
notebooklm_url: https://notebooklm.google.com/notebook/<id>
notebooklm_synced_at: 2026-05-01
notebooklm_source_files:
  - tools.md
  - materials-policy.md
  - certifications.md
  - classes.md
  - safety-rules.md
```

The skill reads `notebooklm_url` and offers it as an alternate query
target when the user asks long-form questions.

## How the skill uses NotebookLM (v0.1 behavior)

The v0.1 skill **doesn't directly query NotebookLM** — that integration
is on the roadmap. Instead, when the user asks a question that the
markdown doesn't answer, the skill says:

> "I don't have that in the markdown. The space's NotebookLM brain at
> `<url>` may have it — try asking there, then paste the answer back
> if you want me to incorporate it into the build packet."

This keeps the markdown as the single source of truth and avoids the
skill over-promising retrieval it doesn't actually do.

## Sync script (roadmap, not v0.1)

A future `scripts/sync_notebooklm.py` would:

1. Read `spaces/<slug>/profile.yaml` to find `notebooklm_url` and
   `notebooklm_source_files`.
2. Push the markdown files to NotebookLM via the unofficial API.
3. Update `notebooklm_synced_at` in the profile.

Until that exists, sync manually: download the markdown from
GitHub, upload to NotebookLM, repeat when the markdown changes.

## Privacy considerations

If the space's profile is marked `visibility: private`:

- Don't auto-suggest NotebookLM as a sync target.
- Don't include `notebooklm_url` in any public artifact (deck, README,
  print packet).
- If the user explicitly opts in, sync — but warn that NotebookLM
  uploads are processed by Google.

## Rationale

The Gemini brainstorm proposed NotebookLM as the canonical store and
markdown as the export. We inverted that — markdown canonical,
NotebookLM optional — because:

- The skill works offline / standalone. No external account required.
- Version control via git is straightforward; NotebookLM doesn't
  expose its versioning.
- A skill that *requires* a third-party account is a higher install
  barrier for outside makers.
- Privacy/policy decisions stay with the user. They can opt into
  NotebookLM if they want richer retrieval.
