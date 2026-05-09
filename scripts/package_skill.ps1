<#
.SYNOPSIS
    Package one skill from this repo into a deployable zip artifact.

.DESCRIPTION
    Reads manifest.yaml to locate the skill directory and canonical version,
    validates git state, and creates a zip in the dist/ directory (or -OutDir).

    Output filename: <skill-name>-v<version>.zip

.PARAMETER SkillName
    The skill key as it appears in manifest.yaml (required).

.PARAMETER DryRun
    Print what would be done without creating the zip.

.PARAMETER FromTag
    Check out this git tag, build the zip, then restore the previous HEAD.

.PARAMETER AllowDirty
    Skip the dirty working-tree check.

.PARAMETER OutDir
    Output directory. Default: dist/ under the repo root.

.EXAMPLE
    .\scripts\package_skill.ps1 skills-meta -DryRun
    .\scripts\package_skill.ps1 skills-meta
    .\scripts\package_skill.ps1 skills-meta -FromTag skills-meta/v1.0.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory, Position = 0)]
    [string]$SkillName,

    [switch]$DryRun,

    [string]$FromTag,

    [switch]$AllowDirty,

    [string]$OutDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot

if (-not $OutDir) {
    $OutDir = Join-Path $RepoRoot 'dist'
}

function Write-Info([string]$msg) { Write-Host "==> $msg" }
function Write-Err([string]$msg)  { Write-Error "error: $msg" }

# --- read manifest.yaml ---
$ManifestPath = Join-Path $RepoRoot 'manifest.yaml'
if (-not (Test-Path $ManifestPath)) {
    Write-Err "manifest.yaml not found at $RepoRoot"
}

$parseScript = @"
import sys, yaml
manifest_path, skill_name = sys.argv[1], sys.argv[2]
with open(manifest_path) as f:
    data = yaml.safe_load(f)
active = data.get('skills', {}) or {}
entry = active.get(skill_name)
if not entry:
    print('NOTFOUND', end='')
    sys.exit(1)
version = entry.get('canonical_version', '')
repo_path = entry.get('repo_path', '')
print(f'{version}|{repo_path}', end='')
"@

$manifestOut = python3 -c $parseScript $ManifestPath $SkillName
if ($LASTEXITCODE -ne 0) {
    Write-Err "skill '$SkillName' not found in manifest.yaml"
}

$parts   = $manifestOut -split '\|', 2
$Version  = $parts[0]
$RepoPath = $parts[1]

if (-not $Version)   { Write-Err "canonical_version missing for '$SkillName' in manifest.yaml" }
if (-not $RepoPath)  { Write-Err "repo_path missing for '$SkillName' in manifest.yaml" }

$SkillDir = Join-Path $RepoRoot $RepoPath
if (-not (Test-Path $SkillDir -PathType Container)) {
    Write-Err "skill directory not found: $SkillDir"
}

$ZipName = "${SkillName}-v${Version}.zip"
$ZipPath = Join-Path $OutDir $ZipName

# --- summary ---
Write-Info "skill:   $SkillName"
Write-Info "version: $Version"
Write-Info "source:  $SkillDir"
Write-Info "output:  $ZipPath"
if ($FromTag) { Write-Info "from-tag: $FromTag" }

if ($DryRun) {
    Write-Host "(dry run — no files written)"
    exit 0
}

# --- dirty-tree check ---
Push-Location $RepoRoot
try {
    if (-not $AllowDirty) {
        $dirty = git status --short 2>$null
        if ($dirty) {
            Write-Err "working tree is dirty. Commit or stash changes before packaging, or use -AllowDirty"
        }
    }

    # --- optional: check out a specific tag ---
    $SavedHead = $null
    if ($FromTag) {
        git fetch --tags --quiet
        $tagExists = git tag | Where-Object { $_ -eq $FromTag }
        if (-not $tagExists) { Write-Err "tag not found: $FromTag" }
        $SavedHead = git rev-parse --abbrev-ref HEAD
        Write-Info "checking out $FromTag"
        git checkout --quiet $FromTag
    }

    try {
        # --- build zip ---
        New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
        Write-Info "creating $ZipPath"
        Compress-Archive -Path $SkillDir -DestinationPath $ZipPath -Force
        $size = (Get-Item $ZipPath).Length
        Write-Info "done: $([math]::Round($size/1KB, 1)) KB written to $ZipPath"
    }
    finally {
        if ($SavedHead) {
            git checkout --quiet $SavedHead 2>$null
        }
    }
}
finally {
    Pop-Location
}
