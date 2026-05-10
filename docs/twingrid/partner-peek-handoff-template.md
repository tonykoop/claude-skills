# TwinGrid Partner Peek Handoff — TEMPLATE

> Per-lane, per-side. Sent **after** the blind pass and after the manager
> has written the shared reveal brief.

## Round identity

- Round: `{{round_number}}`
- Lane: `{{lane}}`
- Side: `{{A | B}}`
- Runtime: `{{claude | codex}}`
- Your blind output folder: `{{/tmp/twingrid-r<N>-<runtime>-<lane>-<slug>}}`
- Partner output folder: `{{/tmp/twingrid-r<N>-<other_runtime>-<lane>-<slug>}}`

## Reveal brief

Read first: `{{/tmp/twingrid-r<N>-partner-peek.md}}`

The brief contains a one-paragraph A/B comparison per lane plus the rules
restated below.

## Rules

- Read **only** your lane section of the reveal brief, then inspect your
  partner's output folder.
- Keep your original blind output intact where practical. Add
  `partner-peek-improvements.md`, `v2-*` files, or clearly named supplemental
  artifacts in **your own** output folder.
- Do **not** edit your partner's output folder.
- If you make repo or skill changes, use the isolated branch/worktree
  assigned to you and open a draft PR. If the improvement is artifact-only,
  do not manufacture a PR; include exact PR-worthy recommendations in your
  improvement memo.
- If a required tool is missing, stop and name the exact missing tool,
  command, and install hint. Do not silently work around it.
- Continue to **NOT** self-report `elapsed_time`, `context_remaining`,
  `usage_remaining`, or `blocked_state`.

## Required outputs

1. `partner-peek-improvements.md` in your output folder.
2. A **partner-peek record** matching
   [`partner-peek-record.schema.yaml`](partner-peek-record.schema.yaml).
   Both YAML and JSON are accepted.
3. At least one **validation run** appropriate to your artifacts. Use the
   tools the manager announced (`yamllint`, `jq`, `shellcheck`, `openscad`,
   `lilypond`, `inkscape`, `rsvg-convert`, etc.) and record the exact
   commands and pass/fail in the record.
4. **One concrete skill-improvement recommendation** for the skill named in
   your assignment, with a PR-worthy diff or proposed file path. If the
   improvement is too large for an artifact-only memo, mark it
   `pr_recommended: true` so the manager can spawn a follow-up issue.

## What "improving your own deliverable" means

You are not rewriting your blind output. You are:

- Adopting the partner's strongest specific ideas (cite by partner artifact
  + line if possible).
- Hardening uncertainty, validation, or safety treatment your blind run
  underweighted.
- Adding the partner-peek record and skill-improvement memo.

## Acceptance

The Partner Peek pass is accepted when:

- Your blind artifacts are unchanged.
- `partner-peek-improvements.md` enumerates which partner ideas you adopted
  and which you rejected and why.
- Your partner-peek record validates against the schema.
- At least one validation command was actually run (not just listed) and its
  result recorded.
- A concrete skill-improvement recommendation is present.
