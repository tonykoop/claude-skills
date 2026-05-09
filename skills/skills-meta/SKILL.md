---
name: skills-meta
description: >-
  Audit installed skills, compare frontmatter to manifest.yaml, and report
  version drift or missing metadata. Use when asked what skills are
  installed, what version a skill is running, whether skills are up to date,
  or to suggest frontmatter fixes. Read-only by default; never rewrite
  installed skills automatically.
---

# skills-meta

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
