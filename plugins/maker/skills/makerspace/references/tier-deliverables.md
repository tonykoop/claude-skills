# Tier deliverables

Detailed contents of each tier. Pair this with
`build-packet-structure.md`, which has the file-by-file spec.

## Tier 1 — Shop-ready

**Use it when:** the user wants to walk in and build today.

**Don't include:** drawings, deck, README, polished assembly manual.
Save those for Tier 2+.

**Quality bar:** *could a competent maker walk into the shop with
this and build the thing without coming back to ask questions?* If
yes, ship it. If no, you're missing something.

**Deliverables:**

| File | Purpose | Done bar |
|------|---------|----------|
| `design.md` | Parametric design, formulas not values | Every dimension cited downstream traces back here |
| `bom.csv` | Bill of materials with prices | Line costs computed, totals match, TBDs marked |
| `cut-list.csv` | Stock plan with kerf | Cuts fit within stock with kerf and trim allowance |
| `op-sequence.md` | Ordered ops with fixturing | Every cited tool exists in the shop profile; cert gaps surfaced |
| `safety-notes.md` | Build-specific safety notes | PPE, tool risks, material risks, fume/fire notes |

## Tier 2 — Portfolio-ready

**Use it when:** the user wants the build on their GitHub portfolio.

**What's added vs Tier 1:**

| File | Purpose | Done bar |
|------|---------|----------|
| `drawings/` or `drawing-brief.md` | Dimensioned drawings (Tier 2 brief OK; full SVGs preferred) | Title block, units, scale, datums, critical dims, tolerances |
| `assembly-manual.md` | Step-by-step build | Every step has tool, time, photo placeholder, gotcha note |
| `sourcing.csv` | Vendor URLs, lead times, alternates | Primary vendor URL works; alt vendor listed where reasonable |
| `validation.csv` | Acceptance checks | Every check has target, tolerance, method, when-to-check |
| `risks.md` | Failure modes + tests | Every risk has a test with pass/fail criteria |
| `README.md` | GitHub front door | Hero placeholder, intent, file map, license |
| `images/` (placeholders OK) | Process/finish photos | Hero placeholder explicitly marked TBD |

## Tier 3 — Capstone-ready

**Use it when:** the user wants this on their résumé, in a job
application, or at a portfolio review.

**What's added vs Tier 2:**

| File | Purpose | Done bar |
|------|---------|----------|
| `deck.pptx` | Capstone slide deck | 13 slides in canonical order, every claim traces to a packet file |
| `print-packet.pdf` | Printable shop packet | 12 sections in canonical order, ≤20 pages typical |
| `site/index.html` | Build-log static site | Single file, hero + intent + workflow + finished + repo link |
| `photo-shotlist.md` | What to photograph | Hero, process, detail, optional maker portrait |

## Cross-tier expectations

These hold at every tier:

- **Parametric design first.** Even Tier 1 has `design.md` with
  formulas. Don't skip and "go straight to cut list" — when the user
  changes a dimension, everything downstream needs to update.
- **Cite the shop profile for every tool/cert/material.** Don't use
  free-form names that don't appear in the profile. The verifier
  checks this.
- **Mark unknowns explicitly.** `TBD`, `assumption`, or `derived
  estimate`. Anywhere else, a guess looks authoritative and that's a
  bug.
- **The verifier runs at the end.** Before declaring done, run the
  verifier specialist (or the script) at the chosen tier.

## When the user says "I just want to build it"

That's a request for Tier 1. Don't over-deliver — Tier 1 is *enough*
when the user isn't planning to share or revisit. Spending time on a
deck the user won't read is wasted effort.

## When the user says "make me a portfolio piece" or "for my résumé"

Tier 3. Don't under-deliver — a deckless GitHub README with a few
photos isn't recruiter-grade.

## When the user says nothing about polish

Default to Tier 1 and confirm: "I'll target Tier 1 (shop-ready) — say
the word if you want Tier 2 or 3 polish." This is faster than asking
upfront and leaves the user in control.

## Pricing context

Tier 3 costs more time than Tier 1 by roughly 3-5x in agent-time and
~10x in human review time. For a quick weekend project, Tier 1 is the
right answer. For a capstone, Tier 3 is the answer. Don't auto-upsell.
