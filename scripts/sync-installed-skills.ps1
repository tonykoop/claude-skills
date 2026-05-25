# sync-installed-skills.ps1
# Syncs canonical Claude skills from this repo's skills/ folder into the
# active Cowork skills-plugin install root.
#
# Behavior:
#   - DELETES instrument-maker-v4 (retired/renamed to instrument-maker)
#   - REPLACES each installed skill that exists in canonical with the canonical copy
#   - INSTALLS canonical skills that aren't yet present in the install root
#   - LEAVES UNTOUCHED any installed skill not in canonical (e.g. Anthropic-bundled
#     docx, xlsx, pptx, pdf, schedule, setup-cowork, skill-creator,
#     web-artifacts-builder, canvas-design, consolidate-memory, yoga-playlist-builder)
#
# Run from PowerShell (from anywhere — paths are absolute):
#   powershell -ExecutionPolicy Bypass -File "C:\Users\Tony\Documents\GitHub\claude-skills\scripts\sync-installed-skills.ps1"

$ErrorActionPreference = 'Stop'

$Canonical   = 'C:\Users\Tony\Documents\GitHub\claude-skills\skills'
$InstallRoot = 'C:\Users\Tony\AppData\Roaming\Claude\local-agent-mode-sessions\skills-plugin\9d425966-e293-4e22-9de1-f950c9e47542\8346fc79-3da6-4b3a-99be-0efde9901f44\skills'

Write-Host "Canonical:  $Canonical"
Write-Host "Install:    $InstallRoot"
Write-Host ""

if (-not (Test-Path $Canonical))   { throw "Canonical path not found: $Canonical" }
if (-not (Test-Path $InstallRoot)) { throw "Install root not found: $InstallRoot" }

# --- 1. Retire instrument-maker-v4 -----------------------------------------
$retired = Join-Path $InstallRoot 'instrument-maker-v4'
if (Test-Path $retired) {
    Write-Host "[RETIRE] instrument-maker-v4 (renamed -> instrument-maker)"
    Get-ChildItem $retired -Recurse -Force | ForEach-Object {
        try { $_.Attributes = 'Normal' } catch { }
    }
    Remove-Item $retired -Recurse -Force
} else {
    Write-Host "[SKIP]   instrument-maker-v4 (already absent)"
}

# --- 2. Sync each canonical skill ------------------------------------------
$canonicalSkills = Get-ChildItem -Directory $Canonical | Where-Object {
    Test-Path (Join-Path $_.FullName 'SKILL.md')
}

foreach ($skill in $canonicalSkills) {
    $name = $skill.Name
    $src  = $skill.FullName
    $dst  = Join-Path $InstallRoot $name

    if (Test-Path $dst) {
        Get-ChildItem $dst -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
            try { $_.Attributes = 'Normal' } catch { }
        }
        Remove-Item $dst -Recurse -Force
        Write-Host "[UPDATE]  $name"
    } else {
        Write-Host "[INSTALL] $name"
    }

    Copy-Item -Path $src -Destination $dst -Recurse -Force
}

# Skills in canonical without a SKILL.md (e.g. WIP "houseplant") are reported, not installed
$skipped = Get-ChildItem -Directory $Canonical | Where-Object {
    -not (Test-Path (Join-Path $_.FullName 'SKILL.md'))
}
foreach ($s in $skipped) {
    Write-Host "[WIP-SKIP] $($s.Name) (no SKILL.md in canonical)"
}

Write-Host ""
Write-Host "Done. Restart Cowork mode for skill changes to take effect."
