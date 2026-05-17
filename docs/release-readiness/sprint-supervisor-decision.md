# Sprint Supervisor Public Release Decision

Issue: https://github.com/tonykoop/claude-skills/issues/164

Decision: staged extraction

`sprint-supervisor` should not be released publicly in its current form. It is
useful operationally, but it is currently a personal/WRFCoin supervisor with a
tmux-agent supervision pattern inside it. The releasable path is to extract the
portable pattern first, then keep the WRFCoin behavior as a private adapter or
project profile.

## Evidence

- `sprint-supervisor` is not present in this repo's shipped skill roots:
  `skills/`, `claude/skills/`, or `codex/skills/`.
- `manifest.yaml` has no `sprint-supervisor` entry, and
  `scripts/package_skill.sh sprint-supervisor --dry-run` exits with
  `error: skill 'sprint-supervisor' not found in manifest.yaml`.
- `skills-meta` sees installed local copies, but every discovered
  `sprint-supervisor` record is `missing-from-manifest`. That means this is an
  installed local/private skill today, not a versioned public release artifact.
- The installed `SKILL.md` is tightly coupled to Tony's operational
  environment:
  - WRFCoin is named in the description and refusal list.
  - tmux targets assume `0:0`, `twingrid-a`, and `twingrid-b`.
  - the watchdog helper path is `/home/tony/wrfcoin/scripts/sprint-watchdog.sh`.
  - approval rubrics include WRFCoin/N5-specific command classes.
  - lockfile and cadence behavior are tuned around this private sprint manager
    topology.
- The repo's public-release gate requires personal paths, private project
  assumptions, operational details, missing bundled resources, deterministic
  setup instructions, and smoke coverage to be reviewed before release.
- The agentic-skill gate requires manifest/changelog alignment, bundled scripts
  referenced by the skill, behavior fixtures, runtime evidence, and regression
  coverage. Those are not available for `sprint-supervisor` in this repo yet.

## Options Considered

### Abstract and Release Now

Not ready. There is no repo-local package to patch, no manifest entry, and no
public demo/test fixture set. A direct release would either publish private
paths and project assumptions or require a broad extraction that is too large
for a closeout lane.

### Keep Private

Acceptable as the current operational state, but incomplete as a product
decision. Because the reusable mechanism is valuable, marking only
`private: true` would preserve safety but lose the chance to package the
generic pattern.

### Staged Extraction

Recommended. Split the current skill into:

- `tmux-agent-supervisor` (public, generic): lockfile coordination, watchdog
  split, 240-second cadence, prompt-shape approval rubric, escalation policy,
  morning summary format, and fixture prompts.
- `sprint-supervisor-wrfcoin` or private profile (not public): WRFCoin/N5
  paths, Tony's tmux topology, project-specific refusal-list entries, and local
  watchdog command wiring.

## Public Release Bar

Do not release a public package until the generic skill has:

- a manifest entry with `canonical_version`, `runtime`, `repo_path`,
  `last_updated`, and `status`;
- a per-skill `CHANGELOG.md`;
- a public `README.md` or reference doc explaining the watchdog-vs-skill split,
  lockfile coordination, and 240-second cadence;
- configurable prompt-approval rubric and refusal-list examples;
- fixture prompts covering trigger, non-trigger, ambiguous scope, adjacent
  skill conflict, safe approval, and escalation/refusal cases;
- a runtime smoke note for at least one tmux-backed environment;
- a public demo transcript or redacted recording for cold-start, supervision,
  and morning-summary flow;
- no unlabelled private paths, WRFCoin assumptions, N5 assumptions, or
  Tony-specific topology requirements.

## Round 2 Recommendation

Open a follow-up implementation lane for staged extraction:

1. Add `skills/tmux-agent-supervisor/` with generic `SKILL.md`,
   `CHANGELOG.md`, `README.md` or `references/operation-model.md`, and a small
   fixture set.
2. Move Tony/WRFCoin specifics into a private adapter/profile outside the
   public package, or document it as an illustrative private extension without
   shipping secrets or local paths.
3. Add the manifest entry only when the generic package passes the agentic
   skill static, behavior, runtime, and regression gates.
4. Leave existing installed `sprint-supervisor` copies private/missing from the
   public manifest until that extraction PR exists.

