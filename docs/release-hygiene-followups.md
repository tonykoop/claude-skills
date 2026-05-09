# Release Hygiene Follow-Ups

Tracked gaps from the 2026-05-09 release-hygiene audit
(`sprint/claude-alice-r1-skills-release-hygiene`). The audit reconciled the
README, `public-release-checklist.md`, and `skill-versioning.md` so they agree
that canonical version metadata lives in `manifest.yaml`. The items below are
intentionally deferred — each maps to an existing GitHub issue and several
overlap with the automation work owned by other lanes.

## Per-skill changelogs (#1)

Most reviewed skills (`maker-engineering`, `yoga-sequencer`, `reverse-engineer`,
`makerspace`, `skills-meta`) deliberately removed in-folder `CHANGELOG.md`
files because the bundled `skill-creator` quality gate flags them as
extraneous. Only `skills/idea-incubator/CHANGELOG.md` survives, by explicit
exception.

Recommended resolution path (not done in this PR to avoid redesign):

- Stand up `docs/skill-changelogs/<skill>.md` as the canonical changelog
  location, outside validator-checked skill files.
- Keep `idea-incubator/CHANGELOG.md` as a transitional symlink or stub
  pointing to the new location until validator behavior is confirmed.
- Update `docs/skill-versioning.md` step 4 to point at the new location.

Until then, manifest `notes` fields and per-skill `evals/round-N-eval.md` files
are the de-facto changelog evidence.

## Tagging policy (#2)

`docs/skill-versioning.md` calls for `<skill-name>/v<X.Y.Z>` tags before
packaging. No tags exist yet in this repo. Adding the first wave of tags
should pair with the packaging-script work in #5 so a tag, a manifest bump,
and a built artifact land together.

## Packaging scripts (#5)

Out of scope for this audit — overlaps with the automation lane owned by
Codex Alice. The release-hygiene docs now describe the *contract* the
packaging scripts should satisfy (manifest is canonical, tag before zip,
changelog source must exist).

## SKILL.md `version` / `last-updated` frontmatter (#6)

Blocked on the `skill-creator` validator. Today the validator accepts only
`name` and `description`; adding `version` / `last-updated` would fail
`quick_validate.py`. Once the validator ships an updated schema, mirror the
manifest's `canonical_version` and `last_updated` into each `SKILL.md`
frontmatter. The current README and public-release checklist already
anticipate this transition.

## Cross-device sync workflow (#12)

Out of scope for this audit — overlaps with #12 and the Codex Alice
automation lane. The release-hygiene docs assume a sync workflow exists
(drift detection, install/uninstall) but do not specify it. Items the sync
workflow needs from this repo:

- A canonical manifest with `canonical_version`, `last_updated`,
  `repo_path`, and `runtime` per skill — present today.
- A predictable changelog source per skill — see #1 above.
- Tagged release artifacts — see #2 above.

## Manifest hygiene observations

Minor inconsistencies left as-is to avoid redesign:

- `runtime:` values mix `portable` (skills-meta) and `shared` (everything
  else under `skills/`). Both refer to multi-runtime skills; consolidating
  to one term would be a one-line follow-up.
- `planned_skills.energy-management` is the only entry under `planned_skills`
  but more planned skills exist as open issues (#13–#18). Either expand this
  section or remove it and rely on the GitHub issue list.
