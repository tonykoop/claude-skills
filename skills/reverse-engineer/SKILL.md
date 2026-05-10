---
name: reverse-engineer
metadata:
  version: 1.1.0
  last-updated: 2026-05-10
description: >-
  Analyze objects, photos, video, sketches, descriptions, and
  named-but-unseen artifacts into disciplined reverse-engineering notes:
  observed facts, inferred facts, assumptions, unknowns, confidence-marked
  dimensions, follow-up measurements, mechanism hypotheses, material/process
  guesses, and builder handoffs. Works on platforms that can render images and
  on platforms that can't (Codex CLI without vision, Gemini CLI text mode,
  mobile zip-upload, pasted-link-only flows) by switching to named-object,
  dictated, video, or description-only intake modes. Use when the user says "reverse engineer
  this", "how does this work?", "make my own version of this", "extract
  dimensions from this photo", "infer the mechanism", "what is inside this?",
  or otherwise asks to understand or recreate a real thing from incomplete
  evidence. Pair with `maker-engineering`, `makerspace`, or `instrument-maker`
  when analysis turns into design or fabrication. Do not use for software
  reverse engineering or protocol analysis.
---

# Reverse Engineer

## Trigger phrases

- `reverse engineer this` / `analyze this object`
- `how does this work?` / `what's inside this?`
- `make my own version of this` / `clone this design`
- `extract dimensions from this photo`
- `infer the mechanism` / `how is this assembled?`
- `teardown notes` / `document this existing thing`

## Do not trigger for

- Software reverse engineering, protocol analysis, or binary disassembly.
- Design work after the object is already understood — route to `maker-engineering` or `makerspace`.
- Requests to reproduce proprietary products commercially — pause and confirm legal scope before writing a production handoff.

Turn incomplete evidence about a real thing into a structured, uncertainty-preserving analysis. The job is not to guess confidently; it is to separate what is visible, what is measured, what is inferred, what is assumed, and what remains unknown so a builder or specialist skill can act without inheriting hidden fiction.

## Core Rule

Never present inferred dimensions, materials, mechanisms, internal structure, or provenance as facts. Every non-observed claim needs a confidence level, evidence note, and next measurement or test that could confirm it.

## Workflow

1. Define the analysis mode:
   - **Photo/object observation** for visual inventories, visible features, and image limits.
   - **Dimension inference** for scale estimates, proportions, tolerances, and missing views.
   - **Mechanism explanation** for motion, force paths, assemblies, hidden components, and failure modes.
   - **Material/process inference** for likely materials, finish, tooling, wear, manufacturing traces, and assembly sequence.
   - **Handoff-to-builder** when there is enough data for `maker-engineering`, `makerspace`, or `instrument-maker`.
2. Run the **image-access preflight** before analysis whenever the prompt names or implies visual evidence ("Image 3", "photo above", "attached", "screenshot", "reference image", "in the conversation"). Record:
   - `image_access_mode`: `direct`, `file-path`, `partial`, `description-only`, or `missing`.
   - `images_referenced_in_prompt`: count or `unknown`.
   - `images_actually_viewable`: count or `unknown`.
   - `source_qualifier`: `analyst-verified`, `file-verified`, `partial-verified`, `observed-by-user`, or `not-provided`.
   Read `references/image-routing-recovery.md` when recovery wording or runtime-specific routing matters.
3. Put a standardized image-access banner as the first line of the report before any analysis:
   - `Mode: VISION-GROUNDED — image_access_mode=direct; images rendered and analyzed directly.`
   - `Mode: FILE-VERIFIED — image_access_mode=file-path; local image file(s) were available and verified before analysis.`
   - `Mode: DEGRADED (partial image) — image_access_mode=partial; only N of M referenced image(s) were viewable. Missing views: ___.`
   - `Mode: DEGRADED (description-only) — image_access_mode=description-only; analysis uses user prose, not analyst-verified pixels.`
   - `Mode: BLOCKED (missing image) — image_access_mode=missing; referenced image(s) are absent. Request recovery or explicit approval to continue in description-only mode.`
4. Inventory the inputs. Note images, sketches, links, user-provided dimensions, known scale references, object access, measurement tools, and usage context. If the runtime can't render attached images (Codex CLI without vision, Gemini CLI text mode, mobile zip-upload that strips media, or any pasted-link-only workflow), say so up front, request a recovery route once, and switch to one of the no-vision intake modes below only when the user approves or the task explicitly permits description-only analysis. Don't pretend to see what you can't.
5. Create the observation ledger using `references/observation-template.md`. Fill observed facts before making inferences. When evidence is user prose about an unavailable image, use `source_qualifier: observed-by-user` and note that the claim is not analyst-verified.
6. Mark every claim as one of:
   - `observed`: directly visible or user-stated as measured.
   - `measured`: supplied by the user or derived from a reliable measurement tool.
   - `inferred`: reasoned from visible evidence, proportions, comparable parts, physics, or known construction methods.
   - `assumed`: chosen to continue analysis, not evidenced enough to rely on.
   - `unknown`: needed, but not available from current evidence.
7. Attach confidence language from `references/confidence-language.md` to inferred or assumed claims. Respect the confidence ceiling for `description-only` and `missing` image modes.
8. Ask for only the measurements that would materially reduce risk. Use `references/measurement-request-checklist.md`.
9. If the user asks to build, repair, clone, or commission the thing, decide whether the evidence is builder-ready:
   - If enough: write a handoff with `references/builder-handoff-template.md`.
   - If not enough: write a "blocked from builder handoff" note with the minimum measurements or tests needed.
   - If the core visual evidence is `description-only` or `missing`, mark builder handoffs `provisional` by default. Use `builder-ready` only when independent measurements, verified files, or explicit user confirmation retire the builder-critical unknowns.
10. Route the next phase:
   - `maker-engineering`: turn verified analysis into engineered design choices, tolerances, simulations, or trade studies.
   - `makerspace`: fabricate fixtures, shop plans, cut lists, toolpaths, or physical parts.
   - `instrument-maker`: create instrument design/build packets after critical acoustic and dimensional data is validated.

## Image Handling

Before describing image content, establish `image_access_mode`:

- `direct`: images are rendered to the model/toolchain and can be analyzed directly.
- `file-path`: local image files are available and the runtime can inspect or render them. Cite filenames and any validation command used.
- `partial`: some referenced images/views are visible and some are missing. Separate claims by source.
- `description-only`: no image is visible, but the user supplied prose describing it.
- `missing`: the prompt references image evidence, but no image or usable description is available.

When images are available, be explicit about viewpoint limits. Report visible features and occlusions separately. If no scale reference exists, estimate only proportions, ratios, counts, and qualitative geometry; ask for a ruler, caliper, coin, grid mat, known fastener, or known object in the next image before claiming absolute dimensions.

For photo-based dimension inference, prefer:

- Known scale object in the same plane as the feature.
- Orthographic front/side/top/bottom views.
- Close macro shots of joints, fasteners, wear, seams, labels, and mechanisms.
- Repeated-part counts and spacing.
- Shadow, perspective, and lens distortion warnings where relevant.

## Intake When You Can't See Images

This skill has to work on platforms that don't render uploaded images and on mobile zip-upload paths that strip attachments. When that happens, fall back to one of these intake modes — each is legitimate, and each comes with its own confidence ceiling.

- **Named-object mode.** The user can identify the object ("vintage Coleman 200A lantern", "Yamaha YPT-220 keyboard", "duduk"). Treat the name as a strong but unverified pointer: pull on widely-known facts about the class, but mark every class-derived claim as `inferred` with `class-knowledge` as the basis and ask the user to confirm specifics (year, model variant, condition, modifications). Never fold class-typical dimensions into a builder handoff without per-instance measurement.
- **Voice/dictated description.** The user speaks or types a description. Mirror their language back as `observed` only when they explicitly assert it ("I'm holding it now and I can see..."), and as `assumed` when they're describing memory or speculation. Ask for the same close-up details the photo checklist would request — just verbally.
- **Video.** If the runtime can play or summarize video, use it the same as photos and additionally extract motion, sequence, and acoustic cues. If it can't, ask the user to scrub through and describe specific moments, or to extract still frames.
- **Sketch or diagram.** Treat as a stylized image: good for topology and connections, weak for absolute dimensions and proportions.
- **Written description only.** The leanest mode. Stick to topology, function, and named parts. Do not produce a dimension table from prose alone — produce a "feature register" instead and route every quantitative question into Measurement Requests.

In every no-vision mode, state the mode at the top of the analysis ("intake mode: named-object + dictated description, no images viewable") so the user knows what discipline you're operating under. Pair with `instrument-maker`'s description-only intake when the object is a musical instrument.

## Output Shape

Start every normal analysis with the image-access banner from Workflow step 3. The degraded-mode banners are required whenever image access is not `direct`. Include an `intake` block from `references/observation-template.md` when the output is more than a quick answer.

For a normal analysis, produce these sections:

1. `Input Inventory`
2. `Observed Facts`
3. `Measured Values`
4. `Inferred Facts`
5. `Assumptions`
6. `Unknowns`
7. `Mechanism or Construction Hypothesis`
8. `Dimension Table`
9. `Material and Process Notes`
10. `Confidence Notes`
11. `Measurement Requests`
12. `Builder Readiness`
13. `Next Handoff`

For quick questions, compress the sections but keep the claim labels and confidence notes.

If producing an agent record or handoff record, include `image_access_mode`, `images_referenced_in_prompt`, `images_actually_viewable`, and `source_qualifiers` so downstream managers and builder skills can detect degraded evidence without rereading prose.

## Builder-Ready Gate

Emit a builder-ready handoff only when all of these are true:

- The functional goal is clear.
- Critical dimensions are measured or have conservative tolerance ranges.
- Materials are known or acceptable substitutions are stated.
- Interfaces, fasteners, joints, or acoustic/contact surfaces are documented.
- Safety, legal, and product-boundary risks have been surfaced.
- Remaining unknowns are non-critical or are explicitly assigned to a test/prototype.

If a user asks to reproduce a proprietary product for commercial use, pause and ask for legal review before writing a production handoff. You may still provide learning-focused analysis, noncommercial repair notes, or high-level functional explanation.

## Reference Map

- `references/observation-template.md`: Claim ledger, dimension table, mechanism notes, and unknown register.
- `references/image-routing-recovery.md`: Image-access preflight modes, degraded banners, and runtime-specific recovery prompts.
- `references/measurement-request-checklist.md`: Follow-up photo and measurement checklist by object type.
- `references/confidence-language.md`: Approved confidence terms and phrases to avoid.
- `references/builder-handoff-template.md`: Compact handoff format for `maker-engineering`, `makerspace`, and `instrument-maker`.
