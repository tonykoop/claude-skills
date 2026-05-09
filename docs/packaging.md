# Skill Packaging and Release

How to build, tag, and distribute a skill artifact from this repo.

---

## Release order

Every release follows this sequence. Do not skip steps — a zip built from an untagged or dirty commit cannot be audited later.

1. Edit the skill under its `repo_path`.
2. Bump `version` in the skill's `SKILL.md` (if the validator accepts it) or record the new version in `manifest.yaml` only.
3. Update `last-updated` / `last_updated` to today's date (ISO-8601: `YYYY-MM-DD`).
4. Add a per-skill changelog entry (see [Changelog format](#changelog-format) below).
5. Update `manifest.yaml` with the new `canonical_version` and `last_updated`.
6. Commit all changes.
7. Tag the commit: `git tag <skill-name>/v<X.Y.Z>` (see [Tag naming](#tag-naming)).
8. Build the zip from the tagged commit using the packaging scripts.
9. Upload or install the artifact on the target runtimes.

---

## Tag naming

Tags use the format `<skill-name>/v<X.Y.Z>` where `skill-name` is the key used in `manifest.yaml`.

```
skills-meta/v1.0.0
tmux-sprint/v2.0.0
maker-engineering/v1.1.0
```

Use the `v` prefix on the version component. Omitting it breaks tooling that
parses release artifacts by tag.

Create a tag from the current commit:

```bash
git tag skills-meta/v1.0.0
git push origin skills-meta/v1.0.0
```

Tag an earlier commit by hash:

```bash
git tag skills-meta/v1.0.0 <commit-sha>
git push origin skills-meta/v1.0.0
```

---

## Bundle generation

Use `scripts/package_skill.sh` (Bash / WSL) or `scripts/package_skill.ps1` (PowerShell) to build a zip artifact.

### Bash / WSL

```bash
# Dry run — shows what would be packaged without creating the zip
./scripts/package_skill.sh skills-meta --dry-run

# Package from current checkout
./scripts/package_skill.sh skills-meta

# Package from a specific tag (checks out the tag, zips, restores HEAD)
./scripts/package_skill.sh skills-meta --from-tag skills-meta/v1.0.0
```

Output: `dist/skills-meta-v1.0.0.zip`

### PowerShell (Windows)

```powershell
# Dry run
.\scripts\package_skill.ps1 skills-meta -DryRun

# Package from current checkout
.\scripts\package_skill.ps1 skills-meta

# Package from tag
.\scripts\package_skill.ps1 skills-meta -FromTag skills-meta/v1.0.0
```

Output: `dist\skills-meta-v1.0.0.zip`

Both scripts:

- Read `manifest.yaml` to locate the skill directory and canonical version.
- Refuse to package a dirty working tree unless `--allow-dirty` / `-AllowDirty` is set.
- Include only the skill directory in the zip, not the full repo.
- Name the output `<skill-name>-v<version>.zip` so artifacts self-document their version.

---

## Validation before packaging

Run these checks before building a release zip:

```bash
# 1. Verify git is clean
git status --short
# expect: no output

# 2. Verify the skill appears in manifest.yaml with the right version
python3 skills/skills-meta/scripts/skills-meta.py --mode single --skill <skill-name>
# expect: status ok, or known drift you've just fixed

# 3. Dry-run the package script
./scripts/package_skill.sh <skill-name> --dry-run
# expect: shows skill path, version, and output filename with no errors
```

If any check fails, fix the issue before tagging.

---

## Upload and install

### Claude Code / Claude Desktop

1. Open Claude Code → Settings → Skills.
2. Upload the zip file or point to the extracted directory.
3. Verify the installed skill version with:
   ```
   what version of <skill-name> am I running?
   ```

### Codex CLI / Codex Desktop

Follow the Codex skill install guide. Unzip to `~/.codex/skills/<skill-name>/` or the configured skill root, then restart Codex.

### Gemini CLI

Unzip to the configured Gemini skill root. Exact path depends on the Gemini CLI version; check the runtime-specific install notes.

### Portable skills

Skills with `runtime: portable` in `manifest.yaml` use the same zip for all runtimes. Install the extracted directory at the skill root for each target runtime.

---

## Initial tags for active skills

When running the tagging workflow for the first time against existing shipped skills, create one tag per active skill at its current `canonical_version`:

```bash
for skill in skills-meta tmux-sprint tmux-v2 merge-review sprint-update disk-cleanup \
             codex-merge-manager codex-gh-fix-ci wrfcoin-sprint-dispatch \
             idea-incubator maker-engineering yoga-sequencer makerspace reverse-engineer; do
  version=$(python3 -c "
import yaml, sys
m = yaml.safe_load(open('manifest.yaml'))
s = m['skills'].get('$skill') or m['skills'].get('$skill'.replace('-','_'))
print(s['canonical_version'] if s else 'MISSING')
")
  echo "tagging $skill/v$version"
  git tag "$skill/v$version" || echo "  tag already exists, skipping"
done
git push origin --tags
```

Run this from the repo root after all active skill versions are correct in `manifest.yaml`.

---

## Changelog format

Each skill that ships a release should have a `CHANGELOG.md` in its skill directory.

```markdown
# Changelog — <skill-name>

## v1.1.0 — 2026-05-09

- Added <feature>.
- Fixed <issue>.

## v1.0.0 — 2026-05-08

- Initial release.
```

One `##` section per version. Keep entries short — this is a release record, not a commit log.

---

## Benchmark run-log archiving

After packaging a release, commit the benchmark run log alongside the artifact. The
benchmark harness (see `docs/benchmarks/` and `scripts/skill_benchmark.py` from the
`sprint/codex-frank-r1-benchmark-harness` branch) emits a `run-log-*.json` file. Store
it under `docs/benchmarks/run-logs/` so regressions are visible in the diff.

Naming convention: `run-log-<skill-name>-v<version>-<YYYYMMDD>.json`
