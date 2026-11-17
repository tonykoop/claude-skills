---
name: handoff
description: >-
  Write next-issue or revision handoff prompts for agent personas. Generates a
  structured .md file in docs/plans/ with worktree setup, draft-PR creation,
  scope, validation, and deployment constraints. The generated prompts instruct
  persona agents to open a draft PR immediately (before writing code) and attach
  both their session plan and the handoff prompt as PR comments — creating a
  decision history record on every PR. Use when the user says "write handoff",
  "next handoff for Alice/Bob/etc", "handoff prompt", "assign persona", or after
  merging a PR to produce the next assignment.
---

# Handoff Prompt Writer

Generate copy-paste-ready handoff prompts for persona agents. Two types:

## Persona Registry

Terminal-level orchestrators are **personas**, not lanes. This avoids confusion
with headless sub-agents (lanes) that personas may dispatch.

| Persona | Shorthand | Worktree suffix |
|---------|-----------|----------------|
| Alice   | A         | `-alice`       |
| Bob     | B         | `-bob`         |
| Cindy   | C         | `-cindy`       |
| Dan     | D         | `-dan`         |
| Elsa    | E         | `-elsa`        |

## Type A: Next-Issue Handoff (after merge)

Write to `docs/plans/YYYY-MM-DD-<persona>-<slug>.md` (lowercase persona name):

```text
# <Persona> Handoff — Wave Xb (Model)

You own wrfcoin/<repo>#<issue>: <title>.

Repo: /home/tony/wrfcoin-public/<repo>   (origin wrfcoin/<repo>)

---

## PHASE 1 — WORKTREE SETUP (do this first)

Create a fresh worktree off the PUBLIC clone. Never use `/home/tony/wrfcoin/<repo>` or
`/home/tony/wrfcoin/worktrees/*`: those are clones of the read-only `*-archive` repos and
a PR from them lands in the wrong repo.

    git -C /home/tony/wrfcoin-public/<repo> fetch origin main
    git -C /home/tony/wrfcoin-public/<repo> worktree add \
        /home/tony/wrfcoin-public/wt-<repo>-<slug> -b <branch-name> origin/main
    cd /home/tony/wrfcoin-public/wt-<repo>-<slug>
    pwd && git remote get-url origin   # must print wrfcoin/<repo>, not *-archive

Do not reuse someone else's worktree, and do not run `git checkout -B` or `git clean -fdx`
in an existing one (both destroy work). Rust builds: check `df -h /` first and stop under
20 GB free; never put a cargo target dir in /tmp.

ALL of your work must happen inside that worktree.

---

## PHASE 2 — DRAFT PR & DECISION RECORD (before writing any code)

Every PR doubles as a decision history record. Before you write a single line of
implementation code, open a draft PR and attach your plan and this handoff prompt
so reviewers (and future agents) can see *what you were told* and *what you planned*.

### Step 1: Read the issue and formulate your plan

    gh issue view <issue> --repo wrfcoin/<repo>

Read the issue, explore the relevant code, then write your implementation plan.
The plan should cover: what you'll change, why, key files involved, and how you'll
validate. Keep it concise — bullet points are fine.

### Step 2: Push branch and open draft PR

You need at least one commit to push, so create an empty one:

    git commit --allow-empty -m "chore: open draft PR for wrfcoin/<repo>#<issue>"
    git push -u origin <branch-name>

Now create the draft PR with your session plan in the body. Use a HEREDOC so the
plan renders as markdown:

    gh pr create --repo wrfcoin/<repo> --draft \
      --title "#<issue>: <short title>" \
      --body "$(cat <<'EOF'
## Session Plan

<your implementation plan here — what you'll change, why, key files, approach>

---
Closes #<issue>
EOF
)"

Capture the PR number from the output — you'll need it for the next step.

### Step 3: Attach the handoff prompt as a PR comment

This handoff prompt lives at:

    /home/tony/wrfcoin/docs/plans/<HANDOFF_FILENAME>

Attach it so the PR preserves the full context of what you were assigned:

    gh pr comment <PR_NUMBER> --repo wrfcoin/<repo> \
      --body-file /home/tony/wrfcoin/docs/plans/<HANDOFF_FILENAME>

If the file path doesn't work (e.g., you're in a worktree without access to it),
paste the handoff content directly:

    gh pr comment <PR_NUMBER> --repo wrfcoin/<repo> --body "$(cat <<'HANDOFF'
<paste full handoff prompt here>
HANDOFF
)"

---

## PHASE 3 — IMPLEMENTATION

Now write your code. Commit and push as you go — the draft PR will collect your
commits automatically.

### Scope
- ...

### Requirements
- ...

### Validation
- ...

---

## PHASE 4 — COMPLETION

When your implementation is done and all validation passes:

    git push origin <branch-name>

Do NOT merge the PR yourself. The lead merges once CI is green (no second reviewer
is required). Consensus code (core4 validation, state apply, rewards, scheduled
features) merges one PR at a time onto current main and ships in a batched node
release via release.sh; never deploy it to a node yourself.
```

### Available semi-permanent worktrees

| Repo | Personas | Path pattern |
|------|----------|-------------|
| core4 | alice-elsa | `worktrees/core4-{alice,bob,cindy,dan,elsa}` |
| backend | alice-elsa | `worktrees/backend-{alice,bob,cindy,dan,elsa}` |
| frontend | alice-elsa | `worktrees/frontend-{alice,bob,cindy,dan,elsa}` |
| infra | alice-elsa | `worktrees/infra-{alice,bob,cindy,dan,elsa}` |
| smart-contracts | alice-cindy | `worktrees/smart-contracts-{alice,bob,cindy}` |
| security-testing | alice-bob | `worktrees/security-testing-{alice,bob}` |
| mobile | alice-bob | `worktrees/mobile-{alice,bob}` |

### Checklist before writing

1. Read the issue(s) to understand scope
2. Check for existing open PRs or prior work on the issue
3. **Assign a persona** — pick an available `<repo>-<persona>` (check sprint doc for in-use personas)
4. Pick a branch name that includes the issue number (e.g., `fix/123-weather-endpoint`)
5. Include deployment constraints (local builds only, SSH to N5 Pro, NO ghcr.io)
6. Include validation commands (`cargo check`, `cargo test -p`, `npm test`, etc.)
7. Include known pre-existing test failures to ignore
8. **Fill in `<HANDOFF_FILENAME>`** with the actual filename you're writing so the agent can reference it in Phase 2 Step 3

## Type B: Revision Handoff (changes requested)

Write to `docs/plans/YYYY-MM-DD-<persona>-revision-<slug>.md`:

```text
Your PR wrfcoin/<repo>#<pr-num> needs changes. Read the review comment and fix what's listed.

## Setup

    cd /home/tony/wrfcoin/worktrees/<repo>-<persona>
    git fetch origin <branch-name>
    git checkout <branch-name>
    git pull origin <branch-name>

## What to fix

Read the review comment on your PR:

    gh pr view <pr-num> --repo wrfcoin/<repo> --comments

Fix every Blocker. Address Warnings if you can.

## Decision record update

After fixing, comment on the PR with what you changed and why, so the decision
history stays complete:

    git add <files> && git commit -m "fix: address review feedback"
    git push origin <branch-name>
    gh pr comment <pr-num> --repo wrfcoin/<repo> --body "$(cat <<'EOF'
## Revision Summary

**Changes made:**
- <what you fixed>

**Review items addressed:**
- <which blockers/warnings you resolved>
EOF
)"

Do NOT open a new PR — push to the same branch.
```

## After writing

1. Report the file path to the user
2. Update the sprint doc persona table with status `next` for new assignments
