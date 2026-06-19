# Instrument Design-Book Chapter Readiness

Issue: https://github.com/tonykoop/claude-skills/issues/92

This document tracks which public instrument repos are ready (or nearly ready)
for an image-gen-2 design-book chapter, per the gate criteria defined in
`plugins/maker/skills/idea-incubator/references/image-gen-2-chapter-template.md`.

A chapter is a **narrative-and-visual layer over an already-validated packet**.
It must not be created — and must not imply build readiness — before the
underlying build packet earns it.

## Hard gate (verbatim from #100 and the template)

> "Only create a chapter after the instrument packet passes its repo gates.
> The chapter should not claim build readiness before the underlying packet
> earns it."

The packet gates a chapter must pass:

- [ ] At least one L2-level (design-complete) packet exists in the repo
- [ ] Parameter CSV (or equivalent build-spec table) is versioned and cited
- [ ] At least one dimensioned drawing (CAD, DXF, or STEP export) is present
- [ ] A BOM is present (even if partial)
- [ ] Wolfram content or measurement evidence present (at least stub)
- [ ] README describes the instrument's identity, not just its build status
- [ ] Repo is public (chapters are public-facing)

## Public Instrument Repos — Gate Status

Snapshot from 2026-06-19. Gate columns are `?` (unverified) until a per-repo
audit is run against the criteria above.

| Repo | L2 packet? | Param CSV? | Drawing? | BOM? | Wolfram? | README? | Chapter-ready? |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `ashiko-drum-workshop` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `barrel-organ` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `cajon` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `duduk` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `gemshorn` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `handpan` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `hydraulophone` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `instrument-showcase` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `kaval-alghosazi-flutes` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `kora` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `marimba` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `music-box` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `ngoni` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `pipa` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `portative-organ` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `sea-organ` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `siku-zampona` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `waterphone` | ? | ? | ? | ? | ? | ? | ❌ unverified |
| `xiao` | ? | ? | ? | ? | ? | ? | ❌ unverified |

## How to audit a repo

Run this for each repo before filling in a gate column:

```bash
# Clone or inspect the repo
gh repo view tonykoop/<repo> --json description,defaultBranchRef

# Check for key artifacts
gh api repos/tonykoop/<repo>/git/trees/HEAD --jq '.tree[].path' | grep -iE \
  'param|bom|cad|drawing|wolfram|\.csv|\.dxf|\.step|\.sldprt'

# Read README
gh api repos/tonykoop/<repo>/readme --jq '.content' | base64 -d | head -40
```

Fill in the table above with `✅`, `⚠️` (partial), or `❌` for each column.
Add a `Notes` column entry when a gate is partially met or conditionally met.

## Chapter production order (when repos start passing gates)

Suggested priority — not binding, Tony decides:

1. **`instrument-showcase`** — if it acts as a meta-index of all instruments,
   it anchors the chapter series even if individual chapters are incomplete.
2. **Any repo with an existing SolidWorks drawing + BOM** — the authority
   artifacts are already present, so the chapter production reduces to a
   visual/editorial task.
3. **Repos with public Wolfram content** — the interactive-content guide
   section writes itself; these chapters will be the most differentiated.
4. **Repos with existing build photos** — reduces the image-gen-2 workload
   to fills and polish, not synthesis from scratch.

## Chapter output destination

Chapters live in their target repos, not in `claude-skills`. The template and
asset contract remain here (in the idea-incubator skill reference). When a
chapter is produced:

1. A new `docs/design-book-chapter/` folder is created in the target instrument
   repo.
2. The asset sidecar metadata (from the template's asset contract) is committed
   alongside each generated image.
3. A `Refs #92` comment is added to this issue linking the chapter PR.

## Related Work

- `plugins/maker/skills/idea-incubator/references/image-gen-2-chapter-template.md`
  — the full asset contract and chapter structure. **Read this first.**
- `docs/image-gen-2/instrument-chapter-production-workflow.md` (Refs #100) —
  the yearbook-style editorial workflow that produces a chapter from a
  gated repo.
- Issue #100 — yearbook-style chapter production workflow (same gate, different
  angle: editorial process vs. chapter structure).
