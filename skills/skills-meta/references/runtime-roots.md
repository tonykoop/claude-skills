# Runtime Roots

Use this reference to teach `skills-meta` where skills may be
organized, duplicated, or stale across machines and runtimes.

`skills-meta` should treat the manifest as canonical, then scan every root the
user provides. A root is only evidence of an installed or archived copy; it is
not automatically the source of truth.

## Known repo-local roots

- `skills/`
- `claude/skills/`
- `codex/skills/`
- `gemini/skills/` when the directory exists

## Example PC roots (WSL2 + Windows)

The following are example source or staging locations for a WSL2 + Windows
setup. Adapt to your own paths — these should be configured, not hard-coded:

- `/mnt/c/Users/<you>/Documents/GitHub/claude-skills/skills`
- `/mnt/c/Users/<you>/Documents/GitHub/claude-skills/claude/skills`
- `/mnt/c/Users/<you>/Documents/GitHub/claude-skills/codex/skills`
- `/mnt/c/Users/<you>/Documents/GitHub/instrument-maker/skills`
- `/mnt/c/Users/<you>/Documents/GitHub/makerspace`
- `/mnt/c/Users/<you>/Documents/GitHub/reverse-engineering/skills`
- `~/.codex/skills`

## Runtime install roots

Different products expose skills differently. Scan these when they exist:

- Claude Code project or user skills directories
- Claude Desktop / Cowork exported or installed skill folders
- Codex CLI `$CODEX_HOME/skills`
- Codex Desktop skill folders or exported bundles
- Gemini CLI skill/plugin folders when a convention exists
- Zip/package staging folders such as Downloads or Quick Share

Do not assume mobile has a readable local filesystem. For mobile-only installs,
ask the user to export, paste, or provide the uploaded zip/manifest when a
direct scan is impossible.

## App-data note

The AppData package folders for Claude and Codex contain app state and session
data. They are useful provenance targets, but they were not skill-install roots
in the scan. Treat them as supporting paths, not canonical roots.

## Configured roots

Use either of these:

- repeated `--root` flags
- `SKILLS_META_ROOTS` with a path-list separator for the current platform

Examples:

```bash
python skills/skills-meta/scripts/skills-meta.py --root ~/.claude/skills --root ~/.codex/skills
```

```bash
SKILLS_META_ROOTS="~/.claude:~/.codex" \
  python skills/skills-meta/scripts/skills-meta.py
```

## Reporting note

If a root does not map cleanly to a runtime, label it as `configured` and print
the path. Do not guess.

## Sync audit behavior

When multiple copies of the same skill appear:

1. Prefer the manifest entry as canonical. The helper picks the copy
   whose path matches `manifest.skills.<name>.repo_path` when present;
   otherwise it falls back to the highest installed semver, then the
   newest `last-updated`, then the first record.
2. Report each discovered copy with path, runtime, version fields, and
   last-updated fields when present. Stale copies get tagged
   `duplicate` and carry a `duplicate-of:<path>` issue.
3. Flag missing frontmatter metadata separately from version drift.
4. Flag copies that are outside the manifest as `unknown`.
5. Do not delete or overwrite stale copies by default. The helper
   prints a cleanup plan; `fix-duplicates --apply` walks each removal
   interactively with a per-copy y/n prompt and never auto-deletes.

## Unreadable roots

When a manifest, `SKILLS_META_ROOTS`, or `--root` entry doesn't exist or
can't be read, the helper does not silently skip it. Instead it reports
the path, the origin (`manifest`, `env`, or `cli`), and a reason:

- `missing` — the path doesn't exist on this machine
- `not-a-directory` — the path resolves to a file or symlink target
- `permission-denied` — the path can't be listed
- `no-skills-found` — the directory exists but has no `SKILL.md` files

This is how mobile-only installs surface in the report. Treat an
unreadable root as a prompt to ask the user for an export, mount the
drive, or fix the path.

Default repo-local roots that don't exist (e.g. a fresh checkout with
no `gemini/skills/`) are skipped silently; that's normal, not drift.

## Sync targets

`--mode sync --target <path>` copies canonical skills from the manifest
into a target install root. Common targets:

- `~/.claude/skills` — Claude Code user skills directory
- `~/.codex/skills` — Codex CLI skills directory
- a repo-local `claude/skills/` or `codex/skills/` when staging portable
  bundles
- an exported zip staging directory before re-packaging

The source of truth is `manifest.skills.<name>.repo_path`. Skills with
no `repo_path` get a `source-missing` entry in the plan. The target is
not auto-detected per skill — pass `--target` explicitly. The same skill
may legitimately live in more than one install root (a `merge-review`
that drives both Claude Code and Codex CLI sprints, for example) and
the helper has no way to guess which runtime you mean.
