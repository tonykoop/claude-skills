# Runtime Roots

Use this reference to teach `skills-meta` where Tony's skills may be
organized, duplicated, or stale across machines and runtimes.

`skills-meta` should treat the manifest as canonical, then scan every root the
user provides. A root is only evidence of an installed or archived copy; it is
not automatically the source of truth.

## Known repo-local roots

- `skills/`
- `claude/skills/`
- `codex/skills/`
- `gemini/skills/` when the directory exists

## Tony's common PC roots

These are common source or staging locations on Tony's main PC. They should be
configurable, not hard-coded forever:

- `/mnt/c/Users/Tony/Documents/GitHub/claude-skills/skills`
- `/mnt/c/Users/Tony/Documents/GitHub/claude-skills/claude/skills`
- `/mnt/c/Users/Tony/Documents/GitHub/claude-skills/codex/skills`
- `/mnt/c/Users/Tony/Documents/GitHub/instrument-maker/skills`
- `/mnt/c/Users/Tony/Documents/GitHub/makerspace`
- `/mnt/c/Users/Tony/Documents/GitHub/reverse-engineering/skills`
- `/home/tony/.codex/skills`

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

## Configured roots

Use either of these:

- repeated `--root` flags
- `SKILLS_META_ROOTS` with a path-list separator for the current platform

Examples:

```bash
python skills/skills-meta/scripts/skills-meta.py --root ~/.claude/skills --root ~/.codex/skills
```

```bash
SKILLS_META_ROOTS="~/.claude/skills:~/.codex/skills" \
  python skills/skills-meta/scripts/skills-meta.py
```

## Reporting note

If a root does not map cleanly to a runtime, label it as `configured` and print
the path. Do not guess.

## Sync audit behavior

When multiple copies of the same skill appear:

1. Prefer the manifest entry as canonical.
2. Report each discovered copy with path, runtime, version fields, and
   last-updated fields when present.
3. Flag missing frontmatter metadata separately from version drift.
4. Flag copies that are outside the manifest as `unknown`.
5. Do not delete or overwrite stale copies. Produce a cleanup checklist instead.
