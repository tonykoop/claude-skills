# Wolfram Workflow

Use Wolfram Desktop/Cloud for interactive physics, optimization, sound synthesis, 3D visualization, and publication-quality computational essays. Prefer `.wl` source files that create or update notebooks, because they are easier to edit and diff than binary-ish `.nb` files.

## Source Roadmap

Read this local roadmap when planning notebooks:

```text
C:\Users\Tony\Documents\GitHub\instrument-maker\docs\wolfram-notebooks-roadmap.md
```

It includes notebook ideas for sound synthesis, `Manipulate`, FEM/NDSolve, optimization, material scatter plots, build-log validation, humidity tuning, G-code animation, and Wolfram-to-CAD bridges.

## File Strategy

- Create `.wl` first: readable Wolfram Language source with equations, data imports, plots, and `CreateDocument`/`NotebookWrite` cells if a `.nb` is needed.
- Create `.nb` only when Wolfram Desktop/Cloud or `wolframscript` is available to generate it reliably.
- Include relative paths for exported CSV/SVG/STL/PNG/PDF artifacts.
- Keep notebook inputs at the top as an association, dataset, or imported workbook table.
- Export static figures for GitHub review when the notebook is interactive.

## v4.2 Packet Generator

Use `scripts/generate_wolfram_packet.py` when a packet needs more than the
root `wolfram-starter.wl` scaffold:

```bash
python3 scripts/generate_wolfram_packet.py ./build-packets/<slug>
```

It emits `wolfram/instrument-model.wl` with:

- packet metadata and file imports;
- model detection from `design.md`;
- core formulas for pipes, Helmholtz resonators, cantilever beams, and strings;
- a `Manipulate` explorer matched to the detected model when possible;
- an audio preview helper;
- validation plot scaffolding from `validation.csv`;
- a `packetNotebook[]` / `CreateDocument` entry point.

Pass `--execute` only when `wolframscript` is installed and local execution is
appropriate. If Wolfram execution is unavailable, the `.wl` source is still a
valid deliverable.

## Desktop And Cloud Execution

- Check for `wolframscript` before attempting local execution.
- If Desktop is unavailable, produce `.wl` and explain how it can be run in Desktop or Cloud.
- For Wolfram Cloud deployment, create code that can be pasted into Cloud or deployed with `CloudDeploy` once credentials/session are available.
- Do not assume the agent has authenticated Cloud access; ask before using browser automation or credentials.

## Notebook Patterns

Use `Manipulate` for:

- Tongue length explorer.
- Helmholtz resonance tuner.
- Bore profile visualizer.
- Segmented ring calculator.
- Tuning-system comparison.

Use `NMinimize` / `FindRoot` for:

- String gauge schedules.
- Minimum shell size for tongue layouts.
- Tube/resonator optimization.
- Pareto tradeoffs: pitch accuracy, mass, material, build constraints.

Use `Sound`, `AudioGenerator`, spectral plots for:

- Flute bore tone color.
- String spectra.
- Tongue/plate timbre comparison.
- Drone/chanter interactions.

Use `Graphics3D`, `RegionPlot3D`, `ParametricPlot3D`, STL export for:

- Bore profiles.
- Segmented drum shells.
- OpenSCAD/STL bridge models.
- Ergonomic scale mockups.
- Toolpath previews.

## Notebook Quality Checklist

- States the instrument, equations, assumptions, units.
- Exposes key parameters as controls.
- Shows target vs predicted values and cents error where relevant.
- Includes at least one known-reference validation.
- Exports a static figure or table for non-Wolfram review.
- Keeps TODOs for missing measurements, empirical constants, or build validation.
