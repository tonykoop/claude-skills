---
name: source-citations
version: 0.1.0
last-updated: 2026-05-22
description: >-
  Turn the Tony Koop instrument-design source library (the Drive spreadsheet of
  ~200 tools, papers, calculators, and references) into a keyed master
  bibliography, AND maintain a companion techniques catalog of demonstrations by
  real makers (timestamped YouTube moments, MakerTok/Instagram clips, wikiHow,
  makerspace notes), so musical instrument design repos can cite both the
  knowledge and the how-to demonstrations that back them. Use when the user
  wants to add cited sources or references to instrument repos, build a
  bibliography or citation registry, catalog maker techniques with deep-links to
  exact video moments, tag sources by instrument, generate or validate a
  SOURCES.md or TECHNIQUES.md, render a browsable Quarto catalog of techniques,
  treat instrument repos as citable research projects, or audit which repos lack
  attribution. Pairs with instrument-maker-v4 (intellectual-provenance
  counterpart to its supply-side sourcing) and laser-art (technique sources).
  Offline; never invents a citation, timestamp, or technique a source does not
  verifiably support.
---

# Source Citations

Tony's 100+ instrument repos are framed as **research projects**. A research
project's credibility comes from traceable provenance: a reader should be able
to follow any design decision back to the source that informed it. This skill
builds that provenance layer on top of the existing source library.

## The core integrity rule

**Never attach a citation a repo's work does not actually rest on.** A wrong or
padded citation is worse than a missing one — it makes a research repo look
fake the moment a knowledgeable reader checks it. Therefore:

- The maker (Tony) decides which sources apply to which repo. The skill never
  guesses citations from a repo's name or topic.
- Every citation carries a one-sentence `why` that the maker wrote, stating
  *how* that source informed *this* instrument.
- The validator refuses to generate a `SOURCES.md` if any cited key is unknown
  or any `why` is blank.

If you (the agent) are tempted to auto-suggest sources, you may *propose
candidates* for the maker to confirm, clearly labelled as unconfirmed — but
you may never write them into `.citations.yaml` yourself.

## Architecture (single source of truth)

```
source library spreadsheet (Drive)         ← human-maintained master list
        │  export to TSV
        ▼
references/library.tsv                      ← flat export, one row per source
        │  scripts/build_registry.py
        ▼
references/registry.yaml  (+ .json)         ← KEYED bibliography, 201 entries
        │                                      each entry has a stable `key`
        │  per repo: maker writes .citations.yaml (curated key list + why)
        ▼
<repo>/SOURCES.md                           ← generated, honest, repo-specific
```

The registry is the **single source of truth** for URLs, descriptions, and
licenses. A repo's `SOURCES.md` holds no URLs of its own — it points at registry
keys, so when a link changes you fix it once in the registry, not in 100 repos.
This mirrors the `instrument-maker-v4` catalog-as-database pattern and Tony's
`claude-skills` meta-repo "canonical source" principle.

### Stable keys are a contract

Once a key is shipped and a repo cites it, **the key must never be renamed** —
renaming silently breaks every repo that cited it. `build_registry.py` derives
keys deterministically and disambiguates collisions with a meaningful token
(author surname, tag) rather than a bare number, so keys stay memorable and
hand-writable. If you ever regenerate the registry, diff the key list against
the previous version and treat any changed key as a breaking change.

## Workflow

### 0. Refresh the registry (only when the spreadsheet changes)

Export the Drive spreadsheet to `references/library.tsv` (tab-separated, same
columns as the sheet: bucket, section, section_title, entry, url, tags,
priority, license, description — priority uses `star` for ★ rows). Then:

```bash
python3 scripts/build_registry.py references/library.tsv \
  --out references/registry.yaml
```

This emits `registry.yaml` and `registry.json` and asserts all keys are unique.

### 1. Tag the library by instrument (the recommended first pass)

Before touching repos, decide which instruments each source applies to. This
makes per-repo curation a menu-pick instead of a search. Fill the `instruments`
list on registry entries (or maintain it in the spreadsheet as an extra column
and re-export). See `references/instrument-tagging.md` for the controlled
vocabulary and the tagging procedure. Tagging is still a human judgement call —
the skill provides structure, not automatic assignment.

### 2. Curate per-repo citations

In each repo, create `.citations.yaml`:

```yaml
instrument: Transverse Flute
repo: transverse-flute
cites:
  - key: demakein
    why: Generated the bore profile and tone-hole positions this design started from.
  - key: nederveen
    why: Authority for the tone-hole end-correction physics behind the hole placement.
```

Keys come from `registry.yaml`. The `why` is the maker's own sentence.

### 3. Validate, then generate

```bash
python3 scripts/gen_sources.py check references/registry.yaml <repo-dir>   # gate
python3 scripts/gen_sources.py gen   <repo-dir>                            # writes SOURCES.md
```

`gen` re-runs `check` first and refuses to write if it fails. `SOURCES.md`
groups sources by lifecycle bucket and renders title, link, license, and the
maker's rationale.

### 4. Audit coverage across many repos

To find which repos still lack attribution, run `check` across a folder of
repos and collect the repos missing `.citations.yaml` or `SOURCES.md`. See
`references/rollout.md` for the batch pattern and the recommended order
(start with the public "done-bar" repos).

## Scope and limits

- **Read-only and offline.** This skill does not fetch URLs or verify that a
  link still resolves — that is a separate link-check concern. It only manages
  the citation *mapping*.
- **Runs on the maker's machine.** The Drive connector available to the agent
  is read-only, so registry refresh and per-repo file writes happen locally on
  Tony's PC where the repos live.
- **Not a supply BOM.** For where to *buy* parts, use
  `instrument-maker-v4`'s `sourcing-and-production.md`. This skill is the
  *intellectual* provenance counterpart.

## Files

- `scripts/build_registry.py` — library TSV → keyed registry.
- `scripts/gen_sources.py` — `check` and `gen` for per-repo `SOURCES.md`.
- `scripts/gen_techniques.py` — `check`/`gen`/`site`/`audit` for the techniques catalog.
- `references/registry.yaml` / `.json` — the keyed bibliography (201 entries).
- `references/techniques.yaml` — the techniques catalog (maker demonstrations).
- `references/library.tsv` — the flat export the registry is built from.
- `references/instrument-tagging.md` — tagging vocabulary and procedure.
- `references/techniques-catalog.md` — the techniques data model and capture flow.
- `references/rollout.md` — batch audit and rollout order.
- `references/citations-template.yaml` — copy into a repo as `.citations.yaml`.
- `captures/` — local Obsidian Web Clipper notes (durable record of clips).

## Companion: techniques catalog (HOW, by real makers)

The bibliography answers "what knowledge backs this design." The techniques
catalog answers "who showed how to do this, and exactly where." Its atomic unit
is a *demonstration* — a person showing a technique — not a tool homepage. A
duduk-reed-scraping clip and a hidden-seam laser trick are technique entries;
the Inkscape that drew the vector is a bibliography source. A technique may
`grounds:`-link to bibliography keys so the two registries cross-reference
without duplicating.

### The link is disposable; the capture is durable

MakerTok and Instagram links rot fast. So the live URL is only a pointer — the
durable record is the `what_they_show` description plus, ideally, a local
**Obsidian Web Clipper** note (`captures/<key>.md`) that pulls the page text and
photos into the vault. The clipper writes Properties as YAML frontmatter and the
page as markdown body, so a clip can carry the same fields the registry uses.
When the clip dies online, your local capture still holds the knowledge.

### confirmed vs unconfirmed — the timestamp integrity rule

Every technique entry has a `status`:

- `confirmed` — a human watched/read it; `start` (seconds) and `what_they_show`
  are verified accurate.
- `unconfirmed` — creator, platform, and URL are real, but the specific moment,
  timestamp, and technique description are **not** verified. These are seeds.

**Only confirmed techniques may be cited by a repo** — `gen_techniques.py check`
hard-fails on any attempt to cite an unconfirmed seed. This exists because a
fabricated timestamp is the worst failure mode: a reader who clicks a citation
and lands on the wrong moment stops trusting every citation. An agent must never
invent a `start` value or a "what they show" from search results alone — finding
that a maker exists is not the same as verifying what they demonstrate at a
given second. Agents may add `unconfirmed` seeds (real creator + URL, blank
timestamp) and propose candidates, but promotion to `confirmed` is a human act
of having actually watched.

### Commands

```bash
python3 scripts/gen_techniques.py audit                       # list by status
python3 scripts/gen_techniques.py check <repo-dir>            # gate (rejects seeds)
python3 scripts/gen_techniques.py gen   <repo-dir>            # writes TECHNIQUES.md
python3 scripts/gen_techniques.py site  techniques-catalog.qmd  # Quarto site
```

The Quarto site embeds confirmed YouTube demos at their exact moment via
`{{< video URL start="SECONDS" >}}` (verified shortcode), lists other platforms
as links, and shows unconfirmed seeds in a separate non-citable section. Render
with `quarto render techniques-catalog.qmd` on the desktop. See
`references/techniques-catalog.md`.
