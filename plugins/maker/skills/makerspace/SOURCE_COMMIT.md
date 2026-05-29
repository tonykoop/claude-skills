# Snapshot provenance

This portable skill package is a snapshot of the standalone
[`tonykoop/makerspace`](https://github.com/tonykoop/makerspace) repo,
trimmed for cross-platform install (Claude Code/Desktop, Codex
CLI/Desktop, Gemini CLI, mobile zip-upload).

## Source of truth

- Standalone repo: `https://github.com/tonykoop/makerspace`
- Snapshot taken: 2026-05-08
- Standalone HEAD at snapshot time: `ee5b0a4e914c17eb9276092b8e3e4f006c0f1f8b`
- Snapshot also includes uncommitted working-tree changes from the
  standalone repo as of 2026-05-08 (the round-1-eval revisions to
  `SKILL.md`, the new `agents/openai.yaml`, the
  `assets/templates/shop-equipment-profile.yaml`, and reference-doc
  updates listed in
  `docs/handoffs/2026-05-08-claude-cross-platform-review/05-makerspace.md`).
  These should land on standalone `main` once the cross-platform review is
  merged so the next snapshot can be taken cleanly from a committed SHA.

## Excluded from the snapshot

- `evals/workspace/` (1.3 MB legacy v0.2 benchmark) — moved to
  `docs/benchmarks/makerspace/` in the host repo to keep the package
  small for mobile installs. Standalone repo keeps the original copy.
- `catalog.sqlite`, `catalog.sqlite-journal`, `dream-log.md` — runtime
  artifacts that should be regenerated rather than shipped.
- `__pycache__/` and `*.pyc` — Python bytecode.
- Repo-level docs (`README.md`, `getting-started.md`, `LICENSE`) — kept
  only in the standalone repo so the snapshot looks like a skill package
  rather than a checkout.

## How to re-sync

Run from the host repo root:

```bash
./scripts/sync_makerspace_snapshot.sh /path/to/standalone/makerspace
```

The script `rsync`s the whitelisted directories, refuses to clobber
unrelated files, prints the standalone HEAD SHA, and reminds you to
update this file. See the script for the authoritative ignore list.
