# ADR: sprint-supervisor public release readiness

- **Status:** Accepted (pending reviewer sign-off)
- **Date:** 2026-06-16
- **Epic:** [#164](https://github.com/tonykoop/claude-skills/issues/164)
- **Decision owner:** sprint-supervisor maintainer
- **Supersedes:** the implicit "keep-private, project-coupled" status quo

## Context

`sprint-supervisor` is an operational skill that babysits a running multi-pane
tmux agent sprint while the user is away: it polls the manager pane and grid
persona panes on an adaptive cadence, auto-approves routine agent permission
prompts via a fixed rubric, escalates destructive prompts, and produces a
morning summary. It scales across multiple supervisors via `/tmp` lockfiles.

The pattern is broadly useful to anyone running a tmux-based agent swarm. But
as written (≤ v1.3.1) the skill was coupled to one specific project ("wrfcoin"):

- **Hardcoded paths:** `/home/tony/wrfcoin/...`, `/home/tony/wrfcoin/worktrees/`,
  `/home/tony/wrfcoin/scripts/sprint-watchdog.sh`.
- **Hardcoded hosts:** the "N5 / N5 Pro testnet" host and its specific
  read-only diagnostic commands (`node-dashboard.py`, etc.) baked into the
  approval rubric and refusal list.
- **Hardcoded labels:** morning-summary repo groups (`core4 / infra / backend /
  frontend / smart-contracts`), the `wrfcoin/<repo>#NNNN` PR citation format,
  and project-flavored scope names (`consensus`, `infra-backend`).
- **Project-flavored tuning notes** referencing specific sprints and repos.

The owner is preparing to release skills publicly, so the skill must either be
abstracted for general use or explicitly marked private and excluded from sync.

## Decision

**Abstract-and-release via a SPLIT.** Ship a generic, project-agnostic
`tmux-agent-supervisor` core, and move every project-specific value into a
**configuration file** that a thin per-project extension supplies.

Concretely:

1. The skill body (SKILL.md) becomes provider- and project-agnostic. All
   illustrative examples use placeholders (`<repo>`, `~/work/<project>`,
   `<host>`).
2. The **refusal list** and **approval rubric** keep a conservative built-in
   baseline but read project-specific extensions from a config file.
3. Project labels (repo groups, PR citation format, protected branches, trusted
   hosts) move entirely into config.
4. A bundled `references/supervisor-config.example.yaml` documents the schema,
   ships safe generic defaults, and includes a **commented wrfcoin-flavored
   example block** so the original behavior is reproducible by anyone who wants
   it — without that behavior being the default.

This is the "split: generic core + configurable extension" option, expressed as
*configuration-driven* extension rather than a second skill package. A separate
`sprint-supervisor-wrfcoin` skill is unnecessary: the only delta is data, and
data belongs in a config file, not in a forked skill body.

## Options considered

### Option A — Keep private
Add a `private: true` marker (skills-meta convention) and exclude from public
sync. *Rejected:* the pattern is the most reusable part of the toolkit, and the
owner's stated direction is public release. Keeping it private wastes the work.

### Option B — Abstract in place (no config file)
Rewrite the SKILL.md to use generic examples but leave behavior hardcoded.
*Rejected:* the refusal list and rubric are exactly the parts a user must tune
for their own protected paths/hosts; hardcoding generic values would make the
skill *less* safe (a user's real protected host wouldn't be covered) while
still requiring a fork to customize.

### Option C — Split: generic core + configurable extension  ✅ chosen
Generic core + a config file that supplies project specifics, with a commented
real-world example. Best of both: public-safe by default, fully recoverable
behavior for the original project, no skill fork to maintain.

### Option D — Two separate skills (`tmux-agent-supervisor` + `sprint-supervisor-wrfcoin`)
*Rejected for now:* doubles maintenance for what is purely a data difference.
Revisit only if a project needs to override skill *logic* (not just values).

## Consequences

**Positive**
- Skill is publicly releasable with no project internals leaked.
- Safety posture improves: the refusal list / trusted-hosts are now explicit
  per-install rather than assumed.
- Original behavior is fully reproducible from the commented example block.
- Single skill body to maintain; no fork drift.

**Negative / costs**
- First-run UX gains a config step. Mitigated: the skill falls back to the
  bundled example defaults and runs, prompting the user once to copy+customize.
- The skill body now references a config schema; the config and SKILL.md must
  stay in sync (changelog discipline).
- Slightly more indirection when reading the rubric (some rows say "from config").

**Neutral**
- Public name stays `sprint-supervisor` for now (see Remaining work). The
  generic identity is "tmux-agent-supervisor" but renaming a skill breaks the
  description-trigger and any existing install references, so it is deferred.

## Migration checklist

- [x] Externalize refusal list + approval rubric + labels into
      `references/supervisor-config.example.yaml` with generic defaults and a
      commented wrfcoin example.
- [x] Add a `## Configuration` section to SKILL.md (lookup order, what config
      controls, fallback behavior).
- [x] Replace hardcoded wrfcoin paths/hosts/labels in SKILL.md with placeholders
      (`<repo>`, `~/work/<project>`, `<host>`, config-supplied groups/citation).
- [x] Preserve the description-trigger frontmatter (triggers unchanged; only the
      "WRFCoin" qualifier removed from the prose).
- [x] Bump version 1.3.1 → 1.4.0 (minor: additive config + genericization).
- [x] Public README explaining watchdog-vs-skill split, lockfile coordination,
      240s cadence reasoning, configuration, and a quickstart.
- [x] CHANGELOG entry for 1.4.0.

## Remaining / optional work (NOT blocking release)

These are intentionally left for the reviewer / a follow-up and tracked as
unchecked items on the PR:

- [ ] **Demo recording** (cold-start → supervise → morning summary). Epic #164
      tracks this; leave the epic open until the demo lands.
- [ ] **Final public name decision.** Keep `sprint-supervisor` vs rename to
      `tmux-agent-supervisor`. Renaming changes the trigger surface and install
      paths — decide deliberately, not as part of this PR.
- [ ] **Genericize reference docs prose.** `references/scaling-topology.md`,
      `morning-summary.md`, `dispatch-patterns.md`, and `routines-integration.md`
      still contain project-flavored worked examples (repo names, host names,
      sprint dates). These are illustrative and safe-ish, but a full public pass
      should swap them for placeholders too. Left as TODO to keep this PR's
      SKILL.md edits surgical and low-risk.
- [ ] **`sprint-watchdog.sh` packaging.** The watchdog is install-only today and
      still carries the original default sessions; package it alongside the skill
      and read its sessions/paths from the same config.
- [ ] **skills-meta manifest** entry confirming the config-file dependency
      (#165).

## Lingering project-specific references (knowingly retained)

The following remain in the SKILL.md tuning-notes sections because they are
*historical run logs*, not live behavior, and rewriting them would distort the
record. They name no secrets and no live paths:

- Dated tuning notes ("2026-05-12 session", "2026-05-18 session") mention repo
  counts and a generic "sandbox DNS block" (the wrfcoin-specific `codex_sandbox`
  wikilink was removed).
- One reference to a "second-level sprint manager" experience.

All live, behavior-driving project specifics (paths, the N5 host, repo groups,
PR citation format) have been moved to config or replaced with placeholders.
