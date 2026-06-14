# verify-and-finish-marketplace.ps1
#
# Run after migrate-to-marketplace.ps1 to:
#   1. Show the actual state of the commit/push/PR
#   2. Add the files the migration script missed (MARKETPLACE.md and the
#      two helper scripts)
#   3. Amend the commit + force-push the branch
#   4. Open a PR if gh CLI is available
#
# The interactive "Should I try again?" prompts you saw are almost certainly
# Windows Defender (or OneDrive) holding .git file handles during git's
# post-push gc. They are NON-FATAL -- git retries cleanup on next operation.
# To stop them recurring, add C:\Users\Tony\Documents\GitHub to Windows
# Defender exclusions, or pause OneDrive on that folder.
#
# Run:
#   powershell -ExecutionPolicy Bypass -File `
#     "C:\Users\Tony\Documents\GitHub\claude-skills\scripts\verify-and-finish-marketplace.ps1"

$ErrorActionPreference = 'Stop'

$Repo = 'C:\Users\Tony\Documents\GitHub\claude-skills'
Set-Location $Repo

Write-Host "=== Current branch ==="
& git rev-parse --abbrev-ref HEAD
Write-Host ""
Write-Host "=== Last 3 commits ==="
& git log --oneline -3
Write-Host ""
Write-Host "=== git status ==="
& git status --short
Write-Host ""
Write-Host "=== Remote head ==="
& git ls-remote --heads origin marketplace-restructure
Write-Host ""

# Stage the files the migration script missed
$missing = @(
    'MARKETPLACE.md',
    'scripts\migrate-to-marketplace.ps1',
    'scripts\verify-and-finish-marketplace.ps1',
    'scripts\sync-installed-skills.ps1'
)

$toAdd = @()
foreach ($f in $missing) {
    if (Test-Path (Join-Path $Repo $f)) { $toAdd += $f }
}

if ($toAdd.Count -gt 0) {
    Write-Host "=== Staging files the migration script missed ==="
    foreach ($f in $toAdd) {
        & git add $f
        Write-Host "  added: $f"
    }
    Write-Host ""

    # Show the staged diff summary
    Write-Host "=== Staged changes ==="
    & git diff --cached --stat
    Write-Host ""

    $resp = Read-Host "Amend the previous commit with these files and force-push? (y/N)"
    if ($resp -eq 'y' -or $resp -eq 'Y') {
        & git commit --amend --no-edit
        & git push --force-with-lease origin marketplace-restructure
        Write-Host "[ok] amended + force-pushed"
    } else {
        Write-Host "Stopping. Files are staged; you can commit/push manually."
        exit 0
    }
} else {
    Write-Host "[ok] no missing files to stage"
}

# Try to open the PR
$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    Write-Host ""
    Write-Host "=== PR status ==="
    $existingPR = & gh pr list --head marketplace-restructure --json number,url,state 2>$null
    if ($existingPR -and $existingPR -ne '[]') {
        Write-Host "PR already exists:"
        Write-Host $existingPR
    } else {
        Write-Host "Opening PR..."
        & gh pr create --fill --base main --head marketplace-restructure
    }
} else {
    Write-Host "[note] gh CLI not found. Open the PR manually at:"
    Write-Host "  https://github.com/tonykoop/claude-skills/pull/new/marketplace-restructure"
}

Write-Host ""
Write-Host "Done."
