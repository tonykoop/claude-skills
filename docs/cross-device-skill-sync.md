# Cross-Device Skill Sync

This workflow keeps skill copies aligned across the source repo, CLI installs,
desktop installs, laptops, and review-only contexts where the installed files
are not directly readable.

## Source Of Truth

Treat this repo as canonical.

1. Update the skill in its repo path:
   - portable skills: `skills/<skill-name>/`
   - Claude-specific skills: `claude/skills/<skill-name>/`
   - Codex-specific skills: `codex/skills/<skill-name>/`
   - Gemini-specific skills, when present: `gemini/skills/<skill-name>/`
2. Update `manifest.yaml` whenever the canonical version, status, or repo path
   changes.
3. Tag the repo before building a distributable artifact. Tags are namespaced by
   skill, for example `skills-meta/v1.0.0`.
4. Build install artifacts from the tag, not from an uncommitted worktree.
5. Install or upload the artifact into each runtime.
6. Run a drift check and record which runtimes could not be inspected directly.

Use private paths only as local examples. The workflow should work anywhere a
repo clone, install directory, or exported zip can be provided.

## What To Sync

Sync the whole skill directory, including:

- `SKILL.md`
- `references/`
- `assets/`
- `scripts/`
- `agents/`
- `evals/` only when the runtime or review workflow needs local evaluation

Do not copy runtime secrets, auth files, caches, session state, local persona
memory, or generated build output into a skill artifact.

## Install Targets

| Target | Install or review location | Check method |
| --- | --- | --- |
| Claude Code | project or user `.claude/skills/<skill-name>/` | `scripts/skill-sync-check.sh --root <path>` |
| Claude Desktop / Cowork | exported or installed skill folder, when visible | scan the folder, or inspect an exported zip |
| Codex CLI | `${CODEX_HOME:-~/.codex}/skills/<skill-name>/` | `scripts/skill-sync-check.sh` |
| Codex Desktop | configured desktop skill folder or exported bundle | scan the folder, or inspect an exported zip |
| Gemini CLI | configured Gemini skill/plugin folder | `scripts/skill-sync-check.sh --root <path>` |
| Laptop clone | local clone of this repo plus runtime install roots | run from the clone and pass laptop-specific roots |
| Review-only or mobile-adjacent | uploaded zip, pasted manifest, screenshot, or exported files | compare package contents to `manifest.yaml`; mark unreadable installs as unverified |

Mobile and review-only contexts often cannot expose a readable filesystem. In
that case, ask for an export, uploaded zip, pasted `SKILL.md` frontmatter, or a
screenshot of the runtime's skill details. Record the result as `unverified`
rather than pretending the check passed.

## Repeatable Check

From the repo root:

```bash
scripts/skill-sync-check.sh
```

This is read-only. It scans repo-local skills plus common local runtime roots
that exist on the current machine. Add explicit roots for desktop exports,
laptop installs, or staging folders:

```bash
scripts/skill-sync-check.sh \
  --root ~/.claude/skills \
  --root ~/.codex/skills \
  --root /path/to/desktop/export
```

For a single skill:

```bash
scripts/skill-sync-check.sh --skill skills-meta
```

For a compact full inventory:

```bash
scripts/skill-sync-check.sh --mode inventory
```

The checker delegates drift detection to `skills/skills-meta/scripts/skills-meta.py`.
`skills-meta` should report:

- one line per discovered skill copy;
- path and inferred runtime or `configured` for extra roots;
- installed `version` and `last-updated` frontmatter;
- canonical version and freshness from `manifest.yaml`;
- `missing`, `unknown`, `planned`, or `drift` status when the copy is not clean;
- missing local manifest entries separately from stale installed copies.

## Sync Plan

Before copying a skill into an install root:

1. Confirm the canonical skill path from `manifest.yaml`.
2. Confirm the target runtime install root.
3. Run the drift check against both source and target.
4. Inspect target-only files before copying.
5. Copy from a tagged artifact or clean checkout.
6. Run the drift check again.

When `rsync` is available, preview the copy first:

```bash
rsync -ani --delete --exclude '.git/' skills/skills-meta/ ~/.codex/skills/skills-meta/
```

Review any lines that would delete or overwrite files. Then run the real command
only after the preview is understood:

```bash
rsync -a --delete --exclude '.git/' skills/skills-meta/ ~/.codex/skills/skills-meta/
```

If `rsync` is not available, copy into a new staging directory first, compare it
with the target, and only replace the target after reviewing the diff.

## Overwrite Guard

Never overwrite target-only files silently.

Before sync, check for files in the target that are absent from the source. With
`rsync`, target-only files appear in the dry run as deletes when `--delete` is
present. Without `rsync`, use a temporary comparison:

```bash
diff -qr skills/skills-meta/ ~/.codex/skills/skills-meta/
```

If the target has local notes, experiments, untracked scripts, or generated
artifacts, pause and choose one of these outcomes:

- move them into a local backup outside the install root;
- promote them into the canonical repo with a normal review;
- leave the target unsynced and mark it as drifted;
- copy only non-conflicting files and record the exception.

For install roots that are also Git worktrees, run:

```bash
git -C <install-root-or-repo> status --short
```

Do not copy over untracked or modified files until the operator has reviewed
them.

## Tagged Artifact Example

Build a portable zip from a tag:

```bash
git archive --format=zip \
  --prefix=skills-meta/ \
  -o dist/skills-meta-v1.0.0.zip \
  skills-meta/v1.0.0:skills/skills-meta
```

For runtime-specific skills, use the runtime path in the archive command, for
example `tmux-v2/v2.0.0:codex/skills/tmux-v2`.

## Laptop And Desktop Notes

- Keep laptop clones synchronized through Git first, then install from the
  checked-out repo or tagged zip.
- Treat desktop app installs as deployment targets, not editing targets. If a
  desktop copy has useful changes, bring them back into the repo as a normal
  change before syncing elsewhere.
- Keep `SKILLS_META_ROOTS` or repeated `--root` flags in the operator's local
  notes for any machine-specific install roots.
- Desktop and mobile exports should be checked as artifacts even when the live
  runtime cannot be scanned.

## Pass Criteria

A sync pass is complete when:

- the repo tag or commit is recorded;
- every readable runtime root was scanned;
- every unreadable runtime was marked `unverified` with the fallback evidence
  used;
- every drift item has an action: updated, backed up, intentionally stale, or
  follow-up issue;
- no target-only files were overwritten without review.

## Platform Smoke Notes

Tested on WSL2 (Ubuntu on Windows). Expected behavior on other platforms:

- **macOS**: `~/.claude/skills/` and `~/.codex/skills/` resolve correctly;
  `rsync` is available by default. `skill-sync-check.sh` should run without
  modification.
- **Windows (PowerShell)**: `skill-sync-check.sh` requires WSL or Git Bash.
  Use `scripts/package_skill.ps1` for packaging; manual copy with Explorer or
  `robocopy` for installs. Drift check from WSL works when the Windows paths
  are mounted under `/mnt/c/`.
- **Codex Desktop / Claude Desktop**: install roots are typically inside the
  app container and not directly readable from the host shell. Use the
  exported zip or pasted `SKILL.md` fallback as described above.
- **Mobile / review-only**: no shell access. Use the exported zip + manifest
  comparison method; record as `unverified`.

## Known Gaps

- **No automated sync**: `skill-sync-check.sh` is read-only and reports drift;
  it does not copy files. A `--apply` mode for safe automated sync is not
  yet implemented (tracked separately in `skills-meta.py --apply` design).
- **Gemini CLI root not confirmed**: the Gemini CLI install root path is
  documented as a placeholder; the actual path depends on the Gemini CLI
  version and has not been smoke-tested.
- **Desktop app containers**: Claude Desktop and Codex Desktop skill roots
  inside app sandboxes cannot be read from the host without export; the
  workflow relies on manual export steps with no automated verification.
- **No tag enforcement**: the workflow documents tagging before artifact
  builds but does not enforce it; `package_skill.sh` accepts `--allow-dirty`
  which bypasses the clean-tag requirement.
