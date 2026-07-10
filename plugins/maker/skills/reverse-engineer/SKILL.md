---
name: reverse-engineer
description: >-
  Analyze real objects from photos, video, sketches, scans, measurements, or
  descriptions into uncertainty-preserving observations, inferred mechanisms,
  confidence-marked dimensions, material/process hypotheses, measurement
  requests, and builder handoffs. Use for "reverse engineer this", "how does
  this work?", "make my own version", "extract dimensions", teardown work, or
  recreating an object as editable CAD. Supports image-to-code-CAD, mesh/scan
  CADFit analysis, and a two-path SolidWorks workflow: hwe-solidworks MCP
  stage-confirm tools when live preflight passes, with in-process VBA-editor
  computer control as the fallback for unavailable or unsupported operations.
  Pair with maker-engineering, makerspace, or instrument-maker when analysis
  becomes design or fabrication. Do not use for software reverse engineering.
---

# Reverse Engineer

## Connectors

This skill works best with these MCP connectors. Claude will suggest connecting any that aren't already linked at the point they're needed (via `mcp__mcp-registry__suggest_connectors`).

- **Adobe for Creativity** (`22854937-9510-4b57-9230-62c820102d8f`) — optional for photo analysis, scale-bar overlay, multi-image stacking for dimension extraction.
- **Wolfram** (`de1d1dc7-ec10-459d-b511-797982834b43`) — optional for dimension/mass back-calculation, mechanism-hypothesis math, statistical confidence intervals on inferred dimensions.
- **Blender** (local stdio MCP — no registry UUID, requires the Blender MCP add-on) — optional for recreating the object as a parametric 3D model during teardown documentation. Skip `suggest_connectors`; direct the user to install the add-on.

## Trigger phrases

- `reverse engineer this` / `analyze this object`
- `how does this work?` / `what's inside this?`
- `make my own version of this` / `clone this design`
- `extract dimensions from this photo`
- `infer the mechanism` / `how is this assembled?`
- `teardown notes` / `document this existing thing`
- `turn this photo into a 3D model` / `recreate this as CAD` / `make a printable version of this`

## Do not trigger for

- Software reverse engineering, protocol analysis, or binary disassembly.
- Design work after the object is already understood — route to `maker-engineering` or `makerspace`.
- Requests to reproduce proprietary products commercially — pause and confirm legal scope before writing a production handoff.

Turn incomplete evidence about a real thing into a structured, uncertainty-preserving analysis. The job is not to guess confidently; it is to separate what is visible, what is measured, what is inferred, what is assumed, and what remains unknown so a builder or specialist skill can act without inheriting hidden fiction.

## Core Rule

Never present inferred dimensions, materials, mechanisms, internal structure, or provenance as facts. Every non-observed claim needs a confidence level, evidence note, and next measurement or test that could confirm it.

## Workflow

0. **Image-access preflight (mandatory).** Before producing any analysis, decide which `image_access_mode` applies and record it. Allowed values:
   - `direct` — the runtime can render the image inline and the agent has actually seen pixels.
   - `file-path` — a local file path was supplied that the agent can read with its tooling (verify with a `Read` or equivalent before claiming this mode).
   - `description-only` — the user provided prose, voice, or a name for the object; the agent has not seen the image.
   - `missing` — the user referred to an image that did not arrive (stripped attachment, broken link, expired upload).
   - `partial` — multiple images were referenced; some are viewable and some are not.

   If the mode is `missing` or `partial`, ask **once** for recovery using the prompts in `references/image-access-recovery.md`. If the user declines recovery or the runtime cannot accept files, proceed under `description-only` with the mode noted and the user's choice recorded.

   Emit the standardized **degraded-mode banner** (see "Degraded-Mode Banner" below) as the first line of every output artifact whenever `image_access_mode` is anything other than `direct`. Do not paraphrase it — downstream automation parses the exact pattern.
1. Define the analysis mode:
   - **Photo/object observation** for visual inventories, visible features, and image limits.
   - **Dimension inference** for scale estimates, proportions, tolerances, and missing views.
   - **Mechanism explanation** for motion, force paths, assemblies, hidden components, and failure modes.
   - **Material/process inference** for likely materials, finish, tooling, wear, manufacturing traces, and assembly sequence.
   - **Handoff-to-builder** when there is enough data for `maker-engineering`, `makerspace`, or `instrument-maker`.
2. Inventory the inputs. Note images, sketches, links, user-provided dimensions, known scale references, object access, measurement tools, and usage context. The preflight result from step 0 belongs in the input inventory: record `image_access_mode`, count of images referenced, count actually viewable, and the user's recovery decision.
3. Create the observation ledger using `references/observation-template.md`. The template's `intake:` YAML block must be filled in before any other section. Fill observed facts before making inferences.
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
   - `instrument-maker`: create instrument design/build packets after critical acoustic and dimensional data is validated.

## CADFit Mesh/Scan Branch

Use the CADFit branch only when the user supplies a real local mesh, scan, or point-cloud artifact such as `.stl`, `.obj`, `.ply`, `.off`, `.step`, or `.stp`. Do not trigger CADFit for photo-only, sketch-only, named-object, dictated-description, or missing-image intake. Those stay in the normal observation-led workflow above.

Before using CADFit tooling:

1. Open `references/cadfit-setup-license.md` and honor the license gate. CADFit is optional external research code and is not bundled in this skill.
2. Confirm the input is a mesh/scan path and record whether it appears watertight or repaired enough for kernel scoring.
3. Run the mesh branch:
   - Feature Extractor: `scripts/cadfit_feature_extractor.py`
   - Candidate scoring: `scripts/cadfit_test_cad_program.py`
   - Correction/pruning: `scripts/cadfit_correction_loop.py`
4. Treat kernel failures and missing native dependencies as normal data signals, not crashes.
5. Use `references/builder-handoff-template.md` for any builder handoff. Mark the handoff `provisional` unless dimensions, interfaces, material/process assumptions, and manufacturing review are all satisfied.

Graceful fallback message when CADFit cannot run:

```text
CADFit mesh/scan branch unavailable: this runtime does not have a usable watertight mesh plus local CadQuery/OpenCascade/CADFit tooling. I will continue with the standard reverse-engineering ledger and list the exact mesh/kernel setup needed before CADFit scoring can run.
```

Never present CADFit IoU as builder readiness by itself. High overlap can still be a manufacturing-wrong CAD tree.

## Parametric Recreation Branch (image → executable CAD)

When the user wants the analysis to end in a *model they can edit and print*
— "turn this photo into a 3D model", "recreate this as CAD" — branch to
`references/parametric-recreation.md` after the observation ledger exists.
The branch turns confidence-marked dimensions into an image-conditioned
code-CAD generation (reference pipeline: local CADAM + Claude via OpenRouter
→ BOSL2/OpenSCAD with a named module per part and editable parameters),
then validates the compiled mesh against an objective gate (renders /
watertight / envelope / min-wall / body count).

Non-negotiables, enforced by the reference:

- The prompt is **built from the ledger** — stated dims carry their values,
  `unknown`s become named placeholder parameters, measurement-gated features
  are declared as placeholders in the prompt itself.
- State fabrication floors (min wall, envelope) in the prompt; thin display
  geometry is the universal failure mode of image-conditioned generation.
- Every artifact carries provenance (pipeline, source image, cost, gate
  scores) and the label **GENERATED — not a measured master**; recreations
  from degraded intake are `provisional` like any other handoff.
- Extract source from the tool's database, not its DOM; compile and gate
  locally, never trust the in-browser preview.

This branch complements CADFit: CADFit starts from a *mesh/scan*, this
branch starts from *photos + the ledger*. Both end in parametric CAD with
validation, and neither is builder-ready by itself.

## Live SolidWorks Recreation

Use both supported SolidWorks paths; select by live capability rather than by
preference alone.

1. Prefer `hwe-solidworks` MCP when its `ping` reports `api_available: true`.
   Read `get_context` before writing. Use `stage_parameter`, `stage_feature`,
   or `stage_mate`, inspect `list_pending`, and call `confirm` only after the
   staged delta matches the observation ledger. Keep wire dimensions in mm.
2. Use VBA-editor computer control when MCP is absent, Connected COM cannot
   attach safely, the operation is not exposed as an MCP tool, or native
   feature-tree control is required. Generate or update an auditable `.bas`,
   run it in-process through SolidWorks Macro/VBE, and capture stage-specific
   errors plus a trace file. Select reference planes by feature object where
   possible instead of localized display names.
3. Validate either path against the real kernel: record active document,
   feature/body count, bounding box or critical dimensions, save/export path,
   and a screenshot or trace. MCP success, macro completion, and visual
   plausibility are evidence—not fabrication authority.
4. Preserve reverse-engineering uncertainty. Map measured ledger values to
   named parameters; keep inferred values confidence-marked and assumptions
   explicit in the CAD parameter ledger.

Do not silently switch paths after a failure. Record the failed preflight or
unsupported operation and the reason for using the fallback.

## Degraded-Mode Banner

When `image_access_mode` is anything other than `direct`, the **first paragraph** of every analysis artifact (notes, builder handoff, agent record summary) must be the following banner. Use the exact wording so downstream tooling can detect it; only fill the bracketed fields:

```text
> **Image-access mode: <mode>.** This analysis was produced without analyst-verified pixels of [N] referenced image(s). All "observed" claims below are transcriptions of the user's prose, name, voice, or sketch — not pixel-verified. Dimensional confidence is capped per `references/confidence-language.md`. Builder handoffs derived from this analysis are **provisional** by default.
```

Where `<mode>` is one of `description-only`, `missing`, `partial`, `file-path` (when the file is present but pixels were not actually rendered by the runtime), or `named-object`.

Pair the banner with the `intake:` YAML block at the top of the observation ledger so a script can both render the warning to a human and parse the structured field.

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

In every no-vision mode, state the mode at the top of the analysis ("intake mode: named-object + dictated description, no images viewable") so the user knows what discipline you're operating under. Pair with `instrument-maker`'s description-only intake when the object is a musical instrument.

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

When `image_access_mode` is `description-only`, `missing`, `partial`, or `named-object`, the builder handoff is **provisional by default**. The header must read `Handoff status: provisional` and the assumptions list must mark each chosen dimension as `assumed (intake degraded)` with a retire-by step. Do not flip to `builder-ready` without either (a) the user explicitly accepting provisional outputs or (b) a follow-up pass with `image_access_mode == direct` or measured values supplied.

If a user asks to reproduce a proprietary product for commercial use, pause and ask for legal review before writing a production handoff. You may still provide learning-focused analysis, noncommercial repair notes, or high-level functional explanation.

## Reference Map

- `references/observation-template.md`: Claim ledger, dimension table, mechanism notes, and unknown register. Includes the required `intake:` YAML block.
- `references/measurement-request-checklist.md`: Follow-up photo and measurement checklist by object type.
- `references/confidence-language.md`: Approved confidence terms and phrases to avoid. Includes the dimensional-confidence cap for degraded-intake modes.
- `references/builder-handoff-template.md`: Compact handoff format for `maker-engineering`, `makerspace`, and `instrument-maker`. Includes the provisional-by-default rule for degraded intake.
- `references/image-access-recovery.md`: Per-runtime recovery prompts when an image arrived but cannot be rendered (Claude Code, Codex CLI, web vision, Gemini CLI text mode, mobile zip-upload).
- `references/parametric-recreation.md`: Image → executable parametric CAD branch — CADAM/Fable prompt recipe built from the observation ledger, BOSL2/OpenSCAD conventions, DB source extraction, objective mesh-gate validation, cost telemetry, and GENERATED-labeling provenance. Proven on the 2026-07-02 four-instrument pilot series (fujara gate 1.000).
- `references/cadfit-setup-license.md`: CADFit optional external setup, attribution, runtime availability matrix, and license gate. Open before any CADFit mesh/scan workflow. CADFit is not bundled in this skill; the license gate currently flags redistribution/commercial-use risk.
- `references/cadfit-feature-extractor.md`: CADFit-style mesh/scan feature extractor adapter. Use only when a real mesh or point-cloud path exists; it returns candidate sketch profiles, slicing planes, revolution axes, or a degraded result asking for usable mesh input.
- `references/cadfit-test-cad-program.md`: CADFit-shaped `test_cad_program()` scoring adapter. Use for candidate CadQuery program feedback; returns Invalid-Ratio, Volumetric IoU, and kernel failure/unavailable signals as data.
- `references/cadfit-correction-loop.md`: Error-guided correction and backward-pruning loop. Use after score payloads to map over-reconstruction to `cut()`, under-reconstruction to `union()`, define termination, and preserve manufacturing-critical operations.
