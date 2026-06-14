# migrate-to-marketplace.ps1
#
# One-shot restructure of the claude-skills repo into a Claude Code
# plugin marketplace layout. Idempotent: safe to re-run.
#
# What it does:
#   1. Fixes a known .git/packed-refs corruption (truncated last line).
#   2. Cleans up sandbox test artifacts (.write-test, test-dir/) if present.
#   3. Creates branch  marketplace-restructure  (or checks out if it exists).
#   4. Moves skill folders into the new plugins/<plugin>/skills/<skill>/ layout:
#        - heifer-zephyr-maker:  instrument-maker, maker-engineering, makerspace,
#                                sheet-metal, laser-art, habitat-maker,
#                                reverse-engineer, sheet-music
#        - tony-life:            idea-incubator, yoga-sequencer, playlist-builder
#        - tony-eng-ops:         tmux-sprint (v2.3.1 from claude/skills),
#                                merge-review (newer from skills/),
#                                sprint-supervisor, run-swarm, ci-triage,
#                                scaffold-hygiene, sprint-update, disk-cleanup
#        - skills-meta:          skills-meta
#   5. Stages all changes (git tracks renames automatically when source+dest
#      share enough content), commits, pushes, and opens a PR via gh CLI if
#      available. Leaves codex/* and houseplant/ untouched.
#
# Run:
#   powershell -ExecutionPolicy Bypass -File `
#     "C:\Users\Tony\Documents\GitHub\claude-skills\scripts\migrate-to-marketplace.ps1"

$ErrorActionPreference = 'Stop'

$Repo = 'C:\Users\Tony\Documents\GitHub\claude-skills'
Set-Location $Repo

# ---------------------------------------------------------------------------
# 1. Fix .git/packed-refs (last line was truncated mid-ref by an interrupted
#    pack-refs run; git complains "unterminated line in .git/packed-refs").
# ---------------------------------------------------------------------------
$packedRefs = Join-Path $Repo '.git\packed-refs'
if (Test-Path $packedRefs) {
    $raw = Get-Content -Raw -LiteralPath $packedRefs
    $lines = $raw -split "`r?`n"
    $kept = @()
    foreach ($line in $lines) {
        # A valid packed-refs line is either:
        #   - "# pack-refs with: ..." header
        #   - "<40-hex-sha> refs/..."
        #   - "^<40-hex-sha>"   (peeled tag)
        # Drop anything that doesn't match -- that includes the truncated tail.
        if ($line -match '^(#|\^[0-9a-f]{40}$|[0-9a-f]{40} refs/)') {
            $kept += $line
        }
    }
    $kept += ''  # trailing newline
    [System.IO.File]::WriteAllText($packedRefs, ($kept -join "`n"))
    Write-Host "[fix] .git/packed-refs sanitized"
} else {
    Write-Host "[skip] no .git/packed-refs (loose refs only)"
}

# ---------------------------------------------------------------------------
# 2. Clean up sandbox test artifacts
# ---------------------------------------------------------------------------
foreach ($cruft in @('.write-test','test-dir')) {
    $p = Join-Path $Repo $cruft
    if (Test-Path $p) {
        Remove-Item -Recurse -Force $p
        Write-Host "[clean] removed $cruft"
    }
}

# ---------------------------------------------------------------------------
# 3. Branch
# ---------------------------------------------------------------------------
$branch = 'marketplace-restructure'
$currentRaw = & git rev-parse --abbrev-ref HEAD
$current = if ($currentRaw) { ($currentRaw | Out-String).Trim() } else { '' }
if ($current -ne $branch) {
    $existsRaw = & git branch --list $branch
    if ($existsRaw) {
        & git checkout $branch
    } else {
        & git checkout -b $branch
    }
}
Write-Host "[branch] on $branch"

# ---------------------------------------------------------------------------
# 4. Move skills into plugin folders
# ---------------------------------------------------------------------------
# Each entry: source path (relative to repo) -> destination path (relative)
$moves = @(
    # heifer-zephyr-maker
    @{ src = 'skills\instrument-maker';   dst = 'plugins\heifer-zephyr-maker\skills\instrument-maker' },
    @{ src = 'skills\maker-engineering';  dst = 'plugins\heifer-zephyr-maker\skills\maker-engineering' },
    @{ src = 'skills\makerspace';         dst = 'plugins\heifer-zephyr-maker\skills\makerspace' },
    @{ src = 'skills\sheet-metal';        dst = 'plugins\heifer-zephyr-maker\skills\sheet-metal' },
    @{ src = 'skills\laser-art';          dst = 'plugins\heifer-zephyr-maker\skills\laser-art' },
    @{ src = 'skills\habitat-maker';      dst = 'plugins\heifer-zephyr-maker\skills\habitat-maker' },
    @{ src = 'skills\reverse-engineer';   dst = 'plugins\heifer-zephyr-maker\skills\reverse-engineer' },
    @{ src = 'skills\sheet-music';        dst = 'plugins\heifer-zephyr-maker\skills\sheet-music' },

    # tony-life
    @{ src = 'skills\idea-incubator';     dst = 'plugins\tony-life\skills\idea-incubator' },
    @{ src = 'skills\yoga-sequencer';     dst = 'plugins\tony-life\skills\yoga-sequencer' },
    @{ src = 'skills\playlist-builder';   dst = 'plugins\tony-life\skills\playlist-builder' },

    # tony-eng-ops -- for tmux-sprint and merge-review, prefer the claude/skills
    # (newer) version where it exists; otherwise use shared /skills.
    @{ src = 'claude\skills\tmux-sprint'; dst = 'plugins\tony-eng-ops\skills\tmux-sprint' },
    @{ src = 'skills\merge-review';       dst = 'plugins\tony-eng-ops\skills\merge-review' },
    @{ src = 'skills\sprint-supervisor';  dst = 'plugins\tony-eng-ops\skills\sprint-supervisor' },
    @{ src = 'skills\run-swarm';          dst = 'plugins\tony-eng-ops\skills\run-swarm' },
    @{ src = 'skills\ci-triage';          dst = 'plugins\tony-eng-ops\skills\ci-triage' },
    @{ src = 'skills\scaffold-hygiene';   dst = 'plugins\tony-eng-ops\skills\scaffold-hygiene' },
    @{ src = 'claude\skills\sprint-update'; dst = 'plugins\tony-eng-ops\skills\sprint-update' },
    @{ src = 'claude\skills\disk-cleanup';  dst = 'plugins\tony-eng-ops\skills\disk-cleanup' },

    # skills-meta
    @{ src = 'skills\skills-meta';        dst = 'plugins\skills-meta\skills\skills-meta' }
)

# Folders to delete after their contents are moved (older duplicates):
#   skills\tmux-sprint           (claude/skills version is newer; this dupe goes away)
#   claude\skills\merge-review   (skills/ version is newer)
$dedupeAfter = @(
    'skills\tmux-sprint',
    'claude\skills\merge-review'
)

foreach ($m in $moves) {
    $src = Join-Path $Repo $m.src
    $dst = Join-Path $Repo $m.dst

    if (-not (Test-Path $src)) {
        if (Test-Path $dst) {
            Write-Host "[ok]   already moved: $($m.dst)"
        } else {
            Write-Warning "[miss] source not found and dest not present: $($m.src)"
        }
        continue
    }
    if (Test-Path $dst) {
        Write-Warning "[skip] dest already exists, leaving source in place: $($m.dst)"
        continue
    }

    $dstParent = Split-Path -Parent $dst
    if (-not (Test-Path $dstParent)) {
        New-Item -ItemType Directory -Force -Path $dstParent | Out-Null
    }

    & git mv $m.src $m.dst
    Write-Host "[mv]   $($m.src) -> $($m.dst)"
}

foreach ($d in $dedupeAfter) {
    $p = Join-Path $Repo $d
    if (Test-Path $p) {
        # Remove via git rm so the deletion is staged.
        & git rm -r --quiet $d
        Write-Host "[rm]   dropped duplicate: $d"
    }
}

# ---------------------------------------------------------------------------
# 5. Stage marketplace + plugin manifests (in case they aren't tracked yet)
# ---------------------------------------------------------------------------
& git add .claude-plugin\marketplace.json | Out-Null
& git add plugins\*\.claude-plugin\plugin.json | Out-Null

# Show what's about to be committed
Write-Host ""
Write-Host "=== git status ==="
& git status --short
Write-Host ""

$response = Read-Host "Commit and push these changes? (y/N)"
if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "Stopping before commit. Re-run when ready, or commit manually."
    exit 0
}

# ---------------------------------------------------------------------------
# 6. Commit + push + PR
# ---------------------------------------------------------------------------
& git commit -m "Restructure repo into Claude Code plugin marketplace layout

- Add .claude-plugin/marketplace.json defining the 'tony-koop' marketplace
- Add 4 plugins under plugins/: heifer-zephyr-maker, tony-life, tony-eng-ops, skills-meta
- Move skill folders from skills/ and claude/skills/ into the new plugin layout
- Keep newer of duplicate skills (tmux-sprint v2.3.1 from claude/skills; merge-review from skills/)
- Leave codex/* and houseplant/ untouched

Install with:
  /plugin marketplace add C:\Users\Tony\Documents\GitHub\claude-skills"

& git push -u origin $branch

# Open PR if gh is available
$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    & gh pr create --fill --base main --head $branch
    Write-Host "[pr] PR opened"
} else {
    Write-Host "[note] gh CLI not found -- open the PR manually on GitHub."
}

Write-Host ""
Write-Host "Done. Next steps:"
Write-Host "  1. Review the PR diff."
Write-Host "  2. Merge to main."
Write-Host "  3. In Claude Code, run:"
Write-Host "       /plugin marketplace add C:\Users\Tony\Documents\GitHub\claude-skills"
Write-Host "  4. /plugin install heifer-zephyr-maker@tony-koop  (and others)"
