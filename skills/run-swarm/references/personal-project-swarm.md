# Personal Project Swarm

Use this reference for Tony's personal `Documents/GitHub` workspace. It is
designed for musical instruments first, but also covers woodworking, crafts,
habitats, portfolio/career highlights, family/photo/story projects, and
presentation repos.

## Default Scope

Default to read-only audit plus issues or a manager report. Implementation is a
second phase that requires explicit manager approval, isolated worktrees, and
repo-specific PRs.

Recommended root:

```text
/mnt/c/Users/Tony/Documents/GitHub
```

## Eight Lenses

### 1. Instrument Acoustics And Validation

Best for: `instrument-maker`, individual instrument repos, sheet-music pairing.

Looks for:

- unverified tuning, scale, bore, string, reed, bridge, or membrane claims
- missing empirical validation loops
- DXF/image artifacts that are not fabrication authority
- prototype readiness overstated as production readiness
- missing measurement logs or L0-L4 readiness labels

Route to: `instrument-maker-v4`, `sheet-music`, `maker-engineering`.

### 2. CAD, Fabrication, And Shop Packets

Best for: woodworking, CNC, laser, SolidWorks, OpenSCAD, habitat builds.

Looks for:

- missing BOM/cut list/toolpath plan
- SVG-only outputs where DXF/CAD authority is needed
- no workholding, kerf, tolerance, or material notes
- build packets that cannot be handed to a shop or makerspace

Route to: `makerspace`, `instrument-maker-v4`, `habitat-maker`.

### 3. Documentation And Storytelling

Best for: design books, build logs, chapters, public repos.

Looks for:

- strong artifacts hidden in archives or `/tmp`
- missing README entry points
- no chapter/build-log structure
- unclear "why this matters" story
- confusing split between A/B blind outputs and combined deliverables

Route to: `idea-incubator`, `sprint-archive`, `instrument-maker-v4`.

### 4. Visual Assets And Presentation

Best for: image-gen-2, diagrams, isometric views, portfolio pages, build books.

Looks for:

- places where generated images would help explain design intent
- missing prompt sidecars or provenance notes
- generated visuals that imply false dimensions
- need for real photos, CAD renders, exploded views, or family-safe album design

Route to: `imagegen`, `instrument-maker-v4`, `idea-incubator`.

### 5. Repo Hygiene And Data Management

Best for: all 101+ GitHub repos.

Looks for:

- dirty repos, stale branches, stale lock files, duplicated skills
- large binary files without LFS
- bloated worktrees or generated artifacts committed in the wrong place
- missing `.gitignore`, manifest drift, or stale skill metadata

Route to: `skills-meta`, `disk-cleanup`, `sprint-update`.

### 6. Public Readiness, IP, And Privacy

Best for: public repo flips, patentable ideas, family/career material.

Looks for:

- private names/photos/locations accidentally headed public
- invention details that need a private patent packet first
- missing license/provenance/source ledgers
- public-facing claims that outrun evidence

Route to: `file-a-patent`, `idea-incubator`, `reverse-engineer`.

### 7. Backlog Triage And Promotion

Best for: idea captures, archived brainstorms, sprint queues.

Looks for:

- raw ideas ready for promote
- clusters that should become one scaffold issue
- issues that should stay open as source ideas
- next sprint queues with clear worktree/PR boundaries

Route to: `idea-incubator`, `tmux-sprint`, `merge-review`.

### 8. Career Highlights And Audience Fit

Best for: career portfolio, family/friends books, personal narrative projects.

Looks for:

- impressive work that is hard to explain to a nontechnical audience
- missing yearbook-style chapter structure
- opportunities for polished case studies, photo books, or highlight reels
- privacy boundaries and consent gates

Route to: `idea-incubator`, `imagegen`, `sprint-archive`.

## Issue Filing Rules

Before filing:

1. Search existing issues in the target repo.
2. Prefer `Refs` source issues when the source idea must stay open.
3. Use labels when available: `instrument`, `maker`, `capture`, `promote`,
   `skills`, `workflow`, `public-ready`, `privacy`, `documentation`.
4. Include concrete evidence: file path, archive folder, PR, or artifact.
5. Keep private/family details out of public issue bodies.

Title patterns:

```text
[swarm/instrument] Add empirical validation loop for <instrument>
[swarm/fabrication] Convert <repo> SVG packet to DXF-first build packet
[swarm/story] Promote <project> into a yearbook-style chapter
[swarm/hygiene] Add LFS/provenance guardrails for <repo>
```

## Manager Summary Template

```markdown
# Personal Project Swarm Summary

Root:
Mode:
Date:

| Lens | Repos touched | Issues filed/drafted | Best next action |
| --- | ---: | ---: | --- |

## Top Recommendations

1.
2.
3.
4.
5.

## Needs Tony Decision

- 

## Ready For Implementation Swarm

- 

## Archive / PR Follow-Through

- Raw artifacts preserved at:
- Combined deliverables opened as PRs:
- Remaining hidden-output risk:
```
