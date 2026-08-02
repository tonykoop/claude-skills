# Approval Rubric — EXAMPLE (illustrative)

`Example, illustrative:` — this is the *shape* of a profile's rubric, not a
shipped policy. A real profile supplies its own lists. Nothing here is
project-specific.

## Safe to auto-approve (prompt shapes)

- Read-only inspection commands (status, diff, log, list).
- Routine file edits within the worktree the worker already owns.
- Re-running a previously-approved command verbatim.
- Test / lint / build invocations that do not push or deploy.

## Always escalate (never auto-approve)

- Destructive git ops: `push --force`, `reset --hard`, branch/tag deletion.
- Filesystem destruction: `rm -rf`, mass delete, overwrite outside the
  worktree.
- Anything touching production, secrets, credentials, or deploy.
- Network calls to unknown hosts.
- Rate-limit / quota / billing prompts.
- Anything the prompt cannot be unambiguously classified against this rubric.

## Refusal list (profile-supplied)

A profile adds project-specific command classes here (e.g. infra mutations
specific to that project). This generic package ships an **empty** refusal list
and expects the profile to populate it. Do not commit project command classes
into this file.
