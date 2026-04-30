Pull all git repositories in the workspace from their current branch's remote, then update all semi-permanent persona worktrees to match their repo's latest main.

Run the pull-all.sh script:

```bash
./.claude/commands/pull-all.sh
```

Report which repos were updated and which were already up to date.

Worktree update logic:
- **Detached HEAD** (idle): advance to latest `origin/main`
- **On main**: pull
- **On a feature branch**: skip (active persona work)
- **Dirty**: skip (uncommitted changes)
- **Listed in `persona-launch.generated.tsv`**: skip (active sprint dispatch)
- **`.sprint-active` marker present**: skip
