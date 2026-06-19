---
name: disk-cleanup
version: 1.1.0
last-updated: 2026-06-19
description: >-
  Weekly-to-biweekly disk recovery for a multi-worktree development setup.
  Runs `cargo clean` per worktree, prunes merged remote branches, cleans
  npm/pnpm caches, optionally prunes Docker, and prints (does NOT run) the
  PowerShell command needed to shrink a WSL2 VHDX. Defaults to `--dry-run`:
  reports what would be cleaned and estimated bytes freed. Destructive
  operations require `--apply`. Use when the user says "disk cleanup",
  "free up space", "clean cargo caches", "worktree is bloated", "shrink
  the WSL VHD", or "weekly cleanup".
---

# disk-cleanup — Weekly Recovery

A multi-worktree development setup with 7+ named persona worktrees, each
running its own `cargo build`, accumulates disk usage fast. This skill is
the periodic recovery routine — safe by default, runs `--dry-run` unless
explicitly told `--apply`, and never deletes branches with unmerged work.

Cadence: weekly to biweekly, manually invoked. No scheduler.

## What it does

1. **Worktree inventory.** Lists all `worktrees/*-<persona>` directories
   under `<workspace>/worktrees/` and their disk usage.
2. **`cargo clean` per worktree.** The biggest space hog in a Rust-heavy
   workspace. Each worktree typically holds 2-8 GB of `target/` debug
   artifacts.
3. **Merged-branch cleanup.** Lists local + remote branches that have been
   merged to `origin/main`. **Never deletes** branches with unmerged
   commits. **Never deletes** branches with active worktrees.
4. **Node-side caches.** `npm cache clean --force` and `pnpm store prune`
   (only if the relevant tools are installed).
5. **Optional Docker prune.** `docker system prune --volumes` only when
   `--include-docker` is passed (this can wipe build caches that take a
   long time to rebuild — opt-in only).
6. **WSL VHD shrink prompt.** **Does not** run `Optimize-VHD` directly —
   WSL cannot shrink its own backing VHD while running. Instead, prints
   the exact PowerShell command to run as Administrator from a Windows
   terminal, with the VHDX path resolved.
7. **Reports freed bytes** per step at the end.

## Defaults

- `--dry-run` is the default. Nothing is deleted; the skill reports
  estimates only.
- `--apply` enables the destructive operations: `cargo clean`, branch
  deletion, npm/pnpm cache clean.
- `--include-docker` adds `docker system prune --volumes` to the apply
  list (requires `--apply`).

## Usage

```bash
# Default: dry-run, see what would happen
tmux-sprint disk-cleanup

# Actually clean (does NOT include docker prune)
tmux-sprint disk-cleanup --apply

# Include docker prune
tmux-sprint disk-cleanup --apply --include-docker

# Just one worktree
tmux-sprint disk-cleanup --worktree core4-alice --apply

# Skip the merged-branch cleanup step
tmux-sprint disk-cleanup --apply --skip-branches

# JSON output for piping
tmux-sprint disk-cleanup --json
```

## Safety contract

These rules are non-negotiable. The skill enforces them in code, not just in
documentation.

### Never delete branches with unmerged work

Before deleting any branch:
1. Confirm `git branch --merged origin/main` includes the candidate.
2. Confirm `git log origin/main..<candidate>` is empty (no commits ahead).
3. Confirm no worktree currently has the branch checked out (`git worktree list`).

If any check fails, the branch is skipped with a clear reason. The skill
reports skipped branches at the end.

### Never delete branches associated with the active sprint

Branches matching `lane*` or `<persona>/<feature>` patterns referenced in the
current `<workspace>/docs/plans/persona-launch.generated.tsv` manifest are
treated as live and never deleted, regardless of merge state.

### Never run cargo clean on a worktree with uncommitted work

Before `cargo clean` in a worktree:
1. `git status --porcelain` must be empty (no uncommitted changes), OR
2. `--force` must be set (acknowledges that uncommitted build state may matter)

The default cargo clean targets only `target/debug/` — not `target/release/`,
which a sprint manager may have built recently for testnet deploys.

### Docker prune is strictly opt-in

`--include-docker` requires both `--apply` and explicit user invocation. The
warning shown beforehand:

```
WARNING: docker system prune --volumes will delete:
  - All stopped containers
  - All networks not used by containers
  - All volumes not used by at least one container
  - All dangling images and build caches

This typically reclaims 20–80GB but may invalidate hours of recent builds.
Continue? (--include-docker --confirm)
```

Adding `--confirm` is the third gate.

## WSL VHD shrink

WSL2 stores its filesystem in a VHDX file under your Windows user profile.
This file **only grows** during normal use; deleted files inside WSL show as
free space within the VHD but the VHDX on Windows stays large. To actually
reclaim the space, the VHD must be compacted while WSL is shut down.

WSL itself cannot do this — `Optimize-VHD` must run from elevated PowerShell
on Windows after `wsl --shutdown`. The skill **prints** the exact command
with your VHDX path resolved:

```
=== WSL VHD Shrink (Manual Step) ===

Your WSL2 distro 'Ubuntu' has a backing VHDX at:
  C:\Users\<you>\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu_*\LocalState\ext4.vhdx

Current size: 142.3 GB
Estimated reclaimable space (based on `df` inside WSL): ~24 GB

To shrink it, exit this skill, close all WSL windows, then in an
ELEVATED PowerShell window on Windows:

  wsl --shutdown
  Optimize-VHD -Path 'C:\Users\<you>\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu_*\LocalState\ext4.vhdx' -Mode Full

This may take 10–30 minutes for a 100+ GB VHDX. Don't interrupt it.
```

The skill itself never runs this — it can't, since it's running inside
WSL. The user copies the printed command and runs it from Windows.

## Output

Default report (after `--apply`):

```
=== disk-cleanup report ===

Worktrees cleaned: 7
  core4-alice          freed 4.2 GB (target/debug/)
  core4-frank          freed 3.8 GB (target/debug/)
  backend-bob          freed 1.2 GB (target/debug/)
  backend-elsa         freed 1.1 GB (target/debug/)
  frontend-cindy       freed 612 MB (node_modules/.cache/)
  frontend-gina        freed 508 MB (node_modules/.cache/)
  infra-dan            freed 89 MB (target/debug/)

Branches deleted: 18
  alice/round48-nonce-fix          (merged to origin/main)
  bob/issue-273-metrics-opt        (merged to origin/main)
  ... (16 more)

Branches skipped: 4
  alice/round53-current        (active in worktree)
  frank/round53-experiment     (unmerged commits)
  bob/feat-new-prefix-keys     (unmerged commits)
  cindy/wip-something          (uncommitted changes)

Caches cleaned:
  npm cache              freed 312 MB
  pnpm store             freed 1.4 GB

Docker:                  skipped (--include-docker not set)

WSL VHD shrink:          [printed PowerShell command — see above]

Total reclaimed:         12.6 GB (Linux side)
                         + ~24 GB potential after Optimize-VHD
```

## Trigger phrases

Invoke this skill when the user says any of:

- "disk cleanup" / "weekly cleanup" / "free up space"
- "clean cargo" / "cargo clean all worktrees"
- "worktree is bloated" / "running out of disk"
- "shrink the WSL VHD" / "optimize-vhd" / "vhdx is too big"
- "prune merged branches"

## Implementation status (v0.1)

The script implementing this skill (`scripts/disk-cleanup.sh`) is included
as a starter — see [`scripts/disk-cleanup.sh`](scripts/disk-cleanup.sh). It
implements the worktree inventory, cargo clean, merged-branch cleanup, and
the WSL VHD shrink command-printer. npm/pnpm cache clean and the Docker
prune step are stubs marked `# TODO`. PRs welcome.
