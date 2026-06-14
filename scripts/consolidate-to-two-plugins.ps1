# consolidate-to-two-plugins.ps1  (robust rescue + rebuild)
#
# Recovers from the broken state created by earlier runs:
#   - stale .git/index.lock blocking every git write
#   - local main diverged from origin/main (PR #179 was squash-merged)
#   - empty plugins/maker, plugins/coding folders littering the tree
#   - empty PR #180 (no commits, branch points at origin/main)
#
# What this does:
#   1. Removes stale .git/index.lock if present (refuses if a real git is running).
#   2. Resets working tree to current HEAD (drops all uncommitted edits).
#   3. Fetches origin and force-syncs local 'main' to origin/main.
#   4. Re-creates branch 'consolidate-to-two-plugins' from the fresh main.
#   5. Renames heifer-zephyr-maker -> maker, tony-eng-ops -> coding.
#   6. Folds tony-life skills into maker, skills-meta skill into coding.
#   7. Removes the empty tony-life/ and skills-meta/ plugin shells.
#   8. Rewrites marketplace.json, both plugin.json files, MARKETPLACE.md.
#   9. git add -A; prompts; commits; force-pushes (updates the empty PR #180).
#
# WARNING: step 2 + 3 are destructive. Anything uncommitted in the working
# tree, and any local commits on 'main' not in origin/main, will be lost.
# Right now you have nothing to lose -- the 595 skill files all live in
# origin/main and are safe.
#
# Run:
#   powershell -ExecutionPolicy Bypass -File `
#     "C:\Users\Tony\Documents\GitHub\claude-skills\scripts\consolidate-to-two-plugins.ps1"

$ErrorActionPreference = 'Stop'

$Repo = 'C:\Users\Tony\Documents\GitHub\claude-skills'
Set-Location $Repo

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Sanitize-PackedRefs {
    $p = Join-Path $Repo '.git\packed-refs'
    if (-not (Test-Path $p)) { return }
    $raw = Get-Content -Raw -LiteralPath $p
    if (-not $raw) { return }
    $kept = @()
    foreach ($line in ($raw -split "`r?`n")) {
        if ($line -match '^(#|\^[0-9a-f]{40}$|[0-9a-f]{40} refs/)') { $kept += $line }
    }
    $kept += ''
    [System.IO.File]::WriteAllText($p, ($kept -join "`n"))
}

function Remove-StaleLock {
    $lock = Join-Path $Repo '.git\index.lock'
    if (-not (Test-Path $lock)) { return }
    try {
        Remove-Item -Force $lock
        Write-Host "[clean] removed stale .git/index.lock"
    } catch {
        Write-Host ""
        Write-Host "ERROR: cannot remove .git/index.lock -- something is holding it open." -ForegroundColor Red
        Write-Host "Close any open instance of: VS Code, GitHub Desktop, JetBrains IDE," -ForegroundColor Yellow
        Write-Host "Sublime Merge, GitKraken. Also pause OneDrive / Google Drive sync"   -ForegroundColor Yellow
        Write-Host "and add C:\Users\Tony\Documents\GitHub\claude-skills\.git to your"    -ForegroundColor Yellow
        Write-Host "Windows Defender exclusion list. Then re-run this script."             -ForegroundColor Yellow
        exit 1
    }
}

function Write-Ascii {
    param([string]$Path, [string]$Content)
    $full = Join-Path $Repo $Path
    $parent = Split-Path -Parent $full
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    $normalized = $Content -replace "`r`n","`n"
    [System.IO.File]::WriteAllText($full, $normalized, [System.Text.UTF8Encoding]::new($false))
    Write-Host "[write] $Path"
}

function Move-Tracked {
    param([string]$Src, [string]$Dst)
    $srcAbs = Join-Path $Repo $Src
    $dstAbs = Join-Path $Repo $Dst
    if (-not (Test-Path $srcAbs)) {
        Write-Warning "[miss] $Src (already moved or never existed)"
        return
    }
    if (Test-Path $dstAbs) {
        $count = (Get-ChildItem $dstAbs -Force -ErrorAction SilentlyContinue | Measure-Object).Count
        if ($count -eq 0) {
            Remove-Item -Force $dstAbs
            Write-Host "[clean] removed empty $Dst before move"
        } else {
            Write-Warning "[skip] dest exists and is not empty: $Dst -- skipping move"
            return
        }
    }
    $dstParent = Split-Path -Parent $dstAbs
    if (-not (Test-Path $dstParent)) { New-Item -ItemType Directory -Force -Path $dstParent | Out-Null }
    & git mv $Src $Dst
    Write-Host "[mv]    $Src -> $Dst"
}

# ---------------------------------------------------------------------------
# 1. Pre-flight cleanup
# ---------------------------------------------------------------------------
Remove-StaleLock
Sanitize-PackedRefs

Write-Host "=== Current state ==="
$curBranchRaw = & git rev-parse --abbrev-ref HEAD
$curBranch = if ($curBranchRaw) { ($curBranchRaw | Out-String).Trim() } else { '' }
Write-Host "branch: $curBranch"
$status = & git status --short
$dirty = ($status | Measure-Object -Line).Lines
Write-Host "dirty entries: $dirty"
Write-Host ""
Write-Host "About to:"
Write-Host "  - git reset --hard HEAD            (drops uncommitted changes)"
Write-Host "  - git fetch origin"
Write-Host "  - git checkout main"
Write-Host "  - git reset --hard origin/main     (force-sync local main to remote)"
Write-Host "  - delete local branch 'consolidate-to-two-plugins' if present"
Write-Host "  - git checkout -b consolidate-to-two-plugins from main"
Write-Host "  - rename + fold the plugins"
Write-Host "  - commit and force-push (refreshes empty PR #180)"
Write-Host ""
$resp = Read-Host "Proceed with destructive reset and rebuild? (y/N)"
if ($resp -ne 'y' -and $resp -ne 'Y') {
    Write-Host "Aborted."
    exit 0
}

# ---------------------------------------------------------------------------
# 2. Reset working tree, then force-sync main to origin/main
# ---------------------------------------------------------------------------
Remove-StaleLock     # in case anything spawned one between steps
& git reset --hard HEAD
Write-Host "[reset] working tree = HEAD"

Remove-StaleLock
& git fetch origin
& git checkout main
Remove-StaleLock
& git reset --hard origin/main
Write-Host "[main]  local main = origin/main"

# Verify the marketplace layout exists on main
if (-not (Test-Path (Join-Path $Repo 'plugins\heifer-zephyr-maker'))) {
    Write-Host "ERROR: plugins/heifer-zephyr-maker not found on main." -ForegroundColor Red
    Write-Host "Has PR #179 actually been merged? Check git log on origin/main." -ForegroundColor Red
    exit 1
}

# ---------------------------------------------------------------------------
# 3. Branch
# ---------------------------------------------------------------------------
$branch = 'consolidate-to-two-plugins'
Remove-StaleLock
$existsLocal = & git branch --list $branch
if ($existsLocal) {
    & git branch -D $branch
    Write-Host "[branch] deleted stale local $branch"
}
Remove-StaleLock
& git checkout -b $branch
Write-Host "[branch] on $branch (from fresh main)"
Write-Host ""

# ---------------------------------------------------------------------------
# 4. Renames + folds
# ---------------------------------------------------------------------------
Remove-StaleLock
Move-Tracked 'plugins\heifer-zephyr-maker' 'plugins\maker'
Remove-StaleLock
Move-Tracked 'plugins\tony-eng-ops'        'plugins\coding'

Remove-StaleLock
Move-Tracked 'plugins\tony-life\skills\yoga-sequencer'   'plugins\maker\skills\yoga-sequencer'
Remove-StaleLock
Move-Tracked 'plugins\tony-life\skills\playlist-builder' 'plugins\maker\skills\playlist-builder'
Remove-StaleLock
Move-Tracked 'plugins\tony-life\skills\idea-incubator'   'plugins\maker\skills\idea-incubator'

Remove-StaleLock
Move-Tracked 'plugins\skills-meta\skills\skills-meta'    'plugins\coding\skills\skills-meta'

foreach ($d in @('plugins\tony-life','plugins\skills-meta')) {
    if (Test-Path (Join-Path $Repo $d)) {
        Remove-StaleLock
        & git rm -r --quiet $d
        Write-Host "[rm]    $d"
    }
}

# ---------------------------------------------------------------------------
# 5. Manifests
# ---------------------------------------------------------------------------
$marketplaceJson = @'
{
  "$schema": "https://claude.com/schemas/plugin-marketplace.json",
  "name": "tony-koop",
  "owner": {
    "name": "Tony Koop",
    "email": "tonykoop@gmail.com",
    "url": "https://github.com/tonykoop"
  },
  "description": "Tony Koop's skill marketplace. Two plugins: 'maker' for physical-world design and personal practice; 'coding' for software/engineering operations. Auto-updates from the claude-skills git repo.",
  "plugins": [
    {
      "name": "maker",
      "source": "./plugins/maker",
      "description": "Physical-world design and personal practice: instrument-maker, sheet-metal, maker-engineering, makerspace, laser-art, habitat-maker, reverse-engineer, sheet-music, yoga-sequencer, playlist-builder, idea-incubator.",
      "category": "making",
      "tags": ["instrument-design", "fabrication", "maker", "yoga", "music", "heifer-zephyr"]
    },
    {
      "name": "coding",
      "source": "./plugins/coding",
      "description": "Engineering operations and developer tooling: tmux-sprint, sprint-supervisor, sprint-update, merge-review, run-swarm, ci-triage, scaffold-hygiene, disk-cleanup, skills-meta.",
      "category": "engineering",
      "tags": ["sprint", "ci", "git", "wrfcoin", "internal-ops", "audit"]
    }
  ]
}
'@
Write-Ascii '.claude-plugin\marketplace.json' $marketplaceJson

$makerJson = @'
{
  "$schema": "https://claude.com/schemas/plugin.json",
  "name": "maker",
  "version": "1.0.0",
  "description": "Tony Koop's maker portfolio: instrument design, fabrication (CNC, laser, sheet-metal), shop-floor planning, wildlife habitat, reverse engineering, sheet music, plus personal-practice skills for yoga sequencing, playlist building, and idea capture.",
  "author": {
    "name": "Tony Koop",
    "email": "tonykoop@gmail.com",
    "url": "https://github.com/tonykoop"
  },
  "homepage": "https://github.com/tonykoop/claude-skills",
  "repository": "https://github.com/tonykoop/claude-skills",
  "license": "MIT",
  "keywords": [
    "instrument-design","maker","cnc","laser","sheet-metal","acoustic",
    "habitat","yoga","music","heifer-zephyr"
  ],
  "skills": ["skills"]
}
'@
Write-Ascii 'plugins\maker\.claude-plugin\plugin.json' $makerJson

$codingJson = @'
{
  "$schema": "https://claude.com/schemas/plugin.json",
  "name": "coding",
  "version": "1.0.0",
  "description": "Engineering operations: tmux multi-pane sprint orchestration, PR review, sprint supervision, GitHub-Queue sync, swarm dispatch, CI triage, scaffold hygiene, disk cleanup, and the skills-meta drift auditor.",
  "author": {
    "name": "Tony Koop",
    "email": "tonykoop@gmail.com",
    "url": "https://github.com/tonykoop"
  },
  "homepage": "https://github.com/tonykoop/claude-skills",
  "repository": "https://github.com/tonykoop/claude-skills",
  "license": "MIT",
  "keywords": ["sprint","tmux","ci","git","wrfcoin","internal-ops","audit","skills-meta"],
  "skills": ["skills"]
}
'@
Write-Ascii 'plugins\coding\.claude-plugin\plugin.json' $codingJson

$marketplaceMd = @'
# tony-koop marketplace

A Claude Code plugin marketplace backed by this repo. Two plugins:

| Plugin | What it does | Skills |
|---|---|---|
| `maker` | Physical-world design and personal practice | instrument-maker, sheet-metal, maker-engineering, makerspace, laser-art, habitat-maker, reverse-engineer, sheet-music, yoga-sequencer, playlist-builder, idea-incubator |
| `coding` | Engineering operations and developer tooling | tmux-sprint, sprint-supervisor, sprint-update, merge-review, run-swarm, ci-triage, scaffold-hygiene, disk-cleanup, skills-meta |

## Install (Claude Code CLI)

Add the marketplace once:

```text
/plugin marketplace add C:\Users\Tony\Documents\GitHub\claude-skills
```

You can also use a `file://` URL, or `https://github.com/tonykoop/claude-skills.git`
to pull from GitHub instead of the local checkout.

Then install whichever plugins you want:

```text
/plugin install maker@tony-koop
/plugin install coding@tony-koop
```

## Auto-update

Open the `/plugin` panel, find `tony-koop`, toggle **Auto-update** on. From
then on, every change pushed to `main` flows in next session with a
`/reload-plugins` prompt.

For managed/org-wide rollout, add to `~/.claude/managed-settings.json`:

```json
{
  "extraKnownMarketplaces": [
    {
      "name": "tony-koop",
      "source": "https://github.com/tonykoop/claude-skills.git",
      "autoUpdate": true
    }
  ]
}
```

## Versioning workflow

Each plugin has its own semver in `plugins/<plugin>/.claude-plugin/plugin.json`.
When you change a skill inside a plugin:

1. Bump the affected skill's `version` (in its `SKILL.md` or `manifest.yaml` entry).
2. Bump the *plugin's* `version` in `plugins/<plugin>/.claude-plugin/plugin.json`.
3. Commit, push. Users on auto-update see it on next session.

Reserve a major bump (e.g. `1.0.0` -> `2.0.0`) for breaking changes: skill
renames, removed skills, restructured plugin contents.

## Repo layout

```
claude-skills/
|-- .claude-plugin/
|   `-- marketplace.json
|-- plugins/
|   |-- maker/
|   |   |-- .claude-plugin/plugin.json
|   |   `-- skills/
|   |       |-- instrument-maker/
|   |       |-- sheet-metal/
|   |       `-- ... (11 skills)
|   `-- coding/
|       |-- .claude-plugin/plugin.json
|       `-- skills/
|           |-- tmux-sprint/
|           |-- skills-meta/
|           `-- ... (9 skills)
|-- claude/               # Claude-specific commands/hooks (not in any plugin yet)
|-- codex/                # Codex CLI skills (consumed directly by Codex)
|-- docs/
|-- manifest.yaml         # canonical version registry (still authoritative for SKILL versions)
`-- scripts/
```

## Cowork mode note

Cowork's Anthropic-bundled skills (docx, xlsx, pptx, pdf, etc.) live in a
separate session-scoped folder Cowork manages. This marketplace doesn't
touch those.
'@
Write-Ascii 'MARKETPLACE.md' $marketplaceMd

# ---------------------------------------------------------------------------
# 6. Stage, commit, force-push (updates empty PR #180)
# ---------------------------------------------------------------------------
Remove-StaleLock
& git add -A

Write-Host ""
Write-Host "=== git status (summary) ==="
& git status --short | Select-Object -First 30
Write-Host "(showing first 30 lines)"
Write-Host ""

$resp = Read-Host "Commit and force-push to PR #180? (y/N)"
if ($resp -ne 'y' -and $resp -ne 'Y') {
    Write-Host "Stopping before commit. Working tree has the consolidation; commit manually when ready."
    exit 0
}

Remove-StaleLock
& git commit -m "Consolidate marketplace to 2 plugins: maker and coding

- Rename plugins/heifer-zephyr-maker -> plugins/maker
- Rename plugins/tony-eng-ops          -> plugins/coding
- Fold tony-life (yoga-sequencer, playlist-builder, idea-incubator) into maker
- Fold skills-meta into coding
- Remove the now-empty tony-life and skills-meta plugin folders
- Refresh marketplace.json, both plugin.json files, and MARKETPLACE.md

Install:
  /plugin install maker@tony-koop
  /plugin install coding@tony-koop"

Remove-StaleLock
& git push --force-with-lease -u origin $branch

# PR #180 already exists pointing at this branch -- the push updates it
$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    Write-Host ""
    Write-Host "=== PR #180 ==="
    & gh pr view 180 --json url,state,title,additions,deletions
}

Write-Host ""
Write-Host "Done. After review + merge:"
Write-Host "  /plugin marketplace update tony-koop"
Write-Host "  /plugin install maker@tony-koop"
Write-Host "  /plugin install coding@tony-koop"
