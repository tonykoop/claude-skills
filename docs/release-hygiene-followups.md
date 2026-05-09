# Release Hygiene Follow-Ups

Tracked gaps from the 2026-05-09 release-hygiene audit
(`sprint/claude-alice-r1-skills-release-hygiene`). The audit reconciled the
README, `public-release-checklist.md`, and `skill-versioning.md` so they agree
that canonical version metadata lives in `manifest.yaml`. The items below are
intentionally deferred to the PRs that own them — this doc is an index, not a
competing source of truth.

## Validator evidence

The decision to keep canonical version metadata in `manifest.yaml` (rather
than `SKILL.md` frontmatter) is grounded in the bundled validator's behavior.

```bash
$ python3 /home/tony/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>
```

Validator source: `/home/tony/.codex/skills/.system/skill-creator/scripts/quick_validate.py`,
`allowed_properties = {"name", "description", "license", "allowed-tools", "metadata"}`.

Observed behavior on 2026-05-09 (verbatim from the audit run):

```text
# baseline (only name + description)
$ python3 .../quick_validate.py skills/idea-incubator
Skill is valid!

# inject version + last-updated as top-level keys
$ python3 .../quick_validate.py /tmp/with-injected-version
Unexpected key(s) in SKILL.md frontmatter: last-updated, version.
Allowed properties are: allowed-tools, description, license, metadata, name
# exit 1

# nest under metadata: { version: ..., last-updated: ... }
$ python3 .../quick_validate.py /tmp/with-metadata-keys
Skill is valid!
# exit 0
```

The `metadata` nesting path is a permitted future migration target; it does
not require a validator update. Until that migration is decided,
`manifest.yaml` remains the single source of truth.

## Per-skill changelogs (#1)

Most reviewed skills (`maker-engineering`, `yoga-sequencer`, `reverse-engineer`,
`makerspace`, `skills-meta`) deliberately removed in-folder `CHANGELOG.md`
files because the `skill-creator` quality gate flagged them as extraneous.
Only `skills/idea-incubator/CHANGELOG.md` survives, by explicit exception.

**Owner:** PR #37 (`sprint/claude-dan-r1-packaging-review`) defines the
release workflow including changelog format. PR #32
(`sprint/codex-alice-r1-manifest-automation`) defines the drift checker that
detects missing per-skill changelogs.

This audit defers the in-folder-vs-out-of-folder decision to those PRs and
will adopt whichever convention they land. Until then, manifest `notes`
fields and per-skill `evals/round-N-eval.md` files are the de-facto
changelog evidence.

## Tagging policy (#2) and packaging scripts (#5)

**Owner:** PR #37 (`sprint/claude-dan-r1-packaging-review`) closes #2 and #5.
It defines tag naming (`<skill-name>/v<X.Y.Z>`), the release order, the
`scripts/package_skill.{sh,ps1}` packaging tooling, and the initial-tagging
recipe for the existing skill set.

This audit aligns the README and public-release checklist with that workflow
(canonical version in `manifest.yaml`, tags before packaging) but does not
duplicate the packaging documentation here.

## Manifest drift detection (#3, #4, #11)

**Owner:** PR #32 (`sprint/codex-alice-r1-manifest-automation`) adds
`docs/manifest-drift-checks.md` and the `--strict` mode in
`skills/skills-meta/scripts/skills-meta.py`. The release-hygiene docs in
this PR assume that drift checker exists and refer to it through
`docs/skill-versioning.md`.

## SKILL.md `version` / `last-updated` frontmatter (#6)

Blocked on the bundled `skill-creator` validator (see Validator evidence
above). Two compatible migration paths remain open:

1. Wait for the validator to add `version` / `last-updated` as top-level
   allowed properties.
2. Carry version data under the already-permitted `metadata` key:

   ```yaml
   ---
   name: skill-name
   description: ...
   metadata:
     version: 1.0.0
     last-updated: 2026-05-09
   ---
   ```

The README and public-release checklist anticipate either resolution.

## Cross-device sync workflow (#12)

Out of scope for this audit. The release-hygiene docs assume a sync workflow
will exist (drift detection, install/uninstall) but do not specify it. Items
the sync workflow needs from this repo, all already in place after the
PR #32 / #35 / #37 set:

- A canonical manifest with `canonical_version`, `last_updated`,
  `repo_path`, and `runtime` per skill — present today.
- A predictable changelog source per skill — see #1 above (owned by #37).
- Tagged release artifacts — see #2 above (owned by #37).
- A drift checker that fails CI on metadata gaps — owned by #32.

## Manifest hygiene observations

Minor inconsistencies left as-is to avoid redesign:

- `runtime:` values mix `portable` (skills-meta) and `shared` (everything
  else under `skills/`). Both refer to multi-runtime skills; consolidating
  to one term would be a one-line follow-up.
- `planned_skills.energy-management` is the only entry under `planned_skills`
  but more planned skills exist as open issues (#13–#18). Either expand this
  section or remove it and rely on the GitHub issue list.
