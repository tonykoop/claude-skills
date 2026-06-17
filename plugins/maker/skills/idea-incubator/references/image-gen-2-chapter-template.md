# Image-gen-2 Chapter Template And Asset Contract

Use this reference when defining or producing an **image-gen-2 design-book /
yearbook chapter** for an instrument repo (Refs #92, #100) — the shared template
and asset contract that must exist *before* any per-repo chapter is generated.
This file is the prerequisite gate both stories name: a chapter may only be
produced once this template and asset contract are defined and the underlying
build packet has passed its repo gates.

This reference defines the *contract*, not the chapters themselves. The chapters
live in their target repos (`instrument-maker-v4`, `sheet-music`,
`instrument-showcase`, or the per-instrument build repo); this skill only owns
the promotion-time template and the provenance/authority rules that keep
generated imagery honest.

## Hard gate: packet first, chapter second

Do not create or promote a chapter until the instrument's build packet has
earned it. Verbatim from #100: *"Only create a chapter after the instrument
packet passes its repo gates. The chapter should not claim build readiness
before the underlying packet earns it."*

A chapter is a **narrative-and-visual layer over an already-validated packet**.
It never adds, implies, or upgrades build readiness. If the packet is provisional,
the chapter says so in plain text on the opening spread.

## Authority vs. concept: the two-source rule

Every chapter draws from exactly two kinds of source, and they are never mixed
or relabeled:

1. **Authority artifacts (load-bearing).** The dimensioned, machine-graded,
   or measured outputs the build actually depends on: parameter CSVs, CAD /
   SolidWorks drawings, DXF/STEP exports, Wolfram-content tables, BOMs, test
   logs. These are cited, versioned, and traceable to the packet commit.
2. **Concept imagery (non-load-bearing).** image-gen-2 renders, cover studies,
   collage concepts, isometric mood views, restorations, mockups. These are
   **derivatives, not evidence**, and must never be read as dimensions, a build
   instruction, or proof of a feature.

The chapter's job is to *pair* the two so a reader feels the instrument while
trusting the numbers — without ever confusing one for the other.

## image-gen-2 asset contract

Each generated asset ships with a sidecar metadata block (front-matter or a
`prompts/` companion file) carrying:

- `asset_id` — stable slug, unique within the chapter.
- `kind` — one of `cover`, `hero`, `spread`, `isometric-concept`, `collage`,
  `restoration`, `mood`. All are concept kinds; none are authority kinds.
- `prompt` — the exact generation prompt (kept under `prompts/` for reproduction).
- `derivative: true` — always. A generated asset is never marked as source or
  evidence.
- `non_dimensional: true` — the render must not be used to read or imply any
  measurement; any number visible in-image is decorative and must be repeated
  from an authority artifact in the caption if it matters.
- `source_provenance` — what real material (if any) informed it, with a pointer
  to the source ledger; if purely synthetic, say so.
- `packet_ref` — the packet commit/tag the chapter sits on top of.
- `caption` and `alt_text` — human caption plus accessibility text; the caption
  carries any real figure by citing the authority artifact, not the render.
- `review_state` — `draft` → `privacy-reviewed` → `proof-reviewed`. No chapter
  publishes with an asset below `proof-reviewed`.

Generated covers, layout studies, collage concepts, restorations, and mockups
are derivatives, not source evidence — consistent with the rollout posture in
[`yearbook-design-book-rollout.md`](yearbook-design-book-rollout.md).

## Chapter structure (minimum viable chapter)

A pilot chapter is the smallest believable artifact, not a full book. The
minimum set:

1. **Opening spread** — instrument name, one-line identity, packet status
   (validated / provisional), and the readiness disclaimer when provisional.
2. **The build, honestly** — the authority artifacts: parameter table (from
   CSV), key drawing (CAD/DXF), and any graded/measured results, each cited to
   the packet commit.
3. **The instrument, felt** — concept imagery paired to the build sections, every
   asset carrying its contract block and a `derivative` label visible to the
   reader.
4. **Build-story arc** — design-log / experiment-lab highlights as narrative
   (yearbook framing: a short arc with captions), drawn from real log entries.
5. **Colophon** — provenance summary: packet ref, authority-artifact versions,
   image-gen-2 prompts location, reviewers (privacy + proof), and the
   derivative-imagery statement.

Yearbook framing (#100) styles 3–4 as editorial spreads with visual hierarchy
and caption arcs; design-book framing (#92) leans into the technical pairing in
2–3. Both use the same contract.

## Privacy and people

If a chapter includes identifiable people, private source images, scans, names,
schools, homes, events, or location history, route through the privacy gates in
[`yearbook-design-book-rollout.md`](yearbook-design-book-rollout.md),
[`photo-album-private-media-pilot.md`](photo-album-private-media-pilot.md), and
[`private-media-decision-stub.md`](private-media-decision-stub.md) before any
export, print, or public push. Instrument chapters are usually public-source, but
build photos with people in them are not.

## Pilot-first

Define the template once (this file), then prove it on **one** instrument repo
with a minimum chapter before any fleet rollout. The pilot-repo choice and the
image-gen-2 generation itself are owner decisions and are made at promotion time
in the target repo — this skill stops at the validated template and contract.

## Promotion handoff

When the pilot is ready, promote per
[`references/promotion-handoff.md`](promotion-handoff.md): the downstream issue
carries the packet ref, the chosen chapter framing (design-book vs. yearbook),
the asset-contract checklist, and the named privacy/proof reviewers. Keep
`Refs #92` / `Refs #100` on the source ideas until the target-repo chapter
scaffold, asset contract instance, and proof workflow exist.
