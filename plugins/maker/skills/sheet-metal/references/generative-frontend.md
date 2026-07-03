# Generative Front-End: text/image → parametric model → DXF candidate

A generation lane added 2026-07-02 from the proven image→CAD framework
(instrument pilot series + Code-CAD Arena, makerbench-hwe). It adds a
*front-end* to this skill — a fast way to get from a brief or reference
photo to a parametric model and a DXF flat-pattern **candidate**. It is not
a review bypass: everything it produces enters the authority ladder at
`concept`/`design`, and the skill's existing DFM review, bend-allowance
math, and shop gates are unchanged and mandatory before fabrication.

## Two lanes

### 1. CADAM image/text lane (parametric OpenSCAD → DXF)

A local CADAM instance (github.com/Adam-CAD/CADAM, GPLv3; Tony's at
`_meta/CADAM` with Claude Fable 5 via OpenRouter) turns a text brief —
optionally with a reference photo attached — into a parametric model with
Customizer sliders, and can export DXF alongside STL/SCAD. Iterate the
sliders/chat until the shape is right, then export the DXF as a flat-pattern
candidate for laser/plasma.

Prompt conventions (mirror the arena task-brief style):

- State **material, thickness/gauge, and inside bend radius** up front, and
  say the part must be a developable/unfoldable surface if it will be bent —
  generated models love non-developable curvature.
- Name every parameter to expose, with values: `flange_height_mm (25)`,
  `hole_pitch_mm (40)`.
- State floors in the prompt: minimum feature width, minimum flange length,
  hole-to-bend distance, overall envelope vs stock sheet size.
- Say "K-factor and bend allowance are applied downstream by the reviewer —
  model at nominal geometry" so the model doesn't invent its own bend math.
- Cap tessellation (`$fn ≤ 96`) and demand one self-contained program with
  a named module per part.

Extraction gotcha: the generated source of truth lives in CADAM's local
Supabase (`messages.parts[].input.code`), not the page DOM. Compile/inspect
locally rather than trusting the browser preview.

### 2. Live SolidWorks copilot lane (real Sheet Metal features)

The Adam plugin drives real SolidWorks — Base Flange, Edge Flange, bends,
and *actual* Flat Pattern export from a real feature tree — which makes it
the stronger lane when the deliverable is a native part with drawings.
Luthier Bridge (StudioPipeline-hwe, `fusion/LuthierBridge` + SolidWorks
adapter) is the Fable-native equivalent: loopback HTTP + bearer token,
two-phase stage/confirm, and session context capture for provenance.

Lane gotchas, verified on a generated multi-part assembly:

- **Units**: SolidWorks exports default to inches in some paths — verify mm
  on every STEP/DXF/STL leaving the session.
- Assembly STL export needs the single-file option
  (`swSTLComponentsIntoOneFile`) or you get one file per body.
- Tessellated exports of native assemblies are typically **non-watertight**;
  that's tessellation, not bad design. Judge the feature tree, not the mesh,
  for design review — use the mesh only for geometric floor checks.
- Headless export from a running session works via COM script (VBScript
  `GetObject(, "SldWorks.Application")` + `OpenDoc`/`SaveAs3`); PowerShell
  late-binding to the SolidWorks COM object fails with
  TYPE_E_ELEMENTNOTFOUND — use cscript.

## Validation: sheet-metal analog of the mesh gate

Before a generated candidate reaches the DFM reviewer, run the objective
floor checks (adapted from the arena mesh gate):

1. compiles/renders at all;
2. **min feature width ≥ floor** — the sheet-metal analog of min-wall;
   generated models routinely emit sub-millimeter tabs, slots, and
   decorative cutouts that no plasma/laser process holds;
3. **min flange length ≥ 4× thickness** (or shop brake minimum);
4. **envelope vs stock**: flat-pattern extents fit the machine bed and the
   stock sheet (compare sorted extents so orientation can't false-fail);
5. **part count matches intent** — distinct bodies per part, nothing fused.

Only candidates passing the floors are worth human DFM review time. The
existing checklists (kerf, bend allowance, K-factor, reliefs, bend order,
DXF layer hygiene) remain **human-owned review gates** — the generative lane
never signs off on its own output.

## Provenance + labeling

Identical to the instrument pilots: every generated artifact records
pipeline + model, source image if any, cost (OpenRouter usage delta) and
wall time, floor-check results — and carries the label **GENERATED — not a
reviewed fabrication drawing** until the skill's authority ladder promotes
it through `design` review to `fabrication` with a named reviewer.
