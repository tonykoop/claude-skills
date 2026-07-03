# CAD Generation Modality Routing + Objective Validation

Three CAD-generation modalities are live and were benchmarked head-to-head
on identical specs (Code-CAD Arena, makerbench-hwe, 2026-07-02). Modality
choice is a routing decision this umbrella skill owns; execution belongs to
the specialist or tool lane chosen.

## The three modalities

| Modality | Input | Output | Reference implementation |
|---|---|---|---|
| **Blind text code-CAD** | measured spec / task brief only | OpenSCAD (BOSL2) program | CLI agents (`claude -p`, `codex exec`, etc.) prompted with a spec-JSON brief |
| **Image-conditioned code-CAD** | reference photo + brief | parametric OpenSCAD with Customizer sliders | local CADAM (`_meta/CADAM`, GPLv3) + Claude via OpenRouter |
| **Live-CAD copilot** | conversational, inside real CAD | native feature trees, drawings, assemblies | Adam plugin (SolidWorks/Fusion/Onshape); Luthier Bridge (StudioPipeline-hwe) is the Fable-native equivalent with loopback auth + stage/confirm |

## Routing table

Route by input type and required deliverable:

- **Measured spec only, no aesthetic target** → blind text code-CAD. Cheapest,
  fully scriptable, benchmarkable.
- **Reference photo or aesthetic target** → image-conditioned lane. First
  three-way datapoint: the same model scored *identically* blind vs
  image-conditioned on the same instrument (same failing sub-gate) — image
  conditioning bought visual fidelity for free without changing geometric
  hygiene. Pair with `reverse-engineer`'s Parametric Recreation Branch when
  the photo is of a real object (ledger discipline first).
- **Needs real feature trees, native files, or 2D drawings** → live-CAD
  copilot lane. Native SolidWorks output arrives as proper multi-part
  assemblies (a generated kora came out as 8 SLDPRTs + SLDASM, 57 distinct
  mesh bodies) but typically non-watertight when tessellated — that's
  tessellation, not design error; plan a mesh-repair step if downstream
  needs watertight.
- **Assembly-heavy in any lane** → demand a named module/part per component
  and *distinct bodies* ("do not fuse across joints"), so body-count
  validation and per-part iteration work. For OpenSCAD, the module-compile
  fallback pattern (compile each zero-arg module standalone and count
  non-empty results) rescues mated assemblies that a disjoint-mesh count
  would punish.

Modality gotchas that affect routing cost estimates:

- Compile time is a real budget: dimpled/domed compound surfaces can need
  10+ minutes in OpenSCAD. State a tessellation cap (`$fn ≤ 96`) in
  image/text lanes, and give validation harnesses an explicit render
  timeout budget rather than a default.
- Live-CAD exports need unit checks (SolidWorks STEP defaults to inches;
  verify mm on every export) and single-file STL settings for assemblies.

## Objective validation harness (any physical project)

Adopt the arena's oracle-free mesh gate as the DoE-style acceptance check
for *any* generated CAD, with per-project floors:

1. **renders** — compiles to a mesh at all;
2. **watertight** — manifold (waivable for live-CAD tessellation, see above);
3. **nonzero volume**;
4. **fits envelope** — compare **sorted** extents against the stated
   envelope so orientation can't fail a valid model;
5. **min wall ≥ floor** — set per project from the fabrication process;
   thin display geometry is the universal generated-CAD failure mode;
6. **body count ≥ expected parts** — the assembly check.

Score = mean of sub-gates. Use it as the acceptance bar in handoffs:
"specialist receives only candidates ≥ X".

## Telemetry pattern

Every generated artifact's provenance records: pipeline + model id, wall
time, thinking time if visible, and **API cost** (OpenRouter usage delta
before/after; the endpoint lags minutes). Single-shot image-conditioned
instruments ran $0.55–0.85; an iterated session ~$4. Costs belong in the
DoE log like any other response variable.

## DoE framing: modality as an experiment axis

Modality itself is a factor. To A/B modalities for a new project family:

- fix instrument/spec, seed, and acceptance gate; vary only the lane;
- run blind and conditioned candidates through the *same* gate, and stage
  blind human votes with anonymized assets (no tool names in file paths);
- track both scorelines separately — two rounds of arena data show
  blind-vote preference and objective gate pass-rate can *anticorrelate*
  (Spearman -0.076, -0.200); a candidate that wins eyes can lose gates.
  Never collapse the two into one number.
- external/late candidates (e.g. a live-CAD result finishing after the
  batch) enter through an ingest path that writes the same trial schema,
  never by hand-editing results.
