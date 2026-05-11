---
name: skills-meta
version: 1.0.0
last-updated: 2026-05-09
description: >-
  Audit installed skills across Claude, Codex, Gemini, and desktop installs.
  Compare frontmatter to manifest.yaml and report version drift, missing
  metadata, unreadable roots, or duplicate copies across roots. Can also sync
  canonical skills from manifest repo_path into a target install root (e.g.
  cross-install Claude-side skills into a Codex CLI skill folder). Use when
  asked what skills are installed, what version a skill is running, whether
  skills are up to date, to suggest frontmatter fixes, to clean up duplicate
  skill copies, or to make a skill available to another runtime on the same
  machine. Read-only by default; never rewrites, deletes, or copies without an
  explicit --apply flag.
---

# skills-meta

## Trigger phrases

- `what skills do I have?` / `list installed skills`
- `what version is [skill] running?`
- `are my skills up to date?` / `check for drift`
- `audit my skills` / `skills inventory`
- `suggest frontmatter fix for [skill]`

## Do not trigger for

- Editing or rewriting skills — treat that as a separate user-authorized task.
- Skill design or new skill creation — route to `skill-creator` if available.

Use this skill to answer "what skill versions am I running?" across Claude,
Codex, Gemini, and desktop installs.

Canonical skill version lives in `manifest.yaml`, not in this skill's
frontmatter.

## Default behavior

1. Inventory installed skills.
2. Compare each skill's `version` and `last-updated` frontmatter to
   `manifest.yaml`.
3. Report drift, missing metadata, unknown skills, and stale installs.
4. If asked for fixes, suggest a copy-pasteable frontmatter block only.

Do not edit installed skills unless the user explicitly asks for a separate
rewrite task.

## Scan roots

Prefer the bundled helper at `scripts/skills-meta.py` for deterministic scans.

Default roots:

- repo-local `skills/`
- `claude/skills/`
- `codex/skills/`
- `gemini/skills/` when present

Also honor `manifest.yaml` `install_roots` entries when present.

Desktop installs are user-configured. Accept roots via `SKILLS_META_ROOTS` or
`--root`.

## Modes

- Inventory: list every discovered skill with version, last-updated,
  runtime/root, and manifest status.
- Single-skill check: focus on one named skill and show installed vs
  canonical version.
- Drift check: surface only mismatches, missing skills, and stale dates.
- Frontmatter-fix: print a suggested frontmatter block, never apply it.
- Fix-duplicates: when a skill name appears at multiple roots, print a
  keep/remove plan. Default is dry-run; pass `--apply` to confirm each
  removal interactively. Never deletes without per-copy y/n.
- Sync: copy manifest skills from their canonical `repo_path` into a
  `--target` install root. Useful for cross-runtime install — e.g.
  making Claude-side skills (`merge-review`, `sprint-update`) available
  to a Codex CLI agent. Dry-run by default; `--apply` copies missing
  skills; `--apply --force` also overwrites targets that have drifted
  from the canonical source. Without `--force`, drifted targets are
  reported and skipped so local edits aren't clobbered silently.

## Sync workflow

Same-machine cross-runtime install. Source of truth is
`manifest.skills.<name>.repo_path`; target is whatever skill folder the
runtime expects (Claude Code: `~/.claude/skills`; Codex CLI:
`~/.codex/skills`; Codex Desktop: its skill bundle path; etc.).

Typical commands:

```bash
# Preview what would happen
python skills/skills-meta/scripts/skills-meta.py --mode sync \
  --target ~/.codex/skills --skill merge-review,sprint-update

# Land missing skills only (drifted targets get reported, not touched)
python skills/skills-meta/scripts/skills-meta.py --mode sync \
  --target ~/.codex/skills --skill merge-review,sprint-update --apply

# Also overwrite drifted targets after eyeballing the diff
python skills/skills-meta/scripts/skills-meta.py --mode sync \
  --target ~/.codex/skills --skill merge-review,sprint-update --apply --force
```

Omit `--skill` to operate on every manifest skill. Sync only knows about
skills listed in `manifest.skills`; unknown directories at the target
are left alone.

## Unreadable roots

When a manifest, `SKILLS_META_ROOTS`, or `--root` entry doesn't exist or
can't be read on this machine, the helper reports it as an unreadable
root with a reason (`missing`, `not-a-directory`, `permission-denied`,
`no-skills-found`). This is how mobile installs and unmounted drives
stay visible instead of silently skipping — when you see one, ask the
user for an export or check the path. Missing repo-local defaults stay
quiet on purpose; they're expected on a fresh checkout.

## Duplicate handling

The same skill can land at multiple roots (a portable copy in `skills/`
and an installed copy under `~/.claude/skills/`, for example). The helper
groups records by name and picks one canonical copy:

1. The path matching `manifest.skills.<name>.repo_path`, if any.
2. The highest installed semver.
3. The newest `last-updated` date.
4. Whichever record came first.

Other copies are tagged `duplicate` with a `duplicate-of:<path>` issue
and surfaced in inventory/drift output. Use `--mode fix-duplicates` to
print a keep/remove plan, or `--mode fix-duplicates --apply` to walk
each removal interactively.

## Output rules

- Keep reports short and mobile-friendly.
- One skill per line when possible.
- Prefer status tags like `ok`, `missing`, `drift`, `planned`,
  `unknown`, `duplicate`.
- Summarize counts first, then the top mismatches.
- If there are many results, cap the initial list and say how many were
  omitted.
- Show file paths only when they help resolve ambiguity.
- Always surface unreadable roots and duplicate counts in the summary.

## References

- [Manifest schema](references/manifest-schema.md)
- [Output examples](references/output-examples.md)
- [Runtime roots](references/runtime-roots.md)
