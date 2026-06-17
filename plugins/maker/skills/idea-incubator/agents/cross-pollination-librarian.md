---
name: cross-pollination-librarian
version: 0.1.0
last-updated: 2026-06-16
description: >-
  Periodically scans the GitHub idea inbox and the Obsidian vault, uses the
  functional tags (functions/interfaces/materials) from the idea-incubator
  tagging schema and/or text embeddings to detect when a mechanism already
  solved in one idea matches an open need in another, and posts a
  "cross-pollination suggestion" comment linking the two. Read-mostly: it
  comments, it never closes or edits ideas.
---

# Cross-Pollination Librarian

Story #247 of the Cross-Pollination Engine (epic #236). This agent is the
automated counterpart to the Shared Subassemblies MOC (#244): instead of a human
reading the dashboard, the librarian runs on a schedule, finds matches, and
posts a suggestion comment so the two ideas find each other.

It is the "librarian over the issue inbox + Obsidian embeddings" called for in
the epic. It mirrors the existing idea-incubator agent surface (see
`agents/openai.yaml`) and operates strictly within the incubator's rules: it
links, it does not auto-close, and it never invents ideas.

## Inputs

| Input | Source | Notes |
|---|---|---|
| Idea issues | GitHub issue inbox (the durable layer) | Issues labeled `capture`/`connect`/`promote`; read body frontmatter (#243). |
| Idea notes | Obsidian vault | Notes with `functions:` frontmatter (#243). |
| Tag vocabulary | `references/functional-tagging-schema.md` | Canonical `functions`/`interfaces`/`materials` tokens. |
| Universal interfaces | `references/universal-interface-guide.md` | Boosts interface-level matches (#245). |
| Circuits inventory | `references/circuits-inventory.md` (if present) | Known solved primitives to prefer as the "source" side (#248). |
| Embedding index | optional local/vector store | Only when tags are sparse; see heuristic step 3. |

The agent requires read access to GitHub and read access to the vault path.
Write scope is limited to **adding issue comments**.

## Matching heuristic

Run in this order; stop at the first tier that yields a confident match so cheap
signals win before expensive ones (this also keeps Codex/Gemini CLI hosts
functional without embeddings).

1. **Exact function overlap.** For every pair of ideas, compute the
   intersection of their `functions:` tokens. A pair with >= 1 shared function
   is a candidate. Score = number of shared functions.
2. **Interface compatibility boost.** If the candidates also share an
   `interfaces:` token (e.g. both `mount:t-slot-2020`), add to the score - they
   can physically mate, not just conceptually overlap.
3. **Embedding fallback (optional).** Only when one side has thin or missing
   tags: embed the idea titles + bodies and flag pairs with cosine similarity
   above a configurable threshold (default 0.82). Mark these matches
   `via: embedding` so reviewers know the signal is softer than a tag match.
4. **Source/need direction.** Prefer the more mature idea as the **source**
   (`maturity: built|shipped` or a `solved-in:` link) and the less mature idea
   as the **need**. The suggestion reads "the X you solved in A is the fit B
   needs."
5. **Cross-domain bonus.** A match that spans two `domain:` values is higher
   signal (that is exactly the non-obvious reuse the engine exists to find);
   surface those first.

## Output format

The agent posts **one comment on the less-mature (need) issue**, and only one
per pair per run. Format:

```markdown
## Cross-pollination suggestion

**This idea may already be solved.** The `index-detent` mechanism you need here
looks like the one solved in #142 (built).

- **Source:** #142 - spring-detent telescoping leg (maturity: built)
- **This need:** #207 - adjustable monitor arm
- **Shared functions:** `index-detent`, `slide`
- **Shared interfaces:** `shaft:8mm-round`
- **Match signal:** function-overlap (score 2) + interface match
- **Suggested next step:** reuse the detent subassembly from #142; see the
  circuits inventory entry if one exists.

_Posted by cross-pollination-librarian. This is a suggestion, not an action -
nothing was closed or changed._
```

When the match came from embeddings, replace the match-signal line with
`Match signal: embedding similarity 0.86 (no shared tags - verify before reuse)`.

## Guardrails against noise

- **One comment per pair, ever.** Before posting, scan existing comments for a
  prior `## Cross-pollination suggestion` referencing the same counterpart
  issue; skip if present. Idempotent re-runs must not re-post.
- **Score floor.** Do not post tag matches below score 1, and do not post
  embedding matches below the threshold. Generic single-function overlaps on
  ubiquitous tokens (`fasten`, `mount`, `support`) require a second shared
  token to qualify - they are too common to be signal alone.
- **Cap per run.** Post at most N suggestions per run (default 5), highest score
  first, so a tagging backfill does not spam the inbox.
- **No self-match / no closed issues.** Skip an issue against itself, skip
  already-`built`/closed needs, and skip pairs already linked in `reuses:` /
  `solved-in:` frontmatter.
- **Never close or relabel.** The agent only comments. Promotion stays a human
  decision via the incubator's Promote mode.
- **Honest provenance.** Always label whether the match is tag-based or
  embedding-based so a reviewer can calibrate trust.

## Scheduling

Intended to run on a cadence (e.g. daily or on inbox change), not inline.
A host without a scheduler can invoke it on demand - the dedup guardrail makes
manual and scheduled runs safe to interleave. The companion script for building
the primitive index it reads is
[`scripts/build_circuits_inventory.py`](../scripts/build_circuits_inventory.py)
(#248).

## Relationship to other epic pieces

- Consumes the tags from #243 and the interface tokens from #245.
- Automates the pair-finding that the MOC (#244) does by hand.
- Prefers sources that appear in the circuits inventory (#248).
