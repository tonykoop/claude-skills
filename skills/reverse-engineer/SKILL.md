---
name: reverse-engineer
description: >-
  Analyze existing objects, photos, video, sketches, dictated or written
  descriptions, and named-but-unseen artifacts into disciplined
  reverse-engineering notes: observed facts, inferred facts, assumptions,
  unknowns, confidence-marked dimensions, follow-up measurement requests,
  mechanism hypotheses, material/process guesses, and builder handoffs. Works
  on platforms that can render images and on platforms that can't (Codex CLI
  without vision, Gemini CLI text mode, mobile zip-upload, pasted-link-only
  flows) by switching to named-object, dictated, video, or
  description-only intake modes. Use when the user says "reverse engineer
  this", "how does this work?", "make my own version of this", "extract
  dimensions from this photo", "infer the mechanism", "what is inside this?",
  or otherwise asks to understand or recreate a real thing from incomplete
  evidence. Pair with maker-engineering, makerspace, and instrument-maker-v4
  when analysis turns into design, fabrication, or instrument build packets.
---

# Reverse Engineer

Version: 1.0.0

Turn incomplete evidence about a real thing into a structured, uncertainty-preserving analysis. The job is not to guess confidently; it is to separate what is visible, what is measured, what is inferred, what is assumed, and what remains unknown so a builder or specialist skill can act without inheriting hidden fiction.

## Core Rule

Never present inferred dimensions, materials, mechanisms, internal structure, or provenance as facts. Every non-observed claim needs a confidence level, evidence note, and next measurement or test that could confirm it.

## Workflow

1. Define the analysis mode:
   - **Photo/object observation** for visual inventories, visible features, and image limits.
   - **Dimension inference** for scale estimates, proportions, tolerances, and missing views.
   - **Mechanism explanation** for motion, force paths, assemblies, hidden components, and failure modes.
   - **Material/process inference** for likely materials, finish, tooling, wear, manufacturing traces, and assembly sequence.
   - **Handoff-to-builder** when there is enough data for `maker-engineering`, `makerspace`, or `instrument-maker-v4`.
2. Inventory the inputs. Note images, sketches, links, user-provided dimensions, known scale references, object access, measurement tools, and usage context. If the runtime can't render attached images (Codex CLI without vision, Gemini CLI text mode, mobile zip-upload that strips media, or any pasted-link-only workflow), say so up front and switch to one of the no-vision intake modes below — don't pretend to see what you can't.
3. Create the observation ledger using `references/observation-template.md`. Fill observed facts before making inferences.
4. Mark every claim as one of:
   - `observed`: directly visible or user-stated as measured.
   - `measured`: supplied by the user or derived from a reliable measurement tool.
   - `inferred`: reasoned from visible evidence, proportions, comparable parts, physics, or known construction methods.
   - `assumed`: chosen to continue analysis, not evidenced enough to rely on.
   - `unknown`: needed, but not available from current evidence.
5. Attach confidence language from `references/confidence-language.md` to inferred or assumed claims.
6. Ask for only the measurements that would materially reduce risk. Use `references/measurement-request-checklist.md`.
7. If the user asks to build, repair, clone, or commission the thing, decide whether the evidence is builder-ready:
   - If enough: write a handoff with `references/builder-handoff-template.md`.
   - If not enough: write a "blocked from builder handoff" note with the minimum measurements or tests needed.
8. Route the next phase:
   - `maker-engineering`: turn verified analysis into engineered design choices, tolerances, simulations, or trade studies.
   - `makerspace`: fabricate fixtures, shop plans, cut lists, toolpaths, or physical parts.
   - `instrument-maker-v4`: create instrument design/build packets after critical acoustic and dimensional data is validated.

## Image Handling

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

In every no-vision mode, state the mode at the top of the analysis ("intake mode: named-object + dictated description, no images viewable") so the user knows what discipline you're operating under. Pair with `instrument-maker-v4`'s description-only intake when the object is a musical instrument.

## Output Shape

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

## Builder-Ready Gate

Emit a builder-ready handoff only when all of these are true:

- The functional goal is clear.
- Critical dimensions are measured or have conservative tolerance ranges.
- Materials are known or acceptable substitutions are stated.
- Interfaces, fasteners, joints, or acoustic/contact surfaces are documented.
- Safety, legal, and product-boundary risks have been surfaced.
- Remaining unknowns are non-critical or are explicitly assigned to a test/prototype.

If a user asks to reproduce a proprietary product for commercial use, pause and ask Tony or the user for legal review before writing a production handoff. You may still provide learning-focused analysis, noncommercial repair notes, or high-level functional explanation.

## Reference Map

- `references/observation-template.md`: Claim ledger, dimension table, mechanism notes, and unknown register.
- `references/measurement-request-checklist.md`: Follow-up photo and measurement checklist by object type.
- `references/confidence-language.md`: Approved confidence terms and phrases to avoid.
- `references/builder-handoff-template.md`: Compact handoff format for `maker-engineering`, `makerspace`, and `instrument-maker-v4`.
