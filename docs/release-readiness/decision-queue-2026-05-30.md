# Morning Human-Decision Queue — 2026-05-30

Source: `run-swarm` issue-scout run, 2026-05-29 (Refs #188).
JSON artifacts expired from `/tmp/`; regenerate via `/run-swarm` if needed.

This document stages all 10 items requiring owner judgment, grouped by type, with ready-to-run implementation commands for the infra items and implementation templates for the others. Check off each item as you address it.

---

## ⚖️ Legal / IP  *(highest priority — public-distribution risk)*

### 1. tongue-drum — copyrighted WOOD magazine scans
- **Repo:** `tonykoop/tongue-drum`
- **Risk:** 5 full-page scans of "Tones-of-Fun Tongue Drum" plan (WOOD mag, Oct 2008). Wholesale reproduction is a fragile fair-use claim under US copyright. Risk activates the moment the repo goes public.
- **Decision:** Delete image files and replace with a citation block, OR confirm you have a license to reproduce and document it.

**Implementation after decision (delete-and-cite path):**
```bash
# From inside the tongue-drum repo
# 1. Find the scan files
find . -name "*.jpg" -o -name "*.png" -o -name "*.pdf" | grep -i "wood\|scan\|magazine" | sort

# 2. Remove them from git history (requires git-filter-repo)
pip install git-filter-repo  # if not installed
git filter-repo --invert-paths --path-glob '*wood*' --path-glob '*WOOD*' --path-glob '*scan*'

# 3. Add to .gitignore so they don't reappear
echo "# Copyrighted magazine scans — store locally, never commit" >> .gitignore
echo "scans/" >> .gitignore
echo "*.scan.jpg" >> .gitignore

# 4. Add citation block in README.md
```

**Citation block template:**
```markdown
## Source Plan

This project is based on: "Tones-of-Fun Tongue Drum," *WOOD Magazine*, October 2008.
Author: [confirm from byline]. ISSN: 0888-7497.
The original plan is not reproduced here; obtain a copy via [WOOD's back-issue archive or your local library].
```

---

### 2. cryptex — third-party design (John Giem) with no attribution
- **Repo:** `tonykoop/cryptex` (currently private)
- **Risk:** `cad/Cryptex/` ships `Craft_a_Cryptex_John_Giem.pdf` + demonstration photos alongside derived SolidWorks files. No attribution, no LICENSE. Blocks any public release or kit sale.
- **Decision required:**
  - Can Giem's plan be redistributed? (Check if it was published under CC or similar — the PDF's header may say. If commercial/all-rights-reserved, you cannot redistribute it.)
  - What license applies to your derived SolidWorks work? (Your files are derived from his plan → your license cannot be more permissive than his.)

**Implementation after decision (attribution-only path, if redistributable):**
```markdown
## Attribution

Cryptex design based on "Craft a Cryptex" by John Giem.
Original plan: [publication/URL/issue]. Used with permission / under [license].
My SolidWorks adaptation © [year] Tony Koop. [License for your derived work.]
```

**Implementation after decision (remove PDF, keep your derived work):**
```bash
git filter-repo --invert-paths --path 'cad/Cryptex/Craft_a_Cryptex_John_Giem.pdf'
# Add a NOTICE.md crediting Giem without redistributing his PDF
```

---

## ✍️ Portfolio narratives  *(only you can author — first-person engineering)*

These items are intentionally left as stubs. The scaffolding below is for reference once you're ready to write.

### 3. tumbler-oven — Diagnostic + Repair narratives
- **Repo:** `tonykoop/tumbler-oven` (or wherever the photos + NOTICE.md live)
- **Decision:** Write the "Diagnostic" and "Repair" sections. Photos and NOTICE.md scope already exist.

**Suggested outline:**
```markdown
## Diagnostic

*What failed, how I found it, what tools I used to confirm.*

- Symptom: [what the tumbler did / didn't do]
- Test: [continuity check? thermal runaway? motor draw?]
- Finding: [root cause — e.g. failed capacitor, worn bearing, seized drum shaft]

## Repair

*What I replaced/rebuilt and why.*

- Part: [part name, source, cost]
- Procedure: [brief step sequence]
- Result: [before/after — does it run now? any lingering caveats?]
```

---

### 4. suction-cup-mount — Hinge geometry + gel-layer interface reflections
- **Patent ref:** US Patent 11,137,017 B2
- **Decision:** Write the two reflections (~1–3 pages each).

**Suggested structure:**
```markdown
## Hinge Geometry Rationale

Why [specific hinge geometry] was chosen over [alternatives].
Key constraint: [load case, assembly tolerance, etc.].
Patent claim [N] covers [specific feature].

## Gel-Layer Interface

How the gel layer achieves [function].
Material selection rationale: [durometer, thickness, surface treatment].
Failure modes observed during testing: [list].
```

---

### 5. _meta/yoga → portfolio.html — Third practice tile
- **Decision:** Do you want to add a yoga/tarot tile to portfolio.html?
  - **Option A:** Add a third practice tile to the "Two Practices" hero (needs: title, 1-sentence description, link target, thumbnail).
  - **Option B:** Keep the 12-class curriculum local-only; don't surface it in the portfolio.

**If Option A:** Edit `portfolio.html`, add a `<div class="practice-tile">` block following the existing tile pattern.

---

## 🧹 Infra / Hygiene  *(implementation-ready after decision)*

### 6. cryptex — 32 binary blobs (≤11.5 MB) with no LFS
- **Repo:** `tonykoop/cryptex`
- **Decision:** Rewrite git history to remove old blobs (clean break, requires force-push, breaks existing clones), OR accept sunk cost and add LFS going forward only.

**Path A — Clean break (rewrite history):**
```bash
cd ~/Documents/GitHub/cryptex   # or wherever

# Install git-filter-repo if needed
pip install git-filter-repo

# Dry run: find all binary blobs over 1 MB in git history
git log --all --pretty=format:"%H" | xargs -I{} git diff-tree --no-commit-id -r {} | \
  grep -E '\.(stl|sldprt|sldasm|slddrw|STEP|step|STL|SLDPRT|SLDASM|SLDDRW)$' | \
  awk '{print $NF}' | sort -u | head -20

# Add LFS tracking first (so re-imported files go to LFS)
git lfs track "*.stl" "*.STL" "*.sldprt" "*.SLDPRT" "*.sldasm" "*.SLDASM" \
  "*.slddrw" "*.SLDDRW" "*.step" "*.STEP"
git add .gitattributes

# Rewrite history to convert blobs to LFS pointers
# WARNING: this rewrites all commits — inform collaborators before running
git lfs migrate import --above=1mb --everything

# Force-push (requires owner access, will break existing clones)
git push --force-with-lease --all
git push --force-with-lease --tags
```

**Path B — Sunk cost (LFS for future only):**
```bash
cd ~/Documents/GitHub/cryptex
git lfs track "*.stl" "*.STL" "*.sldprt" "*.SLDPRT" "*.sldasm" "*.SLDASM" \
  "*.slddrw" "*.SLDDRW" "*.step" "*.STEP"
git add .gitattributes
git commit -m "chore: add LFS tracking for CAD binary assets (going forward)"
git push
```

**Blob-size CI guard (add to `.github/workflows/ci.yml`):**
```yaml
- name: Reject large non-LFS commits
  run: |
    git diff HEAD~1 HEAD --name-only | while read f; do
      size=$(git cat-file -s HEAD:"$f" 2>/dev/null || echo 0)
      if [ "$size" -gt 5242880 ]; then  # 5 MB
        ext="${f##*.}"
        case "$ext" in
          stl|STL|sldprt|SLDPRT|step|STEP|sldasm|SLDASM)
            echo "ERROR: $f ($((size/1024/1024)) MB) is a binary CAD file not tracked by LFS."
            exit 1 ;;
        esac
      fi
    done
```

---

### 7. Stale sprint branches — 9 unmerged remote branches
- **Repos:** `tonykoop/zephyr-zither`, `tonykoop/handpan`, `tonykoop/bell-stack-chord-horn`, `tonykoop/cryptex`
- **Prefixes:** `r3/`, `r26/`, `r35b/`, `gpt55/`
- **Decision:** Review each branch; delete superseded ones, salvage any with unique work.

**Audit commands — run per repo:**
```bash
# List the stale-prefixed branches and their last commit date
for repo in zephyr-zither handpan bell-stack-chord-horn cryptex; do
  echo "=== $repo ==="
  gh api "repos/tonykoop/$repo/branches?per_page=100" | \
    python3 -c "
import json, sys
branches = json.load(sys.stdin)
stale_prefixes = ('r3/', 'r26/', 'r35b/', 'gpt55/')
for b in branches:
    if b['name'].startswith(stale_prefixes):
        print(f'  {b[\"name\"]}')"
done

# For each stale branch, check if it has unmerged commits vs main
# (replace REPO and BRANCH as needed)
gh api "repos/tonykoop/REPO/compare/main...BRANCH" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(f'ahead by {d[\"ahead_by\"]} commits')"
```

**Delete a branch (after confirming it's superseded):**
```bash
gh api -X DELETE "repos/tonykoop/REPO/git/refs/heads/BRANCH"
```

---

### 8. instrument-showcase manifest drift — 46 repos missing from library-manifest.json
- **Repo:** `tonykoop/instrument-showcase`
- **Current state:** `library-manifest.json` has 63 entries; ~109 instrument repos exist.
- **Decision:** Add a CI/automation trigger to regenerate the manifest after each sprint wave, OR regenerate manually now and leave it manual.

**Manual regeneration (one-time fix):**
```bash
# From inside the instrument-showcase repo
# Assumes a build_manifest.py script exists (create if not)
python3 scripts/build_manifest.py > library-manifest.json
git add library-manifest.json
git commit -m "chore: regenerate manifest — sync 109 instrument repos"
git push
```

**GitHub Actions trigger (add to `.github/workflows/update-manifest.yml`):**
```yaml
name: Regenerate instrument manifest
on:
  workflow_dispatch:  # manual trigger
  schedule:
    - cron: '0 9 * * 1'  # every Monday at 09:00 UTC (post-sprint)

jobs:
  regenerate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Regenerate manifest
        run: python3 scripts/build_manifest.py > library-manifest.json
      - name: Commit if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git diff --quiet library-manifest.json || \
            (git add library-manifest.json && \
             git commit -m "chore(manifest): auto-regenerate after sprint wave" && \
             git push)
```

---

## 🏷️ Readiness / scaffolding decisions

### 9. marimba — README rejects V5 status without asserting an L-level
- **Repo:** `tonykoop/marimba`
- **Decision:** Assign an explicit status label (suggested: `Status: L1` if only design sketches exist, `L2` if a build packet exists).
- **Implementation:** Edit `README.md` in the marimba repo, add a status badge:
  ```markdown
  **Status:** L1 — design sketch (no build packet yet)
  ```

---

### 10. chessboard-table — scaffold-only fabrication handoff
- **Repo:** `tonykoop/chessboard-table` (or under `instrument-maker`?)
- **Current state:** All dimensions are `?`, no `bom.csv` or cut-list or VOR exists.
- **Decision:** Complete the shop packet (dimensions + BOM + cut-list + VOR), OR keep as a review scaffold with an explicit `Status: design-capture` label.
- **Implementation:** If completing the packet, use the standard HWE instrument fabrication packet template from `plugins/maker/skills/idea-incubator/references/templates/hybrid-issue-template.md`.

---

## Processing order (recommended)

1. **Item 1 (tongue-drum IP)** — highest public-distribution risk; address before any public release.
2. **Item 2 (cryptex IP)** — second-highest; blocking kit/public release for cryptex.
3. **Item 6 (cryptex LFS)** — resolves alongside item 2; do both in the same session.
4. **Item 7 (stale branches)** — audit takes ~15 min; safe to batch across repos.
5. **Item 8 (manifest drift)** — one command + a GitHub Actions file; low effort.
6. **Items 9-10 (readiness labels)** — quick README edits; do last.
7. **Items 3-5 (narratives)** — unbounded writing work; schedule a dedicated session.
